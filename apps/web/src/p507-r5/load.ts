import { Box3, Mesh, Vector3, type Object3D } from "three";
import { GLTFLoader } from "three/examples/jsm/loaders/GLTFLoader.js";
import { check, logicalId, type Manifest } from "../p507-e1/core.ts";
import { reference } from "../p507-e1/scene-contract.ts";
import { type ChairRoom, type Layout, type Part, type SurveyCollider, type XYZ } from "./chairs.ts";

const names = ["P507_R5_PROPOSAL.glb", "asset-manifest.json"] as const;
type Name = typeof names[number];
type Lock = { revision: "R5"; schema_version: 1; files: Record<Name, { bytes: number; sha256: string }> };
const lockPath = "../../../../experiments/p507-r5/asset-lock.json";
const locks = import.meta.glob<Lock>("../../../../experiments/p507-r5/asset-lock.json", { eager: true, import: "default" });
const directory = "/p507-r5-assets/";
const hex = /^[0-9a-f]{64}$/;
const historicalUnplaced = ["P507-CHAIR-C-09", "P507-CHAIR-C-10"];

export type R5Manifest = Manifest & {
    revision: "R5";
    layout: Layout;
    starting_pose: { feet_survey: XYZ };
};
function finite(values: unknown, size: number): values is number[] {
    return Array.isArray(values) && values.length === size && values.every(Number.isFinite);
}

function validPart(part: Part) {
    return finite(part.min, 3) && finite(part.max, 3) && part.max.every((value, i) => value > part.min[i]);
}
function validCollider(collider: SurveyCollider) {
    if (typeof collider.id !== "string" || !Array.isArray(collider.polygon) || collider.polygon.length < 3 ||
        !collider.polygon.every(p => finite(p, 2)) || !Number.isFinite(collider.bottom_z) ||
        !Number.isFinite(collider.top_z) || collider.top_z <= collider.bottom_z) return false;
    const polygon = collider.polygon;
    const winding = polygon.map(([x, y], i) => {
        const [a, b] = polygon[(i + 1) % polygon.length], [u, v] = polygon[(i + 2) % polygon.length];
        return (a - x) * (v - b) - (b - y) * (u - a);
    });
    return winding.every(value => value > 1e-10) || winding.every(value => value < -1e-10);
}

function validateManifest(manifest: R5Manifest) {
    check(manifest.revision === "R5" && manifest.unit === "metre" &&
        manifest.axis_conversion.includes("(x,z,-y)"), "R5 revision, units or axes are invalid");
    const survey = manifest.survey_baseline;
    check(survey.width_x === 6 && survey.length_y === 8.1 && survey.height_z === 3.5 &&
        survey.source === "USER_REPORTED", "R5 survey provenance mismatch");
    const placed = manifest.instances.filter(row => row.status !== "UNPLACED");
    const ids = new Set(placed.map(row => row.id));
    const all = new Set(manifest.instances.map(row => row.id));
    check(ids.size === placed.length && all.size === manifest.instances.length, "R5 duplicate logical identity");
    check(reference.records.every(row => ids.has(row.id)) && manifest.instances.length - placed.length === 2 &&
        historicalUnplaced.every(id => all.has(id) && !ids.has(id)), "R5 lost frozen R4 identities");
    const { layout } = manifest;
    check(finite(layout.walkable_rect, 4) && finite(manifest.starting_pose.feet_survey, 3) &&
        layout.walkable_rect[2] > layout.walkable_rect[0] && layout.walkable_rect[3] > layout.walkable_rect[1],
        "R5 invalid room or spawn");
    check(layout.static_walk_colliders.every(validCollider) && layout.static_interaction_colliders.every(validCollider),
        "R5 invalid collision volumes");
    const placedChairs = placed.filter(row => row.id.startsWith("P507-CHAIR-"));
    check(layout.chairs.length === 34 && placedChairs.length === 34 &&
        new Set(layout.chairs.map(chair => chair.id)).size === 34, "R5 wrong chair inventory");
    for (const chair of layout.chairs) {
        check(placedChairs.some(row => row.id === chair.id) && ids.has(chair.desk_id) && chair.desk_id.startsWith("P507-DESK-") &&
            finite(chair.stored, 3) && finite(chair.pulled, 3) && finite(chair.seat_eye, 3) &&
            finite(chair.stand, 3) && Number.isFinite(chair.orientation_deg) &&
            chair.stored[2] === 0 && chair.pulled[2] === 0 && chair.stand[2] === 0 &&
            chair.components.length > 0 && chair.components.every(validPart) &&
            chair.occupied_components.length > 0 && chair.occupied_components.every(validPart),
            "R5 invalid chair binding " + chair.id);
    }
    return { manifest, ids };
}

