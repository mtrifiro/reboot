"""Records the last test run's results in `tests/.last-run.json`, as
evidence for the Reboot Flywheel's Prove stage: `scripts/model_diff.py`
says whether a run happened since the design was accepted, and which
scenarios passed at which revision. Imported by `conftest.py`;
git-ignored.

    {"when": "...", "revision": "abc1234", "dirty": false, "full": true,
     "tree": "<the working tree's git hash>",
     "passed": 12, "failed": 0, "wip": 2, "blocked": 1}

`full` is false when the run was narrowed (a path, `-k`, `-m`, a
deselect, an ignore, `--lf`, `--sw`, `--collect-only`): a partial run is
not evidence for a merge or a deploy. `exit` is pytest's status: an
interrupted or errored run is not evidence either. `failed` counts a
scenario marked `xfail` too: an expected failure is still a failure.
`tree` is the working tree as git would store it, every tracked and
untracked (not ignored) file included, so the record names exactly what
ran. `wip` counts scenarios tagged `@wip` that ran (they pass or fail
like any other); `blocked` counts `@blocked` ones, which are skipped
with their reason; `skipped` counts every other skip.

While a run is on, `tests/.suite-running` holds the pytest process's
pid, removed when the run ends, and `tests/.progress.jsonl` gains one
line per scenario as it finishes, so the build can report the run rule
by rule while it goes on:

    {"feature": "tests/room_status.feature", "rule": "Check-out always
     sends the room back to dirty", "scenario": "A guest checks out",
     "outcome": "passed", "seconds": 1.2}

`outcome` is passed, failed, blocked (with its `reason`) or skipped;
`rule` is "" for a scenario under no rule. The file starts empty at
each run."""

import json
import os
import subprocess
import tempfile
from datetime import datetime
from pathlib import Path

PATH = Path(__file__).resolve().parent / ".last-run.json"
RUNNING = Path(__file__).resolve().parent / ".suite-running"
PROGRESS = Path(__file__).resolve().parent / ".progress.jsonl"
_SESSION = None
_SCENARIOS: dict = {}


def _git(*args: str, env: dict | None = None, cwd: str | Path | None = None) -> str:
    try:
        return subprocess.run(
            ["git", *args], cwd=cwd or PATH.parent, capture_output=True, text=True, env=env
        ).stdout.strip()
    except OSError:
        return ""


def _tree() -> str:
    """The working tree's hash, through a scratch index so the real one
    is untouched; "" outside a repository."""
    root = _git("rev-parse", "--show-toplevel")
    if not root:
        return ""
    with tempfile.TemporaryDirectory() as tmp:
        env = {**os.environ, "GIT_INDEX_FILE": os.path.join(tmp, "index")}
        _git("add", "-A", "--", ".", env=env, cwd=root)
        return _git("write-tree", env=env, cwd=root)


# Options whose next argument is a value, not a path to run.
_TAKES_VALUE = {"-p", "-o", "-c", "-n", "-W", "-r", "--rootdir", "--deselect",
                "--ignore", "--ignore-glob", "--confcutdir", "--basetemp", "--junitxml",
                "--tb", "--recording-slowmo", "--recording-dwell"}
# Options that leave scenarios out, or stop before the end.
_NARROWS = {"-k", "-m", "--deselect", "--ignore", "--ignore-glob", "--lf", "--last-failed",
            "--sw", "--stepwise", "--co", "--collect-only"}


def _narrowed(args: list[str]) -> bool:
    """Whether the run was narrowed: to a path, by `-k`, `-m`, a deselect
    or ignore, a rerun of the last failures, stepwise, or collect-only."""
    previous = ""
    for arg in args:
        if previous in _TAKES_VALUE:
            previous = ""
            continue
        name = arg.split("=", 1)[0]
        if name in _NARROWS:
            return True
        if not arg.startswith("-"):
            return True
        previous = arg
    return False


def pytest_sessionstart(session) -> None:  # type: ignore[no-untyped-def]
    global _SESSION
    _SESSION = session
    _SCENARIOS.clear()
    try:
        PROGRESS.write_text("")
    except OSError:
        pass
    try:
        RUNNING.write_text(json.dumps({
            "pid": os.getpid(),
            "started": datetime.now().astimezone().isoformat(timespec="seconds"),
        }) + "\n")
    except OSError:
        pass


def _scenario(nodeid: str) -> dict:
    """The feature file, rule and scenario of a collected test, from
    pytest-bdd's `__scenario__`; {} for a test that isn't a scenario."""
    if not _SCENARIOS and _SESSION is not None:
        for item in getattr(_SESSION, "items", []):
            template = getattr(getattr(item, "obj", None), "__scenario__", None)
            if template is None:
                continue
            feature = template.feature
            path = getattr(feature, "rel_filename", None) or getattr(feature, "filename", "")
            _SCENARIOS[item.nodeid] = {
                "feature": str(path),
                "rule": template.rule.name if template.rule is not None else "",
                "scenario": template.name,
            }
    return _SCENARIOS.get(nodeid, {})


def pytest_runtest_logreport(report) -> None:  # type: ignore[no-untyped-def]
    # One line per scenario: its call's result, or a skip or an error
    # before the call.
    if report.when != "call" and not (report.when == "setup" and report.outcome != "passed"):
        return
    entry = _scenario(report.nodeid) or {"feature": "", "rule": "", "scenario": report.nodeid}
    outcome = report.outcome
    if outcome == "skipped" and "blocked" in report.keywords:
        outcome = "blocked"
    entry = {**entry, "outcome": outcome, "seconds": round(report.duration, 1)}
    if outcome in ("blocked", "skipped") and isinstance(report.longrepr, tuple):
        entry["reason"] = str(report.longrepr[-1]).removeprefix("Skipped: ")
    try:
        with PROGRESS.open("a") as out:
            out.write(json.dumps(entry) + "\n")
    except OSError:
        pass


def pytest_unconfigure(config) -> None:  # type: ignore[no-untyped-def]
    try:
        RUNNING.unlink()
    except OSError:
        pass


def pytest_terminal_summary(terminalreporter, exitstatus, config) -> None:  # type: ignore[no-untyped-def]
    stats = terminalreporter.stats
    calls = [
        r
        for key in ("passed", "failed")
        for r in stats.get(key, [])
        if getattr(r, "when", "") == "call"
    ]
    failed = (sum(1 for r in calls if r.outcome == "failed") + len(stats.get("error", []))
              + len(stats.get("xfailed", [])))
    skipped = stats.get("skipped", [])
    narrowed = _narrowed(list(config.invocation_params.args))
    record = {
        "when": datetime.now().astimezone().isoformat(timespec="seconds"),
        "revision": _git("rev-parse", "--short", "HEAD"),
        "dirty": bool(_git("status", "--porcelain", "--", "api", "backend", "tests", "web", "frontend")),
        "full": not narrowed,
        "exit": int(exitstatus),
        "tree": _tree(),
        "passed": sum(1 for r in calls if r.outcome == "passed"),
        "failed": failed,
        "wip": sum(1 for r in calls if "wip" in r.keywords),
        "blocked": sum(1 for r in skipped if "blocked" in r.keywords),
        "skipped": sum(1 for r in skipped if "blocked" not in r.keywords),
    }
    partial = PATH.with_suffix(".json.partial")
    partial.write_text(json.dumps(record, indent=2) + "\n")
    os.replace(partial, PATH)
