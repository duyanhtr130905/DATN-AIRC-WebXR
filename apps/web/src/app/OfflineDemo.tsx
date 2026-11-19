import { lazy, Suspense, useEffect, useState } from "react";
import { readHealth, readReadiness } from "../api/client.ts";
import { ErrorBoundary } from "../components/ErrorBoundary.tsx";
import { loadDemo, selectedObject } from "../features/catalog/demo.ts";
import { settled } from "../features/visitor/session.ts";
import { useVisitor } from "../features/visitor/useVisitor.ts";
const DemoScene = lazy(() => import("../scene/DemoScene.tsx"));
const scene = loadDemo();
export default function OfflineDemo() {
  const [untrackedId, setUntrackedId] = useState<string | null>(null);
  const visitor = useVisitor();
  const tracked = visitor.session && !visitor.session.clearing;
  const sessionId = visitor.session?.view.id ?? null;
  const recording = tracked && !visitor.pending && !visitor.session?.proofLost &&
    !visitor.suspended && !visitor.session?.view.ended;
  const selectedId = recording ? visitor.session?.view.selected_id ?? null : untrackedId;
  const showDetails = !recording || visitor.session?.view.info_open;
  function select(id: string | null) {
    setUntrackedId(id);
    if (recording && sessionId && id) visitor.actions?.record(sessionId, "object_select", id);
  }
  const [api, setApi] = useState("Đang kiểm tra backend…");
  const [database, setDatabase] = useState("Chưa biết trạng thái database.");
  const [revision, refresh] = useState(0);
  useEffect(() => {
    let active = true;
    setApi("Đang kiểm tra backend…");
    setDatabase("Đang kiểm tra database…");
    readHealth().then(() => { if (active) setApi("Backend đang hoạt động"); })
      .catch(() => { if (active) setApi("Không kết nối được backend"); });
    readReadiness().then(readiness => {
      if (active) setDatabase(readiness.status === "ready" ? "PostgreSQL: sẵn sàng" : `PostgreSQL: chưa sẵn sàng (${readiness.database})`);
    }).catch(() => { if (active) setDatabase("Chưa xác minh được database."); });
    return () => { active = false; };
  }, [revision]);
  const selected = selectedObject(scene, selectedId);
  return <>
    <a className="skip" href="#objects">Đến danh sách đối tượng</a>
    <header><a href="/" className="brand">AIRC <span>KHÔNG GIAN SỐ</span></a><span className="stage">OFFLINE DEMO · FOUNDATION</span></header>
    <main><p className="notice">DEMO OFFLINE ĐƯỢC CHỌN TƯỜNG MINH — không phải Catalog live. <a href="/">Về chế độ API live</a></p>
      <div className="intro"><div><p className="eyebrow">KHÁM PHÁ KHÔNG GIAN</p><h1>Nền tảng cho một góc nhìn mới.</h1></div><p>Scene + Information Panel<br />Chưa có dữ liệu khảo sát thực tế.</p></div>
      <p className="notice">SYNTHETIC / DEMO — DỮ LIỆU MÔ PHỎNG, KHÔNG PHẢI PHÒNG 507</p>
      {(visitor.available || visitor.session || visitor.pending || visitor.message) && <section className="connection" aria-label="Phiên mô phỏng cục bộ">
        <h2>Phiên mô phỏng cục bộ</h2>
        {!visitor.pending && visitor.available && !visitor.session &&
          <button onClick={() => visitor.actions?.start(null)}>Đồng ý ghi phiên mô phỏng</button>}
        {!visitor.pending && visitor.available && visitor.session && settled(visitor.session) &&
          <button onClick={() => visitor.actions?.start(sessionId)}>Đồng ý ghi lượt tham quan mới</button>}
        {visitor.pending && <p role="status">Chờ xác nhận bắt đầu lượt tham quan</p>}
        {visitor.session && <>
          <p role="status" data-testid="visitor-session">
            {visitor.session.clearing ? "Chờ xác nhận xóa trên máy chủ" : visitor.suspended ? "Máy chủ đã tắt ghi phiên" : visitor.session.proofLost ? "Mã phiên hết hiệu lực" : visitor.session.view.ended ? (visitor.session.queue.length ? "Chờ xác nhận kết thúc" : "Đã kết thúc") : "Đang ghi phiên mô phỏng"}
            {" · "}{visitor.session.queue.length} sự kiện chờ
          </p>
          {recording && sessionId && <button onClick={() => visitor.actions?.record(sessionId, "session_end")}>Kết thúc phiên</button>}
          {!visitor.pending && !visitor.session.clearing && sessionId && <button onClick={() => { setUntrackedId(null); visitor.actions?.clear(sessionId); }}>Dừng ghi và xóa phiên</button>}
          {!visitor.pending && <button onClick={() => visitor.actions?.retry()}>Thử đồng bộ lại</button>}
        </>}
        {visitor.pending && <button onClick={() => visitor.actions?.retry()}>Thử xác nhận lượt mới</button>}
        {visitor.message && <p role="status">{visitor.message}</p>}
      </section>}
      <div className="workspace"><section className="scene" aria-label="Cảnh mô phỏng"><div className="scene-label">01 / KHÔNG GIAN DEMO</div><ErrorBoundary><Suspense fallback={<p role="status">Đang tải module 3D…</p>}><DemoScene key={revision} scene={scene} selectedId={selectedId} select={select} /></Suspense></ErrorBoundary><p className="hint">Kéo để xoay · Cuộn để phóng to · Chọn khối hoặc dùng danh sách bên cạnh</p></section>
      <aside><section id="objects"><p className="eyebrow">DANH MỤC MẪU</p><h2>Đối tượng trong cảnh</h2><div className="object-list">{scene.objects.map((object, index) => <button key={object.id} aria-pressed={object.id === selectedId} onClick={() => select(object.id)}><span>0{index + 1}</span>{object.name}<span aria-hidden="true">↗</span></button>)}</div></section>
      <section className="details" aria-live="polite"><h2>{selected?.name ?? "Chọn một đối tượng"}</h2>{recording && sessionId && selected && <button onClick={() => visitor.actions?.record(sessionId, showDetails ? "info_close" : "info_open", selected.id)}>{showDetails ? "Ẩn thông tin" : "Mở thông tin"}</button>}{showDetails && <p>{selected?.description ?? "Thông tin hiển thị tại đây khi bạn chọn trong cảnh hoặc danh sách."}</p>}{selected && showDetails && <dl><dt>Stable ID</dt><dd>{selected.id}</dd><dt>Room ID</dt><dd>{selected.roomId}</dd><dt>Nguồn</dt><dd>{selected.sourceKind}</dd></dl>}</section>
      <section className="connection" aria-live="polite"><h2>Kết nối nền tảng</h2><p data-testid="health">{api}</p><p data-testid="readiness">{database}</p><button onClick={() => refresh(value => value + 1)}>Kiểm tra lại & đặt lại cảnh</button></section></aside></div>
      <footer>Chưa có phiên AR/VR thực tế · Chưa đạt nghiệm thu KPI MT1–MT3 · Guided Tour sẽ phát triển sau</footer>
    </main>
  </>;
}
