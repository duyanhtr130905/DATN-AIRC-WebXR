import type { DemoScene } from "../../shared/types.ts";
// Renderer-independent adapter. Values are arbitrary test coordinates, never room 507 measurements.
export function loadDemo(): DemoScene {
  return {
    id: "demo-room-foundation", sourceKind: "synthetic",
    objects: [
      { id: "demo-object-cube", roomId: "demo-room-foundation", name: "Khối mẫu A", sourceKind: "synthetic", position: [-1.8, 0.65, 0], description: "Primitive để kiểm tra renderer và thao tác chọn." },
      { id: "demo-object-column", roomId: "demo-room-foundation", name: "Khối mẫu B", sourceKind: "synthetic", position: [1.8, 0.65, -1], description: "Dữ liệu minh họa độc lập với AIRC." },
    ],
  };
}
export function selectedObject(scene: DemoScene, id: string | null) {
  return scene.objects.find((object) => object.id === id) ?? null;
}
