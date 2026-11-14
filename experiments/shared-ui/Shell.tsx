import { useEffect, useRef, useState, useSyncExternalStore } from "react";
import {
  NOTICE,
  KIND_LABEL,
  syntheticAdapter,
  type Bridge,
  type SceneData,
} from "../shared-fixtures/domain.ts";
import "./styles.css";
export type Runtime = {
  bridge: Bridge;
  resetCamera(): void;
  enter(mode: "immersive-vr" | "immersive-ar"): Promise<void>;
  exit(): Promise<void>;
};
export type Mount = (
  host: HTMLDivElement,
  scene: SceneData,
  ready: (runtime: Runtime) => void,
  error: (message: string) => void,
) => () => void;
function Inspector({ runtime, guided }: { runtime: Runtime; guided: boolean }) {
  const s = useSyncExternalStore(
    runtime.bridge.subscribe,
    runtime.bridge.getSnapshot,
    runtime.bridge.getSnapshot,
  );
  const selected = s.scene.objects.find((o) => o.id === s.selectedId);
  const [error, setError] = useState("");
  const command = (fn: () => void) => {
    try {
      fn();
      setError("");
    } catch (e) {
      setError(String(e));
    }
  };
  return (
    <>
      <div className="panel-label">
        {guided ? "Hành trình khám phá" : "Thông tin đối tượng"}
      </div>
      <h2 data-testid="selected-name">
        {selected?.name || "Chọn một điểm chạm"}
      </h2>
      <p className="muted">
        {selected?.metadata.description ||
          "Chạm vào khối trong không gian hoặc chọn từ danh mục bên dưới. Mọi dữ liệu tại đây đều là mô phỏng."}
      </p>
      {selected ? (
        <div data-testid="object-details">
          <span className="status" data-testid="status">
            {selected.status.value}
          </span>
          <dl>
            <dt>Loại trạng thái</dt>
            <dd>{KIND_LABEL[selected.status.kind]}</dd>
            <dt>Stable ID</dt>
            <dd data-testid="object-id">{selected.id}</dd>
            <dt>Nguồn</dt>
            <dd>{selected.provenance.source_kind}</dd>
            <dt>Cập nhật</dt>
            <dd data-testid="timestamp">{selected.status.timestamp}</dd>
          </dl>
          <button
            className="primary"
            data-testid="change"
            onClick={() => command(runtime.bridge.cycle)}
          >
            Đổi trạng thái DEMO
          </button>
        </div>
      ) : (
        <div className="empty-mark" aria-hidden="true">
          ↗
        </div>
      )}
      {guided && (
        <div className="tour-controls">
          <p>
            {Math.max(
              0,
              s.scene.objects.findIndex((o) => o.id === s.selectedId),
            ) + 1}{" "}
            / 5 điểm khám phá
          </p>
          <button
            onClick={() =>
              command(() => {
                const i = s.scene.objects.findIndex(
                  (o) => o.id === s.selectedId,
                );
                runtime.bridge.select(s.scene.objects[(i + 1) % 5].id);
              })
            }
          >
            Điểm tiếp theo →
          </button>
        </div>
      )}
      <div className="object-list" aria-label="Danh mục đối tượng">
        <h3>05 điểm tương tác</h3>
        {s.scene.objects.map((o, i) => (
          <button
            key={o.id}
            data-testid={`object-${i + 1}`}
            aria-pressed={s.selectedId === o.id}
            onClick={() => command(() => runtime.bridge.select(o.id))}
          >
            <span className="ordinal">0{i + 1}</span>
            <span>
              {o.name}
              <small>{KIND_LABEL[o.status.kind]}</small>
            </span>
            <span aria-hidden="true">↗</span>
          </button>
        ))}
      </div>
      {error && <p role="alert">{error}</p>}
    </>
  );
}
export function Shell({ label, mount }: { label: string; mount: Mount }) {
  const host = useRef<HTMLDivElement>(null);
  const [runtime, setRuntime] = useState<Runtime | null>(null);
  const [phase, setPhase] = useState(
    "Đang tải dữ liệu DEMO và khởi tạo renderer…",
  );
  const [error, setError] = useState("");
  const [guided, setGuided] = useState(false);
  const [xr, setXr] = useState(
    "XR chỉ bắt đầu khi bấm nút. Chưa kiểm thử thiết bị thật.",
  );
  useEffect(() => {
    let dispose: (() => void) | undefined;
    let cancelled = false;
    const controller = new AbortController();
    syntheticAdapter
      .load(controller.signal)
      .then((scene) => {
        if (cancelled) return;
        dispose = mount(
          host.current!,
          scene,
          (created) => {
            if (!cancelled) {
              setRuntime(created);
              setPhase("Sẵn sàng · dữ liệu synthetic");
            }
          },
          (message) => {
            if (!cancelled) {
              setError(message);
              setPhase("Không thể khởi tạo cảnh");
            }
          },
        );
      })
      .catch((e) => {
        if (!cancelled) setError(String(e));
      });
    return () => {
      cancelled = true;
      controller.abort();
      dispose?.();
    };
  }, [mount]);
  const enter = async (mode: "immersive-vr" | "immersive-ar") => {
    try {
      await runtime!.enter(mode);
      setXr("Session đang chạy; nếu có emulator thì đây chỉ là giả lập.");
    } catch (e) {
      setXr("Không vào được XR: " + String(e));
    }
  };
  return (
    <main>
      <div className="demo-notice">{NOTICE}</div>
      <header>
        <a className="brand" href="#main-view">
          KHÔNG GIAN<span>LAB / M0-B1</span>
        </a>
        <div className="build-label">
          {label}
          <span>PROOF OF CONCEPT</span>
        </div>
      </header>
      <section className="intro">
        <div>
          <p className="eyebrow">01 / KHÁM PHÁ KHÔNG GIAN</p>
          <h1>Một không gian. Nhiều điểm chạm.</h1>
          <p>
            Khám phá 5 đối tượng mẫu, xem thông tin và thử thay đổi trạng thái.
          </p>
        </div>
        <span className="room-tag">
          Phòng DEMO
          <br />
          <small>Primitive · kích thước giả lập</small>
        </span>
      </section>
      <nav className="toolbar" aria-label="Chế độ khám phá">
        <div className="segmented">
          <button aria-pressed={!guided} onClick={() => setGuided(false)}>
            Cảnh + thông tin
          </button>
          <button
            aria-pressed={guided}
            onClick={() => {
              setGuided(true);
              runtime?.bridge.select("demo-object-001");
            }}
          >
            Tour dẫn đường
          </button>
        </div>
        <button
          disabled={!runtime}
          data-testid="reset"
          onClick={() => {
            runtime!.bridge.reset();
            runtime!.resetCamera();
            setGuided(false);
          }}
        >
          ↺ Đặt lại cảnh
        </button>
      </nav>
      <section id="main-view" className="experience">
        <div className="scene-wrap">
          <div
            ref={host}
            className="viewport"
            aria-label="Không gian 3D DEMO"
            data-testid="viewport"
          />
          <div className="scene-caption">
            <span className="live-dot" /> {phase}
          </div>
          <div className="scene-hint">
            Kéo để xoay · Cuộn / chụm để zoom · Chạm để chọn
          </div>
          {error && (
            <div className="scene-error" role="alert">
              <h2>Không thể hiển thị 3D</h2>
              <p>{error}</p>
              <p>
                Thử trình duyệt có WebGL2 hoặc tải lại trang. Không có dữ liệu
                AIRC thật.
              </p>
              <button onClick={() => location.reload()}>Tải lại</button>
            </div>
          )}
        </div>
        <aside className="inspector">
          {runtime ? (
            <Inspector runtime={runtime} guided={guided} />
          ) : (
            <>
              <h2>Chuẩn bị không gian</h2>
              <p role="status">{phase}</p>
            </>
          )}
        </aside>
      </section>
      <section className="xr-bar" aria-label="Thử WebXR">
        <div>
          <strong>Thử nghiệm WebXR</strong>
          <p role="status" data-testid="xr-status">
            {xr}
          </p>
        </div>
        <div className="xr-buttons">
          <button disabled={!runtime} onClick={() => enter("immersive-vr")}>
            Vào VR
          </button>
          <button disabled={!runtime} onClick={() => enter("immersive-ar")}>
            Vào AR
          </button>
          <button
            disabled={!runtime}
            onClick={async () => {
              try {
                await runtime!.exit();
                setXr("Đã thoát XR; trở về Web 3D.");
              } catch (e) {
                setXr(String(e));
              }
            }}
          >
            Thoát XR
          </button>
        </div>
      </section>
      <footer>
        Không phải mô hình phòng 507 · Chưa có dữ liệu khảo sát · Không dùng PoC
        này để nghiệm thu KPI hiệu năng
      </footer>
    </main>
  );
}
export function webglAvailable() {
  if (new URLSearchParams(location.search).has("forceNoWebGL")) return false;
  try {
    return !!document.createElement("canvas").getContext("webgl2");
  } catch {
    return false;
  }
}
