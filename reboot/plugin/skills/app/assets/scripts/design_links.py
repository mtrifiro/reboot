#!/usr/bin/env python3
"""Check the design document's dashboard links against the code.

    scripts/design_links.py                  # check design/design.md
    scripts/design_links.py --port 9873      # rewrite every link to that port, then check

`design/design.md` links each package, domain object, method, feature
and rule to the developer dashboard, which draws them from the code:

    http://127.0.0.1:9871/#/models?type=<package>.<Type>[.<method>]
    http://127.0.0.1:9871/#/features/<path>.feature[/rules/<n>]

A package is the folder under `api/` (`api/rooms/v1/` is `rooms.v1`);
rules count from 1 in file order. This lists:

- **Broken:** a link to an object, method, feature file or rule
  number that doesn't exist.
- **Renumbered:** a rule link whose text is no longer its rule's words.
  When the words are another rule's in the same file, it says which
  number they have now (a rule inserted above renumbers those below).
- **Not linked:** a domain object, method, feature or rule the code
  has and the document doesn't link.

It exits 0 when there is nothing to list, 1 otherwise, and 2 with no
`design/design.md`.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import model_diff  # noqa: E402

ROOT = model_diff.ROOT
DOCUMENT = ROOT / "design" / "design.md"

LINK = re.compile(r"\[([^\]]*)\]\((http://(?:127\.0\.0\.1|localhost):(\d+)/#/([^)\s]*))\)")


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


def words(text: str) -> str:
    return re.sub(r"[\s`*_]+", " ", text).strip().rstrip(".").lower()


def check(document: str) -> dict[str, list[str]]:
    objects, features = code()
    found = {"Broken": [], "Renumbered": [], "Not linked": []}
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
    return found


def main(argv: list[str]) -> int:
    if not DOCUMENT.exists():
        print(f"No {DOCUMENT.relative_to(ROOT)} to check.")
        return 2
    if argv[:1] == ["--port"] and len(argv) == 2 and argv[1].isdigit():
        text = re.sub(r"http://(127\.0\.0\.1|localhost):\d+/#/", rf"http://\1:{argv[1]}/#/",
                      DOCUMENT.read_text())
        DOCUMENT.write_text(text)
    elif argv:
        print(__doc__)
        return 2
    found = check(DOCUMENT.read_text())
    if not any(found.values()):
        print("Every dashboard link in design/design.md names something in the code, "
              "and everything in the code is linked.")
        return 0
    for heading, items in found.items():
        if items:
            print(f"**{heading}** ({len(items)})")
            print("\n".join(f"- {i}" for i in items))
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
