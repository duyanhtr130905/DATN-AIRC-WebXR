import { Canvas, useFrame, useThree } from "@react-three/fiber";
import { XR } from "@react-three/xr";
import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { Group, type WebGLRenderer } from "three";
import { ErrorBoundary } from "../components/ErrorBoundary.tsx";
import { Navigation } from "../p507-e1/core.ts";
import { loadFrozenP507 } from "../p507-e1/load.ts";
import { reference } from "../p507-e1/scene-contract.ts";
import { Desktop, type DeskAction } from "./Desktop.tsx";
import { Immersive, provenance, type Detail } from "./Immersive.tsx";
import { disposeRoom, rendererInfo } from "./runtime.ts";
import { modes, useP507Session } from "./session.ts";
import "./visitor.css";

const ids = new Set(reference.records.map(record => record.id));
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
type Asset = Awaited<ReturnType<typeof loadFrozenP507>>;
type Evidence = { record(event: string): void; renderer?: string; frames: Record<string, number[]>; events: string[] };
declare global { interface Window { __P507_M5__?: Evidence } }

function useEvidence() {
    const evidence = useRef<Evidence>(undefined);
    useEffect(() => {
        if (new URLSearchParams(location.search).get("evidence") !== "1") return;
        const events: string[] = [];
        const report: Evidence = { events, frames: {}, record(event) { if (events.length < 800) events.push(event); } };
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
    const previous = useRef<{ mode: string; timestamp: number }>(undefined);
    useFrame((state, _, frame) => {
        const report = window.__P507_M5__;
        if (!report || document.hidden) return;
        report.renderer ??= rendererInfo(gl);
        const session = gl.xr.getSession();
        const mode = frame ? (session?.environmentBlendMode === "opaque" ? "vr" : "ar") : "web";
        const timestamp = frame?.predictedDisplayTime ?? state.clock.elapsedTime * 1000;
        const samples = report.frames[mode] ??= [];
        const last = previous.current;
        if (last?.mode === mode && samples.length < 360 && timestamp > last.timestamp) samples.push(timestamp - last.timestamp);
        previous.current = { mode, timestamp };
    });
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
    const [asset, setAsset] = useState<Asset>();
    const [error, setError] = useState("");
    const [attempt, retry] = useState(0);
    const [selected, select] = useState<string | null>(null);
    const [blocked, setBlocked] = useState<string | null>(null);
    const [ready, setReady] = useState(false);
    const run = useRef<((action: DeskAction) => void) | null>(null);
    const mount = useRef<Group>(null);
    const clearSelection = useCallback(() => select(null), []);
    const xr = useP507Session(clearSelection);
    const attach = useCallback((renderer: WebGLRenderer | undefined) => {
        xr.renderer.current = renderer;
        setReady(Boolean(renderer));
    }, [xr.renderer]);
    const record = useEvidence();
    const nav = useMemo(() => asset && new Navigation(asset.manifest), [asset]);
    const details = useMemo(() => new Map<string, Detail>(asset?.manifest.instances
        .filter(row => ids.has(row.id)).map(row => [row.id, {
            id: row.id,
            kind: asset.manifest.collision_proxies.find(proxy => proxy.id === row.id)?.kind ?? "UNKNOWN",
            status: row.status,
            source: String(row.survey_transform.source_kind ?? "UNKNOWN"),
            position: String(row.survey_transform.position_source ?? "UNKNOWN"),
        }])), [asset]);
    const detail = selected ? details.get(selected) : undefined;

    useEffect(() => {
        const controller = new AbortController();
        let room: Group | undefined;
        setError("");
        setAsset(undefined);
        const signal = AbortSignal.any([controller.signal, AbortSignal.timeout(30000)]);
        loadFrozenP507(signal).then(loaded => {
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
    }, [attempt]);
    useEffect(() => { record("session:" + xr.status + ":" + (xr.requested ?? "none")); }, [record, xr.status, xr.requested]);

    const disabled = !ready || xr.contextLost || xr.status === "requesting" || Boolean(xr.active);
    return <main className="p507-visitor">
        <nav aria-label="Ứng dụng">
            <a href="/">Không gian số AIRC</a>
            <a href="/?mode=p507">Digital Twin P507</a>
        </nav>
        <h1>Tham quan P507</h1>
        <p className="notice">{provenance}. Mô hình ảo 6,90 × 9,315 × 3,50 m. Dữ liệu tại đây chỉ dùng để xem thử.</p>
        <section className="visitor-xr" aria-label="Chế độ WebXR">
            <h2>Trải nghiệm WebXR</h2>
            <p>AR là mô hình thu nhỏ để bàn, không căn chỉnh 1:1 với phòng thật. VR dùng tuyến và vật cản ảo của R4.</p>
            {modes.map((mode, index) => <div key={mode} data-testid={"support-" + mode} data-support={xr.support[index]}>
                <button disabled={disabled || xr.support[index] !== "supported"} onClick={() => xr.enter(mode)}>
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
                    <p role="alert" data-testid="asset-status" data-result={error}>R4 không khả dụng. Bạn có thể tiếp tục bằng danh sách.</p>
                    <button onClick={() => retry(step => step + 1)}>Thử tải R4 lại</button>
                </div> : asset && nav && xr.store ?
                    <ErrorBoundary><Canvas gl={{ alpha: true }} dpr={[1, 1.5]} camera={{ fov: 78, near: 0.04, far: 60 }}
                        fallback={<p role="alert">WebGL không khả dụng. Hãy dùng danh sách đối tượng.</p>}>
                        <XR store={xr.store}>
                            <ambientLight intensity={0.75} />
                            <directionalLight position={[2, 8, -2]} intensity={2} />
                            <group ref={mount}><primitive object={asset.gltf.scene} /></group>
                            <RendererLifecycle attach={attach} contextLost={xr.lostContext} contextRestored={xr.restoredContext} />
                            <Desktop room={asset.gltf.scene} ids={ids} nav={nav}
                                enabled={!xr.active && !xr.contextLost && xr.status !== "requesting"}
                                pick={select} blocked={setBlocked} controls={run} />
                            <Immersive nav={nav} ids={ids} model={asset.gltf.scene} mount={mount} detail={detail} ar={xr.requested === "immersive-ar"}
                                pick={select} exit={xr.exit} record={record} />
                            <FrameEvidence />
                        </XR>
                    </Canvas></ErrorBoundary> : <p role="status">Đang kiểm tra R4…</p>}
            </section>
            <aside aria-label="Thông tin P507">
                {asset && <p data-testid="asset-status" data-result="E0_SCENE_PASS" data-sha={asset.hash}>R4 đã kiểm tra · 121 ID bố trí · 2 hồ sơ chưa bố trí</p>}
                <label>Đối tượng P507
                    <select value={selected ?? ""} onChange={event => select(event.target.value || null)}>
                        <option value="">Chọn một đối tượng</option>
                        {[...ids].map(id => <option key={id} value={id}>{id}</option>)}
                    </select>
                </label>
                <section className="details" aria-live="polite" data-testid="visitor-detail">
                    <h2>{selected ?? "Thông tin đối tượng"}</h2>
                    {detail ? <dl><dt>Loại</dt><dd>{detail.kind}</dd><dt>Trạng thái mô hình</dt><dd>{detail.status}</dd>
                        <dt>Nguồn</dt><dd>{detail.source}</dd><dt>Vị trí</dt><dd>{detail.position}</dd></dl> :
                        selected && <p>Chi tiết nguồn chưa khả dụng. ID lấy từ chỉ mục R4.</p>}
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
