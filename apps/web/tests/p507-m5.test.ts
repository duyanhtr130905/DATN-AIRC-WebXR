import assert from "node:assert/strict";
import test from "node:test";
import { BoxGeometry, Group, Mesh, MeshBasicMaterial, Raycaster, Vector3 } from "three";
import { intersectLogical, previewHit, thumbstick } from "../src/p507-m5/runtime.ts";

test("R4 pick resolves a placed ancestor and an unknown foreground mesh occludes it", () => {
    const model = new Group();
    const object = new Group();
    object.userData.survey_instance_id = "P507-CHAIR-A-01";
    const geometry = new BoxGeometry(1, 1, 1);
    const material = new MeshBasicMaterial();
    object.add(new Mesh(geometry, material));
    model.add(object);
    const foreign = new Mesh(geometry, material);
    foreign.userData.survey_instance_id = "P507-CHAIR-C-09";
    foreign.position.z = 2;
    const ray = new Raycaster(new Vector3(0, 0, 4), new Vector3(0, 0, -1));
    model.updateMatrixWorld(true);
    try {
        assert.equal(intersectLogical(ray, model, new Set(["P507-CHAIR-A-01"])), "P507-CHAIR-A-01");
        model.add(foreign);
        model.updateMatrixWorld(true);
        assert.equal(intersectLogical(ray, model, new Set(["P507-CHAIR-A-01"])), null);
    } finally {
        geometry.dispose();
        material.dispose();
    }
});

test("tabletop position must be close and below the viewer", () => {
    const head = new Vector3(0, 1.65, 0);
    assert(previewHit(new Vector3(0, 0.75, -1), head));
    for (const point of [[0, 0.75, -0.2], [0, 0.75, -3], [0, 1.7, -1], [0, -0.4, -1]]) {
        assert(!previewHit(new Vector3(...point), head));
    }
});

test("locomotion accepts only mapped live controllers and clears after disconnect", () => {
    const source = { targetRayMode: "tracked-pointer", gamepad: { mapping: "xr-standard", axes: [0, 0, 0.6, -0.8] } };
    const session = (inputSources: unknown[]) => ({ inputSources }) as unknown as XRSession;
    assert.deepEqual(thumbstick(session([source])), [0.8, 0.6]);
    assert.deepEqual(thumbstick(session([ { ...source, targetRayMode: "gaze" } ])), [0, 0]);
    assert.deepEqual(thumbstick(session([])), [0, 0]);
});
