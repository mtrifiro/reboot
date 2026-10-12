#!/usr/bin/env python3
"""How a build went, from its Claude Code transcript: the numbers every
change to the plugin is judged by against a baseline build.

Usage:
    tools/check-transcript.py <transcript.jsonl | project folder>
    tools/check-transcript.py <build> --baseline <build>   # exit 1 if worse

A project folder means its newest session under ~/.claude/projects.
The rest of this docstring is the measure's own (it is the same code
the Plugin Browser's Next page uses, backend/src/build_metrics.py).

How a build went, in the numbers the reboot-next rebuild is judged by
(`~/projects/reboot-next/docs/next-plan.md`, "The test"), read from its
transcript and never typed in.

Times are active time: seconds from the first record, less the time the
user spent answering questions, since a build that waits on a person is
not slower for it. A wait is an `AskUserQuestion` call to its result.

- `questions`: questions asked (`AskUserQuestion`, each question
  counted) before the API file was written.
- `design_s`: until the first message to the user of at least
  `DESIGN_WORDS` words, the first time the design is laid out.
- `api_s`: until the first write of a Python file under `api/`.
- `green_s`: until the first test run that passed with nothing failed.
- `passed`: scenarios passed in the last test run that reported a count.
- `errors`: tool results that failed or carry a traceback, with the
  first line of each (`error_lines`).
- `words_before_api`: words the agent took in before the API file: skill
  bodies loaded and every tool result.
- `plugin`: where its skills came from: a checkout by name, a
  marketplace install, or an upload to the Claude app.

-1 means it never happened in the transcript. This reads the transcript
and never writes it.
"""

import json
import re
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Iterator, Optional

DESIGN_WORDS = 200
API_FILE = re.compile(r"(?:^|/)api/\S+\.py$")
API_IN_SHELL = re.compile(r">\s*\S*\bapi/\S+\.py\b")
PASSED = re.compile(r"\b(\d+) passed\b")
FAILED = re.compile(r"\b\d+ (?:failed|error|errors)\b")
SKILL_BASE = re.compile(r"Base directory for this skill: (\S[^\n]*?)/skills/[a-z-]+")
DECLINED = "doesn't want to proceed"


@dataclass
class Metrics:
    plugin: str = ""
    questions: int = 0
    design_s: int = -1
    api_s: int = -1
    green_s: int = -1
    passed: int = 0
    errors: int = 0
    error_lines: list[str] = field(default_factory=list)
    words_before_api: int = 0
    answered: list[str] = field(default_factory=list)
    design: str = ""


def records(path: Path) -> Iterator[dict]:
    with path.open(encoding="utf-8", errors="replace") as f:
        for line in f:
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(record, dict):
                yield record


def when(record: dict) -> Optional[datetime]:
    stamp = str(record.get("timestamp") or "")
    try:
        return datetime.fromisoformat(stamp.replace("Z", "+00:00"))
    except ValueError:
        return None


def text_of(content: object) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "\n".join(text_of(b.get("text") if isinstance(b, dict) and "text" in b else b.get("content") if isinstance(b, dict) else b) for b in content)
    return ""


def plugin_source(base: str) -> str:
    """Where a skill's base directory says the plugin came from."""
    if "local-agent-mode-sessions" in base:
        return "Claude app upload"
    cache = re.search(r"/plugins/cache/([^/]+)/", base)
    if cache:
        return f"{cache.group(1)} (installed)"
    market = re.search(r"/plugins/marketplaces/([^/]+)", base)
    if market:
        return f"{market.group(1)} (installed)"
    return Path(base).name


def is_api_write(name: str, args: dict) -> bool:
    if name in ("Write", "Edit", "MultiEdit"):
        return bool(API_FILE.search(str(args.get("file_path", ""))))
    if name == "Bash":
        return bool(API_IN_SHELL.search(str(args.get("command", ""))))
    return False


