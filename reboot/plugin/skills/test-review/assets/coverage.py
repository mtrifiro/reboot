#!/usr/bin/env python3
"""The facts a test review starts from, read from a Reboot app's code and tests.

    python3 coverage.py              # Markdown, from the project root
    python3 coverage.py --json       # the same facts as JSON

Reads the API (`api/**/*.py`), the servicers (`backend/src/**/*.py`),
the feature files (`tests/**/*.feature`) and the frontend's pages, and
prints:

- each scenario: its file and line, its rule, its tags, the methods it
  calls or reads, the errors it expects, and whether it is a browser
  scenario;
- each API method: the scenarios that call it, the declared errors no
  scenario expects, and whether any scenario shows a caller refused
  (`PermissionDenied`, `Unauthenticated`);
- each rule: its scenarios, and whether one of them shows the rule
  refusing (an `attempts` that aborts);
- each state value the servicers set (`state.step = "dirty"`) and
  whether a scenario ever asserts it;
- each page and the browser scenarios beside it;
- signals, each with an id (T1, T2, ...), its evidence, and the
  question that decides it. A signal is a place to look, not a
  verdict: a gap matters when a person would be hurt by it.

Uses the domain-review skill's `review.py` for the parsing. Standard
library only. Never imports the app, never runs the tests.
"""

from __future__ import annotations

import ast
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "domain-review" / "assets"))
import review as domain  # noqa: E402

API, BACKEND, TESTS = domain.API, domain.BACKEND, domain.TESTS
FRONTEND = Path("frontend")
REFUSED = ("PermissionDenied", "Unauthenticated")
FACTORIES = ("Reader", "Writer", "Transaction", "Workflow")

CALL = re.compile(r"\b(does|attempts) an? `(\w+)`.*? on `(\w+)`")
READ = re.compile(r"`(\w+)`(?: with [^\n]*?)? on the `(\w+)`")
WEB = re.compile(r"\bin the web app\b|\bopens the web app\b")
PERSON = re.compile(r"\"(\w+)\" (?:is an (?:un)?authenticated user|signs in as)")
ABORT = re.compile(r"aborts with `(\w+)`")
VALUE = re.compile(r"`?([\w.\[\]]+)=\"([^\"]*)\"`?")


def methods_with_errors(api: dict[str, str]) -> dict[str, dict]:
    """{"Type.method": {"kind", "errors": [...]}} from each API's `Type(methods=...)`."""
    out: dict[str, dict] = {}
    for source in api.values():
        tree = domain.parse(source)
        if tree is None:
            continue
        named = {t.id: n.value for n in tree.body if isinstance(n, ast.Assign)
                 for t in n.targets if isinstance(t, ast.Name)}

        def resolve(v):
            return named.get(v.id, v) if isinstance(v, ast.Name) else v

        for node in ast.walk(tree):
            if not (isinstance(node, ast.Call) and domain.name_of(node) == "API"):
                continue
            for type_name, declared in domain.keywords(node).items():
                value = resolve(declared)
                if not (isinstance(value, ast.Call) and domain.name_of(value) == "Type"):
                    continue
                holder = resolve(domain.keywords(value).get("methods"))
                if not isinstance(holder, ast.Call):
                    continue
                for method, factory in domain.keywords(holder).items():
                    if not (isinstance(factory, ast.Call) and domain.name_of(factory) in FACTORIES):
                        continue
                    errs = domain.keywords(factory).get("errors")
                    names = [domain.literal(e).split(".")[-1] for e in errs.elts] \
                        if isinstance(errs, (ast.List, ast.Tuple)) else []
                    out[f"{type_name}.{method}"] = {"kind": domain.name_of(factory), "errors": names}
    return out


