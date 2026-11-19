import { useFrame, useThree } from "@react-three/fiber";
import { useEffect, useRef, type RefObject } from "react";
import { Raycaster, type Object3D } from "three";
import { displacement, InputState, Navigation, PLAYER, SPAWN, type Point } from "../p507-e1/core.ts";
import { intersectLogical, pointerRay } from "./runtime.ts";

export type DeskAction = "forward" | "back" | "left" | "right" | "turn-left" | "turn-right" | "reset" | "focus";
const walkKeys = ["KeyW", "KeyS", "KeyA", "KeyD"];
const directions: Partial<Record<DeskAction, Point>> = {
    forward: [1, 0], back: [-1, 0], left: [0, -1], right: [0, 1],
};

export function Desktop({ room, ids, nav, enabled, pick, blocked, controls }: {
    room: Object3D; ids: Set<string>; nav: Navigation; enabled: boolean;
    pick(id: string | null): void; blocked(id: string | null): void;
    controls: RefObject<((action: DeskAction) => void) | null>;
}) {
    const { gl, get } = useThree();
    const step = useRef<(dt: number) => void>(null);
    useEffect(() => {
        if (!enabled) return;
        const canvas = gl.domElement;
        const camera = get().camera;
        const input = new InputState();
        const ray = new Raycaster();
        let position: Point = [...SPAWN];
        let yaw = -Math.PI / 2;
        let pitch = 0;
        let drag: { id: number; x: number; y: number; moved: boolean } | null = null;
        const sync = () => {
            camera.position.set(position[0], PLAYER.eye, position[1]);
            camera.rotation.set(pitch, yaw, 0, "YXZ");
            camera.updateMatrixWorld();
        };
        const look = (x: number, y: number) => {
            yaw -= x;
            pitch = Math.max(-1.45, Math.min(1.45, pitch - y));
            sync();
        };
        const move = (delta: Point) => {
            if (!delta[0] && !delta[1]) return;
            const next = nav.move(position, delta);
            position = next.position;
            blocked(next.reason);
            sync();
        };
        const clear = () => {
            input.clear();
            drag = null;
            if (document.pointerLockElement === canvas) document.exitPointerLock();
        };
        const select = (x: number, y: number) => {
            pointerRay(ray, camera, canvas, x, y);
            pick(intersectLogical(ray, room, ids));
        };
        controls.current = action => {
            const direction = directions[action];
            if (direction) move(displacement(...direction, yaw, PLAYER.maxDelta));
            if (action === "turn-left") look(-0.16, 0);
            if (action === "turn-right") look(0.16, 0);
            if (action === "reset") {
                clear();
                position = [...SPAWN];
                yaw = -Math.PI / 2;
                pitch = 0;
                pick(null);
                blocked(null);
                sync();
            }
            if (action === "focus") {
                canvas.focus();
                try { void canvas.requestPointerLock?.()?.catch(() => {}); } catch { /* keyboard still usable */ }
            }
        };
        step.current = dt => {
            const [forward, strafe] = input.axes();
            move(displacement(forward, strafe, yaw, dt));
        };
        const down = (event: KeyboardEvent) => {
            if (document.activeElement !== canvas && document.pointerLockElement !== canvas) return;
            if (event.code === "Escape") clear();
            if (event.code === "Enter" && event.target === canvas) {
                event.preventDefault();
                const box = canvas.getBoundingClientRect();
                select(box.left + box.width / 2, box.top + box.height / 2);
            }
            if (walkKeys.includes(event.code)) {
                event.preventDefault();
                input.active = true;
                input.key(event.code, true);
            }
            if (event.code === "ArrowLeft" || event.code === "ArrowRight") {
                event.preventDefault();
                look(event.code === "ArrowLeft" ? -0.055 : 0.055, 0);
            }
        };
        const keyUp = (event: KeyboardEvent) => input.key(event.code, false);
        const lock = () => input.lock(document.pointerLockElement === canvas);
        const pointerDown = (event: PointerEvent) => {
            if (!event.isPrimary || event.button !== 0) return;
            canvas.focus({ preventScroll: true });
            drag = { id: event.pointerId, x: event.clientX, y: event.clientY, moved: false };
            if (document.pointerLockElement !== canvas) canvas.setPointerCapture(event.pointerId);
        };
        const pointerMove = (event: PointerEvent) => {
            if (document.pointerLockElement === canvas) {
                look(event.movementX * 0.002, event.movementY * 0.002);
            } else if (drag?.id === event.pointerId) {
                const dx = event.clientX - drag.x, dy = event.clientY - drag.y;
                if (!drag.moved && Math.hypot(dx, dy) < 5) return;
                drag = { id: drag.id, x: event.clientX, y: event.clientY, moved: true };
                look(dx * 0.004, dy * 0.004);
            }
        };
        const pointerUp = (event: PointerEvent) => {
            if (drag?.id === event.pointerId && !drag.moved) select(event.clientX, event.clientY);
            drag = null;
        };
        const cancel = () => { drag = null; };
        const hide = () => { if (document.hidden) clear(); };
        const listeners = new AbortController();
        const options = { signal: listeners.signal };
        canvas.tabIndex = 0;
        canvas.setAttribute("aria-label", "Cảnh P507 tương tác");
        canvas.addEventListener("pointerdown", pointerDown, options);
        canvas.addEventListener("pointermove", pointerMove, options);
        canvas.addEventListener("pointerup", pointerUp, options);
        canvas.addEventListener("pointercancel", cancel, options);
        canvas.addEventListener("lostpointercapture", cancel, options);
        canvas.addEventListener("blur", clear, options);
        document.addEventListener("pointerlockchange", lock, options);
        document.addEventListener("pointerlockerror", clear, options);
        document.addEventListener("keydown", down, options);
        document.addEventListener("keyup", keyUp, options);
        document.addEventListener("visibilitychange", hide, options);
        window.addEventListener("blur", clear, options);
        window.addEventListener("pagehide", clear, options);
        blocked(null);
        sync();
        return () => {
            listeners.abort();
            clear();
            controls.current = null;
            step.current = null;
        };
    }, [enabled, gl, get, room, ids, nav, pick, blocked, controls]);
    useFrame((_, dt) => step.current?.(dt));
    return null;
}
