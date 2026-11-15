import { diagnostic } from "../features/live/diagnostics.ts";
import { lazy, Suspense, useEffect, useLayoutEffect, useMemo, useState } from "react";
import { CatalogError, readObjects, readRooms } from "../api/catalog.ts";
import type { CatalogObject, Room } from "../features/live/contracts.ts";
import { sceneFromCatalog } from "../features/catalog/adapter.ts";
import { subscribe } from "../features/realtime/client.ts";
import type { Connection, Replica } from "../features/realtime/reducer.ts";
import { ErrorBoundary } from "../components/ErrorBoundary.tsx";
const DemoScene = lazy(() => import("../scene/DemoScene.tsx"));
const labels: Record<Connection, string> = { connecting: "Đang kết nối", synchronizing: "Đang đồng bộ snapshot", connected: "Đã kết nối — synthetic", stale: "STALE — dữ liệu cũ, chưa xác nhận hiện tại", reconnecting: "Đang kết nối lại — dữ liệu còn stale", resync_required: "Cần đồng bộ lại", error: "Không thể đồng bộ; hãy thử lại" };
function errorLabel(error: unknown) {
    if (error instanceof CatalogError) {
        if (error.kind === "unavailable")
            return "Database/backend chưa sẵn sàng (503).";
        if (["network", "timeout"].includes(error.kind))
            return "Backend không khả dụng hoặc quá thời gian chờ.";
        if (error.kind === "not_found")
            return "Phòng/đối tượng không còn được công bố.";
    }
    return "Response không đúng hợp đồng hoặc vượt capacity; không sử dụng dữ liệu.";
}
export default function LiveApp() {
    const [rooms, setRooms] = useState<Room[]>([]);
    const [roomId, setRoomId] = useState("");
    const [catalog, setCatalog] = useState<{
        roomId: string;
        objects: CatalogObject[];
    } | null>(null);
    const [phase, setPhase] = useState("loading");
    const [failure, setFailure] = useState("");
    const [selectedId, select] = useState<string | null>(null);
    const [replica, setReplica] = useState<Replica | null>(null);
    const [revision, refresh] = useState(0);
    useEffect(() => {
        const controller = new AbortController();
        let active = true;
        setPhase("loading");
        setFailure("");
        setCatalog(null);
        setRooms([]);
        setRoomId("");
        setReplica(null);
        select(null);
        readRooms(controller.signal).then(rows => { if (!active)
            return; setRooms(rows); setRoomId(rows[0]?.id ?? ""); setPhase(rows.length ? "objects_loading" : "no_rooms"); })
            .catch(error => { if (active) {
            setFailure(errorLabel(error));
            setPhase("error");
        } });
        return () => { active = false; controller.abort(); };
    }, [revision]);
    useEffect(() => {
        if (!roomId)
            return;
        const controller = new AbortController();
        let active = true;
        setCatalog(null);
        setReplica(null);
        select(null);
        setFailure("");
        setPhase("objects_loading");
        readObjects(roomId, controller.signal).then(objects => {
            if (!active)
                return;
            if (objects.length > 100)
                throw new Error("Scene capacity100");
            setCatalog({ roomId, objects });
            setPhase(objects.length ? "ready" : "no_objects");
        }).catch(error => { if (active) {
            setFailure(errorLabel(error));
            setPhase("error");
        } });
        return () => { active = false; controller.abort(); };
    }, [roomId, revision]);
    useEffect(() => {
        if (!catalog || catalog.roomId !== roomId)
            return;
        return subscribe(roomId, new Set(catalog.objects.map(o => o.id)), setReplica);
    }, [catalog, roomId]);
    useLayoutEffect(() => { if (replica?.roomId === roomId && replica.status === "connected")
        diagnostic("react.applied", { roomId, sequence: replica.sequence }); }, [replica, roomId]);
    const scoped = catalog?.roomId === roomId ? catalog : null;
    const live = replica?.roomId === roomId ? replica : null;
    const states = live?.states ?? {};
    const scene = useMemo(() => scoped ? sceneFromCatalog(scoped.roomId, scoped.objects, states) : null, [scoped, states]);
    const selected = scoped?.objects.find(o => o.id === selectedId);
    const selectedStates = Object.values(states).filter(s => s.target_id === selectedId);
    const schedule = Object.values(states).find(s => s.state_type === "room_schedule");
    const room = rooms.find(r => r.id === roomId);
    return <>
    <a className="skip" href="#objects">Đến danh sách đối tượng</a>
    <header><a href="/" className="brand">AIRC <span>KHÔNG GIAN SỐ</span></a><span className="stage">M1-C · SYNTHETIC VERTICAL SLICE</span></header>
    <main><div className="intro"><div><p className="eyebrow">CATALOG / TRẠNG THÁI / KHÔNG GIAN</p><h1>Khám phá một không gian mô phỏng.</h1></div><p>Scene + Information Panel<br />Chưa có dữ liệu khảo sát thực tế.</p></div>
    <p className="notice">SYNTHETIC / DEMO — DỮ LIỆU MÔ PHỎNG, KHÔNG PHẢI PHÒNG 507</p>
    <section className="room-bar"><label>Phòng synthetic <select aria-label="Phòng synthetic" value={roomId} onChange={e => setRoomId(e.target.value)} disabled={!rooms.length}>{rooms.map(r => <option key={r.id} value={r.id}>{r.name}</option>)}</select></label><button onClick={() => refresh(v => v + 1)}>Tải lại Catalog & kết nối</button><a href="/?mode=offline">Mở DEMO offline riêng</a></section>
    <p role="status" data-testid="catalog-status">{phase === "loading" ? "Đang tải danh sách phòng…" : phase === "objects_loading" ? "Đang tải đối tượng…" : phase === "no_rooms" ? "Chưa có phòng synthetic; cần explicit seed." : phase === "no_objects" ? "Phòng chưa có đối tượng synthetic." : phase === "ready" ? `${scoped?.objects.length ?? 0} đối tượng synthetic từ API` : "Không tải được Catalog."}</p>
    {failure && <p role="alert">{failure}</p>}
    <p className="connection-status" role="status" data-testid="realtime" data-status={live?.status ?? "connecting"}>{scoped ? labels[live?.status ?? "connecting"] : "Chưa có subscription"} {live && `· sequence ${live.sequence}`}</p>
    <div className="workspace"><section className="scene" aria-label="Cảnh mô phỏng"><div className="scene-label">{room?.name ?? "CHƯA CHỌN PHÒNG"} / LAYOUT SYNTHETIC</div>
      {scene ? <ErrorBoundary><Suspense fallback={<p role="status">Đang tải module 3D…</p>}><DemoScene scene={scene} selectedId={selectedId} select={select}/></Suspense></ErrorBoundary> : <p>Canvas chờ Catalog hợp lệ; không dùng fixture thay dữ liệu API.</p>}
      <p className="hint">Kéo để xoay · Chọn khối hoặc dùng danh sách · Layout primitive không phản ánh phòng 507</p>
    </section><aside><section id="objects"><p className="eyebrow">CATALOG SYNTHETIC</p><h2>Đối tượng trong cảnh</h2><div className="object-list">{scoped?.objects.map((o, i) => <button key={o.id} data-object-id={o.id} aria-pressed={selectedId === o.id} onClick={() => select(o.id)}><span>{String(i + 1).padStart(2, "0")}</span>{o.name}<span aria-hidden="true">↗</span></button>)}</div></section>
    <section className="details" aria-live="polite" data-testid="object-panel"><h2>{selected?.name ?? "Chọn một đối tượng"}</h2>{selected && <><p>{selected.metadata.description ?? "Chưa có mô tả public."}</p><dl><dt>Stable UUID</dt><dd>{selected.id}</dd><dt>Loại</dt><dd>{selected.type}</dd><dt>Room UUID</dt><dd>{selected.room_id}</dd><dt>Nguồn</dt><dd>{selected.source_kind}</dd><dt>Nhãn</dt><dd>{selected.metadata.label}</dd></dl>
      {selectedStates.length === 0 && <p>Chưa có state authoritative; không suy đoán trạng thái thiết bị.</p>}
      {selectedStates.map(s => <div className="state-card" key={s.id} data-state-type={s.state_type} data-version={s.version}><strong>{s.state_type}</strong><p>{Object.entries(s.value).map(([k, v]) => `${k}: ${v}`).join(" · ")}</p><small>v{s.version} · {s.source_kind} · {s.committed_at}</small>{live?.status !== "connected" && <p>STALE — chưa xác nhận hiện tại</p>}</div>)}</>}</section>
    <section className="details"><h2>Lịch phòng synthetic</h2><p>{schedule ? `${schedule.value.status} · ${schedule.value.activity} · v${schedule.version}` : "Chưa có lịch phòng authoritative."}</p>{schedule && live?.status !== "connected" && <p>STALE — lịch cũ</p>}</section></aside></div>
    <footer>Chưa nghiệm thu KPI MT1–MT3 · Không có camera/AR/VR tự khởi tạo · Mọi thao tác ghi chỉ qua guarded CLI</footer></main>
  </>;
}
