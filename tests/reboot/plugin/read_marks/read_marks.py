"""What real builds read of the reading path, from their transcripts.

`reading_budget.py` says what a build that follows the skills exactly
reads before it writes code. This report says what builds on this
machine actually opened, so the two can be compared: a skill or
reference every build is meant to read that most builds never open is
a rule not reaching them, and a conditional reference every build opens
anyway is words on the real path that the minimal count leaves out.

    bazel run //tests/reboot/plugin/read_marks:read_marks -- \\
        [--since 2026-10-01] [--min-read 12] [--plugin other|all] [--json]

It reads Claude Code's transcripts (`~/.claude/projects/<project>/
<session>.jsonl`, with each session's sub-agents, or `--transcripts`).
A build is a project whose sessions, taken together, loaded a front
door's skill and read at least `--min-read` items of that front door's
path whole: an aborted start or a continuation after compaction is not
a build on its own. A project that loaded both front doors is compared
against both paths.

A mark is the strongest thing a build did with a file:

* "read": the `Skill` tool or a skill's body taken in, `Read` without
  a range, or `cat`;
* "part": `Read` with an offset or limit, `head`, `tail`, `sed -n`;
* "searched": `Grep` or `Glob` naming it, or `grep`, `rg`, `ls`;
* "never".

Content that reached the agent another way is not seen.

Builds are split by the plugin they ran. A build that loaded only
skills this checkout has ran this checkout's lists (`this`); one that
loaded a skill this checkout doesn't have ran another package
(`other`), whose lists differ, so its "never" on a file here can mean
"not on its list" rather than "skipped". The report shows `this` by
default.

Read-only, and not a check: a report for judging the reading lists.
"""

import argparse
import collections
import json
import os
import re
import sys
from collections.abc import Iterator
from dataclasses import dataclass, field
from datetime import date, timedelta
from pathlib import Path
from tests.reboot.plugin.build_metrics import build_metrics
from tests.reboot.plugin.reading_budget import reading_budget

# The skill names a build loads to take a front door.
DOORS = reading_budget.FRONT_DOORS

# A skill's body arrives as the person's text, headed by its folder.
SKILL_BODY = re.compile(
    r"Base directory for this skill: \S[^\n]*?/skills/([a-z0-9-]+)"
)

# A file under a plugin's `skills/` folder, as a tool call names it:
# `.../reboot/plugin/skills/python/references/api-methods.md`.
SKILL_FILE = re.compile(r"/skills/([a-z0-9-]+/[^\s'\"`;|&()<>*]+?\.md)\b")

MARKS = ("read", "part", "searched", "never")

# The shell commands that read a file whole, read part of it, or only
# look for it.
SHELL_READ = re.compile(r"(?:^|[|;&]\s*|\s)cat\s")
SHELL_PART = re.compile(r"(?:^|[|;&]\s*|\s)(?:head|tail|sed\s+-n)\b")
SHELL_SEARCH = re.compile(r"(?:^|[|;&]\s*|\s)(?:grep|rg|ls|find)\b")


@dataclass
class Session:
    """What one session (with its sub-agents) did with the skills."""

    project: str
    started: str  # YYYY-MM-DD
    skills: set[str] = field(default_factory=set)
    # Skills-relative path -> the marks it got.
    marks: dict[str, set[str]] = field(
        default_factory=lambda: collections.defaultdict(set)
    )


def skill_name(name: str) -> str:
    """`reboot:web-app` -> `web-app`."""
    return name.rsplit(":", 1)[-1]


def call_marks(name: str, args: dict) -> Iterator[tuple[str, str]]:
    """(skills-relative path, mark) for each skill file a tool call
    touches."""
    if name == "Skill":
        skill = skill_name(str(args.get("skill") or ""))
        if skill:
            yield f"{skill}/SKILL.md", "read"
        return
    if name == "Read":
        path = str(args.get("file_path") or "")
        mark = "part" if args.get("offset") or args.get("limit") else "read"
        for found in SKILL_FILE.findall(path):
            yield found, mark
        return
    if name in ("Grep", "Glob"):
        named = " ".join(
            str(args.get(key) or "") for key in ("path", "pattern", "glob")
        )
        for found in SKILL_FILE.findall(named):
            yield found, "searched"
        return
    if name == "Bash":
        command = str(args.get("command") or "")
        # One command can do several things; each file takes the
        # strongest thing done in the segment that names it.
        for segment in re.split(r"&&|\|\||;|\n", command):
            if SHELL_READ.search(segment):
                mark = "read"
            elif SHELL_PART.search(segment):
                mark = "part"
            elif SHELL_SEARCH.search(segment):
                mark = "searched"
            else:
                continue
            for found in SKILL_FILE.findall(segment):
                yield found, mark


