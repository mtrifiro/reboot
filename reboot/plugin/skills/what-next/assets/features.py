#!/usr/bin/env python3
"""What a Reboot app has built and planned, for the what-next skill.

    python3 features.py            # Markdown, from the project root
    python3 features.py --json

Reads `tests/**/*.feature` (each feature, its rules, how many scenarios
each rule has, and its tags: @wip, @browser, @blocked), and from
`design/design.md` the people the brief names, the cycles it names
(written as *a → b → c*), and every name still in code style (`like
this`), which the design uses for what isn't built yet. Also lists
what `design/decisions.md` records as ruled out. Standard library only.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

TESTS, DESIGN = Path("tests"), Path("design")


def features() -> list[dict]:
    out = []
    for path in sorted(TESTS.rglob("*.feature")) if TESTS.is_dir() else []:
        text = path.read_text(encoding="utf-8", errors="replace")
        name = re.search(r"^\s*Feature:\s*(.+)$", text, re.M)
        rules, current = [], None
        tags_above: list[str] = []
        for line in text.splitlines():
            s = line.strip()
            if s.startswith("@"):
                tags_above = s.split()
            elif s.startswith("Rule:"):
                current = {"rule": s[5:].strip(), "scenarios": 0, "tags": []}
                rules.append(current)
                tags_above = []
            elif re.match(r"(Scenario|Scenario Outline|Example):", s):
                if current is None:
                    current = {"rule": "(no rule)", "scenarios": 0, "tags": []}
                    rules.append(current)
                current["scenarios"] += 1
                current["tags"] += [t for t in tags_above if t not in current["tags"]]
                tags_above = []
        feature_tags = re.findall(r"^(@[\w-]+(?:\s+@[\w-]+)*)\s*\n\s*Feature:", text, re.M)
        out.append({
            "file": str(path),
            "feature": name.group(1).strip() if name else path.stem,
            "tags": feature_tags[0].split() if feature_tags else [],
            "rules": rules,
        })
    return out


def design() -> dict:
    found: dict = {"people": [], "cycles": [], "not_built": [], "ruled_out": []}
    doc = DESIGN / "design.md"
    if doc.is_file():
        text = doc.read_text(encoding="utf-8", errors="replace")
        brief = text.split("## ", 2)[1] if text.count("## ") >= 1 else text
        found["cycles"] = [" ".join(c.split()) for c in re.findall(r"\*([^*]*→[^*]*)\*", text)]
        people = re.findall(
            r"\b(?:the )?(front desk|housekeeping|concierge|manager|guests?|staff|admin\w*|customers?|"
            r"members?|owners?|drivers?|patients?|doctors?|nurses?|teachers?|students?|buyers?|sellers?)\b",
            brief, re.I)
        found["people"] = sorted({p.lower().rstrip("s") if p.lower() != "staff" else "staff" for p in people})
        # Names in code style that aren't links: the design's "not built yet".
        found["not_built"] = sorted({m for m in re.findall(r"(?<!\[)`([A-Za-z_][\w.]*)`(?!\])", text)})
    log = DESIGN / "decisions.md"
    if log.is_file():
        for line in log.read_text(encoding="utf-8", errors="replace").splitlines():
            if re.search(r"\b(not|never|no longer|dropped|ruled out|declined|won't)\b", line, re.I):
                found["ruled_out"].append(line.strip()[:200])
    return found


def markdown(fs: list[dict], d: dict) -> str:
    out = ["# What the app has", "", "## Features built", ""]
    for f in fs:
        n = sum(r["scenarios"] for r in f["rules"])
        tags = f" {' '.join(f['tags'])}" if f["tags"] else ""
        out.append(f"- **{f['feature']}**{tags}: {len(f['rules'])} rules, {n} scenarios ({f['file']})")
        for r in f["rules"]:
            t = f" {' '.join(r['tags'])}" if r["tags"] else ""
            out.append(f"  - {r['rule']} ({r['scenarios']}){t}")
    if not fs:
        out.append("- none yet")
    out += ["", "## From the design", ""]
    out.append("- People: " + (", ".join(d["people"]) or "not named"))
    out.append("- Cycles: " + ("; ".join(d["cycles"]) or "none written as a → b"))
    out.append("- Named in code style (not built yet, or not linked): "
               + (", ".join(f"`{n}`" for n in d["not_built"][:40]) or "none"))
    if d["ruled_out"]:
        out += ["", "## Lines in decisions.md that may rule something out (check each)", ""]
        out += [f"- {line}" for line in d["ruled_out"][:20]]
    return "\n".join(out)


def main(argv: list[str]) -> int:
    fs, d = features(), design()
    print(json.dumps({"features": fs, "design": d}, indent=2) if "--json" in argv else markdown(fs, d))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
