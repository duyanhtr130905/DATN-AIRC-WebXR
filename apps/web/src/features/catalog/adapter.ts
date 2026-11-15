import type { CatalogObject, TwinState } from "../live/contracts.ts";
import type { DemoScene, SceneObject } from "../../shared/types.ts";
export function sceneFromCatalog(roomId: string, objects: CatalogObject[], states: Record<string, TwinState>): DemoScene {
    if (objects.length > 100 || new Set(objects.map(o => o.id)).size !== objects.length || objects.some(o => o.room_id !== roomId))
        throw new Error("Scene Catalog capacity/scope");
    const sorted = [...objects].sort((a, b) => a.id.localeCompare(b.id));
    return { id: roomId, sourceKind: "synthetic", objects: sorted.map((o, index): SceneObject => {
            const status = Object.values(states).find(s => s.target_id === o.id && s.state_type === "equipment_status");
            return { id: o.id, roomId: roomId, name: o.name, sourceKind: o.source_kind, description: o.metadata.description ?? "Synthetic Catalog object", position: [(index % 5 - 2) * 1.5, 0.65, (Math.floor(index / 5) - Math.floor((sorted.length - 1) / 5) / 2) * 1.5], equipmentStatus: status?.value.status ?? "unknown", stateVersion: status?.version ?? 0 };
        }) };
}
