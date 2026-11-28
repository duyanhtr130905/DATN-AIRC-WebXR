import {
    ACESFilmicToneMapping, Box3, Color, DirectionalLight, Group, HemisphereLight, Matrix4,
    Material, Mesh, Object3D, PCFSoftShadowMap, PerspectiveCamera, Scene, Texture, Vector3, WebGLRenderer,
} from "three";
import { loadFrozenP507 } from "./p507-e1/load";
import { ChairRoom } from "./p507-r5/chairs";
import { bindChairMeshes, loadR5 as loadR5P507 } from "./p507-r5/load";
import { disposeRoom } from "./p507-m5/runtime";

type Revision = "r4" | "r5";
type Dimensions = { width_x: number; length_y: number; height_z: number };
type CameraPose = {
    position: Vector3; target: Vector3; fov: number;
    cutaway?: boolean; closedDoor?: boolean; pullChairs?: boolean;
};
type Timing = { intervalsMs: number[]; fps: number; p50Ms: number; p95Ms: number; durationMs: number };
declare global {
    interface Window {
        __P507_R5_REVIEW__?: {
            poses: string[];
            aim: (key: string) => void;
            snapshot: () => unknown;
            measure: (warmupMs: number, sampleMs: number) => Promise<Timing>;
        };
    }
}

const canvas = document.querySelector<HTMLCanvasElement>("#scene")!;
const status = document.querySelector<HTMLParagraphElement>("#status")!;
const picker = document.querySelector<HTMLSelectElement>("#camera")!;

function buildPoses(model: Group, { width_x: w, length_y: l, height_z: h }: Dimensions) {
    const poses: Record<string, CameraPose> = {};
    const add = (
        name: string, position: number[], target: number[], fov: number,
        { cutaway = false, closedDoor = false, pullChairs = false } = {},
    ) => {
        poses[name] = {
            position: new Vector3().fromArray(position),
            target: new Vector3().fromArray(target),
            fov, cutaway, closedDoor, pullChairs,
        };
    };
    const center = (selector: RegExp) => {
        const bounds = new Box3();
        model.traverse(node => {
            const id = node.userData.survey_instance_id;
            if (typeof id === "string" && selector.test(id)) bounds.expandByObject(node);
        });
        if (bounds.isEmpty()) throw new Error("Thiếu nhóm đối tượng " + selector.source);
        return bounds.getCenter(new Vector3());
    };
    const boxOf = (selector: RegExp) => {
        const bounds = new Box3();
        model.traverse(node => {
            const id = node.userData.survey_instance_id;
            if (typeof id === "string" && selector.test(id)) bounds.expandByObject(node);
        });
        if (bounds.isEmpty()) throw new Error("Thiếu nhóm đối tượng " + selector.source);
        return bounds;
    };

    // 1. Mặt bằng top-down
    add("Mặt bằng", [w / 2, Math.max(w, l) * 1.18, -l / 2], [w / 2, 0, -l / 2 - .001], 55, { cutaway: true });
    add("Ba cụm bàn", [w + 2.8, h + 5.6, -l * .58], [w / 2, .5, -l / 2], 55, { cutaway: true });

    // 2-3. Toàn cảnh từ cửa & từ cuối phòng
    const door = center(/^P507-DOOR-LEAF-/);
    add("Toàn cảnh từ cửa", [0.85, 1.65, door.z], [w * 0.62, 1.15, -l * 0.36], 82);
    add("Toàn cảnh từ cuối phòng", [w * 0.55, 1.75, -0.55], [w * 0.42, 1.25, -l * 0.65], 82);

    // 4-6. Cụm A, B, C
    for (const cluster of ["A", "B", "C"]) {
        const at = center(new RegExp(`^P507-DESK-${cluster}`));
        add(`Cụm ${cluster}`, [at.x, h + 3.4, at.z - .01], at.toArray(), 52, { cutaway: true });
    }

    // 7. Máy tính và máy in cận cảnh (trên cụm A; R4 vẫn giữ góc cận cụm A tương ứng)
    const deskA = boxOf(/^P507-DESK-A/);
    add("Máy tính và máy in", [deskA.max.x - 0.35, 1.55, (deskA.min.z + deskA.max.z) / 2 - 1.35],
        [deskA.max.x - 0.85, 1.05, (deskA.min.z + deskA.max.z) / 2], 62);

    // 8. Hoa lan và bộ trà
    add("Hoa lan và bộ trà", [(deskA.min.x + deskA.max.x) / 2 - 0.15, 1.48, (deskA.min.z + deskA.max.z) / 2 - 1.25],
        [(deskA.min.x + deskA.max.x) / 2 + 0.15, 1.02, (deskA.min.z + deskA.max.z) / 2], 60);

    // 9. Góc TV, đồng hồ và poster
    const tv = center(/^P507-TV-LARGE$/);
    add("TV, đồng hồ và poster", [2.55, 1.68, tv.z + 2.05], [tv.x + 0.45, 1.75, -l + 0.1], 78);

    // 10. Kệ bốn tầng và bốn bình nước
    const shelf = center(/^P507-UTILITY-SHELF$/);
    add("Kệ bốn tầng và bình nước", [3.05, shelf.y + .42, shelf.z], [shelf.x, shelf.y + .28, shelf.z], 68);

    // 11. Toàn bộ khu tiện ích
    const utility = center(/^P507-(CABINET-FILES|FRIDGE|UTILITY-SHELF|WASTE-BIN|SHOE-RACK|WHITEBOARD)$/);
    add("Khu tiện ích", [Math.min(w * .62, 4.8), 1.85, utility.z], [.3, 1.15, utility.z], 92);

    // 12. Cửa, bảng trắng và kệ giày
    const shoe = center(/^P507-SHOE-RACK$/);
    add("Cửa, bảng trắng và kệ giày", [3.0, 1.65, (shoe.z + door.z) / 2], [0.25, 1.25, (shoe.z + door.z) / 2], 78);

    // 13. Cửa sổ và rèm
    add("Cửa sổ và rèm", [1.35, 1.68, -l * .48], [w - .05, 1.88, -l * .58], 80);

    // 14. Tường logo và tường khung ảnh
    add("Tường khung ảnh", [w * .62, 1.75, 2.75 - l], [w * .62, 2.20, .08 - l], 74);
    add("Tường logo", [w / 2, 1.65, -3.4], [w / 2, 1.9, -.08], 72);

    // 15. Trần và ánh sáng
    add("Trần và ánh sáng", [w / 2, 1.40, -l * 0.65], [w / 2, h, -l * 0.40], 116);

    // 16-17. Lối A-B và Lối B-C khi ghế kéo ra
    const deskB = boxOf(/^P507-DESK-B0[1-4]$/);
    const deskC = boxOf(/^P507-DESK-C0[1-4]$/);
    const abZ = (deskA.max.z + deskB.min.z) / 2;
    const bcZ = (deskB.max.z + deskC.min.z) / 2;
    add("Lối A-B ghế kéo ra", [1.10, 1.55, abZ], [w - 0.6, 0.85, abZ], 74, { pullChairs: true });
    add("Lối B-C ghế kéo ra", [1.10, 1.55, bcZ], [w - 0.6, 0.85, bcZ], 74, { pullChairs: true });

    // 18. Góc nhìn khi ngồi (tại ghế A-01 nhìn về cụm A/tủ)
    const a01 = center(/^P507-CHAIR-A-01$/);
    add("Góc nhìn khi ngồi", [a01.x, 1.20, a01.z + 0.25], [a01.x + 0.4, 1.15, a01.z - 2.2], 76, { pullChairs: true });

    // 19. Cửa mở / đóng
    add("Cửa mở ra ngoài", [-2.5, 1.65, door.z], [.1, 1.34, door.z], 78);
    add("Cửa đóng", [-2.5, 1.65, door.z], [.1, 1.34, door.z], 78, { closedDoor: true });
    return poses;
}

