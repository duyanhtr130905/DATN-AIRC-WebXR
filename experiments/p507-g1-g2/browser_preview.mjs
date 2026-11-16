/** Verify real dev-only P507 GLB in browser, capture G2 hero screenshots.
 * Run only after Blender exports to ignored apps/web/public/p507-local-preview.
 * No reference photographs or sensitive assets are copied to the CI artifacts.
 */
import { spawn } from "node:child_process";
import fs from "node:fs/promises";
import { createRequire } from "node:module";
import path from "node:path";
import { fileURLToPath } from "node:url";

const directory = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(directory, "../..");
const web = path.join(root, "apps", "web");
const out = path.join(root, ".local", "p507-g1-g2");
const require = createRequire(path.join(web, "package.json"));
const { chromium } = require("playwright");
const port = 5178;
const url = "http://127.0.0.1:" + port + "/p507-g1-g2-preview.html";
const nodeExe = process.execPath;
const viteExe = path.join(web, "node_modules", "vite", "bin", "vite.js");
const model = path.join(web, "public", "p507-local-preview", "P507_G1_G2_PROVISIONAL.glb");

async function waitServer(proc) {
  for (let i = 0; i < 75; i++) {
    if (proc.exitCode !== null) throw new Error("Vite terminated: " + proc.exitCode);
    try {
      const r = await fetch(url, { signal: AbortSignal.timeout(1000) });
      if (r.ok) return;
    } catch {}
    await new Promise(resolve => setTimeout(resolve, 200));
  }
  throw new Error("Timed out waiting for local Vite preview server");
}
async function main() {
  await fs.access(model);
  await fs.mkdir(out, { recursive: true });
  const vite = spawn(nodeExe, [viteExe, "--host", "127.0.0.1", "--port", String(port), "--strictPort"],
    { cwd: web, env: { ...process.env, API_PROXY_TARGET: "http://127.0.0.1:1" }, stdio: "pipe" });
  let browser;
  try {
    await waitServer(vite);
    browser = await chromium.launch({
      headless: true,
      executablePath: process.env.CHROME_BIN || "/usr/bin/google-chrome",
      args: ["--no-sandbox", "--use-gl=angle", "--use-angle=swiftshader", "--enable-webgl", "--enable-unsafe-swiftshader", "--disable-dev-shm-usage"]
    });
    const evidence = [];
    for (const [label, size] of [
      ["desktop", { width: 1280, height: 720 }],
      ["mobile", { width: 390, height: 844 }]
    ]) {
      const context = await browser.newContext({ viewport: size, deviceScaleFactor: 1 });
      const page = await context.newPage();
      const errors = [];
      page.on("pageerror", e => errors.push(String(e)));
      await page.goto(url, { waitUntil: "domcontentloaded", timeout: 30000 });
      await page.waitForFunction(() => {
        const el = document.querySelector("#status");
        return !!el && (el.textContent?.includes("GLB PROVISIONAL") || el.textContent?.includes("Không thể"));
      }, { timeout: 35000 });
      const text = (await page.locator("#status").innerText()).trim();
      if (!text.startsWith("GLB PROVISIONAL")) throw new Error(label + " failed to load GLB: " + text);
      await page.waitForTimeout(1750);
      await page.screenshot({ path: path.join(out, "hero-" + label + ".png") });
      const perf = await page.locator("#stats").innerText();
      evidence.push({ viewport: label, size, status: text, perf, errors });
      if (errors.length) throw new Error(label + " browser errors: " + errors.join(" | "));
      if (label === "desktop") {
        await page.locator("#overview").click();
        await page.waitForTimeout(950);
        await page.screenshot({ path: path.join(out, "overview-desktop.png") });
        await page.locator("#logo").click();
        await page.waitForTimeout(950);
        await page.screenshot({ path: path.join(out, "logo-desktop.png") });
      }
      await context.close();
    }
    const report = { source: "CI Chrome software WebGL", notice: "PROVISIONAL geometry-only visual. Not AIRC photo match or hardware FPS KPI.", evidence };
    await fs.writeFile(path.join(out, "browser-report.json"), JSON.stringify(report, null, 2), "utf8");
    console.log(JSON.stringify(report, null, 2));
  } finally {
    if (browser) await browser.close();
    vite.kill("SIGTERM");
  }
}
main().catch(err => { console.error(err); process.exitCode = 1; });
