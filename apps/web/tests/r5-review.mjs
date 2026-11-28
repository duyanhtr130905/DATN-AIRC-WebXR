import assert from "node:assert/strict";
import { execFileSync, spawn } from "node:child_process";
import { existsSync } from "node:fs";
import { mkdir, readFile, writeFile } from "node:fs/promises";
import { createServer } from "node:net";
import { platform, release, cpus } from "node:os";
import { resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { chromium } from "playwright";

const root = fileURLToPath(new URL("../../..", import.meta.url));
const web = resolve(root, "apps/web");
const out = resolve(root, ".local/p507-r5", "review-" + new Date().toISOString().replaceAll(":", "-"));
const bin = process.env.CHROME_BIN || [
    "C:/Program Files/Google/Chrome/Application/chrome.exe", "/usr/bin/google-chrome", "/usr/bin/chromium",
].find(existsSync);
assert.ok(bin, "Set CHROME_BIN to the installed Chrome executable");
await mkdir(out, { recursive: true });

const port = await new Promise((resolvePort, reject) => {
    const reservation = createServer();
    reservation.once("error", reject);
    reservation.listen(0, "127.0.0.1", () => {
        const { port } = reservation.address();
        reservation.close(error => error ? reject(error) : resolvePort(port));
    });
});
const origin = `http://127.0.0.1:${port}`;
const vite = spawn(process.execPath, [
    resolve(web, "node_modules/vite/bin/vite.js"), "--host", "127.0.0.1", "--port", String(port), "--strictPort",
], { cwd: web, windowsHide: true, stdio: ["ignore", "pipe", "pipe"] });
let logs = "";
for (const stream of [vite.stdout, vite.stderr]) stream.on("data", chunk => { logs += chunk; });
const report = {
    result: "FAIL",
    head: execFileSync("git", ["rev-parse", "HEAD"], { cwd: root, encoding: "utf8" }).trim(),
    trackedChanges: Boolean(execFileSync("git", ["status", "--porcelain", "--untracked-files=no"], { cwd: root, encoding: "utf8" }).trim()),
    environment: { os: platform() + " " + release(), cpu: cpus()[0]?.model, rendererMode: "ANGLE SwiftShader" },
    protocol: {
        revisions: ["r4", "r5"], viewport: [1440, 960], dpr: 1, mode: "fixed camera at utility zone",
        warmupMs: 2000, sampleMs: 10000, repetitions: 3, physicalDevices: "NOT RUN",
        comparison: "Same renderer and FOV presets; geometry-relative poses, no pixel alignment claimed",
    },
    revisions: {},
};
let browser;
try {
    await new Promise((ready, reject) => {
        const timeout = setTimeout(() => reject(new Error("Vite did not start")), 30000);
        const finish = error => { clearTimeout(timeout); error ? reject(error) : ready(); };
        vite.once("error", finish);
        vite.once("exit", code => finish(new Error(`Vite exited with ${code}`)));
        vite.stdout.on("data", () => { if (logs.includes("127.0.0.1:")) finish(); });
    });
    browser = await chromium.launch({ headless: true, executablePath: bin, args: [
        "--use-gl=angle", "--use-angle=swiftshader", "--enable-webgl", "--enable-unsafe-swiftshader",
    ] });
    report.environment.browser = browser.version();
    for (const revision of report.protocol.revisions) {
        const context = await browser.newContext({ viewport: { width: 1440, height: 960 }, deviceScaleFactor: 1 });
        const page = await context.newPage();
        const errors = [];
        page.on("pageerror", error => errors.push(error.message));
        const evidence = report.revisions[revision] = { shots: [], timing: [], errors };
        const url = `${origin}/p507-r5-review.html?revision=${revision}`;
        try {
            await page.goto(url);
            try {
                await page.locator(`#status[data-loaded="${revision}"]`).waitFor({ timeout: 65000 });
            } catch (error) {
                throw new Error(`Unable to load ${revision}: ${await page.locator("#status").textContent()}`, { cause: error });
            }
            const poses = await page.evaluate(() => window.__P507_R5_REVIEW__.poses);
            assert(poses.length >= 13);
            for (const [index, key] of poses.entries()) {
                const pose = await page.evaluate(key => {
                    const preview = window.__P507_R5_REVIEW__;
                    preview.aim(key);
                    return preview.snapshot();
                }, key);
                const file = `${revision}-${String(index + 1).padStart(2, "0")}.png`;
                await page.screenshot({ path: resolve(out, file) });
                evidence.shots.push({ file, pose });
            }
            await page.evaluate(() => window.__P507_R5_REVIEW__.aim("Khu tiện ích"));
            const { warmupMs, sampleMs, repetitions } = report.protocol;
            for (let index = 0; index < repetitions; index++) {
                const timing = await page.evaluate(
                    ([warmup, duration]) => window.__P507_R5_REVIEW__.measure(warmup, duration), [warmupMs, sampleMs],
                );
                assert(timing.intervalsMs.length >= 10 && timing.durationMs >= sampleMs);
                evidence.timing.push(timing);
            }
            await page.setViewportSize({ width: 390, height: 844 });
            const pose = await page.evaluate(() => {
                const preview = window.__P507_R5_REVIEW__;
                preview.aim("Cửa sổ và poster");
                return preview.snapshot();
            });
            const file = `${revision}-mobile-390.png`;
            await page.screenshot({ path: resolve(out, file) });
            evidence.shots.push({ file, pose });
            assert.deepEqual(errors, []);
        } finally {
            await context.close();
        }
    }
    const gallery = await browser.newPage({ viewport: { width: 1200, height: 900 } });
    const pairs = await Promise.all(report.revisions.r4.shots.map(async ({ pose, file }, index) => ({
        name: pose.active + (file.includes("mobile") ? " · Mobile" : ""),
        images: await Promise.all([file, report.revisions.r5.shots[index].file].map(async image =>
            "data:image/png;base64," + (await readFile(resolve(out, image))).toString("base64"))),
    })));
    await gallery.setContent(`
        <meta charset="utf-8"><title>P507 R4 / R5</title>
        <style>
            body { margin: 32px; background: #17222a; color: #f3f6f6; font: 16px system-ui; }
            section { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; margin-bottom: 20px; }
            h2 { grid-column: span 2; margin: 0; font-size: 19px; }
            figure { margin: 0; padding: 8px; background: #2b3740; }
            img { width: 100%; height: 290px; object-fit: contain; display: block; }
            figcaption { padding: 6px 0 2px; }
        </style>
        <h1>P507 · R4 frozen / R5 proposal</h1>
        <main></main>`);
    await gallery.evaluate(async rows => {
        const target = document.querySelector("main");
        for (const row of rows) {
            const section = document.createElement("section");
            const heading = document.createElement("h2");
            heading.textContent = row.name;
            section.append(heading);
            await Promise.all(row.images.map(async (src, index) => {
                const figure = document.createElement("figure");
                const image = new Image();
                image.src = src;
                const caption = document.createElement("figcaption");
                caption.textContent = index === 0 ? "Frozen R4" : "R5 PROPOSAL / PROVISIONAL / SYNTHETIC / VIRTUAL ADAPTATION";
                figure.append(image, caption);
                section.append(figure);
                await image.decode();
            }));
            target.append(section);
        }
    }, pairs);
    await gallery.screenshot({ path: resolve(out, "contact-sheet.png"), fullPage: true });
    await gallery.close();
    report.result = "PASS";
} catch (error) {
    report.error = error.stack;
    throw error;
} finally {
    if (browser) await browser.close();
    vite.kill();
    await writeFile(resolve(out, "report.json"), JSON.stringify(report, null, 2) + "\n", { flag: "wx" });
    if (report.result !== "PASS") await writeFile(resolve(out, "vite.log"), logs, { flag: "wx" });
    console.log(out);
}
