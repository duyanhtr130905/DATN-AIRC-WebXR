import assert from "node:assert/strict";
import { randomUUID } from "node:crypto";
import { test } from "node:test";
import { acknowledged, applyEvent, enqueue, hasInteractionCapacity, interactionCapacity, KEY, MAX_SYNC_BATCHES, QUEUE_LIMIT, BATCH_SIZE, readLocal, readView, ROOM, type LocalSession } from "../src/features/visitor/session.ts";

const empty = (): LocalSession => ({
    view: { id: randomUUID(), room_id: ROOM, scope: "synthetic_local", selected_id: null, info_open: false, ended: false, remaining_events: 499 },
    clearing: false, queue: [], clock: 0,
});

test("visitor IDs and interaction state survive a serialized queue round trip", () => {
    const start = empty();
    const first = enqueue(start, "object_select", "demo-object-cube", 100, randomUUID());
    const second = enqueue(first, "info_close", "demo-object-cube", 50, randomUUID());
    const stored = readLocal({ getItem: key => key === KEY ? JSON.stringify(second) : null });
    assert.deepEqual(stored, second);
    assert.equal(second.clock, 101);
    assert.equal(second.view.info_open, false);
    assert.deepEqual(second.queue.reduce(applyEvent, start.view), second.view);
});

test("only complete matching receipts clear queued IDs", () => {
    const stored = enqueue(empty(), "room_enter", null, 100, randomUUID());
    const id = stored.queue[0].id;
    assert.throws(() => acknowledged(stored.queue, { receipts: [] }));
    assert.throws(() => acknowledged(stored.queue, { receipts: [{ id: randomUUID(), status: "accepted" }] }));
    assert.throws(() => acknowledged(stored.queue, { receipts: [{ id, status: "conflict" }] }));
    assert.deepEqual(acknowledged(stored.queue, { receipts: [{ id, status: "duplicate" }] }), new Set([id]));
});

test("queue cap and ended or withdrawn sessions do not record new items", () => {
    const start = empty();
    const full = Array.from({ length: QUEUE_LIMIT - 1 }).reduce<LocalSession>(
        (session) => enqueue(session, "room_enter", null, 100, randomUUID()), start,
    );
    assert.throws(() => enqueue(full, "room_enter", null, 100, randomUUID()));
    assert.equal(enqueue(full, "session_end", null, 100, randomUUID()).queue.length, QUEUE_LIMIT);
    const end = enqueue(start, "session_end", null, 100, randomUUID());
    assert.equal(enqueue(end, "room_enter", null, 100, randomUUID()), end);
    const revoked = { ...start, clearing: true };
    assert.equal(enqueue(revoked, "room_enter", null, 100, randomUUID()), revoked);
    assert.throws(() => readLocal({ getItem: () => "malformed" }));
    assert.throws(() => readLocal({ getItem: () => { throw new Error("denied"); } }));
});

test("the last interaction can be queued once and the terminal event has a separate slot", () => {
    const start = empty();
    start.view.remaining_events = 1;
    const interaction = enqueue(start, "object_select", "demo-object-cube", 100, randomUUID());
    assert.equal(hasInteractionCapacity(interaction), false);
    assert.throws(() => enqueue(interaction, "info_close", "demo-object-cube", 101, randomUUID()));
    const end = enqueue(interaction, "session_end", null, 102, randomUUID());
    assert.deepEqual(end.queue.map(item => item.event_type), ["object_select", "session_end"]);
    const stored = readLocal({ getItem: () => JSON.stringify(end) });
    assert.deepEqual(stored, end);
    assert.throws(() => readView({ ...start.view, remaining_events: -1 }));
});

test("legacy queues reserve exactly one durable terminal after 128 untouched interactions", () => {
    const start = empty();
    delete start.view.remaining_events;
    const legacy: LocalSession = {
        ...start,
        clock: QUEUE_LIMIT,
        queue: Array.from<unknown, LocalSession["queue"][number]>({ length: QUEUE_LIMIT }, (_, i) => ({
            id: `10000000-0000-4000-8000-${String(i).padStart(12, "0")}`,
            schema_version: 1 as const, event_type: "room_enter" as const,
            room_id: ROOM, object_id: null, occurred_at: new Date(i + 1).toISOString(),
        })),
    };
    const restore = (value: LocalSession) => readLocal({ getItem: () => JSON.stringify(value) })!;
    for (const count of [0, 1, 126, 127, 128]) {
        const restored = restore({ ...legacy, queue: legacy.queue.slice(0, count) });
        assert.equal(interactionCapacity(restored), count < 127 ? "server-unknown" : "local-full");
        assert.equal(hasInteractionCapacity(restored), false);
        const known = { ...restored, view: { ...restored.view, remaining_events: 499 } };
        assert.equal(hasInteractionCapacity(known), count < 127);
        assert.throws(() => enqueue(restored, "room_enter", null, 50, randomUUID()));
        const end = enqueue(restored, "session_end", null, 50, randomUUID());
        assert.equal(end.queue.length, count + 1);
        assert.deepEqual(end.queue.slice(0, -1), restored.queue);
        assert.deepEqual(restore(end), end);
        assert.equal(end.queue.at(-1)?.occurred_at, new Date(129).toISOString());
        assert.equal(enqueue(end, "session_end", null, 200, randomUUID()), end);
        assert.equal(enqueue(end, "room_enter", null, 200, randomUUID()), end);
    }

    const end = enqueue(legacy, "session_end", null, 50, randomUUID());
    assert.equal(MAX_SYNC_BATCHES, Math.ceil(end.queue.length / BATCH_SIZE));
    assert.throws(() => restore({ ...end, view: legacy.view }));
    assert.throws(() => restore({ ...legacy, queue: [...legacy.queue, legacy.queue[0]] }));
    assert.throws(() => restore({ ...end, queue: [...end.queue, end.queue[0]] }));
    assert.throws(() => restore({ ...end, queue: [end.queue.at(-1)!, ...end.queue.slice(2)] }));
    assert.throws(() => restore({ ...end, queue: [end.queue.at(-1)!, ...end.queue.slice(2, -1)] }));
});
