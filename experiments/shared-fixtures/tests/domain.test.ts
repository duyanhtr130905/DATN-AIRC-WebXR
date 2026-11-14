import { test } from "node:test";
import assert from "node:assert/strict";
import {
  fixture,
  validateScene,
  DemoController,
  adapterFromLoader,
} from "../domain.ts";
test("fixture has exactly one synthetic room, five stable objects and all three state kinds", () => {
  const s = validateScene(fixture);
  assert.equal(s.objects.length, 5);
  assert.equal(new Set(s.objects.map((o) => o.status.kind)).size, 3);
  assert.ok(s.objects.every((o) => o.provenance.source_kind === "synthetic"));
  assert.notEqual(s.room.id, "507");
});
test("duplicate ID, wrong room, NaN vector and invalid timestamp are rejected", () => {
  for (const mutate of [
    (s: any) => {
      s.objects[1].id = s.objects[0].id;
    },
    (s: any) => {
      s.objects[0].roomId = "wrong";
    },
    (s: any) => {
      s.objects[0].position[0] = NaN;
    },
    (s: any) => {
      s.objects[0].status.timestamp = "bad";
    },
  ]) {
    const s = structuredClone(fixture);
    mutate(s);
    assert.throws(() => validateScene(s));
  }
});
test("real_verified needs evidence, unknown is explicit and cannot be mutated as synthetic", () => {
  const s = structuredClone(fixture);
  s.objects[0].provenance.source_kind = "real_verified";
  assert.throws(() => validateScene(s));
  s.objects[0].provenance.source_kind = "unknown";
  const c = new DemoController(s);
  c.select(s.objects[0].id);
  assert.throws(() => c.cycle());
});
test("selection validates ID; update is immutable, affects one object, timestamps and reset restores fixture", () => {
  const c = new DemoController(fixture, () => "2026-11-14T01:00:00Z");
  assert.throws(() => c.cycle());
  assert.throws(() => c.select("missing"));
  const before = c.getSnapshot();
  c.select(fixture.objects[0].id);
  c.cycle();
  const after = c.getSnapshot();
  assert.notEqual(
    after.scene.objects[0].status.value,
    before.scene.objects[0].status.value,
  );
  assert.equal(after.scene.objects[0].status.timestamp, "2026-11-14T01:00:00Z");
  assert.deepEqual(after.scene.objects[1], before.scene.objects[1]);
  assert.equal(
    before.scene.objects[0].status.value,
    fixture.objects[0].status.value,
  );
  c.reset();
  assert.deepEqual(c.getSnapshot().scene, fixture);
  assert.equal(c.getSnapshot().selectedId, null);
});
test("subscriptions can unsubscribe and snapshots stable between commands", () => {
  const c = new DemoController(fixture);
  let n = 0;
  const off = c.subscribe(() => n++);
  assert.equal(c.getSnapshot(), c.getSnapshot());
  c.select(fixture.objects[0].id);
  off();
  c.cycle();
  assert.equal(n, 1);
});
test("loader adapter validates external input instead of trusting future API", async () => {
  assert.deepEqual(
    await adapterFromLoader(async () => fixture).load(),
    fixture,
  );
  await assert.rejects(adapterFromLoader(async () => ({})).load());
});
