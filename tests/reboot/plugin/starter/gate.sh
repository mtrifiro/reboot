#!/usr/bin/env bash
#
# The starter's gate: render it with sample names into a temporary
# folder and prove it green on the Reboot the skills pin.
#
#   tests/reboot/plugin/starter/gate.sh            the backend: uv sync, rbt generate, mypy, pytest
#   tests/reboot/plugin/starter/gate.sh --web      and the frontend: npm install, rbt generate,
#                                                  npm run build, the browser scenarios
#
# `REBOOT_PLUGIN_SKILLS` names the skills dir to render from (default:
# this checkout's). `REBOOT_DIST` names a reboot-main dist folder (the
# wheel and the three npm tarballs); when set, the rendered project's
# pins are pointed at it the way compose.py does, so the gate runs on
# the same build the test package installs. `KEEP=1` leaves the folder
# behind and prints its path.

set -euo pipefail
HERE="$(cd "$(dirname -- "$0")" && pwd)"
SKILLS="${REBOOT_PLUGIN_SKILLS:-$(cd "$HERE/../../../../reboot/plugin/skills" && pwd)}"
web=""
[ "${1:-}" = "--web" ] && web="--web"

DEST="$(mktemp -d "${TMPDIR:-/tmp}/reboot-starter.XXXXXX")"
if [ -z "${KEEP:-}" ]; then trap 'rm -rf "$DEST"' EXIT; fi
echo "starter: rendering to $DEST (skills: $SKILLS)"
python3 "$SKILLS/python/assets/render.py" --app "Corner Shop" --pkg shop --hub Shop --thing Product $web "$DEST"

if [ -n "${REBOOT_DIST:-}" ]; then
  whl=$(ls "$REBOOT_DIST"/reboot-*.whl)
  api=$(ls "$REBOOT_DIST"/reboot-dev-reboot-api-*.tgz)
  react=$(ls "$REBOOT_DIST"/reboot-dev-reboot-react-*.tgz)
  rweb=$(ls "$REBOOT_DIST"/reboot-dev-reboot-web-*.tgz)
  python3 - "$DEST" "$whl" "$api" "$react" "$rweb" <<'EOF'
import re, sys
from pathlib import Path
dest, whl, api, react, web = sys.argv[1:]
p = Path(dest) / "pyproject.toml"
p.write_text(re.sub(r'reboot(\[[a-z]+\])?==\d+\.\d+\.\d+', lambda m: f'reboot{m.group(1) or ""} @ file://{whl}', p.read_text()))
j = Path(dest) / "frontend" / "package.json"
if j.exists():
    s = j.read_text()
    for name, path in (("api", api), ("react", react), ("web", web)):
        s = re.sub(rf'"@reboot-dev/reboot-{name}":\s*"[^"]*"', f'"@reboot-dev/reboot-{name}": "file:{path}"', s)
    j.write_text(s)
EOF
fi

cd "$DEST"
step() { echo; echo "starter: $*"; "$@"; }
step uv sync
step uv run rbt generate
step uv run mypy backend/ tests/
step uv run pytest tests/shop_test.py -q
if [ -n "$web" ]; then
  (cd frontend && step npm install --no-audit --no-fund)
  step uv run rbt generate
  (cd frontend && step npm run build)
  step uv run playwright install chromium
  step uv run pytest tests/web_test.py -q
fi
echo
echo "starter: green${web:+ (backend and web)}"
[ -z "${KEEP:-}" ] || echo "starter: kept at $DEST"
