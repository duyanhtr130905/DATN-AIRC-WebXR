export type TimingMode = "web" | "vr" | "ar";
type TimingStatus = "waiting" | "recording" | "complete" | "interrupted";

export type TimingCapture = {
    mode: TimingMode;
    durationMs: number;
    status: TimingStatus;
    startedAt?: number;
    lastAt?: number;
    intervalsMs: number[];
    framebuffer?: [number, number];
    nominalHz?: number;
};

export function startTiming(mode: TimingMode, durationMs = 120_000): TimingCapture {
    if (!["web", "vr", "ar"].includes(mode) || !Number.isFinite(durationMs) ||
        durationMs < 1_000 || durationMs > 180_000) {
        throw new RangeError("Choose web, vr or ar and a duration of 1000–180000 ms");
    }
    return { mode, durationMs, status: "waiting", intervalsMs: [] };
}

export function interruptTiming(capture?: TimingCapture) {
    if (capture?.status === "recording") capture.status = "interrupted";
}

export function sampleTiming(capture: TimingCapture, mode: TimingMode, visible: boolean, now: number) {
    if (capture.status === "complete" || capture.status === "interrupted") return;
    if (!visible || mode !== capture.mode) {
        interruptTiming(capture);
        return;
    }
    if (capture.lastAt === undefined) {
        capture.status = "recording";
        capture.startedAt = capture.lastAt = now;
        return;
    }
    capture.intervalsMs.push(now - capture.lastAt);
    capture.lastAt = now;
    if (now - capture.startedAt! >= capture.durationMs) capture.status = "complete";
    else if (capture.intervalsMs.length >= 50_000) interruptTiming(capture);
}
