import { diagnostic } from "../features/live/diagnostics.ts";
import type { SceneObject } from "../shared/types.ts";
import type { Mesh, MeshStandardMaterial } from "three";
import { useCallback, useEffect, useRef, useState } from "react";
import { Canvas, useThree } from "@react-three/fiber";
import { XR, createXRStore } from "@react-three/xr";
import { OrbitControls } from "three/examples/jsm/controls/OrbitControls.js";
import type { DemoScene as SceneData } from "../shared/types.ts";
import { ErrorBoundary } from "../components/ErrorBoundary.tsx";
function supportsWebGL() {
    const canvas = document.createElement("canvas");
    const context = canvas.getContext("webgl2");
    context?.getExtension("WEBGL_lose_context")?.loseContext();
    return Boolean(context);
}
function Controls({ fail }: {
    fail(): void;
}) {
    const { camera, gl } = useThree();
    useEffect(() => {
        const controls = new OrbitControls(camera, gl.domElement);
        controls.target.set(0, 0.5, 0);
        controls.minDistance = 4;
        controls.maxDistance = 20;
        controls.maxPolarAngle = Math.PI / 2 - 0.05;
        controls.update();
        const lost = (event: Event) => { event.preventDefault(); fail(); };
        gl.domElement.addEventListener("webglcontextlost", lost);
        return () => { controls.dispose(); gl.domElement.removeEventListener("webglcontextlost", lost); };
    }, [camera, gl, fail]);
    return null;
}
// Dedicated lifecycle: no auto session, emulator or camera acquisition in the official foundation.
export default function DemoScene({ scene, selectedId, select }: {
    scene: SceneData;
    selectedId: string | null;
    select(id: string): void;
}) {
    const [supported] = useState(supportsWebGL);
    const [ready, setReady] = useState(false);
    const [lost, setLost] = useState(false);
    const onLost = useCallback(() => setLost(true), []);
    const [store] = useState(() => createXRStore({ offerSession: false, enterGrantedSession: false, emulate: false, controller: { model: false }, hand: { model: false } }));
    useEffect(() => () => store.destroy(), [store]);
    if (!supported || lost)
        return <p role="alert">WebGL2 không khả dụng hoặc context đã mất. Bạn vẫn có thể xem danh sách đối tượng DEMO.</p>;
    return <ErrorBoundary>
    {!ready && <p role="status">Đang chuẩn bị renderer…</p>}
    <Canvas aria-label="Không gian 3D DEMO" camera={{ position: [8, 7, 11], fov: 45 }} dpr={[1, 1.5]} onCreated={() => setReady(true)}>
      <XR store={store}>
        <color attach="background" args={["#e7ece8"]}/>
        <ambientLight intensity={1.8}/><directionalLight position={[5, 8, 4]} intensity={2.5}/>
        <Controls fail={onLost}/>
        <mesh rotation={[-Math.PI / 2, 0, 0]}><planeGeometry args={[9, 7]}/><meshStandardMaterial color="#d1ddd4"/></mesh>
        <gridHelper args={[9, 9, "#96ada1", "#bdcbc2"]} position={[0, 0.01, 0]}/>
        <mesh position={[0, 1.5, -3.5]}><boxGeometry args={[9, 3, 0.12]}/><meshStandardMaterial color="#f6f3e9"/></mesh>
        {scene.objects.map(object => <StateMesh key={object.id} object={object} selected={object.id === selectedId} select={select}/>)}
      </XR>
    </Canvas>
  </ErrorBoundary>;
}
function StateMesh({ object, selected, select }: {
    object: SceneObject;
    selected: boolean;
    select(id: string): void;
}) {
    const mesh = useRef<Mesh>(null);
    const observed = useRef("");
    const color = object.equipmentStatus === "maintenance" ? "#c14336" : object.equipmentStatus === "offline" ? "#6c7377" : selected ? "#c46b37" : object.equipmentStatus === "unknown" ? "#768b98" : "#357469";
    return <mesh ref={mesh} name={object.id} position={object.position} userData={{ objectId: object.id, equipmentStatus: object.equipmentStatus ?? "unknown", version: object.stateVersion ?? 0 }} onClick={event => { event.stopPropagation(); select(object.id); }} onAfterRender={renderer => {
            const material = mesh.current?.material as MeshStandardMaterial | undefined;
            const actual = material?.color.getHexString();
            const key = `${object.stateVersion}/${actual}`;
            if (actual && observed.current !== key) {
                observed.current = key;
                diagnostic("scene.afterRender", { roomId: object.roomId, objectId: object.id, version: object.stateVersion ?? 0, status: object.equipmentStatus ?? "unknown", materialColor: actual, drawCalls: renderer.info.render.calls });
            }
        }}><boxGeometry args={[1.3, 1.3, 1.3]}/><meshStandardMaterial color={color}/></mesh>;
}
