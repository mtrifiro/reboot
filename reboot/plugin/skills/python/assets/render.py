#!/usr/bin/env python3
"""render.py: a new Reboot project from the starter, named for the design.

    python3 '<the python skill>/assets/render.py' --app 'Maison Desk' \\
        --pkg hotel --hub Hotel --thing Room [--things Rooms] [--web] [DEST]

(single quotes: the plugin's path may hold a space, and the plugin's
auto-approve hook passes a command with single quotes, not double)

Writes into DEST (default: the current directory) the project shell
and the starter app, every file named and worded for the design:

  * `api/<pkg>/v1/<pkg>.py`: a `User`, the one `<Hub>` (fixed id, the
    snake case of its name) holding the `<Thing>`s, and a `<Thing>`,
    with a factory writer, a reader, an edit, a transaction on the hub
    that adds one, and a typed error;
  * their servicers, each with its real authorizer (anyone signed in;
    `create` and `open` internal), `main.py` with `initialize` and the
    development sign-in;
  * the tests: `tests/<things>.feature` in the built-in steps (adding,
    listing, editing, the rule that a name is required, that anonymous
    callers are refused), `tests/<pkg>_test.py`, `conftest.py`, and the
    app skill's test record and scripts;
  * with `--web`, the whole frontend (Vite, React, the house look, the
    page that lists and adds `<Thing>`s, signed in) and the browser
    scenarios, `tests/<pkg>_web.feature` and `tests/web_test.py`.

A file that already exists is kept, never overwritten. Then it is
green as it stands:

    uv sync && uv run rbt generate && uv run pytest
    cd frontend && npm install && npm run build      # with --web

and the build edits it into the design: the fields and methods the
design names, beside the ones here, in the same shape. Nothing here is
read first; it is the shape the references describe.
"""

import argparse
import re
import shutil
import stat
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent  # <skills>/python/assets
SKILLS = HERE.parents[1]
PROJECT = HERE / "project"
WEB = SKILLS / "web-app" / "assets" / "starter"
APP_ASSETS = SKILLS / "app" / "assets"

CAMEL = re.compile(r"^[A-Z][A-Za-z0-9]*$")
PKG = re.compile(r"^[a-z][a-z0-9_]*$")


def snake(camel: str) -> str:
    return re.sub(r"(?<!^)(?=[A-Z])", "_", camel).lower()


def words(camel: str) -> str:
    return snake(camel).replace("_", " ")


def lower_camel(camel: str) -> str:
    return camel[0].lower() + camel[1:]


# A web app's `.rbtrc` configs, after the shared project's lines: the
# backend serves the web app from Vite's dev server (`--web-app`), under
# portless by default, on plain ports with `--config=ports`, or built
# with `--config=dist` (python/references/lifecycle-rbtrc.md).
WEB_RBTRC = """
# The web app, served by the backend from Vite's dev server. Named URLs
# via portless (https://github.com/vercel-labs/portless) by default: the
# app is https://<project-name>.localhost, Vite (`cd frontend && npm run
# dev`) is https://frontend.<project-name>.localhost. Needs the portless
# proxy (`portless proxy start`).
dev run --default-config=portless
dev run:portless --portless
dev run:portless --frontend-url=https://frontend.<project-name>.localhost
dev run:portless --web-app

# Plain ports instead: `rbt dev run --config=ports`, with Vite run as
# `cd frontend && npm run dev:ports`; the app is http://localhost:9991.
dev run:ports --frontend-url=http://localhost:5173
dev run:ports --web-app

# The built web app at `/`, no Vite: `rbt dev run --config=dist` after
# `cd frontend && npm run build`.
dev run:dist --web-app-dist-path=frontend/dist/web

# Production (`rbt serve run`, the deploy's container) serves the built
# web app at `/` too.
serve run --web-app-dist-path=frontend/dist/web
"""


def tokens(args) -> dict[str, str]:
    things = args.things or args.thing + "s"
    # The project's folder, not the app's working name: the name is the
    # app's address under portless (https://<name>.localhost, and the
    # dashboard's), and two builds of one prompt would pick the same
    # working name and take each other's addresses. A folder is unique on
    # the machine, and stays put when the app is renamed.
    folder = Path(args.dest).resolve().name
    slug = args.slug or re.sub(r"[^a-z0-9]+", "-", folder.lower()).strip("-") \
        or re.sub(r"[^a-z0-9]+", "-", args.app.lower()).strip("-")
    return {
        "__APP_NAME__": args.app,
        "__app_slug__": slug,
        "<project-name>": slug,
        "__pkg__": args.pkg,
        "__Hub__": args.hub,
        "__hub__": snake(args.hub),
        "__hub text__": words(args.hub),
        "__Thing__": args.thing,
        "__thing__": snake(args.thing),
        "__thingCamel__": lower_camel(args.thing),
        "__thing text__": words(args.thing),
        "__Things__": things,
        "__things__": snake(things),
        "__thingsCamel__": lower_camel(things),
        "__things text__": words(things),
        "__Things text__": words(things).capitalize(),
    }


