import test from "node:test";
import assert from "node:assert/strict";
import { loadDemo, selectedObject } from "../src/features/catalog/demo.ts";
test("demo selection preserves stable identity and synthetic provenance", () => {
  const scene = loadDemo();
  assert.equal(new Set(scene.objects.map(object => object.id)).size, scene.objects.length);
  assert.ok(scene.objects.every(object => object.roomId === scene.id && object.sourceKind === "synthetic"));
  assert.equal(selectedObject(scene, "missing"), null);
  assert.equal(selectedObject(scene, null), null);
  assert.equal(selectedObject(scene, scene.objects[1].id)?.name, "Khối mẫu B");
  assert.notEqual(loadDemo().objects, scene.objects);
});
