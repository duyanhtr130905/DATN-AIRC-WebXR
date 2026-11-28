import { Canvas, useFrame, useThree } from "@react-three/fiber";
import { XR, useXR } from "@react-three/xr";
import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { Box3, Group, Vector3, type WebGLRenderer } from "three";
import { ErrorBoundary } from "../components/ErrorBoundary.tsx";
import { Navigation, logicalId, type Point } from "../p507-e1/core.ts";
import { loadFrozenP507 } from "../p507-e1/load.ts";
import { reference } from "../p507-e1/scene-contract.ts";
import { ChairRoom, labels, type Action } from "../p507-r5/chairs.ts";
import { bindChairMeshes, loadR5 } from "../p507-r5/load.ts";
import { Desktop, type DeskAction } from "./Desktop.tsx";
import { Immersive, provenance, type Detail } from "./Immersive.tsx";
import { disposeRoom, rendererInfo } from "./runtime.ts";
import { modes, useP507Session } from "./session.ts";
import { interruptTiming, sampleTiming, startTiming, type TimingCapture, type TimingMode } from "./timing.ts";
import "./visitor.css";

const frozenIds = new Set(reference.records.map(record => record.id));
const r5Label = "R5 PROPOSAL / PROVISIONAL / SYNTHETIC / VIRTUAL ADAPTATION";
const controls: [DeskAction, string][] = [
    ["forward", "Tiến"], ["back", "Lùi"], ["left", "Sang trái"], ["right", "Sang phải"],
    ["turn-left", "Xoay trái"], ["turn-right", "Xoay phải"], ["reset", "Về điểm bắt đầu"],
    ["focus", "Dùng chuột và bàn phím"],
];
const supportLabels = {
    checking: "Đang kiểm tra", supported: "Có hỗ trợ", unsupported: "Thiết bị không hỗ trợ",
    denied: "Bị chặn bởi quyền hoặc chính sách", unavailable: "Không kiểm tra được runtime",
    insecure: "Cần ngữ cảnh bảo mật",
};
const statusLabels = {
    idle: "Bạn đang ở chế độ Web 3D.", requesting: "Đang yêu cầu phiên XR…",
    active: "Phiên XR đang hoạt động.", ended: "Đã thoát XR và trở về Web 3D.",
    denied: "Quyền XR bị từ chối. Bạn vẫn có thể dùng Web 3D.",
    unsupported: "Runtime không hỗ trợ chế độ này. Bạn vẫn có thể dùng Web 3D.",
    aborted: "Phiên XR bị hủy. Bạn có thể thử lại hoặc dùng Web 3D.",
    failed: "Lỗi runtime XR. Bạn có thể thử lại hoặc dùng Web 3D.",
    "context-lost": "Mất ngữ cảnh WebGL. Bạn vẫn có thể dùng danh sách đối tượng.",
};
type Asset = (Awaited<ReturnType<typeof loadFrozenP507>> & { revision: "R4" }) |
    Awaited<ReturnType<typeof loadR5>>;
type Evidence = {
    record(event: string): void;
    startTiming(mode: TimingMode, durationMs?: number): void;
    renderer?: string;
    frames: Record<string, number[]>;
    events: string[];
    timing?: TimingCapture;
    webPose?: { x: number; z: number; yaw: number; eye: number };
    r5Bounds?(id: string): { min: number[]; max: number[]; center: number[] } | undefined;
    snapshotR5?(): { chairs: Record<string, unknown>; moving?: string; seated?: string };
};
declare global { interface Window { __P507_M5__?: Evidence } }

function useEvidence() {
    const evidence = useRef<Evidence>(undefined);
    useEffect(() => {
        if (new URLSearchParams(location.search).get("evidence") !== "1") return;
        const events: string[] = [];
        const report: Evidence = {
            events, frames: {},
            record(event) { if (events.length < 800) events.push(event); },
            startTiming(mode, durationMs) { report.timing = startTiming(mode, durationMs); },
        };
        evidence.current = report;
        window.__P507_M5__ = report;
        return () => {
            evidence.current = undefined;
            if (window.__P507_M5__ === report) delete window.__P507_M5__;
        };
    }, []);
    return useCallback((event: string) => evidence.current?.record(event), []);
}

