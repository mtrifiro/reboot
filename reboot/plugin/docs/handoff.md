# Handoff: reboot-next, 2026-10-12 morning

Written before a switch of Claude login so the next session can pick up
exactly here. Read this, then `~/projects/reboot-next/reboot/plugin/docs/next-plan.md`
and `next-items.yaml` (the record the Plugin Browser's Next page shows).

## The project in one paragraph

The Reboot plugin is being rebuilt from upstream (reboot-dev/reboot `main`,
`reboot/plugin/`, after reboot#186) with what the fork (`~/projects/reboot-plugin`,
branch `ia-restructure`) learned ported underneath, in layers L0 to L6, each
judged by a hotel build against a baseline. Tracked in the Plugin Browser at
http://localhost:9600/__/frontend/web/#/next (repo `~/projects/plugin-browser`,
ports 9600/4600).

## Where everything is

| What | Where |
|---|---|
| next (integration branch) | `~/projects/reboot-next`, a worktree of `~/projects/reboot`, branch `next`, sparse: `reboot/plugin`, `tests/reboot/plugin` |
| Plan and record | `~/projects/reboot-next/reboot/plugin/docs/next-plan.md`, `next-items.yaml` |
| Branches for upstream PRs (all in `~/projects/reboot`, none pushed) | `agents-md` (39b31ed6), `next-l0-budget` (8879b7f4), `next-l0-build-metrics` (6d1f3dd2) |
| Their worktrees (session scratch, may vanish; branches are safe in git) | scratchpad `wt-agents`, `wt-budget`, `wt-metrics` under `/private/tmp/claude-501/-Users-mtrifiro-projects-reboot-plugin/4e404610-.../scratchpad/` |
| PR description draft for agents-md | `~/projects/next-work/pr-drafts/agents-md.md` (results section still a placeholder) |
| AGENTS.md experiment: scripts, partial results | `~/projects/next-work/experiment/` |
| Experiment working copies and live runs | scratchpad `exp/` (A1, B1, CA1, CB1, ...) and `codex-home/` |
| Claude Code install of next | `~/projects/next-test` (enables `reboot@reboot-next` only) |
| Claude app upload of main's plugin | `~/Downloads/reboot-next-main.plugin` |

## Done this session (2026-10-11 to 12)

