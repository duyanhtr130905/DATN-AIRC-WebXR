export const ROOM = "demo-room-foundation";
export const PATH = "/api/v1/visitor";
export const KEY = "airc.synthetic.visitor.v1";
export const PENDING_KEY = KEY + ".start";
export const QUEUE_LIMIT = 128;
const LEGACY_TERMINAL_LIMIT = QUEUE_LIMIT + 1;
export const BATCH_SIZE = 16;
export const MAX_SYNC_BATCHES = Math.ceil(LEGACY_TERMINAL_LIMIT / BATCH_SIZE);
type ObjectId = "demo-object-cube" | "demo-object-column";
export type Kind = "room_enter" | "object_select" | "info_open" | "info_close" | "session_end";
export type VisitEvent = {
    id: string; schema_version: 1; event_type: Kind; room_id: typeof ROOM;
    object_id: ObjectId | null; occurred_at: string;
};
export type View = {
    id: string; room_id: typeof ROOM; scope: "synthetic_local";
    selected_id: ObjectId | null; info_open: boolean; ended: boolean; remaining_events?: number;
};
export type LocalSession = { view: View; queue: VisitEvent[]; clock: number; clearing: boolean; proofLost?: boolean };
export type PendingStart = { id: string; previousId: string | null; prepared: boolean };

const uuid = /^[\da-f]{8}-[\da-f]{4}-4[\da-f]{3}-[89ab][\da-f]{3}-[\da-f]{12}$/;
const kinds = ["room_enter", "object_select", "info_open", "info_close", "session_end"];
const objectId = (value: unknown): value is ObjectId =>
    value === "demo-object-cube" || value === "demo-object-column";

export function readRemaining(input: { remaining_events?: unknown }): number | undefined {
    const remaining = input.remaining_events;
    if (remaining === undefined) return undefined; // Previously stored views and older API responses.
    if (typeof remaining !== "number" || !Number.isSafeInteger(remaining) || remaining < 0 || remaining > 500) {
        throw new Error("Invalid remaining event count");
    }
    return remaining;
}

export function readView(input: unknown): View {
    const value = input as Partial<View> | null;
    if (!value || typeof value.id !== "string" || !uuid.test(value.id) ||
        value.room_id !== ROOM || value.scope !== "synthetic_local" ||
        (value.selected_id !== null && !objectId(value.selected_id)) ||
        typeof value.info_open !== "boolean" || typeof value.ended !== "boolean") {
        throw new Error("Invalid synthetic session");
    }
    readRemaining(value);
    return value as View;
}

export function readPending(storage: Pick<Storage, "getItem">): PendingStart | null {
    const raw = storage.getItem(PENDING_KEY);
    if (raw === null) return null;
    if (raw.length > 256) throw new Error("Invalid start attempt");
    const attempt = JSON.parse(raw) as PendingStart;
    if (!attempt || !uuid.test(attempt.id) ||
        (attempt.previousId !== null && !uuid.test(attempt.previousId)) ||
        typeof attempt.prepared !== "boolean") throw new Error("Invalid start attempt");
    return attempt;
}

export const settled = (session: LocalSession) =>
    session.view.ended && session.queue.length === 0 && !session.clearing && !session.proofLost;

export function readLocal(storage: Pick<Storage, "getItem">): LocalSession | null {
    const raw = storage.getItem(KEY);
    if (raw === null) return null;
    if (raw.length > 50_000) throw new Error("Invalid queue");
    const value = JSON.parse(raw) as LocalSession;
    readView(value.view);
    if ((value.proofLost !== undefined && typeof value.proofLost !== "boolean") || !Number.isSafeInteger(value.clock) || typeof value.clearing !== "boolean" ||
        !Array.isArray(value.queue) || value.queue.length > LEGACY_TERMINAL_LIMIT ||
        value.queue.some(item => !uuid.test(item.id) || item.schema_version !== 1 ||
            item.room_id !== ROOM || !kinds.includes(item.event_type) ||
            !Number.isFinite(Date.parse(item.occurred_at)) ||
            (["room_enter", "session_end"].includes(item.event_type)
                ? item.object_id !== null : !objectId(item.object_id)))) {
        throw new Error("Invalid queue");
    }
    // Older clients could fill all 128 slots with interactions. The only
    // valid overflow is one final terminal event with an optimistic ended view.
    const terminalIndex = value.queue.findIndex(item => item.event_type === "session_end");
    if (terminalIndex !== -1
        ? terminalIndex !== value.queue.length - 1 || !value.view.ended
        : value.queue.length > QUEUE_LIMIT) {
        throw new Error("Invalid terminal event in queue");
    }
    return value;
}

export function applyEvent(view: View, item: VisitEvent): View {
    if (item.event_type === "session_end") return { ...view, ended: true };
    if (item.event_type === "room_enter") return view;
    return { ...view, selected_id: item.object_id, info_open: item.event_type !== "info_close" };
}

export function interactionCapacity({ view, queue }: LocalSession) {
    if (queue.length >= QUEUE_LIMIT - 1) return "local-full";
    if (view.remaining_events === undefined) return "server-unknown";
    // Count unacknowledged interactions conservatively until their receipts arrive.
    return view.remaining_events > queue.length ? "available" : "server-full";
}

export function hasInteractionCapacity(session: LocalSession): boolean {
    return !session.view.ended && !session.clearing && !session.proofLost &&
        interactionCapacity(session) === "available";
}

export function enqueue(session: LocalSession, kind: Kind, object: string | null, now: number,
    id: string): LocalSession {
    if (session.clearing || session.proofLost || session.view.ended) return session;
    if (kind !== "session_end" && !hasInteractionCapacity(session)) throw new Error("Session is full");
    if (kind === "session_end" && session.queue.length >= LEGACY_TERMINAL_LIMIT) {
        throw new Error("Queue is full");
    }
    if (object !== null && !objectId(object)) throw new Error("Unknown synthetic object");
    if ((kind === "room_enter" || kind === "session_end") !== (object === null)) {
        throw new Error("Invalid synthetic object for event");
    }
    const clock = Math.max(now, session.clock + 1);
    const event: VisitEvent = {
        id, schema_version: 1, event_type: kind, room_id: ROOM, object_id: object,
        occurred_at: new Date(clock).toISOString(),
    };
    return { ...session, clock, queue: [...session.queue, event], view: applyEvent(session.view, event) };
}

export function acknowledged(sent: VisitEvent[], body: unknown): Set<string> {
    const receipts = (body as { receipts?: { id: string; status: string }[] } | null)?.receipts;
    if (!Array.isArray(receipts) || receipts.length !== sent.length || receipts.some((item, i) =>
        item.id !== sent[i].id || !["accepted", "duplicate"].includes(item.status))) {
        throw new Error("Incomplete receipt");
    }
    return new Set(receipts.map(item => item.id));
}
