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
        Writes frontend/web/public/look-preview.html: each choice lettered
        A, B, C..., drawn as a piece of the app (a masthead, a card, its
        buttons and status colours). The dev server serves it at
        /look-preview.html.
    python3 look.py set action teal       (or a brand's hex: #0a6e5c)
    python3 look.py set neutrals cool
    python3 look.py set type serif
    python3 look.py set corners round
        Changes the values in place in `:root`, after saving tokens.css;
        removes the preview; prints the contrast check; exits 3 when a pair
        fails it.
    python3 look.py undo
        Puts back tokens.css as it was before the last `set`.
    python3 look.py check
        The contrast check alone.

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


def has_other_schemes(css: str) -> bool:
    return bool(re.search(r"prefers-color-scheme:\s*dark|data-theme", css))


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


def values_for(kind: str, choice: str, now: dict[str, str]) -> dict[str, str]:
    if kind == "action":
        return action_values(choice, now)
    table = {"neutrals": NEUTRALS, "type": TYPES, "corners": CORNERS}.get(kind)
    if table is None:
        raise SystemExit(f"look: no kind '{kind}'; one of action, neutrals, type, corners")
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
    if has_other_schemes(css):
        print("  note: tokens.css has a dark scheme too; `set` changes `:root` only, so change the dark one by hand")
    print("\nThe choices")
    print(f"  action:   {', '.join(ACTIONS)}, or a brand's hex  ({WORDS['action']})")
    print(f"  neutrals: {', '.join(NEUTRALS)}  ({WORDS['neutrals']})")
    print(f"  type:     {', '.join(TYPES)}  ({WORDS['type']})")
    print(f"  corners:  {', '.join(CORNERS)}  ({WORDS['corners']})")


def app_name() -> str:
    for f in (Path("AGENTS.md"), Path("README.md")):
        if f.is_file():
            m = re.search(r"^#\s+(.+)$", f.read_text(), re.M)
            if m:
                return re.split(r"[:—–-]\s", m.group(1))[0].strip()
    return Path.cwd().name


def preview(kind: str, choices: list[str]) -> None:
    css = read()
    now = tokens(css)
    statuses = [n for n in now if n.startswith("color-status-") and not n.endswith("-soft")][:3]
    name = html.escape(app_name())
    cards = []
    for i, choice in enumerate(choices):
        changes = values_for(kind, choice, now)
        vals = {**now, **changes}
        style = "; ".join(f"--{k}: {v}" for k, v in vals.items())
        pills = "".join(
            f'<span class="pill" style="color: var(--{s}); background: var(--{s}-soft, var(--color-surface-sunk, '
            f'var(--color-canvas))); border-color: var(--{s})">{html.escape(s.removeprefix("color-status-"))}</span>'
            for s in statuses)
        # Only the pairs this choice changes: what fails already is the review's.
        fails = [line for line in check(vals) if line.startswith("FAIL")
                 and any(f"--{n} " in line + " " for n in changes)]
        cards.append(f"""
<section class="choice" style="{html.escape(style)}">
  <h2 class="label">{chr(65 + i)}: {html.escape(choice)}</h2>
  <div class="app">
    <header class="mast"><span class="mark">{name[:1]}</span><strong>{name}</strong>
      <nav><a aria-current="page">Today</a><a>All</a><a>Settings</a></nav></header>
    <main>
      <h1>A page heading</h1>
      <p class="soft">One line of quiet text under it.</p>
      <div class="card"><h3>A card</h3><p>Its text, and a <a class="link">link</a>.</p>{pills}
        <div class="row"><button class="primary">Primary action</button><button class="plain">Cancel</button>
        <span class="danger">Something went wrong</span></div></div>
    </main>
  </div>
  {"<p class='warn'>Hard to read: " + html.escape("; ".join(f.split(") ", 1)[1].split(": ")[0] for f in fails)) + "</p>" if fails else ""}
</section>""")
    page = f"""<!doctype html><html><head><meta charset="utf-8"><title>{name}: {kind} choices</title>
<style>
body {{ margin: 0; padding: 24px; font: 15px/1.5 {SANS}; background: #eceae6; color: #222; }}
.intro {{ max-width: 900px; margin: 0 auto 16px; }}
.grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(420px, 1fr)); gap: 20px; }}
.label {{ font-size: 15px; margin: 0 0 8px; }}
.app {{ background: var(--color-canvas); color: var(--color-ink); font-family: var(--font-body);
  border: 1px solid #ccc; border-radius: 10px; overflow: hidden; }}
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
</style></head><body>
<p class="intro">{name}: {len(choices)} choices for {html.escape(WORDS.get(kind, kind))}, each drawn with the app's own
tokens. Pick one by its letter.</p>
<div class="grid">{''.join(cards)}</div></body></html>"""
    PREVIEW.parent.mkdir(parents=True, exist_ok=True)
    PREVIEW.write_text(page)
    print(f"{PREVIEW} (served at /look-preview.html)")


def save() -> None:
    HISTORY.mkdir(parents=True, exist_ok=True)
    shutil.copy2(TOKENS, HISTORY / f"tokens-{time.strftime('%Y%m%d-%H%M%S')}-{time.time_ns() % 10**6:06d}.css")


def set_(kind: str, choice: str) -> int:
    css = read()
    now = tokens(css)
    values = values_for(kind, choice, now)
    save()
    new, changed = set_values(css, values)
    TOKENS.write_text(new)
    PREVIEW.unlink(missing_ok=True)
    print(f"set {kind} {choice}: " + (", ".join(f"--{n}" for n in changed) or "nothing (the app has none of its tokens)"))
    if has_other_schemes(css):
        print("note: tokens.css has a dark scheme; it was not changed")
    return report(tokens(new))


def undo() -> None:
    saved = sorted(HISTORY.glob("tokens-*.css")) if HISTORY.is_dir() else []
    if not saved:
        raise SystemExit("look: nothing to undo")
    shutil.copy2(saved[-1], TOKENS)
    saved[-1].unlink()
    print(f"put back {TOKENS} from before the last set")


def report(t: dict[str, str]) -> int:
    lines = check(t)
    print("\n".join(lines) or "no colour pairs to check")
    return 3 if any(line.startswith("FAIL") for line in lines) else 0


def main(argv: list[str]) -> int:
    if argv[:1] == ["show"]:
        show()
    elif argv[:1] == ["preview"] and len(argv) == 3:
        preview(argv[1], [c.strip() for c in argv[2].split(",") if c.strip()])
    elif argv[:1] == ["set"] and len(argv) == 3:
        return set_(argv[1], argv[2])
    elif argv == ["undo"]:
        undo()
    elif argv == ["check"]:
        return report(tokens(read()))
    else:
        print(__doc__)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
