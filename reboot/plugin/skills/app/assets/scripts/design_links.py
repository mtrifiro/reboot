#!/usr/bin/env python3
"""Check the design document's dashboard links against the code.

    scripts/design_links.py                  # check design/design.md, else the decisions log
    scripts/design_links.py --port 9873      # rewrite every link (and the log's) to that port, then check
    scripts/design_links.py --base https://dashboard-hotel.localhost
                                             # rewrite every link to that dashboard, then check

`design/design.md` links each package, domain object, method, feature
and rule to the developer dashboard, which draws them from the code:

    http://127.0.0.1:9871/#/models?type=<package>.<Type>[.<method>]
    http://127.0.0.1:9871/#/features/<path>.feature[/rules/<n>]

or, under portless, the same routes on `https://dashboard-<app>.localhost/`.

A package is the folder under `api/` (`api/rooms/v1/` is `rooms.v1`);
rules count from 1 in file order. This lists:

- **Broken:** a link to an object, method, feature file or rule
  number that doesn't exist.
- **Renumbered:** a rule link whose text is no longer its rule's words.
  When the words are another rule's in the same file, it says which
  number they have now (a rule inserted above renumbers those below).
- **Not linked:** a domain object, method, feature or rule the code
  has and the document doesn't link, or a `design/decisions.md` entry
  it doesn't link.
- **Decisions:** a link to `decisions.md#<anchor>` that no entry's
  heading makes, and in the newest entry (the log is never edited, so
  older entries keep what was true then) a dashboard link to nothing
  in the code, or to a rule by its number, which a later rule would
  shift.

With no `design/design.md` (the design is the code, and the log its
record: `design-document.md`), only the **Decisions** check runs, on
`design/decisions.md`'s newest entry.

It exits 0 when there is nothing to list, 1 otherwise, and 2 with
neither file.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import model_diff  # noqa: E402

ROOT = model_diff.ROOT
DOCUMENT = ROOT / "design" / "design.md"
DECISIONS = ROOT / "design" / "decisions.md"

ENTRY_LINK = re.compile(r"\]\((?:\./)?decisions\.md#([^)\s]+)\)")
# A dashboard link: on a plain port, or under portless by its name.
LINK = re.compile(
    r"\[([^\]]*)\]\(((?:http://(?:127\.0\.0\.1|localhost):(\d+)"
    r"|https://dashboard[.-][a-z0-9-]+\.localhost)/#/([^)\s]*))\)"
)
BASE = re.compile(r"(?:http://(?:127\.0\.0\.1|localhost):\d+|https://dashboard[.-][a-z0-9-]+\.localhost)/#/")


def package_of(path: str) -> str:
    """`api/rooms/v1/rooms.py` -> `rooms.v1`."""
    return ".".join(Path(path).parent.relative_to("api").parts)


def code() -> tuple[dict[str, set[str]], dict[str, list[str]]]:
    """({"<package>.<Type>": {methods}}, {"tests/x.feature": [rule, ...]})."""
    objects: dict[str, set[str]] = {}
    for path, source in model_diff.files_at(None, "api", ".py").items():
        types, _ = model_diff.model_of({path: source})
        for name, declared in types.items():
            objects[f"{package_of(path)}.{name}"] = set(declared["methods"])
    features = {
        path: [r for r in model_diff.parse_feature(text).rules if r]
        for path, text in model_diff.files_at(None, "tests", ".feature").items()
    }
    return objects, features


def anchors(log: str) -> list[tuple[str, str]]:
    """[(anchor, heading)] of the log's entries, as GitHub makes them:
    lowercase, punctuation dropped, each space a hyphen, a repeat -1."""
    seen: dict[str, int] = {}
    out = []
    for line in log.splitlines():
        if not line.startswith("## "):
            continue
        heading = line[3:].strip()
        slug = re.sub(r"[^\w\- ]", "", heading.lower()).replace(" ", "-")
        n = seen.get(slug, 0)
        seen[slug] = n + 1
        out.append((f"{slug}-{n}" if n else slug, heading))
    return out


def check_decisions(document: str, objects: dict[str, set[str]],
                    features: dict[str, list[str]]) -> tuple[list[str], list[str]]:
    """(problems, entries the document doesn't link)."""
    if not DECISIONS.exists():
        return [], []
    log = DECISIONS.read_text()
    entries = anchors(log)
    known = {a for a, _ in entries}
    problems = [
        f"line {n}: no entry in decisions.md has the anchor #{a}"
        for n, line in enumerate(document.splitlines(), 1)
        for a in ENTRY_LINK.findall(line) if a not in known
    ]
    linked = set(ENTRY_LINK.findall(document))
    unlinked = [f"decisions entry \"{h}\" (#{a})" for a, h in entries if a not in linked]
    if entries:
        newest = log[log.rindex("\n## " + entries[-1][1]) + 1:] if log.count("\n## ") else log
        for text, url, _, route in LINK.findall(newest):
            page, _, query = route.partition("?")
            where = f"newest entry: [{text}]({url})"
            if page == "models" and query.startswith("type="):
                name = query[len("type="):]
                owner, _, method = name.rpartition(".")
                if name not in objects and method not in objects.get(owner, ()):
                    problems.append(f"{where}: no object or method `{name}` in api/")
            elif page.startswith("features/"):
                path, _, rule = page[len("features/"):].partition("/rules/")
                if path not in features:
                    problems.append(f"{where}: no feature file `{path}`")
                elif rule:
                    problems.append(f"{where}: link the feature file, not rule {rule}; "
                                    "a rule added later would shift it")
    return problems, unlinked


def words(text: str) -> str:
    return re.sub(r"[\s`*_]+", " ", text).strip().rstrip(".").lower()


def check(document: str) -> dict[str, list[str]]:
    objects, features = code()
    found = {"Broken": [], "Renumbered": [], "Not linked": [], "Decisions": []}
    linked: set[str] = set()
    for n, line in enumerate(document.splitlines(), 1):
        for text, url, _, route in LINK.findall(line):
            where = f"line {n}: [{text}]({url})"
            page, _, query = route.partition("?")
            if page == "models" and query.startswith("type="):
                name = query[len("type="):]
                if name in objects:
                    linked.add(name)
                    continue
                owner, _, method = name.rpartition(".")
                if method in objects.get(owner, ()):
                    linked.add(name)
                    continue
                found["Broken"].append(f"{where}: no object or method `{name}` in api/")
            elif page.startswith("features/"):
                path, _, rule = page[len("features/"):].partition("/rules/")
                if path not in features:
                    found["Broken"].append(f"{where}: no feature file `{path}`")
                    continue
                if not rule:
                    linked.add(path)
                    continue
                rules = features[path]
                if not rule.isdigit() or not 1 <= int(rule) <= len(rules):
                    found["Broken"].append(f"{where}: `{path}` has {len(rules)} rules")
                    continue
                actual = rules[int(rule) - 1]
                said = words(text).removeprefix("rule: ")
                if said in (words(actual), ""):
                    linked.add(f"{path}/rules/{rule}")
                    continue
                now = [i for i, r in enumerate(rules, 1) if words(r) == said]
                # It links the rule its words name, at the wrong number.
                linked.add(f"{path}/rules/{now[0] if now else rule}")
                found["Renumbered"].append(
                    f"{where}: that rule is now /rules/{now[0]}" if now
                    else f"{where}: rule {rule} reads \"{actual}\""
                )
            # Other pages (#/models, #/features, #/changelog, ...) need no check.
    for name, methods in sorted(objects.items()):
        if name not in linked:
            found["Not linked"].append(f"object `{name}`")
        found["Not linked"] += [f"method `{name}.{m}`" for m in sorted(methods) if f"{name}.{m}" not in linked]
    for path, rules in sorted(features.items()):
        if path not in linked:
            found["Not linked"].append(f"feature `{path}`")
        found["Not linked"] += [
            f"rule `{path}/rules/{i}`: {r}" for i, r in enumerate(rules, 1)
            if f"{path}/rules/{i}" not in linked
        ]
    problems, unlinked = check_decisions(document, objects, features)
    found["Decisions"] += problems
    found["Not linked"] += unlinked
    return found


def check_log() -> int:
    """Only the newest decisions entry's links, when no design document exists."""
    objects, features = code()
    problems, _ = check_decisions("", objects, features)
    if not problems:
        print("Every dashboard link in design/decisions.md's newest entry names something in the code.")
        return 0
    print(f"**Decisions** ({len(problems)})")
    print("\n".join(f"- {i}" for i in problems))
    return 1


def main(argv: list[str]) -> int:
    if not DOCUMENT.exists() and not DECISIONS.exists():
        print(f"No {DOCUMENT.relative_to(ROOT)} or {DECISIONS.relative_to(ROOT)} to check.")
        return 2
    if argv[:1] == ["--port"] and len(argv) == 2 and argv[1].isdigit():
        # The log too: only the port changes, never an entry's words.
        for path in (DOCUMENT, DECISIONS):
            if path.exists():
                path.write_text(re.sub(r"http://(127\.0\.0\.1|localhost):\d+/#/",
                                       rf"http://\1:{argv[1]}/#/", path.read_text()))
    elif argv[:1] == ["--base"] and len(argv) == 2 and re.fullmatch(
            r"http://(?:127\.0\.0\.1|localhost):\d+|https://dashboard[.-][a-z0-9-]+\.localhost",
            argv[1].rstrip("/")):
        # Plain ports to portless, or back: only the base changes.
        for path in (DOCUMENT, DECISIONS):
            if path.exists():
                path.write_text(BASE.sub(argv[1].rstrip("/") + "/#/", path.read_text()))
    elif argv:
        print(__doc__)
        return 2
    if not DOCUMENT.exists():
        return check_log()
    found = check(DOCUMENT.read_text())
    if not any(found.values()):
        print("Every dashboard link in design/design.md names something in the code, "
              "everything in the code is linked, and so is every decisions entry.")
        return 0
    for heading, items in found.items():
        if items:
            print(f"**{heading}** ({len(items)})")
            print("\n".join(f"- {i}" for i in items))
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
