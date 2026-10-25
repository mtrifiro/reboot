#!/usr/bin/env python3
"""Show or set a web app's palette: its page, text, lines and accent together.

    python3 <this file>                # list the palettes, the current one marked
    python3 <this file> sand-brown     # set it in the project in this directory
    python3 <this file> sand-brown --band deep --paper tinted
                                       # with its band (calm, deep or hue) and
                                       # paper (white or tinted); calm and white
                                       # when not given
    python3 <this file> pick           # one of the fifteen with a band and a paper,
                                       # picked by this folder's name: prints
                                       # "sand-brown --band deep --paper tinted"
    python3 <this file> pick sage-teal slate-blue sand-gold
                                       # one of those, the same way
    python3 <this file> --css design/comp/comp.css sand-brown --band hue
                                       # on a copy of the stylesheet (the comp)
    python3 <this file> --from '#2f6b4f'   # the palette nearest a brand colour:
                                       # prints it and how far off, changing nothing
    python3 <this file> --from '#2f6b4f' --set   # and sets it in the project

`house` is Reboot's own (cream paper, navy ink and accent); the others
pair a gray and an accent from Radix Colors (palettes.json beside this
file; its MIT notice is palettes.LICENSE). A Radix palette has a band
and a paper as well, so fifteen palettes make ninety pages, not fifteen
hues of one: the band (the page head) is calm, a light tint of the accent; deep,
the gray's darkest step, as the top bar; or hue, the accent's darkest
step, as the house look's navy. The paper is white, the gray's second
step, or tinted, its third, the panels lifting off it as they do off the
house look's cream. `house` keeps its own. Rewrites the colour tokens in
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
BANDS = ("calm", "deep", "hue")
PAPERS = ("white", "tinted")
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


def band_paper(name: str, found: dict[str, dict], band: str, paper: str) -> dict[str, dict[str, str]]:
    """The tokens a band and a paper change on a Radix palette, per scheme:
    calm leaves the band as the palette has it; deep takes the palette's
    own deep entry (the gray's darkest step); hue makes the band the
    accent's darkest step with the tint on it (light), a dark wash of the
    hue with the ink on it (dark). Tinted paper moves the page one gray
    step up and the glow with it; the panels keep their step and lift."""
    p = found[name]
    out: dict[str, dict[str, str]] = {"light": {}, "dark": {}}
    if band == "deep":
        out = {w: dict(p["deep"][w]) for w in ("light", "dark")}
    elif band == "hue":
        out["light"] = {"accent-deep": p["light"]["on-deep"], "on-deep": p["light"]["accent-deep"]}
        out["dark"] = {"accent-deep": p["dark"]["accent-tint"], "on-deep": p["dark"]["ink"]}
    if paper == "tinted":
        out["light"].update({"bg": p["light"]["bg-glow"], "bg-glow": p["light"]["track"]})
        out["dark"].update({"bg": p["dark"]["bg-2"], "bg-glow": p["dark"]["panel"]})
    return out


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


def pick_feel(folder: str) -> tuple[str, str]:
    """The band and the paper for a folder, as `pick` does the palette."""
    def at(key: str, n: int) -> int:
        return int(hashlib.sha256(key.encode()).hexdigest(), 16) % n
    return BANDS[at(folder + "/band", len(BANDS))], PAPERS[at(folder + "/paper", len(PAPERS))]


def pick(names: list[str], folder: str) -> str:
    """One of the names, the same for a folder every time, different
    across folders: two builds of one prompt don't share a palette.
    With no names, the fifteen (never house, which is asked for by
    name): a build's own nomination repeats (hotel-330 to -332 each put
    sand-bronze first for a hotel), the folder's hash doesn't. Each is
    as likely as the next: picking the gray family first (10-23) gave
    olive-grass, alone in its family, one build in five (hotel-335 and
    -337 both Meadow)."""
    def at(key: str, n: int) -> int:
        return int(hashlib.sha256(key.encode()).hexdigest(), 16) % n
    return sorted(names)[at(folder, len(names))]


def main(argv: list[str]) -> int:
    global STYLESHEET
    found = palettes()
    band, paper = "calm", "white"
    rest: list[str] = []
    i = 0
    while i < len(argv):
        if argv[i] in ("--band", "--paper", "--css") and i + 1 < len(argv):
            if argv[i] == "--band":
                band = argv[i + 1]
            elif argv[i] == "--paper":
                paper = argv[i + 1]
            else:
                STYLESHEET = Path(argv[i + 1])
            i += 2
        else:
            rest.append(argv[i])
            i += 1
    argv = rest
    if band not in BANDS or paper not in PAPERS:
        print(f"palette: --band takes {', '.join(BANDS)}; --paper takes {', '.join(PAPERS)}", file=sys.stderr)
        return 2
    if argv[:1] == ["pick"]:
        names = argv[1:] or [n for n in found if n != "house"]
        unknown = [n for n in names if n not in found]
        if unknown:
            print(f"palette: pick takes palette names; {', '.join(unknown)} not one of: "
                  f"{', '.join(found)}", file=sys.stderr)
            return 2
        folder = Path.cwd().name
        band, paper = pick_feel(folder)
        print(f"{pick(names, folder)} --band {band} --paper {paper}")
        return 0
    if argv[:1] == ["--from"] and len(argv) in (2, 3) and argv[2:] in ([], ["--set"]):
        brand = argv[1].strip()
        if not re.fullmatch(r"#[0-9a-fA-F]{6}", brand):
            print("palette: --from takes a colour as #rrggbb", file=sys.stderr)
            return 2
        name, off = nearest(brand.lower(), found)
        p = found[name]
        print(f"nearest to {brand}: {name} ({p['label']}: {p['colours']}), accent {p['light']['accent']}, "
              f"{off:.0f} degrees of hue away" + ("; close" if off <= 15 else "; the nearest of the sixteen, not a match"))
        if argv[2:] != ["--set"]:
            return 0
        argv = [name]
    if not argv:
        css = STYLESHEET.read_text(encoding="utf-8") if STYLESHEET.is_file() else ""
        accent, ink = light_value(css, "accent"), light_value(css, "ink")
        for name, p in found.items():
            mark = "*" if (p["light"]["accent"], p["light"]["ink"]) == (accent, ink) else " "
            print(f"{mark} {name:<14} {p.get('label', ''):<9} {p.get('colours', ''):<18} "
                  f"accent {p['light']['accent']} light, {p['dark']['accent']} dark")
        return 0
    if not STYLESHEET.is_file():
        print(f"palette: no {STYLESHEET}; run from the project root", file=sys.stderr)
        return 2
    css = STYLESHEET.read_text(encoding="utf-8")
    accent, ink = light_value(css, "accent"), light_value(css, "ink")
    if not argv:
        for name, p in found.items():
            mark = "*" if (p["light"]["accent"], p["light"]["ink"]) == (accent, ink) else " "
            print(f"{mark} {name:<14} {p.get('label', ''):<9} {p.get('colours', ''):<18} "
                  f"accent {p['light']['accent']} light, {p['dark']['accent']} dark")
        return 0
    name = argv[0]
    if name not in found:
        print(f"palette: no palette '{name}'; one of: {', '.join(found)}", file=sys.stderr)
        return 2
    palette = found[name]
    css = set_tokens(css, palette)
    feel = ""
    if name != "house":
        css = set_tokens(css, band_paper(name, found, band, paper))
        feel = f", {band} band, {paper} paper"
    css = CREDIT.sub("", css)
    if name != "house":
        css = (f"/* Palette: {name}{feel}, colors from Radix Colors (https://github.com/radix-ui/colors), "
               f"Copyright (c) 2021 Radix, MIT License. */\n") + css
    STYLESHEET.write_text(css, encoding="utf-8")
    if STYLESHEET == Path("frontend/web/src/styles.css") and FAVICON.is_file() and accent:
        svg = FAVICON.read_text(encoding="utf-8")
        FAVICON.write_text(re.sub(re.escape(accent), palette["light"]["accent"], svg, flags=re.I), encoding="utf-8")
    print(f"Palette: {name}{feel} ({palette['source']})")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
