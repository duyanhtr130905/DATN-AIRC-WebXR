import assert from "node:assert/strict";
import { spawn } from "node:child_process";
import { once } from "node:events";
import { mkdir, readFile, writeFile } from "node:fs/promises";
import { createServer } from "node:net";
import { resolve } from "node:path";
import { setTimeout as delay } from "node:timers/promises";
import { chromium } from "playwright";

const root = process.cwd();
const out = resolve(root, ".local/m4-visitor-browser");
const children = new Set();
const steps = [];
const storageKey = "airc.synthetic.visitor.v1";

async function port() {
    const server = createServer();
    server.listen(0, "127.0.0.1");
    await once(server, "listening");
    const value = server.address().port;
    await new Promise((resolve, reject) => server.close(error => error ? reject(error) : resolve()));
    return value;
}

function child(command, args, cwd, env) {
    const process = spawn(command, args, { cwd, env, stdio: "ignore", windowsHide: true });
    children.add(process);
    process.once("exit", () => children.delete(process));
    return process;
}

async function stop(process) {
    if (process.exitCode !== null || process.signalCode !== null) return;
    const exited = once(process, "exit");
    process.kill();
    await exited;
}

async function waitFor(check, reason, timeout = 15_000) {
    const deadline = Date.now() + timeout;
    while (Date.now() < deadline) {
        if (await check()) return;
        await delay(100);
    }
    throw new Error(reason);
}

async function ready(url) {
    await waitFor(async () => {
        try { return (await fetch(url, { signal: AbortSignal.timeout(500) })).ok; }
        catch { return false; }
    }, "Local service did not become ready");
}

const apiPort = await port();
const webPort = await port();
const origin = `http://127.0.0.1:${webPort}`;
const apiOrigin = `http://127.0.0.1:${apiPort}`;
const startApi = () => child(process.env.API_PYTHON, [
    "-m", "uvicorn", "app.main:create_app", "--factory", "--host", "127.0.0.1",
    "--port", String(apiPort), "--no-proxy-headers", "--no-access-log",
], resolve(root, "apps/api"), {
    ...process.env,
    ADMIN_ENABLED: "true", ADMIN_ORIGIN: origin, VISITOR_SYNTHETIC_ENABLED: "true",
    REALTIME_DISPATCHER_ENABLED: "false", CORS_ORIGINS: origin,
});
const path = origin + "/?mode=offline";
const active = page => page.getByTestId("visitor-session");
const button = (page, name) => page.getByRole("button", { name, exact: true });
const stored = page => page.evaluate(key => JSON.parse(localStorage.getItem(key)), storageKey);
const has = async (page, text) => (await active(page).textContent({ timeout: 500 })).includes(text);
const waitQueue = async (page, count) => waitFor(
    async () => (await stored(page))?.queue.length === count, `Expected ${count} queued events`,
);
let browser;

