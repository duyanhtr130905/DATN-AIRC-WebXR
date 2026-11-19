import assert from "node:assert/strict";
import { spawn, execFileSync } from "node:child_process";
import { createHash } from "node:crypto";
import { existsSync } from "node:fs";
import { mkdir, readFile, writeFile } from "node:fs/promises";
import os from "node:os";
import { resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { chromium } from "playwright";

const root = fileURLToPath(new URL("../../..", import.meta.url));
const web = resolve(root, "apps/web");
const out = resolve(root, ".local/p507-m5");
const origin = "http://127.0.0.1:5195";
const url = origin + "/?mode=p507-visit&evidence=1";
const requireR4 = process.argv.includes("--require-r4");
const lock = JSON.parse(await readFile(resolve(root, "experiments/p507-webxr/asset-lock.json")));
const locked = lock.files["P507_G1_G2_PROVISIONAL.glb"].sha256;
const report = {
    scope: requireR4 ? "Chrome WebGL + original frozen R4 / Chrome + IWER" : "Chrome fallback/mock only; original R4 and XR not tested",
    runtime: "IWER 2.8.0 (explicit test fixture, where indicated)",
    head: execFileSync("git", ["rev-parse", "HEAD"], { cwd: root, encoding: "utf8" }).trim(),
    trackedChanges: Boolean(execFileSync("git", ["status", "--porcelain", "--untracked-files=no"], { cwd: root, encoding: "utf8" }).trim()),
    os: os.type() + " " + os.release(),
    gpuKpi: "NOT TESTED",
    scenarios: [], console: [],
};
await mkdir(out, { recursive: true });
const server = spawn(process.execPath, [resolve(web, "node_modules/vite/bin/vite.js"), "--port", "5195", "--strictPort"], {
    cwd: web, windowsHide: true, stdio: "ignore",
});
let browser;
let page; let activeRequests = [];
const errors = [];
const data = (locator, attribute, value) => locator.and(page.locator("[data-" + attribute + '="' + value + '"]')).waitFor();
const status = state => data(page.getByTestId("xr-status"), "status", state);
const result = state => data(page.getByTestId("asset-status"), "result", state);
const event = name => page.waitForFunction(name => window.__P507_M5__?.events.includes(name), name);

async function scenario(name, expected, run) {
    try {
        const actual = await run();
        assert.deepEqual(activeRequests, [], "The visitor must not call data APIs or send telemetry");
        assert.equal(await page.evaluate(() => window.mediaCalls), 0);
        report.scenarios.push({ name, expected, actual, result: "PASS" });
        console.log("PASS", name);
    } catch (error) {
        report.scenarios.push({ name, expected, actual: String(error), result: "FAIL" });
        throw error;
    }
}

async function open(context, { mock, iwer, missing = !requireR4 } = {}) {
    if (page) await page.close();
    page = await context.newPage();
    page.setDefaultTimeout(45000);
    page.on("pageerror", error => errors.push(String(error)));
    page.on("console", message => {
        if (["warning", "error"].includes(message.type()) && report.console.length < 100) {
            report.console.push({ type: message.type(), text: message.text() });
        }
    });
    const requests = []; activeRequests = requests;
    page.on("request", request => {
        if (request.method() !== "GET" || /\/api\/|\/ws\//.test(request.url())) requests.push(request.url());
    });
    await page.addInitScript(({ mock }) => {
        window.mediaCalls = 0;
        if (navigator.mediaDevices) navigator.mediaDevices.getUserMedia = async () => {
            ++window.mediaCalls;
            throw new Error("Unexpected media access");
        };
        if (!mock) return;
        if (mock === "insecure") Object.defineProperty(window, "isSecureContext", { value: false });
        window.capability = { checks: [], requests: [], available: false };
        const runtime = new EventTarget();
        runtime.isSessionSupported = async mode => {
            window.capability.checks.push(mode);
            return window.capability.available;
        };
        runtime.requestSession = async mode => {
            window.capability.requests.push({ mode, userActive: navigator.userActivation.isActive });
            throw new DOMException("Denied fixture", "NotAllowedError");
        };
        Object.defineProperty(navigator, "xr", { configurable: true, value: runtime });
    }, { mock });
    if (missing) await page.route("**/p507-e1-assets/asset-manifest.json", route => route.fulfill({ status: 404 }));
    if (iwer) {
        await page.addInitScript(options => { window.iwerOptions = options; }, iwer);
        await page.goto(origin + "/tests/m5-iwer.html?mode=p507-visit&evidence=1");
    } else await page.goto(url);
    await page.getByRole("heading", { name: "Tham quan P507" }).waitFor();
    return requests;
}

async function waitR4() {
    await result("E0_SCENE_PASS");
    assert.equal(await page.getByTestId("asset-status").getAttribute("data-sha"), locked);
    await page.waitForFunction(() => window.__P507_M5__?.frames.web?.length > 1);
}

const input = (hand, position, rotation) => page.evaluate(({ hand, position, rotation }) => {
    const controller = window.iwer.device.controllers[hand];
    controller.position.set(...position);
    controller.quaternion.set(...rotation);
}, { hand, position, rotation });
async function trigger(hand = "right") {
    await page.evaluate(async hand => {
        const device = window.iwer.device;
        const controller = device.controllers[hand];
        const frame = () => new Promise(done => device.activeSession.requestAnimationFrame(done));
        controller.updateButtonValue("trigger", 1);
        await Promise.race([frame(), new Promise(done => setTimeout(done, 3000))]);
        controller.updateButtonValue("trigger", 0);
        await Promise.race([frame(), new Promise(done => setTimeout(done, 3000))]);
    }, hand);
}
const selection = () => page.getByLabel("Đối tượng P507").inputValue();
const down = [-Math.SQRT1_2, 0, 0, Math.SQRT1_2];
async function closeFromPanel() {
    const direction = [0.36, 0.155, -1.35];
    const magnitude = Math.hypot(...direction);
    const [x, y, z] = direction.map(v => v / magnitude);
    const quaternion = [y, -x, 0, 1 - z];
    const norm = Math.hypot(...quaternion);
    await input("right", [0, 1.65, 0], quaternion.map(v => v / norm));
    await trigger();
    await event("exit:world-panel");
}

try {
    for (let i = 0; ; i++) {
        if (await fetch(origin).then(value => value.ok).catch(() => false)) break;
        assert(i < 80 && server.exitCode === null, "Vite failed to start");
        await new Promise(done => setTimeout(done, 200));
    }
    if (requireR4) for (const file of ["asset-manifest.json", "P507_G1_G2_PROVISIONAL.glb"]) {
        const bytes = await readFile(resolve(root, ".local/p507-e0-e1/served", file));
        const actual = createHash("sha256").update(bytes).digest("hex");
        assert.equal(actual, lock.files[file].sha256);
        (report.hashes ??= {})[file] = actual;
    }
    const executablePath = process.env.CHROME_BIN || [
        "C:/Program Files/Google/Chrome/Application/chrome.exe", "/usr/bin/google-chrome",
    ].find(existsSync);
    assert(executablePath, "Chrome required");
    browser = await chromium.launch({
        executablePath, args: ["--use-angle=swiftshader", "--enable-unsafe-swiftshader", "--no-sandbox"],
    });
    report.chrome = browser.version();
    const context = await browser.newContext({ viewport: { width: 1200, height: 900 } });
    let requests;
    await scenario("Unsupported and missing R4", "Disabled XR, bounded 404, stable list, no requestSession or sensor call", async () => {
        requests = await open(context, { mock: "unsupported", missing: true });
        await data(page.getByTestId("support-immersive-vr"), "support", "unsupported");
        await result("MISSING");
        assert(await page.getByRole("button", { name: "Vào VR" }).isDisabled());
        assert.equal(await page.getByLabel("Đối tượng P507").locator("option").count(), 122);
        assert.deepEqual(await page.evaluate(() => window.capability.requests), []);
        assert.deepEqual(requests, []);
        return "121 placed IDs selectable as a list, missing asset, zero immersive requests";
    });
    await scenario("Insecure context (injected browser state)", "Capability rejected before navigator and without session request", async () => {
        await open(context, { mock: "insecure", missing: true });
        await data(page.getByTestId("support-immersive-ar"), "support", "insecure");
        assert.deepEqual(await page.evaluate(() => window.capability.checks), []);
        assert(await page.getByRole("button", { name: "Vào AR" }).isDisabled());
        return "Insecure status, XR capability and session calls = 0";
    });
    if (requireR4) {
        await scenario("R4 desktop WebGL / capability change / denied", "Exact pinned R4, actual geometry pick, device change reprobe, trusted gesture, denied falls back", async () => {
            requests = await open(context, { mock: "denied" });
            await waitR4();
            const canvas = page.locator("canvas");
            await canvas.focus();
            await canvas.scrollIntoViewIfNeeded();
            const box = await canvas.boundingBox();
            for (const [x, y] of [[.5,.55], [.5,.65], [.45,.68], [.5,.7], [.55,.68]]) {
                await page.mouse.click(box.x + box.width * x, box.y + box.height * y);
                if (await selection()) break;
            }
            const picked = await selection();
            assert.equal(picked, "P507-WINDOW-04");
            await page.getByTestId("visitor-detail").getByRole("heading", { name: picked }).waitFor();
            await page.screenshot({ path: resolve(out, "desktop-r4.png") });
            await page.getByRole("button", { name: "Về điểm bắt đầu" }).click();
            for (let i = 0; i < 20 && !await page.getByTestId("collision").count(); i++) {
                await page.getByRole("button", { name: "Lùi", exact: true }).click();
            }
            const boundary = await page.getByTestId("collision").textContent();
            assert.deepEqual(await page.evaluate(() => window.capability.requests), []);
            await page.evaluate(() => {
                window.capability.available = true;
                navigator.xr.dispatchEvent(new Event("devicechange"));
            });
            await data(page.getByTestId("support-immersive-vr"), "support", "supported");
            await page.getByRole("button", { name: "Vào VR" }).click();
            await status("denied");
            assert.deepEqual(await page.evaluate(() => window.capability.requests),
                [{ mode: "immersive-vr", userActive: true }]);
            assert.deepEqual(requests, []);
            return { picked, boundary, requests: 1 };
        });
        await scenario("Corrupt GLB / wrong identity / retry", "Modified frozen bytes rejected before rendering or mapping; exact original succeeds on retry", async () => {
            await open(context, { missing: true });
            await result("MISSING");
            await page.unroute("**/p507-e1-assets/asset-manifest.json");
            await page.route("**/p507-e1-assets/*.glb", route => route.fulfill({ body: Buffer.from("invalid glTF") }));
            await page.getByRole("button", { name: "Thử tải R4 lại" }).click();
            await result("HASH_MISMATCH");
            assert.equal(await page.locator("canvas").count(), 0);
            await page.unroute("**/p507-e1-assets/*.glb");
            await page.getByRole("button", { name: "Thử tải R4 lại" }).click();
            await waitR4();
            return "HASH_MISMATCH then E0_SCENE_PASS";
        });
        await scenario("IWER VR / placed logical ID / loss and re-entry", "Real R4 controller ray resolves P507-CHAIR-A-01, releases once, no walking through obstacle, lifecycle restores desktop", async () => {
            await open(context, { iwer: {} });
            await waitR4();
            assert.deepEqual(await page.evaluate(() => window.iwer.logs), []);
            await page.getByRole("button", { name: "Vào VR" }).click();
            await status("active");
            await event("inputs:2");
            await input("right", [2.175 - 1.25, 1.45, -6.115 + 7.415], down);
            await trigger();
            await event("select:P507-CHAIR-A-01");
            await event("selectend");
            assert.equal(await selection(), "P507-CHAIR-A-01");
            await page.screenshot({ path: resolve(out, "iwer-vr-selection.png") });
            await page.evaluate(() => window.iwer.device.updateVisibilityState("visible-blurred"));
            await event("visibility:visible-blurred");
            await page.evaluate(() => window.iwer.device.updateVisibilityState("visible"));
            await event("visibility:visible");
            await page.evaluate(() => { window.iwer.device.controllers.right.connected = false; });
            await event("inputs:1");
            await page.evaluate(() => { window.iwer.device.controllers.right.connected = true; });
            await page.waitForFunction(() => window.__P507_M5__.events.filter(event => event === "inputs:2").length >= 2);
            await page.evaluate(() => window.iwer.device.position.set(2.175 - 1.25, 1.65, -6.115 + 7.415));
            await page.waitForFunction(() => window.__P507_M5__.events.some(event =>
                event.startsWith("physical-boundary:P507-")));
            await page.evaluate(() => window.iwer.device.position.set(0, 1.65, 0));
            await event("physical-boundary:clear");
            await page.evaluate(() => window.iwer.device.controllers.right.updateAxes("thumbstick", -1, 0));
            await page.waitForFunction(() => window.__P507_M5__.events.includes("thumbstick-boundary:ROOM_BOUNDARY_OUTSIDE_UNSURVEYED"));
            await page.evaluate(() => window.iwer.device.controllers.right.updateAxes("thumbstick", 0, 0));
            await page.evaluate(() => window.iwer.device.activeSession.end());
            await status("ended");
            assert.equal(await selection(), "");
            await page.getByRole("button", { name: "Vào VR" }).click();
            await status("active");
            await closeFromPanel();
            await status("ended");
            const evidence = await page.evaluate(() => ({
                events: window.__P507_M5__.events, frames: window.__P507_M5__.frames,
                renderer: window.__P507_M5__.renderer, calls: window.iwer.logs, listeners: window.iwer.listeners(),
            }));
            assert(evidence.calls.every(call => call.userActive));
            assert.equal(evidence.events.filter(event => event === "select:P507-CHAIR-A-01").length, 1);
            assert.equal(evidence.events.filter(event => event === "selectend").length, 2);
            for (const index of [1, 2]) {
                assert.equal(evidence.listeners[index + ":select:addEventListener"], 1);
                assert.equal(evidence.listeners[index + ":select:removeEventListener"], 1);
            }
            report.vr = evidence;
            return "R4 chair A-01 from tracked-pointer; release once, visibility, lost and reconnected controller, obstacle gate, system end and re-entry";
        });
        await scenario("IWER AR hit test, explicit placement, unmount", "IWER grants hit test, one deliberate select places tabletop, ray from above the ceiling reaches interior, AR ends on unmount", async () => {
            await open(context, { iwer: {} });
            await waitR4();
            await page.evaluate(() => {
                window.iwer.device.quaternion.set(-Math.sin(.35), 0, 0, Math.cos(.35));
            });
            await page.getByRole("button", { name: "Vào AR" }).click();
            await status("active");
            await event("ar:surface");
            assert(!await page.evaluate(() => window.__P507_M5__.events.includes("ar:placed")));
            await trigger();
            await event("ar:placed");
            await input("right", [0.08 * (2.175 - 3.45), 1.18,
                -0.93 / Math.tan(0.7) + 0.08 * (-6.115 + 4.6575)], down);
            await trigger();
            await event("select:P507-CHAIR-A-01");
            assert.equal(await selection(), "P507-CHAIR-A-01");
            await page.screenshot({ path: resolve(out, "iwer-ar-placed.png") });
            const arEvidence = await page.evaluate(() => ({
                events: window.__P507_M5__.events, frames: window.__P507_M5__.frames,
                renderer: window.__P507_M5__.renderer, calls: window.iwer.logs,
            }));
            assert.equal(arEvidence.calls[0].mode, "immersive-ar");
            assert.equal(arEvidence.calls[0].userActive, true);
            await page.evaluate(() => window.iwer.device.activeSession.end());
            await status("ended");
            assert.equal(await selection(), "");
            await page.getByRole("button", { name: "Vào AR" }).click();
            await status("active");
            await page.evaluate(() => window.unmountVisitor());
            await page.waitForFunction(() => !window.iwer.device.activeSession && !window.__P507_M5__);
            const arCleanup = await page.evaluate(() => ({
                calls: window.iwer.logs, listeners: window.iwer.listeners(),
            }));
            assert.equal(arCleanup.calls.length, 2);
            assert(arCleanup.calls.every(call => call.mode === "immersive-ar" && call.userActive));
            for (const index of [1, 2]) {
                assert.equal(arCleanup.listeners[index + ":select:addEventListener"], 1);
                assert.equal(arCleanup.listeners[index + ":select:removeEventListener"], 1);
            }
            report.ar = { ...arEvidence, ...arCleanup };
            return "Synthetic horizontal IWER surface, explicit placement, same R4 chair as VR, re-entry and unmount cleanup";
        });
        await scenario("IWER AR without hit test", "No model placement when feature absent, end to Web 3D", async () => {
            await open(context, { iwer: { noHitTest: true } });
            await waitR4();
            await page.getByRole("button", { name: "Vào AR" }).click();
            await status("active");
            await event("ar:unavailable");
            await trigger();
            assert(!await page.evaluate(() => window.__P507_M5__.events.includes("ar:placed")));
            await closeFromPanel();
            await status("ended");
            return "Unsupported optional feature reported; no placement; desktop recovered";
        });
        await scenario("Actual WebGL context loss and restore", "Lose context via WEBGL_lose_context, list available and canvas usable after restoration", async () => {
            await open(context);
            await waitR4();
            const extension = await page.evaluate(() => {
                const gl = document.querySelector("canvas").getContext("webgl2");
                window.loss = gl.getExtension("WEBGL_lose_context");
                window.loss?.loseContext();
                return Boolean(window.loss);
            });
            assert(extension);
            await status("context-lost");
            await page.getByLabel("Đối tượng P507").selectOption("P507-CHAIR-A-01");
            await page.evaluate(() => window.loss.restoreContext());
            await status("idle");
            await page.getByRole("button", { name: "Về điểm bắt đầu" }).click();
            assert.equal(await selection(), "");
            return "Context-lost and restored browser events; list continuity and desktop reset";
        });
        const touch = await browser.newContext({ viewport: { width: 390, height: 844 }, isMobile: true, hasTouch: true });
        await scenario("Responsive touch", "No horizontal overflow, touch targets and actual canvas tap", async () => {
            await open(touch);
            await waitR4();
            assert(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth));
            const canvas = page.locator("canvas");
            await canvas.scrollIntoViewIfNeeded();
            await canvas.scrollIntoViewIfNeeded();
            const box = await canvas.boundingBox();
            for (const y of [.55, .65, .7]) {
                await page.touchscreen.tap(box.x + box.width / 2, box.y + box.height * y);
                if (await selection()) break;
            }
            const picked = await selection();
            assert.equal(picked, "P507-WINDOW-04");
            await page.getByRole("button", { name: "Về điểm bắt đầu" }).tap();
            assert.equal(await selection(), "");
            await page.screenshot({ path: resolve(out, "touch-r4.png"), fullPage: true });
            return { picked, viewport: "390x844" };
        });
        await touch.close();
    }
    assert.deepEqual(errors, []);
    report.result = "PASS";
} catch (error) {
    report.result = "FAIL";
    report.error = String(error);
    report.pageErrors = errors;
    if (page && !page.isClosed()) {
        report.failure = await page.evaluate(() => ({
            events: window.__P507_M5__?.events, frames: window.__P507_M5__?.frames,
            calls: window.iwer?.logs, listeners: window.iwer?.listeners(),
        })).catch(() => null);
        await page.screenshot({ path: resolve(out, "failure.png"), timeout: 10000 }).catch(() => {});
    }
    throw error;
} finally {
    await writeFile(resolve(out, "report.json"), JSON.stringify(report, null, 2) + "\n");
    await browser?.close();
    server.kill();
}
