import { createRoot } from "react-dom/client";
import {
  World,
  ACESFilmicToneMapping,
  Vector3,
  Mesh,
  BoxGeometry,
  PlaneGeometry,
  MeshStandardMaterial,
  AmbientLight,
  DirectionalLight,
  Color,
  GridHelper,
  createSystem,
  createComponent,
  Types,
  RayInteractable,
  SessionMode,
  type Entity,
} from "@iwsdk/core";
import { OrbitControls } from "three/examples/jsm/controls/OrbitControls.js";
import projectOptions from "virtual:iwsdk-project";
import { Shell, webglAvailable, type Mount } from "../../shared-ui/Shell.tsx";
import {
  DemoController,
  fixture,
  type SceneData,
  type Bridge,
} from "../../shared-fixtures/domain.ts";
const Identity = createComponent("DemoIdentity", {
  stableId: { type: Types.String, default: "" },
  stateValue: { type: Types.String, default: "" },
});
// System owns domain state. Entity indices are never exported as durable object IDs.
class DemoBridgeSystem
  extends createSystem({ objects: { required: [Identity] } })
  implements Bridge
{
  controller = new DemoController(fixture);
  entities = new Map<string, Entity>();
  configure(scene: SceneData) {
    this.controller = new DemoController(scene);
    this.cleanupFuncs.push(
      this.controller.subscribe(() => {
        for (const o of this.controller.getSnapshot().scene.objects) {
          const e = this.entities.get(o.id);
          if (e?.active) e.setValue(Identity, "stateValue", o.status.value);
        }
      }),
    );
  }
  getSnapshot = () => this.controller.getSnapshot();
  subscribe = (listener: () => void) => this.controller.subscribe(listener);
  select = (id: string) => {
    if (!this.entities.get(id)?.active)
      throw new Error("Entity không còn hoạt động.");
    this.controller.select(id);
  };
  cycle = () => {
    const id = this.getSnapshot().selectedId;
    if (!id || !this.entities.get(id)?.active)
      throw new Error("Không có entity được chọn.");
    this.controller.cycle();
  };
  reset = () => this.controller.reset();
}
const mount: Mount = (host, scene, ready, fail) => {
  if (!webglAvailable()) {
    fail("WebGL2 không khả dụng trong môi trường hiện tại.");
    return () => {};
  }
  let cancelled = false;
  let world: World | undefined;
  let dispose = () => {};
  World.create(host, {
    ...projectOptions,
    xr: {
      sessionMode: SessionMode.ImmersiveVR,
      offer: "none",
      launchOnSessionGranted: false,
    },
    features: { ...projectOptions.features, spatialUI: false },
  })
    .then((created) => {
      world = created;
      if (cancelled) {
        created.destroy();
        return;
      }
      created.scene.background = new Color("#e9ede4");
      created.renderer.toneMapping = ACESFilmicToneMapping;
      created.renderer.setPixelRatio(1);
      created.renderer.domElement.dataset.renderer = "iwsdk";
      created.registerSystem(DemoBridgeSystem);
      const bridge = created.getSystem(DemoBridgeSystem)!;
      bridge.configure(scene);
      const add = (mesh: Mesh) => {
        created.createTransformEntity(mesh);
        return mesh;
      };
      const ambient = new AmbientLight(0xffffff, 1.7);
      created.scene.add(ambient);
      const light = new DirectionalLight(0xffffff, 3);
      light.position.set(5, 10, 7);
      created.scene.add(light);
      const floor = add(
        new Mesh(
          new PlaneGeometry(12, 9),
          new MeshStandardMaterial({ color: "#d9dfce", roughness: 1 }),
        ),
      );
      floor.rotation.x = -Math.PI / 2;
      floor.position.y = -0.04;
      created.scene.add(new GridHelper(12, 12, "#bec9b8", "#cdd5c5"));
      const wall = add(
        new Mesh(
          new BoxGeometry(12, 3, 0.12),
          new MeshStandardMaterial({ color: "#f8f3e8" }),
        ),
      );
      wall.position.set(0, 1.5, -4.5);
      const side = add(
        new Mesh(
          new BoxGeometry(0.12, 3, 9),
          new MeshStandardMaterial({ color: "#ece8db" }),
        ),
      );
      side.position.set(-6, 1.5, 0);
      const meshes = new Map<string, Mesh>();
      scene.objects.forEach((o, i) => {
        const mesh = new Mesh(
          new BoxGeometry(1.35, 1.3, 1.1),
          new MeshStandardMaterial({
            color: ["#347569", "#557c9a", "#9c8163", "#5b7e66", "#a98a44"][i],
            roughness: 0.65,
          }),
        );
        mesh.position.set(...o.position);
        mesh.name = o.id;
        const entity = created.createTransformEntity(mesh);
        entity.addComponent(Identity, {
          stableId: o.id,
          stateValue: o.status.value,
        });
        entity.addComponent(RayInteractable);
        entity.object3D!.addEventListener("click", () => bridge.select(o.id));
        bridge.entities.set(o.id, entity);
        meshes.set(o.id, mesh);
        const base = add(
          new Mesh(
            new BoxGeometry(1.7, 0.08, 1.5),
            new MeshStandardMaterial({ color: "#b7c5ad" }),
          ),
        );
        base.position.set(o.position[0], 0.04, o.position[2]);
      });
      const controls = new OrbitControls(
        created.camera,
        created.renderer.domElement,
      );
      controls.target.set(0, 0.4, 0);
      controls.minDistance = 5;
      controls.maxDistance = 25;
      controls.maxPolarAngle = Math.PI / 2 - 0.05;
      controls.update();
      const resize = () => {
        if (created.renderer.xr.isPresenting) return;
        const r = host.getBoundingClientRect();
        created.renderer.setSize(r.width, r.height, false);
        created.camera.aspect = r.width / r.height;
        created.camera.updateProjectionMatrix();
      };
      const observer = new ResizeObserver(resize);
      observer.observe(host);
      window.addEventListener("resize", resize);
      resize();
      const unlisten = bridge.subscribe(() => {
        const s = bridge.getSnapshot();
        s.scene.objects.forEach((o, i) => {
          const m = meshes.get(o.id)!.material as MeshStandardMaterial;
          m.color.set(
            s.selectedId === o.id
              ? "#c67537"
              : ["#347569", "#557c9a", "#9c8163", "#5b7e66", "#a98a44"][i],
          );
          m.emissive.set(s.selectedId === o.id ? "#46250c" : "#000000");
        });
      });
      const lost = () => fail("WebGL context đã mất; hãy tải lại trang.");
      created.renderer.domElement.addEventListener("webglcontextlost", lost);
      dispose = () => {
        observer.disconnect();
        window.removeEventListener("resize", resize);
        unlisten();
        controls.dispose();
        created.renderer.domElement.removeEventListener(
          "webglcontextlost",
          lost,
        );
      };
      window.__poc = {
        engine: "IWSDK",
        snapshot: () => structuredClone(bridge.getSnapshot()),
        project: (id) => {
          const o = scene.objects.find((o) => o.id === id)!;
          const v = new Vector3(...o.position).project(created.camera);
          const r = created.renderer.domElement.getBoundingClientRect();
          return {
            x: r.left + ((v.x + 1) * r.width) / 2,
            y: r.top + ((1 - v.y) * r.height) / 2,
          };
        },
        info: () => ({
          calls: created.renderer.info.render.calls,
          triangles: created.renderer.info.render.triangles,
        }),
        xr: () => ({
          active: created.renderer.xr.isPresenting,
          inputs: created.session?.inputSources.length || 0,
        }),
        ecs: () =>
          [...bridge.entities].map(([id, e]) => ({
            id,
            index: e.index,
            stableId: e.getValue(Identity, "stableId"),
            state: e.getValue(Identity, "stateValue"),
          })),
        device: () => window.IWER_DEVICE,
      };
      ready({
        bridge,
        exit: async () => {
          await created.session?.end();
        },
        resetCamera: () => {
          created.camera.position.set(10, 9, 14);
          controls.target.set(0, 0.4, 0);
          controls.update();
        },
        enter: async (mode) => {
          if (!navigator.xr || !(await navigator.xr.isSessionSupported(mode)))
            throw new Error("Mode không được runtime hỗ trợ.");
          created.launchXR({
            sessionMode:
              mode === "immersive-vr"
                ? SessionMode.ImmersiveVR
                : SessionMode.ImmersiveAR,
          });
          const deadline = Date.now() + 12000;
          while (!created.session) {
            if (Date.now() > deadline)
              throw new Error(
                "Session không khởi động; có thể do quyền/runtime.",
              );
            await new Promise((r) => setTimeout(r, 50));
          }
        },
      });
    })
    .catch((error) => {
      if (!cancelled) fail(String(error));
    });
  return () => {
    cancelled = true;
    delete window.__poc;
    dispose();
    world?.destroy();
  };
};
createRoot(document.getElementById("root")!).render(
  <Shell label="B / Meta Immersive Web SDK" mount={mount} />,
);