function FrameEvidence() {
    const gl = useThree(state => state.gl);
    const activeSession = useXR(state => state.session);
    const previous = useRef<{ mode: string; timestamp: number }>(undefined);
    useEffect(() => {
        if (!activeSession) return;
        const interrupt = () => interruptTiming(window.__P507_M5__?.timing);
        const handleVisibility = () => {
            if (activeSession.visibilityState !== "visible") interrupt();
        };
        activeSession.addEventListener("visibilitychange", handleVisibility);
        activeSession.addEventListener("end", interrupt);
        return () => {
            activeSession.removeEventListener("visibilitychange", handleVisibility);
            activeSession.removeEventListener("end", interrupt);
        };
    }, [activeSession]);
    useEffect(() => {
        const handleVisibility = () => {
            if (document.hidden && !gl.xr.getSession()) interruptTiming(window.__P507_M5__?.timing);
        };
        const handleLoss = () => interruptTiming(window.__P507_M5__?.timing);
        document.addEventListener("visibilitychange", handleVisibility);
        gl.domElement.addEventListener("webglcontextlost", handleLoss);
        return () => {
            interruptTiming(window.__P507_M5__?.timing);
            document.removeEventListener("visibilitychange", handleVisibility);
            gl.domElement.removeEventListener("webglcontextlost", handleLoss);
        };
    }, [gl]);
    useFrame((state, _, frame) => {
        const report = window.__P507_M5__;
        if (!report) return;
        const session = gl.xr.getSession();
        if (!session && report.snapshotR5) {
            const { position, rotation } = state.camera;
            report.webPose = { x: position.x, z: position.z, yaw: rotation.y, eye: position.y };
        }
        const mode = frame ? (session?.environmentBlendMode === "opaque" ? "vr" : "ar") : "web";
        const visible = session ? session.visibilityState === "visible" : !document.hidden;
        const timing = report.timing;
        if (timing) {
            if (timing.status === "waiting" && visible && mode === timing.mode) {
                const layer = session?.renderState.baseLayer;
                timing.framebuffer = layer ? [layer.framebufferWidth, layer.framebufferHeight] :
                    [gl.domElement.width, gl.domElement.height];
                timing.nominalHz = (session as (XRSession & { frameRate?: number }) | null)?.frameRate;
            }
            sampleTiming(timing, mode, visible, performance.now());
        }
        if (!visible) {
            previous.current = undefined;
            return;
        }
        report.renderer ??= rendererInfo(gl);
        const timestamp = frame?.predictedDisplayTime ?? state.clock.elapsedTime * 1000;
        const samples = report.frames[mode] ??= [];
        const last = previous.current;
        if (last?.mode === mode && samples.length < 360 && timestamp > last.timestamp) samples.push(timestamp - last.timestamp);
        previous.current = { mode, timestamp };
    });
    return null;
}

function ChairFrames({ model, room }: { model: Group; room: ChairRoom }) {
    const syncMesh = useMemo(() => bindChairMeshes(model, room), [model, room]);
    useEffect(() => {
        const evidence = window.__P507_M5__;
        if (!evidence) return;
        const known = new Set(room.chairIDs);
        evidence.r5Bounds = id => {
            if (!known.has(id)) return undefined;
            const bounds = new Box3();
            model.updateWorldMatrix(true, true);
            model.traverse(node => {
                if (node.userData.survey_instance_id !== id || logicalId(node.parent, known)) return;
                bounds.union(new Box3().setFromObject(node, true));
            });
            return bounds.isEmpty() ? undefined : {
                min: bounds.min.toArray(), max: bounds.max.toArray(), center: bounds.getCenter(new Vector3()).toArray(),
            };
        };
        return () => { delete evidence.r5Bounds; };
    }, [model, room]);
    useFrame((_, dt) => { room.tick(dt); syncMesh(); });
    return null;
}

