import react from "@vitejs/plugin-react";
import path from "path";
import { defineConfig } from "vite";

export default defineConfig({
  plugins: [react()],
  // The SPA's sources, `index.html`, `public/` and `.env*` live
  // under `web/`.
  root: "web",
  build: {
    // Beside `web/`, where the backend or a static host serves it
    // at `/`; the default `base: "/"` stays.
    outDir: "../dist/web",
    emptyOutDir: true,
  },
  resolve: {
    // The generated client, imported as `@api/<pkg>/v1/<name>_rbt_react`.
    alias: { "@api": path.resolve(__dirname, "api") },
    // Two copies of `react` or `zod` — one from the app, one pulled
    // through the Reboot packages — break hooks and schema identity
    // checks at runtime.
    dedupe: ["react", "react-dom", "zod"],
  },
  server: {
    // Listen on every interface. Vite's default is `localhost`,
    // which on modern Node resolves to IPv6 `[::1]` only; a
    // forwarded port (Codespaces, VS Code remote, a dev VM, a
    // tunnel) connects over IPv4 `127.0.0.1` and gets connection
    // refused, so the page is unreachable from the browser even
    // though the dev server is healthy and logs no error.
    host: true,
    // Settable per machine, for one where 5173 is taken.
    port: parseInt(process.env.PORT || "5173", 10),
  },
});