def scenarios_of(features: dict[str, str]) -> tuple[list[dict], list[dict]]:
    scenarios, rules = [], []
    for path, text in features.items():
        rule = None
        feature_tags: list[str] = []
        tags: list[str] = []
        current = None
        background: list[str] = []
        in_background = False
        for i, line in enumerate(text.splitlines(), 1):
            s = line.strip()
            if not s or s.startswith("#"):
                continue
            if s.startswith("@"):
                tags += s.split()
                continue
            if s.startswith("Feature:"):
                feature_tags, tags = tags, []
                continue
            if s.startswith("Background:"):
                in_background, current = True, None
                continue
            if s.startswith("Rule:"):
                rule = {"file": path, "line": i, "rule": s[5:].strip(), "scenarios": []}
                rules.append(rule)
                in_background, current, tags = False, None, []
                continue
            if s.startswith(("Scenario:", "Scenario Outline:", "Example:")):
                in_background = False
                current = {"file": path, "line": i, "name": s.split(":", 1)[1].strip(),
                           "rule": rule["rule"] if rule else "", "tags": feature_tags + tags,
                           "browser": False, "steps": []}
                tags = []
                scenarios.append(current)
                if rule:
                    rule["scenarios"].append(current["name"])
                continue
            if in_background:
                background.append(s)
            elif current is not None:
                current["steps"].append(s)
        for sc in scenarios:
            if sc["file"] == path:
                sc["background"] = background
    for sc in scenarios:
        steps = sc.get("background", []) + sc["steps"]
        calls, attempts, reads, aborts, values = set(), set(), set(), set(), set()
        for st in steps:
            for verb, m, t in CALL.findall(st):
                (attempts if verb == "attempts" else calls).add(f"{t}.{m}")
            for m, t in READ.findall(st):
                reads.add(f"{t}.{m}")
            aborts |= set(ABORT.findall(st))
            for field, v in VALUE.findall(st):
                values.add((field.split(".")[-1].split("[")[0], v))
        # A read that aborts is attempted too: "`get` on the `Room` for "x" aborts with ...".
        for st in sc["steps"]:
            if ABORT.search(st):
                for m, t in READ.findall(st):
                    attempts.add(f"{t}.{m}")
        sc["browser"] = any(WEB.search(st) for st in sc["steps"])
        sc.update(calls=sorted(calls), attempts=sorted(attempts), reads=sorted(reads),
                  aborts=sorted(aborts), values=sorted(values))
        sc.pop("background", None)
        sc.pop("steps", None)
    return scenarios, rules


def set_values(code: dict[str, str]) -> dict[str, list[str]]:
    """{field: [values]} for each `state.<field> = <a string or a NAME bound to one>`."""
    trees = {p: t for p, src in code.items() if (t := domain.parse(src)) is not None}
    constants = {
        t.id: n.value.value
        for tree in trees.values() for n in tree.body
        if isinstance(n, ast.Assign) and isinstance(n.value, ast.Constant) and isinstance(n.value.value, str)
        for t in n.targets if isinstance(t, ast.Name) and t.id.isupper()
    }
    found: dict[str, set] = defaultdict(set)
    for tree in trees.values():
        for node in ast.walk(tree):
            if not isinstance(node, ast.Assign):
                continue
            for target in node.targets:
                if not (isinstance(target, ast.Attribute) and isinstance(target.value, ast.Name)
                        and target.value.id == "state"):
                    continue
                # The values the field can take: the expression itself, either
                # side of an `or`, either branch of an `if`; never a condition
                # or a call's arguments.
                todo = [node.value]
                while todo:
                    part = todo.pop()
                    if isinstance(part, ast.Constant) and isinstance(part.value, str) and part.value:
                        found[target.attr].add(part.value)
                    elif isinstance(part, ast.Name) and part.id in constants:
                        found[target.attr].add(constants[part.id])
                    elif isinstance(part, ast.BoolOp):
                        todo += part.values
                    elif isinstance(part, ast.IfExp):
                        todo += [part.body, part.orelse]
    return {f: sorted(v) for f, v in found.items()}


def pages() -> list[str]:
    web = FRONTEND / "web" / "src"
    if not web.is_dir():
        return []
    found = sorted(str(p) for p in (web / "pages").glob("*.tsx")) if (web / "pages").is_dir() else []
    return found or ([str(web / "App.tsx")] if (web / "App.tsx").is_file() else [])


