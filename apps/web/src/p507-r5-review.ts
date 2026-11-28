import {
    ACESFilmicToneMapping, Box3, Color, DirectionalLight, Group, HemisphereLight, Matrix4,
    Material, Mesh, Object3D, PerspectiveCamera, Scene, Texture, Vector3, WebGLRenderer,
} from "three";
import { loadFrozenP507 } from "./p507-e1/load";
import { loadR5 as loadR5P507 } from "./p507-r5/load";
import { disposeRoom } from "./p507-m5/runtime";

type Revision = "r4" | "r5";
type Dimensions = { width_x: number; length_y: number; height_z: number };
type CameraPose = { position: Vector3; target: Vector3; fov: number; cutaway?: boolean; closedDoor?: boolean };
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
    const add = (name: string, position: number[], target: number[], fov: number, cutaway = false) => {
        poses[name] = { position: new Vector3().fromArray(position), target: new Vector3().fromArray(target), fov, cutaway };
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
    add("Mặt bằng", [w / 2, Math.max(w, l) * 1.21, -l / 2], [w / 2, 0, -l / 2 - .001], 55, true);
    add("Ba cụm bàn", [w + 3, h + 6, -l * .58], [w / 2, .5, -l / 2], 55, true);
    for (const cluster of ["A", "B", "C"]) {
        const at = center(new RegExp(`^P507-DESK-${cluster}`));
        add(`Cụm ${cluster}`, [at.x, h + 3.8, at.z - .01], at.toArray(), 51, true);
    }
    const tv = center(/^P507-TV-LARGE$/);
    add("TV và tủ trưng bày", [2.65, 1.65, tv.z + 1.8], tv.toArray(), 78);
    const shelf = center(/^P507-UTILITY-SHELF$/);
    add("Kệ đồ", [2.55, shelf.y + .25, shelf.z], shelf.toArray(), 65);
    const utility = center(/^P507-(CABINET-FILES|FRIDGE|UTILITY-SHELF|WASTE-BIN|SHOE-RACK|WHITEBOARD)$/);
    add("Khu tiện ích", [Math.min(w * .57, 4.8), 2.0, utility.z], [.3, 1.15, utility.z], 94);
    add("Cửa sổ và poster", [1.15, 1.7, -l * .48], [w - .05, 1.9, -l * .59], 81);
    add("Tường khung ảnh", [w * .63, 1.65, 2.55 - l], [w * .63, 2.1, .08 - l], 72);
    add("Tường logo", [w / 2, 1.65, -3.6], [w / 2, 1.9, -.08], 70);
    add("Trần", [w / 2, 1.65, -l / 2], [w / 2, h, -l / 2 - .001], 132);
    const door = center(/^P507-DOOR-LEAF-/);
    add("Cửa mở ra ngoài", [-2.5, 1.65, door.z], [.1, 1.34, door.z], 78);
    add("Cửa đóng", [-2.5, 1.65, door.z], [.1, 1.34, door.z], 78);
    poses["Cửa đóng"].closedDoor = true;
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
    const scene = new Scene();
    scene.background = new Color("#d9dedc");
    const dimensions = asset.manifest.virtual_dimensions;
    const daylight = new DirectionalLight(0xfff4e3, 2);
    daylight.position.set(dimensions.width_x - .35, dimensions.height_z - .4, -dimensions.length_y * .55);
    daylight.target.position.set(dimensions.width_x * .3, 0, -dimensions.length_y * .55);
    scene.add(new HemisphereLight(0xe6efff, 0xc9bfa9, 1.25), daylight, daylight.target, model);

    const poses = buildPoses(model, dimensions);
    const doors = collectDoorRoots(model);
    const cutaway: Object3D[] = [];
    const materials = new Set<Material>(), textures = new Set<Texture>();
    let meshes = 0, triangles = 0;
    model.traverse(node => {
        if (/^P507_(ARCH_(CEILING|WALL_EAST|EAST_|WINDOW_|ROLLER_|BLIND_)|CEILING)/.test(node.name)
            || /^(P507-(LIGHT|FAN|AC|PROJECTOR|CAMERA|WINDOW|BLIND)-)/.test(String(node.userData.survey_instance_id))) {
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
