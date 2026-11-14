import { Component, useEffect, useRef, useSyncExternalStore } from "react";
import { createRoot } from "react-dom/client";
import { Canvas, useThree } from "@react-three/fiber";
import { XR, createXRStore } from "@react-three/xr";
import { OrbitControls } from "three/examples/jsm/controls/OrbitControls.js";
import { Vector3 } from "three";
import { Shell, webglAvailable, type Mount } from "../../shared-ui/Shell.tsx";
import { DemoController } from "../../shared-fixtures/domain.ts";
const emulate = new URLSearchParams(location.search).get("emulate") === "1";
const store = createXRStore({
  offerSession: false,
  enterGrantedSession: false,
  controller: { model: false },
  hand: { model: false },
  emulate: emulate ? { inject: true, syntheticEnvironment: false } : false,
});
// IWER 2.8 protects native navigator.xr even when it reports no device. Explicit emulation URL is consent to install its JS runtime, not a claim about native support.
const unsubscribeEmulator = store.subscribe((state, previous) => {
  if (emulate && state.emulator && state.emulator !== previous.emulator)
    state.emulator.installRuntime({ forceInstall: true });
});
class Boundary extends Component<
  { children: React.ReactNode; fail(message: string): void },
  { error: boolean }
> {
  state = { error: false };
  static getDerivedStateFromError() {
    return { error: true };
  }
  componentDidCatch(error: Error) {
    this.props.fail(error.message);
  }
  render() {
    return this.state.error ? null : this.props.children;
  }
}
let resetCamera = () => {};
function Camera({ controller }: { controller: DemoController }) {
  const { camera, gl } = useThree();
  useEffect(() => {
    const controls = new OrbitControls(camera, gl.domElement);
    controls.target.set(0, 0.4, 0);
    controls.minDistance = 5;
    controls.maxDistance = 25;
    controls.maxPolarAngle = Math.PI / 2 - 0.05;
    controls.update();
    resetCamera = () => {
      camera.position.set(10, 9, 14);
      controls.target.set(0, 0.4, 0);
      controls.update();
    };
    const lost = (event: Event) => event.preventDefault();
    gl.domElement.addEventListener("webglcontextlost", lost);
    return () => {
      controls.dispose();
      gl.domElement.removeEventListener("webglcontextlost", lost);
      resetCamera = () => {};
    };
  }, [camera, gl]);
  return null;
}
function Scene({ controller }: { controller: DemoController }) {
  const s = useSyncExternalStore(
    controller.subscribe,
    controller.getSnapshot,
    controller.getSnapshot,
  );
  return (
    <>
      <color attach="background" args={["#e9ede4"]} />
      <ambientLight intensity={1.7} />
      <directionalLight position={[5, 10, 7]} intensity={3} />
      <Camera controller={controller} />
      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, -0.04, 0]}>
        <planeGeometry args={[12, 9]} />
        <meshStandardMaterial color="#d9dfce" roughness={1} />
      </mesh>
      <gridHelper args={[12, 12, "#bec9b8", "#cdd5c5"]} position={[0, 0, 0]} />
      <mesh position={[0, 1.5, -4.5]}>
        <boxGeometry args={[12, 3, 0.12]} />
        <meshStandardMaterial color="#f8f3e8" />
      </mesh>
      <mesh position={[-6, 1.5, 0]}>
        <boxGeometry args={[0.12, 3, 9]} />
        <meshStandardMaterial color="#ece8db" />
      </mesh>
      {s.scene.objects.map((o, i) => (
        <group key={o.id}>
          <mesh
            position={o.position}
            onClick={(e) => {
              e.stopPropagation();
              controller.select(o.id);
            }}
            name={o.id}
          >
            <boxGeometry args={[1.35, 1.3, 1.1]} />
            <meshStandardMaterial
              color={
                s.selectedId === o.id
                  ? "#c67537"
                  : ["#347569", "#557c9a", "#9c8163", "#5b7e66", "#a98a44"][i]
              }
              roughness={0.65}
              emissive={s.selectedId === o.id ? "#46250c" : "#000000"}
            />
          </mesh>
          <mesh position={[o.position[0], 0.04, o.position[2]]}>
            <boxGeometry args={[1.7, 0.08, 1.5]} />
            <meshStandardMaterial color="#b7c5ad" />
          </mesh>
        </group>
      ))}
    </>
  );
}
const mount: Mount = (host, scene, ready, fail) => {
  if (!webglAvailable()) {
    fail("WebGL2 không khả dụng trong môi trường hiện tại.");
    return () => {};
  }
  const controller = new DemoController(scene);
  const root = createRoot(host);
  root.render(
    <Boundary fail={fail}>
      <Canvas
        camera={{ position: [10, 9, 14], fov: 50 }}
        dpr={1}
        gl={{ antialias: true }}
        onCreated={({ gl, camera }) => {
          window.__poc = {
            engine: "R3F",
            snapshot: () => structuredClone(controller.getSnapshot()),
            project: (id) => {
              const o = scene.objects.find((o) => o.id === id)!;
              const v = new Vector3(...o.position).project(camera);
              const r = gl.domElement.getBoundingClientRect();
              return {
                x: r.left + ((v.x + 1) * r.width) / 2,
                y: r.top + ((1 - v.y) * r.height) / 2,
              };
            },
            info: () => ({
              calls: gl.info.render.calls,
              triangles: gl.info.render.triangles,
            }),
            xr: () => ({
              active: gl.xr.isPresenting,
              inputs: gl.xr.getSession()?.inputSources.length || 0,
            }),
            device: () => store.getState().emulator,
          };
          gl.domElement.dataset.renderer = "r3f";
          gl.domElement.addEventListener(
            "webglcontextlost",
            () => fail("WebGL context đã mất; hãy tải lại trang."),
            { once: true },
          );
          ready({
            bridge: controller,
            exit: async () => {
              await store.getState().session?.end();
            },
            resetCamera: () => resetCamera(),
            enter: async (mode) => {
              if (
                !navigator.xr ||
                !(await navigator.xr.isSessionSupported(mode))
              )
                throw new Error("Mode không được runtime hỗ trợ.");
              if (mode === "immersive-vr") await store.enterVR();
              else await store.enterAR();
            },
          });
        }}
      >
        <XR store={store}>
          <Scene controller={controller} />
        </XR>
      </Canvas>
    </Boundary>,
  );
  return () => {
    delete window.__poc;
    unsubscribeEmulator();
    root.unmount();
    store.destroy();
  };
};
createRoot(document.getElementById("root")!).render(
  <Shell label="A / React Three Fiber + XR" mount={mount} />,
);
