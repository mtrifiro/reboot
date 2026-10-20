#!/usr/bin/env python3
"""A "restarting" page at the app's address while the build has it
stopped, in place of the proxy's 502.

    python3 <this file> start [--name <app>] [--port 9991]
    python3 <this file> stop

Run from the project root. `start` serves one page for every path, a
503 that reloads itself every three seconds, so the user's open tab
shows the app again by itself once it is back. Under portless (the
app's address is https://<name>.localhost) it takes a free port and
points the app's name at it with `portless alias`; the app takes its
name back when `rbt dev run` starts, so run `stop` once the app
answers again. On plain ports it holds --port (9991 by default),
which the app needs back, so run `stop` just before starting the app.
`<name>` defaults to the `.rbtrc`'s `--application-name`. The pid is in
`.standby.pid`. Standard library only.
"""

from __future__ import annotations

import html
import http.server
import os
import re
import shutil
import signal
import socket
import subprocess
import sys
from pathlib import Path

PID = Path(".standby.pid")

PAGE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta http-equiv="refresh" content="3">
<title>{name} · restarting</title>
<style>
  :root {{ --bg: #f7f5ed; --ink: #103761; --muted: #506a85; --line: #d9dfe6; color-scheme: light dark; }}
  @media (prefers-color-scheme: dark) {{ :root {{ --bg: #0b1f36; --ink: #f7f5ed; --muted: #9aabbf; --line: #24405f; }} }}
  body {{ margin: 0; min-height: 100vh; display: grid; place-items: center; background: var(--bg); color: var(--ink);
          font: 15px/1.5 "DM Sans", system-ui, sans-serif; padding: 0 16px; }}
  main {{ max-width: 34rem; display: grid; gap: 10px; }}
  .eyebrow {{ font-size: 12px; font-weight: 600; letter-spacing: .06em; text-transform: uppercase; color: var(--muted); }}
  h1 {{ font: 600 28px/1.2 "Space Grotesk", system-ui, sans-serif; margin: 0; }}
  p {{ margin: 0; color: var(--muted); }}
  .dot {{ display: inline-block; width: 8px; height: 8px; border-radius: 50%; background: var(--muted); margin-right: 8px;
          animation: pulse 1.2s ease-in-out infinite; }}
  @keyframes pulse {{ 50% {{ opacity: .25; }} }}
  @media (prefers-reduced-motion: reduce) {{ .dot {{ animation: none; }} }}
</style>
</head>
<body>
<main>
  <span class="eyebrow"><span class="dot"></span>{name}</span>
  <h1>Restarting</h1>
  <p>The app is restarting after a change to its API. This page reloads
  by itself and shows the app again as soon as it is back, usually within
  a minute.</p>
</main>
</body>
</html>
"""


def app_name() -> str:
    rbtrc = Path(".rbtrc")
    if rbtrc.is_file():
        found = re.search(r"--application-name[= ](\S+)", rbtrc.read_text(encoding="utf-8"))
        if found:
            return found.group(1)
    return Path.cwd().name


def portless() -> str | None:
    return shutil.which("portless")


def under_portless(name: str) -> bool:
    tool = portless()
    if not tool:
        return False
    listed = subprocess.run([tool, "list"], capture_output=True, text=True).stdout
    return f"https://{name}.localhost" in listed


def free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def serve(name: str, port: int) -> None:
    body = PAGE.format(name=html.escape(name)).encode()

    class Standby(http.server.BaseHTTPRequestHandler):
        def do_GET(self) -> None:  # noqa: N802
            self.send_response(503)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Retry-After", "3")
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)

        do_HEAD = do_GET

        def log_message(self, *args: object) -> None:
            pass

    http.server.ThreadingHTTPServer(("127.0.0.1", port), Standby).serve_forever()


def stop() -> int:
    if not PID.is_file():
        return 0
    try:
        os.kill(int(PID.read_text().strip()), signal.SIGTERM)
    except (ProcessLookupError, ValueError):
        pass
    PID.unlink(missing_ok=True)
    print("standby: stopped")
    return 0


def main(argv: list[str]) -> int:
    if argv[:1] == ["stop"]:
        return stop()
    if argv[:1] == ["serve"]:
        serve(argv[1], int(argv[2]))
        return 0
    if argv[:1] != ["start"]:
        print(__doc__, file=sys.stderr)
        return 2
    args = argv[1:]
    name = args[args.index("--name") + 1] if "--name" in args else app_name()
    stop()
    if under_portless(name):
        port = free_port()
        child = subprocess.Popen([sys.executable, __file__, "serve", name, str(port)],
                                 stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
        subprocess.run([portless(), "alias", name, str(port)], capture_output=True, text=True)
        where = f"https://{name}.localhost"
    else:
        port = int(args[args.index("--port") + 1]) if "--port" in args else 9991
        child = subprocess.Popen([sys.executable, __file__, "serve", name, str(port)],
                                 stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
        where = f"http://localhost:{port}"
    PID.write_text(str(child.pid))
    print(f"standby: a 'restarting' page at {where} (pid {child.pid}); "
          + ("stop it once the app answers again" if under_portless(name) else "stop it just before starting the app"))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
