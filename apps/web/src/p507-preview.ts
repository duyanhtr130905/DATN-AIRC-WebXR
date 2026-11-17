/** Development-only P507 review. No production scene or automatic XR access. */
import {
  ACESFilmicToneMapping, AmbientLight, Box3, Color, DirectionalLight, HemisphereLight,
  Material, Matrix4, Mesh, MeshStandardMaterial, Object3D, PCFSoftShadowMap, PerspectiveCamera, PMREMGenerator,
  RectAreaLight, Scene, SRGBColorSpace, Texture, Vector3, WebGLRenderer
} from "three";
import { GLTFLoader } from "three/examples/jsm/loaders/GLTFLoader.js";
import { OrbitControls } from "three/examples/jsm/controls/OrbitControls.js";
import { RoomEnvironment } from "three/examples/jsm/environments/RoomEnvironment.js";
import { RectAreaLightUniformsLib } from "three/examples/jsm/lights/RectAreaLightUniformsLib.js";

const canvas = document.querySelector<HTMLCanvasElement>("#view");
const status = document.querySelector<HTMLElement>("#status");
const stats = document.querySelector<HTMLElement>("#stats");
const show = (message: string) => { if (status) status.textContent = message; };
type ReviewAPI = { aim: (key: string) => void; pause: () => void; snapshot: () => Record<string, unknown> };
declare global { interface Window { __P507_REVIEW__?: ReviewAPI } }

if (!import.meta.env.DEV) show("BẢN PREVIEW CHỈ HỖ TRỢ VITE DEV, KHÔNG ĐƯỢC DEPLOY.");
else if (!canvas || !window.WebGL2RenderingContext) show("WebGL2 không khả dụng. Không thể xem preview.");
else run(canvas).catch(error => show("Không thể mở cảnh 3D: " + String(error)));

