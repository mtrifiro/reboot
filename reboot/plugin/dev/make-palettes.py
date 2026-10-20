#!/usr/bin/env python3
"""Regenerate skills/web-app/assets/palettes.json from Radix Colors.

    npm pack @radix-ui/colors@3.0.0 && tar xzf radix-ui-colors-3.0.0.tgz
    python3 dev/make-palettes.py package > skills/web-app/assets/palettes.json

Radix Colors (https://github.com/radix-ui/colors) is MIT licensed; its
notice is kept beside the output in skills/web-app/assets/palettes.LICENSE.
Each palette is a gray and an accent. Light: the page is gray-2, panels
gray-1, text gray-12, muted gray-11, lines gray-6; the
accent is the first of steps 9-12 that reads on the page (3:1) with
white on it (4.5:1). Dark: the page is gray-1, panels gray-3 and the
track gray-5, so a panel stands off the page by its surface and a
hairline, not a shadow; the accent
is the first of steps 11, 10, 9 with gray-1 on it. The page head's band
is calm: accent-4 mixed halfway with gray-6, accent-12 text (dark:
accent-2, accent-12 text); "deep" keeps the dark band (gray-12, gray-1
text; dark: gray-4), set with `look.py set band deep`.
Tints are the accent's step 3 (light) and 4 (dark). The top bar is
solid whatever the band: the deep values (gray-12 with gray-1 text;
dark gray-4 with gray-12).
"""
import json, re, sys
from pathlib import Path

RADIX = Path(sys.argv[1])
PAIRS = [("sand", "bronze"), ("sand", "brown"), ("sand", "orange"), ("sand", "gold"),
         ("olive", "grass"), ("sage", "teal"), ("slate", "blue"), ("slate", "iris"),
         ("mauve", "plum"), ("mauve", "crimson")]

def scale(name, dark):
    text = (RADIX / f"{name}{'-dark' if dark else ''}.css").read_text().split("@supports")[0]
    return {int(k): v for k, v in re.findall(rf"--{name}-(\d+):\s*(#[0-9a-f]{{6}})", text)}

def lum(h):
    def lin(c):
        c /= 255
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = (int(h[i:i + 2], 16) for i in (1, 3, 5))
    return 0.2126 * lin(r) + 0.7152 * lin(g) + 0.0722 * lin(b)

def contrast(a, b):
    x, y = sorted((lum(a), lum(b)), reverse=True)
    return (x + 0.05) / (y + 0.05)

def pick(a, g, bg, order):
    for step, on in order:
        on_hex = {"white": "#ffffff", "g1": g[1], "g12": g[12]}[on]
        if contrast(a[step], bg) >= 3.0 and contrast(on_hex, a[step]) >= 4.5:
            return a[step], on_hex, step
    raise SystemExit(f"no accent step passes")

def mix(a, b, t):
    """a moved t of the way to b, channel by channel."""
    x = [int(a[i:i + 2], 16) for i in (1, 3, 5)]
    y = [int(b[i:i + 2], 16) for i in (1, 3, 5)]
    return "#" + "".join(f"{round(p * (1 - t) + q * t):02x}" for p, q in zip(x, y))

out = {}
for gray, acc in PAIRS:
    fam, steps, deep = {}, [], {}
    for dark in (False, True):
        g, a = scale(gray, dark), scale(acc, dark)
        if not dark:
            bg = g[2]
            accent, on, step = pick(a, g, bg, [(9, "white"), (10, "white"), (11, "white"), (12, "white"), (9, "g12")])
            vals = {"bg": g[2], "bg-2": g[1], "panel": g[1], "ink": g[12], "muted": g[11], "line": g[6], "track": g[4],
                    "accent": accent, "on-accent": on, "accent-deep": mix(a[4], g[6], 0.5), "on-deep": a[12],
                    "accent-tint": a[3], "bg-glow": a[2]}
            deep["light"] = {"accent-deep": g[12], "on-deep": g[1]}
            vals.update({"bar": g[12], "on-bar": g[1]})
        else:
            bg = g[1]
            accent, on, step = pick(a, g, bg, [(11, "g1"), (10, "g1"), (9, "g1"), (9, "white")])
            vals = {"bg": g[1], "bg-2": g[2], "panel": g[3], "ink": g[12], "muted": g[11], "line": g[6], "track": g[5],
                    "accent": accent, "on-accent": on, "accent-deep": a[2], "on-deep": a[12],
                    "accent-tint": a[4], "bg-glow": a[2]}
            deep["dark"] = {"accent-deep": g[4], "on-deep": g[12]}
            vals.update({"bar": g[4], "on-bar": g[12]})
        fam["dark" if dark else "light"] = vals
        steps.append(f"{acc}-{step}")
    out[f"{gray}-{acc}"] = {"source": f"Radix Colors {gray} with {steps[0]} (light), {steps[1]} (dark)", **fam,
                            "deep": deep}
json.dump(out, sys.stdout, indent=1)
print()
