import type { Health, Readiness } from "../shared/types.ts";
async function request(path: string, fetcher: typeof fetch, timeoutMs: number) {
  const controller = new AbortController();
  let timer: ReturnType<typeof setTimeout> | undefined;
  const expired = new Promise<never>((_resolve, reject) => {
    timer = setTimeout(() => { controller.abort(); reject(new Error("API timeout aborted")); }, timeoutMs);
  });
  try {
    return await Promise.race([
      (async () => {
        const response = await fetcher(path, { signal: controller.signal, credentials: "omit" });
        const data: unknown = await response.json();
        return { response, data };
      })(),
      expired,
    ]);
  } finally { clearTimeout(timer); }

}
function validDate(value: unknown) { return typeof value === "string" && Number.isFinite(Date.parse(value)); }
export async function readHealth(fetcher: typeof fetch = fetch, timeoutMs = 4000): Promise<Health> {
  const { response, data } = await request("/api/health", fetcher, timeoutMs);
  if (!response.ok) throw new Error("HTTP status không hợp lệ");
  const health = data as Health;
  if (health.status !== "alive" || health.service !== "airc-api" || !validDate(health.timestamp)) throw new Error("API contract không hợp lệ");
  return health;
}
export async function readReadiness(fetcher: typeof fetch = fetch, timeoutMs = 4000): Promise<Readiness> {
  const { response, data } = await request("/api/ready", fetcher, timeoutMs);
  if (![200, 503].includes(response.status)) throw new Error("HTTP status không hợp lệ");
  const ready = data as Readiness;
  if (!["ready", "not_ready"].includes(ready.status)
    || !["ready", "unavailable", "not_configured"].includes(ready.database)
    || !validDate(ready.timestamp)
    || (ready.status === "ready") !== (ready.database === "ready")
    || (response.status === 200) !== (ready.status === "ready")) throw new Error("API contract không hợp lệ");
  return ready;
}
export async function readStatus(fetcher: typeof fetch = fetch, timeoutMs = 4000) {
  const [health, readiness] = await Promise.all([readHealth(fetcher, timeoutMs), readReadiness(fetcher, timeoutMs)]);
  return { health, readiness };
}