async function fetchPinned(name: Name, lock: Lock, signal?: AbortSignal) {
    const expected = lock.files[name];
    check(Number.isSafeInteger(expected?.bytes) && expected.bytes > 0 && expected.bytes <= 50_000_000 &&
        hex.test(expected.sha256), "Invalid R5 size budget or SHA-256");
    const response = await fetch(directory + name, { signal, credentials: "omit" });
    check(response.ok && response.body, "Thiếu asset " + name + " (HTTP " + response.status + ").");
    const reader = response.body.getReader();
    const bytes = new Uint8Array(expected.bytes);
    let offset = 0;
    try {
        for (;;) {
            const { done, value } = await reader.read();
            if (done) break;
            check(offset + value.length <= bytes.length, "R5 asset exceeds size budget");
            bytes.set(value, offset);
            offset += value.length;
        }
    } finally {
        await reader.cancel().catch(() => {});
    }
    const digest = await crypto.subtle.digest("SHA-256", bytes);
    const hash = Array.from(new Uint8Array(digest), byte => byte.toString(16).padStart(2, "0")).join("");
    check(offset === bytes.length && hash === expected.sha256, "R5 SHA-256/bytes mismatch: " + name);
    return bytes.buffer;
}

function validateEmbeddedGlb(bytes: ArrayBuffer) {
    check(bytes.byteLength >= 20, "R5 GLB is truncated");
    const header = new DataView(bytes);
    const jsonLength = header.getUint32(12, true);
    check(header.getUint32(0, true) === 0x46546c67 && header.getUint32(4, true) === 2 &&
        header.getUint32(8, true) === bytes.byteLength && header.getUint32(16, true) === 0x4e4f534a &&
        jsonLength <= bytes.byteLength - 20, "Invalid R5 GLB header");
    const content = JSON.parse(new TextDecoder().decode(new Uint8Array(bytes, 20, jsonLength)));
    for (const embedded of [...(content.buffers ?? []), ...(content.images ?? [])]) {
        check(embedded.uri === undefined, "R5 GLB declares an external or URI resource");
    }
}

function validateActualScene(root: Object3D, manifest: R5Manifest, ids: Set<string>) {
    check(root.position.lengthSq() === 0 && root.quaternion.w === 1 && root.scale.toArray().every(x => x === 1),
        "R5 model must have an identity transform");
    root.updateMatrixWorld(true);
    const matched = new Map<string, Box3>();
    const position = new Vector3();
    let vertexSamples = 0;
    root.traverse(node => {
        const tag = node.userData.survey_instance_id;
        if (typeof tag === "string") check(ids.has(tag), "R5 GLB contains an unknown or unplaced ID " + tag);
        if (!(node instanceof Mesh)) return;
        const id = logicalId(node, ids);
        if (!id) return;
        const bounds = matched.get(id) ?? new Box3();
        const attr = node.geometry.getAttribute("position");
        for (let i = 0; i < attr.count; i++) {
            position.fromBufferAttribute(attr, i).applyMatrix4(node.matrixWorld);
            check(Number.isFinite(position.x + position.y + position.z), "R5 non-finite vertex: " + id);
            bounds.expandByPoint(position);
            vertexSamples++;
        }
        matched.set(id, bounds);
    });
    for (const item of manifest.instances) {
        if (item.status === "UNPLACED") continue;
        const actual = matched.get(item.id);
        check(actual && !actual.isEmpty(), "R5 missing mesh geometry for " + item.id);
        const authored = item.authored_bounds_survey;
        check(finite(authored, 6), "Invalid R5 authored bounds: " + item.id);
        const [x0, y0, z0, x1, y1, z1] = authored;
        const expected = [x0, z0, -y1, x1, z1, -y0];
        const world = [...actual.min.toArray(), ...actual.max.toArray()];
        check(world.every((value, index) => Math.abs(value - expected[index]) <= .003),
            "R5 GLTFLoader bounds mismatch: " + item.id);
    }
    return { placedIDs: matched.size, vertexSamples };
}