function RendererLifecycle({ attach, contextLost, contextRestored }: {
    attach(renderer: WebGLRenderer | undefined): void; contextLost(): void; contextRestored(): void;
}) {
    const gl = useThree(state => state.gl);
    const callbacks = useRef({ contextLost, contextRestored });
    callbacks.current = { contextLost, contextRestored };
    useEffect(() => {
        const element = gl.domElement;
        const lost = (event: Event) => { event.preventDefault(); callbacks.current.contextLost(); };
        const restored = () => callbacks.current.contextRestored();
        element.addEventListener("webglcontextlost", lost);
        element.addEventListener("webglcontextrestored", restored);
        attach(gl);
        return () => {
            element.removeEventListener("webglcontextlost", lost);
            element.removeEventListener("webglcontextrestored", restored);
            attach(undefined);
        };
    }, [gl, attach]);
    return null;
}

function assetFailure(error: unknown) {
    const text = error instanceof Error ? error.message : "";
    if (text.includes("HTTP 404")) return "MISSING";
    if (/SHA-256|size budget/.test(text)) return "HASH_MISMATCH";
    if (error instanceof DOMException && error.name === "TimeoutError") return "TIMEOUT";
    if (!window.isSecureContext) return "INSECURE_CONTEXT";
    return "INVALID_ASSET";
}

