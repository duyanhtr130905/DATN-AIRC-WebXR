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
  assert(ids.filter(id => id.startsWith("P507-DESK-")).length === 17, "Expected actual 17 desks in GLB");
  for (const group of ["B", "C"]) for (const expected of inventory.chairs.instances.filter(c => c.cluster === group && c.placement_role === "right_end")) {
    const chair = bounds[expected.id];
    const desk = bounds[`P507-DESK-${group}05`];
    assert(chair && desk && chair[0] >= desk[3] - .005, `${expected.id} chair is not on right of longitudinal desk`);
  }
  const cabinet = bounds["P507-CABINET-LOW"];
  const water = bounds["P507-WATER-DISPENSER"];
  assert(cabinet && water, "Hero asset IDs missing from actual GLB");
  for (const id of ids.filter(id => /P507-(DESK|CHAIR|CABINET|WATER)/.test(id))) {
    const b = bounds[id];
    assert(b[0] >= -.001 && b[3] <= 6.001 && b[2] >= -8.101 && b[5] <= .001 && b[1] >= -.005,
      `Actual GLB furniture exceeds room or floor: ${id} ${b}`);
    if (!id.startsWith("P507-CHAIR-")) continue;
    const overlap = Math.max(0, Math.min(b[3], cabinet[3]) - Math.max(b[0], cabinet[0])) *
      Math.max(0, Math.min(b[5], cabinet[5]) - Math.max(b[2], cabinet[2]));
    assert(overlap < .000001, "Actual GLB cabinet-chair overlap: " + id);
  }
  // North TV is at negative glTF Z; four east windows must remain near X=6.
  assert(bounds["P507-TV-LARGE"]?.[2] < -7.8, "TV/wall orientation is incorrect");
  assert(metrics.windowCenters.length === 4 && metrics.windowCenters.every(p => p[0] > 5.9 && p[2] < 0), "Four windows must be on east wall after axis conversion");
  return { actualDeskCount: 17, cabinetChairOverlaps: 0, roomFurnitureBounds: "PASS", rightChairSide: "PASS" };
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
      const shots = process.env.P507_SHOTS ? process.env.P507_SHOTS.split(",").filter(Boolean) : label === "desktop" ? ["hero", "wide", "overview", "clusters"] : ["hero"];
      for (const shot of shots) {
        await page.evaluate(key => window.__P507_REVIEW__.aim(key), shot);
        await page.waitForFunction(() => window.__P507_REVIEW__.snapshot().frameTimeMs.sampleCount >= 8, null, { timeout: 180000 });
        const metrics = await page.evaluate(() => window.__P507_REVIEW__.snapshot());
        assert(metrics.drawCalls > 30 && metrics.trianglesPerFrame > 1000, "View has no meaningful visible geometry: " + shot);
        assert(metrics.frameTimeMs.sampleCount >= 8, "Insufficient real frame samples");
        const geometry = baselineCapture ? { result: "BASELINE_ONLY", notice: "Historical layout known to overlap; new geometry acceptance guards intentionally not applied to baseline evidence." } : inspectGeometry(metrics);
        const image = await screenshot(page, `${shot}-${label}.png`);
        console.log("Captured", label, shot, "samples", metrics.frameTimeMs.sampleCount, "p95_ms", metrics.frameTimeMs.p95);
        evidence.push({ viewport: label, shot, image, status: text, metrics, geometry, errors: [...errors] });
      }
      // Retain a UI-visible inventory screenshot to prove UNPLACED count disclosure.
      await page.evaluate(() => { window.__P507_REVIEW__.aim("hero"); document.querySelector("details").open = true; });
      await page.screenshot({ path: path.join(out, `inventory-${label}.png`) });
      assert(errors.length === 0, "Browser console/page errors: " + errors.join(" | "));
      await context.close();
    }
    const report = {
      source: "Chrome ANGLE SwiftShader software WebGL; desktop/mobile viewport emulation",
      historicalBaselineCapture: baselineCapture,
      checkoutHeadSha: execFileSync("git", ["rev-parse", "HEAD"], { cwd: root, encoding: "utf8" }).trim(),
      ciHeadSha: process.env.GITHUB_HEAD_SHA || null,
      ciCheckoutSha: process.env.GITHUB_SHA || null,
      ciRunId: process.env.GITHUB_RUN_ID || null,
      browser: browser.version(), glbSha256: createHash("sha256").update(modelBytes).digest("hex"),
      glbBytes: modelBytes.length, capturedAtUtc: new Date().toISOString(),
      notice: "PROVISIONAL. Not physical device FPS, owner art approval, AIRC photo matching or real source-to-render evidence.", evidence
    };
    await fs.writeFile(path.join(out, "browser-report.json"), JSON.stringify(report, null, 2), "utf8");
    console.log(JSON.stringify({ views: evidence.length, glbBytes: modelBytes.length, checkoutHeadSha: report.checkoutHeadSha,
      evidence: evidence.map(e => ({ shot: e.shot, viewport: e.viewport, calls: e.metrics.drawCalls,
        frameTimeMs: e.metrics.frameTimeMs, geometry: e.geometry })) }, null, 2));
  } finally { if (browser) await browser.close(); vite.kill("SIGTERM"); }
}
main().catch(error => { console.error(error); process.exitCode = 1; });
