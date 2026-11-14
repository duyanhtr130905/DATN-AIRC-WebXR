import type { Snapshot } from "../shared-fixtures/domain.ts";
declare global {
  interface Window {
    __poc?: {
      engine: string;
      snapshot(): Snapshot;
      project(id: string): { x: number; y: number };
      info(): { calls: number; triangles: number };
      xr(): { active: boolean; inputs: number };
      ecs?(): unknown;
      device?(): any;
    };
    IWER_DEVICE?: any;
  }
}
export {};
