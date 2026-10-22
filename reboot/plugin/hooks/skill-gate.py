#!/usr/bin/env python3
"""Refuse an edit under a Reboot project's own folders until the skill
that holds that folder's rules has been loaded in the session.

A PreToolUse hook, on two kinds of call:

  * `Skill`: records the skill loaded (`reboot:python` → `python`) in
    the session's list, and decides nothing.
  * `Edit`, `Write`, `MultiEdit`, `NotebookEdit`: finds the file's
    Reboot project (the nearest ancestor holding `.rbtrc`; a file
    outside one is not this hook's business), maps its folder to the
    skills that carry its rules, and when none of them has been loaded
    this session, denies the edit with the skill to load. The model
    reads the reason, loads the skill, and edits again.

    folder                 any of these skills loaded
    api/                   python, web-app, mcp-app, feature
    backend/src/           python, web-app, mcp-app, feature
    frontend/web/          web-app
    frontend/mcp/          mcp-app
    tests/*.feature        feature, web-app, mcp-app

  The web-app and mcp-app skills read the python references on their
  own path, so a build that loaded either has the API's rules without
  a `Skill` call for `python`; the mapping accepts them. crm-30
  (2026-10-22) edited `frontend/web/src/components/` with only
  `agents-md`, `run` and `dashboard` loaded, after a reminder on that
  very prompt to use the skills: this hook would have denied the edit
  and named `web-app`.

The session's list lives beside say-dashboard-links.py's marker, in the
system temp dir under `reboot-plugin/`, keyed by `session_id`. Both
Claude Code and Codex act on a `deny`. Any failure to read the input
or the list decides nothing (exit 0, no output), never a denial by
accident. Edits through Bash (`sed -i`, a heredoc) are not seen here.
"""

from __future__ import annotations

import json
import os
import re
import sys
import tempfile
from pathlib import Path

EDIT_TOOLS = {"Edit", "Write", "MultiEdit", "NotebookEdit"}

# The folder (relative to the project root, with a trailing slash) or
# suffix an edit touches, and the skills that carry its rules.
RULES: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("api/", ("python", "web-app", "mcp-app", "feature")),
    ("backend/src/", ("python", "web-app", "mcp-app", "feature")),
    ("frontend/web/", ("web-app",)),
    ("frontend/mcp/", ("mcp-app",)),
    ("tests/", ("feature", "web-app", "mcp-app")),  # .feature files only, below
)


def session_file(event: dict) -> Path:
    session = re.sub(r"[^\w-]", "", str(event.get("session_id", ""))) or "unknown"
    return Path(tempfile.gettempdir()) / "reboot-plugin" / f"{session}.skills"


def project_root(path: Path) -> Path | None:
    for d in (path, *path.parents):
        if (d / ".rbtrc").is_file():
            return d
    return None


def needed(rel: str) -> tuple[str, ...] | None:
    """The skills one of which must be loaded for an edit at `rel`."""
    for folder, skills in RULES:
        if rel.startswith(folder):
            if folder == "tests/" and not rel.endswith(".feature"):
                return None
            return skills
    return None


def deny(reason: str) -> None:
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": "deny",
        "permissionDecisionReason": reason,
    }}))


def main() -> int:
    try:
        event = json.load(sys.stdin)
    except Exception:
        return 0
    tool = str(event.get("tool_name", ""))
    tool_input = event.get("tool_input") or {}
    if tool == "Skill":
        name = str(tool_input.get("skill", ""))
        if name.startswith("reboot:"):
            f = session_file(event)
            try:
                f.parent.mkdir(parents=True, exist_ok=True)
                with f.open("a", encoding="utf-8") as out:
                    out.write(name[len("reboot:"):] + "\n")
            except OSError:
                pass
        return 0
    if tool not in EDIT_TOOLS:
        return 0
    raw = str(tool_input.get("file_path") or tool_input.get("notebook_path") or "")
    if not raw:
        return 0
    cwd = Path(str(event.get("cwd") or os.getcwd()))
    path = Path(raw) if os.path.isabs(raw) else cwd / raw
    path = Path(os.path.normpath(path))
    root = project_root(path.parent)
    if root is None:
        return 0
    rel = path.relative_to(root).as_posix()
    skills = needed(rel)
    if skills is None:
        return 0
    try:
        loaded = set(session_file(event).read_text(encoding="utf-8").split())
    except OSError:
        loaded = set()
    if loaded & set(skills):
        return 0
    first = skills[0]
    behaviour = (" (the `feature` skill first if this is new or changed behaviour)"
                 if first != "feature" else "")
    deny(f"`{rel}` is a Reboot project's own: load the `reboot:{first}` skill with the Skill tool "
         f"before editing it{behaviour}, then make this edit again. "
         f"Its rules are the skill's, not this session's memory.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