function collectDoorRoots(model: Group) {
    const doors: { node: Object3D; open: Matrix4; closed: Matrix4 }[] = [];
    model.updateMatrixWorld(true);
    model.traverse(node => {
        if (!String(node.userData.survey_instance_id).startsWith("P507-DOOR-LEAF-")
            || node.userData.door_swing !== "OUTWARD") return;
        const [x, y, z] = node.userData.hinge_survey as number[];
        const hinge = new Vector3(x, z, -y);
        const angle = Number(node.userData.demo_open_angle_deg) * Math.PI / 180;
        const closing = new Matrix4().makeTranslation(hinge.x, hinge.y, hinge.z)
            .multiply(new Matrix4().makeRotationY(-angle))
            .multiply(new Matrix4().makeTranslation(-hinge.x, -hinge.y, -hinge.z));
        const fromWorld = node.parent?.matrixWorld.clone().invert() ?? new Matrix4();
        doors.push({ node, open: node.matrix.clone(), closed: fromWorld.multiply(closing).multiply(node.matrixWorld) });
    });
    return doors;
}

function frameTiming(intervalsMs: number[]): Timing {
    const sorted = intervalsMs.slice().sort((a, b) => a - b);
    const durationMs = intervalsMs.reduce((sum, frame) => sum + frame, 0);
    return {
        intervalsMs, durationMs, fps: 1000 * intervalsMs.length / durationMs,
        p50Ms: sorted[Math.ceil(sorted.length * .5) - 1],
        p95Ms: sorted[Math.ceil(sorted.length * .95) - 1],
    };
}

