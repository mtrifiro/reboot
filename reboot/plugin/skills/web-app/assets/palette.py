#!/usr/bin/env python3
"""Show or set a web app's palette: its page, text, lines and accent together.

    python3 <this file>                # list the palettes, the current one marked
    python3 <this file> sand-brown     # set it in the project in this directory
    python3 <this file> pick           # one of the ten, picked by this folder's
                                       # name: prints its name
    python3 <this file> pick sage-teal slate-blue sand-gold
                                       # one of those, the same way
    python3 <this file> --from '#2f6b4f'   # the palette nearest a brand colour:
                                       # prints it and how far off, changing nothing
    python3 <this file> --from '#2f6b4f' --set   # and sets it in the project

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

import colorsys
import hashlib
import json
import re
import sys
from pathlib import Path

STYLESHEET = Path("frontend/web/src/styles.css")
FAVICON = Path("frontend/web/public/favicon.svg")
PALETTES_FILE = Path(__file__).resolve().parent / "palettes.json"

HOUSE = {
    "label": "Reboot", "colours": "cream and navy",
    "source": "the house look: cream paper, navy ink and accent",
    "light": {"bg": "#f7f5ed", "bg-2": "#ffffff", "panel": "#ffffff", "ink": "#103761", "muted": "#506a85",
              "line": "#d9dfe6", "track": "#ece9df", "accent": "#103761", "on-accent": "#ffffff",
              "accent-deep": "#13294a", "on-deep": "#f7f5ed", "accent-tint": "#e6f3dc", "bg-glow": "#f1eee4",
              "bar": "#13294a", "on-bar": "#f7f5ed", "good": "#3f7a2e", "warn": "#a8660f", "bad": "#b42318"},
    "dark": {"bg": "#0b1f36", "bg-2": "#112a47", "panel": "#112a47", "ink": "#f7f5ed", "muted": "#9aabbf",
             "line": "#24405f", "track": "#1a3354", "accent": "#9cc4f2", "on-accent": "#0b1f36",
             "accent-deep": "#07182b", "on-deep": "#f7f5ed", "accent-tint": "#1f3d3a", "bg-glow": "#0e2440",
             "bar": "#07182b", "on-bar": "#f7f5ed", "good": "#8ccb6b", "warn": "#f2c784", "bad": "#f07a6e"},
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


def hue(hex_colour: str) -> float:
    r, g, b = (int(hex_colour[i:i + 2], 16) / 255 for i in (1, 3, 5))
    return colorsys.rgb_to_hls(r, g, b)[0] * 360


def nearest(brand: str, found: dict[str, dict]) -> tuple[str, float]:
    """The palette whose light accent is nearest the brand colour in hue."""
    def off(name: str) -> float:
        d = abs(hue(found[name]["light"]["accent"]) - hue(brand)) % 360
        return min(d, 360 - d)
    name = min((n for n in found if n != "house"), key=off)
    return name, off(name)


def pick(names: list[str], folder: str) -> str:
    """One of the names, the same for a folder every time, different
    across folders: two builds of one prompt don't share a palette.
    With no names, the ten (never house, which is asked for by name):
    a build's own nomination repeats (hotel-330 to -332 each put
    sand-bronze first for a hotel), the folder's hash doesn't. The gray
    family (the part before the hyphen) is picked first, then the
    accent within it: four of the ten are sand, and a flat pick put
    four hotels in a row on warm paper."""
    def at(key: str, n: int) -> int:
        return int(hashlib.sha256(key.encode()).hexdigest(), 16) % n
    families: dict[str, list[str]] = {}
    for name in names:
        families.setdefault(name.split("-")[0], []).append(name)
    family = sorted(families)[at(folder, len(families))]
    return families[family][at(folder + "/" + family, len(families[family]))]


def main(argv: list[str]) -> int:
    found = palettes()
    if argv[:1] == ["pick"]:
        names = argv[1:] or [n for n in found if n != "house"]
        unknown = [n for n in names if n not in found]
        if unknown:
            print(f"palette: pick takes palette names; {', '.join(unknown)} not one of: "
                  f"{', '.join(found)}", file=sys.stderr)
            return 2
        print(pick(names, Path.cwd().name))
        return 0
    if argv[:1] == ["--from"] and len(argv) in (2, 3) and argv[2:] in ([], ["--set"]):
        brand = argv[1].strip()
        if not re.fullmatch(r"#[0-9a-fA-F]{6}", brand):
            print("palette: --from takes a colour as #rrggbb", file=sys.stderr)
            return 2
        name, off = nearest(brand.lower(), found)
        p = found[name]
        print(f"nearest to {brand}: {name} ({p['label']}: {p['colours']}), accent {p['light']['accent']}, "
              f"{off:.0f} degrees of hue away" + ("; close" if off <= 15 else "; the nearest of the eleven, not a match"))
        if argv[2:] != ["--set"]:
            return 0
        argv = [name]
    if not argv:
        css = STYLESHEET.read_text(encoding="utf-8") if STYLESHEET.is_file() else ""
        accent, bg = light_value(css, "accent"), light_value(css, "bg")
        for name, p in found.items():
            mark = "*" if (p["light"]["accent"], p["light"]["bg"]) == (accent, bg) else " "
            print(f"{mark} {name:<14} {p.get('label', ''):<8} {p.get('colours', ''):<18} "
                  f"accent {p['light']['accent']} light, {p['dark']['accent']} dark")
        return 0
    if not STYLESHEET.is_file():
        print(f"palette: no {STYLESHEET}; run from the project root", file=sys.stderr)
        return 2
    css = STYLESHEET.read_text(encoding="utf-8")
    accent, bg = light_value(css, "accent"), light_value(css, "bg")
    if not argv:
        for name, p in found.items():
            mark = "*" if (p["light"]["accent"], p["light"]["bg"]) == (accent, bg) else " "
            print(f"{mark} {name:<14} {p.get('label', ''):<8} {p.get('colours', ''):<18} "
                  f"accent {p['light']['accent']} light, {p['dark']['accent']} dark")
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
