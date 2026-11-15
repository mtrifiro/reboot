#!/usr/bin/env python3
"""Show, preview, change and undo a Reboot web app's look: the values in
`frontend/web/src/tokens.css`, the one file the pages take every colour,
corner and typeface from (the frontend skill's `visual-interactive.md`).

Run from the project root.

    python3 look.py show
        The look now, and the choices.
    python3 look.py preview action teal,blue,#0a6e5c
    python3 look.py preview neutrals warm,cool,white
    python3 look.py preview type system,serif,rounded
    python3 look.py preview corners sharp,soft,round
    python3 look.py preview palette harbour,almond,ocean --page /board
        Writes frontend/web/public/look-preview.html: each choice lettered
        A, B, C..., showing the app's own page (`/` unless --page says)
        in frames with the choice's tokens applied, in light and, when
        the app has a dark scheme, dark. Where a frame can't show the
        page, a piece of the app (a masthead, a card, its buttons and
        status colours) stands in. It prints where the dev server serves
        it (/__/frontend/look-preview.html with the Reboot Vite plugin).
    python3 look.py set action teal       (or a brand's hex: #0a6e5c)
    python3 look.py set neutrals cool
    python3 look.py set palette harbour
    python3 look.py set type serif
    python3 look.py set corners round
        Changes the values in place in `:root`, after saving tokens.css,
        and keeps the dark scheme in step (derived from the new light
        values); removes the preview; prints the contrast check for both
        schemes; exits 3 when a pair fails it.
    python3 look.py dark
        Adds a dark scheme derived from the light one, for an app that
        has none.
    python3 look.py undo
        Puts back tokens.css as it was before the last `set` or `dark`.
    python3 look.py check
        The contrast check alone, both schemes.

Token names never change, only their values; a token the app doesn't
have is left out, never added. Standard library only.
"""

from __future__ import annotations

import colorsys
import html
import json
import re
import shutil
import sys
import time
from pathlib import Path

WEB = Path("frontend/web")
TOKENS = WEB / "src/tokens.css"
PREVIEW = WEB / "public/look-preview.html"
HISTORY = WEB / ".look-history"

