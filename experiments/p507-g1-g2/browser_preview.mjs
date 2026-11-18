/** Real Chrome screenshots and raw software-WebGL evidence for the actual generated GLB. */
import { spawn, execFileSync } from "node:child_process";
import { createHash } from "node:crypto";
import fs from "node:fs/promises";
import { createRequire } from "node:module";
import path from "node:path";
import { fileURLToPath } from "node:url";

const directory = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(directory, "../..");
const web = path.join(root, "apps", "web");
const out = process.env.P507_EVIDENCE_DIR || path.join(root, ".local", "p507-g1-g2");
const baselineCapture = process.env.P507_BASELINE === "1";
const require = createRequire(path.join(web, "package.json"));
const { chromium } = require("playwright");
const port = 5178;
const url = `http://127.0.0.1:${port}/p507-g1-g2-preview.html`;
const model = path.join(web, "public", "p507-local-preview", "P507_G1_G2_PROVISIONAL.glb");
const referenceManifest = JSON.parse(await fs.readFile(path.join(directory, "reference-manifest.json"), "utf8"));
const inventory = JSON.parse(await fs.readFile(path.join(directory, "p507-provisional.json"), "utf8"));
const assert = (value, message) => { if (!value) throw new Error(message); };
async function waitServer(proc) {
  for (let i = 0; i < 75; i++) {
    if (proc.exitCode !== null) throw new Error("Vite terminated: " + proc.exitCode);
    try { if ((await fetch(url, { signal: AbortSignal.timeout(1000) })).ok) return; } catch {}
    await new Promise(resolve => setTimeout(resolve, 200));
  }
  throw new Error("Timed out waiting for local Vite preview");
}
function inspectGeometry(metrics) {
  const bounds = metrics.objectBounds;
  const ids = Object.keys(bounds);
  const expectedChairs = inventory.chairs.instances.filter(c => c.status === "PLACED_PROVISIONAL");
  const unplaced = inventory.chairs.instances.filter(c => c.status === "UNPLACED");
  assert(ids.filter(id => id.startsWith("P507-DESK-")).length === 17, "Expected 17 actual desks in GLB");
  assert(metrics.placedChairIds.length === expectedChairs.length, "GLB chair count differs from explicit placed inventory");
  assert(metrics.unplacedIds.length === unplaced.length && metrics.inventoryTotal === inventory.chairs.count, "UNPLACED disclosure differs from inventory");
  const expected = [
    ...inventory.objects.filter(o => o.status !== "UNPLACED"),
    ...Object.values(inventory.hero), ...expectedChairs,
    ...inventory.ceiling.instances, ...inventory.photo_wall.frames,
    ...inventory.openings.windows.flatMap(w => [w, w.blind]), ...inventory.openings.door.leaves
  ];
  for (const item of expected) assert(bounds[item.id], "Missing authored GLB object: " + item.id);
  for (const chair of unplaced) assert(!bounds[chair.id], "UNPLACED chair unexpectedly rendered: " + chair.id);
  for (const group of ["B", "C"]) {
    const right = expectedChairs.filter(c => c.cluster === group && c.placement_role === "right_end");
    assert(right.length === 2, "Exactly two right chairs required for " + group);
    for (const expected of right) {
      const chair = bounds[expected.id], desk = bounds[`P507-DESK-${group}05`];
      assert(chair[0] >= desk[3] - .003, "Actual right chair penetrates longitudinal desk: " + expected.id);
    }
  }
  for (const [id,b] of Object.entries(bounds)) {
    if (!expected.some(o => o.id === id)) continue;
    assert(b.every(Number.isFinite), "Nonfinite actual GLB bounds: " + id);
    const leaf = inventory.openings.door.leaves.find(o=>o.id===id);
    const exteriorLeaf = leaf?.swing === "OUTWARD" && inventory.openings.door.swing === "OUTWARD";
    const width=inventory.room.width_x,length=inventory.room.length_y,height=inventory.room.height_z;
    assert(b[0] >= (exteriorLeaf ? -.853 : -.003) && b[3] <= (exteriorLeaf ? .003 : width+.003) && b[2] >= -(exteriorLeaf ? inventory.openings.door.to_y+.04 : length+.003) && b[5] <= (exteriorLeaf ? -inventory.openings.door.from_y+.04 : .003) && b[1] >= -.005 && b[4] <= height+.005,
      `Actual authored geometry outside room: ${id} ${b}`);
  }
  assert(metrics.visibility.hiddenFurnitureIds.length===0, "Furniture hidden by review camera: "+metrics.visibility.hiddenFurnitureIds);
  if(metrics.architecturalCutaway) assert(metrics.visibility.enabledCeilingIds.length===0, "Ceiling device group not hidden in cutaway");
  else assert(metrics.visibility.enabledCeilingIds.length===inventory.ceiling.instances.length, "Ceiling unexpectedly hidden outside cutaway");
  assert(metrics.approvedLayoutTotal===inventory.chairs.approved_layout_count && expectedChairs.length===34 && ["P507-CHAIR-C-09","P507-CHAIR-C-10"].every(id=>unplaced.some(c=>c.id===id)),"Owner layout must place 34 of 36 historical chairs");
  assert(metrics.roomDimensions.width_x===6.9 && metrics.roomDimensions.length_y===9.315 && metrics.surveyBaseline.width_x===6 && metrics.surveyBaseline.length_y===8.1,"Virtual/survey dimensions confused in exported metadata");
  assert(metrics.wallBaseColorSrgb==="#F5E6C8" && metrics.wallMaterialUses>=4,"Vanilla wall material absent or inconsistent in actual GLB");
  assert(Object.keys(metrics.fileGlassBays).length===3 && metrics.fileGlassAlpha>.05 && metrics.fileGlassAlpha<.4,"Actual three clear glass cabinet panes missing");
  const shelf= bounds['P507-UTILITY-SHELF'],smallTv=bounds['P507-TV-SMALL'];
  assert(shelf[5]-shelf[2]>1.45 && shelf[3]-shelf[0]<.49,"Actual shelf was not widened along wall");
  assert(smallTv[1]>=shelf[4]-.005 && smallTv[0]>=shelf[0]-.005 && smallTv[3]<=shelf[3]+.005 && smallTv[2]>=shelf[2]-.005 && smallTv[5]<=shelf[5]+.005,"Small TV loses shelf support");
  for(const chair of expectedChairs){
    const back=metrics.chairBackCenters[chair.id];assert(back,"Actual chair back not found: "+chair.id);
    const a=chair.orientation_deg*Math.PI/180,dx=back[0]-chair.center[0],dz=back[2]+chair.center[1];
    assert(dx*Math.sin(a)+dz*Math.cos(a)>.06 && Math.abs(dx*Math.cos(a)-dz*Math.sin(a))<.10,"Actual chair back orientation differs from sitting direction: "+chair.id);
  }
  const currentLeaves=Object.values(metrics.currentDoorBounds);
  assert(currentLeaves.length===2,"Exported hinge/leaf metadata missing");
  if(metrics.doorPose==='OUTWARD')assert(currentLeaves.every(b=>b[3]<=.003 && b[0]<-.5),"Actual outward leaf remains inside room");
  else assert(currentLeaves.every(b=>b[0]>-.10 && b[3]<.003),"Closed demonstration is not rigid hinge closure");
  const cabinet = bounds["P507-CABINET-LOW"];
  for (const expected of expectedChairs) {
    const b = bounds[expected.id];
    const area = Math.max(0, Math.min(b[3], cabinet[3]) - Math.max(b[0], cabinet[0])) *
      Math.max(0, Math.min(b[5], cabinet[5]) - Math.max(b[2], cabinet[2]));
    assert(area < .000001, "Actual cabinet-chair overlap: " + expected.id);
  }
  assert(metrics.windowCenters.length === 4 && metrics.windowCenters.every(p => Math.abs(p[0]-inventory.room.width_x)<.10 && p[2] < 0), "Four windows must remain on east wall");
  for (const prefix of ["P507-LIGHT-", "P507-FAN-", "P507-AC-", "P507-PROJECTOR-", "P507-CAMERA-"]) {
    const desired = inventory.ceiling.instances.filter(o => o.id.startsWith(prefix));
    assert(ids.filter(id => id.startsWith(prefix)).length === desired.length, "Actual ceiling device count: " + prefix);
  }
  assert(ids.filter(id => id.startsWith("P507-FRAME-")).length === 27, "Expected 27 independent observed-layout frame placeholders");
  const components = Object.entries(metrics.componentBounds);
  const center = b => [(b[0]+b[3])/2,(b[1]+b[4])/2,(b[2]+b[5])/2];
  const control = components.find(([name]) => name.includes("WATER_CONTROL"));
  const body = components.find(([name]) => (name.includes("WATER_BODY") || name.includes("WATER_GRAY_ENCLOSURE")));
  const screen = components.find(([name]) => name.includes("TV_BLACK_SCREEN"));
  assert(control && body && screen, "Required real mesh components for rotation evidence missing");
  const delta = center(control[1]).map((v,i) => v-center(body[1])[i]);
  assert(delta[0] > .12 && Math.abs(delta[2]) < .06, "Water front mesh was not actually rotated to +X");
  const s=screen[1], screenAngle = Math.atan2(s[5]-s[2],s[3]-s[0])*180/Math.PI;
  assert(screenAngle > 18 && screenAngle < 32, "TV screen geometry is not diagonally mounted: " + screenAngle);
  return { actualDeskCount:17, actualPlacedChairs:expectedChairs.length, unplacedChairs:unplaced.length,
    cabinetChairOverlaps:0, roomFurnitureBounds:"PASS", rightChairSide:"PASS", actualWaterFrontDeltaGltf:delta,
    actualTvScreenAabbAngleDegrees:screenAngle, ceilingDeviceCount:inventory.ceiling.instances.length,
    frameCount:27, windowCount:4, blindCount:4, notice:"Bounds/component checks complement Blender oriented vertex validation; not visual approval or circulation certification." };
}

