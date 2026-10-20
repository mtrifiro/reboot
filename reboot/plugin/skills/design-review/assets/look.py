#!/usr/bin/env python3
"""Show, preview, change and undo a Reboot web app's look.

Run from the project root (the folder holding frontend/web/src/styles.css).

    python3 look.py show
        The look now: accent, neutrals, type and corners, and the choices.
    python3 look.py preview accent teal,blue,#0a6e5c
    python3 look.py preview neutrals cool,warm,grey
    python3 look.py preview type house,classic,plain
    python3 look.py preview corners sharp,soft,round
        Writes frontend/web/public/look-preview.html: each choice, lettered
        A, B, C..., drawn as a piece of the app in light and dark. The dev
        server serves it at /look-preview.html.
    python3 look.py set accent teal          (or a brand's hex: #0a6e5c)
    python3 look.py set accent #0a6e5c --dark #5fd0bd
    python3 look.py set neutrals warm
    python3 look.py set type classic
    python3 look.py set corners round
        Changes the tokens in place in the light block and both dark
        blocks (type also rewrites main.tsx's font imports), after saving
        the files it touches. Removes the preview page. Prints the
        contrast check; exits 3 when a pair fails it.
    python3 look.py undo
        Puts back the files as they were before the last `set`.
    python3 look.py check
        The contrast check alone.

Standard library only. The house stylesheet's token names never change;
only their values do.
"""

from __future__ import annotations

import colorsys
import html
import re
import shutil
import sys
import time
from pathlib import Path

WEB = Path("frontend/web")
STYLESHEET = WEB / "src/styles.css"
MAIN = WEB / "src/main.tsx"
FAVICON = WEB / "public/favicon.svg"
PREVIEW = WEB / "public/look-preview.html"
HISTORY = WEB / ".look-history"