def facts() -> dict:
    api = domain.sources(API, ".py")
    backend = domain.sources(BACKEND, ".py")
    features = domain.sources(TESTS, ".feature")
    methods = methods_with_errors(api)
    scenarios, rules = scenarios_of(features)

    by_method = {}
    for m, info in methods.items():
        touching = [s for s in scenarios if m in s["calls"] or m in s["attempts"] or m in s["reads"]]
        expected = {e for s in touching if m in s["attempts"] for e in s["aborts"]}
        by_method[m] = {
            "kind": info["kind"],
            "scenarios": [f"{s['file']}:{s['line']}" for s in touching],
            "errors": info["errors"],
            "errors_unexpected": [e for e in info["errors"] if e not in expected],
            "refusal_shown": bool(expected & set(REFUSED)),
        }
    for r in rules:
        own = [s for s in scenarios if s["rule"] == r["rule"] and s["file"] == r["file"]]
        r["refusal"] = any(s["attempts"] and s["aborts"] for s in own)
        r["count"] = len(own)

    asserted: dict[str, set] = defaultdict(set)
    for s in scenarios:
        for field, v in s["values"]:
            asserted[field].add(v)
    states = {f: {"set": vs, "never_asserted": [v for v in vs if v not in asserted.get(f, set())]}
              for f, vs in set_values({**api, **backend}).items()}
    page_list = pages()
    browser = [s for s in scenarios if s["browser"]]
    users = {m.group(1) for t in features.values() for m in PERSON.finditer(t)}
    unauthenticated = any("is an unauthenticated user" in t for t in features.values())

    signals = []

    def signal(kind: str, what: str, evidence: list[str], decide: str) -> None:
        signals.append({"id": f"T{len(signals) + 1}", "kind": kind, "what": what,
                        "evidence": evidence, "decide": decide})

    untouched = [m for m, b in by_method.items() if not b["scenarios"] and not m.endswith(".create")]
    if untouched:
        signal("methods no scenario calls", f"{len(untouched)} method(s) no scenario calls or reads", untouched,
               "What does each do for a person, and which scenario would show it?")
    never = [f"{m}: {', '.join(b['errors_unexpected'])}" for m, b in by_method.items()
             if b["errors_unexpected"] and b["scenarios"]]
    if never:
        signal("errors never shown", f"{len(never)} called method(s) declare errors no scenario makes happen",
               never, "When does each happen to a person, and is the refusal what they should see?")
    writes = [m for m, b in by_method.items() if b["kind"] in ("Writer", "Transaction", "Workflow")
              and not m.endswith(".create")]
    refused = [m for m in writes if by_method[m]["refusal_shown"]]
    if writes and not refused:
        signal("no one is ever refused", f"none of {len(writes)} writing methods has a scenario where a caller "
               "is refused (`PermissionDenied` or `Unauthenticated`)", [],
               "Who must not do each of these? A scenario per role boundary shows the authorizer holds.")
    if not unauthenticated:
        signal("no signed-out caller", "no scenario calls as an unauthenticated user", [],
               "What does a signed-out visitor see or get refused?")
    for r in rules:
        if r["count"] == 0:
            signal("rule without scenarios", f"rule \"{r['rule']}\" has no scenario", [f"{r['file']}:{r['line']}"],
                   "What would show it kept?")
        elif not r["refusal"]:
            signal("rule never refuses", f"rule \"{r['rule']}\" has {r['count']} scenario(s), none of them an "
                   "attempt that is refused", [f"{r['file']}:{r['line']}"],
                   "A rule that forbids something is proven by the attempt it refuses: which attempt breaks "
                   "it? (A rule that only says what always happens may need none.)")
        elif r["count"] == 1:
            signal("rule with one scenario", f"rule \"{r['rule']}\" has one scenario", [f"{r['file']}:{r['line']}"],
                   "Is there a second way to break it (another step, another role, an edge value)?")
    for field, st in states.items():
        if st["never_asserted"]:
            signal("state never checked", f"`{field}` is set to {', '.join(st['never_asserted'])} in the "
                   "servicers, and no scenario checks it", [],
                   "Which path leads there, and what should a person see then?")
    if page_list and not browser:
        signal("no browser scenarios", f"{len(page_list)} page(s), no browser scenario", page_list,
               "What does a person do on each page, click by click?")
    elif len(browser) < len(page_list):
        signal("fewer browser scenarios than pages", f"{len(page_list)} pages, {len(browser)} browser scenario(s)",
               page_list + [f"{s['file']}:{s['line']} {s['name']}" for s in browser],
               "Which page has no scenario of a person doing its main job, click by click?")
    if len(users) <= 1:
        signal("one person only", f"the scenarios use {len(users) or 'no'} named person(s)", sorted(users),
               "What happens when two people act at once on the same thing?")
    wip = [f"{s['file']}:{s['line']}" for s in scenarios if "@wip" in s["tags"]]
    if wip:
        signal("still @wip", f"{len(wip)} scenario(s) tagged `@wip`", wip[:6],
               "Finished? `@wip` left on keeps them out of the record.")
    workflows = [m for m, b in by_method.items() if b["kind"] == "Workflow"]
    recovery = (TESTS).is_dir() and any("failure" in p.name or "recovery" in p.name for p in TESTS.rglob("*_test.py"))
    if workflows and not recovery:
        signal("workflows untested on restart", f"{len(workflows)} workflow(s), no failure-recovery test",
               workflows, "What must not happen twice if the app restarts mid-way? "
               "(python/references/testing-failure-recovery.md)")

    totals = {
        "scenarios": len(scenarios),
        "browser": len(browser),
        "rules": len(rules),
        "methods": len(methods),
        "methods_called": sum(1 for b in by_method.values() if b["scenarios"]),
        "errors": sum(len(b["errors"]) for b in by_method.values()),
        "errors_shown": sum(len(b["errors"]) - len(b["errors_unexpected"]) for b in by_method.values()),
        "rules_refusing": sum(1 for r in rules if r["refusal"]),
        "people": sorted(users),
    }
    return {"totals": totals, "methods": by_method, "rules": rules, "states": states,
            "pages": page_list, "scenarios": scenarios, "signals": signals}


