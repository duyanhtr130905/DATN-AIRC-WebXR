import { observationAge } from "../features/live/observationAge.ts";
import { Canvas, useThree } from "@react-three/fiber";
import { OrbitControls } from "three/examples/jsm/controls/OrbitControls.js";
import { useCallback, useEffect, useLayoutEffect, useState } from "react";
import type { Object3D } from "three";
import { readObjects, readRooms } from "../api/catalog.ts";
import { ErrorBoundary } from "../components/ErrorBoundary.tsx";
import type { CatalogObject, TwinState } from "../features/live/contracts.ts";
import { diagnostic } from "../features/live/diagnostics.ts";
import { subscribe } from "../features/realtime/client.ts";
import type { Replica } from "../features/realtime/reducer.ts";
import { logicalId } from "../p507-e1/core.ts";
import { loadFrozenP507 } from "../p507-e1/load.ts";
import { reference } from "../p507-e1/scene-contract.ts";
import mapping from "./p507-mapping.json";

const ids = reference.records.map(row => row.id);
const known = new Set(ids);
const roomId = mapping.room_id;

export function bindCatalog(rows: CatalogObject[]) {
    const objects = new Map<string, CatalogObject>();
    const expected = new Map(Object.entries(mapping.objects).map(([logical, uuid]) => [uuid, logical]));
    for (const object of rows) {
        const logical = expected.get(object.id);
        if (!logical || !known.has(logical) || objects.has(logical) ||
            object.room_id !== roomId ||
            object.source_kind !== "synthetic" || object.metadata.description !== mapping.evidence_ref)
            throw new Error("P507 Catalog mapping conflict");
        objects.set(logical, object);
    }
    if (objects.size !== ids.length || ids.length !== 121)
        throw new Error("P507 Catalog mapping incomplete");
    return objects;
}

function Controls() {
    const { camera, gl, invalidate } = useThree();
    useEffect(() => {
        const controls = new OrbitControls(camera, gl.domElement);
        controls.target.set(3.45, 1.2, -4.65);
        controls.minDistance = 1;
        controls.maxDistance = 14;
        const requestFrame = () => invalidate();
        controls.addEventListener("change", requestFrame);
        controls.update();
        invalidate();
        return () => {
            controls.removeEventListener("change", requestFrame);
            controls.dispose();
        };
    }, [camera, gl, invalidate]);
    return null;
}

function StateCard({ state, stale }: { state: TwinState; stale: boolean }) {
    const [now, setNow] = useState(Date.now);
    useEffect(() => {
        const timer = setInterval(() => setNow(Date.now()), 1000);
        return () => clearInterval(timer);
    }, []);
    const observed = state.source_observed_at;
    return <div className="state-card" data-state-type={state.state_type} data-version={state.version}>
        <strong>{state.state_type}</strong>
        <p>{Object.entries(state.value).map(([key, value]) => `${key}: ${value}`).join(" · ")}</p>
        <dl>
            <dt>Nguồn</dt><dd>{state.source_kind} · fixture {mapping.revision}</dd>
            <dt>Phiên bản</dt><dd>{state.version}</dd>
            <dt>Thời điểm quan sát</dt><dd>{observed ?? "UNKNOWN"}</dd>
            <dt>Tuổi theo đồng hồ trình duyệt</dt><dd>{observationAge(observed, now, state.committed_at)} · cadence chưa xác minh</dd>
            <dt>Thời điểm ghi trong DB</dt><dd>{state.committed_at}</dd>
        </dl>
        {stale && <p>STALE — mất đồng bộ</p>}
    </div>;
}

