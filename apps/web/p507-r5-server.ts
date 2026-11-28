import type { Plugin } from "vite";
import { createReadStream } from "node:fs";
import { stat } from "node:fs/promises";
import { fileURLToPath } from "node:url";

const files = new Set(["P507_R5_PROPOSAL.glb", "asset-manifest.json"]);
const addresses = new Set(["127.0.0.1", "::1", "::ffff:127.0.0.1"]);
const hosts = new Set(["127.0.0.1", "localhost", "[::1]"]);

export function p507R5Assets(): Plugin {
    return {
        name: "p507-r5-dev-assets",
        apply: "serve",
        configureServer(server) {
            server.middlewares.use("/p507-r5-assets/", async (req, res) => {
                const name = req.url?.replace(/^\//, "");
                const notFound = () => { res.statusCode = 404; res.end("R5 asset is unavailable"); };
                let host = "";
                try { host = new URL("http://" + req.headers.host).hostname; } catch { /* deny malformed Host */ }
                if (req.method !== "GET" || !hosts.has(host) || !addresses.has(req.socket.remoteAddress ?? "") ||
                    !name || !files.has(name)) return notFound();
                const path = fileURLToPath(new URL("../../.local/p507-r5/served/" + name, import.meta.url));
                try {
                    const size = (await stat(path)).size;
                    res.setHeader("Content-Type", name.endsWith(".glb") ? "model/gltf-binary" : "application/json");
                    res.setHeader("Content-Length", size);
                    res.setHeader("Cache-Control", "no-store");
                    const stream = createReadStream(path);
                    stream.on("error", () => { if (res.headersSent) res.destroy(); else notFound(); });
                    res.on("close", () => stream.destroy());
                    stream.pipe(res);
                } catch {
                    notFound();
                }
            });
        },
    };
}