async function screenshot(page, filename) {
  await page.evaluate(() => { document.querySelector(".panel").style.visibility = "hidden"; });
  const pixels = await page.screenshot({ path: path.join(out, filename) });
  await page.evaluate(() => { document.querySelector(".panel").style.visibility = "visible"; });
  assert(pixels.length > 10000, "Screenshot unexpectedly empty: " + filename);
  return { filename, pngBytes: pixels.length, notice: "Actual image requires manual visual inspection; render-call guard is not art acceptance." };
}
async function main() {
  const modelBytes = await fs.readFile(model);
  await fs.mkdir(out, { recursive: true });
  const vite = spawn(process.execPath, [path.join(web, "node_modules", "vite", "bin", "vite.js"),
    "--host", "127.0.0.1", "--port", String(port), "--strictPort"],
  { cwd: web, env: { ...process.env, API_PROXY_TARGET: "http://127.0.0.1:1" }, stdio: "pipe" });
  let browser;
  try {
    await waitServer(vite);
    browser = await chromium.launch({ headless: true,
      executablePath: process.env.CHROME_BIN || (process.platform === "win32" ? "C:/Program Files/Google/Chrome/Application/chrome.exe" : "/usr/bin/google-chrome"),
      args: ["--no-sandbox", "--use-gl=angle", "--use-angle=swiftshader", "--enable-webgl", "--enable-unsafe-swiftshader", "--disable-dev-shm-usage"] });
    const evidence = [];
    for (const [label, size] of [["desktop", { width: 1280, height: 720 }], ["mobile", { width: 390, height: 844 }]]) {
      const context = await browser.newContext({ viewport: size, deviceScaleFactor: 1 });
      const page = await context.newPage();
      page.setDefaultTimeout(180000);
      const errors = [];
      page.on("pageerror", e => errors.push(String(e)));
      page.on("console", message => { if (message.type() === "error") errors.push(message.text()); });
      await page.goto(url, { waitUntil: "domcontentloaded", timeout: 30000 });
      await page.waitForFunction(() => !!window.__P507_REVIEW__ || document.querySelector("#status")?.textContent?.startsWith("Không thể"), null, { timeout: 180000 });
      const text = (await page.locator("#status").innerText()).trim();
      assert(text.startsWith("GLB PROVISIONAL"), "GLB load failed: " + text);
      const shots = process.env.P507_SHOTS ? process.env.P507_SHOTS.split(",").filter(Boolean) : label === "desktop" ? ["overview", "clusters", "cluster_A", "cluster_B", "cluster_C", "door_outward", "door_closed", "tv_corner", "utility", "shelf", "vanilla_wall", "ceiling", "hero", "photo_wall", "logo", "windows"] : ["hero"];
      for (const shot of shots) {
        await page.evaluate(key => window.__P507_REVIEW__.aim(key), shot);
        await page.waitForFunction(() => window.__P507_REVIEW__.snapshot().frameTimeMs.sampleCount >= 12, null, { timeout: 240000 });
        const metrics = await page.evaluate(() => { window.__P507_REVIEW__.pause(); return window.__P507_REVIEW__.snapshot(); });
        assert(metrics.frameTimeMs.raw.length >= 12 && metrics.frameTimeMs.raw.every(value => Number.isFinite(value) && value > 0), "Invalid rAF interval measurement");
        assert(metrics.drawCalls > 0 && metrics.trianglesPerFrame > 100, "View has no meaningful visible geometry: " + shot);
        assert(metrics.frameTimeMs.sampleCount >= 12, "Insufficient real frame samples");
        const geometry = baselineCapture ? { result: "BASELINE_ONLY", notice: "Historical layout known to overlap; new geometry acceptance guards intentionally not applied to baseline evidence." } : inspectGeometry(metrics);
        const image = await screenshot(page, `${shot}-${label}.png`);
        console.log("Captured", label, shot, "samples", metrics.frameTimeMs.sampleCount, "p95_ms", metrics.frameTimeMs.p95);
        evidence.push({ viewport: label, shot, image, status: text, metrics, geometry, errors: [...errors] });
      }
      await fs.writeFile(path.join(out, "browser-progress.json"), JSON.stringify({ status:"CAPTURING", completedViews:evidence.length, evidence },null,2));
      // Retain a UI-visible inventory screenshot to prove UNPLACED count disclosure.
      await page.evaluate(() => { window.__P507_REVIEW__.aim("hero"); document.querySelector("details").open = true; });
      await page.waitForFunction(() => window.__P507_REVIEW__.snapshot().frameTimeMs.sampleCount >= 2, null, { timeout:240000 });
      await page.evaluate(() => window.__P507_REVIEW__.pause());
      await page.screenshot({ path: path.join(out, `inventory-${label}.png`) });
      assert(errors.length === 0, "Browser console/page errors: " + errors.join(" | "));
      await context.close();
    }
    const report = {
      source: "Chrome ANGLE SwiftShader software WebGL; desktop/mobile viewport emulation",
      historicalBaselineCapture: baselineCapture,
      baselineAssetSourceSha: process.env.P507_BASELINE_SHA || null,
      references: { opened:referenceManifest.references.length, sourceIds:referenceManifest.references.map(r=>r.id), photoMatch:"PARTIAL: qualitative source review; cameras estimated" },
      captureMethod:"Continuous full-quality WebGL for measurement; freeze drawing only afterwards to avoid screenshot/automation GPU contention. All measured slow intervals retained.",
      workTreeDirty: execFileSync("git", ["status", "--porcelain"], {cwd:root, encoding:"utf8"}).trim().length > 0,
      checkoutHeadSha: execFileSync("git", ["rev-parse", "HEAD"], { cwd: root, encoding: "utf8" }).trim(),
      ciHeadSha: process.env.GITHUB_HEAD_SHA || null,
      ciCheckoutSha: process.env.GITHUB_SHA || null,
      ciRunId: process.env.GITHUB_RUN_ID || null,
      browser: browser.version(), glbSha256: createHash("sha256").update(modelBytes).digest("hex"),
      glbBytes: modelBytes.length, capturedAtUtc: new Date().toISOString(),
      notice: "PROVISIONAL. Sources inspected locally, cameras estimated; not calibrated photo matching, physical-device FPS, owner art approval or real source-to-render evidence.", evidence
    };
    await fs.writeFile(path.join(out, "browser-report.json"), JSON.stringify(report, null, 2), "utf8");
    if(!baselineCapture){
      const assetPath=path.join(out,'asset-manifest.json');
      const asset=JSON.parse(await fs.readFile(assetPath,'utf8'));
      assert(asset.model_sha256===report.glbSha256,'Browser/asset manifest GLB mismatch');
      asset.preview_camera_presets=evidence.map(e=>({viewport:e.viewport,shot:e.shot,position_gltf:e.metrics.cameraPositionGltf,target_gltf:e.metrics.cameraTargetGltf,fov:e.metrics.verticalFovDegrees,cutaway:e.metrics.architecturalCutaway,doorPose:e.metrics.doorPose}));
      asset.browser_performance_report='browser-report.json';
      asset.renderer_geometry_metrics=Object.fromEntries(['meshCount','geometryCount','triangleCount','materialCount','textureMemoryEstimateBytes'].map(k=>[k,evidence[0].metrics[k]]));
      await fs.writeFile(assetPath,JSON.stringify(asset,null,2)+'\n','utf8');
    }
    const gallery = await browser.newPage({ viewport:{width:1340,height:200},deviceScaleFactor:1 });
    const tiles=[];
    for (const e of evidence) {
      const png=await fs.readFile(path.join(out,e.image.filename));
      tiles.push(`<article><strong>${e.viewport} · ${e.shot}</strong><img src="data:image/png;base64,${png.toString("base64")}"></article>`);
    }
    await gallery.setContent(`<html><head><style>body{margin:24px;background:#eae8df;color:#26383e;font:15px Arial}h1{font-size:22px}main{display:grid;grid-template-columns:repeat(3,1fr);gap:12px}article{background:#fff;padding:10px}strong{display:block;margin-bottom:6px}img{width:100%;height:225px;object-fit:contain;background:#d9dedc}</style></head><body><h1>P507 · actual GLB WebGL review · ${report.ciHeadSha || report.checkoutHeadSha}</h1><p>OWNER-APPROVED VIRTUAL +15% · 34 placed / 36 historical chairs · owner visual approval pending · no survey photographs</p><main>${tiles.join("")}</main></body></html>`);
    await gallery.locator("img").evaluateAll(images=>Promise.all(images.map(img=>img.decode())));
    await gallery.screenshot({path:path.join(out,"contact-sheet.png"),fullPage:true});
    await gallery.close();
    console.log(JSON.stringify({ views: evidence.length, glbBytes: modelBytes.length, checkoutHeadSha: report.checkoutHeadSha,
      evidence: evidence.map(e => ({ shot: e.shot, viewport: e.viewport, calls: e.metrics.drawCalls,
        frameTimeMs: e.metrics.frameTimeMs, geometry: e.geometry })) }, null, 2));
  } finally { if (browser) await browser.close(); vite.kill("SIGTERM"); }
}
main().catch(error => { console.error(error); process.exitCode = 1; });