export default function P507App() {
    const [revision, retry] = useState(0);
    const [backendError, setBackendError] = useState(false);
    const [objects, setObjects] = useState<Map<string, CatalogObject>>();
    const [replica, setReplica] = useState<Replica>();
    const [selected, select] = useState("");
    useEffect(() => {
        const controller = new AbortController();
        readRooms(controller.signal).then(rooms => {
            if (!rooms.some(room => room.id === roomId && room.code === "DEMO-P507"))
                throw new Error("P507 fixture unavailable");
            return readObjects(roomId, controller.signal);
        }).then(rows => {
            if (!controller.signal.aborted) setObjects(bindCatalog(rows));
        }).catch(() => {
            if (!controller.signal.aborted) setBackendError(true);
        });
        return () => controller.abort();
    }, [revision]);
    useEffect(() => {
        if (objects) return subscribe(roomId, new Set([...objects.values()].map(object => object.id)), setReplica);
    }, [objects]);
    useLayoutEffect(() => {
        if (replica?.status === "connected") diagnostic("react.applied", { roomId, sequence: replica.sequence });
    }, [replica]);
    const scoped = replica?.roomId === roomId ? replica : undefined;
    const states = Object.values(scoped?.states ?? {});
    const object = objects?.get(selected);
    const objectStates = states.filter(state => state.target_kind === "object" && state.target_id === object?.id);
    const schedule = states.find(state => state.target_kind === "room" && state.target_id === roomId && state.state_type === "room_schedule");
    const stale = scoped?.status !== "connected";
    return <main>
        <h1>Digital Twin P507</h1><a href="/?mode=p507-visit">Mở chế độ tham quan Web 3D / XR</a>
        <p className="notice">PROVISIONAL / SYNTHETIC · R4 · Quyền dữ liệu AIRC chưa xác nhận</p>
        <p role="status" data-testid="realtime" data-status={scoped?.status ?? (backendError ? "error" : "connecting")}>
            {backendError ? "UNAVAILABLE — backend hoặc mapping không khả dụng" : scoped?.status ?? "Đang kết nối"}
            {scoped && stale && " · STALE"}
        </p>
        <button onClick={() => { setObjects(undefined); setReplica(undefined); setBackendError(false); retry(value => value + 1); }}>Tải lại P507</button>
        <div className="workspace">
            <P507Scene key={revision} pick={select} />
            <aside>
                <label>Đối tượng P507 <select aria-label="Đối tượng P507" value={selected} onChange={event => select(event.target.value)}>
                    <option value="">Chọn đối tượng</option>
                    {ids.map(id => <option key={id} value={id}>{id}</option>)}
                </select></label>
                <section className="details" aria-live="polite" data-testid="object-panel">
                    <h2>{selected || "Thông tin đối tượng"}</h2>
                    {object && <p>Catalog UUID {object.id} · {mapping.revision}</p>}
                    {objectStates.length === 0 && <p>UNKNOWN — chưa có trạng thái đối tượng</p>}
                    {objectStates.map(state => <StateCard key={state.id} state={state} stale={stale} />)}
                </section>
                <section className="details" data-testid="schedule-panel">
                    <h2>Lịch phòng P507</h2>
                    {schedule ? <StateCard state={schedule} stale={stale} /> : <p>UNKNOWN — chưa có lịch phòng</p>}
                </section>
            </aside>
        </div>
    </main>;
}

export function P507Scene({ pick }: { pick(id: string): void }) {
    const [scene, setScene] = useState<Object3D>();
    const [assetError, setAssetError] = useState("");
    const pickMesh = useCallback((event: { object: Object3D; stopPropagation(): void }) => {
        const id = logicalId(event.object, known);
        if (id) {
            event.stopPropagation();
            pick(id);
        }
    }, [pick]);
    useEffect(() => {
        const controller = new AbortController();
        loadFrozenP507(controller.signal).then(({ gltf }) => {
            if (!controller.signal.aborted) setScene(gltf.scene);
        }).catch(() => {
            if (!controller.signal.aborted) setAssetError("UNAVAILABLE — không tải được asset R4 đã kiểm hash.");
        });
        return () => controller.abort();
    }, []);
    return <section className="scene" aria-label="Cảnh P507">
                {assetError ? <p role="alert">{assetError}</p> : scene ?
                    <ErrorBoundary>
                        <Canvas frameloop="demand" camera={{ position: [1.25, 1.65, -7.415], fov: 48 }} fallback={<p role="alert">WebGL không khả dụng</p>}>
                            <ambientLight intensity={0.75} />
                            <directionalLight position={[2, 8, -2]} intensity={2} />
                            <Controls />
                            <primitive object={scene} onClick={pickMesh} />
                        </Canvas>
                    </ErrorBoundary> : <p role="status">Đang kiểm tra asset R4…</p>}
            </section>;
}
