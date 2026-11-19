import { Raycaster, Vector2, Vector3, type Camera, type Object3D, type Texture, type WebGLRenderer } from "three";
import { logicalId, type Point } from "../p507-e1/core.ts";

export function visibleRoomHit(ray: Raycaster, room: Object3D) {
    return ray.intersectObject(room, true).find(hit => {
        for (let node: Object3D | null = hit.object; node; node = node.parent) {
            if (!node.visible) return false;
        }
        return true;
    });
}

export function intersectLogical(ray: Raycaster, room: Object3D, ids: Set<string>) {
    const first = visibleRoomHit(ray, room);
    return first ? logicalId(first.object, ids) : null;
}

export function tabletopCutaway(room: Object3D, ids: Set<string>) {
    const hidden: Object3D[] = [];
    room.traverse(node => {
        // R4's anonymous ceiling and perimeter shells cover the interior when seen from above.
        if (!node.visible || !/^P507_ARCH_(CEILING_|WALL_)/.test(node.name)) return;
        if (logicalId(node, ids)) return;
        const subtree = new Set<string>();
        node.traverse(child => {
            const id = child.userData.survey_instance_id;
            if (typeof id === "string") subtree.add(id);
        });
        if (subtree.size) return;
        node.visible = false;
        hidden.push(node);
    });
    return () => hidden.forEach(node => { node.visible = true; });
}

export function pointerRay(ray: Raycaster, camera: Camera, element: HTMLCanvasElement, x: number, y: number) {
    const rect = element.getBoundingClientRect();
    const center = document.pointerLockElement === element;
    camera.updateMatrixWorld();
    ray.setFromCamera(center ? new Vector2() :
        new Vector2(2 * (x - rect.left) / rect.width - 1, 1 - 2 * (y - rect.top) / rect.height), camera);
}

export function disposeRoom(room: Object3D) {
    const resources = new Set<{ dispose(): void }>();
    room.traverse(node => {
        if (!("isMesh" in node) || !("geometry" in node) || !("material" in node)) return;
        resources.add(node.geometry as { dispose(): void });
        for (const material of Array.isArray(node.material) ? node.material : [node.material]) {
            resources.add(material);
            for (const value of Object.values(material)) {
                if (value && (value as Texture).isTexture) resources.add(value as Texture);
            }
        }
    });
    resources.forEach(resource => resource.dispose());
}

export function thumbstick(session: XRSession): Point {
    const input = Array.from(session.inputSources).find(source =>
        source.targetRayMode === "tracked-pointer" && source.gamepad?.mapping === "xr-standard" &&
        source.gamepad.axes.length >= 4 && Math.hypot(source.gamepad.axes[2], source.gamepad.axes[3]) > 0.2);
    return input?.gamepad ? [-input.gamepad.axes[3], input.gamepad.axes[2]] : [0, 0];
}

export function previewHit(hit: Vector3, head: Vector3) {
    const horizontal = Math.hypot(hit.x - head.x, hit.z - head.z);
    const below = head.y - hit.y;
    return horizontal >= 0.35 && horizontal <= 2.5 && below >= 0.15 && below <= 1.7;
}

export function rendererInfo(gl: WebGLRenderer) {
    const context = gl.getContext();
    const debug = context.getExtension("WEBGL_debug_renderer_info");
    return debug ? context.getParameter(debug.UNMASKED_RENDERER_WEBGL) : "UNKNOWN";
}
