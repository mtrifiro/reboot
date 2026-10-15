import { useEffect, useState, type ReactNode } from "react";

// While the Reboot backend can't be reached, the app shows a page that
// says so, instead of failing call by call or showing a blank page, and
// checks again every few seconds; as soon as the backend answers, the
// app appears, with no reload. Any HTTP answer, even an error, means the
// backend is up; only a failed connection means it is down. `no-cors`
// lets the check reach it without CORS headers.
const DOWN_EVERY_MS = 3_000;
const UP_EVERY_MS = 10_000;

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

  useEffect(() => {
    let stopped = false;
    let timer: number | undefined;
    const check = async () => {
      const ok = await reachable(url);
      if (stopped) return;
      setUp(ok);
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
  return <BackendDown url={url} />;
}

function BackendDown({ url }: { url: string }) {
  return (
    <main className="empty" role="status" aria-live="polite">
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
