import assert from "node:assert/strict";
import { test } from "node:test";
import { sampleTiming, startTiming } from "../src/p507-m5/timing.ts";

test("timing records every callback interval for the requested mode and stops at duration", () => {
    const capture = startTiming("vr", 1000);
    sampleTiming(capture, "web", true, 0);
    assert.equal(capture.status, "waiting");
    for (const time of [50, 66, 110, 1051, 1065]) sampleTiming(capture, "vr", true, time);
    assert.equal(capture.status, "complete");
    assert.deepEqual(capture.intervalsMs, [16, 44, 941]);
});

test("visibility or mode change interrupts a sample instead of counting a paused interval", () => {
    const capture = startTiming("ar", 1000);
    sampleTiming(capture, "ar", true, 50);
    sampleTiming(capture, "ar", true, 75);
    sampleTiming(capture, "ar", false, 90);
    sampleTiming(capture, "ar", true, 1000);
    assert.equal(capture.status, "interrupted");
    assert.deepEqual(capture.intervalsMs, [25]);
    const web = startTiming("web");
    sampleTiming(web, "web", true, 20);
    sampleTiming(web, "vr", true, 40);
    assert.equal(web.status, "interrupted");
    assert.throws(() => startTiming("vr", Infinity), RangeError);
});