try {
    let api = startApi();
    child(process.execPath, [resolve(root, "apps/web/node_modules/vite/bin/vite.js"),
        "--port", String(webPort), "--strictPort"], resolve(root, "apps/web"), {
        ...process.env, API_PROXY_TARGET: apiOrigin,
    });
    await Promise.all([ready(apiOrigin + "/api/ready"), ready(origin)]);
    browser = await chromium.launch({
        executablePath: process.env.CHROME_BIN || "/usr/bin/google-chrome",
        args: ["--use-angle=swiftshader", "--enable-unsafe-swiftshader"],
    });
    const context = await browser.newContext({ acceptDownloads: true });
    const page = await context.newPage();
    const requests = [];
    const trackRequests = request => {
        if (request.url().includes("/api/v1/visitor/sessions") && request.method() === "POST") {
            requests.push(request.url());
        }
    };
    context.on("request", trackRequests);
    await page.goto(path);
    await button(page, "Đồng ý ghi phiên mô phỏng").waitFor();
    await page.getByRole("button", { name: /Khối mẫu A/ }).click();
    assert.equal(requests.length, 0);
    assert.equal(await stored(page), null);
    steps.push("browse without opt-in produces no visitor writes or storage");

    await button(page, "Đồng ý ghi phiên mô phỏng").click();
    await active(page).waitFor();
    await waitQueue(page, 0);
    const original = (await stored(page)).view.id;
    const proof = (await context.cookies()).find(cookie => cookie.name === "airc_visitor");
    assert.equal(proof.httpOnly, true);
    assert.equal(proof.sameSite, "Strict");
    assert.ok(!(await page.evaluate(() => document.cookie)).includes("airc_visitor"));
    const other = await context.newPage();
    await other.goto(path);
    await active(other).waitFor();
    assert.equal((await stored(other)).view.id, original);

    await context.setOffline(true);
    await Promise.all([
        page.getByRole("button", { name: /Khối mẫu B/ }).click(),
        other.getByRole("button", { name: /Khối mẫu A/ }).click(),
    ]);
    await waitQueue(page, 2);
    const queued = (await stored(page)).queue;
    assert.equal(new Set(queued.map(event => event.id)).size, 2);
    steps.push("two tabs share one session and preserve both IDs while Chrome is offline");

    let servedAndDropped = false;
    let retryIds;
    const pattern = "**/api/v1/visitor/sessions/**";
    await context.route(pattern, async route => {
        if (!servedAndDropped && route.request().method() === "POST") {
            const result = await route.fetch({ maxRetries: 0 });
            assert.equal(result.status(), 200);
            servedAndDropped = true;
        }
        await route.abort("connectionfailed");
    });
    await context.setOffline(false);
    await waitFor(() => servedAndDropped, "Browser did not send the offline queue after reconnect");
    await page.reload();
    await active(page).waitFor();
    assert.deepEqual((await stored(page)).queue.map(event => event.id), queued.map(event => event.id));
    assert.equal((await stored(page)).view.id, original);
    steps.push("response discarded after PostgreSQL commit; reload with visitor API unreachable retains IDs");

    await stop(api);
    api = startApi();
    await ready(apiOrigin + "/api/ready");
    // Either tab can win the shared network lock. Observe both before restoring the route.
    const duplicate = context.waitForEvent("response", async response => {
        if (!response.url().endsWith("/events") || !response.ok()) return false;
        const { receipts } = await response.json();
        if (!receipts.every(row => row.status === "duplicate")) return false;
        retryIds = receipts.map(row => row.id);
        return true;
    });
    await context.unroute(pattern);
    await button(page, "Thử đồng bộ lại").click();
    await duplicate;
    await waitQueue(page, 0);
    assert.deepEqual(retryIds, queued.map(event => event.id));
    const lastObject = queued.at(-1).object_id;
    const lastName = lastObject === "demo-object-cube" ? /Khối mẫu A/ : /Khối mẫu B/;
    assert.equal(await page.getByRole("button", { name: lastName }).getAttribute("aria-pressed"), "true");
    await button(page, "Ẩn thông tin").click();
    await button(page, "Mở thông tin").waitFor();
    await waitQueue(page, 0);
    await page.reload();
    await button(page, "Mở thông tin").waitFor();
    assert.equal((await stored(page)).view.id, original);
    await button(page, "Mở thông tin").click();
    await button(page, "Ẩn thông tin").waitFor();
    await waitQueue(page, 0);
    steps.push("API process restarted; duplicate receipts accepted, room selection and info panel restored");

    const unavailable = await browser.newContext();
    await unavailable.addInitScript(() => {
        Object.defineProperty(window, "localStorage", { get() { throw new Error("blocked"); } });
    });
    const denied = await unavailable.newPage();
    await denied.goto(path);
    await denied.getByText("Bộ nhớ trình duyệt không khả dụng.", { exact: false }).waitFor();
    await denied.getByRole("button", { name: /Khối mẫu A/ }).click();
    assert.equal(await button(denied, "Đồng ý ghi phiên mô phỏng").count(), 0);
    await unavailable.close();
    steps.push("storage-denied browser retains scene interaction without tracking");

    await button(page, "Kết thúc phiên").click();
    await waitFor(() => has(page, "Đã kết thúc"), "Session did not end");
    await waitQueue(page, 0);
    const admin = await context.newPage();
    await admin.goto(origin + "/?mode=admin");
    await admin.getByLabel("Tên đăng nhập").fill("visitor_qa");
    await admin.getByLabel("Mật khẩu").fill(process.env.M4_TEST_OPERATOR_PASSWORD);
    await button(admin, "Đăng nhập").click();
    await button(admin, "Báo cáo phiên mô phỏng").click();
    const totals = admin.getByTestId("visitor-totals");
    await totals.waitFor();
    assert.match(await totals.textContent(), /^1 phiên · 7 sự kiện$/);
    await mkdir(out, { recursive: true });
    for (const [format, name] of [["csv", "Xuất CSV"], ["json", "Xuất JSON"]]) {
        const pending = admin.waitForEvent("download");
        await button(admin, name).click();
        const download = await pending;
        assert.equal(download.suggestedFilename(), `synthetic-local-sessions.${format}`);
        const body = await readFile(await download.path(), "utf8");
        assert.ok(body.includes(original));
        if (format === "json") {
            const data = JSON.parse(body);
            assert.equal(data.scope, "synthetic_local");
            assert.equal(data.events.length, 7);
            assert.equal(new Set(data.events.map(event => event.event_id)).size, 7);
        } else assert.equal(body.trim().split("\r\n").length, 8);
    }
    await admin.screenshot({ path: resolve(out, "admin-report.png") });
    steps.push("named Admin reports and downloads matching CSV and JSON from Chrome");

    await context.setOffline(true);
    await button(page, "Dừng ghi và xóa phiên").click();
    await waitFor(async () => (await stored(other))?.clearing, "Other tab did not observe withdrawal");
    assert.deepEqual((await stored(page)).queue, []);
    await context.setOffline(false);
    await waitFor(async () => (await stored(other)) === null, "Cleanup did not complete");
    await other.reload();
    await button(other, "Đồng ý ghi phiên mô phỏng").waitFor();
    assert.equal((await context.cookies()).some(cookie => cookie.name === "airc_visitor"), false);
    steps.push("offline withdrawal clears queue in both tabs and deletes data on reconnect");

    await writeFile(resolve(out, "report.json"), JSON.stringify({
        status: "PASS", chrome: browser.version(), node: process.version,
        code_sha: process.env.M4_TEST_SHA, steps,
    }, null, 2));
} finally {
    if (browser) await browser.close();
    await Promise.all([...children].map(stop));
}
