/** Development-only P507 review. No production scene or automatic XR access. */
import {
  ACESFilmicToneMapping, AmbientLight, Box3, Color, DirectionalLight, HemisphereLight,
  Material, Mesh, MeshStandardMaterial, Object3D, PCFSoftShadowMap, PerspectiveCamera, PMREMGenerator,
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
type ReviewAPI = { aim: (key: string) => void; snapshot: () => Record<string, unknown> };
declare global { interface Window { __P507_REVIEW__?: ReviewAPI } }

if (!import.meta.env.DEV) show("BẢN PREVIEW CHỈ HỖ TRỢ VITE DEV, KHÔNG ĐƯỢC DEPLOY.");
else if (!canvas || !window.WebGL2RenderingContext) show("WebGL2 không khả dụng. Không thể xem preview.");
else run(canvas).catch(error => show("Không thể mở cảnh 3D: " + String(error)));

async function run(element: HTMLCanvasElement) {
  const gl = new WebGLRenderer({ canvas: element, antialias: true, powerPreference: "high-performance" });
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
  scene.environmentIntensity = .45;
  environment.dispose(); pmrem.dispose();
  scene.add(new AmbientLight(0xffffff, .12));
  scene.add(new HemisphereLight(0xe4efff, 0xc1b7a2, .55));
  const sun = new DirectionalLight(0xfff4e3, 2);
  // Source is just inside east glazing; window placeholders cannot block daylight.
  sun.position.set(5.7, 3.1, -4.4);
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
  for (const x of [1.52, 4.48]) for (const y of [1, 3, 5.05, 7]) {
    const panel = new RectAreaLight(0xfff4df, 2.6, .6, .6);
    panel.position.set(x, 3.39, -y); panel.lookAt(x, 0, -y); scene.add(panel);
  }
  const camera = new PerspectiveCamera(58, window.innerWidth / window.innerHeight, .04, 60);
  const controls = new OrbitControls(camera, element);
  controls.enableDamping = true;
  controls.minDistance = .3; controls.maxDistance = 22;
  controls.maxPolarAngle = Math.PI * .98;
  // Survey XYZ -> glTF (x,z,-y); exporter already performs this conversion.
  const presets = {
    hero: { pos: [1.10, 1.65, -4.8], target: [.95, 1.35, -7.95], fov: 64, cutaway: false },
    wide: { pos: [.72, 1.68, -4.7], target: [3.15, 1.05, -7.45], fov: 74, cutaway: false },
    overview: { pos: [3, 10.7, -4.05], target: [3, 0, -4.051], fov: 52, cutaway: true },
    clusters: { pos: [7.9, 7.3, -4.2], target: [3, .35, -2.8], fov: 53, cutaway: true },
    logo: { pos: [2.8, 1.65, -5.7], target: [3, 1.3, -.08], fov: 62, cutaway: false }
  };
  type Preset = keyof typeof presets;
  let current: Preset = "hero";
  const overheadNodes: Object3D[] = [], eastWalls: Object3D[] = [];
  const frameTimes: number[] = [];
  function aim(key: string) {
    if (!(key in presets)) throw new Error("Unknown review camera: " + key);
    current = key as Preset;
    gl.shadowMap.needsUpdate = true;
    const preset = presets[current];
    overheadNodes.forEach(node => { node.visible = !preset.cutaway; });
    // Explicit architectural cutaway only. All furniture stays visible in every shot.
    eastWalls.forEach(node => { node.visible = current !== "clusters"; });
    camera.position.fromArray(preset.pos); controls.target.fromArray(preset.target);
    camera.fov = current === "hero" && camera.aspect < .8 ? 68 : preset.fov;
    if (current === "overview") camera.position.y = Math.max(camera.position.y, 3.35 / (Math.tan(camera.fov * Math.PI / 360) * camera.aspect)); camera.updateProjectionMatrix(); controls.update();
    frameTimes.length = 0;
    const note = document.querySelector("#camera-note");
    if (note) note.textContent = preset.cutaway ? "CUTAWAY: chỉ ẩn trần/tường ngoài để kiểm tra; giữ toàn bộ nội thất." : "Góc phối cảnh đề xuất; PHOTO_MATCH BLOCKED.";
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
  let inventoryTotal = 36;
  let unplacedIds: string[] = [];
  loaded.traverse(node => {
    if (typeof node.userData.chair_inventory_count === "number") inventoryTotal = node.userData.chair_inventory_count;
    if (Array.isArray(node.userData.unplaced_chair_ids)) unplacedIds = node.userData.unplaced_chair_ids;
    else if (typeof node.userData.unplaced_chair_ids === "string") unplacedIds = JSON.parse(node.userData.unplaced_chair_ids);
    if (typeof node.userData.survey_instance_id === "string") ids.add(node.userData.survey_instance_id);
    else if (typeof node.userData.unplaced_chair_ids === "string") unplacedIds = JSON.parse(node.userData.unplaced_chair_ids);
    const mesh = node as Mesh;
    if (!mesh.isMesh) return;
    meshCount++; mesh.castShadow = true; mesh.receiveShadow = true;
    if (mesh.name.includes("WINDOW_GLASS")) mesh.castShadow = false;
    geometries.add(mesh.geometry);
    triangleCount += Math.floor((mesh.geometry.index?.count ?? mesh.geometry.attributes.position?.count ?? 0) / 3);
    for (const mat of Array.isArray(mesh.material) ? mesh.material : [mesh.material]) {
      materials.add(mat);
      if (mat instanceof MeshStandardMaterial && mat.name.includes("OFF_SCREEN")) mat.envMapIntensity = .12;
      if (mat instanceof MeshStandardMaterial && mat.name.includes("TV_BEZEL")) mat.envMapIntensity = .35;
      for (const value of Object.values(mat)) if (value instanceof Texture) textures.add(value);
    }
    const id = mesh.userData.survey_instance_id;
    if (typeof id === "string") ids.add(id);
    if (node.name.startsWith("P507_ARCH_CEILING") || node.name.startsWith("P507_CEILING")) overheadNodes.push(node);
    if (/P507_ARCH_(WALL_EAST|EAST_|WINDOW_|ROLLER_|BLIND_|BASEBOARD_EAST)/.test(node.name)) eastWalls.push(node);
  });
  loaded.updateMatrixWorld(true);
  loaded.traverse(node => { if (node.name.startsWith("P507_ARCH_WINDOW_GLASS")) windowCenters.push(node.getWorldPosition(new Vector3()).toArray()); });
  for (const id of ids) {
    const bounds = new Box3();
    loaded.traverse(node => { if (node.userData.survey_instance_id === id) bounds.union(new Box3().setFromObject(node)); });
    objectBounds[id] = [...bounds.min.toArray(), ...bounds.max.toArray()];
  }
  const placedChairIds = [...ids].filter(id => id.startsWith("P507-CHAIR-"));
  scene.add(loaded); aim("hero");
  show(`GLB PROVISIONAL đã tải: ${meshCount} meshes, ${triangleCount} triangles. Ghế đã đặt ${placedChairIds.length}/${inventoryTotal}; UNPLACED ${inventoryTotal - placedChairIds.length}. Cần chủ dự án duyệt hình.`);
  const unplaced = document.querySelector("#unplaced");
  if (unplaced) unplaced.textContent = unplacedIds.length ? "Chưa đặt: " + unplacedIds.join(", ") : `Inventory ${inventoryTotal}; số ghế chưa đặt ${inventoryTotal - placedChairIds.length}. Vị trí vẫn provisional.`;
  const quantile = (a: number[], q: number) => a.slice().sort((x, y) => x - y)[Math.max(0, Math.ceil(q * a.length) - 1)] ?? 0;
  const context = gl.getContext();
  const debug = context.getExtension("WEBGL_debug_renderer_info");
  const textureMemoryBytes = [...textures].reduce((sum, tex) => {
    const image = tex.image as { width?: number; height?: number } | undefined;
    return sum + (image?.width ?? 0) * (image?.height ?? 0) * 4 * (tex.generateMipmaps ? 4 / 3 : 1);
  }, 0);
  let stopped = false, prior = performance.now(), frames = 0, lastReport = prior;
  const snapshot = () => ({
    camera: current, cameraHeightM: camera.position.y, verticalFovDegrees: camera.fov,
    cameraPositionGltf: camera.position.toArray(), cameraTargetGltf: controls.target.toArray(),
    method: "Proposed geometric framing, no reference photo available; no 1:1 match claim",
    architecturalCutaway: presets[current].cutaway,
    viewport: { width: innerWidth, height: innerHeight, dpr: gl.getPixelRatio() },
    glbBytes: bytes.byteLength, meshCount, geometryCount: geometries.size, triangleCount,
    materialCount: materials.size, textureCount: textures.size, textureMemoryEstimateBytes: Math.round(textureMemoryBytes),
    textureEstimateMethod: "RGBA8 width*height, 4/3 mip overhead; excludes renderer environment/shadow buffers",
    rendererTextures: gl.info.memory.textures, loadTimeMs,
    drawCalls: gl.info.render.calls, trianglesPerFrame: gl.info.render.triangles,
    frameTimeMs: { sampleCount: frameTimes.length, p50: quantile(frameTimes, .5), p95: quantile(frameTimes, .95),
      min: frameTimes.length ? Math.min(...frameTimes) : 0, max: frameTimes.length ? Math.max(...frameTimes) : 0, raw: [...frameTimes] },
    sampling: "All rAF intervals after camera selection; no slow frame rejection; last 600 samples",
    gpu: debug ? context.getParameter(debug.UNMASKED_RENDERER_WEBGL) : context.getParameter(context.RENDERER),
    vendor: debug ? context.getParameter(debug.UNMASKED_VENDOR_WEBGL) : context.getParameter(context.VENDOR),
    userAgent: navigator.userAgent, ids: [...ids].sort(), placedChairIds, unplacedIds, inventoryTotal, objectBounds, windowCenters
  });
  window.__P507_REVIEW__ = { aim, snapshot };
  function render(now: number) {
    if (stopped) return;
    frameTimes.push(now - prior); prior = now;
    if (frameTimes.length > 600) frameTimes.shift();
    controls.update(); gl.render(scene, camera); frames++;
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
