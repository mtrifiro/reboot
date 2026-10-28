#!/usr/bin/env python3
"""The facts a domain review starts from, read from a Reboot app's code.

    python3 review.py              # Markdown, from the project root
    python3 review.py --json       # the same facts as JSON

Reads the API (`api/**/*.py`), the servicers (`backend/src/**/*.py`)
and the feature files (`tests/**/*.feature`), and prints:

- each domain object: its state's fields, its collections and their
  shape, its methods by kind, and its method and field name groups;
- the calls between domain objects, from the servicers, with the kind
  of each method called;
- the packages under `api/`, their size and any import circle;
- signals, each with an id (S1, S2, ...), its evidence, and the
  question that decides it. A signal is a place to look, not a
  verdict: the review weighs it against the app's numbers.

Standard library only. Never imports the app.
"""

from __future__ import annotations

import ast
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

API, BACKEND, TESTS = Path("api"), Path("backend/src"), Path("tests")

# A method list this long, or this many name groups, suggests a domain
# object holding more than one concern (state-actor-decomposition.md).
MANY_METHODS = 15
MANY_GROUPS = 3
# A package this size is suggested for a split (accept-design.md).
PACKAGE_SPLIT_AT = 6
# A transaction touching this many domain objects is worth a look.
WIDE_TRANSACTION = 3
EXTERNAL = re.compile(r"\b(httpx|requests|aiohttp|openai|anthropic|stripe|boto3|smtplib|twilio)\b")


def literal(node: ast.AST | None) -> str:
    if node is None:
        return ""
    if isinstance(node, ast.Constant):
        return node.value if isinstance(node.value, str) else repr(node.value)
    return ast.unparse(node)


def keywords(call: ast.Call) -> dict[str, ast.AST]:
    return {k.arg: k.value for k in call.keywords if k.arg}


def name_of(call: ast.Call) -> str:
    f = call.func
    return f.id if isinstance(f, ast.Name) else f.attr if isinstance(f, ast.Attribute) else ""


def sources(folder: Path, suffix: str) -> dict[str, str]:
    if not folder.is_dir():
        return {}
    # Generated code (`*_rbt.py`, `backend/api/`) is never the app's own.
    return {
        str(p): p.read_text(encoding="utf-8", errors="replace")
        for p in sorted(folder.rglob(f"*{suffix}"))
        if "_rbt" not in p.name and "node_modules" not in p.parts
        and not (folder != API and "api" in p.relative_to(folder).parts[:1])
    }


def parse(text: str) -> ast.Module | None:
    try:
        return ast.parse(text)
    except SyntaxError:
        return None


# The API: domain objects, their state and methods, and the packages.


def model_of(api: dict[str, str]) -> tuple[dict, dict]:
    types: dict = {}
    models: dict = {}
    for path, source in api.items():
        tree = parse(source)
        if tree is None:
            continue
        named = {
            t.id: node.value
            for node in tree.body
            if isinstance(node, ast.Assign)
            for t in node.targets
            if isinstance(t, ast.Name)
        }

        def resolve(value: ast.AST | None) -> ast.AST | None:
            return named.get(value.id, value) if isinstance(value, ast.Name) else value

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and any(literal(b).split(".")[-1] == "Model" for b in node.bases):
                models[node.name] = {
                    item.target.id: literal(item.annotation)
                    for item in node.body
                    if isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name)
                }
            if isinstance(node, ast.Call) and name_of(node) == "API":
                for type_name, declared in keywords(node).items():
                    value = resolve(declared)
                    if not (isinstance(value, ast.Call) and name_of(value) == "Type"):
                        continue
                    kw = keywords(value)
                    methods = {}
                    holder = resolve(kw.get("methods"))
                    if isinstance(holder, ast.Call):
                        for method, factory in keywords(holder).items():
                            if isinstance(factory, ast.Call):
                                methods[method] = name_of(factory)
                    types[type_name] = {
                        "state": literal(kw.get("state")),
                        "file": path,
                        "line": value.lineno,
                        "methods": methods,
                    }
    return types, models


def packages_of(api: dict[str, str]) -> dict[str, dict]:
    packages: dict[str, dict] = {}
    for path, source in api.items():
        parts = Path(path).parts
        if len(parts) < 3:
            continue
        name = parts[1]
        entry = packages.setdefault(name, {"objects": [], "imports": set()})
        tree = parse(source)
        if tree is None:
            continue
        entry["imports"] |= {
            node.module.split(".")[0]
            for node in ast.walk(tree)
            if isinstance(node, ast.ImportFrom) and node.module
        }
    return packages


