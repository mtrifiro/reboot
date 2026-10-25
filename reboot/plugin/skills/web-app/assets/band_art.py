#!/usr/bin/env python3
"""The band's art as SVG markup, the same pattern the app draws.

    python3 '<the web-app skill>/assets/band_art.py' 'Rack Rate'

Prints the <svg class="band-art"> for an app's name: quarter circles,
half circles, dots and bars on a 40 px grid, laid out from the name.
The starter's patterns/BandArt.tsx draws the same shapes from the same
name (the same hash and the same random numbers), so the comp's band
(comp.py puts this in it) is the app's: change one, change both. The
tones are classes (t1..t5) the stylesheet colours from the band and the
accent. Standard library only.
"""

from __future__ import annotations

import sys

CELL, COLS, ROWS = 40, 18, 6
KINDS = ("q0", "q1", "q2", "q3", "h0", "h1", "h2", "h3", "dot", "circle", "square", "bar")
M32 = 0xFFFFFFFF


def seed_of(name: str) -> int:
    h = 2166136261
    for ch in name:
        h = ((h ^ ord(ch)) * 16777619) & M32
    return h


def random(seed: int):
    """mulberry32, as BandArt.tsx has it, on unsigned 32-bit values."""
    state = [seed & M32]

    def imul(a: int, b: int) -> int:
        return (a * b) & M32

    def nxt() -> float:
        state[0] = (state[0] + 0x6D2B79F5) & M32
        a = state[0]
        t = imul(a ^ (a >> 15), 1 | a)
        t = ((t + imul(t ^ (t >> 7), 61 | t)) & M32) ^ t
        return ((t ^ (t >> 14)) & M32) / 4294967296

    return nxt


def shapes(name: str) -> list[tuple[str, int, int, int]]:
    nxt = random(seed_of(name))
    taken: set[int] = set()
    out = []
    for r in range(ROWS):
        for c in range(COLS):
            if r * COLS + c in taken or c < 5:
                continue
            under_buttons = r >= 3 and c >= 8
            p = (0.12 + 0.43 * (c - 5) / 12) * (0.35 if under_buttons else 1)
            if nxt() >= p:
                continue
            kind = KINDS[int(nxt() * len(KINDS))]
            tone = (1 if nxt() < 0.5 else 5) if under_buttons else 1 + int(nxt() * 5)
            if kind == "bar":
                if c + 1 < COLS and r * COLS + c + 1 not in taken:
                    taken.add(r * COLS + c + 1)
                else:
                    kind = "square"
            taken.add(r * COLS + c)
            out.append((kind, c * CELL, r * CELL, tone))
    return out


def element(kind: str, x: int, y: int, tone: int) -> str:
    s, h, cls = CELL, CELL // 2, f't{tone}'
    d = {
        "q0": f"M{x} {y}h{s}a{s} {s} 0 0 1 -{s} {s}z",
        "q1": f"M{x + s} {y}v{s}a{s} {s} 0 0 1 -{s} -{s}z",
        "q2": f"M{x + s} {y + s}h-{s}a{s} {s} 0 0 1 {s} -{s}z",
        "q3": f"M{x} {y + s}v-{s}a{s} {s} 0 0 1 {s} {s}z",
        "h0": f"M{x} {y + s}a{h} {h} 0 0 1 {s} 0z",
        "h1": f"M{x} {y}a{h} {h} 0 0 0 {s} 0z",
        "h2": f"M{x} {y}a{h} {h} 0 0 1 0 {s}z",
        "h3": f"M{x + s} {y}a{h} {h} 0 0 0 0 {s}z",
    }
    if kind == "dot":
        return f'<circle class="{cls}" cx="{x + h}" cy="{y + h}" r="8"/>'
    if kind == "circle":
        return f'<circle class="{cls}" cx="{x + h}" cy="{y + h}" r="{h}"/>'
    if kind == "square":
        return f'<rect class="{cls}" x="{x}" y="{y}" width="{s}" height="{s}"/>'
    if kind == "bar":
        return f'<rect class="{cls}" x="{x}" y="{y}" width="{2 * s}" height="{s}"/>'
    return f'<path class="{cls}" d="{d[kind]}"/>'


def svg(name: str) -> str:
    body = "".join(element(*shape) for shape in shapes(name))
    return (f'<svg class="band-art" aria-hidden="true" viewBox="0 0 {CELL * COLS} {CELL * ROWS}" '
            f'preserveAspectRatio="xMaxYMin slice">{body}</svg>')


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(__doc__.strip().splitlines()[2].strip(), file=sys.stderr)
        sys.exit(2)
    print(svg(sys.argv[1]))
