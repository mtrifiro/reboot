#!/usr/bin/env python3
"""Where a Reboot project stands, for the help skill.

    python3 status.py            # Markdown, from the project root (or any folder)
    python3 status.py --json

Reads only files and the process table; starts and changes nothing:

- the stage: no project, design only, backend built, frontend built,
  deployed (from api/, backend/, frontend/web/, design/decisions.md or design/design.md,
  tests/*.feature, deploy/ledger.jsonl);
- the app's name (the log's "Design proposed: <name>" entry, or design.md's
  title, else .rbtrc's application name);
- the features, their rule counts and which are @wip;
- what is running in this project (`rbt dev run`, `rbt dashboard`,
  the Vite dev server) and the ports it listens on;
- the last test run (tests/.last-run.json), and whether one is running;
- the reviews written so far (design/review.md, look-review.md,
  what-next.md).

Standard library only; `ps` and `lsof` where present.
"""

from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path.cwd()


def run(*cmd: str) -> str:
    if not shutil.which(cmd[0]):
        return ""
    try:
        return subprocess.run(cmd, capture_output=True, text=True, timeout=10).stdout
    except (OSError, subprocess.TimeoutExpired):
        return ""


def app_name() -> str:
    log = ROOT / "design/decisions.md"
    if log.is_file():
        found = re.search(r"^## [^\n]*?Design proposed:\s*(.+?)\s*$",
                          log.read_text(encoding="utf-8", errors="replace"), re.M)
        if found:
            return found.group(1)
    design = ROOT / "design/design.md"
    if design.is_file():
        first = design.read_text(encoding="utf-8", errors="replace").splitlines()[:1]
        if first and first[0].startswith("# "):
            return re.sub(r":\s*the design$", "", first[0][2:].strip())
    rbtrc = ROOT / ".rbtrc"
    if rbtrc.is_file():
        found = re.search(r"--application-name=(\S+)", rbtrc.read_text())
        if found:
            return found.group(1)
    return ROOT.name


def features() -> list[dict]:
    out = []
    tests = ROOT / "tests"
    for path in sorted(tests.rglob("*.feature")) if tests.is_dir() else []:
        text = path.read_text(encoding="utf-8", errors="replace")
        name = re.search(r"^\s*Feature:\s*(.+)$", text, re.M)
        out.append({
            "feature": name.group(1).strip() if name else path.stem,
            "rules": len(re.findall(r"^\s*Rule:", text, re.M)),
            "wip": bool(re.search(r"^\s*@wip\b[^\n]*\n\s*Feature:", text, re.M)),
        })
    return out


def stage(fs: list[dict]) -> str:
    if (ROOT / "deploy/ledger.jsonl").is_file():
        return "deployed"
    has_api = any((ROOT / "api").rglob("*.py")) if (ROOT / "api").is_dir() else False
    has_web = (ROOT / "frontend/web/src").is_dir()
    has_mcp = any((ROOT / "frontend").glob("*/src/**/*.tsx")) and not has_web if (ROOT / "frontend").is_dir() else False
    if has_api and (has_web or has_mcp):
        return "frontend built"
    if has_api and fs:
        return "backend built"
    if (ROOT / "design/design.md").is_file() or (ROOT / "design/decisions.md").is_file():
        return "design only"
    return "no project"


def processes() -> list[dict]:
    """What runs in this project, with the ports its process tree listens on."""
    table = run("ps", "-axo", "pid=,ppid=,command=")
    rows = []
    for line in table.splitlines():
        parts = line.strip().split(None, 2)
        if len(parts) == 3 and parts[0].isdigit():
            rows.append((int(parts[0]), int(parts[1]), parts[2]))
    children: dict[int, list[int]] = {}
    for pid, ppid, _ in rows:
        children.setdefault(ppid, []).append(pid)

    def tree(pid: int) -> list[int]:
        out, todo = [], [pid]
        while todo:
            p = todo.pop()
            out.append(p)
            todo += children.get(p, [])
        return out

    def cwd(pid: int) -> str:
        found = re.search(r"^n(.+)$", run("lsof", "-a", "-p", str(pid), "-d", "cwd", "-Fn"), re.M)
        return found.group(1) if found else ""

    def ports(pids: list[int]) -> list[int]:
        if not pids:
            return []
        out = run("lsof", "-a", "-p", ",".join(map(str, pids)), "-iTCP", "-sTCP:LISTEN", "-Fn", "-P")
        # The ports a person opens; the rest are Reboot's own, picked by
        # the system from the ephemeral range.
        return sorted({int(m) for m in re.findall(r"^n.*:(\d+)$", out, re.M) if int(m) < 49152})

    found = []
    kinds = (("app", r"rbt dev run"), ("dashboard", r"rbt dashboard"), ("web dev server", r"/vite(\s|$)"))
    seen: set[int] = set()
    for pid, ppid, command in rows:
        for kind, pattern in kinds:
            if re.search(pattern, command) and "uv run" not in command and pid not in seen:
                here = cwd(pid)
                if here and (Path(here) == ROOT or ROOT in Path(here).parents):
                    seen.update(tree(pid))
                    found.append({"what": kind, "pid": pid, "ports": ports(tree(pid))})
    return found


def last_run() -> dict:
    record = ROOT / "tests/.last-run.json"
    out: dict = {"running": (ROOT / "tests/.suite-running").exists()}
    if record.is_file():
        try:
            out.update(json.loads(record.read_text()))
        except ValueError:
            pass
    return out


def status() -> dict:
    fs = features()
    return {
        "project": str(ROOT),
        "app": app_name(),
        "stage": stage(fs),
        "features": fs,
        "running": processes(),
        "last_run": last_run(),
        "reviews": [str(p.relative_to(ROOT)) for p in sorted((ROOT / "design").glob("*.md"))
                    if p.name in ("review.md", "look-review.md", "what-next.md")]
                   if (ROOT / "design").is_dir() else [],
        "design": (ROOT / "design/design.md").is_file() or (ROOT / "design/decisions.md").is_file(),
    }


def markdown(s: dict) -> str:
    out = [f"# {s['app']}: {s['stage']}", ""]
    for f in s["features"]:
        rules = f"{f['rules']} rule" + ("" if f["rules"] == 1 else "s")
        out.append(f"- {f['feature']} ({rules}){' — in progress (@wip)' if f['wip'] else ''}")
    if not s["features"]:
        out.append("- no features yet")
    out.append("")
    if s["running"]:
        for p in s["running"]:
            out.append(f"- running: {p['what']} (pid {p['pid']}) on {', '.join(map(str, p['ports'])) or 'no port found'}")
    else:
        out.append("- running: nothing in this project")
    r = s["last_run"]
    if r.get("running"):
        out.append("- tests: a run is in progress")
    elif "passed" in r:
        kind = "full" if r.get("full") else "partial"
        out.append(f"- last test run ({kind}, {r.get('when', '?')}): {r.get('passed', 0)} passed, "
                   f"{r.get('failed', 0)} failed, {r.get('blocked', 0)} blocked")
    else:
        out.append("- tests: no run recorded")
    out.append("- reviews: " + (", ".join(s["reviews"]) or "none"))
    return "\n".join(out)


def main(argv: list[str]) -> int:
    s = status()
    print(json.dumps(s, indent=2) if "--json" in argv else markdown(s))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