def circles(packages: dict[str, dict]) -> list[list[str]]:
    found: list[list[str]] = []
    seen: set[frozenset] = set()

    def walk(start: str, here: str, path: list[str]) -> None:
        for nxt in sorted(packages.get(here, {}).get("imports", set()) & set(packages) - {here}):
            if nxt == start:
                key = frozenset(path)
                if key not in seen:
                    seen.add(key)
                    found.append(path + [start])
            elif nxt not in path:
                walk(start, nxt, path + [nxt])

    for name in sorted(packages):
        walk(name, name, [name])
    return found


def groups(names: list[str]) -> dict[str, list[str]]:
    """Names sharing a first or last word, when three or more do."""
    by: dict[str, list[str]] = defaultdict(list)
    for n in names:
        words = n.split("_")
        if len(words) > 1:
            by[words[0]].append(n)
            if words[-1] != words[0]:
                by["*_" + words[-1]].append(n)
    return {k: v for k, v in by.items() if len(v) >= 3}


def collection_shape(annotation: str, models: dict) -> str | None:
    a = annotation.replace(" ", "")
    inner = re.match(r"(?:list|List|set|Set)\[(.+)\]$", a) or re.match(r"(?:dict|Dict)\[[^,]+,(.+)\]$", a)
    if not inner:
        return None
    element = inner.group(1).split(".")[-1]
    if element in models:
        return "A: records inline (rewritten whole on every write; bounded only)"
    if element in ("str", "bytes"):
        return "B: ids or values inline (rewritten whole on every write; low thousands at most)"
    return f"C: {element} values inline (rewritten whole on every write)"


# The servicers: which domain object each serves, and what each method calls.


def servicers_of(backend: dict[str, str], types: dict) -> dict:
    """{Type: {"file", "methods": {m: {"line", "calls": [...], "external": [...]}}, "authorizer": bool}}."""
    out: dict = {}
    for path, source in backend.items():
        tree = parse(source)
        if tree is None:
            continue
        for cls in [n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]:
            served = next(
                (literal(b).split(".")[0] for b in cls.bases if literal(b).endswith(".Servicer")
                 and literal(b).split(".")[0] in types),
                None,
            )
            if not served:
                continue
            entry = out.setdefault(served, {"file": path, "methods": {}, "authorizer": False})
            for fn in cls.body:
                if not isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    continue
                if fn.name == "authorizer":
                    entry["authorizer"] = True
                calls = []
                guarded = set()
                for node in ast.walk(fn):
                    if isinstance(node, ast.Call) and name_of(node) in ("at_most_once", "at_least_once", "until"):
                        for sub in ast.walk(node):
                            guarded.add(id(sub))
                for node in ast.walk(fn):
                    if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Attribute):
                        continue
                    # Other.ref(id).method(...), Other.forall(ids).method(...), Other.create(...)
                    target = node.func.value
                    if isinstance(target, ast.Call) and isinstance(target.func, ast.Attribute) \
                            and isinstance(target.func.value, ast.Name) and target.func.value.id in types \
                            and target.func.attr in ("ref", "forall"):
                        arg = target.args[0] if target.args else None
                        constant = isinstance(arg, ast.Constant) or (
                            isinstance(arg, ast.Name) and arg.id.isupper())
                        calls.append({
                            "to": target.func.value.id, "method": node.func.attr,
                            "via": target.func.attr, "constant_id": literal(arg) if constant else "",
                            "line": node.lineno,
                        })
                    elif isinstance(node.func.value, ast.Name) and node.func.value.id in types \
                            and node.func.attr == "create":
                        calls.append({"to": node.func.value.id, "method": "create", "via": "create",
                                      "constant_id": "", "line": node.lineno})
                external = sorted({
                    f"{m.group(1)} (line {n.lineno})"
                    for n in ast.walk(fn) if isinstance(n, ast.Call) and id(n) not in guarded
                    for m in [EXTERNAL.search(ast.unparse(n.func))] if m
                })
                entry["methods"][fn.name] = {"line": fn.lineno, "calls": calls, "external": external}
    return out


