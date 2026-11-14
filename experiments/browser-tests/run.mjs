import { chromium } from "playwright";
import { spawn } from "node:child_process";
import {
  existsSync,
  mkdirSync,
  writeFileSync,
  readFileSync,
  readdirSync,
  unlinkSync,
} from "node:fs";
import { fileURLToPath } from "node:url";
import path from "node:path";
import net from "node:net";
import assert from "node:assert/strict";
import os from "node:os";
const root = fileURLToPath(new URL("../../", import.meta.url));
const out = path.join(root, ".local/poc-browser");
mkdirSync(out, { recursive: true });
for (const name of readdirSync(out)) {
  if (/^poc-[ab]-(r3f-xr|iwsdk).*\.(png|log)$/.test(name))
    unlinkSync(path.join(out, name));
}
const temp = path.join(root, ".local/t");
mkdirSync(temp, { recursive: true });
process.env.TEMP = temp;
process.env.TMP = temp;
process.env.TMPDIR = temp;
const rows = [];
const push = rows.push.bind(rows);
rows.push = (...items) => {
  for (const item of items)
    console.log(
      item.project || "setup",
      item.scenario || "main-flow",
      item.status,
    );
  return push(...items);
};
const servers = [];
let browser;
const report = {
  executed_at: new Date().toISOString(),
  os: os.platform(),
  node: process.version,
  scenario_scope:
    "Synthetic primitives only; desktop software WebGL and viewport emulation, not Galaxy/headset performance.",
  results: rows,
};
const browserPath =
  process.env.CHROME_BIN ||
  [
    process.env.PROGRAMFILES &&
      path.join(
        process.env.PROGRAMFILES,
        "Google/Chrome/Application/chrome.exe",
      ),
    "/usr/bin/google-chrome",
    "/usr/bin/chromium",
  ].find((p) => p && existsSync(p));
