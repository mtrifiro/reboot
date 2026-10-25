#!/usr/bin/env python3
"""The release record: what a deploy ships, and the evidence it rests on.

    scripts/release_record.py --dry-run                 # before the deploy: show the user
    scripts/release_record.py [--revision N] [--api-url URL] [--site URL]
                                                        # after it: append the row

Promoting is the user's decision (the Reboot Flywheel); this shows what
it rests on and never stops a deploy. Both forms print the commits since
the last deploy, the model diff against it, the last test run, the
accepted design, and any servicer with no authorizer (which `rbt dev`
allows with a warning and Reboot Cloud denies). Without `--dry-run` it
then appends one row to `deploy/ledger.jsonl`. The last row is the revision that
is live, and its `release` field is the record:

    {"at": "...", "commit": "abc1234", "revision": 17, "api_url": "...",
     "release": {"tests": {...}, "since": "9f8e7d6", "commits": [...],
                 "model_diff": {"design": [...], "prove": [...]},
                 "unauthorized_servicers": [], "accepted": {...}}}

It reads `scripts/model_diff.py` and `tests/.last-run.json`
(`tests/last_run.py`). Without git it still records the test run and
the design; the commits need git.
"""

from __future__ import annotations

import datetime
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LEDGER = ROOT / "deploy" / "ledger.jsonl"


def run(*args: str) -> str:
    return subprocess.run(args, cwd=ROOT, capture_output=True, text=True).stdout


def diff_json(*args: str) -> dict:
    out = run(sys.executable, "scripts/model_diff.py", *args, "--head", "--json")
    try:
        return json.loads(out)
    except json.JSONDecodeError:
        return {}


def when(accepted: dict) -> str:
    at = accepted.get("at", "")[:10]
    return f"at {accepted['commit'][:7]} ({at})" if accepted.get("commit") else f"on {at}"


def last_row() -> dict:
    if not LEDGER.is_file():
        return {}
    rows = [line for line in LEDGER.read_text().splitlines() if line.strip()]
    return json.loads(rows[-1]) if rows else {}


def main(argv: list[str]) -> int:
    dry = "--dry-run" in argv
    opts: dict[str, str] = {}
    rest = [a for a in argv if a != "--dry-run"]
    while rest:
        flag = rest.pop(0)
        if flag not in ("--revision", "--api-url", "--site") or not rest:
            print(__doc__, file=sys.stderr)
            return 2
        opts[flag] = rest.pop(0)

    sha = run("git", "rev-parse", "--short", "HEAD").strip()
    if not sha:
        print("release: no git history here, so the record lists no commits")
    since = last_row().get("commit", "") if sha else ""
    release: dict = {}

    if since and run("git", "cat-file", "-t", since).strip() == "commit":
        commits = run("git", "log", "--format=%h %s", f"{since}..HEAD").splitlines()
        print(f"release: since the last deploy ({since}):")
        for c in commits:
            print(f"  {c}")
        print(run(sys.executable, "scripts/model_diff.py", since, "--head").rstrip())
        diff = diff_json(since)
        release.update(since=since, commits=commits,
                       model_diff={"design": diff.get("design", []), "prove": diff.get("prove", [])})
    else:
        print("release: the first deploy recorded here")

    record = ROOT / "tests" / ".last-run.json"
    tests = json.loads(record.read_text()) if record.is_file() else {}
    release["tests"] = tests
    if not tests:
        print("release: tests: no run recorded (tests/.last-run.json); run the full test suite first")
    else:
        where = "the full test suite" if tests.get("full") else "a partial run"
        print(f"release: tests: {tests.get('passed', 0)} passed, {tests.get('failed', 0)} failed, "
              f"{tests.get('wip', 0)} @wip, {tests.get('blocked', 0)} @blocked; {where} at "
              f"{tests.get('revision') or 'this folder'}{' with uncommitted changes' if tests.get('dirty') else ''}")
        if (tests.get("revision") != sha or tests.get("dirty") or not tests.get("full")
                or tests.get("failed") or tests.get("exit")):
            print(f"release: tests: not a clean, full, passing run of {sha}; tell the user before promoting")

    if (ROOT / "design" / "accepted.json").is_file():
        out = run(sys.executable, "scripts/model_diff.py", "--json")
        design = json.loads(out) if out.strip().startswith("{") else {}
    else:
        design = diff_json("HEAD") if sha else {}
    accepted = design.get("accepted")
    release["accepted"] = accepted
    if accepted is None:
        print("release: design: no acceptance record (design/accepted.json)")
    elif accepted.get("design_changes"):
        print(f"release: design: {accepted['design_changes']} design change(s) since the acceptance "
              f"{when(accepted)}; not accepted. Tell the user before promoting")
    else:
        print(f"release: design: accepted {when(accepted)}")
    unauthorized = design.get("unauthorized_servicers", [])
    release["unauthorized_servicers"] = unauthorized
    if unauthorized:
        print(f"release: authorizers: {' '.join(unauthorized)} have no authorizer; Reboot Cloud "
              "denies every call to them. Tell the user before promoting")

    if dry:
        print("release: dry run; nothing recorded.")
        return 0
    row: dict = {"at": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
                 "commit": sha}
    if "--revision" in opts:
        row["revision"] = int(opts["--revision"])
    if "--api-url" in opts:
        row["api_url"] = opts["--api-url"]
    if "--site" in opts:
        row["site"] = opts["--site"]
    row["release"] = release
    LEDGER.parent.mkdir(exist_ok=True)
    with LEDGER.open("a") as f:
        f.write(json.dumps(row) + "\n")
    print(f"release: recorded in {LEDGER.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