def singletons_of(backend: dict[str, str], types: dict) -> dict[str, list[str]]:
    """{Type: [where]} for a domain object reached or created by a fixed id
    anywhere in the backend (a seed, an initialize hook, a servicer)."""
    found: dict[str, list[str]] = defaultdict(list)
    for path, source in backend.items():
        tree = parse(source)
        if tree is None:
            continue
        for node in ast.walk(tree):
            if not (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)):
                continue
            owner = node.func.value
            # Type.ref(ID) / Type.create(context, ID) / Type.idempotently(...).create(context, ID)
            if isinstance(owner, ast.Call) and isinstance(owner.func, ast.Attribute) \
                    and owner.func.attr == "idempotently":
                owner = owner.func.value
            if not (isinstance(owner, ast.Name) and owner.id in types):
                continue
            args = node.args[:1] if node.func.attr == "ref" else node.args[1:2] if node.func.attr == "create" else []
            for arg in args:
                if isinstance(arg, ast.Constant) or (isinstance(arg, ast.Name) and arg.id.isupper()):
                    found[owner.id].append(f"{path}:{node.lineno} ({literal(arg)})")
    return dict(found)


def feature_rules(tests: dict[str, str]) -> dict[str, int]:
    return {p: len(re.findall(r"^\s*Rule:", t, re.M)) for p, t in tests.items()}


def facts() -> dict:
    api = sources(API, ".py")
    backend = sources(BACKEND, ".py")
    tests = sources(TESTS, ".feature")
    types, models = model_of(api)
    servicers = servicers_of(backend, types)
    packages = packages_of(api)
    for t, info in types.items():
        pkg = Path(info["file"]).parts[1] if len(Path(info["file"]).parts) > 2 else ""
        if pkg in packages:
            packages[pkg]["objects"].append(t)
    for p in packages.values():
        p["imports"] = sorted(p["imports"] & set(packages))

    objects = {}
    for t, info in types.items():
        state = models.get(info["state"], {})
        collections = {f: s for f, a in state.items() if (s := collection_shape(a, models))}
        kinds: dict[str, list[str]] = defaultdict(list)
        for m, k in info["methods"].items():
            kinds[k].append(m)
        objects[t] = {
            "where": f"{info['file']}:{info['line']}",
            "fields": state,
            "collections": collections,
            "methods": dict(kinds),
            "method_groups": groups(list(info["methods"])),
            "field_groups": groups(list(state)),
            "servicer": servicers.get(t, {}).get("file", ""),
            "authorizer": servicers.get(t, {}).get("authorizer", False),
        }

    edges = []
    for t, s in servicers.items():
        for m, mi in s["methods"].items():
            for c in mi["calls"]:
                kind = types.get(c["to"], {}).get("methods", {}).get(c["method"], "create" if c["via"] == "create" else "?")
                edges.append({"from": f"{t}.{m}", "from_kind": types[t]["methods"].get(m, "helper"),
                              "to": f"{c['to']}.{c['method']}", "to_kind": kind, "via": c["via"],
                              "constant_id": c["constant_id"], "at": f"{s['file']}:{c['line']}"})

    signals = []

    def signal(kind: str, what: str, evidence: list[str], decide: str) -> None:
        signals.append({"id": f"S{len(signals) + 1}", "kind": kind, "what": what,
                        "evidence": evidence, "decide": decide})

    # One actor that every write of a kind goes through: writes to one
    # actor run one at a time (servicer-writer.md).
    singletons = singletons_of(backend, types)
    for t in sorted(singletons):
        writes = sorted(m for m, k in types[t]["methods"].items()
                        if k in ("Writer", "Transaction") and m != "create")
        if not writes:
            continue
        inbound = [f"{e['from']} -> {e['to']} ({e['at']})" for e in edges
                   if e["to"].split(".")[0] == t and e["to_kind"] in ("Writer", "Transaction")]
        signal("one actor for everyone",
               f"`{t}` is a single actor (fixed id), and its {len(writes)} writing method(s) "
               f"({', '.join(writes)}) each wait their turn on it, from every user at once",
               singletons[t][:2] + inbound,
               f"How many of these a second at the busiest hour? Must they be ordered with one another, "
               f"or does each touch a different part (a room, a night, a member) that could be its own actor?")
    for t, o in objects.items():
        for f, shape in o["collections"].items():
            signal("collection inline",
                   f"`{t}.{f}` is a collection kept inside the actor ({shape})",
                   [f"{o['where']} state {f}: {o['fields'][f]}"],
                   f"How many can `{t}` hold in a year? Is that bound set by the domain, not a cap?")
        n = sum(len(v) for v in o["methods"].values())
        if n >= MANY_METHODS or len(o["method_groups"]) >= MANY_GROUPS or len(o["field_groups"]) >= MANY_GROUPS:
            signal("several concerns",
                   f"`{t}` has {n} methods in groups {', '.join(o['method_groups']) or '-'}"
                   f" and field groups {', '.join(o['field_groups']) or '-'}",
                   [o["where"]],
                   "Do these groups change at different times, from different people? Each is a candidate domain object.")
        if o["servicer"] and not o["authorizer"]:
            signal("no authorizer", f"`{t}`'s servicer has no `authorizer()`", [o["servicer"]],
                   "Who may call each method? (servicer-authorizer.md)")
    for e in edges:
        if e["via"] == "forall" and e["from_kind"] == "Reader":
            target = e["to"].split(".")[0]
            summary = any("summary" in m for m in types[target]["methods"])
            signal("fan-out read",
                   f"`{e['from']}` reads every `{target}` through `{e['to']}` and re-runs when any of them changes"
                   + ("" if summary or "summary" in e["to"] else f"; `{target}` has no summary reader"),
                   [e["at"]],
                   f"How many `{target}` per call, and how many pages subscribe at once?")
    by_tx: dict[str, set] = defaultdict(set)
    for e in edges:
        if e["from_kind"] == "Transaction" and e["to_kind"] in ("Writer", "Transaction", "create"):
            by_tx[e["from"]].add(e["to"].split(".")[0])
    for tx, touched in sorted(by_tx.items()):
        if len(touched | {tx.split(".")[0]}) >= WIDE_TRANSACTION:
            signal("wide transaction",
                   f"`{tx}` changes {len(touched | {tx.split('.')[0]})} domain objects at once: "
                   f"{', '.join(sorted(touched | {tx.split('.')[0]}))}",
                   [], "Must all of these change together, or could one writer and a derived reader do?")
    for t, s in servicers.items():
        for m, mi in s["methods"].items():
            if mi["external"] and types[t]["methods"].get(m) == "Workflow":
                signal("unguarded outside call",
                       f"`{t}.{m}` is a workflow calling out without `at_most_once` / `at_least_once`",
                       [f"{s['file']}: {', '.join(mi['external'])}"],
                       "What happens if this call runs twice after a restart? (servicer-workflow.md)")
    for circle in circles({k: {"imports": set(v["imports"])} for k, v in packages.items()}):
        signal("package circle", "packages import each other: " + " -> ".join(circle), [],
               "Which one is on top, joining the others?")
    for name, p in sorted(packages.items()):
        if len(p["objects"]) >= PACKAGE_SPLIT_AT:
            signal("big package", f"package `{name}` holds {len(p['objects'])} domain objects", p["objects"],
                   "Which areas of the work do they fall into?")
    if len(packages) > 1:
        small = [n for n, p in packages.items() if len(p["objects"]) <= 1]
        if len(small) > len(packages) / 2:
            signal("packages too fine", f"{len(small)} of {len(packages)} packages hold one domain object or none",
                   small, "Does each package stand for an area of the work, or would fewer read better?")
    return {"objects": objects, "edges": edges, "packages": packages,
            "rules": feature_rules(tests), "signals": signals}


