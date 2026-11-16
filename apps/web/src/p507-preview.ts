/** Development-only P507 GLB lookdev viewer.
 * Requires a local, ignored Blender GLB. Not linked from official App.
 */
import {
  ACESFilmicToneMapping, AmbientLight, Box3, Color, DirectionalLight,
  HemisphereLight, Mesh, Object3D, PerspectiveCamera, Scene, SRGBColorSpace,
  Vector3, WebGLRenderer
} from "three";
import { GLTFLoader } from "three/examples/jsm/loaders/GLTFLoader.js";
import { OrbitControls } from "three/examples/jsm/controls/OrbitControls.js";

const canvas = document.querySelector<HTMLCanvasElement>("#view");
const status = document.querySelector<HTMLElement>("#status");
const stats = document.querySelector<HTMLElement>("#stats");

function show(message: string) { if (status) status.textContent = message; }

if (!import.meta.env.DEV) {
  show("BẢN PREVIEW CHỈ HỖ TRỢ VITE DEV, KHÔNG ĐƯỢC DEPLOY.");
} else if (!canvas || !window.WebGL2RenderingContext) {
  show("WebGL2 không khả dụng. Không thể xem preview trên thiết bị này.");
} else {
  run(canvas).catch(error => show("Không thể mở cảnh 3D: " + String(error)));
}

async function run(element: HTMLCanvasElement) {
  const gl = new WebGLRenderer({ canvas: element, antialias: true, powerPreference: "high-performance" });
  gl.setPixelRatio(Math.min(window.devicePixelRatio, 1.5));
  gl.setSize(window.innerWidth, window.innerHeight);
  gl.outputColorSpace = SRGBColorSpace;
  gl.toneMapping = ACESFilmicToneMapping;
  gl.toneMappingExposure = 1.25;
  gl.shadowMap.enabled = true;
  const scene = new Scene();
  scene.background = new Color("#d2d5d2");
  const camera = new PerspectiveCamera(56, window.innerWidth / window.innerHeight, .05, 100);
  const controls = new OrbitControls(camera, element);
  controls.enableDamping = true;
  controls.minDistance = 1.2; controls.maxDistance = 30;
  controls.maxPolarAngle = Math.PI * .98;
  scene.add(new AmbientLight(0xffffff, .45));
  scene.add(new HemisphereLight(0xf0f8ff, 0xc4c0b6, 1.55));
  const sun = new DirectionalLight(0xfff2e4, 2.7);
  sun.position.set(9, 9, -3); sun.castShadow = true;
  sun.shadow.mapSize.set(1024, 1024);
  sun.shadow.camera.near = .3; sun.shadow.camera.far = 30;
  sun.shadow.camera.left = -12; sun.shadow.camera.right = 12;
  sun.shadow.camera.top = 12; sun.shadow.camera.bottom = -12;
  scene.add(sun);
  // Blender glTF exporter does Z-up -> glTF Y-up. Never apply it twice.
  const presets = {
    overview: { pos: new Vector3(9, 6.6, 4), target: new Vector3(3, 1.2, -4) },
    hero: { pos: new Vector3(3.5, 2.1, -3.2), target: new Vector3(1.3, 1.65, -7.75) },
    logo: { pos: new Vector3(3, 2, -6.9), target: new Vector3(3, 1.7, -.08) }
  };
  function aim(key: keyof typeof presets) {
    camera.position.copy(presets[key].pos);
    controls.target.copy(presets[key].target);
    controls.update();
  }
  aim("hero");
  for (const key of ["overview", "hero", "logo"] as const) {
    document.getElementById(key)?.addEventListener("click", () => aim(key));
  }
  const assetUrl = "/p507-local-preview/P507_G1_G2_PROVISIONAL.glb";
  let loaded: Object3D;
  try {
    const gltf = await new GLTFLoader().loadAsync(assetUrl);
    loaded = gltf.scene;
  } catch (error) {
    gl.dispose(); controls.dispose();
    show("Chưa có GLB local. Chạy Blender generator rồi chép file vào apps/web/public/p507-local-preview/ (gitignored).");
    if (stats) stats.textContent = String(error);
    return;
  }
  const world = new Box3().setFromObject(loaded);
  if (world.isEmpty()) throw new Error("GLB contains no visible geometry");
  let meshCount = 0; let triangleCount = 0;
  const ids = new Set<string>();
  loaded.traverse(node => {
    const mesh = node as Mesh;
    if (!mesh.isMesh) return;
    meshCount++; mesh.castShadow = true; mesh.receiveShadow = true;
    if (mesh.geometry.index) triangleCount += Math.floor(mesh.geometry.index.count / 3);
    else if (mesh.geometry.attributes.position) triangleCount += Math.floor(mesh.geometry.attributes.position.count / 3);
    if (typeof mesh.userData.survey_instance_id === "string") ids.add(mesh.userData.survey_instance_id);
  });
  scene.add(loaded);
  show("GLB PROVISIONAL đã tải: " + meshCount + " meshes, " + triangleCount + " triangles, " + ids.size + " survey IDs. Cần chủ dự án duyệt góc HERO.");
  const frameTimes: number[] = [];
  let prior = performance.now(); let stopped = false; let frames = 0; let lastReport = prior;
  const quantile = (a: number[], q: number) =>
    a.slice().sort((x,y) => x-y)[Math.min(a.length-1, Math.ceil(q*a.length)-1)] ?? 0;
  const render = (now: number) => {
    if (stopped) return;
    const elapsed = now-prior; prior=now;
    if (elapsed < 500) { frameTimes.push(elapsed); if (frameTimes.length > 300) frameTimes.shift(); }
    controls.update(); gl.render(scene, camera); frames++;
    if (now-lastReport > 1500 && stats) {
      const p50=quantile(frameTimes,.5),p95=quantile(frameTimes,.95);
      stats.textContent = "draw calls: " + gl.info.render.calls
        + "\ntriangles/frame: " + gl.info.render.triangles
        + "\nframe-time p50/p95: " + p50.toFixed(1) + " / " + p95.toFixed(1) + " ms"
        + "\nviewport: " + window.innerWidth + "×" + window.innerHeight
        + "\nDPR " + gl.getPixelRatio() + "\nframes: " + frames
        + "\nNOT physical-device KPI evidence.";
      lastReport=now;
    }
    requestAnimationFrame(render);
  };
  requestAnimationFrame(render);
  const resize = () => {
    camera.aspect=window.innerWidth/window.innerHeight; camera.updateProjectionMatrix();
    gl.setSize(window.innerWidth,window.innerHeight);
  };
  window.addEventListener("resize",resize);
  window.addEventListener("pagehide",()=>{
    stopped=true; window.removeEventListener("resize",resize); controls.dispose(); gl.dispose();
  },{once:true});
}
