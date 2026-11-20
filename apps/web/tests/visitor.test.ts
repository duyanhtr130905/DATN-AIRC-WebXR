import assert from "node:assert/strict";
import { randomUUID } from "node:crypto";
import { test } from "node:test";
import { acknowledged, applyEvent, enqueue, hasInteractionCapacity, KEY, QUEUE_LIMIT, readLocal, readView, ROOM, type LocalSession } from "../src/features/visitor/session.ts";

const empty = (): LocalSession => ({
    view: { id: randomUUID(), room_id: ROOM, scope: "synthetic_local", selected_id: null, info_open: false, ended: false },
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
