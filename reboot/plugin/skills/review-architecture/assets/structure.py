#!/usr/bin/env python3
"""The facts an architecture review starts from, read from a Reboot app's code.

    python3 structure.py              # Markdown, from the project root
    python3 structure.py --json       # the same facts as JSON

Reads the API (`api/**/*.py`), the backend (`backend/src/**/*.py`), the
tests (`tests/`), the frontend (`frontend/**/src/`) and the project's
own files, and prints:

- the shape of the code: files and functions by size, servicers by
  method count, function bodies repeated across files;
- the API surface: each method, its kind, and who uses it (another
  servicer, the frontend, the tests), so a method no one calls shows;
- authorization: each servicer's `authorizer()`, the methods it names,
  whether it has a `_default`, and every `allow()`;
- errors: broad `except`, plain exceptions raised from servicers;
- the rules: rules without scenarios, scenarios still `@wip` or
  `@blocked`, and the last recorded run;
- the frontend: files by size, raw colours outside `styles.css`;
- readiness to run elsewhere: environment reads, secrets in code, the
  deploy ledger;
- signals, each with an id (A1, A2, ...), its evidence, and the
  question that decides it. A signal is a place to look, not a
  verdict.

The domain model's scale (single actors, collections, fan-out reads,
wide transactions) is the review-domain skill's: its `review.py` is
imported for the parsing and not repeated here. Standard library only.
Never imports the app.
"""

from __future__ import annotations

import ast
import hashlib
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "review-domain" / "assets"))
import review as domain  # noqa: E402

API, BACKEND, TESTS = domain.API, domain.BACKEND, domain.TESTS
FRONTEND = Path("frontend")

# A file this long is hard to hold in one's head; a function this long
# usually does more than one thing.
LONG_FILE = 400
LONG_FUNCTION = 60
# A servicer with this many methods may hold more than one concern.
MANY_METHODS = 15
# An object more than this many others call is a hub: every request waits on it.
HUB_CALLERS = 4
# Repeated bodies shorter than this many statements are noise.
REPEAT_MIN_STATEMENTS = 5
RAW_COLOUR = re.compile(r"#[0-9a-fA-F]{3,8}\b|\brgba?\(|\bhsla?\(")
SECRET = re.compile(r"""(?i)(api[_-]?key|secret|token|password)\s*[:=]\s*["'][^"']{12,}["']""")
ENV = re.compile(r"\bos\.environ\b|\bos\.getenv\(")


def camel(name: str) -> str:
    head, *rest = name.split("_")
    return head + "".join(w[:1].upper() + w[1:] for w in rest)


def lines(text: str) -> int:
    return text.count("\n") + 1


def frontend_sources() -> dict[str, str]:
    if not FRONTEND.is_dir():
        return {}
    out = {}
    for p in sorted(FRONTEND.rglob("*")):
        if p.suffix not in (".ts", ".tsx", ".css") or "node_modules" in p.parts \
                or "dist" in p.parts or "_rbt" in p.name or "api" in p.relative_to(FRONTEND).parts[:1]:
            continue
        out[str(p)] = p.read_text(encoding="utf-8", errors="replace")
    return out


def functions(tree: ast.Module):
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            yield node


def body_key(fn: ast.AST) -> str | None:
    body = [s for s in fn.body if not (isinstance(s, ast.Expr) and isinstance(s.value, ast.Constant))]
    if sum(1 for _ in ast.walk(ast.Module(body=body, type_ignores=[])) if isinstance(_, ast.stmt)) \
            < REPEAT_MIN_STATEMENTS:
        return None
    dumped = "".join(ast.dump(s, annotate_fields=False) for s in body)
    return hashlib.sha1(dumped.encode()).hexdigest()


