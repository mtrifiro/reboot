import { useEffect, useState, type ReactNode } from "react";

// While the Reboot backend can't be reached, the app shows a page that
// says so, instead of failing call by call or showing a blank page, and
// checks again every few seconds; as soon as the backend answers, the
// app appears, with no reload. Any HTTP answer, even an error, means the
// backend is up; only a failed connection means it is down. `no-cors`
// lets the check reach it without CORS headers.
const DOWN_EVERY_MS = 3_000;
const UP_EVERY_MS = 10_000;

// Reboot's web library adds its own red "Trouble connecting..." box to
// the page in development, 10 seconds into a lost connection, with this
// id. While the page below says what is happening, that box only covers
// it, so it is hidden then (and only then).
const REBOOT_WARNING_ID = "localhostWarning";

async function reachable(url: string): Promise<boolean> {
  try {
    await fetch(url, { mode: "no-cors", cache: "no-store" });
    return true;
  } catch {
    return false;
  }
}

export function BackendCheck({
  url,
  children,
}: {
  url: string;
  children: ReactNode;
}) {
  const [up, setUp] = useState<boolean | null>(null);
  // Whether the backend answered since the page loaded: losing it after
  // that is, in development, nearly always `rbt dev run` restarting it
  // after a change to the backend's code.
  const [wasUp, setWasUp] = useState(false);

  useEffect(() => {
    let stopped = false;
    let timer: number | undefined;
    const check = async () => {
      const ok = await reachable(url);
      if (stopped) return;
      setUp(ok);
      if (ok) setWasUp(true);
      timer = window.setTimeout(check, ok ? UP_EVERY_MS : DOWN_EVERY_MS);
    };
    check();
    return () => {
      stopped = true;
      window.clearTimeout(timer);
    };
  }, [url]);

  if (up === null) return null; // the first check, a few milliseconds
  if (up) return <>{children}</>;
  return <BackendDown url={url} restarting={wasUp} />;
}

// A ring in the accent color, turning while the backend restarts, so the
// page reads as waiting rather than stuck. Its style is here, not in the
// house stylesheet, so the page needs nothing else; the stylesheet's
// reduced-motion rule still stops it.
function Spinner() {
  return (
    <>
      <style>{`
        @keyframes backend-check-turn { to { transform: rotate(360deg); } }
        .backend-check-spinner {
          width: 40px;
          height: 40px;
          margin: 0 auto 24px;
          border-radius: 50%;
          border: 3px solid var(--track);
          border-top-color: var(--accent);
          animation: backend-check-turn 0.9s linear infinite;
        }
      `}</style>
      <div className="backend-check-spinner" aria-hidden="true" />
    </>
  );
}

function BackendDown({ url, restarting }: { url: string; restarting: boolean }) {
  const hideRebootWarning = (
    <style>{`#${REBOOT_WARNING_ID} { display: none !important; }`}</style>
  );
  if (restarting && import.meta.env.DEV) {
    return (
      <main className="empty" role="status" aria-live="polite">
        {hideRebootWarning}
        <Spinner />
        <h1>The backend is restarting</h1>
        <p>
          It restarts by itself after each change to its code, and keeps
          its data. This can take a couple of minutes; the app comes back
          on its own.
        </p>
        <p className="small">
          If it takes more than five minutes, the backend may have
          stopped: ask Claude to check the app.
        </p>
      </main>
    );
  }
  return (
    <main className="empty" role="status" aria-live="polite">
      {hideRebootWarning}
      <h1>The app's backend isn't running</h1>
      {import.meta.env.DEV ? (
        <>
          <p>
            This page is served, but the Reboot backend at{" "}
            <span className="mono">{url}</span> doesn't answer, so there is
            nothing to show yet.
          </p>
          <p>
            Start it from the project folder with{" "}
            <span className="mono">uv run rbt dev run</span>, or ask Claude
            to start the app.
          </p>
        </>
      ) : (
        <p>The app can't reach its server right now.</p>
      )}
      <p className="small">
        Checking again every few seconds; the app opens as soon as the
        backend answers.
      </p>
    </main>
  );
}