def markdown(f: dict) -> str:
    t = f["totals"]
    out = ["# Test review facts", "",
           f"- Scenarios: {t['scenarios']} ({t['browser']} in a browser)",
           f"- Methods called by a scenario: {t['methods_called']} of {t['methods']}",
           f"- Declared errors a scenario makes happen: {t['errors_shown']} of {t['errors']}",
           f"- Rules with a refused attempt: {t['rules_refusing']} of {t['rules']}",
           f"- People in the scenarios: {', '.join(t['people']) or 'none'}", "",
           "## Methods", "", "| Method | Kind | Scenarios | Errors never shown | Refusal shown |",
           "| --- | --- | --- | --- | --- |"]
    for m, b in f["methods"].items():
        out.append(f"| `{m}` | {b['kind']} | {len(b['scenarios']) or '**0**'} | "
                   f"{', '.join(b['errors_unexpected']) or '-'} | {'yes' if b['refusal_shown'] else '-'} |")
    out += ["", "## Rules", ""]
    for r in f["rules"]:
        out.append(f"- \"{r['rule']}\": {r['count']} scenario(s)"
                   + ("" if r["refusal"] else ", **none refused**") + f" ({r['file']}:{r['line']})")
    if not f["rules"]:
        out.append("- none")
    out += ["", "## State values", ""]
    for field, st in f["states"].items():
        out.append(f"- `{field}`: {', '.join(st['set'])}"
                   + (f"; never checked: {', '.join(st['never_asserted'])}" if st["never_asserted"] else ""))
    if not f["states"]:
        out.append("- none found")
    out += ["", "## Pages", ""] + ([f"- {p}" for p in f["pages"]] or ["- none"])
    out += ["", "## Signals", ""]
    for s in f["signals"]:
        out.append(f"- **{s['id']} {s['kind']}:** {s['what']}.")
        for e in s["evidence"][:6]:
            out.append(f"  - {e}")
        if len(s["evidence"]) > 6:
            out.append(f"  - and {len(s['evidence']) - 6} more")
        out.append(f"  - Decide: {s['decide']}")
    if not f["signals"]:
        out.append("- none")
    return "\n".join(out)


def main(argv: list[str]) -> int:
    if not API.is_dir():
        print("coverage: no api/ folder; run from a Reboot project's root", file=sys.stderr)
        return 2
    f = facts()
    print(json.dumps(f, indent=2, default=list) if "--json" in argv else markdown(f))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
