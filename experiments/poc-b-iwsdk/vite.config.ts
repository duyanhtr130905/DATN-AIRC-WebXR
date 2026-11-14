import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import { fileURLToPath } from "node:url";
import { iwsdkDev } from "@iwsdk/vite-plugin-dev";
export default defineConfig({
  plugins: [react(), iwsdkDev({ https: false })],
  resolve: {
    alias: {
      react: fileURLToPath(new URL("./node_modules/react", import.meta.url)),
      "react-dom": fileURLToPath(
        new URL("./node_modules/react-dom", import.meta.url),
      ),
    },
  },
  server: { host: "127.0.0.1", fs: { allow: [".."] } },
  preview: { host: "127.0.0.1" },
});
