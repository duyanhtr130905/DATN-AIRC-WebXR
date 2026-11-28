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
                preview.aim("Cửa sổ và rèm");
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
    const oldEvidence = resolve(root, ".local/p507-r5/P507-R5-80b5d6f5e496-evidence");
    const oldMapping = {
        "Mặt bằng": "neutral-review/r5-01.png",
        "Ba cụm bàn": "neutral-review/r5-02.png",
        "Cụm A": "neutral-review/r5-03.png",
        "Cụm B": "neutral-review/r5-04.png",
        "Cụm C": "neutral-review/r5-05.png",
        "TV, đồng hồ và poster": "neutral-review/r5-06.png",
        "Kệ bốn tầng và bình nước": "neutral-review/r5-07.png",
        "Khu tiện ích": "neutral-review/r5-08.png",
        "Cửa sổ và rèm": "neutral-review/r5-09.png",
        "Tường khung ảnh": "neutral-review/r5-10.png",
        "Tường logo": "neutral-review/r5-11.png",
        "Trần và ánh sáng": "neutral-review/r5-12.png",
        "Lối A-B ghế kéo ra": "runtime/r5-aisle-A-B.png",
        "Lối B-C ghế kéo ra": "runtime/r5-aisle-B-C.png",
        "Cửa mở ra ngoài": "neutral-review/r5-13.png",
        "Cửa đóng": "neutral-review/r5-14.png",
        "Cửa sổ và rèm · Mobile": "neutral-review/r5-mobile-390.png",
    };
    const gallery = await browser.newPage({ viewport: { width: 1440, height: 900 } });
    const pairs = await Promise.all(report.revisions.r4.shots.map(async ({ pose, file }, index) => {
        const label = pose.active + (file.includes("mobile") ? " · Mobile" : "");
        const oldRel = oldMapping[label];
        const oldPath = oldRel ? resolve(oldEvidence, oldRel) : null;
        const oldSrc = oldPath && existsSync(oldPath)
            ? "data:image/png;base64," + (await readFile(oldPath)).toString("base64")
            : null;
        const [r4Src, r5Src] = await Promise.all([file, report.revisions.r5.shots[index].file].map(async image =>
            "data:image/png;base64," + (await readFile(resolve(out, image))).toString("base64")));
        return { name: label, images: [r4Src, oldSrc, r5Src] };
    }));
    await gallery.setContent(`
        <meta charset="utf-8"><title>P507 R4 / R5 cũ / R5 compact</title>
        <style>
            body { margin: 24px; background: #17222a; color: #f3f6f6; font: 15px system-ui; }
            section { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 12px; margin-bottom: 18px; }
            h2 { grid-column: span 3; margin: 0; font-size: 18px; }
            figure { margin: 0; padding: 8px; background: #2b3740; display: flex; flex-direction: column; }
            img { width: 100%; height: 240px; object-fit: contain; display: block; }
            .absent { height: 240px; display: grid; place-items: center; color: #9fb0bd; border: 1px dashed #4a5a66; font-size: 13px; text-align: center; padding: 8px; }
            figcaption { padding: 6px 0 2px; font-size: 13px; }
        </style>
        <h1>P507 · Đối chiếu Frozen R4 (6,90×9,315) / R5 cũ 80b5d6f (8,63×15,55) / R5 compact mới (7,26×10,76)</h1>
        <main></main>`);
    await gallery.evaluate(async rows => {
        const captions = [
            "Frozen R4 (6,90 × 9,315 × 3,50 m)",
            "R5 cũ 80b5d6f (8,63 × 15,55 × 3,50 m)",
            "R5 compact mới (7,26 × 10,76 × 3,50 m)",
        ];
        const target = document.querySelector("main");
        for (const row of rows) {
            const section = document.createElement("section");
            const heading = document.createElement("h2");
            heading.textContent = row.name;
            section.append(heading);
            const figures = await Promise.all(row.images.map(async (src, index) => {
                const figure = document.createElement("figure");
                if (src) {
                    const image = new Image();
                    image.src = src;
                    figure.append(image);
                    await image.decode();
                } else {
                    const placeholder = document.createElement("div");
                    placeholder.className = "absent";
                    placeholder.textContent = "Không có góc chụp tương ứng trong snapshot R5 cũ (80b5d6f)";
                    figure.append(placeholder);
                }
                const caption = document.createElement("figcaption");
                caption.textContent = captions[index];
                figure.append(caption);
                return figure;
            }));
            section.append(...figures);
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
