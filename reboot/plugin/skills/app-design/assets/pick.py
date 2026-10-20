#!/usr/bin/env python3
"""One of several choices, the same for a project folder every time and
different across folders, so two builds of one prompt differ.

    python3 <this file> name Larkspur Quayside "The Ledger Room" Bellhop Fenwick

The first argument says what is picked (`name`), so the pick for a name
and for anything else in the same folder don't move together. Prints the
choice. Run from the project root. Standard library only.
"""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path


def pick(what: str, choices: list[str], folder: str) -> str:
    digest = hashlib.sha256(f"{what}:{folder}".encode()).hexdigest()
    return choices[int(digest, 16) % len(choices)]


def main(argv: list[str]) -> int:
    if len(argv) < 3:
        print("pick: give what is picked and two or more choices: pick.py name A B C", file=sys.stderr)
        return 2
    print(pick(argv[0], argv[1:], Path.cwd().name))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
