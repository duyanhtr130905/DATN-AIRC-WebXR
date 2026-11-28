import assert from "node:assert/strict";
import { execFileSync, spawn } from "node:child_process";
import { createServer } from "node:net";
import { mkdir, readFile, writeFile } from "node:fs/promises";
import { request } from "node:http";
import { existsSync } from "node:fs";
import { resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { chromium } from "playwright";
import { Quaternion, Vector3 } from "three";

const root = fileURLToPath(new URL("../../..", import.meta.url));
const web = resolve(root, "apps/web");
const out = resolve(root, process.env.R5_BROWSER_OUT || ".local/p507-r5/runtime-" + Date.now());
const missingOnly = process.argv.includes("--missing");
const onlyVR = process.argv.includes("--only-vr");
const report = {
    head: execFileSync("git", ["rev-parse", "HEAD"], { cwd: root, encoding: "utf8" }).trim(),
    trackedChanges: Boolean(execFileSync("git", ["status", "--porcelain", "--untracked-files=no"], { cwd: root, encoding: "utf8" }).trim()),
    scope: missingOnly ? "Missing R5 and DEV middleware negatives" : "Chrome software WebGL and IWER, actual R5 locked GLB",
    scenarios: [], result: "FAIL",
};
await mkdir(out, { recursive: true });
const listener = createServer();
await new Promise(resolve => listener.listen(0, "127.0.0.1", resolve));
const port = listener.address().port;
await new Promise(resolve => listener.close(resolve));
const origin = "http://127.0.0.1:" + port;
const base = "/?mode=p507-visit&revision=r5&evidence=1";
const iwer = "/tests/m5-iwer.html?mode=p507-visit&revision=r5&evidence=1";
const vite = spawn(process.execPath, ["node_modules/vite/bin/vite.js", "--port", String(port), "--strictPort"], {
    cwd: web, stdio: "ignore", windowsHide: true,
});
let browser;
const binary = process.env.CHROME_BIN || ["C:/Program Files/Google/Chrome/Application/chrome.exe", "/usr/bin/google-chrome", "/usr/bin/chromium"]
    .find(existsSync);
const row = async (name, run) => {
    const result = { name, result: "FAIL" };
    report.scenarios.push(result);
    result.observation = await run();
    result.result = "PASS";
    console.log("PASS " + name);
};
const closeEnough = (actual, expected, tolerance = .005) => assert.ok(
    Math.hypot(...actual.map((value, index) => value - expected[index])) < tolerance,
    JSON.stringify({ actual, expected, tolerance }),
);

async function aim(page, position, target) {
    const direction = new Vector3(...target).sub(new Vector3(...position)).normalize();
    const quaternion = new Quaternion().setFromUnitVectors(new Vector3(0, 0, -1), direction).toArray();
    await page.evaluate(({ position, quaternion }) => {
        const controller = window.iwer.device.controllers.right;
        controller.position.set(...position);
        controller.quaternion.set(...quaternion);
    }, { position, quaternion });
}
async function trigger(page) {
    await page.evaluate(async () => {
        const device = window.iwer.device;
        const frame = () => new Promise(done => device.activeSession.requestAnimationFrame(done));
        device.controllers.right.updateButtonValue("trigger", 1);
        await frame();
        device.controllers.right.updateButtonValue("trigger", 0);
        await frame();
    });
}
async function event(page, name) {
    try {
        await page.waitForFunction(name => window.__P507_M5__?.events.includes(name), name);
    } catch (error) {
        const recent = await page.evaluate(() => window.__P507_M5__?.events.slice(-16)).catch(() => undefined);
        throw new Error("Missing event " + name + "; observed " + JSON.stringify(recent), { cause: error });
    }
}
const snapshot = page => page.evaluate(() => window.__P507_M5__?.snapshotR5?.());
const bound = (page, id) => page.evaluate(id => window.__P507_M5__?.r5Bounds?.(id), id);
const waitLoaded = (page, hash) => page.locator('[data-testid="asset-status"][data-result="E0_SCENE_PASS"][data-sha="' + hash + '"]')
    .waitFor({ timeout: 60000 });

try {
    for (let i = 0; !await fetch(origin).then(r => r.ok).catch(() => false); i++) {
        assert.ok(i < 100 && vite.exitCode === null, "Vite startup failed");
        await new Promise(done => setTimeout(done, 150));
    }
    assert.ok(binary, "Chrome not found");
    browser = await chromium.launch({ executablePath: binary, headless: true,
        args: ["--use-gl=angle", "--use-angle=swiftshader", "--enable-unsafe-swiftshader", "--enable-webgl"] });
    report.chrome = browser.version();
    const context = await browser.newContext({ viewport: { width: 1280, height: 800 } });
    await row("DEV-only allowlist and explicit R5 missing fallback", async () => {
        const forbidden = [
            "/p507-r5-assets/asset-lock.json",
            "/p507-r5-assets/%61sset-manifest.json",
            "/p507-r5-assets/%2e%2e%2fasset-manifest.json",
            "/p507-r5-assets/P507_R5_PROPOSAL.blend",
            "/@fs/" + resolve(root, ".local/p507-r5/served/asset-manifest.json").replaceAll("\\", "/"),
        ];
        const statuses = {};
        for (const target of forbidden) {
            const response = await fetch(origin + target);
            statuses[target] = response.status;
            assert.ok([403, 404].includes(response.status), target);
        }
        const deniedHost = await new Promise((done, reject) => {
            request(origin + "/p507-r5-assets/asset-manifest.json", { headers: { Host: "non-loopback.invalid" } }, response => {
                response.resume();
                done(response.statusCode);
            }).on("error", reject).end();
        });
        assert.ok([403, 404].includes(deniedHost), "non-loopback host must be denied: " + deniedHost);
        statuses.nonLoopbackHost = deniedHost;
        const page = await context.newPage();
        await page.route("**/p507-r5-assets/**", route => route.fulfill({ status: 404 }));
        await page.goto(origin + base);
        await page.getByTestId("asset-status").filter({ hasText: "R5 không khả dụng" }).waitFor();
        assert.equal(await page.getByTestId("asset-status").getAttribute("data-result"), "MISSING");
        await page.getByRole("button", { name: "Thử tải R5 lại" }).click();
        assert.equal(await page.getByRole("link", { name: "Trở về R4" }).getAttribute("href"), "/?mode=p507-visit");
        await page.close();
        return statuses;
    });
    if (!missingOnly) {
        const manifest = JSON.parse(await readFile(resolve(root, ".local/p507-r5/served/asset-manifest.json"), "utf8"));
        const hash = manifest.model_sha256;
        report.modelSha256 = hash;
        if (!onlyVR) await row("Web 3D uses real R5 scene, stored chair identities, capsule input and fallback", async () => {
            const page = await context.newPage();
            await page.goto(origin + base);
            await waitLoaded(page, hash);
            await page.waitForFunction(() => window.__P507_M5__?.webPose);
            const before = await snapshot(page);
            assert.equal(Object.keys(before.chairs).length, 34);
            for (const chair of manifest.layout.chairs) {
                assert.equal(before.chairs[chair.id].state, "stored");
                closeEnough(before.chairs[chair.id].pose, chair.stored);
                assert.ok(await bound(page, chair.id), chair.id + " real scene geometry");
            }
            const start = await page.evaluate(() => window.__P507_M5__.webPose);
            await page.getByRole("button", { name: "Tiến", exact: true }).click();
            await page.waitForFunction(({ x, z }) => {
                const p = window.__P507_M5__?.webPose;
                return p && Math.hypot(p.x - x, p.z - z) > 0.035;
            }, start);
            const moved = await page.evaluate(() => window.__P507_M5__.webPose);
            await page.getByRole("button", { name: "Về điểm bắt đầu", exact: true }).click();
            await page.waitForFunction(start => window.__P507_M5__?.webPose?.x === start.x &&
                window.__P507_M5__?.webPose?.z === start.z, start);
            await page.screenshot({ path: resolve(out, "r5-web.png") });
            await page.close();
            return { chairs: Object.keys(before.chairs).length, start, moved };
        });
        if (!onlyVR) await row("All 34 actual GLB chairs animate and complete the four-action Web 3D cycle", async () => {
            const page = await context.newPage();
            await page.goto(origin + "/tests/r5-walk.html?mode=p507-visit&revision=r5&evidence=1");
            await waitLoaded(page, hash);
            await page.waitForFunction(() => window.__P507_R5_TEST__ && window.__P507_M5__?.webPose);
            const picker = page.getByLabel("Đối tượng P507");
            const chairActions = page.getByTestId("chair-actions");
            const result = [];
            const point = ([x, y]) => [x, -y];
            const place = coordinates => page.evaluate(point => window.__P507_R5_TEST__.place(point, -Math.PI / 2), coordinates);
            const state = (id, wanted) => page.waitForFunction(({ id, wanted }) =>
                window.__P507_M5__?.snapshotR5?.().chairs[id]?.state === wanted, { id, wanted });
            const pose = () => page.evaluate(() => window.__P507_M5__.webPose);
            for (const chair of manifest.layout.chairs) {
                await picker.selectOption(chair.id);
                const original = await bound(page, chair.id);
                assert.ok(original, chair.id);
                const shift = chair.pulled.map((value, i) => value - chair.stored[i]);
                const pulledCenter = original.center.map((value, i) => value + [shift[0], shift[2], -shift[1]][i]);
                const approach = await page.evaluate(choices => choices.find(point => !window.__P507_R5_TEST__.blocked(point, point)),
                    [chair.approach, ...chair.approach_alternatives].map(point));
                assert.ok(approach, chair.id + " valid approach fixture");
                await place(approach);
                await chairActions.getByRole("button", { name: "Kéo ghế ra" }).click();
                await state(chair.id, "pulled-out");
                const pulledBounds = await bound(page, chair.id);
                closeEnough(pulledBounds.center, pulledCenter);
                await place(point(chair.stand));
                await chairActions.getByRole("button", { name: "Ngồi xuống" }).click();
                await state(chair.id, "occupied");
                await page.waitForFunction(eye => Math.abs(window.__P507_M5__.webPose.eye - eye) < .003, chair.seat_eye[2]);
                const seated = await pose();
                closeEnough([seated.x, seated.z], point(chair.seat_eye));
                if (result.length === 0) await page.screenshot({ path: resolve(out, "r5-web-seated.png") });
                await chairActions.getByRole("button", { name: "Đứng dậy" }).click();
                await state(chair.id, "pulled-out");
                await page.waitForFunction(() => Math.abs(window.__P507_M5__.webPose.eye - 1.65) < .003);
                const standing = await pose();
                closeEnough([standing.x, standing.z], point(chair.stand));
                await place(approach);
                await chairActions.getByRole("button", { name: "Cất ghế" }).click();
                await state(chair.id, "stored");
                const restored = await bound(page, chair.id);
                closeEnough(restored.center, original.center);
                result.push({ id: chair.id, approach, seated, standing, storedBounds: original, pulledBounds, restoredBounds: restored });
            }
            await page.reload();
            await waitLoaded(page, hash);
            await page.waitForFunction(() => window.__P507_M5__?.snapshotR5);
            const afterReload = await snapshot(page);
            assert.equal(Object.values(afterReload.chairs).filter(({ state }) => state === "stored").length, 34);
            await page.close();
            return { fixture: "Placement at validated approach/stand anchors. Chair UI, state, mesh and camera exercised in actual R5.", chairs: result };
        });
        if (!onlyVR) await row("Real keyboard capsule traverses both fully occupied R5 aisles in both directions", async () => {
            const plan = JSON.parse(execFileSync(process.env.API_PYTHON || "python", ["experiments/p507-r5/layout_checks.py"],
                { cwd: root, encoding: "utf8" }));
            const page = await context.newPage();
            await page.goto(origin + "/tests/r5-walk.html?mode=p507-visit&revision=r5&evidence=1");
            await waitLoaded(page, hash);
            await page.waitForFunction(() => window.__P507_R5_TEST__ && window.__P507_M5__?.webPose);
            await page.evaluate(() => window.__P507_R5_TEST__.occupyAll());
            const fixture = await snapshot(page);
            assert.equal(Object.values(fixture.chairs).filter(({ state }) => state === "occupied").length, 34);
            assert.equal(fixture.seated, undefined);
            const camera = page.locator("canvas").first();
            const west = 1.10, east = manifest.layout.walkable_rect[2] - .40;
            const stop = async (key, threshold, increasing) => {
                await page.keyboard.down(key);
                try {
                    await page.waitForFunction(({ threshold, increasing }) => {
                        const { x } = window.__P507_M5__.webPose;
                        return increasing ? x >= threshold : x <= threshold;
                    }, { threshold, increasing }, { timeout: 100000 });
                } finally {
                    await page.keyboard.up(key);
                }
                return page.evaluate(() => window.__P507_M5__.webPose);
            };
            const travelled = [];
            for (const [aisle, geometry] of Object.entries(plan.aisles.occupied)) {
                assert.ok(geometry.width_m >= .90);
                const z = -(geometry.north_edge.y_m + geometry.south_edge.y_m) / 2;
                await page.evaluate(({ west, z }) => window.__P507_R5_TEST__.place([west, z], -Math.PI / 2), { west, z });
                await camera.focus();
                const eastPose = await stop("w", east - .05, true);
                const westPose = await stop("s", west + .05, false);
                closeEnough([eastPose.z], [z]);
                closeEnough([westPose.z], [z]);
                travelled.push({ aisle, measuredWidth: geometry.width_m, start: [west, z], eastPose, westPose });
                await page.screenshot({ path: resolve(out, "r5-aisle-" + aisle + ".png") });
            }
            await page.close();
            return { fixture: "All 34 synthetic seated envelopes active; place at west aisle entry only; travel via W/S and capsule.", travelled };
        });
        if (!onlyVR) await row("IWER AR tabletop hit test, actual chair ray and adjustment", async () => {
            const page = await context.newPage();
            await page.goto(origin + iwer);
            await waitLoaded(page, hash);
            await page.getByRole("button", { name: "Vào AR" }).click();
            await page.evaluate(() => window.iwer.device.quaternion.set(-Math.sin(.35), 0, 0, Math.cos(.35)));
            await event(page, "ar:surface");
            await aim(page, [0, 1.45, 0], [0, .7, -1]);
            await trigger(page);
            await event(page, "ar:placed");
            await page.evaluate(() => window.iwer.device.quaternion.set(0, 0, 0, 1));
            const picker = page.getByLabel("Đối tượng P507");
            let chosen, before;
            for (const candidate of manifest.layout.chairs) {
                before = await bound(page, candidate.id);
                assert.ok(before);
                const [x, , z] = before.center;
                await aim(page, [x, 1.42, z], [x, before.max[1], z]);
                await trigger(page);
                if (await picker.inputValue() === candidate.id) { chosen = candidate; break; }
            }
            assert.ok(chosen, "actual R5 tabletop ray must resolve a chair");
            const actionButton = [-.311, 1.806, -1.35];
            await aim(page, [0, 1.65, 0], actionButton);
            await trigger(page);
            await event(page, "chair:pull:" + chosen.id);
            await page.waitForFunction(id => window.__P507_M5__?.snapshotR5?.().chairs[id]?.state === "pulled-out", chosen.id);
            const after = await bound(page, chosen.id);
            closeEnough(after.center, before.center.map((v, i) =>
                v + [.08 * (chosen.pulled[0] - chosen.stored[0]), 0, -.08 * (chosen.pulled[1] - chosen.stored[1])][i]));
            await aim(page, [0, 1.65, 0], actionButton);
            await trigger(page);
            await event(page, "chair:store:" + chosen.id);
            await page.waitForFunction(id => window.__P507_M5__?.snapshotR5?.().chairs[id]?.state === "stored", chosen.id);
            await page.screenshot({ path: resolve(out, "r5-ar.png") });
            await page.evaluate(() => window.iwer.device.activeSession.end());
            await event(page, "session:ended:immersive-ar");
            assert.equal((await snapshot(page)).moving, undefined);
            await page.close();
            return { id: chosen.id, source: "R5 GLB actual controller ray", before, pulled: after };
        });
        await row("IWER VR controller selects and seats in real R5, preserves tracking, and re-enters", async () => {
            const page = await context.newPage();
            await page.goto(origin + "/tests/r5-walk.html?mode=p507-visit&revision=r5&evidence=1");
            await waitLoaded(page, hash);
            await page.getByRole("button", { name: "Vào VR" }).click();
            await event(page, "session:active:immersive-vr");
            await page.evaluate(() => { window.iwer.device.position.x = -2; });
            await event(page, "physical-boundary:ROOM_BOUNDARY_OUTSIDE_UNSURVEYED");
            await page.evaluate(() => { window.iwer.device.position.x = 0; });
            await event(page, "physical-boundary:clear");
            await page.waitForFunction(() => window.__P507_R5_VR_TEST__);
            const point = ([x, y]) => [x, -y];
            const place = anchor => page.evaluate(anchor => window.__P507_R5_VR_TEST__.place(anchor), point(anchor));
            const tracker = () => page.evaluate(() => window.__P507_R5_VR_TEST__.tracker());
            const panelAction = async index => {
                const [position, target] = await page.evaluate(index => {
                    const test = window.__P507_R5_VR_TEST__;
                    return [test.tracker().reference, test.actionTarget(index)];
                }, index);
                await aim(page, position, target);
                await trigger(page);
            };
            const chair = manifest.layout.chairs.find(chair => chair.id === "P507-CHAIR-A-07");
            assert.ok(chair);
            const validApproach = await page.evaluate(choices =>
                choices.find(([x, y]) => window.__P507_R5_VR_TEST__.valid([x, -y])),
            [chair.approach, ...chair.approach_alternatives]);
            assert.ok(validApproach, "VR approach checkpoint");
            await place(validApproach);
            const bounds = await bound(page, chair.id);
            const [x, , z] = bounds.center;
            const [source, target] = await page.evaluate(({ x, z, top }) => {
                const test = window.__P507_R5_VR_TEST__;
                return [[x, 1.6, z], [x, top - .1, z]].map(point => test.toReference(point));
            }, { x, z, top: bounds.max[1] });
            await aim(page, source, target);
            await trigger(page);
            await event(page, "select:" + chair.id);
            await panelAction(0);
            await event(page, "chair:pull:" + chair.id);
            await page.waitForFunction(id => window.__P507_M5__?.snapshotR5?.().chairs[id]?.state === "pulled-out", chair.id);
            await place(chair.stand);
            await page.evaluate(() => {
                const yaw = .35;
                window.iwer.device.quaternion.set(0, Math.sin(yaw / 2), 0, Math.cos(yaw / 2));
            });
            const standingBefore = await tracker();
            await panelAction(0);
            await event(page, "chair:sit:" + chair.id);
            await page.waitForFunction(id => window.__P507_M5__?.snapshotR5?.().seated === id, chair.id);
            const seated = await tracker();
            closeEnough(seated.world, [chair.seat_eye[0], chair.seat_eye[2], -chair.seat_eye[1]]);
            closeEnough(seated.reference, standingBefore.reference);
            const expectedYaw = chair.orientation_deg * Math.PI / 180 - .35;
            assert.ok(Math.abs(Math.sin(seated.originYaw - expectedYaw)) < .005 &&
                Math.cos(seated.originYaw - expectedYaw) > .99, "seat yaw must compensate tracked head yaw once");
            await page.evaluate(async () => {
                const controller = window.iwer.device.controllers.right;
                controller.updateAxes("thumbstick", 0, -1);
                for (let i = 0; i < 8; i++) {
                    await new Promise(done => window.iwer.device.activeSession.requestAnimationFrame(done));
                }
                controller.updateAxes("thumbstick", 0, 0);
            });
            closeEnough((await tracker()).world, seated.world);
            await page.screenshot({ path: resolve(out, "r5-vr-seated.png") });
            await panelAction(0);
            await event(page, "chair:stand:" + chair.id);
            await page.waitForFunction(id => window.__P507_M5__?.snapshotR5?.().chairs[id]?.state === "pulled-out", chair.id);
            const standingAfter = await tracker();
            closeEnough(standingAfter.world, [chair.stand[0], standingBefore.reference[1], -chair.stand[1]]);
            await page.screenshot({ path: resolve(out, "r5-vr.png") });
            await page.evaluate(() => window.iwer.device.activeSession.end());
            await event(page, "session:ended:immersive-vr");
            await page.getByRole("button", { name: "Vào VR" }).click();
            await page.waitForFunction(() => window.iwer.logs.filter(entry => entry.mode === "immersive-vr").length === 2);
            await page.evaluate(() => window.iwer.device.activeSession.end());
            await page.close();
            return { room: "R5", runtime: "IWER", boundary: "ROOM_BOUNDARY_OUTSIDE_UNSURVEYED", chair: chair.id, standingBefore, seated, standingAfter, locomotionLocked: true };
        });
    }
    report.result = "PASS";
} catch (error) {
    report.error = error.stack;
    process.exitCode = 1;
} finally {
    await browser?.close();
    vite.kill();
    await writeFile(resolve(out, "report.json"), JSON.stringify(report, null, 2) + "\n");
    console.log(JSON.stringify(report, null, 2));
}
