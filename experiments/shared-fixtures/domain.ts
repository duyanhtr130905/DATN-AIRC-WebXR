export type SourceKind = "synthetic" | "unknown" | "real_verified";
export type StateKind =
  | "room_schedule"
  | "device_condition"
  | "exhibit_information";
export type DemoObject = {
  id: string;
  name: string;
  type: string;
  roomId: string;
  position: [number, number, number];
  metadata: { description: string };
  status: { kind: StateKind; value: string; timestamp: string };
  provenance: { source_kind: SourceKind; evidenceRef?: string };
};
export type SceneData = {
  room: {
    id: string;
    name: string;
    dimensions: [number, number, number];
    source_kind: SourceKind;
  };
  objects: DemoObject[];
};
export const NOTICE = "DEMO – DỮ LIỆU MÔ PHỎNG, KHÔNG PHẢI PHÒNG 507";
export const VALUES: Record<StateKind, string[]> = {
  room_schedule: ["Trống · DEMO", "Đã đặt · DEMO"],
  device_condition: ["Sẵn sàng · DEMO", "Bảo trì · DEMO"],
  exhibit_information: ["Đang trưng bày · DEMO", "Đang cập nhật · DEMO"],
};
export const KIND_LABEL: Record<StateKind, string> = {
  room_schedule: "Lịch phòng",
  device_condition: "Tình trạng thiết bị",
  exhibit_information: "Thông tin trưng bày",
};
const names = [
  "Trạm quan sát DEMO",
  "Cụm xử lý DEMO",
  "Bệ trưng bày DEMO",
  "Màn thông tin DEMO",
  "Bảng lịch DEMO",
];
const positions: [number, number, number][] = [
  [-3, 0.65, -1.8],
  [0, 0.65, -1.8],
  [3, 0.65, -1.8],
  [-1.8, 0.65, 1.5],
  [2, 0.65, 1.5],
];
export const fixture: SceneData = {
  room: {
    id: "demo-room-001",
    name: "Không gian thử nghiệm",
    dimensions: [12, 3, 9],
    source_kind: "synthetic",
  },
  objects: names.map((name, i) => ({
    id: `demo-object-${String(i + 1).padStart(3, "0")}`,
    name,
    type: ["workstation", "equipment", "exhibit", "display", "schedule"][i],
    roomId: "demo-room-001",
    position: positions[i],
    metadata: {
      description:
        "Primitive và nội dung giả lập dùng chung để so sánh renderer; không đại diện bất kỳ thiết bị AIRC nào.",
    },
    status: {
      kind: (
        [
          "device_condition",
          "device_condition",
          "exhibit_information",
          "exhibit_information",
          "room_schedule",
        ] as StateKind[]
      )[i],
      value: [
        "Sẵn sàng · DEMO",
        "Sẵn sàng · DEMO",
        "Đang trưng bày · DEMO",
        "Đang trưng bày · DEMO",
        "Trống · DEMO",
      ][i],
      timestamp: "2026-11-14T00:00:00+07:00",
    },
    provenance: { source_kind: "synthetic" },
  })),
};
const vector = (v: unknown): v is [number, number, number] =>
  Array.isArray(v) &&
  v.length === 3 &&
  v.every((n) => typeof n === "number" && Number.isFinite(n));