def read_session(path: Path) -> Session:
    files = [path, *sorted(path.with_suffix("").glob("subagents/*.jsonl"))]
    session = Session(project=path.parent.name, started="")
    for file in files:
        for record in build_metrics.lines(file):
            at = build_metrics.parse_time(record)
            if at is not None and not session.started:
                session.started = at.date().isoformat()
            message = record.get("message")
            content = message.get("content") if isinstance(
                message, dict
            ) else None
            if record.get("type") == "assistant" and isinstance(content, list):
                for block in content:
                    if not isinstance(block, dict):
                        continue
                    if block.get("type") != "tool_use":
                        continue
                    args = block.get("input")
                    args = args if isinstance(args, dict) else {}
                    name = str(block.get("name"))
                    if name == "Skill":
                        session.skills.add(
                            skill_name(str(args.get("skill") or ""))
                        )
                    for found, mark in call_marks(name, args):
                        session.marks[found].add(mark)
            elif record.get("type") == "user":
                text = build_metrics.text_of(content)
                for skill in SKILL_BODY.findall(text):
                    session.skills.add(skill)
                    session.marks[f"{skill}/SKILL.md"].add("read")
    return session


def strongest(marks: set[str]) -> str:
    return next((m for m in MARKS if m in marks), "never")


@dataclass(frozen=True)
class Item:
    """One file on a front door's reading path."""

    path: str  # relative to the skills folder
    step: str  # "skill", or the reading list's step
    conditional: bool


def path_items(skills: Path, door: str) -> list[Item]:
    items = [
        Item(f"{skill}/SKILL.md", "skill", False)
        for skill in reading_budget.SKILLS_LOADED[door]
    ]
    conditional = reading_budget.CONDITIONAL[door]
    for entry in reading_budget.reading_list(skills, door):
        if entry.path:
            items.append(
                Item(entry.path, entry.step, entry.path in conditional)
            )
    return items


def doors_items(skills: Path, doors: set[str]) -> list[Item]:
    """Every item of each door's path, each once, a file conditional
    only when it is conditional for every door that lists it."""
    found: dict[str, Item] = {}
    for door in sorted(doors):
        for item in path_items(skills, door):
            if item.path in found:
                if not item.conditional:
                    found[item.path] = Item(
                        item.path, found[item.path].step, False
                    )
            else:
                found[item.path] = item
    return list(found.values())


def report(
    skills: Path,
    sessions: list[Session],
    min_read: int,
    plugin: str,
) -> dict:
    own = {p.parent.name for p in skills.glob("*/SKILL.md")}

    # One build per project and plugin: the union of its sessions.
    projects: dict[tuple[str, str], dict] = collections.defaultdict(
        lambda: {
            "marks": collections.defaultdict(set),
            "skills": set(),
            "dates": set(),
            "sessions": 0,
        }
    )
    for s in sessions:
        which = "this" if s.skills <= own else "other"
        p = projects[(which, s.project)]
        p["sessions"] += 1
        p["skills"] |= s.skills
        p["dates"].add(s.started)
        for path, marks in s.marks.items():
            p["marks"][path] |= marks

    wanted = {"this": {"this"}, "other": {"other"}, "all": {"this", "other"}}
    builds: list[dict] = []
    counted: collections.Counter = collections.Counter()
    tally: dict[str, collections.Counter] = collections.defaultdict(
        collections.Counter
    )
    meta: dict[str, Item] = {}
    for (which, project), p in sorted(
        projects.items(), key=lambda kv: min(kv[1]["dates"])
    ):
        doors = p["skills"] & set(DOORS)
        if not doors:
            continue
        items = doors_items(skills, doors)
        marks = {i.path: strongest(p["marks"].get(i.path, set())) for i in items}
        read_whole = sum(1 for m in marks.values() if m == "read")
        if read_whole < min_read:
            continue
        counted[which] += 1
        if which not in wanted[plugin]:
            continue
        builds.append(
            {
                "date": min(p["dates"]),
                "project": project,
                "plugin": which,
                "doors": sorted(doors),
                "sessions": p["sessions"],
                "read_whole": read_whole,
                "never": sum(
                    1 for i in items
                    if not i.conditional and marks[i.path] == "never"
                ),
            }
        )
        for item in items:
            meta[item.path] = item
            tally[item.path][marks[item.path]] += 1

    rows = []
    for path, c in tally.items():
        item = meta[path]
        rows.append(
            {
                "path": path,
                "step": item.step,
                "conditional": item.conditional,
                "builds": sum(c.values()),
                **{mark: c[mark] for mark in MARKS},
            }
        )
    return {
        "builds_by_plugin": dict(counted),
        "builds": builds,
        "every_build": sorted(
            (r for r in rows if not r["conditional"]),
            key=lambda r: (-r["never"] / r["builds"], r["step"], r["path"]),
        ),
        "conditional": sorted(
            (r for r in rows if r["conditional"]),
            key=lambda r: (-r["read"], r["path"]),
        ),
    }


