import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";
import { reboot } from "@reboot-dev/reboot-react/vite";

// The stock Vite file plus Reboot's plugin: it serves the SPA in `web/`
// at `/` (and at any path, so the app's routes survive a reload),
// builds it to `dist/web/`, aliases `@api` to the generated client,
// dedupes `react`, `react-dom` and `zod`, reads `.env*` from `web/`,
// and listens on every interface. It owns `root`, `base`, `envDir`,
// `publicDir`, `build.outDir` and the alias: setting one here is an
// error (web-app/references/react-client.md).
export default defineConfig({
  plugins: [react(), reboot({ webAppPath: "web", apiPath: "api" })],
});
