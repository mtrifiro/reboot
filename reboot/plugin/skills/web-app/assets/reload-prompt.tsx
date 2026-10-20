import { useEffect, useState } from "react";

// Tells an open tab that a newer version of the app has been published,
// and reloads only when asked: someone halfway through something would
// lose it. Each tab compares the script it loaded with the one the site
// serves now. Vite names the entry script by its contents
// (`/assets/index-<hash>.js`), so a new build has a new name and a
// republish of the same code keeps it: no build id, `version.json` or
// Vite config. It checks when the tab comes back into view and every
// few minutes, in production only (`vite dev` has no hashed script).
// Adapted from Reboot CRM's `UpgradeNotices.tsx`.
const CHECK_EVERY_MS = 5 * 60 * 1000;

// The script this tab loaded, by the name Vite gave it; blank under
// `vite dev`.
function loadedBundle(): string {
  const src = document.querySelector<HTMLScriptElement>(
    'script[type="module"][src*="/assets/index-"]',
  )?.src;
  return src ? new URL(src).pathname : "";
}

export function ReloadPrompt({ name = "The app" }: { name?: string }) {
  // How many times a check has found a newer build, and how many of
  // those "Later" has put off: Later hides it until the next check.
  const [found, setFound] = useState(0);
  const [putOff, setPutOff] = useState(0);

  useEffect(() => {
    const loaded = loadedBundle();
    if (!import.meta.env.PROD || !loaded) return;
    let live = true;
    const check = async () => {
      try {
        const page = await (await fetch("/", { cache: "no-store" })).text();
        const current = page.match(/\/assets\/index-[\w-]+\.js/)?.[0];
        if (live && current && current !== loaded) setFound((n) => n + 1);
      } catch {
        // Offline, or the host is mid-publish: the next check will say.
      }
    };
    const onShow = () => {
      if (document.visibilityState === "visible") void check();
    };
    document.addEventListener("visibilitychange", onShow);
    window.addEventListener("focus", onShow);
    const timer = window.setInterval(check, CHECK_EVERY_MS);
    return () => {
      live = false;
      document.removeEventListener("visibilitychange", onShow);
      window.removeEventListener("focus", onShow);
      window.clearInterval(timer);
    };
  }, []);

  if (found === 0 || putOff >= found) return null;
  return (
    <div
      role="alertdialog"
      aria-labelledby="reload-prompt-title"
      style={{
        position: "fixed",
        right: 16,
        bottom: 16,
        zIndex: 1000,
        maxWidth: 360,
        padding: "12px 16px",
        background: "var(--panel)",
        color: "var(--ink)",
        border: "1px solid var(--line)",
        borderRadius: "var(--radius)",
        boxShadow: "var(--elev)",
      }}
    >
      <p id="reload-prompt-title" style={{ margin: "0 0 8px" }}>
        {name} has been updated. Reload to get the new version.
      </p>
      <div style={{ display: "flex", gap: 8, justifyContent: "flex-end" }}>
        <button type="button" className="ghost" onClick={() => setPutOff(found)}>
          Later
        </button>
        <button
          type="button"
          className="primary"
          onClick={() => window.location.reload()}
        >
          Reload
        </button>
      </div>
    </div>
  );
}