# The house palettes, the same as web-app/assets/accent.py.
ACCENTS: dict[str, dict[str, dict[str, str]]] = {
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

# The page, panels, text and lines: cool is the house default.
NEUTRALS: dict[str, dict[str, dict[str, str]]] = {
    "cool": {
        "light": {"bg": "#f4f4f7", "bg-2": "#ffffff", "panel": "#ffffff", "ink": "#1b1d26", "muted": "#5c6070", "line": "#dcdde5", "track": "#e6e6ee"},
        "dark": {"bg": "#14151c", "bg-2": "#1d1f29", "panel": "#1d1f29", "ink": "#ecebf4", "muted": "#a0a3b3", "line": "#2f3140", "track": "#262838"},
    },
    "warm": {
        "light": {"bg": "#f6f3ee", "bg-2": "#fffdf9", "panel": "#fffdf9", "ink": "#24201b", "muted": "#675f55", "line": "#e2dcd2", "track": "#ebe5db"},
        "dark": {"bg": "#181613", "bg-2": "#221f1b", "panel": "#221f1b", "ink": "#f0ebe3", "muted": "#ada597", "line": "#36322c", "track": "#2b2823"},
    },
    "grey": {
        "light": {"bg": "#f5f5f5", "bg-2": "#ffffff", "panel": "#ffffff", "ink": "#1c1c1c", "muted": "#5e5e5e", "line": "#dedede", "track": "#e8e8e8"},
        "dark": {"bg": "#151515", "bg-2": "#1f1f1f", "panel": "#1f1f1f", "ink": "#ededed", "muted": "#a3a3a3", "line": "#313131", "track": "#282828"},
    },
    "white": {
        "light": {"bg": "#ffffff", "bg-2": "#ffffff", "panel": "#ffffff", "ink": "#16171d", "muted": "#5a5d6b", "line": "#e4e5eb", "track": "#ececf1"},
        "dark": {"bg": "#0f1014", "bg-2": "#17181e", "panel": "#17181e", "ink": "#ededf2", "muted": "#9fa2b0", "line": "#2a2c36", "track": "#22232c"},
    },
}

# Type: display, text and mono, each an @fontsource-variable package
# (installed for the app) and a Google Fonts family (for the preview).
TYPE: dict[str, dict[str, tuple[str, str]]] = {
    "house": {"display": ("Bricolage Grotesque", "bricolage-grotesque"), "text": ("Instrument Sans", "instrument-sans"), "mono": ("JetBrains Mono", "jetbrains-mono")},
    "classic": {"display": ("Fraunces", "fraunces"), "text": ("Inter", "inter"), "mono": ("JetBrains Mono", "jetbrains-mono")},
    "plain": {"display": ("Inter", "inter"), "text": ("Inter", "inter"), "mono": ("JetBrains Mono", "jetbrains-mono")},
    "geometric": {"display": ("Space Grotesk", "space-grotesk"), "text": ("DM Sans", "dm-sans"), "mono": ("JetBrains Mono", "jetbrains-mono")},
    "bookish": {"display": ("Newsreader", "newsreader"), "text": ("Source Sans 3", "source-sans-3"), "mono": ("JetBrains Mono", "jetbrains-mono")},
}
TYPE_WORDS = {
    "house": "a characterful grotesque over a clean sans (the house look)",
    "classic": "an editorial serif for headings over Inter",
    "plain": "Inter throughout: quiet, familiar, dense",
    "geometric": "geometric and technical",
    "bookish": "a reading serif for headings over a humanist sans",
}
FALLBACK = {
    "display": 'ui-sans-serif, system-ui, -apple-system, "Segoe UI", sans-serif',
    "text": 'ui-sans-serif, system-ui, -apple-system, "Segoe UI", sans-serif',
    "mono": "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace",
}
SERIF = {"Fraunces", "Newsreader"}

CORNERS = {"sharp": ("2px", "2px"), "soft": ("8px", "6px"), "round": ("14px", "10px")}

# A :root block: its selector and its body, up to the closing brace.
BLOCK = re.compile(r"([^{}]*:root[^{}]*)\{([^{}]*)\}")


def scheme(body: str) -> str | None:
    if "color-scheme: dark" in body:
        return "dark"
    if "color-scheme: light" in body:
        return "light"
    return None


def tokens(css: str) -> dict[str, dict[str, str]]:
    """The token values of the light block and the first dark block."""
    found: dict[str, dict[str, str]] = {}
    for match in BLOCK.finditer(css):
        which = scheme(match.group(2))
        if which and which not in found:
            found[which] = dict(re.findall(r"--([\w-]+):\s*([^;]+);", match.group(2)))
    return found


def set_values(css: str, values: dict[str, dict[str, str]] | dict[str, str]) -> str:
    """Rewrite token values in place: per scheme, or the same in every block."""

    def block(match: re.Match[str]) -> str:
        selector, body = match.group(1), match.group(2)
        which = scheme(body)
        if which is None:
            return match.group(0)
        chosen = values.get(which, {}) if which in values else values
        for token, value in chosen.items():  # type: ignore[union-attr]
            if not isinstance(value, str):
                continue
            body = re.sub(
                r"(--%s:)[^;]*;" % re.escape(token),
                lambda m: m.group(1) + " " + value + ";",
                body,
                count=1,
            )
        return selector + "{" + body + "}"

    return BLOCK.sub(block, css)


# Color arithmetic, for a brand's hex and the contrast check.


def rgb(hex_: str) -> tuple[float, float, float]:
    h = hex_.strip().lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    return tuple(int(h[i : i + 2], 16) / 255 for i in (0, 2, 4))  # type: ignore[return-value]


def to_hex(r: float, g: float, b: float) -> str:
    return "#" + "".join(f"{round(max(0, min(1, c)) * 255):02x}" for c in (r, g, b))


def luminance(hex_: str) -> float:
    def lin(c: float) -> float:
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4

    r, g, b = (lin(c) for c in rgb(hex_))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(a: str, b: str) -> float:
    la, lb = sorted((luminance(a), luminance(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


def hls(hex_: str, light: float | None = None, sat: float | None = None) -> str:
    h, l, s = colorsys.rgb_to_hls(*rgb(hex_))
    return to_hex(*colorsys.hls_to_rgb(h, l if light is None else light, s if sat is None else sat))


def until(hex_: str, against: str, ratio: float, step: float) -> str:
    """Move the lightness of hex_ by step until it reaches ratio against `against`."""
    h, l, s = colorsys.rgb_to_hls(*rgb(hex_))
    while contrast(to_hex(*colorsys.hls_to_rgb(h, l, s)), against) < ratio and 0 < l < 1:
        l = max(0.0, min(1.0, l + step))
    return to_hex(*colorsys.hls_to_rgb(h, l, s))


def brand(light_hex: str, dark_hex: str | None, bg: dict[str, str]) -> dict[str, dict[str, str]]:
    """A whole accent family from a brand's color, in both schemes."""
    _, _, s = colorsys.rgb_to_hls(*rgb(light_hex))
    accent = until(light_hex, bg["light"], 3.0, -0.02)
    on = "#ffffff" if contrast("#ffffff", accent) >= 4.5 else hls(accent, 0.1)
    dark = dark_hex or hls(light_hex, 0.72, min(s, 0.6))
    dark = until(dark, bg["dark"], 4.5, 0.02)
    return {
        "light": {"accent": accent, "on-accent": on, "accent-deep": hls(accent, 0.2, min(s, 0.7)),
                  "on-deep": "#f4f4f7", "accent-tint": hls(accent, 0.93, min(s, 0.6)),
                  "bg-glow": hls(accent, 0.94, 0.15)},
        "dark": {"accent": dark, "on-accent": hls(dark, 0.12), "accent-deep": hls(dark, 0.08, min(s, 0.7)),
                 "on-deep": hls(dark, 0.94, 0.15), "accent-tint": hls(dark, 0.2, 0.35),
                 "bg-glow": hls(dark, 0.11, 0.15)},
    }


def accent_family(name: str, dark_hex: str | None, now: dict[str, dict[str, str]]) -> dict[str, dict[str, str]]:
    if name in ACCENTS:
        return ACCENTS[name]
    if re.fullmatch(r"#?[0-9a-fA-F]{6}|#?[0-9a-fA-F]{3}", name):
        return brand(name if name.startswith("#") else "#" + name, dark_hex,
                     {w: now[w].get("bg", "#ffffff") for w in ("light", "dark")})
    raise SystemExit(f"look: no accent '{name}'; one of {', '.join(ACCENTS)}, or a hex such as #0a6e5c")


def hue_warning(hex_: str) -> str | None:
    h, l, s = colorsys.rgb_to_hls(*rgb(hex_))
    deg = h * 360
    if s < 0.2:
        return None
    for lo, hi, what in ((90, 165, "green"), (30, 60, "amber"), (345, 361, "red"), (0, 15, "red")):
        if lo <= deg < hi:
            return (f"the accent is close to {what}, which the stylesheet keeps for status "
                    f"(--good, --warn, --bad); pills and dots may read as the accent")
    return None


def check(css: str) -> list[str]:
    """Contrast pairs that fail, in each scheme."""
    t = tokens(css)
    failed = []
    pairs = (("ink", "bg", 7.0), ("ink", "panel", 7.0), ("muted", "bg", 4.5), ("muted", "panel", 4.5),
             ("on-accent", "accent", 4.5), ("on-deep", "accent-deep", 4.5), ("accent", "bg", 3.0),
             ("ink", "accent-tint", 4.5))
    for which in ("light", "dark"):
        for a, b, need in pairs:
            va, vb = t.get(which, {}).get(a, ""), t.get(which, {}).get(b, "")
            if not (re.fullmatch(r"#[0-9a-fA-F]{6}", va.strip()) and re.fullmatch(r"#[0-9a-fA-F]{6}", vb.strip())):
                continue
            got = contrast(va.strip(), vb.strip())
            if got < need:
                failed.append(f"{which}: --{a} on --{b} is {got:.1f}:1, needs {need:g}:1")
    return failed


# The preview page: each choice drawn as a piece of the app, its tokens
# set on its own box so the boxes don't affect each other.

SAMPLE = """
<div class="mock" style="{style}">
  <div class="bar"><span class="mark"></span><b>{product}</b><span class="nav">Board</span><span class="nav on">Bookings</span></div>
  <div class="band"><small>Front desk</small><h2>Today's arrivals</h2><p>Every guest arriving today, and the room held for them.</p></div>
  <div class="body">
    <div class="stats"><div class="stat"><small>Arriving</small><strong>12</strong><i style="width:40%"></i></div>
      <div class="stat sel"><small>Checked in</small><strong>5</strong><i style="width:70%"></i></div></div>
    <div class="list">
      <div class="row"><span>Priya Nair</span><em class="pill good">Checked in</em><span class="mono">201</span></div>
      <div class="row sel"><span>Omar Haddad</span><em class="pill">Arriving</em><span class="mono">203</span></div>
      <div class="row"><span>Mei Lin</span><em class="pill warn">Late</em><span class="mono">207</span></div>
    </div>
    <div class="btns"><button class="primary">Check in</button><button class="ghost">Move room</button></div>
  </div>
</div>"""

PAGE = """<!doctype html>
<html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Look choices</title>
{fonts}
<style>
body{{margin:0;padding:24px 16px;font:14px/1.45 ui-sans-serif,system-ui,-apple-system,"Segoe UI",sans-serif;background:#eeeef1;color:#1b1d26}}
@media (prefers-color-scheme: dark){{body{{background:#101116;color:#ecebf4}}}}
h1{{font-size:20px;margin:0 0 4px}} .lede{{margin:0 0 20px;opacity:.75}}
.choice{{margin:0 0 28px}} .choice h3{{font-size:16px;margin:0 0 10px}} .choice h3 b{{display:inline-block;min-width:1.6em}}
.pair{{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:16px}}
.mock{{background:var(--bg);color:var(--ink);border:1px solid var(--line);border-radius:var(--radius);overflow:hidden;font-family:var(--font-text)}}
.bar{{display:flex;gap:14px;align-items:center;padding:10px 14px;background:var(--accent-deep);color:var(--on-deep);font-family:var(--font-display)}}
.mark{{width:14px;height:14px;border-radius:4px;background:var(--accent)}}
.nav{{opacity:.75;font-size:13px}} .nav.on{{opacity:1;background:color-mix(in srgb,var(--on-deep) 14%,transparent);padding:2px 8px;border-radius:var(--radius-sm)}}
.band{{background:var(--accent-deep);color:var(--on-deep);padding:4px 14px 16px}}
.band small{{opacity:.8}} .band h2{{margin:2px 0;font:600 22px/1.2 var(--font-display)}} .band p{{margin:0;opacity:.85;font-size:13px}}
.body{{padding:14px;display:grid;gap:12px}}
.stats{{display:grid;grid-template-columns:1fr 1fr;gap:10px}}
.stat{{background:var(--panel);border:1px solid var(--line);border-radius:var(--radius);padding:8px 10px;display:grid;gap:2px}}
.stat.sel{{border-color:var(--accent);box-shadow:inset 0 0 0 1px var(--accent)}}
.stat small{{color:var(--muted);font-size:12px}} .stat strong{{font:600 22px var(--font-display)}}
.stat i{{display:block;height:4px;border-radius:2px;background:var(--accent)}}
.list{{background:var(--panel);border:1px solid var(--line);border-radius:var(--radius);overflow:hidden}}
.row{{display:grid;grid-template-columns:1fr auto 3em;gap:10px;align-items:center;padding:8px 10px;border-top:1px solid var(--line)}}
.row:first-child{{border-top:0}} .row.sel{{background:var(--accent-tint)}}
.pill{{font-style:normal;font-size:12px;padding:1px 8px;border-radius:999px;border:1px solid var(--line);color:var(--muted)}}
.pill.good{{color:var(--good);border-color:currentColor}} .pill.warn{{color:var(--warn);border-color:currentColor}}
.mono{{font-family:var(--font-mono);font-size:12px;color:var(--muted);text-align:right}}
.btns{{display:flex;gap:8px;flex-wrap:wrap}}
button{{font:600 13px var(--font-text);padding:7px 12px;border-radius:var(--radius-sm);border:1px solid var(--line);cursor:pointer}}
button.primary{{background:var(--accent);color:var(--on-accent);border-color:var(--accent)}}
button.ghost{{background:transparent;color:var(--ink)}}
.scheme{{font-size:12px;opacity:.7;margin:0 0 4px}}
</style></head><body>
<h1>{title}</h1><p class="lede">Each choice in light and dark. Say which letter, or ask for something else.</p>
{choices}
</body></html>"""


def style_of(values: dict[str, str]) -> str:
    return ";".join(f"--{k}:{html.escape(v.strip(), quote=True)}" for k, v in values.items())


def product_name() -> str:
    index = WEB / "index.html"
    if index.is_file():
        found = re.search(r"<title>([^<]+)</title>", index.read_text(encoding="utf-8"))
        if found:
            return html.escape(found.group(1).strip())
    return "Your app"


def type_values(name: str) -> dict[str, str]:
    t = TYPE[name]
    out = {}
    for role in ("display", "text", "mono"):
        family = t[role][0]
        fallback = 'ui-serif, Georgia, serif' if family in SERIF else FALLBACK[role]
        out[f"font-{role}"] = f'"{family} Variable", "{family}", {fallback}'
    return out


def preview(kind: str, names: list[str]) -> None:
    css = STYLESHEET.read_text(encoding="utf-8")
    now = tokens(css)
    letters = "ABCDEFGH"
    product = product_name()
    families: set[str] = set()
    blocks = []
    for i, name in enumerate(names[: len(letters)]):
        light, dark = dict(now["light"]), dict(now["light"])
        dark.update(now.get("dark", {}))
        label = name
        if kind == "accent":
            fam = accent_family(name, None, now)
            light.update(fam["light"]), dark.update(fam["dark"])
        elif kind == "neutrals":
            if name not in NEUTRALS:
                raise SystemExit(f"look: no neutrals '{name}'; one of {', '.join(NEUTRALS)}")
            light.update(NEUTRALS[name]["light"]), dark.update(NEUTRALS[name]["dark"])
        elif kind == "type":
            if name not in TYPE:
                raise SystemExit(f"look: no type '{name}'; one of {', '.join(TYPE)}")
            light.update(type_values(name)), dark.update(type_values(name))
            families.update(f for f, _ in TYPE[name].values())
            label = f"{name}: {TYPE_WORDS[name]}"
        elif kind == "corners":
            if name not in CORNERS:
                raise SystemExit(f"look: no corners '{name}'; one of {', '.join(CORNERS)}")
            r, rs = CORNERS[name]
            light.update({"radius": r, "radius-sm": rs}), dark.update({"radius": r, "radius-sm": rs})
        else:
            raise SystemExit("look: preview accent | neutrals | type | corners")
        mocks = "".join(
            f'<div><p class="scheme">{w}</p>{SAMPLE.format(style=style_of(v), product=product)}</div>'
            for w, v in (("Light", light), ("Dark", dark))
        )
        blocks.append(f'<section class="choice"><h3><b>{letters[i]}</b>{html.escape(label)}</h3><div class="pair">{mocks}</div></section>')
    fonts = ""
    if kind == "type" and families:
        q = "&".join("family=" + f.replace(" ", "+") + ":wght@400;600" for f in sorted(families))
        fonts = f'<link rel="stylesheet" href="https://fonts.googleapis.com/css2?{q}&display=swap">'
    titles = {"accent": "Accent color", "neutrals": "Page and text tones", "type": "Typefaces", "corners": "Corners"}
    PREVIEW.parent.mkdir(parents=True, exist_ok=True)
    PREVIEW.write_text(PAGE.format(fonts=fonts, title=titles[kind], choices="".join(blocks)), encoding="utf-8")
    print(f"wrote {PREVIEW}: " + ", ".join(f"{letters[i]} {n}" for i, n in enumerate(names[: len(letters)])))


def save(paths: list[Path]) -> Path:
    slot = HISTORY / time.strftime("%Y%m%d-%H%M%S")
    n = 1
    while slot.exists():
        slot = slot.with_name(slot.name.split("~")[0] + f"~{n}")
        n += 1
    slot.mkdir(parents=True)
    for p in paths:
        if p.is_file():
            dest = slot / p.relative_to(WEB)
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(p, dest)
    return slot


def undo() -> int:
    slots = sorted(HISTORY.glob("*")) if HISTORY.is_dir() else []
    if not slots:
        print("look: nothing to undo")
        return 2
    slot = slots[-1]
    for f in slot.rglob("*"):
        if f.is_file():
            shutil.copy2(f, WEB / f.relative_to(slot))
    shutil.rmtree(slot)
    print(f"put back the look from before the last change ({len(slots) - 1} earlier change(s) can still be undone)")
    return 0


def set_type(name: str, css: str) -> str:
    if name not in TYPE:
        raise SystemExit(f"look: no type '{name}'; one of {', '.join(TYPE)}")
    css = set_values_root_only(css, type_values(name))
    if MAIN.is_file():
        main = MAIN.read_text(encoding="utf-8")
        main = re.sub(r'^import "@fontsource(?:-variable)?/[^"]+";\n', "", main, flags=re.M)
        packages = sorted({pkg for _, pkg in TYPE[name].values()})
        main = "".join(f'import "@fontsource-variable/{p}";\n' for p in packages) + main
        MAIN.write_text(main, encoding="utf-8")
        print("install: npm install " + " ".join(f"@fontsource-variable/{p}" for p in packages)
              + "   (in frontend/)")
    return css


def set_values_root_only(css: str, values: dict[str, str]) -> str:
    """Fonts and corners live in the light :root block only."""
    def block(match: re.Match[str]) -> str:
        selector, body = match.group(1), match.group(2)
        if scheme(body) != "light":
            return match.group(0)
        for token, value in values.items():
            body = re.sub(r"(--%s:)[^;]*;" % re.escape(token), lambda m: m.group(1) + " " + value + ";", body, count=1)
        return selector + "{" + body + "}"

    return BLOCK.sub(block, css)


def show() -> int:
    css = STYLESHEET.read_text(encoding="utf-8")
    t = tokens(css)
    light = t.get("light", {})
    accent = light.get("accent", "?").strip()
    named = next((n for n, p in ACCENTS.items() if p["light"]["accent"] == accent), None)
    neutral = next((n for n, p in NEUTRALS.items() if p["light"]["bg"] == light.get("bg", "").strip()), None)
    font = re.match(r'\s*"([^"]+?)(?: Variable)?"', light.get("font-display", ""))
    kind = next((n for n, p in TYPE.items() if font and p["display"][0] == font.group(1)
                 and re.match(r'\s*"([^"]+?)(?: Variable)?"', light.get("font-text", "")).group(1) == p["text"][0]), None)
    radius = light.get("radius", "").strip()
    corners = next((n for n, (r, _) in CORNERS.items() if r == radius), None)
    print(f"accent    {named or 'custom'} ({accent})        choices: {', '.join(ACCENTS)}, or a brand's hex")
    print(f"neutrals  {neutral or 'custom'}                    choices: {', '.join(NEUTRALS)}")
    print(f"type      {kind or 'custom'} ({font.group(1) if font else '?'})   choices: {', '.join(TYPE)}")
    print(f"corners   {corners or 'custom'} ({radius})            choices: {', '.join(CORNERS)}")
    undoable = len(list(HISTORY.glob('*'))) if HISTORY.is_dir() else 0
    print(f"undo      {undoable} change(s) can be undone")
    return 0


def main(argv: list[str]) -> int:
    if not STYLESHEET.is_file():
        print(f"look: no {STYLESHEET}; run from the project root of a web app built in the house look", file=sys.stderr)
        return 2
    if not argv or argv[0] == "show":
        return show()
    if argv[0] == "undo":
        return undo()
    if argv[0] == "check":
        failed = check(STYLESHEET.read_text(encoding="utf-8"))
        print("\n".join(failed) if failed else "contrast: every pair passes in light and dark")
        return 3 if failed else 0
    if argv[0] == "preview" and len(argv) >= 3:
        preview(argv[1], [n for n in argv[2].split(",") if n])
        return 0
    if argv[0] != "set" or len(argv) < 3:
        print(__doc__)
        return 2
    kind, name = argv[1], argv[2]
    dark_hex = argv[argv.index("--dark") + 1] if "--dark" in argv else None
    css = STYLESHEET.read_text(encoding="utf-8")
    now = tokens(css)
    slot = save([STYLESHEET, MAIN, FAVICON])
    if kind == "accent":
        fam = accent_family(name, dark_hex, now)
        old = now["light"].get("accent", "").strip().lower()
        css = set_values(css, fam)
        if FAVICON.is_file() and old:
            svg = FAVICON.read_text(encoding="utf-8")
            FAVICON.write_text(re.sub(re.escape(old), fam["light"]["accent"], svg, flags=re.I), encoding="utf-8")
        warn = hue_warning(fam["light"]["accent"])
        if warn:
            print("note: " + warn)
    elif kind == "neutrals":
        if name not in NEUTRALS:
            raise SystemExit(f"look: no neutrals '{name}'; one of {', '.join(NEUTRALS)}")
        css = set_values(css, NEUTRALS[name])
    elif kind == "type":
        css = set_type(name, css)
    elif kind == "corners":
        if name not in CORNERS:
            raise SystemExit(f"look: no corners '{name}'; one of {', '.join(CORNERS)}")
        r, rs = CORNERS[name]
        css = set_values_root_only(css, {"radius": r, "radius-sm": rs})
    else:
        shutil.rmtree(slot)
        print("look: set accent | neutrals | type | corners")
        return 2
    STYLESHEET.write_text(css, encoding="utf-8")
    if PREVIEW.is_file():
        PREVIEW.unlink()
    print(f"set {kind} to {name}; saved the files before it (python3 look.py undo puts them back)")
    failed = check(css)
    print("\n".join(failed) if failed else "contrast: every pair passes in light and dark")
    return 3 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
