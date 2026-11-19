import assert from "node:assert/strict";
import { spawn, spawnSync } from "node:child_process";
import { existsSync } from "node:fs";
import { mkdir, readFile, writeFile } from "node:fs/promises";
import { resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { chromium } from "playwright";

const root = fileURLToPath(new URL("../../..", import.meta.url));
const output = resolve(root, ".local/m3-browser");
const mapping = JSON.parse(await readFile(resolve(root, "apps/web/src/app/p507-mapping.json")));
const database = new URL(process.env.DATABASE_URL.replace("postgresql+psycopg:", "postgresql:")).pathname.slice(1);
assert.match(database, /^airc_test_catalog_[0-9a-f]{32}$/);
const assetExpected = process.env.M3_REQUIRE_FROZEN === "1";
const origin = "http://127.0.0.1:5173";
const report = {
    status: "FAIL", scope: "PROVISIONAL / SYNTHETIC",
    build: spawnSync("git", ["rev-parse", "HEAD"], { cwd: root, encoding: "utf8", windowsHide: true }).stdout.trim(),
    assetExpected, samples: [],
};
await mkdir(output, { recursive: true });
const frontend = spawn(process.execPath, [
    resolve(root, "apps/web/node_modules/vite/bin/vite.js"), "--host", "127.0.0.1",
    "--port", "5173", "--strictPort",
], {
    cwd: resolve(root, "apps/web"), windowsHide: true, stdio: "ignore",
    env: { ...process.env, DATABASE_URL: "", API_PROXY_TARGET: `http://127.0.0.1:${process.env.API_PORT}`, VITE_TEST_DIAGNOSTICS: "1" },
});
let browser;
try {
    for (let attempt = 0; ; attempt++) {
        assert.equal(frontend.exitCode, null, "Dedicated Vite exited");
        if (await fetch(origin).then(response => response.ok).catch(() => false)) break;
        assert.ok(attempt < 60, "Vite unavailable");
        await new Promise(done => setTimeout(done, 250));
    }
    const executablePath = process.env.CHROME_BIN || [
        "C:/Program Files/Google/Chrome/Application/chrome.exe", "/usr/bin/google-chrome",
    ].find(existsSync);
    assert.ok(executablePath, "Installed Chrome required");
    browser = await chromium.launch({ executablePath, args: ["--use-angle=swiftshader", "--enable-unsafe-swiftshader"] });
    report.chrome = browser.version();
    const page = await browser.newPage();
    page.setDefaultTimeout(12000);
    const errors = [];
    page.on("pageerror", error => errors.push(error.message));
    await page.goto(origin + "/?mode=p507");
    const realtime = page.getByTestId("realtime");
    const connected = page.locator('[data-testid="realtime"][data-status="connected"]');
    await connected.waitFor();
    if (assetExpected) await page.locator("canvas").waitFor();
    else await page.getByRole("alert").filter({ hasText: "asset R4" }).waitFor();
    const picker = page.getByLabel("Đối tượng P507");
    const panel = page.getByTestId("object-panel");
    const schedule = page.getByTestId("schedule-panel");
    const ids = Object.keys(mapping.objects);
    assert.equal(await picker.locator("option").count(), 122);
    if (assetExpected) {
        const canvas = await page.locator("canvas").boundingBox();
        for (const fraction of [0.5, 0.65, 0.35, 0.8, 0.2]) {
            await page.mouse.click(canvas.x + canvas.width * 0.5, canvas.y + canvas.height * fraction);
            if (await picker.inputValue()) break;
        }
        const picked = await picker.inputValue();
        assert.ok(mapping.objects[picked], "Frozen mesh ray must select a known logical ID");
        assert.match(await panel.innerText(), new RegExp(mapping.objects[picked]));
        report.frozenMeshSelection = picked;
    }
    const [other, target] = [ids.at(0), ids.at(-1)];
    await picker.selectOption(target);
    assert.match(await panel.innerText(), new RegExp(mapping.objects[target]));
    assert.match(await panel.innerText(), /UNKNOWN/);
    await panel.screenshot({ path: resolve(output, "panel-before.png") });

    async function update(type, logical, expected, value, visiblePanel, expectedText) {
        const file = resolve(output, "observation.json");
        const observed = new Date().toISOString();
        await writeFile(file, JSON.stringify({
            state_type: type, logical_id: logical, expected_version: expected, observed_at: observed, value,
        }));
        const result = spawnSync(process.env.API_PYTHON, [
            "-m", "app.modules.p507_cli", "--confirm-database", database,
            "--authorize-synthetic", mapping.revision, "--observation", file,
        ], { cwd: resolve(root, "apps/api"), encoding: "utf8", windowsHide: true, timeout: 10000 });
        assert.equal(result.status, 0, "Guarded ingest failed");
        const row = JSON.parse(result.stdout);
        const route = logical ? `objects/${mapping.objects[logical]}` : `rooms/${mapping.room_id}`;
        const response = await fetch(`${origin}/api/v1/${route}/states`);
        assert.ok(response.ok);
        const table = await response.json();
        assert.ok(table.data.some(state => state.id === row.state.id && state.version === expected + 1));
        const events = await page.waitForFunction(sequence => {
            const trace = window.__AIRC_TEST__.events;
            const receive = trace.find(event => event.kind === "received" && event.sequence === sequence && event.type === "state.updated");
            const render = trace.find(event => event.kind === "react.applied" && event.sequence === sequence);
            return receive && render ? { receive, render, timeOrigin: performance.timeOrigin } : null;
        }, row.sequence).then(handle => handle.jsonValue());
        assert.ok(events.render.at >= events.receive.at);
        assert.match(await visiblePanel.innerText(), expectedText);
        report.samples.push({ type, logical, observed, ...row, ...events });
    }

    await update("room_schedule", null, 0, { status: "free", activity: "Synthetic schedule" }, schedule, /free/);
    await update("room_schedule", null, 1, { status: "occupied", activity: "Synthetic class" }, schedule, /occupied/);
    await update("equipment_status", target, 0, { status: "available" }, panel, /available/);
    await update("equipment_status", target, 1, { status: "maintenance" }, panel, /maintenance/);
    await update("equipment_status", target, 2, { status: "offline" }, panel, /offline/);
    await update("equipment_status", other, 0, { status: "available" }, panel, /offline/);
    assert.doesNotMatch(await panel.innerText(), /status: available/);
    await update("exhibit_info", target, 0, { title: "Synthetic exhibit A", text: "Fixture" }, panel, /exhibit A/);
    await update("exhibit_info", target, 1, { title: "Synthetic exhibit B", text: "Revised fixture" }, panel, /exhibit B/);
    await panel.screenshot({ path: resolve(output, "panel-after.png") });

    await page.evaluate(() => {
        const probe = window.__AIRC_TEST__;
        probe.inject(probe.lastDelta);
        probe.inject({ ...probe.lastDelta, sequence: probe.lastDelta.sequence - 1 });
        probe.inject({ ...probe.lastDelta, sequence: probe.lastDelta.sequence + 2 });
    });
    await page.waitForFunction(() => window.__AIRC_TEST__.events.some(event => event.status === "resync_required"));
    await connected.waitFor();
    await page.evaluate(() => window.__AIRC_TEST__.disconnect());
    await page.waitForFunction(() => window.__AIRC_TEST__.events.some(event => event.status === "stale"));
    await connected.waitFor();
    assert.match(await panel.innerText(), /exhibit B/);
    assert.match(await realtime.innerText(), /connected/);
    assert.deepEqual(errors, []);
    report.recovery = await page.evaluate(() => window.__AIRC_TEST__.events.filter(event => event.kind === "connection"));
    report.mapping = { placed: 121, matched: ids.length, unmatched: 0, duplicate: 0, revision: mapping.revision };
    report.status = "PASS";
} finally {
    await browser?.close();
    frontend.kill();
    await writeFile(resolve(output, "report.json"), JSON.stringify(report, null, 2));
}