async function run(element: HTMLCanvasElement) {
  const gl = new WebGLRenderer({ canvas: element, antialias: true, powerPreference: "high-performance" });
  // Refraction target is half resolution; the main screenshot remains full viewport.
  // This is recorded in metrics and does not alter asset geometry/materials.
  gl.transmissionResolutionScale = .5;
  gl.setPixelRatio(Math.min(window.devicePixelRatio, 1.5));
  gl.setSize(window.innerWidth, window.innerHeight);
  gl.outputColorSpace = SRGBColorSpace;
  gl.toneMapping = ACESFilmicToneMapping;
  gl.toneMappingExposure = 1;
  gl.shadowMap.enabled = true;
  gl.shadowMap.type = PCFSoftShadowMap;
  // Scene is static: reuse the shadow map until a cutaway/camera preset changes.
  gl.shadowMap.autoUpdate = false;
  const scene = new Scene();
  scene.background = new Color("#d9dedc");
  // Self-generated neutral room reflections: no remote HDRI or private photograph.
  const pmrem = new PMREMGenerator(gl);
  const environment = new RoomEnvironment();
  const environmentTarget = pmrem.fromScene(environment, .04, .1, 100);
  scene.environment = environmentTarget.texture;
  scene.environmentIntensity = .30;
  environment.dispose(); pmrem.dispose();
  scene.add(new AmbientLight(0xffffff, .04));
  scene.add(new HemisphereLight(0xe4efff, 0xc1b7a2, .34));
  const sun = new DirectionalLight(0xfff4e3, 2);
  // Source is just inside east glazing; window placeholders cannot block daylight.
  sun.position.set(6.6, 3.1, -5);
  sun.target.position.set(1.4, .1, -6.1);
  sun.castShadow = true;
  sun.shadow.mapSize.set(1024, 1024);
  sun.shadow.camera.near = .1; sun.shadow.camera.far = 18;
  sun.shadow.camera.left = -5; sun.shadow.camera.right = 5;
  sun.shadow.camera.top = 5; sun.shadow.camera.bottom = -5;
  sun.shadow.normalBias = .012; sun.shadow.bias = -.0001;
  sun.shadow.radius = 3;
  scene.add(sun, sun.target);
  RectAreaLightUniformsLib.init();
  // Eight modelled panel diffusers remain in the GLB. Two broad area strips
  // approximate their aggregate indirect fill; this is realtime lookdev, not GI simulation.
  for (const x of [1.4375, 5.4625]) {
    const panelFill = new RectAreaLight(0xfff2dc, .95, .65, 6.5);
    panelFill.position.set(x, 3.40, -4.6575); panelFill.lookAt(x, 0, -4.6575);
    scene.add(panelFill);
  }
  const camera = new PerspectiveCamera(58, window.innerWidth / window.innerHeight, .04, 60);
  const controls = new OrbitControls(camera, element);
  controls.enableDamping = true;
  controls.minDistance = .3; controls.maxDistance = 22;
  controls.maxPolarAngle = Math.PI * .98;
  // Survey XYZ -> glTF (x,z,-y); exporter already performs this conversion.
  const presets = {
    cluster_A: {pos:[4.05,4.8,-7],target:[4.05,.25,-7.001],fov:50,cutaway:true,source:"OWNER_34_LAYOUT",confidence:"Geometric review camera"},
    cluster_B: {pos:[3.65,4.8,-4.2],target:[3.65,.25,-4.201],fov:50,cutaway:true,source:"OWNER_34_LAYOUT",confidence:"Geometric review camera"},
    cluster_C: {pos:[4.1,4.8,-1.3],target:[4.1,.25,-1.301],fov:50,cutaway:true,source:"OWNER_34_LAYOUT",confidence:"Geometric review camera"},
    door_outward: {pos:[-2.5,1.65,-7.415],target:[.1,1.3,-7.415],fov:78,cutaway:false,source:"OWNER_OUTWARD",confidence:"Exterior demonstration; outside corridor UNKNOWN"},
    door_closed: {pos:[-2.5,1.65,-7.415],target:[.1,1.3,-7.415],fov:78,cutaway:false,source:"OWNER_OUTWARD",confidence:"Same GLB leaves closed about exported hinges for inspection"},
    shelf: {pos:[2.1,1.65,-2.8],target:[.3,1.05,-2.8],fov:76,cutaway:false,source:"PHOTO-04/OWNER",confidence:"Proposed1.50m shelf, not measured"},
    vanilla_wall: {pos:[4,1.65,-6.9],target:[3.8,2.2,-9.245],fov:75,cutaway:false,source:"PHOTO-04/05/OWNER",confidence:"Relative vanilla tone; no calibrated color claim"},
    hero: { pos: [2.90, 1.65, -6.865], target: [1.45, 1.60, -8.865], fov: 78, cutaway: false, source: "PHOTO-13", confidence: "ESTIMATED, not calibrated" },
    tv_corner: { pos: [2.60, 1.65, -7.365], target: [1.20, 1.65, -8.865], fov: 78, cutaway: false, source: "PHOTO-01/13", confidence: "ESTIMATED, not calibrated" },
    entry: { pos: [.76, 1.72, -8.165], target: [3.55, .95, -3.2], fov: 84, cutaway: false, source: "SKETCH-FLOOR/PHOTO-12", confidence: "Geometric review camera" },
    wide: { pos: [.72, 1.68, -4.7], target: [3.15, 1.05, -7.45], fov: 74, cutaway: false, source: "PHOTO-06", confidence: "ESTIMATED" },
    overview: { pos: [3.45, 12.5, -4.6575], target: [3.45, 0, -4.6585], fov: 52, cutaway: true, source: "SKETCH-FLOOR", confidence: "Geometric review camera" },
    clusters: { pos: [8.9, 9, -4.7], target: [3.45, .35, -4.5], fov: 53, cutaway: true, source: "SKETCH-FLOOR/PHOTO-07", confidence: "Architectural cutaway" },
    photo_wall: { pos: [4.15, 1.65, -6.565], target: [4.15, 2.35, -9.245], fov: 61, cutaway: false, source: "PHOTO-09", confidence: "ESTIMATED, not calibrated" },
    utility: { pos: [3.50, 2.0, -2.9], target: [.30, 1.15, -2.9], fov: 76, cutaway: false, source: "PHOTO-04/05/11", confidence: "Elevated review camera, not source pose" },
    ceiling: { pos: [3.45, 1.65, -4.6575], target: [3.45, 3.50, -4.6585], fov: 135, cutaway: false, source: "PHOTO-12/CEILING-DIGITAL", confidence: "Wide upward inspection, not source pose" },
    windows: { pos: [1.10, 1.70, -4.05], target: [6.86, 1.95, -4.6575], fov: 74, cutaway: false, source: "PHOTO-03/12", confidence: "ESTIMATED, not calibrated" },
    logo: { pos: [3.45, 1.65, -3.50], target: [3.45, 1.90, -.08], fov: 70, cutaway: false, source: "PHOTO-10", confidence: "Neutral brand placeholder only" }
  };
  type Preset = keyof typeof presets;
  let current: Preset = "hero";
  const overheadNodes: Object3D[] = [], eastWalls: Object3D[] = [];
  const doorRoots: {node:Object3D; open:Matrix4; closed:Matrix4}[] = [];
  function setDoorPose(closed:boolean) {
    for (const leaf of doorRoots) (closed ? leaf.closed : leaf.open).decompose(leaf.node.position,leaf.node.quaternion,leaf.node.scale);
    scene.updateMatrixWorld(true);
  }
  const frameTimes: number[] = [];
  let paused = false;
  let prior: number | null = null;
  function aim(key: string) {
    if (!(key in presets)) throw new Error("Unknown review camera: " + key);
    current = key as Preset;
    paused = false; prior = null;
    gl.shadowMap.needsUpdate = true;
    const preset = presets[current];
    setDoorPose(current === "door_closed");
    overheadNodes.forEach(node => { node.visible = !preset.cutaway; });
    // Explicit architectural cutaway only. All furniture stays visible in every shot.
    eastWalls.forEach(node => { node.visible = !(current === "clusters" || current.startsWith("cluster_")); });
    camera.position.fromArray(preset.pos); controls.target.fromArray(preset.target);
    camera.fov = current === "hero" && camera.aspect < .8 ? 94 : preset.fov;
    if (current === "hero" && camera.aspect < .8) {
      camera.position.set(1.35, 1.62, -5.565); controls.target.set(1.35, 1.45, -8.915);
    }
    if (current === "overview") camera.position.y = Math.max(camera.position.y, 3.35 / (Math.tan(camera.fov * Math.PI / 360) * camera.aspect)); camera.updateProjectionMatrix(); controls.update();
    frameTimes.length = 0;
    const note = document.querySelector("#camera-note");
    if (note) note.textContent = preset.cutaway ? "CUTAWAY: chỉ ẩn trần/tường ngoài để kiểm tra; giữ toàn bộ nội thất." : "Nguồn ảnh đã đối chiếu; camera ước lượng, PHOTO_MATCH PARTIAL.";
  }
  for (const key of Object.keys(presets)) document.getElementById(key)?.addEventListener("click", () => aim(key));
  const assetUrl = "/p507-local-preview/P507_G1_G2_PROVISIONAL.glb";
  const loadStart = performance.now();
  const response = await fetch(assetUrl);
  if (!response.ok) throw new Error("Chưa có GLB local. Chạy Blender generator và chép vào p507-local-preview.");
  const bytes = await response.arrayBuffer();
  const gltf = await new GLTFLoader().parseAsync(bytes, "/p507-local-preview/");
  const loaded = gltf.scene;
  const loadTimeMs = performance.now() - loadStart;
  if (new Box3().setFromObject(loaded).isEmpty()) throw new Error("GLB has no geometry");
  let meshCount = 0, triangleCount = 0;
  const ids = new Set<string>(), geometries = new Set(), materials = new Set<Material>(), textures = new Set<Texture>();
  const objectBounds: Record<string, number[]> = {};
  const windowCenters: number[][] = [];
  const componentBounds: Record<string, number[]> = {};
  const assetMetadata: Record<string, Record<string, unknown>> = {};
  const blindNames = new Set<string>();
  let inventoryTotal = 36, approvedLayoutTotal = 34;
  let roomDimensions={width_x:6.9,length_y:9.315,height_z:3.5};
  let surveyBaseline:Record<string,unknown>={};
  const chairBackCenters:Record<string,number[]>={};
  const fileGlassBays:Record<string,number[]>={}; let fileGlassAlpha=1;
  let wallBaseColorSrgb="";let wallMaterialUses=0;
  let unplacedIds: string[] = [];
  let unplacedReasons: Record<string,string> = {};
  loaded.traverse(node => {
    if (typeof node.userData.room_dimensions_survey_axes === "string") roomDimensions=JSON.parse(node.userData.room_dimensions_survey_axes);
    if (typeof node.userData.survey_baseline === "string") surveyBaseline=JSON.parse(node.userData.survey_baseline);
    if (typeof node.userData.approved_layout_chair_count === "number") approvedLayoutTotal=node.userData.approved_layout_chair_count;
    if (typeof node.userData.unplaced_chair_reasons === "string") unplacedReasons = JSON.parse(node.userData.unplaced_chair_reasons);
    if (typeof node.userData.chair_inventory_count === "number") inventoryTotal = node.userData.chair_inventory_count;
    if (Array.isArray(node.userData.unplaced_chair_ids)) unplacedIds = node.userData.unplaced_chair_ids;
    else if (typeof node.userData.unplaced_chair_ids === "string") unplacedIds = JSON.parse(node.userData.unplaced_chair_ids);
    if (typeof node.userData.survey_instance_id === "string") {
      ids.add(node.userData.survey_instance_id);
      assetMetadata[node.userData.survey_instance_id] = { ...assetMetadata[node.userData.survey_instance_id], ...node.userData };
    }
    // glTF multi-material assets are Groups: collect cutaway roots BEFORE mesh filtering.
    if (node.name.startsWith("P507_ARCH_CEILING") || node.name.startsWith("P507_CEILING") || ["light_panel","ceiling_fan","cassette_ac","projector","camera"].includes(node.userData.logical_type)) overheadNodes.push(node);
    if (/P507_ARCH_(WALL_EAST|EAST_|WINDOW_|ROLLER_|BLIND_|BASEBOARD_EAST)/.test(node.name)) eastWalls.push(node);
    const mesh = node as Mesh;
    if (!mesh.isMesh) return;
    if (node.name.includes("ROLLER_SHADE") || node.name.includes("BLIND_FABRIC")) blindNames.add(node.name);
    meshCount++; mesh.castShadow = true; mesh.receiveShadow = true;
    if (mesh.name.includes("WINDOW_GLASS")) mesh.castShadow = false;
    geometries.add(mesh.geometry);
    triangleCount += Math.floor((mesh.geometry.index?.count ?? mesh.geometry.attributes.position?.count ?? 0) / 3);
    for (const mat of Array.isArray(mesh.material) ? mesh.material : [mesh.material]) {
      materials.add(mat);
      if(mat.name==='P507_PBR_FILE_CABINET_CLEAR_GLASS') fileGlassAlpha=mat.opacity;
      if (mat instanceof MeshStandardMaterial && mat.name === "P507_PBR_CREAM_PAINT") {wallBaseColorSrgb="#"+mat.color.getHexString().toUpperCase();wallMaterialUses++;}
      if (mat instanceof MeshStandardMaterial && mat.name.includes("OFF_SCREEN")) mat.envMapIntensity = .12;
      if (mat instanceof MeshStandardMaterial && mat.name.includes("TV_BEZEL")) mat.envMapIntensity = .35;
      for (const value of Object.values(mat)) if (value instanceof Texture) textures.add(value);
    }
    const id = mesh.userData.survey_instance_id;
    if (typeof id === "string") ids.add(id);
  });
  loaded.updateMatrixWorld(true);
  loaded.traverse(node => {
    let owner:Object3D|null=node;
    while(owner && typeof owner.userData.survey_instance_id!=="string") owner=owner.parent;
    const id=owner?.userData.survey_instance_id;
    if (typeof id !== "string") return;
    if (id.startsWith("P507-DOOR-LEAF-") && node.userData.door_swing === "OUTWARD" && node.parent?.userData.survey_instance_id !== id) {
      const h=node.userData.hinge_survey as number[], angle=Number(node.userData.demo_open_angle_deg)*Math.PI/180;
      const hinge=new Vector3(h[0],h[2],-h[1]);
      const delta=new Matrix4().makeTranslation(hinge.x,hinge.y,hinge.z).multiply(new Matrix4().makeRotationY(-angle)).multiply(new Matrix4().makeTranslation(-hinge.x,-hinge.y,-hinge.z));
      const parentInverse=node.parent ? node.parent.matrixWorld.clone().invert() : new Matrix4();
      doorRoots.push({node,open:node.matrix.clone(),closed:parentInverse.multiply(delta).multiply(node.matrixWorld)});
    }
    if(Number.isInteger(node.userData.file_cabinet_bay)) {const b=new Box3().setFromObject(node);fileGlassBays[String(node.userData.file_cabinet_bay)]=[...b.min.toArray(),...b.max.toArray()];}
    const mesh=node as Mesh;
    if (id.startsWith("P507-CHAIR-") && mesh.isMesh) {
      const positions=mesh.geometry.attributes.position;const sum=new Vector3();let count=0;
      for(let i=0;i<positions.count;i++){const v=new Vector3().fromBufferAttribute(positions,i).applyMatrix4(mesh.matrixWorld);if(v.y>.85){sum.add(v);count++;}}
      if(count) chairBackCenters[id]=sum.multiplyScalar(1/count).toArray();
    }
  });
  loaded.traverse(node => {
    if (node.name.startsWith("P507_ARCH_WINDOW_GLASS")) windowCenters.push(node.getWorldPosition(new Vector3()).toArray());
    if (node.name.includes("WATER_CONTROL") || (node.name.includes("WATER_BODY") || node.name.includes("WATER_GRAY_ENCLOSURE")) || node.name.includes("TV_BLACK_SCREEN") || node.name.includes("TV_REAR")) {
      const box = new Box3().setFromObject(node);
      componentBounds[node.name] = [...box.min.toArray(), ...box.max.toArray()];
    }
  });
  for (const id of ids) {
    const bounds = new Box3();
    loaded.traverse(node => { if (node.userData.survey_instance_id === id) bounds.union(new Box3().setFromObject(node)); });
    objectBounds[id] = [...bounds.min.toArray(), ...bounds.max.toArray()];
  }
  const placedChairIds = [...ids].filter(id => id.startsWith("P507-CHAIR-"));
  scene.add(loaded); aim("hero");
  show(`GLB PROVISIONAL đã tải: ${meshCount} meshes, ${triangleCount} triangles. Ghế lịch sử ${inventoryTotal}; bố cục chốt ${approvedLayoutTotal}; đã đặt ${placedChairIds.length}; chưa đặt ${unplacedIds.length}; UNPLACED ${inventoryTotal - placedChairIds.length}. Cần chủ dự án duyệt hình.`);
  const unplaced = document.querySelector("#unplaced");
  if (unplaced) unplaced.textContent = unplacedIds.length ? "Chưa đặt trong phương án này: " + unplacedIds.map(id => id + (unplacedReasons[id] ? " — " + unplacedReasons[id] : "")).join("; ") : `Inventory ${inventoryTotal}; số ghế chưa đặt ${inventoryTotal - placedChairIds.length}. Vị trí vẫn provisional.`;
  const quantile = (a: number[], q: number) => a.slice().sort((x, y) => x - y)[Math.max(0, Math.ceil(q * a.length) - 1)] ?? 0;
  const context = gl.getContext();
  const debug = context.getExtension("WEBGL_debug_renderer_info");
  const textureMemoryBytes = [...textures].reduce((sum, tex) => {
    const image = tex.image as { width?: number; height?: number } | undefined;
    return sum + (image?.width ?? 0) * (image?.height ?? 0) * 4 * (tex.generateMipmaps ? 4 / 3 : 1);
  }, 0);
  let stopped = false, frames = 0, lastReport = performance.now(), firstFrameCompletedMs: number | null = null;
  const effectiveVisible = (node: Object3D) => {
    let at: Object3D | null = node;
    while (at) { if (!at.visible) return false; at=at.parent; }
    return true;
  };
  const visibilityEvidence = () => {
    const ceilingEnabled=new Set<string>(), hiddenFurniture=new Set<string>(), ceilingInFrustum=new Set<string>();
    loaded.traverse(node => {
      const id=node.userData.survey_instance_id;
      if (typeof id!=="string") return;
      if (/^P507-(LIGHT|FAN|AC|PROJECTOR|CAMERA)-/.test(id) && effectiveVisible(node)) {
        ceilingEnabled.add(id);
        const p=node.getWorldPosition(new Vector3()).project(camera);
        if (Math.abs(p.x)<=1 && Math.abs(p.y)<=1 && p.z>=-1 && p.z<=1) ceilingInFrustum.add(id);
      }
      if (/^P507-(DESK|CHAIR|CABINET|WATER|TV|UTILITY|FRIDGE|SHOE|WASTE|WHITEBOARD|DISPLAY)/.test(id) && !effectiveVisible(node)) hiddenFurniture.add(id);
    });
    return { enabledCeilingIds:[...ceilingEnabled].sort(), ceilingOriginsInCameraFrustum:[...ceilingInFrustum].sort(), hiddenFurnitureIds:[...hiddenFurniture].sort() };
  };
  const snapshot = () => ({
    camera: current, cameraHeightM: camera.position.y, verticalFovDegrees: camera.fov,
    cameraPositionGltf: camera.position.toArray(), cameraTargetGltf: controls.target.toArray(),
    method: "16 source images/sketches opened and compared locally; proposed cameras, no calibrated 1:1 match claim",
    sourceReference: presets[current].source, cameraConfidence: presets[current].confidence,
    lightingMethod: "Four east windows/daylight; 8 modelled emissive diffusers, 2 area strips approximate aggregate ceiling fill; procedural IBL",
    transmissionResolutionScale: gl.transmissionResolutionScale, renderPaused: paused,
    firstFrameCompletedMs,
    architecturalCutaway: presets[current].cutaway,
    visibility: visibilityEvidence(),
    roomDimensions,surveyBaseline,approvedLayoutTotal,wallBaseColorSrgb,wallMaterialUses,chairBackCenters,fileGlassBays,fileGlassAlpha,
    doorPose: current==="door_closed" ? "CLOSED_DEMONSTRATION" : "OUTWARD",
    currentDoorBounds: Object.fromEntries(doorRoots.map(({node})=>{const b=new Box3().setFromObject(node);return [node.userData.survey_instance_id,[...b.min.toArray(),...b.max.toArray()]];})),
    viewport: { width: innerWidth, height: innerHeight, dpr: gl.getPixelRatio() },
    glbBytes: bytes.byteLength, meshCount, geometryCount: geometries.size, triangleCount,
    materialCount: materials.size, textureCount: textures.size, textureMemoryEstimateBytes: Math.round(textureMemoryBytes),
    textureEstimateMethod: "RGBA8 width*height, 4/3 mip overhead; excludes renderer environment/shadow buffers",
    rendererTextures: gl.info.memory.textures, loadTimeMs,
    drawCalls: gl.info.render.calls, trianglesPerFrame: gl.info.render.triangles,
    frameTimeMs: { sampleCount: frameTimes.length, p50: quantile(frameTimes, .5), p95: quantile(frameTimes, .95),
      min: frameTimes.length ? Math.min(...frameTimes) : 0, max: frameTimes.length ? Math.max(...frameTimes) : 0, raw: [...frameTimes] },
    sampling: "All rAF intervals after camera selection; no slow frame rejection; last 600 samples; paused only after measurement for screenshot capture",
    gpu: debug ? context.getParameter(debug.UNMASKED_RENDERER_WEBGL) : context.getParameter(context.RENDERER),
    vendor: debug ? context.getParameter(debug.UNMASKED_VENDOR_WEBGL) : context.getParameter(context.VENDOR),
    userAgent: navigator.userAgent, ids: [...ids].sort(), placedChairIds, unplacedIds, unplacedReasons, inventoryTotal, objectBounds, windowCenters, blindNames: [...blindNames], componentBounds, assetMetadata
  });
  window.__P507_REVIEW__ = { aim, snapshot, pause: () => { paused = true; } };
  function render(now: number) {
    if (stopped) return;
    if (paused) { requestAnimationFrame(render); return; }
    // Establish the first rAF timestamp; never subtract a newer performance.now().
    if (prior !== null) frameTimes.push(now - prior);
    prior = now;
    if (frameTimes.length > 600) frameTimes.shift();
    controls.update(); gl.render(scene, camera); frames++;
    if (firstFrameCompletedMs === null) firstFrameCompletedMs = performance.now() - loadStart;
    if (now - lastReport > 1500 && stats) {
      stats.textContent = `draw calls: ${gl.info.render.calls} · triangles/frame: ${gl.info.render.triangles}\nframe-time p50/p95: ${quantile(frameTimes, .5).toFixed(1)} / ${quantile(frameTimes, .95).toFixed(1)} ms · n=${frameTimes.length}\n${innerWidth}×${innerHeight} · DPR ${gl.getPixelRatio()} · frames ${frames}\nSoftware/viewport smoke ≠ physical-device KPI.`;
      lastReport = now;
    }
    requestAnimationFrame(render);
  }
  requestAnimationFrame(render);
  const resize = () => { camera.aspect = innerWidth / innerHeight; camera.updateProjectionMatrix(); gl.setSize(innerWidth, innerHeight); };
  window.addEventListener("resize", resize);
  window.addEventListener("pagehide", () => {
    stopped = true; window.removeEventListener("resize", resize); controls.dispose(); environmentTarget.dispose(); gl.dispose();
  }, { once: true });
}
