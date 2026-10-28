import { useEffect, useState, type ReactNode } from "react";

// While the Reboot backend can't be reached, the app says so, instead of
// failing call by call, and checks again every few seconds; as soon as
// the backend answers, it is back, with no reload. Any HTTP answer, even
// an error, means the backend is up; only a failed connection means it
// is down. `no-cors` lets the check reach it without CORS headers.
//
// In development the check replaces the app with a page that says what
// is happening (the backend restarting after a change, or not started).
// In production it never takes the app down: a person may be halfway
// through something, so a banner over the app says it is reconnecting,
// and the app renders at once, without waiting for the first check.
const DOWN_EVERY_MS = 3_000;
const UP_EVERY_MS = 10_000;
// One failed check is often a blip (a network hiccup, a laptop waking
// up): the backend counts as down only after this many in a row.
const FAILURES_TO_DOWN = 2;

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
  name = "The app",
  children,
}: {
  url: string;
  // The app's name, for the production banner: "Maison Desk is
  // updating, or can't reach its server."
  name?: string;
  children: ReactNode;
}) {
  // In development, nothing renders until the first check (a few
  // milliseconds on localhost), so a backend that isn't started shows
  // its page at once; in production the app renders right away.
  const [up, setUp] = useState<boolean | null>(
    import.meta.env.DEV ? null : true,
  );
  // Whether the backend answered since the page loaded: losing it after
  // that is, in development, nearly always `rbt dev run` restarting it
  // after a change to the backend's code.
  const [wasUp, setWasUp] = useState(false);

  useEffect(() => {
    let stopped = false;
    let timer: number | undefined;
    let failures = 0;
    let first = true;
    const check = async () => {
      const ok = await reachable(url);
      if (stopped) return;
      failures = ok ? 0 : failures + 1;
      // The first check decides at once, so a backend that was never
      // started shows its page without a wait; after that, it takes
      // `FAILURES_TO_DOWN` failures in a row.
      if (ok) {
        setUp(true);
        setWasUp(true);
      } else if (first || failures >= FAILURES_TO_DOWN) {
        setUp(false);
      }
      first = false;
      timer = window.setTimeout(check, ok ? UP_EVERY_MS : DOWN_EVERY_MS);
    };
    check();
    return () => {
      stopped = true;
      window.clearTimeout(timer);
    };
  }, [url]);

  if (up === null) return null; // development's first check
  if (up) return <>{children}</>;
  if (!import.meta.env.DEV) {
    return (
      <>
        <Reconnecting name={name} />
        {children}
      </>
    );
  }
  return <BackendDown url={url} restarting={wasUp} />;
}

// Production: a slim banner over the app, which stays as it is. A
// backend that stops answering in production is most often a new
// version being deployed (`rbt cloud up` takes about a minute), so the
// banner says that first.
function Reconnecting({ name }: { name: string }) {
  return (
    <div
      role="status"
      aria-live="polite"
      style={{
        position: "fixed",
        top: 0,
        left: 0,
        right: 0,
        zIndex: 1000,
        padding: "8px 16px",
        textAlign: "center",
        background: "var(--panel)",
        color: "var(--ink)",
        borderBottom: "1px solid var(--line)",
        boxShadow: "var(--elev)",
      }}
    >
      {name} is updating, or can't reach its server right now.
      Reconnecting…
    </div>
  );
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

// Development only: the page that replaces the app.
function BackendDown({ url, restarting }: { url: string; restarting: boolean }) {
  const hideRebootWarning = (
    <style>{`#${REBOOT_WARNING_ID} { display: none !important; }`}</style>
  );
  if (restarting) {
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
      <p>
        This page is served, but the Reboot backend at{" "}
        <span className="mono">{url}</span> doesn't answer, so there is
        nothing to show yet.
      </p>
      <p>
        Start it from the project folder with{" "}
        <span className="mono">uv run rbt dev run</span>, or ask Claude to
        start the app.
      </p>
      <p className="small">
        Checking again every few seconds; the app opens as soon as the
        backend answers.
      </p>
    </main>
  );
}