def read(path: Path) -> Metrics:
    m = Metrics()
    start: Optional[datetime] = None
    asked: dict[str, datetime] = {}
    waits: list[tuple[datetime, datetime]] = []
    api_at: Optional[datetime] = None

    def active(at: datetime) -> int:
        assert start is not None
        waited = sum(
            (min(end, at) - begin).total_seconds()
            for begin, end in waits
            if begin < at
        )
        return max(0, round((at - start).total_seconds() - waited))

    for record in records(path):
        at = when(record)
        if at is None:
            continue
        if start is None:
            start = at
        message = record.get("message") or {}
        content = message.get("content") if isinstance(message, dict) else None
        kind = record.get("type")
        if kind == "assistant" and isinstance(content, list):
            for block in content:
                if not isinstance(block, dict):
                    continue
                if block.get("type") == "text":
                    words = len(str(block.get("text", "")).split())
                    if m.design_s < 0 and words >= DESIGN_WORDS:
                        m.design_s = active(at)
                        m.design = str(block["text"])
                elif block.get("type") == "tool_use":
                    name, args = str(block.get("name")), block.get("input") or {}
                    if name == "AskUserQuestion":
                        asked[str(block.get("id"))] = at
                        if api_at is None:
                            m.questions += len(args.get("questions") or [])
                    elif api_at is None and is_api_write(name, args):
                        api_at = at
                        m.api_s = active(at)
        elif kind == "user":
            if isinstance(content, str) or record.get("isMeta"):
                body = text_of(content)
                base = SKILL_BASE.search(body)
                if base and not m.plugin:
                    m.plugin = plugin_source(base.group(1))
                if api_at is None and base:
                    m.words_before_api += len(body.split())
                continue
            if not isinstance(content, list):
                continue
            for block in content:
                if not isinstance(block, dict):
                    continue
                if block.get("type") == "text":
                    body = str(block.get("text", ""))
                    base = SKILL_BASE.search(body)
                    if base:
                        if not m.plugin:
                            m.plugin = plugin_source(base.group(1))
                        if api_at is None:
                            m.words_before_api += len(body.split())
                    continue
                if block.get("type") != "tool_result":
                    continue
                result = text_of(block.get("content"))
                tool_id = str(block.get("tool_use_id"))
                if tool_id in asked:
                    waits.append((asked.pop(tool_id), at))
                    if "answered" in result:
                        m.answered.append(result.strip()[:600])
                    continue
                if api_at is None:
                    m.words_before_api += len(result.split())
                if (block.get("is_error") and DECLINED not in result) or "Traceback (most recent call last)" in result:
                    m.errors += 1
                    first = next((line.strip() for line in reversed(result.splitlines()) if line.strip()), "")
                    if len(m.error_lines) < 20:
                        m.error_lines.append(first[:200])
                counts = PASSED.findall(result)
                if counts:
                    m.passed = int(counts[-1])
                    if m.green_s < 0 and not FAILED.search(result):
                        m.green_s = active(at)
    return m


# What "no worse than the baseline" allows: a time may run this much
# over before it counts as worse, since two runs of one prompt vary.
SLACK = 1.10

# The numbers a layer's test compares, in order, and which way is better.
COMPARED = (
    ("questions", "Questions before code", "fewer"),
    ("design_s", "Active time to the design", "sooner"),
    ("api_s", "Active time to the API file", "sooner"),
    ("green_s", "Active time to the first passing scenario", "sooner"),
    ("words_before_api", "Words taken in before the API file", "fewer"),
    ("errors", "Errors hit", "fewer"),
)

# Of those, the ones a layer's test needs no worse.
GATED = ("questions", "design_s", "api_s", "green_s")


def worse(key: str, value: int, baseline: int) -> bool:
    """Whether `value` is worse than the baseline's. A step that never
    happened (-1) is worse when the baseline reached it."""
    if baseline < 0:
        return False
    if value < 0:
        return True
    if key in ("questions", "errors"):
        return value > baseline
    return value > baseline * SLACK


def transcript_for(arg: str) -> Path:
    path = Path(arg).expanduser()
    if path.is_file():
        return path
    folder = Path.home() / ".claude" / "projects" / str(path.resolve()).replace("/", "-").replace(".", "-")
    sessions = sorted(folder.glob("*.jsonl"), key=lambda p: p.stat().st_mtime)
    if not sessions:
        raise SystemExit(f"no transcript for {arg} (looked in {folder})")
    return sessions[-1]


def show(seconds: int) -> str:
    return "never" if seconds < 0 else f"{seconds // 60}m {seconds % 60:02d}s"


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description="How a build went, from its transcript.")
    parser.add_argument("build", help="a transcript .jsonl, or the project folder it ran in")
    parser.add_argument("--baseline", help="a build to compare with; exit 1 when worse on a gated number")
    args = parser.parse_args()
    build = read(transcript_for(args.build))
    base = read(transcript_for(args.baseline)) if args.baseline else None
    print(f"plugin: {build.plugin or '?'}")
    worse_on = []
    for key, label, _ in COMPARED + (("passed", "Scenarios passed, last run", "more"),):
        value = getattr(build, key)
        shown = show(value) if key.endswith("_s") else f"{value:,}"
        line = f"{label:<44} {shown:>10}"
        if base is not None:
            was = getattr(base, key)
            line += f"   baseline {show(was) if key.endswith('_s') else f'{was:,}':>10}"
            if key != "passed" and worse(key, value, was):
                line += "   WORSE" + (" (gated)" if key in GATED else "")
                if key in GATED:
                    worse_on.append(key)
        print(line)
    for err in build.error_lines:
        print(f"  error: {err}")
    return 1 if worse_on else 0


if __name__ == "__main__":
    raise SystemExit(main())
