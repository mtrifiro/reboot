import "@fontsource-variable/space-grotesk";
import "@fontsource-variable/dm-sans";
import "@fontsource/dm-mono/400.css";
import "@fontsource/dm-mono/500.css";
import "./styles.css";
import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { RebootClientProvider } from "@reboot-dev/reboot-react";
import App from "./App.tsx";
import { BackendCheck } from "./backend-check";
import { ReloadPrompt } from "./reload-prompt";
import { applySavedTheme } from "./theme";

applySavedTheme();

// The backend serves this page (`rbt dev run --web-app` in
// development, the built app in production), so its origin is the
// backend's; `VITE_REBOOT_URL` is only for a static host elsewhere.
const REBOOT_URL =
  (import.meta.env.VITE_REBOOT_URL as string | undefined) ??
  window.location.origin;

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <BackendCheck url={REBOOT_URL} name="__APP_NAME__">
      <RebootClientProvider url={REBOOT_URL}>
        <App />
        <ReloadPrompt name="__APP_NAME__" />
      </RebootClientProvider>
    </BackendCheck>
  </StrictMode>,
);
