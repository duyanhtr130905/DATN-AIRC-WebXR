import assert from "node:assert/strict";
import { spawn, spawnSync } from "node:child_process";
import { existsSync } from "node:fs";
import { mkdir, readFile, writeFile } from "node:fs/promises";
import { resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { chromium } from "playwright";

const root = fileURLToPath(new URL("../../..", import.meta.url));
const out = resolve(root, ".local/m3-admin-browser");
const mapping = JSON.parse(await readFile(resolve(root, "apps/web/src/app/p507-mapping.json")));
const origin = "http://127.0.0.1:5173";
const fixture = process.env.M3_TEST_LOGIN;
assert.ok(fixture, "Ephemeral fixture account required");
const { M3_TEST_LOGIN, ...frontendEnv } = process.env;
const frontend = spawn(process.execPath, [
    resolve(root, "apps/web/node_modules/vite/bin/vite.js"), "--port", "5173", "--strictPort",
], { cwd: resolve(root, "apps/web"), windowsHide: true, stdio: "ignore",
    env: { ...frontendEnv, API_PROXY_TARGET: `http://127.0.0.1:${process.env.API_PORT}` } });
const report = { status: "FAIL", samples: [], frozen: process.env.M3_REQUIRE_FROZEN === "1",
    build: spawnSync("git", ["rev-parse", "HEAD"], { cwd: root, encoding: "utf8", windowsHide: true }).stdout.trim() };
await mkdir(out, { recursive: true });
let browser;
try {
    for (let attempt = 0; ; attempt++) {
        assert.equal(frontend.exitCode, null, "Vite exited");
        if (await fetch(origin).then(response => response.ok).catch(() => false)) break;
        assert.ok(attempt < 60, "Vite unavailable");
        await new Promise(done => setTimeout(done, 250));
    }
    const executablePath = process.env.CHROME_BIN || [
        "C:/Program Files/Google/Chrome/Application/chrome.exe", "/usr/bin/google-chrome",
    ].find(existsSync);
    assert.ok(executablePath, "Chrome required");
    browser = await chromium.launch({ executablePath, args: ["--use-angle=swiftshader", "--enable-unsafe-swiftshader"] });
    report.chrome = browser.version();
    const page = await browser.newPage({ viewport: { width: 1440, height: 1100 }, timezoneId: "UTC" });
    page.setDefaultTimeout(20000);
    const frames = [];
    page.on("websocket", socket => {
        if (socket.url().endsWith("/ws/v1/admin/p507")) socket.on("framereceived", ({ payload }) => {
            const message = JSON.parse(payload);
            if (message.type === "admin.invalidate") frames.push({ ...message, received_ms: Date.now() });
        });
    });
    await page.goto(origin + "/?mode=admin");
    await page.getByLabel("Tên đăng nhập").fill("qa_operator");
    await page.getByLabel("Mật khẩu", { exact: true }).fill(fixture);
    await page.getByRole("button", { name: "Đăng nhập" }).click();
    await page.getByTestId("admin-sync").filter({ hasText: "CONNECTED" }).waitFor();
    await page.evaluate(room => {
        const url = new URL("/ws/v1/state", location.href);
        url.protocol = "ws:";
        url.searchParams.set("room_id", room);
        url.searchParams.set("protocol", "2");
        window.publicFrames = [];
        window.publicProbe = new WebSocket(url);
        window.publicProbe.onmessage = event => window.publicFrames.push(JSON.parse(event.data));
    }, mapping.room_id);
    await page.waitForFunction(() => window.publicFrames.some(frame => frame.type === "snapshot.end"));
    const picker = page.getByLabel("Đối tượng", { exact: true });
    assert.equal(await picker.locator("option").count(), 122);
    if (report.frozen) {
        await page.locator("canvas").waitFor({ timeout: 40000 });
        const box = await page.locator("canvas").boundingBox();
        for (const y of [0.5, 0.65, 0.35, 0.8, 0.2]) {
            await page.mouse.click(box.x + box.width * 0.5, box.y + box.height * y);
            if (await picker.inputValue()) break;
        }
        report.mesh = await picker.inputValue();
        assert.ok(Object.values(mapping.objects).includes(report.mesh));
    } else await page.getByRole("alert").filter({ hasText: "asset R4" }).waitFor();
    const panel = page.getByTestId("admin-panel");
    const catalog = page.locator("form").filter({ has: page.getByRole("button", { name: "Lưu danh mục" }) });
    await picker.selectOption("");
    await catalog.getByLabel("Tên", { exact: true }).fill("Synthetic inventory item");
    await catalog.getByLabel("Loại", { exact: true }).fill("fixture");
    await catalog.getByLabel("Nhóm", { exact: true }).fill("test");
    await catalog.getByRole("button", { name: "Lưu danh mục" }).click();
    await panel.getByRole("heading", { name: "Synthetic inventory item" }).waitFor();
    assert.match(await panel.innerText(), /NOT_MODELED/);
    const created = await picker.inputValue();
    assert.equal((await fetch(origin + "/api/v1/objects/" + created)).status, 404);
    const target = report.mesh || Object.values(mapping.objects)[0];
    await picker.selectOption(target);
    await catalog.getByLabel("Tên", { exact: true }).fill("Private synthetic test label");
    await catalog.getByRole("button", { name: "Lưu danh mục" }).click();
    await panel.getByRole("heading", { name: "Private synthetic test label" }).waitFor();
    assert.match(await panel.innerText(), new RegExp(target));
    await panel.screenshot({ path: resolve(out, "panel-before.png") });

    for (const [index, type] of ["equipment_status", "exhibit_info", "room_schedule"].entries()) {
        const form = page.getByRole("form", { name: type });
        if (type === "equipment_status") await form.getByLabel("Trạng thái").selectOption("maintenance");
        if (type === "exhibit_info") await form.getByLabel("Tiêu đề").fill("Synthetic exhibit revision");
        if (type === "room_schedule") await form.getByLabel("Hoạt động").fill("Synthetic schedule activity");
        const observed = new Date(Date.now() - 1000).toISOString().slice(0, 19);
        await form.locator("input[type=datetime-local]").fill(observed);
        const accepted = page.waitForResponse(response => response.url().endsWith("/api/v1/admin/p507/state") && response.request().method() === "PUT" && response.ok());
        const start_ms = Date.now();
        await form.getByRole("button", { name: "Lưu quan sát" }).click();
        const container = type === "room_schedule" ? page.getByTestId("admin-schedule") : panel;
        const state = container.locator(`[data-state-type="${type}"][data-version="1"]`);
        await state.waitFor();
        const applied_ms = Date.now();
        const persisted = await (await accepted).json();
        assert.equal(persisted.sequence, index + 1);
        assert.equal(persisted.state.state_type, type);
        assert.match(await state.innerText(), /qa_operator/);
        const frame = frames.find(frame => frame.sequence === index + 1);
        assert.ok(frame, "Authoritative room invalidation must reach Chrome");
        report.samples.push({
            ...frame, state_type: type, version: persisted.state.version,
            target_id: persisted.state.target_id, observed_at: persisted.state.source_observed_at,
            db_recorded_at: persisted.state.committed_at, start_ms, applied_ms,
        });
    }
    const publicFrames = await page.evaluate(() => {
        window.publicProbe.close();
        return window.publicFrames;
    });
    assert.ok(publicFrames.every(frame => frame.type !== "state.updated" && (frame.sequence ?? 0) === 0));
    assert.doesNotMatch(JSON.stringify(publicFrames), /qa_operator|Synthetic exhibit revision/);
    report.publicFrames = publicFrames.map(frame => ({ type: frame.type, sequence: frame.sequence }));
    const publicStates = await (await fetch(origin + `/api/v1/rooms/${mapping.room_id}/states`)).json();
    assert.deepEqual(publicStates.data, []);
    assert.doesNotMatch(await (await fetch(origin + "/api/v1/objects/" + target)).text(), /Private synthetic test label/);
    await panel.screenshot({ path: resolve(out, "panel-after.png") });
    await page.getByTestId("admin-schedule").locator("[data-state-type=room_schedule]").screenshot({ path: resolve(out, "panel-schedule.png") });
    await page.getByRole("button", { name: "Đăng xuất" }).click();
    await page.getByRole("heading", { name: "Đăng nhập quản trị P507" }).waitFor();
    assert.equal(await page.evaluate(async () => (await fetch("/api/v1/admin/p507")).status), 401);
    report.status = "PASS";
} finally {
    await browser?.close();
    frontend.kill();
    await writeFile(resolve(out, "report.json"), JSON.stringify(report, null, 2));
}