const wait = (ms) => new Promise((r) => setTimeout(r, ms));
async function until(fn, expected, timeout = 20000) {
  const deadline = Date.now() + timeout;
  while (Date.now() < deadline) {
    if (await fn()) return;
    await wait(100);
  }
  throw new Error("Timeout: " + expected);
}
async function port() {
  const s = net.createServer();
  await new Promise((r) => s.listen(0, "127.0.0.1", r));
  const p = s.address().port;
  await new Promise((r) => s.close(r));
  return p;
}
async function serve(project, dev = false) {
  const directory = path.join(root, "experiments", project),
    p = await port();
  let logs = "";
  const child = spawn(
    process.execPath,
    [
      path.join(directory, "node_modules/vite/bin/vite.js"),
      ...(dev ? [] : ["preview"]),
      "--host",
      "127.0.0.1",
      "--port",
      String(p),
      "--strictPort",
    ],
    { cwd: directory, windowsHide: true, stdio: ["ignore", "pipe", "pipe"] },
  );
  child.stdout.on("data", (b) => (logs += b));
  child.stderr.on("data", (b) => (logs += b));
  servers.push({
    child,
    project,
    get logs() {
      return logs;
    },
  });
  const url = `http://127.0.0.1:${p}`;
  await until(
    async () => {
      if (child.exitCode !== null) throw new Error(logs);
      try {
        return (await fetch(url)).ok;
      } catch {
        return false;
      }
    },
    "server " + project,
    30000,
  );
  return url;
}
async function pageFor(
  viewport = { width: 1280, height: 900 },
  mobile = false,
) {
  const context = await browser.newContext({
    viewport,
    deviceScaleFactor: 1,
    isMobile: mobile,
    hasTouch: mobile,
  });
  const page = await context.newPage();
  page.setDefaultTimeout(10000);
  page.setDefaultNavigationTimeout(30000);
  const errors = [];
  page.on("pageerror", (e) => {
    if (errors.length < 10) errors.push(e.stack || e.message);
  });
  await page.addInitScript(() => {
    window.__cameraCalls = 0;
    if (navigator.mediaDevices)
      navigator.mediaDevices.getUserMedia = async () => {
        window.__cameraCalls++;
        throw new Error("Camera forbidden in PoC tests");
      };
  });
  return { page, context, errors };
}
async function testDesktop(project, url) {
  const { page, context, errors } = await pageFor();
  const start = performance.now();
  try {
    await page.goto(url, {waitUntil:"domcontentloaded"});
    await until(
      () =>
        page.evaluate(() => !!window.__poc && window.__poc.info().calls > 0),
      "render ready",
    );
    await page.getByTestId("object-1").waitFor();
    await page.waitForTimeout(250);
    const readyMs = Math.round(performance.now() - start);
    assert.equal(await page.evaluate(() => window.__poc.xr().active), false);
    const initial = await page.evaluate(() => window.__poc.snapshot());
    assert.equal(initial.scene.objects.length, 5);
    assert.ok(
      initial.scene.objects.every(
        (o) => o.provenance.source_kind === "synthetic",
      ),
    );
    const xy = await page.evaluate(() =>
      window.__poc.project("demo-object-001"),
    );
    await page.mouse.click(xy.x, xy.y);
    await until(
      () =>
        page.evaluate(
          () => window.__poc.snapshot().selectedId === "demo-object-001",
        ),
      "real canvas click",
    );
    const before = await page.getByTestId("status").textContent();
    await page.getByTestId("change").click();
    const after = await page.getByTestId("status").textContent();
    assert.notEqual(before, after);
    if (project === "poc-b-iwsdk") {
      const entities = await page.evaluate(() => window.__poc.ecs());
      assert.equal(entities.length, 5);
      assert.equal(
        entities.find((e) => e.id === "demo-object-001").state,
        after,
      );
    }
    const hostBox = await page.getByTestId("viewport").boundingBox();
    const canvasBox = await page.locator("canvas").boundingBox();
    assert.ok(
      Math.abs(canvasBox.width - hostBox.width) < 2 &&
        Math.abs(canvasBox.height - hostBox.height) < 2,
      "canvas confined to host",
    );
    const beforeProjection = await page.evaluate(() =>
      window.__poc.project("demo-object-002"),
    );
    const canvas = await page.locator("canvas").boundingBox();
    await page.mouse.move(
      canvas.x + canvas.width * 0.7,
      canvas.y + canvas.height * 0.5,
    );
    await page.mouse.down();
    await page.mouse.move(
      canvas.x + canvas.width * 0.7 + 70,
      canvas.y + canvas.height * 0.5 + 20,
      { steps: 6 },
    );
    await page.mouse.up();
    const afterProjection = await page.evaluate(() =>
      window.__poc.project("demo-object-002"),
    );
    assert.ok(
      Math.abs(beforeProjection.x - afterProjection.x) > 1,
      "orbit changes camera projection",
    );
    await page.getByTestId("reset").click();
    assert.equal(
      await page.evaluate(() => window.__poc.snapshot().selectedId),
      null,
    );
    await page
      .getByRole("button", { name: "Tour dẫn đường", exact: true })
      .click();
    await until(
      () =>
        page.evaluate(
          () => window.__poc.snapshot().selectedId === "demo-object-001",
        ),
      "tour first",
    );
    await page
      .getByRole("button", { name: "Điểm tiếp theo →", exact: true })
      .click();
    assert.equal(
      await page.evaluate(() => window.__poc.snapshot().selectedId),
      "demo-object-002",
    );
    await page.screenshot({
      path: path.join(out, project + "-guided-desktop.png"),
      fullPage: true,
    });
    await page
      .getByRole("button", { name: "Cảnh + thông tin", exact: true })
      .click();
    await page.getByTestId("object-3").click();
    await page.screenshot({
      path: path.join(out, project + "-panel-desktop.png"),
      fullPage: true,
    });
    await page.getByRole("button", { name: "Vào AR", exact: true }).click();
    await until(
      async () =>
        (await page.getByTestId("xr-status").textContent()).includes(
          "Không vào được XR",
        ),
      "unsupported native XR",
    );
    const info = await page.evaluate(() => window.__poc.info());
    assert.equal(await page.evaluate(() => window.__cameraCalls), 0);
    assert.deepEqual(errors, []);
    rows.push({
      project,
      scenario: "desktop-main-flows",
      status: "PASS",
      expected:
        "Real canvas pick, state update, ECS projection (B), orbit/reset, guided next, native XR fallback; no startup session/camera/runtime exception.",
      actual: { readyMs, info, before, after },
      screenshots: [
        project + "-guided-desktop.png",
        project + "-panel-desktop.png",
      ],
    });
    await page.goto(url + "/?forceNoWebGL=1", {waitUntil:"domcontentloaded"});
    await page.getByRole("alert").waitFor();
    assert.ok((await page.getByRole("alert").textContent()).includes("WebGL2"));
    rows.push({
      project,
      scenario: "webgl-unsupported",
      status: "PASS",
      expected: "Readable error, no scene",
      actual: "WebGL2 error displayed (controlled failure path)",
    });
  } finally {
    await context.close();
  }
}
async function testMobile(project, url) {
  const { page, context, errors } = await pageFor(
    { width: 390, height: 844 },
    true,
  );
  try {
    await page.goto(url, {waitUntil:"domcontentloaded"});
    await until(
      () =>
        page.evaluate(() => !!window.__poc && window.__poc.info().calls > 0),
      "mobile ready",
    );
    await page.getByTestId("object-1").waitFor();
    await page.waitForTimeout(250);
    const xy = await page.evaluate(() =>
      window.__poc.project("demo-object-001"),
    );
    await page.touchscreen.tap(xy.x, xy.y);
    await until(
      () =>
        page.evaluate(
          () => window.__poc.snapshot().selectedId === "demo-object-001",
        ),
      "touch canvas pick",
    );
    await page.getByTestId("object-5").tap();
    assert.equal(
      await page.getByTestId("object-id").textContent(),
      "demo-object-005",
    );
    await page.getByTestId("change").tap();
    await page.getByTestId("object-2").focus();
    assert.equal(
      await page
        .getByTestId("object-2")
        .evaluate((e) => e === document.activeElement),
      true,
    );
    const dimensions = await page.evaluate(() => ({
      width: innerWidth,
      scroll: document.documentElement.scrollWidth,
    }));
    assert.equal(dimensions.width, 390);
    assert.equal(dimensions.scroll, 390);
    await page.screenshot({
      path: path.join(out, project + "-panel-mobile.png"),
      fullPage: true,
    });
    assert.deepEqual(errors, []);
    rows.push({
      project,
      scenario: "mobile-touch-and-layout",
      status: "PASS",
      expected:
        "390px no overflow, actual canvas touch, object list tap, state update, focus; viewport emulation only",
      actual: dimensions,
      screenshots: [project + "-panel-mobile.png"],
    });
  } finally {
    await context.close();
  }
}
async function testEmulator(project, url) {
  const { page, context, errors } = await pageFor();
  try {
    await page.goto(url + (project === "poc-a-r3f-xr" ? "/?emulate=1" : "/"));
    await until(
      () => page.evaluate(() => !!window.__poc),
      "emulator app ready",
    );
    await until(
      () => page.evaluate(() => !!window.__poc.device?.()),
      "IWER injected",
      30000,
    );
    assert.equal(await page.evaluate(() => window.__poc.xr().active), false);
    await page.getByRole("button", { name: "Vào VR", exact: true }).click();
    await until(
      () => page.evaluate(() => window.__poc.xr().active),
      "enter emulated VR",
      20000,
    );
    await until(
      () => page.evaluate(() => window.__poc.xr().inputs > 0),
      "XR input sources",
      10000,
    );
    const actual = await page.evaluate(() => window.__poc.xr());
    await page.screenshot({
      path: path.join(out, project + "-iwer.png"),
      fullPage: true,
    });
    await page
      .getByTitle(/^(Click to exit XR session|Exit XR session)$/)
      .click();
    await until(
      () => page.evaluate(() => !window.__poc.xr().active),
      "exit emulated VR",
    );
    assert.deepEqual(errors, []);
    rows.push({
      project,
      scenario: "iwer-lifecycle-and-input-sources",
      status: "PASS",
      expected:
        "Explicit VR entry, IWER input sources >0, exit returns browser-first; no physical hardware claim",
      actual,
      unverified:
        "Controller ray target selection, locomotion/comfort and physical hardware not tested",
      runtimeErrors: errors,
      screenshots: [project + "-iwer.png"],
    });
  } catch (error) {
    await page
      .screenshot({
        path: path.join(out, project + "-iwer-failure.png"),
        fullPage: true,
      })
      .catch(() => {});
    rows.push({
      project,
      scenario: "iwer-diagnostics",
      status: "FAIL",
      error: error.message,
      actual: {
        message: await page
          .getByTestId("xr-status")
          .textContent()
          .catch(() => null),
        errors,
        buttons: await page
          .getByRole("button")
          .allTextContents()
          .catch(() => []),
      },
    });
    throw error;
  } finally {
    await context.close();
  }
}
try {
  if (!browserPath)
    throw new Error(
      "NOT RUN: Chrome unavailable; set CHROME_BIN. No automatic browser download.",
    );
  browser = await chromium.launch({
    executablePath: browserPath,
    headless: true,
    args: ["--use-angle=swiftshader", "--enable-unsafe-swiftshader"],
  });
  report.browser = browser.version();
  for (const project of process.env.POC_ONLY
    ? [process.env.POC_ONLY]
    : ["poc-a-r3f-xr", "poc-b-iwsdk"]) {
    const url = await serve(project);
    for (const job of process.env.POC_PHASE === "emulation"
      ? []
      : [() => testDesktop(project, url), () => testMobile(project, url)]) {
      try {
        await job();
      } catch (e) {
        rows.push({ project, status: "FAIL", error: e.message });
      }
    }
    const emulationUrl =
      project === "poc-a-r3f-xr" ? url : await serve(project, true);
    try {
      await testEmulator(project, emulationUrl);
    } catch (e) {
      rows.push({
        project,
        scenario: "iwer-lifecycle-and-input-sources",
        status: "FAIL",
        error: e.message,
      });
    }
  }
} catch (e) {
  rows.push({
    scenario: "setup",
    status: browserPath ? "FAIL" : "NOT RUN",
    error: e.message,
  });
} finally {
  await browser?.close();
  for (const s of servers) {
    s.child.kill();
    await Promise.race([
      new Promise((r) => s.child.once("exit", r)),
      wait(3000),
    ]);
    writeFileSync(path.join(out, s.project + "-server.log"), s.logs);
  }
  report.status =
    rows.length && rows.every((r) => r.status === "PASS") ? "PASS" : "FAIL";
  writeFileSync(
    path.join(out, "report.json"),
    JSON.stringify(report, null, 2) + "\n",
  );
  console.log(JSON.stringify(report, null, 2));
  if (report.status !== "PASS") process.exitCode = 1;
}
