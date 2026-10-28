import react from "@vitejs/plugin-react";
import path from "path";
import { defineConfig } from "vite";

export default defineConfig({
  plugins: [react()],
  // The SPA's sources, `index.html`, `public/` and `.env*` live under `web/`.
  root: "web",
  build: {
    outDir: "../dist/web",
    emptyOutDir: true,
  },
  resolve: {
    // The generated client, imported as `@api/hotel/v1/hotel_rbt_react`.
    alias: { "@api": path.resolve(import.meta.dirname, "api") },
    // One copy each of `react` and `zod`, or hooks and schemas break.
    dedupe: ["react", "react-dom", "zod"],
  },
  server: {
    // Every interface: Vite's default `localhost` is IPv6-only on modern Node.
    host: true,
    port: parseInt(process.env.PORT || "5173", 10),
  },
});