- Decided to rebuild from upstream instead of the fork; the fork is the source to port from.
- Found the plugin's real source is `reboot/plugin/` in reboot-dev/reboot; reboot#186 already fixed authorizers and `allowed_origins` (L1 items skipped).
- Plugin Browser: a Next page (record, layers, builds against the baseline, three-way file compare, About with strategy, Where it stands), moved to ports 9600/4600.
- **hotel-7** (main's plugin, Claude app) is the new baseline: 4 questions, design 47 s, API 6m30s, first passing scenario 14m26s, 33 scenarios, 34,671 words before the API. hotel-6 (1.6.0): 3, 49 s, 5m31s, 10m03s, 39, 46,179. The fourth question is the production sign-in provider (L1 item `provider-at-deploy`, noted).
- **L0 rebuilt the upstream way** after a senior-engineer review: Bazel `py_test`s under `tests/reboot/plugin/`, nothing shipped in the plugin.
  - `reading_budget`: every reading-list reference exists; conditional entries named with their words; ceilings web-app 39,000 (37,248 today), mcp-ui 52,000 (49,907). 9 tests.
  - `build_metrics`: reads Claude Code and Codex transcripts (adapters to one event stream), `check_transcript` binary, 17 tests.
  - Both merged into next; the old `reboot/plugin/tools/` commit reverted.
- **agents-md** (Ben's request): new skill plus calls from web-app, mcp-ui (step 1 and Update Flow) and run; marketplace and README. Tested on hotel-6 copies (fresh, and folding an existing CLAUDE.md). Merged into next. No conflicts with open PRs #192, #220, #223, #225 (checked line ranges).
- Bazelisk installed (Bazel 8.7.0 pinned by the repo); the new Bazel targets have NOT been run under Bazel yet.

## In flight when this was written

**AGENTS.md experiment** (does the map save time on a follow-up task?). Task in
`experiment/prompt.txt`: add an out-of-order reason to hotel-6, with a scenario,
done when backend scenarios and mypy pass. A = copy with AGENTS.md, B = without.

- A1 (Claude Code, with map): first edit 53 s after 8 calls; hit its 50 min limit with its test run hung. Rerun by hand afterwards: its new scenarios pass, mypy clean (full suite result: see the scratch task `bz9dg5zc1` output, or rerun `uv run pytest tests/hotel_test.py` in `exp/A1`).
- B1 first try (without): killed by A1's `pkill -f "pytest tests/hotel_test.py"` (side-by-side runs could reach each other; now sequential). First edit 57 s after 9 calls.
- B1 rerun (without): running when written; early numbers first edit 96 s after 19 calls.
- Then Codex CA1, CB1, queued, in `codex-home` (CODEX_HOME), using the ChatGPT app's codex binary `/Applications/ChatGPT.app/Contents/Resources/codex-cli/bin/codex` (the npm CLI 0.146 can't use the account's models). The user's `~/.codex` is untouched.
- Hangs: an untouched hotel-6 copy runs 10 scenarios in 28 s, so hangs came from running suites at once, not the machine.
- Measure: `python3 ~/projects/next-work/experiment/measure2.py A1 B1 CA1 CB1` (reads next's `build_metrics`).
- If the runs died with the login switch: rerun B1, then CA1 and CB1, one at a time, with `run-seq.sh` / `run-codex.sh` (paths inside point at the scratch `exp/`; recreate copies from `~/projects/hotel-6` the same way if scratch is gone: rsync without node_modules, .venv, .rbt, .git; A copies get the AGENTS.md and CLAUDE.md from `exp/A1`).

## Next steps, in order

1. Finish the experiment (B1, CA1, CB1), fill the results into `pr-drafts/agents-md.md`, show the user, then (on their go) push `agents-md` to the fork `mtrifiro/reboot` and open the PR to reboot-dev/reboot.
2. Run the two L0 Bazel targets: `bazel test //tests/reboot/plugin/reading_budget:reading_budget_test //tests/reboot/plugin/build_metrics:build_metrics_test` (first run fetches Bazel and the toolchain; stop and report if it pulls in very large toolchains).
3. Port the evals (L0's last item), then open the two L0 PRs, budget first, each on its own.
4. L1: `oauth-import`, `reserved-names`, `api-facts`, `provider-at-deploy`, `vite-pins`.

## Rules the user set this session

- Commit or push only when asked; nothing is pushed. Opening a PR is outward-facing: ask first.
- Ben (Reboot) asked for the AGENTS.md PR; the user wants all evidence in the PR or its comments.
- The Plugin Browser runs on 9600/4600 so hotel builds keep 9991/4444; a change that adds an API field restarts it (wait until it serves before saying done); removing a response field stops `rbt dev run`.

## Update 2026-10-12 ~10:30: tests hang on this Mac; restart before resuming

- B1 (without map) finished at its 50 min limit, stuck in the test run like A1. Before-the-tests numbers stand: A1 53 s / 8 calls to first edit, B1 96 s / 19 calls. Total time and pass counts are not usable from A1/B1.
- An untouched hotel-6 copy (scratch `exp/D`) hangs too, even 2 scenarios (`-k "massage_during or date_outside"`), with every Reboot app, proxy and Docker container stopped. Stack dump: the step waits on the scenario's Reboot server; its envoy was seen at 100–180% CPU. Memory was swapping heavily (~5.8M swapouts). Earlier the same day 10 scenarios ran in 28 s.
- The user was asked to restart the Mac. After it: recreate the copies (scratch is gone), check 2 scenarios pass in under a minute, then run A1/B1 suites for pass counts (or rerun the arms) and the Codex pair with run-codex.sh (CA1 had started and was stopped at 10 s; no edits).
- The Codex queue was stopped on purpose; nothing is running.
- Plugin Browser, hotel-7 and findings-board servers were stopped (hotel-7's restarted from Claude-app run tabs until the user stopped them there). Restart the Plugin Browser with `uv run rbt dev run` + `npm run dev` in `~/projects/plugin-browser` (ports 9600/4600).
- A finding was written to `~/projects/hotel-7/FINDINGS.md` (new file): the `.rbtrc` reference doesn't say `rbt dev run` restarts on API changes via `--generate-watch`. hotel-7 is not yet in the plugin corpus's `sources.md`.
