#!/usr/bin/env bash
# Rebuild skills/quickstart/assets/hotel/ from a commit of the hotel app's
# own repository, so the quickstart always ships a named, tested commit.
#
#   dev/sync-quickstart-hotel.sh <hotel repo> [<commit>]   (default HEAD)
#
# Copies the commit's files (not the working tree), less what the
# quickstart copies from the app skill at setup (scripts/, tests/last_run.py)
# and the project's own AGENTS.md. Copies the browser recordings from the
# repo's last test run only if that run was full, clean and passing on the
# same code as the commit (api/, backend/, frontend/, tests/); otherwise it
# stops and says to run `scripts/test.sh full` first. Writes the source
# commit to assets/hotel/SOURCE.
set -euo pipefail

repo=$(cd "${1:?usage: $0 <hotel repo> [<commit>]}" && pwd)
commit=$(git -C "$repo" rev-parse --short "${2:-HEAD}")
here=$(cd "$(dirname "$0")/.." && pwd)
dest="$here/skills/quickstart/assets/hotel"

run="$repo/tests/.last-run.json"
[ -f "$run" ] || { echo "sync: no test run in $repo; run scripts/test.sh full at $commit" >&2; exit 1; }
read -r full dirty passed failed revision < <(python3 - "$run" <<'PY'
import json, sys
r = json.load(open(sys.argv[1]))
print(r.get("full"), r.get("dirty"), r.get("passed", 0), r.get("failed", 0), r.get("revision", ""))
PY
)
if [ "$full" != True ] || [ "$dirty" != False ] || [ "$failed" != 0 ]; then
  echo "sync: the last run wasn't a full, clean, passing run; run scripts/test.sh full at $commit" >&2
  exit 1
fi
# The run must have covered every scenario in the commit, not a subset.
expected=$(git -C "$repo" ls-tree -r --name-only "$commit" tests \
  | grep '\.feature$' \
  | while read -r f; do git -C "$repo" show "$commit:$f"; done \
  | grep -cE '^[[:space:]]*Scenario( Outline)?:' || true)
counted=$(python3 -c "import json,sys; r=json.load(open(sys.argv[1])); print(sum(r.get(k,0) for k in ('passed','failed','wip','blocked','skipped')))" "$run")
if [ "$counted" -lt "$expected" ]; then
  echo "sync: the last run counted $counted scenarios; $commit has $expected; run scripts/test.sh full at $commit" >&2
  exit 1
fi
for path in api backend frontend tests; do
  if [ "$(git -C "$repo" rev-parse "$revision:$path")" != "$(git -C "$repo" rev-parse "$commit:$path")" ]; then
    echo "sync: the last run ($revision) tested different $path/ than $commit; run scripts/test.sh full at $commit" >&2
    exit 1
  fi
done

tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
git -C "$repo" archive "$commit" | tar -x -C "$tmp"
rm -rf "$tmp/scripts" "$tmp/tests/last_run.py" "$tmp/AGENTS.md" "$tmp/.env"
cp -R "$repo"/tests/*.recordings "$tmp/tests/" 2>/dev/null || true

rm -rf "$dest"
mkdir -p "$dest"
cp -R "$tmp/." "$dest/"
name=$(basename "$(dirname "$(cd "$repo" && cd "$(git rev-parse --git-common-dir)" && pwd)")")
branch=$(git -C "$repo" branch --contains "$commit" --format='%(refname:short)' | head -1)
printf '%s %s (%s)\n' "$name" "$commit" "$branch" > "$dest/SOURCE"
echo "sync: assets/hotel/ is $(cat "$dest/SOURCE") ($passed scenarios passed at $revision); $(find "$dest" -name '*.webm' | wc -l | tr -d ' ') videos"
