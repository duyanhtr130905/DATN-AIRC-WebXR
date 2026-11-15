import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
// Local development only; API_PROXY_TARGET is a Node-side setting, never embedded in VITE_*.
const target = process.env.API_PROXY_TARGET || "http://127.0.0.1:8000";
export default defineConfig({
    plugins: [react()],
    server: { host: "127.0.0.1", proxy: { "/api": { target }, "/ws": { target, ws: true, changeOrigin: false } } },
    preview: { host: "127.0.0.1", proxy: { "/api": { target }, "/ws": { target, ws: true, changeOrigin: false } } },
});
