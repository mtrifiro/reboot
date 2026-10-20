#!/usr/bin/env python3
"""After the build starts or opens the Reboot dashboard, tell the agent
to give the user its links now, as message text.

A PostToolUse hook. The skills ask for this line ("the dashboard's
first start"), but builds kept writing it only in their thinking
("Dashboard is live with links to Book, Account, ..." with no link),
which the user can't click. A reminder arriving right after the tool
call, before the agent's next step, gets it said.

It fires once per session, on the first of:

  * a Bash call running `rbt dashboard`: its portless address,
    `https://dashboard-<app>.localhost`, unless the call asks for plain
    ports (`--config=ports`, `--no-portless`) or the project's
    `.rbtrc` doesn't default it to portless; else the port from
    `--port`, the project's `.claude/launch.json`, or 9871 (crm-30's
    reminder linked 127.0.0.1:9871 while the dashboard ran under
    portless);
  * opening the dashboard in the Claude app's Browser pane (a
    `preview_start` named `dashboard`, its URL from `launch.json`).

It links each domain object it finds in the project's API files
(`api/<package>/<version>/*.py`, each `<Name>=Type(`), so the line
names the app's own objects. Prints nothing, and does nothing, when the
call isn't one of these, the session has had its reminder, or the input
can't be read.
"""

import json
import os
import re
import sys
import tempfile
from pathlib import Path

DEFAULT_PORT = 9871
PORT = re.compile(r"--port[= ](\d{2,5})")
DASHBOARD_COMMAND = re.compile(r"\brbt\s+dashboard\b")
TYPE = re.compile(r"^\s*([A-Z]\w*)\s*=\s*Type\(", re.M)


def launch_url(cwd: Path) -> str:
    """The dashboard's URL in the project's `.claude/launch.json`."""
    try:
        launch = json.loads((cwd / ".claude" / "launch.json").read_text())
    except (OSError, ValueError):
        return ""
    for config in launch.get("configurations", []):
        if isinstance(config, dict) and config.get("name") == "dashboard":
            return str(config.get("url") or "").rstrip("/")
    return ""


def objects(cwd: Path) -> list[str]:
    """Each domain object, as `<package>.<version>.<Name>`."""
    found = []
    for path in sorted((cwd / "api").glob("*/*/*.py")):
        package, version = path.parent.parent.name, path.parent.name
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        found += [f"{package}.{version}.{name}" for name in TYPE.findall(text)]
    return found


def app_name(cwd: Path) -> str:
    """The `.rbtrc`'s `--application-name`, else the folder's name."""
    try:
        found = re.search(r"--application-name[= ](\S+)", (cwd / ".rbtrc").read_text())
    except OSError:
        found = None
    return found.group(1) if found else cwd.name


def portless_dashboard(command: str, cwd: Path) -> str:
    """The dashboard's portless address when this call runs it there."""
    if re.search(r"--config[= ]ports\b|--no-portless\b|--port[= ]\d", command):
        return ""
    try:
        rbtrc = (cwd / ".rbtrc").read_text()
    except OSError:
        return ""
    if "--config=portless" in command or re.search(r"^dashboard --default-config=portless", rbtrc, re.M):
        return f"https://dashboard-{app_name(cwd)}.localhost"
    return ""


def dashboard_url(event: dict, cwd: Path) -> str:
    """The dashboard's URL when this call started or opened it, else ""."""
    tool = str(event.get("tool_name", ""))
    args = event.get("tool_input") or {}
    if tool == "Bash":
        command = str(args.get("command", ""))
        if not DASHBOARD_COMMAND.search(command):
            return ""
        named = portless_dashboard(command, cwd)
        if named:
            return named
        port = PORT.search(command)
        if port:
            return f"http://127.0.0.1:{port.group(1)}"
        return launch_url(cwd) or f"http://127.0.0.1:{DEFAULT_PORT}"
    if tool.endswith("preview_start") and args.get("name") == "dashboard":
        return launch_url(cwd) or f"http://127.0.0.1:{DEFAULT_PORT}"
    return ""


def reminder(url: str, names: list[str]) -> str:
    links = " · ".join(
        f"[{name.rsplit('.', 1)[-1]}]({url}/#/models?type={name})"
        for name in names
    )
    pages = (
        f"[Models]({url}/#/models) · [Features]({url}/#/features) · "
        f"[Changelog]({url}/#/changelog)"
    )
    what = (
        f"each domain object, linked: {links}, with a few words on what "
        f"each holds; then {pages}"
        if links else
        f"{pages}; link each domain object the same way "
        f"({url}/#/models?type=<package>.<version>.<Name>) once it is "
        "written"
    )
    return (
        f"The Reboot dashboard is starting at {url}. Before your next tool "
        "call, send the user a message, as message text and never only in "
        f"thinking, since a line in thinking can't be clicked: {what}. Say "
        "what it shows them (the domain model the rules run on), in the "
        "user's nouns; then go on."
    )


def main() -> int:
    try:
        event = json.load(sys.stdin)
    except ValueError:
        return 0
    if not isinstance(event, dict):
        return 0
    cwd = Path(str(event.get("cwd") or os.getcwd()))
    url = dashboard_url(event, cwd)
    if not url:
        return 0
    session = re.sub(r"[^\w-]", "", str(event.get("session_id", ""))) or "unknown"
    marker = Path(tempfile.gettempdir()) / "reboot-plugin" / f"{session}.dashboard-links"
    if marker.exists():
        return 0
    try:
        marker.parent.mkdir(parents=True, exist_ok=True)
        marker.touch()
    except OSError:
        pass
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PostToolUse",
            "additionalContext": reminder(url, objects(cwd)),
        }
    }))
    return 0


if __name__ == "__main__":
    sys.exit(main())
