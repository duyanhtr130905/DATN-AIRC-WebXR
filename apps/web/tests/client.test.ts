import test from "node:test";
import assert from "node:assert/strict";
import { readStatus, readHealth, readReadiness } from "../src/api/client.ts";
const timestamp = "2026-11-14T00:00:00Z";
function mock(database = "not_configured", code = 503): typeof fetch {
  return async (url) => new Response(JSON.stringify(String(url).endsWith("health")
    ? { status: "alive", service: "airc-api", timestamp }
    : { status: database === "ready" ? "ready" : "not_ready", database, timestamp }),
    { status: String(url).endsWith("health") ? 200 : code });
}
test("alive process and unavailable DB remain distinct", async () => {
  const result = await readStatus(mock());
  assert.equal(result.health.status, "alive");
  assert.equal(result.readiness.status, "not_ready");
});
test("ready response requires consistent HTTP and DB states", async () => {
  assert.equal((await readStatus(mock("ready", 200))).readiness.database, "ready");
  await assert.rejects(readStatus(mock("ready", 503)), /contract/);
  await assert.rejects(readStatus(mock("unknown", 503)), /contract/);
});
test("rejects non-API HTML and network errors", async () => {
  await assert.rejects(readStatus(async () => new Response("<html>")));
  await assert.rejects(readStatus(async () => { throw new Error("offline"); }), /offline/);
});
test("timeout aborts network rather than hanging", async () => {
  const fetcher: typeof fetch = async (_url, init) => new Promise((_resolve, reject) => {
    init?.signal?.addEventListener("abort", () => reject(new Error("aborted")), { once: true });
  });
  await assert.rejects(readStatus(fetcher, 15), /aborted/);
});

test("health remains alive independently when readiness transport fails", async () => {
  const fetcher: typeof fetch = async (url, init) => {
    if (String(url).endsWith("ready")) throw new Error("dependency-timeout");
    return mock()(url, init);
  };
  assert.equal((await readHealth(fetcher)).status, "alive");
  await assert.rejects(readReadiness(fetcher), /dependency-timeout/);
});

test("timeout covers a body that stalls after headers", async () => {
  const fetcher: typeof fetch = async () => new Response(new ReadableStream({ start() {} }));
  await assert.rejects(readHealth(fetcher, 15), /timeout/);
});
