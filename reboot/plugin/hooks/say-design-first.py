#!/usr/bin/env python3
"""Refuse the first write of a build's `design/decisions.md` once, so
the design summary goes out in the chat before it is saved.

A PreToolUse hook on Write. The `app-design` skill says the design is
the response's own text first, then saved as the first entry of
`design/decisions.md`. Builds kept writing the file and going straight
on to the mockup with the summary only in their thinking (hotel-350,
351, 352, 355, 356, 358: six in a row), so the user never saw the
features. A hook can't see the text of the response it runs in, so it
can't tell whether the summary was sent: it refuses the first write
once, with the reason saying what to send, and lets the retry through.

It fires once per session and project, only on a Write that creates
`design/decisions.md` (the file doesn't exist yet). Prints nothing, and
decides nothing, for any other call or when the input can't be read.
"""

import hashlib
import json
import os
import re
import sys
import tempfile
from pathlib import Path

REASON = (
    "Not yet: the user hasn't seen the design. Send the proposed design "
    "now as message text, never only in thinking, in the shape of "
    "design-messages.md's \"The proposed design\": the brief, the "
    "features in build order with their rules, what is not in this "
    "build, what it keeps track of, the look, and Assumed. Then write "
    "this file again, unchanged, from that message."
)


def main() -> int:
    try:
        event = json.load(sys.stdin)
    except ValueError:
        return 0
    if not isinstance(event, dict) or event.get("tool_name") != "Write":
        return 0
    raw = str((event.get("tool_input") or {}).get("file_path") or "")
    if not raw:
        return 0
    cwd = Path(str(event.get("cwd") or os.getcwd()))
    path = Path(raw) if os.path.isabs(raw) else cwd / raw
    if path.name != "decisions.md" or path.parent.name != "design" or path.exists():
        return 0
    session = re.sub(r"[^\w-]", "", str(event.get("session_id", ""))) or "unknown"
    project = hashlib.sha1(str(path.parent.parent).encode()).hexdigest()[:12]
    marker = Path(tempfile.gettempdir()) / "reboot-plugin" / f"{session}.{project}.design-first"
    if marker.exists():
        return 0
    try:
        marker.parent.mkdir(parents=True, exist_ok=True)
        marker.touch()
    except OSError:
        return 0
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": REASON,
        }
    }))
    return 0


if __name__ == "__main__":
    sys.exit(main())
