import assert from "node:assert/strict";
import test from "node:test";
import { observationAge } from "../src/features/live/observationAge.ts";

test("observation age handles missing, invalid and skewed clocks", () => {
    const value = "2026-11-19T04:00:00Z";
    const timestamp = Date.parse(value);
    assert.equal(observationAge(value, timestamp), "0 s");
    assert.equal(observationAge(value, timestamp + 1900), "1 s");
    assert.equal(observationAge(null, timestamp), "UNKNOWN");
    assert.equal(observationAge("invalid", timestamp), "UNKNOWN");
    assert.equal(observationAge("2026-11-19T04:00:00", timestamp), "UNKNOWN");
    assert.match(observationAge(value, timestamp + 500, "2026-11-19T03:59:59Z"), /^TIME_UNCERTAIN/);
    assert.match(observationAge(value, timestamp + 500, "2026-11-19T05:00:00Z"), /^TIME_UNCERTAIN/);
    assert.match(observationAge(value, timestamp - 1), /^TIME_UNCERTAIN/);
    assert.match(observationAge(value, timestamp - 3600000), /^TIME_UNCERTAIN/);
});