def markdown(f: dict) -> str:
    out = ["# Domain review facts", "", "## Domain objects", ""]
    out += ["| Object | Methods by kind | Collections | Where |", "| --- | --- | --- | --- |"]
    for t, o in f["objects"].items():
        kinds = "; ".join(f"{k} {len(v)}" for k, v in sorted(o["methods"].items()))
        cols = "; ".join(f"`{c}` {s.split(':')[0]}" for c, s in o["collections"].items()) or "-"
        out.append(f"| `{t}` | {kinds} | {cols} | {o['where']} |")
    out += ["", "## Calls between domain objects", ""]
    for e in f["edges"]:
        cid = f" (one actor: {e['constant_id']})" if e["constant_id"] else ""
        out.append(f"- {e['from']} [{e['from_kind']}] -> {e['to']} [{e['to_kind']}] via {e['via']}{cid}")
    if not f["edges"]:
        out.append("- none found")
    out += ["", "## Packages", ""]
    for n, p in sorted(f["packages"].items()):
        out.append(f"- `{n}`: {', '.join(p['objects']) or 'no domain objects'}"
                   + (f"; imports {', '.join(p['imports'])}" if p["imports"] else ""))
    out += ["", f"## Rules: {sum(f['rules'].values())} across {len(f['rules'])} feature file(s)", "",
            "## Signals", ""]
    for s in f["signals"]:
        out.append(f"- **{s['id']} {s['kind']}:** {s['what']}.")
        for e in s["evidence"][:6]:
            out.append(f"  - {e}")
        out.append(f"  - Decide: {s['decide']}")
    if not f["signals"]:
        out.append("- none")
    return "\n".join(out)


def main(argv: list[str]) -> int:
    if not API.is_dir():
        print("review: no api/ folder; run from a Reboot project's root", file=sys.stderr)
        return 2
    f = facts()
    print(json.dumps(f, indent=2, default=list) if "--json" in argv else markdown(f))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