ACTIONS = {
    "teal": "#1f5f5b", "blue": "#1d5fa8", "indigo": "#3f4aa8", "violet": "#6b3fa0",
    "plum": "#7a2e5a", "green": "#2f6f3e", "amber": "#8a5200", "slate": "#3d4a5c",
    "navy": "#1f2a44", "rust": "#9a3d16",
}
NEUTRALS = {
    "warm": {"canvas": "#f6f3ee", "surface": "#ffffff", "surface-sunk": "#efebe4", "surface-soft": "#efebe4",
             "ink": "#1f2328", "ink-soft": "#5d636b", "line": "#ddd6cb"},
    "cream": {"canvas": "#faf6ec", "surface": "#fffdf8", "surface-sunk": "#f1ebdc", "surface-soft": "#f1ebdc",
              "ink": "#2a2520", "ink-soft": "#6a6158", "line": "#e5dccb"},
    "cool": {"canvas": "#f3f5f8", "surface": "#ffffff", "surface-sunk": "#e9edf2", "surface-soft": "#e9edf2",
             "ink": "#1b2330", "ink-soft": "#566170", "line": "#d5dce5"},
    "grey": {"canvas": "#f4f4f5", "surface": "#ffffff", "surface-sunk": "#ebebed", "surface-soft": "#ebebed",
             "ink": "#1f1f23", "ink-soft": "#5f5f68", "line": "#dcdce0"},
    "white": {"canvas": "#ffffff", "surface": "#ffffff", "surface-sunk": "#f4f4f5", "surface-soft": "#f4f4f5",
              "ink": "#18181b", "ink-soft": "#5b5b63", "line": "#e4e4e7"},
}
# Whole palettes: the page, the cards, the text, the lines and the action
# colour, chosen together so they hold together. Each passes `check` as it
# stands; the cards are the page lightened, the sunk surfaces its own tone.
PALETTES = {
    "cherry": {"canvas": "#ffffff", "sunk": "#f5f5f5", "ink": "#1a1a1a", "ink-soft": "#404040",
               "line": "#cccccc", "action": "#de283b"},
    "crimson": {"canvas": "#e9e9e9", "sunk": "#dfdfdf", "ink": "#000000", "ink-soft": "#565656",
                "line": "#b7b7b7", "action": "#8b0000"},
    "studio": {"canvas": "#ffffff", "sunk": "#f5f5f5", "ink": "#333333", "ink-soft": "#5c5c5c",
               "line": "#cccccc", "action": "#3f51b5"},
    "ocean": {"canvas": "#ffffff", "sunk": "#f5f5f5", "ink": "#333333", "ink-soft": "#5c5c5c",
              "line": "#cccccc", "action": "#0077c2"},
    "parchment": {"canvas": "#f5ecd7", "sunk": "#ebe2cd", "ink": "#353535", "ink-soft": "#5f5f5f",
                  "line": "#c2baa6", "action": "#1e295a"},
    "cabin": {"canvas": "#e5e5e5", "sunk": "#dbdbdb", "ink": "#333333", "ink-soft": "#5c5c5c",
              "line": "#b3b3b3", "action": "#8b5d33"},
    "almond": {"canvas": "#f5f5dc", "sunk": "#ebebd2", "ink": "#000000", "ink-soft": "#5f5f5f",
               "line": "#c2c2aa", "action": "#8b5a2b"},
    "harbour": {"canvas": "#f2f2f2", "sunk": "#e8e8e8", "ink": "#333333", "ink-soft": "#5c5c5c",
                "line": "#bfbfbf", "action": "#2c3e50"},
    "lavender": {"canvas": "#e6e6fa", "sunk": "#d2d2f6", "ink": "#333333", "ink-soft": "#424242",
                 "line": "#b4b4c8", "action": "#6b5b95"},
    "midnight": {"canvas": "#ffffff", "sunk": "#e3f6f5", "ink": "#1e2022", "ink-soft": "#52616b",
                 "line": "#bae8e8", "action": "#272343"},
}
SANS = 'system-ui, -apple-system, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif'
TYPES = {
    "system": {"font-body": SANS, "font-display": SANS},
    "serif": {"font-body": SANS, "font-display": 'ui-serif, "Iowan Old Style", Georgia, "Times New Roman", serif'},
    "rounded": {"font-body": SANS, "font-display": 'ui-rounded, "SF Pro Rounded", "Arial Rounded MT Bold", ' + SANS},
    "humanist": {"font-body": 'Seravek, "Gill Sans Nova", Ubuntu, Calibri, "DejaVu Sans", sans-serif',
                 "font-display": 'Seravek, "Gill Sans Nova", Ubuntu, Calibri, "DejaVu Sans", sans-serif'},
    "book": {"font-body": 'ui-serif, "Iowan Old Style", Georgia, serif',
             "font-display": 'ui-serif, "Iowan Old Style", Georgia, serif'},
}
CORNERS = {
    "sharp": {"radius-sm": "2px", "radius-md": "3px", "radius-lg": "4px"},
    "soft": {"radius-sm": "4px", "radius-md": "8px", "radius-lg": "12px"},
    "round": {"radius-sm": "8px", "radius-md": "14px", "radius-lg": "20px"},
}
WORDS = {
    "action": "the colour of buttons, links and the selected thing",
    "neutrals": "the page, the cards, the text and the lines",
    "palette": "the page, the cards, the text, the lines and the action colour, together",
    "type": "the headings' and the text's typefaces (system faces, nothing to install)",
    "corners": "how round buttons, cards and fields are",
}


# -- tokens.css ---------------------------------------------------------------

ROOT_BLOCK = re.compile(r"(:root\s*\{)(.*?)(\})", re.S)
DECL = re.compile(r"--([a-z0-9-]+)\s*:\s*([^;]+);")


