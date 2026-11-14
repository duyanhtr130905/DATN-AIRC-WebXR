export type SourceKind = "synthetic" | "unknown" | "real_verified";
export interface SceneObject {
  id: string;
  roomId: string;
  name: string;
  sourceKind: SourceKind;
  position: [number, number, number];
  description: string;
}
export interface DemoScene { id: string; sourceKind: "synthetic"; objects: SceneObject[] }
export interface Health { status: "alive"; service: "airc-api"; timestamp: string }
export interface Readiness { status: "ready" | "not_ready"; database: "ready" | "unavailable" | "not_configured"; timestamp: string }