async function run(revision: Revision) {
    const lifetime = new AbortController();
    window.addEventListener("pagehide", () => lifetime.abort(), { once: true });
    const loadStart = performance.now();
    const loadSignal = AbortSignal.any([lifetime.signal, AbortSignal.timeout(60_000)]);
    const asset = revision === "r5" ? await loadR5P507(loadSignal) : await loadFrozenP507(loadSignal);
    const parsedMs = performance.now() - loadStart;
    const model = asset.gltf.scene;
    let renderer: WebGLRenderer;
    try {
        renderer = new WebGLRenderer({ canvas, antialias: true, powerPreference: "high-performance" });
    } catch (error) {
        disposeRoom(model);
        throw error;
    }
    renderer.transmissionResolutionScale = .5;
    renderer.setPixelRatio(Math.min(devicePixelRatio, 1.5));
    renderer.toneMapping = ACESFilmicToneMapping;
    renderer.toneMappingExposure = revision === "r5" ? 1.05 : 1.0;
    renderer.shadowMap.enabled = revision === "r5";
    renderer.shadowMap.type = PCFSoftShadowMap;
    renderer.shadowMap.autoUpdate = false;
    const scene = new Scene();
    scene.background = new Color("#d9dedc");
    const dimensions = asset.manifest.virtual_dimensions;
    const daylight = new DirectionalLight(0xfff6e8, revision === "r5" ? 1.65 : 2);
    daylight.position.set(dimensions.width_x + (revision === "r5" ? 3.0 : -0.35), dimensions.height_z + (revision === "r5" ? 1.5 : -0.4), -dimensions.length_y * .48);
    daylight.target.position.set(dimensions.width_x * .25, 0, -dimensions.length_y * .52);
    if (revision === "r5") {
        daylight.castShadow = true;
        daylight.shadow.mapSize.set(1024, 1024);
        daylight.shadow.bias = -0.0001;
        daylight.shadow.normalBias = 0.03;
        daylight.shadow.camera.left = -8;
        daylight.shadow.camera.right = 8;
        daylight.shadow.camera.top = 8;
        daylight.shadow.camera.bottom = -8;
        daylight.shadow.camera.near = 0.5;
        daylight.shadow.camera.far = 24;
    }
    scene.add(
        new HemisphereLight(revision === "r5" ? 0xf5f8ff : 0xe6efff, revision === "r5" ? 0xede6da : 0xc9bfa9, revision === "r5" ? 1.35 : 1.25),
        daylight, daylight.target, model,
    );
    if (revision === "r5") {
        const fillWest = new DirectionalLight(0xf3f6ff, 0.68);
        fillWest.position.set(-2.5, 1.1, -dimensions.length_y * 0.25);
        fillWest.target.position.set(dimensions.width_x * 0.65, 2.5, -dimensions.length_y * 0.68);
        const fillSouth = new DirectionalLight(0xfff9f0, 0.48);
        fillSouth.position.set(dimensions.width_x * 0.5, 1.2, -dimensions.length_y - 2.0);
        fillSouth.target.position.set(dimensions.width_x * 0.5, 1.8, 0);
        scene.add(fillWest, fillWest.target, fillSouth, fillSouth.target);
    }

    const poses = buildPoses(model, dimensions);
    const doors = collectDoorRoots(model);
    const chairRoom = "revision" in asset && asset.revision === "R5"
        ? new ChairRoom(asset.manifest.layout, asset.manifest.starting_pose.feet_survey)
        : undefined;
    const syncChairs = chairRoom ? bindChairMeshes(model, chairRoom) : undefined;
    const cutaway: Object3D[] = [];
    const materials = new Set<Material>(), textures = new Set<Texture>();
    let meshes = 0, triangles = 0;
    model.traverse(node => {
        if (/^P507_(ARCH_(CEILING|WALL_EAST|EAST_|WINDOW_|ROLLER_|BLIND_)|CEILING)/.test(node.name)
            || /^(P507-(LIGHT|FAN|AC|PROJECTOR|CAMERA|WINDOW|BLIND)-|P507-POSTER-0[45]$)/.test(String(node.userData.survey_instance_id))) {
            cutaway.push(node);
        }
        if (!(node instanceof Mesh)) return;
        meshes++;
        triangles += (node.geometry.index?.count ?? node.geometry.attributes.position.count) / 3;
        for (const material of Array.isArray(node.material) ? node.material : [node.material]) {
            materials.add(material);
            for (const value of Object.values(material)) if (value instanceof Texture) textures.add(value);
        }
    });
    const textureEstimateBytes = [...textures].reduce((sum, texture) => {
        const image = texture.image as { width?: number; height?: number } | undefined;
        return sum + (image?.width ?? 0) * (image?.height ?? 0) * 4 * (texture.generateMipmaps ? 4 / 3 : 1);
    }, 0);
    const camera = new PerspectiveCamera(70, 1, .04, 70);
    const context = renderer.getContext();
    const debugInfo = context.getExtension("WEBGL_debug_renderer_info");
    const resize = () => {
        renderer.setSize(canvas.clientWidth, canvas.clientHeight, false);
        camera.aspect = canvas.clientWidth / Math.max(1, canvas.clientHeight);
        camera.updateProjectionMatrix();
    };
    let active = "Mặt bằng";
    const render = () => renderer.render(scene, camera);
    const aim = (key: string) => {
        const pose = poses[key];
        if (!pose) throw new Error("Góc xem không hợp lệ");
        active = key;
        picker.value = key;
        for (const node of cutaway) node.visible = !pose.cutaway;
        for (const { node, open, closed } of doors) {
            (pose.closedDoor ? closed : open).decompose(node.position, node.quaternion, node.scale);
        }
        if (chairRoom && syncChairs) {
            for (const entry of chairRoom.entries.values()) {
                entry.state = pose.pullChairs ? "pulled-out" : "stored";
                entry.offset = pose.pullChairs ? 1 : 0;
            }
            syncChairs();
        }
        renderer.shadowMap.needsUpdate = revision === "r5";
        camera.position.copy(pose.position);
        camera.fov = pose.fov;
        camera.lookAt(pose.target);
        camera.updateProjectionMatrix();
        render();
    };
    const onResize = () => { resize(); render(); };
    window.addEventListener("resize", onResize, { signal: lifetime.signal });
    lifetime.signal.addEventListener("abort", () => {
        disposeRoom(model);
        renderer.dispose();
        delete window.__P507_R5_REVIEW__;
    }, { once: true });
    picker.replaceChildren(...Object.keys(poses).map(key => new Option(key, key)));
    picker.addEventListener("change", () => aim(picker.value), { signal: lifetime.signal });
    picker.disabled = false;
    resize();
    aim("Mặt bằng");
    const firstRenderMs = performance.now() - loadStart;
    const label = revision === "r5" ? "R5 PROPOSAL / PROVISIONAL / SYNTHETIC / VIRTUAL ADAPTATION" : "R4 frozen";
    status.textContent = `${label} · ${dimensions.width_x} × ${dimensions.length_y} × ${dimensions.height_z} m`;
    status.dataset.loaded = revision;

    window.__P507_R5_REVIEW__ = {
        poses: Object.keys(poses),
        aim,
        snapshot: () => ({
            revision, modelSha256: asset.hash, modelBytes: asset.manifest.model_bytes, dimensions, active,
            position: camera.position.toArray(), target: poses[active].target.toArray(), fov: camera.fov,
            viewport: [canvas.width, canvas.height], dpr: renderer.getPixelRatio(), cutaway: !!poses[active].cutaway,
            renderer: debugInfo ? context.getParameter(debugInfo.UNMASKED_RENDERER_WEBGL) : context.getParameter(context.RENDERER),
            meshes, triangles, materials: materials.size, textures: textures.size, textureEstimateBytes,
            parsedMs, firstRenderMs, drawCalls: renderer.info.render.calls, visibleTriangles: renderer.info.render.triangles,
            doorsWithHinge: doors.length,
        }),
        measure: async (warmupMs, sampleMs) => {
            await new Promise<void>((resolve, reject) => {
                let started: number | undefined;
                const warm = (time: number) => {
                    if (lifetime.signal.aborted || context.isContextLost()) {
                        reject(new Error("Render bị gián đoạn")); return;
                    }
                    started ??= time;
                    render();
                    if (time - started >= warmupMs) resolve();
                    else requestAnimationFrame(warm);
                };
                requestAnimationFrame(warm);
            });
            const intervals: number[] = [];
            await new Promise<void>((resolve, reject) => {
                let started: number | undefined, previous: number | undefined;
                const sample = (time: number) => {
                    if (lifetime.signal.aborted || document.hidden || context.isContextLost()) {
                        reject(new Error("Đo khung hình bị gián đoạn")); return;
                    }
                    started ??= time;
                    if (previous !== undefined) intervals.push(time - previous);
                    previous = time;
                    render();
                    if (time - started >= sampleMs && intervals.length >= 10) resolve();
                    else requestAnimationFrame(sample);
                };
                requestAnimationFrame(sample);
            });
            return frameTiming(intervals);
        },
    };
}

if (!import.meta.env.DEV) status.textContent = "Trang đối chiếu chỉ chạy ở môi trường Vite DEV.";
else {
    const revision = new URLSearchParams(location.search).get("revision") === "r4" ? "r4" : "r5";
    run(revision).catch(error => { status.textContent = String(error); });
}