export async function loadR5(signal?: AbortSignal) {
    const lock = locks[lockPath];
    check(lock, "R5 chưa có khóa kiểm chứng (HTTP 404).");
    check(lock.revision === "R5" && lock.schema_version === 1, "Invalid R5 asset lock");
    const manifestBytes = await fetchPinned("asset-manifest.json", lock, signal);
    const { ids, manifest } = validateManifest(JSON.parse(new TextDecoder().decode(manifestBytes)));
    const bytes = await fetchPinned("P507_R5_PROPOSAL.glb", lock, signal);
    const hash = lock.files["P507_R5_PROPOSAL.glb"].sha256;
    check(manifest.model_sha256 === hash && manifest.model_bytes === bytes.byteLength, "R5 GLB manifest identity mismatch");
    validateEmbeddedGlb(bytes);
    const gltf = await new GLTFLoader().parseAsync(bytes, directory);
    gltf.scene.traverse(node => {
        if (!(node instanceof Mesh)) return;
        const mats = Array.isArray(node.material) ? node.material : [node.material];
        const isShadowQuad = mats.some(m => m?.name?.includes("CONTACT_SHADOW"));
        const isShell = /^P507_ARCH_(FLOOR|WALL_)/.test(node.name);
        if (isShadowQuad) {
            node.castShadow = false;
            node.receiveShadow = false;
            node.renderOrder = 1;
            for (const m of mats) {
                if (m) {
                    m.depthWrite = false;
                    m.polygonOffset = true;
                    m.polygonOffsetFactor = -2;
                }
            }
        } else if (isShell) {
            node.castShadow = false;
            node.receiveShadow = true;
        } else {
            const isGlass = mats.some(m => m?.transparent || /GLASS|CARAFE|PET|CLOCK_LENS/.test(m?.name ?? ""));
            node.castShadow = !isGlass;
            node.receiveShadow = true;
        }
    });
    const geometry = validateActualScene(gltf.scene, manifest, ids);
    return { revision: "R5" as const, gltf, manifest, geometry, hash, ids };
}

export function bindChairMeshes(root: Object3D, room: ChairRoom) {
    const known = new Set(room.chairIDs);
    const bindings: { node: Object3D; id: string; base: Vector3 }[] = [];
    root.traverse(node => {
        const id = node.userData.survey_instance_id;
        if (typeof id !== "string" || !known.has(id) || logicalId(node.parent, known)) return;
        bindings.push({ node, id, base: node.position.clone() });
    });
    const delta = new Vector3(), world = new Vector3(), origin = new Vector3();
    const previous = new Map<Object3D, XYZ>();
    return () => {
        let moved = false;
        for (const { node, id, base } of bindings) {
            const chair = room.entries.get(id)!.chair;
            const [x, y, z] = room.pose(id);
            const last = previous.get(node);
            if (!node.parent || (last && x === last[0] && y === last[1] && z === last[2])) continue;
            if (!moved) {
                root.updateWorldMatrix(true, false);
                origin.set(0, 0, 0).applyMatrix4(root.matrixWorld);
                moved = true;
            }
            previous.set(node, [x, y, z]);
            if (x === chair.stored[0] && y === chair.stored[1] && z === chair.stored[2]) {
                node.position.copy(base);
                continue;
            }
            delta.set(x - chair.stored[0], z - chair.stored[2], chair.stored[1] - y)
                .applyMatrix4(root.matrixWorld).sub(origin);
            node.parent.localToWorld(world.copy(base)).add(delta);
            node.position.copy(node.parent.worldToLocal(world));
        }
        if (moved) root.updateMatrixWorld(true);
    };
}
