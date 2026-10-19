#!/usr/bin/env python3
"""Show or set a web app's palette: its page, text, lines and accent together.

    python3 <this file>                # list the palettes, the current one marked
    python3 <this file> sand-brown     # set it in the project in this directory

`house` is Reboot's own (cream paper, navy ink and accent); the others
pair a gray and an accent from Radix Colors (palettes.json beside this
file; its MIT notice is palettes.LICENSE). Rewrites the colour tokens in
the light and both dark blocks of frontend/web/src/styles.css, names a
Radix palette's source in a comment at the stylesheet's top, and puts the
new accent in frontend/web/public/favicon.svg. Everything else in the
stylesheet derives from these. A brand's own colors replace these values
by hand instead. Standard library only.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

STYLESHEET = Path("frontend/web/src/styles.css")
FAVICON = Path("frontend/web/public/favicon.svg")
PALETTES_FILE = Path(__file__).resolve().parent / "palettes.json"

HOUSE = {
    "source": "the house look: cream paper, navy ink and accent",
    "light": {"bg": "#f7f5ed", "bg-2": "#ffffff", "panel": "#ffffff", "ink": "#103761", "muted": "#506a85",
              "line": "#d9dfe6", "track": "#ece9df", "accent": "#103761", "on-accent": "#ffffff",
              "accent-deep": "#13294a", "on-deep": "#f7f5ed", "accent-tint": "#e6f3dc", "bg-glow": "#f1eee4"},
    "dark": {"bg": "#0b1f36", "bg-2": "#112a47", "panel": "#112a47", "ink": "#f7f5ed", "muted": "#9aabbf",
             "line": "#24405f", "track": "#1a3354", "accent": "#9cc4f2", "on-accent": "#0b1f36",
             "accent-deep": "#07182b", "on-deep": "#f7f5ed", "accent-tint": "#1f3d3a", "bg-glow": "#0e2440"},
}

# A :root block: its selector and its body, up to the closing brace.
BLOCK = re.compile(r"([^{}]*:root[^{}]*)\{([^{}]*)\}")
CREDIT = re.compile(r"/\* Palette: [^*]*\*/\n")


def palettes() -> dict[str, dict]:
    found = {"house": HOUSE}
    found.update(json.loads(PALETTES_FILE.read_text(encoding="utf-8")))
    return found


def scheme(body: str) -> str | None:
    if "color-scheme: dark" in body:
        return "dark"
    if "color-scheme: light" in body:
        return "light"
    return None


def light_value(css: str, token: str) -> str | None:
    for match in BLOCK.finditer(css):
        if scheme(match.group(2)) == "light":
            found = re.search(r"--%s:\s*(#[0-9a-fA-F]{3,8})\b" % re.escape(token), match.group(2))
            if found:
                return found.group(1).lower()
    return None


def set_tokens(css: str, palette: dict[str, dict[str, str]]) -> str:
    def block(match: re.Match[str]) -> str:
        selector, body = match.group(1), match.group(2)
        which = scheme(body)
        if which is None:
            return match.group(0)
        for token, value in palette[which].items():
            body = re.sub(
                r"(--%s:\s*)#[0-9a-fA-F]{3,8}\b" % re.escape(token),
                lambda m: m.group(1) + value,
                body,
            )
        return selector + "{" + body + "}"

    return BLOCK.sub(block, css)


def main(argv: list[str]) -> int:
    if not STYLESHEET.is_file():
        print(f"palette: no {STYLESHEET}; run from the project root", file=sys.stderr)
        return 2
    css = STYLESHEET.read_text(encoding="utf-8")
    found = palettes()
    accent, bg = light_value(css, "accent"), light_value(css, "bg")
    if not argv:
        for name, p in found.items():
            mark = "*" if (p["light"]["accent"], p["light"]["bg"]) == (accent, bg) else " "
            print(f"{mark} {name:<14} accent {p['light']['accent']} light, {p['dark']['accent']} dark")
        return 0
    name = argv[0]
    if name not in found:
        print(f"palette: no palette '{name}'; one of: {', '.join(found)}", file=sys.stderr)
        return 2
    palette = found[name]
    css = CREDIT.sub("", set_tokens(css, palette))
    if name != "house":
        css = (f"/* Palette: {name}, colors from Radix Colors (https://github.com/radix-ui/colors), "
               f"Copyright (c) 2021 Radix, MIT License. */\n") + css
    STYLESHEET.write_text(css, encoding="utf-8")
    if FAVICON.is_file() and accent:
        svg = FAVICON.read_text(encoding="utf-8")
        FAVICON.write_text(re.sub(re.escape(accent), palette["light"]["accent"], svg, flags=re.I), encoding="utf-8")
    print(f"Palette: {name} ({palette['source']})")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