def render(text: str, t: dict[str, str]) -> str:
    for key in sorted(t, key=len, reverse=True):
        text = text.replace(key, t[key])
    return text


def copy_tree(src: Path, dest: Path, t: dict[str, str], written: list, kept: list) -> None:
    for path in sorted(src.rglob("*")):
        if path.is_dir() or "__pycache__" in path.parts:
            continue
        rel = Path(render(str(path.relative_to(src)), t))
        target = dest / rel
        if target.exists():
            kept.append(rel)
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        try:
            data = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            shutil.copy2(path, target)
        else:
            target.write_text(render(data, t), encoding="utf-8")
            shutil.copymode(path, target)
        written.append(rel)


def main(argv: list[str]) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--app", required=True, help='the app\'s name as shown: "Maison Desk"')
    p.add_argument("--pkg", required=True, help="the API package, lower case: hotel")
    p.add_argument("--hub", required=True, help="the one hub object, CamelCase: Hotel")
    p.add_argument("--thing", required=True, help="the first feature's central object, CamelCase: Room")
    p.add_argument("--things", help="its plural when it isn't <thing>s: Stays, Inventory")
    p.add_argument("--slug", help="the project name for pyproject, .rbtrc and package.json, and so its portless address (default: the project folder's name)")
    p.add_argument("--web", action="store_true", help="also the web app and its browser scenarios")
    p.add_argument("--force", action="store_true", help="render into a folder that already has an api/")
    p.add_argument("dest", nargs="?", default=".", help="the project folder (default: here)")
    args = p.parse_args(argv)

    problems = []
    if not PKG.match(args.pkg):
        problems.append(f"--pkg {args.pkg!r}: lower case letters, digits and underscores, starting with a letter")
    for flag in ("hub", "thing", "things"):
        value = getattr(args, flag)
        if value is not None and not CAMEL.match(value):
            problems.append(f"--{flag} {value!r}: CamelCase, starting with a capital")
    if args.hub == args.thing:
        problems.append("--hub and --thing must differ")
    if args.things is not None and args.things == args.thing:
        problems.append("--things must differ from --thing")
    if problems:
        print("\n".join(problems), file=sys.stderr)
        return 2

    dest = Path(args.dest).resolve()
    if (dest / "api").exists() and not args.force:
        print(f"{dest} already has an api/: this is a built app, not a new one "
              f"(--force renders beside it, keeping every existing file)", file=sys.stderr)
        return 2
    for src in (PROJECT, APP_ASSETS) + ((WEB,) if args.web else ()):
        if not src.is_dir():
            print(f"missing {src}: run this from the plugin's own copy", file=sys.stderr)
            return 2

    t = tokens(args)
    written: list[Path] = []
    kept: list[Path] = []
    dest.mkdir(parents=True, exist_ok=True)
    copy_tree(PROJECT, dest, t, written, kept)
    copy_tree(APP_ASSETS, dest, t, written, kept)
    if args.web:
        copy_tree(WEB, dest, t, written, kept)
        rbtrc = dest / ".rbtrc"
        if rbtrc.exists() and "dev run:portless" not in rbtrc.read_text(encoding="utf-8"):
            rbtrc.write_text(rbtrc.read_text(encoding="utf-8") + render(WEB_RBTRC, t), encoding="utf-8")
        # The browser scenarios need Playwright: the shell keeps the two
        # lines commented out for apps without a web app.
        pyproject = dest / "pyproject.toml"
        if pyproject.exists():
            text = pyproject.read_text(encoding="utf-8")
            text = text.replace('    # Only with web app scenarios (`testing-web-app.md`):\n', "")
            text = text.replace('    # "playwright>=', '    "playwright>=').replace('    # "pytest-playwright>=', '    "pytest-playwright>=')
            pyproject.write_text(text, encoding="utf-8")
    test_sh = dest / "scripts" / "test.sh"
    if test_sh.exists():
        test_sh.chmod(test_sh.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)

    print(f"{t['__APP_NAME__']}: {len(written)} files written to {dest}"
          + (f", {len(kept)} kept as they were" if kept else ""))
    for rel in written:
        print(f"  {rel}")
    print("\nNext, from that folder:\n  uv sync && uv run rbt generate && uv run pytest")
    if args.web:
        print("  (cd frontend && npm install) && uv run rbt generate && (cd frontend && npm run build)")
        print("  uv run playwright install chromium   # once, for the browser scenarios")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