def authorizers(backend: dict[str, str], types: dict) -> dict[str, dict]:
    """{Type: {"file", "line", "named": [...], "default": bool, "allow": [lines]}}."""
    out: dict[str, dict] = {}
    for path, source in backend.items():
        tree = domain.parse(source)
        if tree is None:
            continue
        for cls in [n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]:
            served = next((domain.literal(b).split(".")[0] for b in cls.bases
                           if domain.literal(b).endswith(".Servicer")
                           and domain.literal(b).split(".")[0] in types), None)
            if not served:
                continue
            entry = out.setdefault(served, {"file": path, "line": cls.lineno, "named": [],
                                            "default": False, "allow": [], "has": False})
            for fn in cls.body:
                if not (isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)) and fn.name == "authorizer"):
                    continue
                entry["has"], entry["line"] = True, fn.lineno
                for node in ast.walk(fn):
                    if isinstance(node, ast.Call) and domain.name_of(node) == "Authorizer":
                        for k in domain.keywords(node):
                            if k == "_default":
                                entry["default"] = True
                            else:
                                entry["named"].append(k)
                    if isinstance(node, ast.Call) and domain.name_of(node) == "allow" and not node.args \
                            and not node.keywords:
                        entry["allow"].append(f"{path}:{node.lineno}")
    return out


def feature_facts(tests: dict[str, str]) -> dict:
    empty_rules, wip, blocked, scenarios = [], [], [], 0
    for path, text in tests.items():
        rule, rule_line, count, tags = None, 0, 0, []
        for i, line in enumerate(text.splitlines(), 1):
            s = line.strip()
            if s.startswith("@"):
                tags = s.split()
                continue
            if s.startswith("Rule:"):
                if rule is not None and count == 0:
                    empty_rules.append(f"{path}:{rule_line} {rule}")
                rule, rule_line, count = s[5:].strip(), i, 0
            elif s.startswith(("Scenario:", "Scenario Outline:", "Example:")):
                count += 1
                scenarios += 1
                if "@wip" in tags:
                    wip.append(f"{path}:{i}")
                if "@blocked" in tags:
                    blocked.append(f"{path}:{i}")
            elif s.startswith("Feature:"):
                if "@wip" in tags:
                    wip.append(f"{path}:{i} (the whole feature)")
                if "@blocked" in tags:
                    blocked.append(f"{path}:{i} (the whole feature)")
            if s and not s.startswith("@"):
                tags = [] if not s.startswith(("Feature:", "Rule:")) else tags
        if rule is not None and count == 0:
            empty_rules.append(f"{path}:{rule_line} {rule}")
    return {"scenarios": scenarios, "rules_without_scenarios": empty_rules, "wip": wip, "blocked": blocked}


