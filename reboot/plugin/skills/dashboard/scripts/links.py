"""Print links into a Reboot app's developer dashboard, by the ids it uses.

    python3 links.py [PROJECT] [--only FILE ...]

PROJECT is the app's root (the folder with `.rbtrc`), the current
directory by default. `--only` keeps the state types of the API files
and the features of the feature files named, for a report on what was
just written. Prints Markdown: each state type and its methods, each
feature with its rules and scenarios, then the app's own URLs.

The ids are the dashboard's own: the API is read with the dashboard's
reader (`reboot.dashboard.backend.api_reader`, in the app's
environment), so a state type is `<package>.<Type>`, e.g.
`bank.v1.Account`, and a method `bank.v1.Account.deposit`; a feature
is its file's path from the project root, a rule its place in the
file counting from one, a scenario the line it is declared on. Every
link is a hash route (`/#/models/...`), as the dashboard routes.
"""
import json
import re
import subprocess
import sys
from pathlib import Path

KINDS = ("reader", "writer", "transaction", "workflow", "ui")


def rbtrc(root: Path) -> dict:
    out = {"api": "api", "name": None, "portless": False}
    for line in (root / ".rbtrc").read_text().splitlines():
        line = line.split("#", 1)[0].strip()
        m = re.fullmatch(r"generate\s+([^\s-][^\s]*)", line)
        if m:
            out["api"] = m.group(1).rstrip("/")
        m = re.match(r"dev run\s+--application-name=(\S+)", line)
        if m:
            out["name"] = m.group(1)
        if re.match(r"dashboard\s+--default-config=portless", line):
            out["portless"] = True
    return out


def python(root: Path) -> list[str]:
    venv = root / ".venv" / "bin" / "python"
    return [str(venv)] if venv.exists() else ["uv", "run", "--project", str(root), "python"]


def state_types(root: Path, api_dir: str, only: set[str]) -> list[dict]:
    types = []
    for f in sorted((root / api_dir).rglob("*.py")):
        rel = f.relative_to(root / api_dir).as_posix()
        if f.name == "__init__.py" or (only and f"{api_dir}/{rel}" not in only):
            continue
        run = subprocess.run(python(root) + ["-m", "reboot.dashboard.backend.api_reader", api_dir, rel],
                             cwd=root, capture_output=True, text=True)
        if run.returncode != 0 or run.stdout.strip() in ("", "null"):
            continue
        api = json.loads(run.stdout)
        for t in api.get("stateTypes", []):
            methods = [(m["name"], next((k for k in KINDS if k in m), "method")) for m in t.get("methods", [])]
            types.append({"id": f"{api['package']}.{t['name']}", "file": f"{api_dir}/{rel}", "methods": methods})
    return types


def features(root: Path, only: set[str]) -> list[dict]:
    out = []
    for f in sorted(root.glob("tests/**/*.feature")):
        rel = f.relative_to(root).as_posix()
        if only and rel not in only:
            continue
        feat = {"id": rel, "name": rel, "rules": [], "scenarios": []}
        tags: list[str] = []
        for n, line in enumerate(f.read_text().splitlines(), 1):
            s = line.strip()
            if s.startswith("@"):
                tags += s.split()
                continue
            m = re.match(r"(Feature|Rule|Scenario Outline|Scenario Template|Scenario|Example):\s*(.*)", s)
            if not m:
                if s and not s.startswith("#"):
                    tags = []
                continue
            kind, title = m.groups()
            if kind == "Feature":
                feat["name"] = title
            elif kind == "Rule":
                feat["rules"].append({"n": len(feat["rules"]) + 1, "name": title})
            else:
                feat["scenarios"].append({"line": n, "name": title, "tags": tags,
                                          "rule": len(feat["rules"]) or None})
            tags = []
        out.append(feat)
    return out


def main() -> int:
    args = sys.argv[1:]
    only = set(args[args.index("--only") + 1:]) if "--only" in args else set()
    if "--only" in args:
        args = args[:args.index("--only")]
    root = Path(args[0] if args else ".").resolve()
    conf = rbtrc(root)
    base = (f"https://dashboard-{conf['name']}.localhost" if conf["portless"] and conf["name"]
            else "http://127.0.0.1:9871")
    lines = [f"Dashboard: {base}/"]
    page = f"{base}/#"  # the dashboard routes by hash
    for t in state_types(root, conf["api"], only):
        lines.append(f"- State type [{t['id']}]({page}/models/{t['id']}?type={t['id']}) ({t['file']})")
        for name, kind in t["methods"]:
            mid = f"{t['id']}.{name}"
            lines.append(f"  - {kind} [{name}]({page}/models/{mid}?type={mid})")
    for f in features(root, only):
        lines.append(f"- Feature [{f['name']}]({page}/features/{f['id']})")
        for r in f["rules"]:
            lines.append(f"  - Rule [{r['name'] or r['n']}]({page}/features/{f['id']}/rules/{r['n']})")
        for s in f["scenarios"]:
            tag = f" {' '.join(s['tags'])}" if s["tags"] else ""
            lines.append(f"  - Scenario [{s['name']}]({page}/features/{f['id']}/scenarios/{s['line']}){tag}")
    if not only:
        lines.append(f"- [Changelog]({page}/changelog)")
        if conf["name"] and conf["portless"]:
            lines.append(f"- The app: https://{conf['name']}.localhost/")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    sys.exit(main())
