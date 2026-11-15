export const MAX_STATES = 512;
export const UUID = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
export function record(value: unknown): Record<string, unknown> {
    if (!value || typeof value !== "object" || Array.isArray(value))
        throw new Error("Invalid object");
    return value as Record<string, unknown>;
}
export function id(value: unknown): string {
    if (typeof value !== "string" || !UUID.test(value))
        throw new Error("Invalid UUID");
    return value.toLowerCase();
}
export function integer(value: unknown, min = 0, max = Number.MAX_SAFE_INTEGER): number {
    if (!Number.isSafeInteger(value) || (value as number) < min || (value as number) > max)
        throw new Error("Invalid integer");
    return value as number;
}
export function text(value: unknown, max: number): string {
    if (typeof value !== "string" || !value.trim() || value.length > max)
        throw new Error("Invalid text");
    return value;
}
export function date(value: unknown): string {
    const result = text(value, 64);
    if (!/(Z|[+-]\d{2}:\d{2})$/i.test(result) || !Number.isFinite(Date.parse(result)))
        throw new Error("Invalid timestamp");
    return result;
}
export type Metadata = {
    label?: string | null;
    description?: string | null;
};
export interface Room {
    id: string;
    code: string;
    name: string;
    source_kind: "synthetic";
    metadata: Metadata;
    created_at: string;
    updated_at: string;
}
export interface CatalogObject extends Omit<Room, "code"> {
    room_id: string;
    type: string;
}
export interface TwinState {
    id: string;
    room_id: string;
    target_kind: "room" | "object";
    target_id: string;
    state_type: "room_schedule" | "equipment_status" | "exhibit_info";
    value: Record<string, string>;
    version: number;
    source_kind: "synthetic";
    source_observed_at: string | null;
    committed_at: string;
}
function metadata(raw: unknown): Metadata {
    const r = record(raw);
    const result: Metadata = {};
    for (const [key, max] of [["label", 256], ["description", 512]] as const) {
        if (r[key] !== undefined) {
            if (r[key] !== null && (typeof r[key] !== "string" || (r[key] as string).length > max))
                throw new Error("Invalid metadata");
            result[key] = r[key] as string | null;
        }
    }
    if (Object.keys(r).some(key => !["label", "description"].includes(key)))
        throw new Error("Private metadata rejected");
    return result;
}
function common(raw: unknown) {
    const r = record(raw);
    if (r.source_kind !== "synthetic")
        throw new Error("Non-synthetic data rejected");
    return { id: id(r.id), name: text(r.name, 256), source_kind: "synthetic" as const, metadata: metadata(r.metadata), created_at: date(r.created_at), updated_at: date(r.updated_at) };
}
export function room(raw: unknown): Room { const r = record(raw); return { ...common(r), code: text(r.code, 64) }; }
export function object(raw: unknown): CatalogObject { const r = record(raw); return { ...common(r), room_id: id(r.room_id), type: text(r.type, 64) }; }
export function state(raw: unknown): TwinState {
    const r = record(raw);
    const v = record(r.value);
    const value: Record<string, string> = {};
    if (r.source_kind !== "synthetic")
        throw new Error("Non-synthetic state");
    if (r.state_type === "equipment_status") {
        if (!["available", "maintenance", "offline"].includes(String(v.status)))
            throw new Error("Invalid equipment state");
        value.status = text(v.status, 32);
    }
    else if (r.state_type === "room_schedule") {
        if (!["free", "occupied", "closed"].includes(String(v.status)))
            throw new Error("Invalid schedule");
        value.status = text(v.status, 32);
        value.activity = text(v.activity, 160);
    }
    else if (r.state_type === "exhibit_info") {
        value.title = text(v.title, 160);
        if (typeof v.text !== "string" || v.text.length > 800)
            throw new Error("Invalid exhibit");
        value.text = v.text;
    }
    else
        throw new Error("Invalid state type");
    if (Object.keys(v).some(key => !(key in value)))
        throw new Error("Unknown value field");
    if ((r.state_type === "room_schedule") !== (r.target_kind === "room") || !["room", "object"].includes(String(r.target_kind)))
        throw new Error("Invalid state target");
    return { id: id(r.id), room_id: id(r.room_id), target_kind: r.target_kind as TwinState["target_kind"], target_id: id(r.target_id), state_type: r.state_type as TwinState["state_type"], value, version: integer(r.version, 1), source_kind: "synthetic", source_observed_at: r.source_observed_at === null ? null : date(r.source_observed_at), committed_at: date(r.committed_at) };
}
export function scopedState(raw: unknown, roomId: string, objectIds: ReadonlySet<string>): TwinState {
    const result = state(raw);
    if (result.room_id !== roomId || (result.target_kind === "room" ? result.target_id !== roomId : !objectIds.has(result.target_id)))
        throw new Error("State outside Catalog scope");
    return result;
}