export default function Visitor() {
    const isR5 = useMemo(() => new URLSearchParams(location.search).get("revision") === "r5", []);
    const revision = isR5 ? "R5" : "R4";
    const [asset, setAsset] = useState<Asset>();
    const [error, setError] = useState("");
    const [attempt, retry] = useState(0);
    const [selected, select] = useState<string | null>(null);
    const [blocked, setBlocked] = useState<string | null>(null);
    const [ready, setReady] = useState(false);
    const [chairMessage, setChairMessage] = useState("");
    const [, chairUpdate] = useState(0);
    const run = useRef<((action: DeskAction) => void) | null>(null);
    const mount = useRef<Group>(null);
    const chairCommand = useRef<((id: string, action: Action) => string | null) | null>(null);
    const clearSelection = useCallback(() => select(null), []);
    const xr = useP507Session(clearSelection);
    const attach = useCallback((renderer: WebGLRenderer | undefined) => {
        xr.renderer.current = renderer;
        setReady(Boolean(renderer));
    }, [xr.renderer]);
    const record = useEvidence();
    const chairRoom = useMemo(() => asset?.revision === "R5"
        ? new ChairRoom(asset.manifest.layout, asset.manifest.starting_pose.feet_survey, () => chairUpdate(n => n + 1))
        : undefined, [asset]);
    const nav = useMemo(() => chairRoom ?? (asset && new Navigation(asset.manifest)), [asset, chairRoom]);
    const footprint = useMemo<Point | undefined>(() => asset?.revision === "R5"
        ? [asset.manifest.virtual_dimensions.width_x, asset.manifest.virtual_dimensions.length_y] : undefined, [asset]);
    const ids = asset?.revision === "R5" ? asset.ids : isR5 ? undefined : frozenIds;
    const details = useMemo(() => new Map<string, Detail>(asset?.manifest.instances
        .filter(row => ids?.has(row.id)).map(row => [row.id, {
            id: row.id,
            kind: "logical_type" in row && typeof row.logical_type === "string"
                ? row.logical_type
                : asset.manifest.collision_proxies.find(proxy => proxy.id === row.id)?.kind ?? "UNKNOWN",
            status: row.status,
            source: String(row.survey_transform.source_kind ?? "UNKNOWN"),
            position: String(row.survey_transform.position_source ?? "UNKNOWN"),
        }])), [asset, ids]);
    const detail = selected ? details.get(selected) : undefined;

    useEffect(() => {
        const controller = new AbortController();
        let room: Group | undefined;
        setError("");
        setAsset(undefined);
        const signal = AbortSignal.any([controller.signal, AbortSignal.timeout(30000)]);
        const pending = isR5 ? loadR5(signal) : loadFrozenP507(signal).then(loaded => ({ ...loaded, revision: "R4" as const }));
        pending.then(loaded => {
            room = loaded.gltf.scene;
            if (signal.aborted) {
                disposeRoom(room);
                room = undefined;
                if (!controller.signal.aborted) setError(assetFailure(signal.reason));
            } else setAsset(loaded);
        }).catch(error => {
            if (!controller.signal.aborted) setError(assetFailure(error));
        });
        return () => {
            controller.abort();
            if (room) disposeRoom(room);
        };
    }, [attempt, isR5]);

    useEffect(() => {
        if (!chairRoom) return;
        const handleVisibility = () => {
            if (document.hidden) chairRoom.interrupt();
        };
        const hide = () => chairRoom.reset();
        document.addEventListener("visibilitychange", handleVisibility);
        window.addEventListener("pagehide", hide);
        const evidence = window.__P507_M5__;
        if (evidence) evidence.snapshotR5 = () => ({
            moving: chairRoom.moving, seated: chairRoom.seat?.id,
            chairs: Object.fromEntries([...chairRoom.chairIDs].map(id => [id, { pose: chairRoom.pose(id), state: chairRoom.state(id) }])),
        });
        return () => {
            document.removeEventListener("visibilitychange", handleVisibility);
            window.removeEventListener("pagehide", hide);
            if (evidence) delete evidence.snapshotR5;
        };
    }, [chairRoom]);
    useEffect(() => { setChairMessage(""); }, [selected]);
    useEffect(() => { record("session:" + xr.status + ":" + (xr.requested ?? "none")); }, [record, xr.status, xr.requested]);

    const disabled = !ready || xr.contextLost || xr.status === "requesting" || Boolean(xr.active);
    const chairState = selected ? chairRoom?.state(selected) : undefined;
    const dimensions = footprint ? `${footprint[0]} × ${footprint[1]} × 3,50` : "6,90 × 9,315 × 3,50";
    const lost = () => { chairRoom?.reset(); xr.lostContext(); };
    return <main className="p507-visitor">
        <nav aria-label="Ứng dụng">
            <a href="/">Không gian số AIRC</a>
            <a href="/?mode=p507">Digital Twin P507</a>
            {isR5 ? <a href="/?mode=p507-visit">Trở về R4</a> :
                <a href="/?mode=p507-visit&revision=r5">Xem đề xuất R5</a>}
        </nav>
        <h1>Tham quan P507</h1>
        <p className="notice">{isR5 ? r5Label : provenance}.
            {(!isR5 || footprint) && <> Mô hình ảo {dimensions} m.</>} Dữ liệu tại đây chỉ dùng để xem thử.</p>
        <section className="visitor-xr" aria-label="Chế độ WebXR">
            <h2>Trải nghiệm WebXR</h2>
            <p>AR là mô hình thu nhỏ để bàn có mặt cắt, không căn chỉnh 1:1 với phòng thật. VR dùng tuyến và vật cản ảo của {revision}.</p>
            {modes.map((mode, index) => <div key={mode} data-testid={"support-" + mode} data-support={xr.support[index]}>
                <button disabled={disabled || Boolean(chairRoom?.seat || chairRoom?.moving) || xr.support[index] !== "supported"} onClick={() => xr.enter(mode)}>
                    {mode === "immersive-vr" ? "Vào VR" : "Vào AR"}
                </button>
                <span>{supportLabels[xr.support[index]]}</span>
            </div>)}
            {xr.active && <button onClick={xr.exit}>Thoát XR</button>}
            <p role="status" data-testid="xr-status" data-status={xr.status} data-mode={xr.active}
                data-requested={xr.requested}>{statusLabels[xr.status]}</p>
        </section>
        <div className="workspace">
            <section className="scene visitor-scene" aria-label="Web 3D P507">
                {error ? <div className="visitor-asset">
                    <p role="alert" data-testid="asset-status" data-result={error}>{revision} không khả dụng. {isR5 ? "Có thể mở lại R4 bằng liên kết phía trên." : "Bạn có thể tiếp tục bằng danh sách."}</p>
                    <button onClick={() => retry(step => step + 1)}>Thử tải {revision} lại</button>
                </div> : asset && nav && ids && xr.store ?
                    <ErrorBoundary><Canvas gl={{ alpha: true }} dpr={[1, 1.5]} camera={{ fov: 78, near: 0.04, far: 60 }}
                        fallback={<p role="alert">WebGL không khả dụng. Hãy dùng danh sách đối tượng.</p>}>
                        <XR store={xr.store}>
                            <ambientLight intensity={0.75} />
                            <directionalLight position={[2, 8, -2]} intensity={2} />
                            <group ref={mount}><primitive object={asset.gltf.scene} /></group>
                            <RendererLifecycle attach={attach} contextLost={lost} contextRestored={xr.restoredContext} />
                            {chairRoom && <ChairFrames model={asset.gltf.scene} room={chairRoom} />}
                            <Desktop room={asset.gltf.scene} ids={ids} nav={nav} chairRoom={chairRoom} chairCommand={chairCommand}
                                enabled={!xr.active && !xr.contextLost && xr.status !== "requesting"}
                                pick={select} blocked={setBlocked} controls={run} />
                            <Immersive nav={nav} chairRoom={chairRoom} footprint={footprint} ids={ids} model={asset.gltf.scene} mount={mount} detail={detail} ar={xr.requested === "immersive-ar"}
                                pick={select} exit={xr.exit} record={record} />
                            {new URLSearchParams(location.search).get("evidence") === "1" && <FrameEvidence />}
                        </XR>
                    </Canvas></ErrorBoundary> : <p role="status">Đang kiểm tra {revision}…</p>}
            </section>
            <aside aria-label="Thông tin P507">
                {asset && <p data-testid="asset-status" data-result="E0_SCENE_PASS" data-sha={asset.hash}>{revision} đã kiểm tra · {asset.geometry.placedIDs} ID bố trí · 2 hồ sơ chưa bố trí</p>}
                <label>Đối tượng P507
                    <select value={selected ?? ""} onChange={event => select(event.target.value || null)}>
                        <option value="">Chọn một đối tượng</option>
                        {[...(ids ?? [])].map(id => <option key={id} value={id}>{id}</option>)}
                    </select>
                </label>
                <section className="details" aria-live="polite" data-testid="visitor-detail">
                    <h2>{selected ?? "Thông tin đối tượng"}</h2>
                    {detail ? <dl><dt>Loại</dt><dd>{detail.kind}</dd><dt>Trạng thái mô hình</dt><dd>{detail.status}</dd>
                        <dt>Nguồn</dt><dd>{detail.source}</dd><dt>Vị trí</dt><dd>{detail.position}</dd></dl> :
                        selected && <p>Chi tiết nguồn chưa khả dụng. ID lấy từ chỉ mục {revision}.</p>}
                    {chairRoom && selected && chairState && <div className="chair-actions" data-testid="chair-actions"
                        data-state={chairState} data-moving={chairRoom.moving === selected}>
                        <p>Ghế mô phỏng · {chairRoom.moving === selected ? "Đang di chuyển" :
                            { stored: "Đã cất", "pulled-out": "Đã kéo ra", occupied: "Đang ngồi" }[chairState]}</p>
                        {chairRoom.actions(selected, "web").map(action => <button key={action}
                            disabled={disabled || Boolean(chairRoom.moving)} onClick={() => {
                                const result = chairCommand.current?.(selected, action);
                                setChairMessage(result ?? "");
                                record("chair:" + action + ":" + selected + (result ? ":blocked" : ""));
                            }}>{labels[action]}</button>)}
                        {chairMessage && <p role="status">{chairMessage}</p>}
                    </div>}
                </section>
            </aside>
        </div>
        <section className="visitor-walk" aria-label="Di chuyển Web 3D">
            <h2>Di chuyển Web 3D</h2>
            <p>Chọn hoặc chạm vào đồ vật để xem thông tin. Kéo để nhìn quanh. Khi cảnh đang được chọn, dùng WASD để đi, ← → để xoay, Enter để chọn ở tâm ngắm.</p>
            {controls.map(([action, label]) => <button key={action} disabled={disabled} onClick={() => run.current?.(action)}>{label}</button>)}
            {blocked && <p role="status" data-testid="collision">Dừng ở giới hạn tuyến · {blocked}</p>}
        </section>
    </main>;
}
