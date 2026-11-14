import { lazy, Suspense, useEffect, useState } from "react";
import { readHealth, readReadiness } from "../api/client.ts";
import { ErrorBoundary } from "../components/ErrorBoundary.tsx";
import { loadDemo, selectedObject } from "../features/catalog/demo.ts";
const DemoScene = lazy(() => import("../scene/DemoScene.tsx"));
const scene = loadDemo();
export default function App() {
  const [selectedId, select] = useState<string | null>(null);
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
    <header><a href="/" className="brand">AIRC <span>KHÔNG GIAN SỐ</span></a><span className="stage">M0-B2 · FOUNDATION</span></header>
    <main>
      <div className="intro"><div><p className="eyebrow">KHÁM PHÁ KHÔNG GIAN</p><h1>Nền tảng cho một góc nhìn mới.</h1></div><p>Scene + Information Panel<br />Chưa có dữ liệu khảo sát thực tế.</p></div>
      <p className="notice">SYNTHETIC / DEMO — DỮ LIỆU MÔ PHỎNG, KHÔNG PHẢI PHÒNG 507</p>
      <div className="workspace"><section className="scene" aria-label="Cảnh mô phỏng"><div className="scene-label">01 / KHÔNG GIAN DEMO</div><ErrorBoundary><Suspense fallback={<p role="status">Đang tải module 3D…</p>}><DemoScene key={revision} scene={scene} selectedId={selectedId} select={select} /></Suspense></ErrorBoundary><p className="hint">Kéo để xoay · Cuộn để phóng to · Chọn khối hoặc dùng danh sách bên cạnh</p></section>
      <aside><section id="objects"><p className="eyebrow">DANH MỤC MẪU</p><h2>Đối tượng trong cảnh</h2><div className="object-list">{scene.objects.map((object, index) => <button key={object.id} aria-pressed={object.id === selectedId} onClick={() => select(object.id)}><span>0{index + 1}</span>{object.name}<span aria-hidden="true">↗</span></button>)}</div></section>
      <section className="details" aria-live="polite"><h2>{selected?.name ?? "Chọn một đối tượng"}</h2><p>{selected?.description ?? "Thông tin hiển thị tại đây khi bạn chọn trong cảnh hoặc danh sách."}</p>{selected && <dl><dt>Stable ID</dt><dd>{selected.id}</dd><dt>Room ID</dt><dd>{selected.roomId}</dd><dt>Nguồn</dt><dd>{selected.sourceKind}</dd></dl>}</section>
      <section className="connection" aria-live="polite"><h2>Kết nối nền tảng</h2><p data-testid="health">{api}</p><p data-testid="readiness">{database}</p><button onClick={() => refresh(value => value + 1)}>Kiểm tra lại & đặt lại cảnh</button></section></aside></div>
      <footer>Chưa có phiên AR/VR thực tế · Chưa đạt nghiệm thu KPI MT1–MT3 · Guided Tour sẽ phát triển sau</footer>
    </main>
  </>;
}
