#!/usr/bin/env python3
"""Show or set a web app's accent, one of the house palette's colors.

    python3 <this file>                # list the palettes, the current one marked
    python3 <this file> teal           # set it in the project in this directory

Rewrites the accent family (--accent, --on-accent, --accent-deep,
--on-deep, --accent-tint, --bg-glow) in the light and both dark blocks
of frontend/web/src/styles.css, and the old accent's color in
frontend/web/public/favicon.svg. Everything else in the stylesheet
derives from these. A brand's own colors replace these values by hand
instead. Standard library only.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

STYLESHEET = Path("frontend/web/src/styles.css")
FAVICON = Path("frontend/web/public/favicon.svg")

PALETTES: dict[str, dict[str, dict[str, str]]] = {
    "navy": {
        "light": {"accent": "#103761", "on-accent": "#ffffff", "accent-deep": "#13294a", "on-deep": "#f7f5ed", "accent-tint": "#e6f3dc", "bg-glow": "#f1eee4"},
        "dark": {"accent": "#9cc4f2", "on-accent": "#0b1f36", "accent-deep": "#07182b", "on-deep": "#f7f5ed", "accent-tint": "#1f3d3a", "bg-glow": "#0e2440"},
    },
    "teal": {
        "light": {"accent": "#076c6a", "on-accent": "#ffffff", "accent-deep": "#023534", "on-deep": "#f4f4f7", "accent-tint": "#d5f0ee", "bg-glow": "#e4efee"},
        "dark": {"accent": "#4bc2be", "on-accent": "#012221", "accent-deep": "#011514", "on-deep": "#e4efee", "accent-tint": "#003231", "bg-glow": "#101f1e"},
    },
    "cyan": {
        "light": {"accent": "#026983", "on-accent": "#ffffff", "accent-deep": "#00435a", "on-deep": "#f4f4f7", "accent-tint": "#d6eef8", "bg-glow": "#e4eef2"},
        "dark": {"accent": "#48bee2", "on-accent": "#00212a", "accent-deep": "#00141b", "on-deep": "#e4eef2", "accent-tint": "#00303d", "bg-glow": "#111e23"},
    },
    "blue": {
        "light": {"accent": "#0163ac", "on-accent": "#ffffff", "accent-deep": "#012f55", "on-deep": "#f4f4f7", "accent-tint": "#dcecfd", "bg-glow": "#e6edf4"},
        "dark": {"accent": "#6eb6fe", "on-accent": "#001d39", "accent-deep": "#001126", "on-deep": "#e6edf4", "accent-tint": "#0d2c49", "bg-glow": "#151d26"},
    },
    "indigo": {
        "light": {"accent": "#3351df", "on-accent": "#ffffff", "accent-deep": "#13226e", "on-deep": "#f4f4f7", "accent-tint": "#e1e9fe", "bg-glow": "#e9ecf5"},
        "dark": {"accent": "#9cacfe", "on-accent": "#131642", "accent-deep": "#060e2b", "on-deep": "#e9ecf5", "accent-tint": "#1c284a", "bg-glow": "#181c26"},
    },
    "violet": {
        "light": {"accent": "#5b3fd6", "on-accent": "#ffffff", "accent-deep": "#2b1a6b", "on-deep": "#f4f4f7", "accent-tint": "#ebe6fb", "bg-glow": "#ecebf4"},
        "dark": {"accent": "#b4a1ff", "on-accent": "#1b1340", "accent-deep": "#0f0b2a", "on-deep": "#ecebf4", "accent-tint": "#2a2448", "bg-glow": "#1a1b26"},
    },
    "purple": {
        "light": {"accent": "#8734c9", "on-accent": "#ffffff", "accent-deep": "#3e1061", "on-deep": "#f4f4f7", "accent-tint": "#eee5fa", "bg-glow": "#eeeaf3"},
        "dark": {"accent": "#c99ef9", "on-accent": "#260e3a", "accent-deep": "#170826", "on-deep": "#eeeaf3", "accent-tint": "#322144", "bg-glow": "#1e1a24"},
    },
    "plum": {
        "light": {"accent": "#a0309a", "on-accent": "#ffffff", "accent-deep": "#4e034c", "on-deep": "#f4f4f7", "accent-tint": "#f5e3f3", "bg-glow": "#f1e9f0"},
        "dark": {"accent": "#e099da", "on-accent": "#30092e", "accent-deep": "#1f051d", "on-deep": "#f1e9f0", "accent-tint": "#3c1d39", "bg-glow": "#221821"},
    },
    "rose": {
        "light": {"accent": "#b7186e", "on-accent": "#ffffff", "accent-deep": "#570131", "on-deep": "#f4f4f7", "accent-tint": "#fbe2ea", "bg-glow": "#f3e9ec"},
        "dark": {"accent": "#f295ba", "on-accent": "#37051e", "accent-deep": "#240312", "on-deep": "#f3e9ec", "accent-tint": "#421b2c", "bg-glow": "#24181c"},
    },
}

# A :root block: its selector and its body, up to the closing brace.
BLOCK = re.compile(r"([^{}]*:root[^{}]*)\{([^{}]*)\}")


def scheme(body: str) -> str | None:
    if "color-scheme: dark" in body:
        return "dark"
    if "color-scheme: light" in body:
        return "light"
    return None


def light_accent(css: str) -> str | None:
    for match in BLOCK.finditer(css):
        if scheme(match.group(2)) == "light":
            found = re.search(r"--accent:\s*(#[0-9a-fA-F]{3,8})\b", match.group(2))
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
        print(f"accent: no {STYLESHEET}; run from the project root", file=sys.stderr)
        return 2
    css = STYLESHEET.read_text(encoding="utf-8")
    now = light_accent(css)
    if not argv:
        for name, palette in PALETTES.items():
            mark = "*" if palette["light"]["accent"] == now else " "
            print(f"{mark} {name:<7} {palette['light']['accent']} light, "
                  f"{palette['dark']['accent']} dark")
        return 0
    name = argv[0]
    if name not in PALETTES:
        print(f"accent: no palette '{name}'; one of: {', '.join(PALETTES)}", file=sys.stderr)
        return 2
    palette = PALETTES[name]
    STYLESHEET.write_text(set_tokens(css, palette), encoding="utf-8")
    if FAVICON.is_file() and now:
        svg = FAVICON.read_text(encoding="utf-8")
        FAVICON.write_text(
            re.sub(re.escape(now), palette["light"]["accent"], svg, flags=re.I),
            encoding="utf-8",
        )
    print(f"Accent: {name}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