def facts() -> dict:
    api = domain.sources(API, ".py")
    backend = domain.sources(BACKEND, ".py")
    tests_py = domain.sources(TESTS, ".py")
    features = domain.sources(TESTS, ".feature")
    front = frontend_sources()
    types, _models = domain.model_of(api)
    servicers = domain.servicers_of(backend, types)

    # Size.
    sized = sorted(((p, lines(t)) for d in (api, backend, tests_py, front) for p, t in d.items()),
                   key=lambda x: -x[1])
    long_functions, repeats = [], defaultdict(list)
    for path, source in {**backend, **tests_py}.items():
        tree = domain.parse(source)
        if tree is None:
            continue
        for fn in functions(tree):
            n = (fn.end_lineno or fn.lineno) - fn.lineno + 1
            if n >= LONG_FUNCTION:
                long_functions.append(f"{path}:{fn.lineno} {fn.name} ({n} lines)")
            key = body_key(fn)
            if key:
                repeats[key].append(f"{path}:{fn.lineno} {fn.name}")
    repeated = [where for where in repeats.values() if len(where) > 1]

    # The API surface and who uses it.
    called_by_servicers = defaultdict(list)
    for t, s in servicers.items():
        for m, mi in s["methods"].items():
            for c in mi["calls"]:
                called_by_servicers[f"{c['to']}.{c['method']}"].append(f"{t}.{m}")
    backend_text = "\n".join(backend.values())
    front_text = "\n".join(front.values())
    test_text = "\n".join(list(tests_py.values()) + list(features.values()))
    surface = []
    for t, info in types.items():
        for m, kind in info["methods"].items():
            users = []
            if called_by_servicers.get(f"{t}.{m}") or re.search(rf"\.{re.escape(m)}\(", backend_text):
                users.append("backend")
            if re.search(rf"\b({re.escape(camel(m))}|use{re.escape(camel(m)[:1].upper() + camel(m)[1:])})\b",
                         front_text):
                users.append("frontend")
            if re.search(rf"\b({re.escape(m)}|{re.escape(camel(m))})\b", test_text):
                users.append("tests")
            surface.append({"method": f"{t}.{m}", "kind": kind, "used_by": users})

    auth = authorizers(backend, types)

    # Errors.
    broad, plain = [], []
    for path, source in backend.items():
        tree = domain.parse(source)
        if tree is None:
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.ExceptHandler):
                caught = domain.literal(node.type) if node.type else ""
                if caught in ("", "Exception", "BaseException"):
                    broad.append(f"{path}:{node.lineno} except {caught or '(bare)'}")
            if isinstance(node, ast.Raise) and isinstance(node.exc, ast.Call) \
                    and domain.name_of(node.exc) in ("Exception", "ValueError", "RuntimeError",
                                                     "KeyError", "AssertionError"):
                plain.append(f"{path}:{node.lineno} raise {domain.name_of(node.exc)}")

    rules = feature_facts(features)
    last_run = {}
    if (TESTS / ".last-run.json").is_file():
        try:
            last_run = json.loads((TESTS / ".last-run.json").read_text())
        except ValueError:
            pass

    raw_colours = [f"{p}:{i}" for p, t in front.items() if not p.endswith("styles.css")
                   for i, line in enumerate(t.splitlines(), 1) if RAW_COLOUR.search(line)]
    env_reads = [f"{p}:{i}" for p, t in backend.items() for i, line in enumerate(t.splitlines(), 1)
                 if ENV.search(line)]
    secrets = [f"{p}:{i}" for d in (backend, front) for p, t in d.items()
               for i, line in enumerate(t.splitlines(), 1) if SECRET.search(line)]
    deployed = Path("deploy/ledger.jsonl").is_file()

    signals = []

    def signal(kind: str, what: str, evidence: list[str], decide: str) -> None:
        signals.append({"id": f"A{len(signals) + 1}", "kind": kind, "what": what,
                        "evidence": evidence, "decide": decide})

    for path, n in sized:
        # The house stylesheet is copied whole from the starter.
        if n >= LONG_FILE and not path.endswith("styles.css"):
            signal("long file", f"`{path}` is {n} lines", [path],
                   "Does it hold one concern, or several that change for different reasons?")
    if long_functions:
        signal("long functions", f"{len(long_functions)} function(s) of {LONG_FUNCTION} lines or more",
               long_functions, "Does each do one thing a reader can name? What would its helpers be called?")
    for t, s in servicers.items():
        n = len(s["methods"])
        if n >= MANY_METHODS:
            signal("big servicer", f"`{t}`'s servicer has {n} methods and helpers", [s["file"]],
                   "Do they serve one domain object's job, or does a second object hide in them?")
    # Who calls whom, from each servicer's own calls. A roster read by the
    # authorizers' helper module is the house pattern
    # (python/references/auth-roles.md), so it is not a call here; a roster
    # kept on an object that also does other work is its own signal.
    calls = defaultdict(set)
    files = {s["file"]: t for t, s in servicers.items()}
    for t, s in servicers.items():
        for mi in s["methods"].values():
            for c in mi["calls"]:
                if c["to"] != t:
                    calls[t].add(c["to"])
    callers = defaultdict(set)
    for a, bs in calls.items():
        for b in bs:
            callers[b].add(a)
    for t, who in sorted(callers.items()):
        if len(who) > HUB_CALLERS:
            signal("hub object", f"`{t}` is called by {len(who)} other objects", sorted(who),
                   "Is it one object's job, or an index each area could own? Every caller waits on it, "
                   "one call at a time (app-design skill, section 3, the domain model's shape).")
    for a, b in sorted({tuple(sorted((a, b))) for a, bs in calls.items() for b in bs if a in calls.get(b, ())}):
        signal("objects call each other", f"`{a}` and `{b}` call each other", [a, b],
               "Which one owns the step? The other is told by its caller, or reads, never calls back.")
    for path, source in backend.items():
        # A helper module whose predicates decide who may call.
        if path in files or "Authorizer.Decision" not in source:
            continue
        for t in sorted({m.group(1) for m in re.finditer(r"\b([A-Z]\w*)\.ref\(", source) if m.group(1) in types}):
            n = len(servicers.get(t, {}).get("methods", {}))
            if callers.get(t) or n >= MANY_METHODS:
                signal("roster on a busy object",
                       f"the authorizers in `{path}` read roles from `{t}`, which also has {n} methods"
                       + (f" and {len(callers[t])} caller(s)" if callers.get(t) else ""),
                       [path, servicers.get(t, {}).get("file", "")],
                       "Every authorized call in the app waits on it. Give the roster its own object "
                       "(python/references/auth-roles.md), so the hub keeps only its own job.")
    for where in repeated:
        signal("repeated code", f"the same body in {len(where)} places", where,
               "Is this one idea that belongs in one helper, or two that only look alike today?")
    unused = [s["method"] for s in surface if not s["used_by"]]
    if unused:
        signal("unused methods", f"{len(unused)} API method(s) no servicer, page or test calls", unused,
               "Is each one for a feature still to come, an MCP or AI caller, or dead weight in the API?")
    untested = [s["method"] for s in surface if s["used_by"] and "tests" not in s["used_by"]
                and s["kind"] in ("Writer", "Transaction", "Workflow")
                and not s["method"].endswith(".create")]
    if untested:
        signal("writes no test names", f"{len(untested)} writing method(s) no test or scenario names",
               untested, "Which rule does each serve, and which scenario would show it kept?")
    for t, a in auth.items():
        # Reboot's own `User` (set_claims) enforces its rule itself.
        if t == "User" and "set_claims" in servicers.get(t, {}).get("methods", {}):
            continue
        if not a["has"]:
            signal("no authorizer", f"`{t}`'s servicer has no `authorizer()`", [a["file"]],
                   "Who may call each method? (python/references/servicer-authorizer.md)")
            continue
        missing = sorted(set(types[t]["methods"]) - set(a["named"]))
        if missing and not a["default"]:
            signal("internal only",
                   f"`{t}`'s authorizer names no rule for {', '.join(missing)} and has no `_default`",
                   [f"{a['file']}:{a['line']}"],
                   "Without `_default`, each is callable only from inside the app "
                   "(python/references/auth-custom-predicates.md): is that meant, a step another object "
                   "takes, or does a page, a test or an AI caller need it?")
        if a["default"] and len(a["named"]) <= 1 and len(types[t]["methods"]) > 3:
            signal("one rule for everything",
                   f"`{t}`'s authorizer gives {len(types[t]['methods'])} methods one `_default` rule",
                   [f"{a['file']}:{a['line']}"],
                   "Do all of them really have the same callers? Which may only some roles do?")
        if a["allow"]:
            signal("allow()", f"`{t}`'s authorizer lets anyone call {len(a['allow'])} method(s)", a["allow"],
                   "Is each meant to be public, signed out included?")
    if broad:
        signal("broad except", f"{len(broad)} broad `except`", broad,
               "What error is expected here? A caught Reboot error that should reach the caller is lost.")
    if plain:
        signal("plain exceptions", f"{len(plain)} plain exception(s) raised in the backend", plain,
               "Should the caller see a declared error (`errors=[...]` on the method) it can handle?")
    if rules["rules_without_scenarios"]:
        signal("rules without scenarios", f"{len(rules['rules_without_scenarios'])} rule(s) no scenario proves",
               rules["rules_without_scenarios"], "What scenario would show each kept?")
    if rules["wip"]:
        signal("still @wip", f"{len(rules['wip'])} scenario(s) or feature(s) still tagged `@wip`",
               rules["wip"][:6], "Is the feature finished? `@wip` left on hides it from the record.")
    if rules["blocked"]:
        signal("@blocked", f"{len(rules['blocked'])} scenario(s) tagged `@blocked`", rules["blocked"],
               "What blocks each, and is it the app or Reboot?")
    if last_run and (last_run.get("failed") or not last_run.get("full")):
        signal("last run", f"the last recorded run was {'partial' if not last_run.get('full') else 'failing'}"
               f" ({last_run.get('passed', 0)} passed, {last_run.get('failed', 0)} failed)",
               [str(TESTS / ".last-run.json")], "Run the whole suite before any change.")
    if raw_colours:
        signal("raw colours", f"{len(raw_colours)} raw colour(s) outside `styles.css`", raw_colours[:6],
               "Should each be a token, so the look changes in one place?")
    if secrets:
        signal("secret in code", f"{len(secrets)} line(s) that look like a secret in the source", secrets,
               "Is it a real key? It belongs in a secret, never in the code.")
    if env_reads:
        signal("environment reads", f"{len(env_reads)} read(s) of the environment in the backend", env_reads,
               "Is each one set in production (a secret, the deploy's settings), with a default for dev?")

    return {
        "files": [{"file": p, "lines": n} for p, n in sized[:12]],
        "servicers": {t: {"file": s["file"], "methods": len(s["methods"]), "names": sorted(s["methods"])}
                      for t, s in servicers.items()},
        "surface": surface,
        "authorizers": auth,
        "rules": rules,
        "last_run": last_run,
        "deployed": deployed,
        "signals": signals,
    }