def sessions_since(transcripts: Path, since: str) -> list[Session]:
    found = []
    for file in sorted(transcripts.glob("*/*.jsonl")):
        session = read_session(file)
        if session.started and session.started >= since and (
            session.skills & set(DOORS)
        ):
            found.append(session)
    return found


def print_report(result: dict, since: str, min_read: int, plugin: str) -> None:
    counted = ", ".join(
        f"{k} {v}" for k, v in sorted(result["builds_by_plugin"].items())
    ) or "none"
    print(
        f"builds since {since} (>= {min_read} items read whole): {counted};"
        f" shown: {plugin}"
    )
    builds = result["builds"]
    if not builds:
        return
    print(
        "\nbuilds: date, project, plugin, front doors, sessions, items read"
        " whole, items every build reads that it never opened"
    )
    for b in builds:
        print(
            f"  {b['date']}  {b['project'][-32:]:<32} {b['plugin']:<5} "
            f"{'+'.join(b['doors']):<15} {b['sessions']:>2} "
            f"{b['read_whole']:>3} {b['never']:>3}"
        )
    print("\nitems every build reads, by share of builds that never opened them")
    print(
        f"  {'never':>5} {'step':<16} {'builds':>6} {'read':>4} {'part':>4}"
        f" {'srch':>4} {'never':>5}  path"
    )
    for r in result["every_build"]:
        print(
            f"  {r['never'] / r['builds'] * 100:4.0f}% {r['step'][:16]:<16}"
            f" {r['builds']:>6} {r['read']:>4} {r['part']:>4}"
            f" {r['searched']:>4} {r['never']:>5}  {r['path']}"
        )
    read_anyway = [r for r in result["conditional"] if r["read"]]
    if read_anyway:
        print("\nconditional references read whole anyway (builds read / builds):")
        for r in read_anyway:
            print(f"  {r['read']:>3}/{r['builds']:<3} {r['path']}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument(
        "--since",
        default=(date.today() - timedelta(days=30)).isoformat(),
        help="first session date to count (YYYY-MM-DD; default 30 days ago)",
    )
    parser.add_argument(
        "--min-read",
        type=int,
        default=12,
        help="items of the path a project must have read whole to count",
    )
    parser.add_argument(
        "--transcripts",
        default=str(Path.home() / ".claude" / "projects"),
    )
    parser.add_argument(
        "--plugin",
        choices=("this", "other", "all"),
        default="this",
        help="builds that ran this checkout's skills, another package's, or all",
    )
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    # Under `bazel run`, the checkout is BUILD_WORKSPACE_DIRECTORY.
    root = Path(os.environ.get("BUILD_WORKSPACE_DIRECTORY", "."))
    skills = Path(
        os.environ.get(
            "REBOOT_PLUGIN_SKILLS", str(root / "reboot/plugin/skills")
        )
    )
    if not skills.is_dir():
        print(f"read_marks: no skills folder at {skills}", file=sys.stderr)
        return 2
    sessions = sessions_since(Path(args.transcripts).expanduser(), args.since)
    result = report(skills, sessions, args.min_read, args.plugin)
    if args.json:
        print(json.dumps({"since": args.since, **result}, indent=2))
    else:
        print_report(result, args.since, args.min_read, args.plugin)
    return 0


if __name__ == "__main__":
    sys.exit(main())
