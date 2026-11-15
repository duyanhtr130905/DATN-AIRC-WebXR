import { chromium } from "playwright";
import { spawn } from "node:child_process";
import { existsSync } from "node:fs";
import { mkdir, writeFile, unlink, readFile } from "node:fs/promises";
import { fileURLToPath } from "node:url";
import { resolve } from "node:path";
import { createServer } from "node:net";
import { platform, release } from "node:os";
import assert from "node:assert/strict";
import { PerspectiveCamera, Vector3 } from "three";
const root = resolve(fileURLToPath(new URL("../../..", import.meta.url)));
const web = resolve(root, "apps/web");
const out = resolve(root, ".local/app-browser");
const temp = resolve(root, ".local/t");
assert.equal(JSON.parse(await readFile(resolve(web, "package.json"), "utf8")).name, "airc-web");
await mkdir(out, { recursive: true }); await mkdir(temp, { recursive: true });
for (const name of ["desktop.png", "mobile-390.png", "unsupported.png", "report.json"]) {
  try { await unlink(resolve(out, name)); } catch (error) { if (error.code !== "ENOENT") throw error; }
}
const bin = process.env.CHROME_BIN || ["C:/Program Files/Google/Chrome/Application/chrome.exe", "/usr/bin/google-chrome", "/usr/bin/chromium", "/usr/bin/chromium-browser"].find(existsSync);
const report = { executedAt: new Date().toISOString(), os: `${platform()} ${release()}`, browser: null, renderer: "native Chrome WebGL2, software ANGLE", xr: "NOT RUN: no XR session or physical device", scenarios: [] };
const children = [];
let browser;
let logs = "";
async function port() { const server = createServer(); await new Promise(r => server.listen(0, "127.0.0.1", r)); const value = server.address().port; await new Promise(r => server.close(r)); return value; }
function start(command, args, env = {}) {
  const child = spawn(command, args, { cwd: root, env: { ...process.env, ...env }, windowsHide: true, stdio: ["ignore", "pipe", "pipe"] });
  children.push(child); child.stdout.on("data", data => { logs += data; }); child.stderr.on("data", data => { logs += data; });
  child.on("error", error => { logs += error.message; });
  return child;
}
async function wait(url, child) {
  for (let i = 0; i < 120; i++) {
    if (child.exitCode !== null) throw new Error(`Service exited before ready: ${url}`);
    try { if ((await fetch(url)).ok) return; } catch { /* service still starting */ }
    await new Promise(r => setTimeout(r, 250));
  }
  throw new Error(`Service startup timeout: ${url}`);
}
async function waitForCanvasLayout(page, minimumWidth) {
  // Canvas can exist at its initial 300x150 size before ResizeObserver commits.
  // Wait for measurable host/canvas agreement instead of weakening the assertion or sleeping.
  await page.waitForFunction(minimum => {
    const canvas = document.querySelector("canvas");
    const host = canvas?.closest(".scene");
    if (!canvas || !host) return false;
    const rect = canvas.getBoundingClientRect();
    const bounds = host.getBoundingClientRect();
    return rect.width > minimum && rect.height > 300 && Math.abs(rect.width - bounds.width) < 2;
  }, minimumWidth);
  await page.evaluate(() => new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve))));
}
async function scenario(name, action) {
  const row = { scenario: name, expected: "Assertions pass", actual: "", status: "FAIL" };
  report.scenarios.push(row);
  await action(); row.status = "PASS"; row.actual = "All assertions passed";
}
try {
  if (!bin) { report.status = "NOT RUN"; throw new Error("Chrome not found; set CHROME_BIN. No browser is downloaded."); }
  const apiPort = await port(); const webPort = await port();
  const python = process.env.API_PYTHON || "python";
  const backend = spawn(python, ["-m", "uvicorn", "app.main:create_app", "--factory", "--app-dir", resolve(root, "apps/api"), "--host", "127.0.0.1", "--port", String(apiPort)], {
    cwd: temp, windowsHide: true, stdio: ["ignore", "pipe", "pipe"],
    env: Object.fromEntries(Object.entries(process.env).filter(([key]) => !["DATABASE_URL", "CORS_ORIGINS"].includes(key.toUpperCase()))),
  });
  children.push(backend); backend.on("error", e => { logs += e.message; });
  backend.stdout.on("data", d => { logs += d; }); backend.stderr.on("data", d => { logs += d; });
  const frontend = start(process.execPath, [resolve(web, "node_modules/vite/bin/vite.js"), "preview", "--config", resolve(web, "vite.config.ts"), "--host", "127.0.0.1", "--port", String(webPort), "--strictPort", "--outDir", resolve(web, "dist")], { API_PROXY_TARGET: `http://127.0.0.1:${apiPort}` });
  await wait(`http://127.0.0.1:${apiPort}/api/health`, backend);
  await wait(`http://127.0.0.1:${webPort}/?mode=offline`, frontend);
  browser = await chromium.launch({ executablePath: bin, headless: true, args: ["--use-angle=swiftshader", "--enable-unsafe-swiftshader"], env: { ...process.env, TEMP: temp, TMP: temp, TMPDIR: temp } });
  report.browser = browser.version();
  const context = await browser.newContext({ viewport: { width: 1440, height: 1000 } });
  const page = await context.newPage(); const errors = [];
  page.on("pageerror", e => errors.push(e.message));
  await scenario("Desktop: renderer + real FastAPI health, DB not configured", async () => {
    await page.goto(`http://127.0.0.1:${webPort}/?mode=offline`, { waitUntil: "networkidle" });
    await page.getByTestId("health").filter({ hasText: "Backend đang hoạt động" }).waitFor();
    assert.match(await page.getByTestId("readiness").innerText(), /not_configured/);
    await page.locator("canvas").waitFor();
    await waitForCanvasLayout(page, 400);
    const box = await page.locator("canvas").boundingBox(); assert.ok(box.width > 400);
    await page.getByRole("button", { name: /Khối mẫu A/ }).click();
    assert.equal(await page.getByRole("button", { name: /Khối mẫu A/ }).getAttribute("aria-pressed"), "true");
    await page.screenshot({ path: resolve(out, "desktop.png"), fullPage: true });
  });
  await scenario("Actual mouse ray pick + keyboard selection + reset", async () => {
    const rect = await page.locator("canvas").boundingBox();
    const camera = new PerspectiveCamera(45, rect.width / rect.height, 0.1, 1000);
    camera.position.set(8, 7, 11); camera.lookAt(0, 0.5, 0); camera.updateMatrixWorld();
    const p = new Vector3(1.8, 0.65, -1).project(camera);
    await page.mouse.click(rect.x + (p.x + 1) * rect.width / 2, rect.y + (1 - p.y) * rect.height / 2);
    await page.getByRole("button", { name: /Khối mẫu B/ }).waitFor();
    assert.equal(await page.getByRole("button", { name: /Khối mẫu B/ }).getAttribute("aria-pressed"), "true");
    await page.getByRole("button", { name: /Khối mẫu A/ }).focus(); await page.keyboard.press("Enter");
    assert.equal(await page.getByRole("button", { name: /Khối mẫu A/ }).getAttribute("aria-pressed"), "true");
    await page.getByRole("button", { name: /Kiểm tra lại/ }).click();
    await page.getByTestId("health").filter({ hasText: "Backend đang hoạt động" }).waitFor();
  });
  await scenario("390px viewport emulation: touch + focus + no overflow", async () => {
    const mobile = await browser.newContext({ viewport: { width: 390, height: 844 }, hasTouch: true, isMobile: true });
    const p = await mobile.newPage(); p.on("pageerror", e => errors.push(e.message));
    await p.goto(`http://127.0.0.1:${webPort}/?mode=offline`, { waitUntil: "networkidle" });
    await waitForCanvasLayout(p, 300);
    await p.getByRole("button", { name: /Khối mẫu B/ }).tap();
    assert.equal(await p.getByRole("button", { name: /Khối mẫu B/ }).getAttribute("aria-pressed"), "true");
    assert.ok(await p.evaluate(() => document.documentElement.scrollWidth <= innerWidth));
    await p.getByRole("button", { name: /Khối mẫu A/ }).focus();
    assert.ok(await p.getByRole("button", { name: /Khối mẫu A/ }).evaluate(e => e === document.activeElement));
    await p.screenshot({ path: resolve(out, "mobile-390.png"), fullPage: true }); await mobile.close();
  });
  await scenario("WebGL2 unsupported: injected unavailable getContext, DOM still usable", async () => {
    const unsupported = await browser.newContext();
    await unsupported.addInitScript(() => { const original = HTMLCanvasElement.prototype.getContext; HTMLCanvasElement.prototype.getContext = function(type, ...args) { return type === "webgl2" ? null : original.call(this, type, ...args); }; });
    const p = await unsupported.newPage(); await p.goto(`http://127.0.0.1:${webPort}/?mode=offline`);
    await p.getByRole("alert").filter({ hasText: /WebGL2/ }).waitFor();
    await p.getByRole("button", { name: /Khối mẫu A/ }).click();
    await p.screenshot({ path: resolve(out, "unsupported.png"), fullPage: true }); await unsupported.close();
  });
  await scenario("Readiness network failure preserves live backend status", async () => {
    await page.route("**/api/ready", route => route.abort());
    await page.getByRole("button", { name: /Kiểm tra lại/ }).click();
    await page.getByTestId("health").filter({ hasText: "Backend đang hoạt động" }).waitFor();
    await page.getByTestId("readiness").filter({ hasText: "Chưa xác minh được database" }).waitFor();
    await page.unroute("**/api/ready");
  });
  await scenario("Backend unavailable: network failure is visible (browser routing mock)", async () => {
    await page.route("**/api/*", route => route.abort());
    await page.getByRole("button", { name: /Kiểm tra lại/ }).click();
    await page.getByTestId("health").filter({ hasText: "Không kết nối được backend" }).waitFor();
  });
  await scenario("Live mode never silently falls back when DB unavailable", async()=>{
    const live=await context.newPage();await live.goto(`http://127.0.0.1:${webPort}/`);
    await live.getByRole("alert").filter({hasText:/Database\/backend/}).waitFor();
    assert.equal(await live.locator("[data-object-id]").count(),0);
    assert.equal(await live.locator("canvas").count(),0);await live.close();
  });
  assert.deepEqual(errors, []); report.status = "PASS";
} catch (error) {
  report.status ??= "FAIL"; report.error = String(error); process.exitCode = 1;
} finally {
  await browser?.close();
  for (const child of children.reverse()) {
    if (child.exitCode !== null) continue;
    const ended = new Promise(r => child.once("exit", r)); child.kill();
    const finished = await Promise.race([ended.then(() => true), new Promise(r => setTimeout(() => r(false), 3000))]);
    if (!finished) { child.kill("SIGKILL"); await Promise.race([ended, new Promise(r => setTimeout(r, 3000))]); }
  }
  // Logs contain local startup messages only; report omits environment variables and DB URL.
  if (report.status !== "PASS") console.error(logs.slice(-3000));
  await writeFile(resolve(out, "report.json"), JSON.stringify(report, null, 2) + "\n");
  console.log(JSON.stringify(report, null, 2));
}