def read() -> str:
    if not TOKENS.is_file():
        raise SystemExit(f"look: no {TOKENS}; run from the project root of a web app built by the frontend skill")
    return TOKENS.read_text()


def tokens(css: str) -> dict[str, str]:
    """The first `:root` block's tokens, without the `--`."""
    m = ROOT_BLOCK.search(css)
    return {k: " ".join(v.split()) for k, v in DECL.findall(m.group(2))} if m else {}


DARK_BLOCK = re.compile(r"(@media\s*\(\s*prefers-color-scheme:\s*dark\s*\)\s*\{\s*:root\s*\{)(.*?)(\}\s*\})", re.S)
ACTION_KEYS = {"color-action", "color-action-hover", "color-action-soft", "color-on-action"}


def has_dark(css: str) -> bool:
    return bool(DARK_BLOCK.search(css))


def dark_tokens(css: str) -> dict[str, str]:
    """The dark scheme's tokens over the light ones: what a dark page uses."""
    m = DARK_BLOCK.search(css)
    dark = {k: " ".join(v.split()) for k, v in DECL.findall(m.group(2))} if m else {}
    return {**tokens(css), **dark}


def has_other_schemes(css: str) -> bool:
    """A scheme this script doesn't drive: a `data-theme` switch, or a dark
    block in another shape."""
    return bool(re.search(r"prefers-color-scheme:\s*dark|data-theme", css)) and not has_dark(css)


def set_values(css: str, values: dict[str, str]) -> tuple[str, list[str]]:
    """Each token's value in the first `:root` block, in place; the names
    the app has, changed."""
    m = ROOT_BLOCK.search(css)
    body, changed = m.group(2), []
    for name, value in values.items():
        new, n = re.subn(rf"(--{re.escape(name)}\s*:\s*)[^;]+;", lambda x: f"{x.group(1)}{value};", body, count=1)
        if n:
            body = new
            changed.append(name)
    return css[:m.start(2)] + body + css[m.end(2):], changed


def set_dark_values(css: str, values: dict[str, str]) -> tuple[str, list[str]]:
    """Each value in the dark block, which mirrors the light one: changed in
    place, added when the block lacks it; the block itself added, with
    `color-scheme: light dark` on the light `:root`, when there is none."""
    m = DARK_BLOCK.search(css)
    if not m:
        root = ROOT_BLOCK.search(css)
        if "color-scheme" not in root.group(2):
            css = css[:root.end(1)] + "\n  color-scheme: light dark;" + css[root.end(1):]
        lines = "".join(f"    --{k}: {v};\n" for k, v in values.items())
        return css.rstrip("\n") + f"\n\n@media (prefers-color-scheme: dark) {{\n  :root {{\n{lines}  }}\n}}\n", list(values)
    body, changed = m.group(2), []
    for name, value in values.items():
        new, n = re.subn(rf"(--{re.escape(name)}\s*:\s*)[^;]+;", lambda x: f"{x.group(1)}{value};", body, count=1)
        body = new if n else body.rstrip() + f"\n    --{name}: {value};\n  "
        changed.append(name)
    return css[:m.start(2)] + body + css[m.end(2):], changed


# -- colour -------------------------------------------------------------------

def rgb(hex_: str) -> tuple[float, float, float]:
    h = hex_.strip().lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))  # type: ignore[return-value]


def to_hex(r: float, g: float, b: float) -> str:
    return "#" + "".join(f"{round(max(0, min(1, c)) * 255):02x}" for c in (r, g, b))


def is_hex(v: str) -> bool:
    return bool(re.fullmatch(r"#[0-9a-fA-F]{3}([0-9a-fA-F]{3})?", v.strip()))


def luminance(hex_: str) -> float:
    def lin(c: float) -> float:
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = rgb(hex_)
    return 0.2126 * lin(r) + 0.7152 * lin(g) + 0.0722 * lin(b)


