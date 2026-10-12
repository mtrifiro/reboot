#!/bin/sh
# The plugin's checks, the same locally as in CI: the reading budget
# under its ceilings, the hooks' manifests well formed, the shell
# scripts clean under shellcheck, the Python tools compiling.
#
#   tools/check.sh
set -eu
cd "$(dirname -- "$0")/.."
fail=0

echo "== reading budget"
python3 tools/budget.py --check >/dev/null || fail=1

echo "== manifests"
for f in hooks/hooks.json .claude-plugin/marketplace.json; do
    python3 -m json.tool "$f" >/dev/null || { echo "FAIL: $f is not valid JSON"; fail=1; }
done

echo "== shell"
if command -v shellcheck >/dev/null 2>&1; then
    shellcheck -S warning hooks-handlers/*.sh tools/*.sh || fail=1
else
    echo "shellcheck not installed; skipped (brew install shellcheck)"
fi

echo "== python"
for f in tools/*.py; do python3 -c "import ast, sys; ast.parse(open(sys.argv[1]).read(), sys.argv[1])" "$f" || fail=1; done

[ "$fail" -eq 0 ] && echo "all checks passed"
exit "$fail"
