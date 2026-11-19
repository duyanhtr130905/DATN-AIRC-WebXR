import { XROrigin, useXR } from "@react-three/xr";
import { useFrame, useThree } from "@react-three/fiber";
import { useEffect, useMemo, useRef, useState, type RefObject } from "react";
import { BufferAttribute, BufferGeometry, CanvasTexture, Group, Line, LineBasicMaterial, Matrix4, Mesh, Quaternion, Raycaster, SRGBColorSpace, Vector3 } from "three";
import { displacement, Navigation, SPAWN, type Point } from "../p507-e1/core.ts";
import { intersectLogical, previewHit, thumbstick } from "./runtime.ts";

type Preview = "waiting" | "surface" | "unavailable" | "placed";
export const provenance = "R4 · PROVISIONAL / USER_REPORTED · quyền đang chờ";
export type Detail = { id: string; kind: string; status: string; source: string; position: string };

function makePanel() {
    const canvas = document.createElement("canvas");
    canvas.width = 1024;
    canvas.height = 320;
    const texture = new CanvasTexture(canvas);
    texture.colorSpace = SRGBColorSpace;
    return { canvas, texture };
}

export function Immersive({ nav, ids, model, mount, detail, ar, pick, exit, record }: {
    nav: Navigation; ids: Set<string>; model: Group; mount: RefObject<Group | null>;
    detail?: Detail; ar: boolean; pick(id: string | null): void; exit(): void;
    record(event: string): void;
}) {
    const session = useXR(state => state.session);
    const { gl } = useThree();
    const origin = useRef<Group>(null);
    const panel = useRef<Mesh>(null);
    const hitSource = useRef<XRHitTestSource>(null);
    const target = useRef<Vector3>(null);
    const previewState = useRef<Preview>("waiting");
    const [preview, setPreview] = useState<Preview>("waiting");
    const [stationary, setStationary] = useState(false);
    const [inputs, setInputs] = useState(0);
    const lastSafe = useRef<Point>([...SPAWN]);
    const collision = useRef<string | null>(null);
    const navBlock = useRef<string | null>(null);
    const anchor = useRef<Vector3>(null);
    const scratch = useRef({
        ray: new Raycaster(), rayRotation: new Quaternion(), matrix: new Matrix4(),
        head: new Vector3(), headQuaternion: new Quaternion(), direction: new Vector3(), world: new Vector3(),
    });
    const beam = useMemo(() => {
        const geometry = new BufferGeometry();
        geometry.setAttribute("position", new BufferAttribute(new Float32Array(6), 3));
        const line = new Line(geometry, new LineBasicMaterial({ color: "#fff2ad" }));
        line.frustumCulled = false;
        line.visible = false;
        return line;
    }, []);
    const [label] = useState(makePanel);
    function updatePreview(value: Preview) {
        if (previewState.current !== value) {
            previewState.current = value;
            setPreview(value);
            record("ar:" + value);
        }
    }
    const exitRef = useRef(exit);
    exitRef.current = exit;

    useEffect(() => {
        if (!session) return;
        const group = mount.current!;
        const view = origin.current!;
        const selectedPanel = panel.current!;
        target.current = null;
        anchor.current = null;
        lastSafe.current = [...SPAWN];
        collision.current = null;
        navBlock.current = null;
        view.position.set(ar ? 0 : SPAWN[0], 0, ar ? 0 : SPAWN[1]);
        group.visible = !ar;
        group.position.set(0, 0, 0);
        group.scale.setScalar(ar ? 0.08 : 1);
        previewState.current = "waiting";
        setPreview("waiting");
        setStationary(false);
        let cancelled = false;

        const inputChanged = () => {
            setInputs(session.inputSources.length);
            record("inputs:" + session.inputSources.length);
        };
        const visible = () => {
            target.current = null;
            record("visibility:" + session.visibilityState);
        };
        const select = (event: XRInputSourceEvent) => {
            const reference = gl.xr.getReferenceSpace();
            if (!reference || session.visibilityState !== "visible") return;
            const pose = event.frame.getPose(event.inputSource.targetRaySpace, reference);
            if (!pose) return;
            const { ray, rayRotation, matrix } = scratch.current;
            view.updateMatrixWorld();
            ray.ray.origin.setFromMatrixPosition(matrix.fromArray(pose.transform.matrix)).applyMatrix4(view.matrixWorld);
            rayRotation.setFromRotationMatrix(matrix);
            ray.ray.direction.set(0, 0, -1).applyQuaternion(rayRotation).transformDirection(view.matrixWorld);
            const ui = ray.intersectObject(selectedPanel, false)[0];
            if (ui?.uv && ui.uv.y < 0.24 && ui.uv.x > 0.69) {
                record("exit:world-panel");
                exitRef.current();
                return;
            }
            if (ar && previewState.current !== "placed") {
                if (!target.current || previewState.current !== "surface") return;
                anchor.current = target.current.clone();
                group.position.copy(anchor.current).add(new Vector3(-0.08 * 3.45, 0, 0.08 * 4.6575));
                group.visible = true;
                group.updateMatrixWorld(true);
                updatePreview("placed");
                return;
            }
            if (!group.visible) return;
            const id = intersectLogical(ray, model, ids);
            pick(id);
            record("select:" + (id ?? "none"));
        };
        const released = () => record("selectend");
        session.addEventListener("select", select);
        session.addEventListener("selectend", released);
        session.addEventListener("inputsourceschange", inputChanged);
        session.addEventListener("visibilitychange", visible);
        inputChanged();
        if (ar) {
            const request = async () => {
                try {
                    const viewer = await session.requestReferenceSpace("viewer");
                    if (!session.requestHitTestSource) throw new Error("hit-test unavailable");
                    const source = await session.requestHitTestSource({ space: viewer });
                    if (!source) throw new Error("hit-test unavailable");
                    if (cancelled) source.cancel();
                    else hitSource.current = source;
                } catch {
                    if (!cancelled) updatePreview("unavailable");
                }
            };
            void request();
        }
        return () => {
            cancelled = true;
            hitSource.current?.cancel();
            hitSource.current = null;
            target.current = null;
            session.removeEventListener("select", select);
            session.removeEventListener("selectend", released);
            session.removeEventListener("inputsourceschange", inputChanged);
            session.removeEventListener("visibilitychange", visible);
            group.visible = true;
            group.position.set(0, 0, 0);
            group.scale.setScalar(1);
            group.updateMatrixWorld(true);
        };
        // A fresh effect owns the listeners and hit-test source for each session.
    }, [session, ar, gl, ids, model, mount, pick, record]);

    useEffect(() => {
        const ctx = label.canvas.getContext("2d")!;
        const lines = detail ? [detail.id, detail.kind + " · " + detail.status,
            "Nguồn " + detail.source] : [
            ar ? "P507 · Bản xem thử để bàn" : "P507 · Tham quan VR",
            ar ? (preview === "unavailable" ? "Hit test không khả dụng" :
                preview === "placed" ? "Chạm để chọn đối tượng" :
                preview === "surface" ? "Chạm để đặt mô hình" : "Hướng máy về mặt phẳng gần") :
                stationary ? "Dừng lại và trở về vị trí hợp lệ" : "Chọn bằng tia · Di chuyển bằng cần điều khiển",
            ar ? "Mô hình ảo thu nhỏ, không căn chỉnh 1:1" : "Thiết bị nhập " + inputs,
        ];
        ctx.fillStyle = "#17332e";
        ctx.fillRect(0, 0, 1024, 320);
        ctx.fillStyle = "#f9faf4";
        ctx.font = "bold 48px sans-serif";
        ctx.fillText(lines[0], 32, 66, 950);
        ctx.font = "36px sans-serif";
        ctx.fillText(lines[1], 32, 126, 950);
        ctx.fillText(lines[2], 32, 180, 950);
        ctx.fillStyle = "#e5cdf0";
        ctx.font = "28px sans-serif";
        ctx.fillText(provenance, 32, 230, 950);
        ctx.fillStyle = "#f1e2c5";
        ctx.fillRect(707, 244, 317, 76);
        ctx.fillStyle = "#172f29";
        ctx.font = "bold 33px sans-serif";
        ctx.fillText("Thoát XR", 766, 294);
        label.texture.needsUpdate = true;
    }, [detail, ar, preview, stationary, inputs, label]);
    useEffect(() => () => {
        label.texture.dispose();
        beam.geometry.dispose();
        beam.material.dispose();
    }, [label, beam]);

    useFrame((_, dt, frame) => {
        const reference = gl.xr.getReferenceSpace();
        const view = origin.current;
        const group = mount.current;
        const ui = panel.current;
        beam.visible = false;
        if (!frame || !reference || !view || !group || !ui || session?.visibilityState !== "visible") return;
        const pose = frame.getViewerPose(reference);
        if (!pose) {
            group.visible = false;
            target.current = null;
            return;
        }
        const { matrix, head, headQuaternion, direction, world } = scratch.current;
        head.setFromMatrixPosition(matrix.fromArray(pose.transform.matrix));
        headQuaternion.setFromRotationMatrix(matrix);
        if (!ar) {
            const actual: Point = [view.position.x + head.x, view.position.z + head.z];
            const path = nav.blocked(lastSafe.current, actual);
            if (collision.current !== path) {
                collision.current = path;
                setStationary(Boolean(path));
                record("physical-boundary:" + (path ?? "clear"));
            }
            group.visible = !path;
            if (!path) {
                const [forward, strafe] = thumbstick(session);
                direction.set(0, 0, -1).applyQuaternion(headQuaternion);
                const yaw = Math.atan2(-direction.x, -direction.z);
                const next = nav.move(actual, displacement(forward, strafe, yaw, dt));
                if (view.position.x !== next.position[0] - head.x || view.position.z !== next.position[1] - head.z) {
                    view.position.x = next.position[0] - head.x;
                    view.position.z = next.position[1] - head.z;
                }
                lastSafe.current = next.position;
                if (navBlock.current !== next.reason) {
                    navBlock.current = next.reason;
                    record("thumbstick-boundary:" + (next.reason ?? "clear"));
                }
            }
        } else {
            group.visible = Boolean(anchor.current);
            if (hitSource.current && !anchor.current) {
                const hit = frame.getHitTestResults(hitSource.current)[0]?.getPose(reference);
                target.current = null;
                if (hit) {
                    world.setFromMatrixPosition(matrix.fromArray(hit.transform.matrix));
                    direction.set(0, 1, 0).transformDirection(matrix);
                    if (direction.y >= 0.85 && previewHit(world, head)) target.current = world.clone();
                }
                updatePreview(target.current ? "surface" : "waiting");
            }
        }
        view.updateMatrixWorld();
        ui.position.set(0, 0.27, -1.35).applyQuaternion(headQuaternion).add(head).applyMatrix4(view.matrixWorld);
        ui.quaternion.copy(headQuaternion);
        ui.updateMatrixWorld();
        const sources = Array.from(session.inputSources);
        const source = sources.find(input => input.targetRayMode === "tracked-pointer" && input.handedness === "right") ??
            sources.find(input => input.targetRayMode === "tracked-pointer" || input.targetRayMode === "gaze");
        const sourcePose = source && frame.getPose(source.targetRaySpace, reference);
        if (sourcePose) {
            const ray = scratch.current.ray;
            matrix.fromArray(sourcePose.transform.matrix);
            ray.ray.origin.setFromMatrixPosition(matrix).applyMatrix4(view.matrixWorld);
            ray.ray.direction.set(0, 0, -1).transformDirection(matrix).transformDirection(view.matrixWorld);
            const end = ray.intersectObject(ui, false)[0] ?? (group.visible ? ray.intersectObject(model, true)[0] : undefined);
            ray.ray.at(Math.min(end?.distance ?? 3, 3), world);
            beam.geometry.attributes.position.setXYZ(0, ...ray.ray.origin.toArray());
            beam.geometry.attributes.position.setXYZ(1, ...world.toArray());
            beam.geometry.attributes.position.needsUpdate = true;
            beam.visible = true;
        }
    });

    return <>
        <XROrigin ref={origin} />
        <primitive object={beam} />
        <mesh ref={panel} visible={Boolean(session)} renderOrder={10}>
            <planeGeometry args={[0.94, 0.294]} />
            <meshBasicMaterial map={label.texture} depthTest={false} depthWrite={false} toneMapped={false} />
        </mesh>
    </>;
}