def contrast(a: str, b: str) -> float:
    la, lb = sorted((luminance(a), luminance(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


def mix(a: str, b: str, t: float) -> str:
    """`a` moved `t` of the way to `b`."""
    return to_hex(*(x + (y - x) * t for x, y in zip(rgb(a), rgb(b))))


def lighten(hex_: str, by: float) -> str:
    h, l, s = colorsys.rgb_to_hls(*rgb(hex_))
    return to_hex(*colorsys.hls_to_rgb(h, max(0, min(1, l + by)), s))


def action_values(choice: str, now: dict[str, str]) -> dict[str, str]:
    """The action family from a named colour or a hex: the colour (darkened
    until white text on it reads), its hover, its soft tint, its text."""
    base = ACTIONS.get(choice, choice)
    if not is_hex(base):
        raise SystemExit(f"look: no action colour '{choice}'; one of {', '.join(ACTIONS)}, or a hex such as #0a6e5c")
    canvas = now.get("color-canvas", "#ffffff") if is_hex(now.get("color-canvas", "")) else "#ffffff"
    for _ in range(40):
        if contrast(base, "#ffffff") >= 4.5 and contrast(base, canvas) >= 3:
            break
        base = lighten(base, -0.02)
    return {"color-action": base, "color-action-hover": lighten(base, -0.06),
            "color-action-soft": mix(base, "#ffffff", 0.88), "color-on-action": "#ffffff"}


def hls(h: float, l: float, s: float) -> str:
    return to_hex(*colorsys.hls_to_rgb(h, l, s))


def lighten_until(colour: str, on: str, need: float) -> str:
    """`colour` lightened, a step at a time, until it reads on `on`."""
    for _ in range(50):
        if contrast(colour, on) >= need:
            break
        colour = lighten(colour, 0.02)
    return colour


def derive_dark(t: dict[str, str]) -> dict[str, str]:
    """The dark scheme from the light one, as the frontend skill's tokens
    say: a near-black canvas with the light canvas's hue, cards a step
    lighter, near-white ink, the action and every status lightened until
    each reads. Only the tokens the app has."""
    def c(name: str) -> str | None:
        v = t.get(name, "")
        return v if is_hex(v) else None
    h, _, s = colorsys.rgb_to_hls(*rgb(c("color-canvas") or "#ffffff"))
    s = min(s, 0.18)
    canvas, surface, sunk = hls(h, 0.10, s), hls(h, 0.15, s), hls(h, 0.12, s)
    ink = hls(h, 0.93, min(s, 0.08))
    d = {"color-canvas": canvas, "color-surface": surface, "color-surface-sunk": sunk,
         "color-surface-soft": sunk, "color-line": hls(h, 0.26, s), "color-ink": ink,
         "color-ink-soft": lighten_until(hls(h, 0.66, min(s, 0.08)), surface, 4.5)}
    if c("color-action"):
        a = lighten_until(c("color-action"), surface, 4.5)
        d.update({"color-action": a, "color-action-hover": lighten(a, 0.06),
                  "color-action-soft": mix(a, canvas, 0.8),
                  "color-on-action": max(("#111111", ink), key=lambda x: contrast(x, a))})
    if c("color-danger"):
        d["color-danger"] = lighten_until(c("color-danger"), surface, 4.5)
    for name in t:
        if re.fullmatch(r"color-status-[a-z0-9-]+", name) and not name.endswith("-soft") and c(name):
            if f"{name}-soft" in t:
                tint = mix(c(name), canvas, 0.78)
                d[f"{name}-soft"], d[name] = tint, lighten_until(c(name), tint, 4.5)
            else:
                d[name] = lighten_until(c(name), surface, 3.0)
    return {k: v for k, v in d.items() if k in t}


def dark_for(kind: str, light: dict[str, str]) -> dict[str, str]:
    """The dark values a change of `kind` moves: all of them for a page's
    tones, the action family for an action colour, none for type or corners."""
    if kind in ("neutrals", "palette"):
        return derive_dark(light)
    if kind == "action":
        return {k: v for k, v in derive_dark(light).items() if k in ACTION_KEYS}
    return {}


def palette_values(choice: str) -> dict[str, str]:
    if choice not in PALETTES:
        raise SystemExit(f"look: no palette '{choice}'; one of {', '.join(PALETTES)}")
    p = PALETTES[choice]
    neutrals = {"color-canvas": p["canvas"], "color-surface": mix(p["canvas"], "#ffffff", 0.6),
                "color-surface-sunk": p["sunk"], "color-surface-soft": p["sunk"], "color-ink": p["ink"],
                "color-ink-soft": p["ink-soft"], "color-line": p["line"]}
    return {**neutrals, **action_values(p["action"], neutrals)}


def values_for(kind: str, choice: str, now: dict[str, str]) -> dict[str, str]:
    if kind == "action":
        return action_values(choice, now)
    if kind == "palette":
        return palette_values(choice)
    table = {"neutrals": NEUTRALS, "type": TYPES, "corners": CORNERS}.get(kind)
    if table is None:
        raise SystemExit(f"look: no kind '{kind}'; one of action, neutrals, palette, type, corners")
    if choice not in table:
        raise SystemExit(f"look: no {kind} '{choice}'; one of {', '.join(table)}")
    prefix = "color-" if kind == "neutrals" else ""
    return {prefix + k: v for k, v in table[choice].items()}


# -- the contrast check ------------------------------------------------------

def check(t: dict[str, str]) -> list[str]:
    """Each pair the pages draw text on, with what it must reach: 4.5 for
    text, 3 for a large shape (a button on the page)."""
    def c(name: str) -> str | None:
        v = t.get(name, "")
        return v if is_hex(v) else None
    pairs = [
        ("color-ink", "color-canvas", 4.5, "text on the page"),
        ("color-ink", "color-surface", 4.5, "text on a card"),
        ("color-ink-soft", "color-canvas", 4.5, "quiet text on the page"),
        ("color-ink-soft", "color-surface", 4.5, "quiet text on a card"),
        ("color-on-action", "color-action", 4.5, "a button's label"),
        ("color-action", "color-canvas", 3.0, "a button on the page"),
        ("color-action", "color-surface", 4.5, "a link on a card"),
        ("color-danger", "color-surface", 4.5, "an error on a card"),
    ]
    for name in t:
        m = re.fullmatch(r"color-status-([a-z0-9-]+?)", name)
        if m and not name.endswith("-soft"):
            soft = f"{name}-soft"
            pairs.append((name, soft if c(soft) else "color-surface", 4.5 if c(soft) else 3.0,
                          f"the '{m.group(1)}' status" + (" on its tint" if c(soft) else " on a card")))
    out = []
    for fg, bg, need, what in pairs:
        a, b = c(fg), c(bg)
        if a and b:
            r = contrast(a, b)
            out.append(f"{'ok  ' if r >= need else 'FAIL'} {r:5.2f} (needs {need}) {what}: --{fg} on --{bg}")
    return out


# -- commands -----------------------------------------------------------------

def show() -> None:
    css = read()
    t = tokens(css)
    def pick(*names: str) -> str:
        return ", ".join(f"--{n} {t[n]}" for n in names if n in t)
    statuses = [n for n in t if n.startswith("color-status-") and not n.endswith("-soft")]
    print("The look now")
    print("  action:   " + pick("color-action", "color-on-action"))
    print("  neutrals: " + pick("color-canvas", "color-surface", "color-ink", "color-ink-soft", "color-line"))
    print("  type:     " + pick("font-display", "font-body"))
    print("  corners:  " + pick("radius-sm", "radius-md", "radius-lg"))
    print(f"  statuses: {len(statuses)} ({', '.join(s.removeprefix('color-status-') for s in statuses)})")
    if has_dark(css):
        d = dark_tokens(css)
        print("  dark:     " + ", ".join(f"--{n} {d[n]}" for n in ("color-canvas", "color-ink", "color-action") if n in d)
              + " (follows the system; kept in step by `set`)")
    elif has_other_schemes(css):
        print("  note: tokens.css switches schemes another way; `set` changes `:root` only, so change the other by hand")
    else:
        print("  dark:     none; `dark` adds one derived from these")
    print("\nThe choices")
    print(f"  action:   {', '.join(ACTIONS)}, or a brand's hex  ({WORDS['action']})")
    print(f"  neutrals: {', '.join(NEUTRALS)}  ({WORDS['neutrals']})")
    print(f"  palette:  {', '.join(PALETTES)}  ({WORDS['palette']})")
    print(f"  type:     {', '.join(TYPES)}  ({WORDS['type']})")
    print(f"  corners:  {', '.join(CORNERS)}  ({WORDS['corners']})")


def app_name() -> str:
    for f in (Path("AGENTS.md"), Path("README.md")):
        if f.is_file():
            m = re.search(r"^#\s+(.+)$", f.read_text(), re.M)
            if m:
                return re.split(r"[:—–-]\s", m.group(1))[0].strip()
    return Path.cwd().name


def mock(vals: dict[str, str], name: str, statuses: list[str]) -> str:
    """A piece of the app drawn with `vals`: where a frame can't show a page."""
    style = "; ".join(f"--{k}: {v}" for k, v in vals.items())
    pills = "".join(
        f'<span class="pill" style="color: var(--{s}); background: var(--{s}-soft, var(--color-surface-sunk, '
        f'var(--color-canvas))); border-color: var(--{s})">{html.escape(s.removeprefix("color-status-"))}</span>'
        for s in statuses)
    return f"""<div class="mock app" hidden style="{html.escape(style)}">
    <header class="mast"><span class="mark">{name[:1]}</span><strong>{name}</strong>
      <nav><a aria-current="page">Today</a><a>All</a><a>Settings</a></nav></header>
    <main>
      <h1>A page heading</h1>
      <p class="soft">One line of quiet text under it.</p>
      <div class="card"><h3>A card</h3><p>Its text, and a <a class="link">link</a>.</p>{pills}
        <div class="row"><button class="primary">Primary action</button><button class="plain">Cancel</button>
        <span class="danger">Something went wrong</span></div></div>
    </main>
  </div>"""


def preview(kind: str, choices: list[str], page: str = "/") -> None:
    css = read()
    now = tokens(css)
    dark_now = dark_tokens(css) if has_dark(css) else None
    statuses = [n for n in now if n.startswith("color-status-") and not n.endswith("-soft")][:3]
    name = html.escape(app_name())
    def what(line: str) -> str:
        return line.split(") ", 1)[1].split(": ")[0]
    already = {"light": {what(x) for x in check(now) if x.startswith("FAIL")},
               "dark": {what(x) for x in check(dark_now or {}) if x.startswith("FAIL")}}
    sections, frames = [], []
    for i, choice in enumerate(choices):
        changes = values_for(kind, choice, now)
        light = {**now, **changes}
        schemes = [("light", light)]
        if dark_now is not None:
            same = {k: v for k, v in changes.items() if not k.startswith("color-")}
            schemes.append(("dark", {**dark_now, **same, **dark_for(kind, light)}))
        figures = []
        for scheme, vals in schemes:
            frames.append({"scheme": scheme, "values": vals})
            figures.append(f"""<figure><figcaption>{scheme.capitalize()}</figcaption>
  <div class="frame"><iframe data-n="{len(frames) - 1}" src="{html.escape(page)}" title="{scheme}"></iframe></div>
  {mock(vals, name, statuses)}</figure>""")
        # Only what this choice breaks: what fails already is the review's.
        fails = [f"{scheme}: " + what(line) for scheme, vals in schemes
                 for line in check(vals) if line.startswith("FAIL")
                 and what(line) not in already[scheme]]
        warn = f"<p class='warn'>Hard to read: {html.escape('; '.join(fails))}</p>" if fails else ""
        sections.append(f"""<section class="choice"><h2 class="label">{chr(65 + i)}: {html.escape(choice)}</h2>
<div class="pair">{''.join(figures)}</div>{warn}</section>""")
    page_html = f"""<!doctype html><html><head><meta charset="utf-8"><title>{name}: {kind} choices</title>
<style>
body {{ margin: 0; padding: 24px; font: 15px/1.5 {SANS}; background: #eceae6; color: #222; }}
.intro {{ max-width: 900px; margin: 0 0 16px; }}
.choice {{ margin: 0 0 28px; }}
.label {{ font-size: 16px; margin: 0 0 8px; }}
.pair {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(380px, 1fr)); gap: 16px; }}
figure {{ margin: 0; }}
figcaption {{ font-size: 13px; color: #555; margin-bottom: 4px; }}
.frame {{ position: relative; aspect-ratio: 16 / 10; overflow: hidden; border: 1px solid #ccc;
  border-radius: 10px; background: #fff; }}
.frame iframe {{ position: absolute; top: 0; left: 0; width: 1280px; height: 800px; border: 0;
  transform-origin: 0 0; }}
.app {{ background: var(--color-canvas); color: var(--color-ink); font-family: var(--font-body);
  border: 1px solid #ccc; border-radius: 10px; overflow: hidden; }}
.app[hidden] {{ display: none; }}
.mast {{ display: flex; gap: 12px; align-items: center; padding: 12px 16px; background: var(--color-surface);
  border-bottom: 1px solid var(--color-line); font-family: var(--font-display); }}
.mark {{ display: inline-grid; place-items: center; width: 28px; height: 28px; border-radius: var(--radius-md);
  background: var(--color-action); color: var(--color-on-action); font-weight: 700; }}
nav {{ display: flex; gap: 12px; margin-left: auto; font-size: 14px; }}
nav a {{ color: var(--color-ink-soft); }}
nav a[aria-current] {{ color: var(--color-action); font-weight: 600; }}
main {{ padding: 16px; }}
h1, h3 {{ font-family: var(--font-display); margin: 0 0 4px; }}
h1 {{ font-size: 24px; }} h3 {{ font-size: 17px; }}
.soft {{ color: var(--color-ink-soft); margin: 0 0 12px; }}
.card {{ background: var(--color-surface); border: 1px solid var(--color-line); border-radius: var(--radius-lg);
  padding: 14px; }}
.link {{ color: var(--color-action); text-decoration: underline; }}
.pill {{ display: inline-block; margin: 6px 6px 0 0; padding: 2px 10px; border: 1px solid;
  border-radius: var(--radius-sm); font-size: 13px; }}
.row {{ display: flex; gap: 8px; align-items: center; margin-top: 12px; flex-wrap: wrap; }}
button {{ font: inherit; padding: 6px 14px; border-radius: var(--radius-md); cursor: pointer; }}
.primary {{ background: var(--color-action); color: var(--color-on-action); border: 0; }}
.plain {{ background: transparent; color: var(--color-ink); border: 1px solid var(--color-line); }}
.danger {{ color: var(--color-danger); font-size: 14px; }}
.warn {{ color: #8a1c12; font-size: 13px; }}
.fallback {{ font-size: 13px; color: #555; }}
</style></head><body>
<p class="intro">{name}: {len(choices)} choice{"s" if len(choices) != 1 else ""} for {html.escape(WORDS.get(kind, kind))}, each shown on the app's own
page ({html.escape(page)}){" in light and dark" if dark_now is not None else ""}. Pick one by its letter.</p>
<p class="fallback" id="fallback" hidden>Where the page couldn't be shown, a piece of the app stands in, drawn
with the same colours.</p>
{''.join(sections)}
<script>
const FRAMES = {json.dumps(frames)};
const fit = f => {{ f.style.transform = `scale(${{f.parentElement.clientWidth / 1280}})`; }};
const fallBack = f => {{
  if (f.dataset.shown) return;
  f.parentElement.hidden = true;
  f.parentElement.nextElementSibling.hidden = false;
  document.getElementById("fallback").hidden = false;
}};
document.querySelectorAll("iframe[data-n]").forEach(f => {{
  const {{ scheme, values }} = FRAMES[f.dataset.n];
  fit(f);
  f.addEventListener("load", () => {{
    try {{
      const root = f.contentDocument.documentElement;
      for (const [k, v] of Object.entries(values)) root.style.setProperty(`--${{k}}`, v, "important");
      root.style.setProperty("color-scheme", scheme, "important");
      f.dataset.shown = "1";
    }} catch (e) {{ fallBack(f); }}
  }});
  setTimeout(() => fallBack(f), 15000);
}});
addEventListener("resize", () => document.querySelectorAll("iframe[data-n]").forEach(fit));
</script></body></html>"""
    PREVIEW.parent.mkdir(parents=True, exist_ok=True)
    PREVIEW.write_text(page_html)
    print(f"{PREVIEW}, served at {preview_path()} on the app's address")


def preview_path() -> str:
    """Where the dev server serves the preview. With the Reboot Vite plugin
    the web app's `public/` is under its base, and a page anywhere else is
    answered with the app itself."""
    for config in Path("frontend").glob("vite.config.*"):
        if re.search(r"reboot\([^)]*webAppPath", config.read_text()):
            return "/__/frontend/look-preview.html"
    return "/look-preview.html"


def save() -> None:
    HISTORY.mkdir(parents=True, exist_ok=True)
    shutil.copy2(TOKENS, HISTORY / f"tokens-{time.time_ns():020d}.css")


def set_(kind: str, choice: str) -> int:
    css = read()
    now = tokens(css)
    values = values_for(kind, choice, now)
    save()
    new, changed = set_values(css, values)
    print(f"set {kind} {choice}: " + (", ".join(f"--{n}" for n in changed) or "nothing (the app has none of its tokens)"))
    if has_dark(new):
        dark = dark_for(kind, tokens(new))
        if dark:
            new, _ = set_dark_values(new, dark)
            print("  dark, kept in step: " + ", ".join(f"--{n}" for n in dark))
    elif has_other_schemes(css):
        print("note: tokens.css switches schemes another way; it was not changed")
    TOKENS.write_text(new)
    PREVIEW.unlink(missing_ok=True)
    return report(new)


def add_dark() -> int:
    css = read()
    if has_dark(css):
        raise SystemExit("look: tokens.css has a dark scheme already; `set` keeps it in step")
    if has_other_schemes(css):
        raise SystemExit("look: tokens.css switches schemes another way; change it by hand")
    save()
    new, changed = set_dark_values(css, derive_dark(tokens(css)))
    TOKENS.write_text(new)
    print(f"added a dark scheme, following the system: {len(changed)} colours")
    return report(new)


def undo() -> None:
    saved = sorted(HISTORY.glob("tokens-*.css")) if HISTORY.is_dir() else []
    if not saved:
        raise SystemExit("look: nothing to undo")
    shutil.copy2(saved[-1], TOKENS)
    saved[-1].unlink()
    print(f"put back {TOKENS} from before the last change")


def check_both(css: str) -> list[str]:
    """The check for the light scheme, and for the dark one when there is one."""
    lines = check(tokens(css))
    if has_dark(css):
        lines = [f"light {line}" for line in lines] + [f"dark  {line}" for line in check(dark_tokens(css))]
    return lines


def report(css: str) -> int:
    lines = check_both(css)
    print("\n".join(lines) or "no colour pairs to check")
    return 3 if any("FAIL" in line.split(" (")[0] for line in lines) else 0


def main(argv: list[str]) -> int:
    page = "/"
    if "--page" in argv:
        i = argv.index("--page")
        page, argv = argv[i + 1], argv[:i] + argv[i + 2:]
    if argv[:1] == ["show"]:
        show()
    elif argv[:1] == ["preview"] and len(argv) == 3:
        preview(argv[1], [c.strip() for c in argv[2].split(",") if c.strip()], page)
    elif argv[:1] == ["set"] and len(argv) == 3:
        return set_(argv[1], argv[2])
    elif argv == ["dark"]:
        return add_dark()
    elif argv == ["undo"]:
        undo()
    elif argv == ["check"]:
        return report(read())
    else:
        print(__doc__)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