export function validateScene(input: unknown): SceneData {
  if (!input || typeof input !== "object")
    throw new Error("Scene phải là object.");
  const data = input as SceneData;
  const kinds: SourceKind[] = ["synthetic", "unknown", "real_verified"];
  if (
    !data.room ||
    typeof data.room.id !== "string" ||
    !data.room.id.trim() ||
    !kinds.includes(data.room.source_kind) ||
    !vector(data.room.dimensions) ||
    data.room.dimensions.some((n) => n <= 0) ||
    !Array.isArray(data.objects)
  )
    throw new Error("Room hoặc danh mục không hợp lệ.");
  const ids = new Set<string>([data.room.id]);
  for (const object of data.objects) {
    if (
      !object ||
      typeof object.id !== "string" ||
      !object.id.trim() ||
      ids.has(object.id)
    )
      throw new Error("Duplicate hoặc thiếu stable ID.");
    ids.add(object.id);
    if (
      object.roomId !== data.room.id ||
      !vector(object.position) ||
      typeof object.name !== "string" ||
      !object.name.trim() ||
      typeof object.type !== "string" ||
      typeof object.metadata?.description !== "string"
    )
      throw new Error("Object metadata/room/position không hợp lệ.");
    if (
      !object.status ||
      !Object.hasOwn(VALUES, object.status.kind) ||
      typeof object.status.value !== "string" ||
      !object.status.value.trim() ||
      !Number.isFinite(Date.parse(object.status.timestamp))
    )
      throw new Error("Trạng thái hoặc timestamp không hợp lệ.");
    if (!object.provenance || !kinds.includes(object.provenance.source_kind))
      throw new Error("Thiếu provenance.");
    if (
      object.provenance.source_kind === "real_verified" &&
      !object.provenance.evidenceRef?.trim()
    )
      throw new Error(
        "real_verified cần evidenceRef; không tự nâng synthetic thành dữ liệu thật.",
      );
  }
  return structuredClone(data);
}
export interface DataAdapter {
  load(signal?: AbortSignal): Promise<SceneData>;
}
export const syntheticAdapter: DataAdapter = {
  async load(signal) {
    if (signal?.aborted) throw new Error("Đã hủy tải.");
    return validateScene(fixture);
  },
};
// Adapter boundary only: caller supplies an authorized loader later; no network/database is implemented.
export const adapterFromLoader = (
  loader: (signal?: AbortSignal) => Promise<unknown>,
): DataAdapter => ({
  async load(signal) {
    return validateScene(await loader(signal));
  },
});
export type Snapshot = {
  scene: SceneData;
  selectedId: string | null;
  revision: number;
};
export interface Bridge {
  getSnapshot(): Snapshot;
  subscribe(listener: () => void): () => void;
  select(id: string): void;
  cycle(): void;
  reset(): void;
}
export class DemoController implements Bridge {
  private initial: SceneData;
  private snapshot: Snapshot;
  private listeners = new Set<() => void>();
  private clock: () => string;
  constructor(scene: SceneData, clock = () => new Date().toISOString()) {
    this.clock = clock;
    this.initial = validateScene(scene);
    this.snapshot = {
      scene: validateScene(scene),
      selectedId: null,
      revision: 0,
    };
  }
  getSnapshot = () => this.snapshot;
  subscribe = (listener: () => void) => {
    this.listeners.add(listener);
    return () => {
      this.listeners.delete(listener);
    };
  };
  private publish(snapshot: Snapshot) {
    this.snapshot = snapshot;
    this.listeners.forEach((listener) => listener());
  }
  select = (id: string) => {
    if (!this.snapshot.scene.objects.some((o) => o.id === id))
      throw new Error("Không tìm thấy stable object ID.");
    this.publish({ ...this.snapshot, selectedId: id });
  };
  cycle = () => {
    const current = this.snapshot.scene.objects.find(
      (o) => o.id === this.snapshot.selectedId,
    );
    if (!current) throw new Error("Hãy chọn đối tượng trước.");
    if (current.provenance.source_kind !== "synthetic")
      throw new Error("PoC chỉ cho sửa trạng thái synthetic.");
    const values = VALUES[current.status.kind];
    const timestamp = this.clock();
    if (!Number.isFinite(Date.parse(timestamp)))
      throw new Error("Clock không hợp lệ.");
    const objects = this.snapshot.scene.objects.map((o) =>
      o.id !== current.id
        ? o
        : {
            ...o,
            status: {
              ...o.status,
              value:
                values[(values.indexOf(o.status.value) + 1) % values.length],
              timestamp,
            },
          },
    );
    this.publish({
      ...this.snapshot,
      scene: { ...this.snapshot.scene, objects },
      revision: this.snapshot.revision + 1,
    });
  };
  reset = () =>
    this.publish({
      scene: structuredClone(this.initial),
      selectedId: null,
      revision: this.snapshot.revision + 1,
    });
}
