import { useFrame, useThree } from "@react-three/fiber";
import { useEffect, useRef, type RefObject } from "react";
import { Raycaster, type Object3D } from "three";
import { displacement, InputState, type Navigation, PLAYER, SPAWN, type Point } from "../p507-e1/core.ts";
import type { Action, ChairRoom } from "../p507-r5/chairs.ts";
import { intersectLogical, pointerRay } from "./runtime.ts";

declare global {
    interface Window {
        __P507_R5_TEST__?: {
            place(point: Point, yaw: number): void;
            occupyAll(): void;
            blocked(a: Point, b: Point): string | null;
        };
    }
}

export type DeskAction = "forward" | "back" | "left" | "right" | "turn-left" | "turn-right" | "reset" | "focus";
const walkKeys = ["KeyW", "KeyS", "KeyA", "KeyD"];
const directions: Partial<Record<DeskAction, Point>> = {
    forward: [1, 0], back: [-1, 0], left: [0, -1], right: [0, 1],
};

export function Desktop({ room, ids, nav, chairRoom, enabled, pick, blocked, controls, chairCommand }: {
    room: Object3D; ids: Set<string>; nav: Pick<Navigation, "blocked" | "move">; chairRoom?: ChairRoom; enabled: boolean;
    pick(id: string | null): void; blocked(id: string | null): void;
    controls: RefObject<((action: DeskAction) => void) | null>;
    chairCommand: RefObject<((id: string, action: Action) => string | null) | null>;
}) {
    const { gl, get } = useThree();
    const step = useRef<(dt: number) => void>(null);
    useEffect(() => {
        if (!enabled) return;
        const canvas = gl.domElement;
        const camera = get().camera;
        const input = new InputState();
        const ray = new Raycaster();
        const spawn = chairRoom?.spawn ?? SPAWN;
        let position: Point = [...spawn];
        let eye = PLAYER.eye;
        let yaw = -Math.PI / 2;
        let pitch = 0;
        let drag: { id: number; x: number; y: number; moved: boolean } | null = null;
        const sync = () => {
            camera.position.set(position[0], eye, position[1]);
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
                chairRoom?.reset();
                position = [...spawn];
                eye = PLAYER.eye;
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
        chairCommand.current = (id, action) => {
            if (!chairRoom) return "R4 không có thao tác ghế";
            const chair = chairRoom.entries.get(id)?.chair;
            const failure = chairRoom.action(id, action, { mode: "web", position });
            if (failure || !chair) return failure;
            if (action === "sit" || action === "stand") {
                const [x, y, z] = action === "sit" ? chair.seat_eye : chair.stand;
                position = [x, -y];
                eye = action === "sit" ? z : PLAYER.eye;
                if (action === "sit") {
                    yaw = chair.orientation_deg * Math.PI / 180;
                    pitch = 0;
                }
                clear();
                sync();
            }
            return null;
        };
        step.current = dt => {
            if (chairRoom && !chairRoom.seat && eye !== PLAYER.eye) {
                position = [...spawn];
                eye = PLAYER.eye;
                yaw = -Math.PI / 2;
                pitch = 0;
                sync();
            }
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
        if (import.meta.env.DEV && chairRoom && location.pathname === "/tests/r5-walk.html") {
            window.__P507_R5_TEST__ = {
                place(point, view) {
                    if (chairRoom.seat || chairRoom.blocked(point, point) || !Number.isFinite(view)) {
                        throw new Error("Invalid walk fixture placement");
                    }
                    clear();
                    position = [...point];
                    eye = PLAYER.eye;
                    yaw = view;
                    pitch = 0;
                    sync();
                },
                occupyAll() {
                    chairRoom.reset();
                    for (const entry of chairRoom.entries.values()) {
                        entry.state = "occupied";
                        entry.offset = 1;
                    }
                },
                blocked: (a, b) => chairRoom.blocked(a, b),
            };
            listeners.signal.addEventListener("abort", () => { delete window.__P507_R5_TEST__; });
        }
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
            chairCommand.current = null;
            step.current = null;
        };
    }, [enabled, gl, get, room, ids, nav, chairRoom, pick, blocked, controls, chairCommand]);
    useFrame((_, dt) => step.current?.(dt));
    return null;
}
