import assert from "node:assert/strict";
import { randomUUID } from "node:crypto";
import { test } from "node:test";
import { acknowledged, applyEvent, enqueue, KEY, QUEUE_LIMIT, readLocal, ROOM, type LocalSession } from "../src/features/visitor/session.ts";

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
    const full = Array.from({ length: QUEUE_LIMIT }).reduce<LocalSession>(
        (session) => enqueue(session, "room_enter", null, 100, randomUUID()), start,
    );
    assert.throws(() => enqueue(full, "room_enter", null, 100, randomUUID()));
    const end = enqueue(start, "session_end", null, 100, randomUUID());
    assert.equal(enqueue(end, "room_enter", null, 100, randomUUID()), end);
    const revoked = { ...start, clearing: true };
    assert.equal(enqueue(revoked, "room_enter", null, 100, randomUUID()), revoked);
    assert.throws(() => readLocal({ getItem: () => "malformed" }));
    assert.throws(() => readLocal({ getItem: () => { throw new Error("denied"); } }));
});