def markdown(f: dict) -> str:
    out = ["# Architecture review facts", "", "## Largest files", ""]
    out += [f"- {x['file']}: {x['lines']} lines" for x in f["files"]] or ["- none"]
    out += ["", "## Servicers", ""]
    out += [f"- `{t}`: {s['methods']} methods and helpers ({s['file']})" for t, s in f["servicers"].items()] \
        or ["- none"]
    out += ["", "## API surface", "", "| Method | Kind | Used by |", "| --- | --- | --- |"]
    out += [f"| `{s['method']}` | {s['kind']} | {', '.join(s['used_by']) or '**no one**'} |"
            for s in f["surface"]]
    out += ["", "## Authorization", ""]
    for t, a in f["authorizers"].items():
        if not a["has"]:
            own = t == "User" and "set_claims" in f["servicers"].get(t, {}).get("names", [])
            out.append(f"- `{t}`: " + ("Reboot's own rule (the user themself, or the app)" if own
                                       else "**no authorizer**"))
            continue
        out.append(f"- `{t}`: rules for {', '.join(a['named']) or 'no method by name'}"
                   + ("; a `_default` for the rest" if a["default"] else "")
                   + (f"; `allow()` ×{len(a['allow'])}" if a["allow"] else ""))
    r = f["rules"]
    out += ["", f"## Scenarios: {r['scenarios']}; @wip {len(r['wip'])}; @blocked {len(r['blocked'])}; "
            f"rules without one {len(r['rules_without_scenarios'])}", ""]
    if f["last_run"]:
        lr = f["last_run"]
        out.append(f"Last run {lr.get('when', '?')}: {lr.get('passed', 0)} passed, {lr.get('failed', 0)} failed"
                   + (", full" if lr.get("full") else ", partial"))
    out.append(f"Deployed: {'yes (deploy/ledger.jsonl)' if f['deployed'] else 'no'}")
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
    out += ["", "The domain model's scale: `python3 <the review-domain skill>/assets/review.py`."]
    return "\n".join(out)


def main(argv: list[str]) -> int:
    if not API.is_dir():
        print("structure: no api/ folder; run from a Reboot project's root", file=sys.stderr)
        return 2
    f = facts()
    print(json.dumps(f, indent=2, default=list) if "--json" in argv else markdown(f))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
