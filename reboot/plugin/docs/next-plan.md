# Reboot plugin, next

The plan for a new plugin experience: 1.6.0's shape, with what the
`ia-restructure` fork learned added underneath it.

## Why

The fork (`~/projects/reboot-plugin`, branch `ia-restructure`, 248 commits
on 1.6.0) made the plugin more correct, but the experience got slower and
heavier. A side-by-side run of 1.6.0 (hotel-6, below) showed what was lost:

- **Speed.** The whole design arrived 47 seconds after the last answer.
  The API was written 5 minutes later, and the first scenario passed
  10 minutes later.
- **The level of information in the design.** One plain-language message
  covered who uses the app, what it keeps track of and why each is its own
  record, the features with their rules, the screens and the seed data.
- **Precomputed features and few questions.** The features were proposed,
  not asked for. Every question had a "(Recommended)" first option, and
  following the recommendations was the whole answer.

The fork's gains are in correctness, templates, guards, UI and deploy. Its
losses come from the conversation layer on top: the welcome, the framed
reports, the step lines, the voice rules and the hooks that enforce them.
Its web-app reading path grew from 37,127 to 46,687 words.

## Decisions (2026-10-11)

1. **Base.** Reboot main (`8b87909`, after reboot#186), not the 1.6.0
   release. The plugin's source is `reboot/plugin/` in `reboot-dev/reboot`;
   `reboot-dev/reboot-plugin` only mirrors releases, and #186 had already
   landed several of the fork's findings there (authorizers from day
   one, `allowed_origins` outside dev, `mcp=None`, the tests' `oauth=`
   wiring, one frontend layout). `~/projects/reboot-next` is a worktree
   of `~/projects/reboot` on branch `next`, with only `reboot/plugin/`
   checked out. `next` is the integration branch and alone carries
   `reboot/plugin/docs/`. Each layer is its own branch from reboot main,
   and becomes a PR to reboot-dev/reboot like #186.
2. **Flywheel brand, light.** A stage heading on the design message
   ("Reboot Design · The hotel") and on the handoff ("Reboot Prove · …").
   No reports, no step lines, no progress band.
3. **Voice.** 1.6.0's natural voice, with no voice rules for now. Revisit
   once the layers are in.

## The shape to keep (1.6.0)

- A one-sentence start, and one routing question only when the prompt
  doesn't name a front door (`skills/app/SKILL.md:89-121`).
- The dashboard starts early, so the user watches the API take shape
  (`skills/web-app/SKILL.md:537-541`).
- One design message in plain language. Every choice gets its what and
  its why (`skills/web-app/SKILL.md:361-421`).
- Questions with the recommended option first.
- Features agreed in English before their files are written
  (`skills/feature/SKILL.md:43-66`).
- A linear build list that names its references at each step
  (`skills/web-app/SKILL.md:524-607`).
- A plain handoff: a URL and a first thing to try
  (`skills/run/SKILL.md:214-229`).
- A reminder hook that leads with "do not guess Reboot behavior"
  (`hooks-handlers/remind.sh:119-134`).

## Layers

Every layer must pass the test below before the next one starts. Paths
marked F: are in the fork, `~/projects/reboot-plugin`.

### L0. Measurement (no change for the user)

- `F:tools/budget.py`, set to reboot main's minimal-path counts as hard
  ceilings: web-app 38,116 words and mcp-ui 48,769 (1.6.0 was 37,127 and
  48,306). The ceilings only move down.
  Whatever a layer adds, it pays for with cuts.
- `F:tools/run-evals.sh` and `F:evals/`. Keep the cases that test
  substance, such as design, correctness and accept. Drop the graders for
  reports, the welcome and voice.
- `F:tools/check-transcript.py`, cut down to the metrics below.
- `F:tools/check.sh` lint and unit stages, plus shellcheck.
- A local commit on `next` that renames the marketplace to `reboot-next`,
  so `reboot/plugin/` installs beside the others. Never upstreamed.
- A new baseline: one hotel build on reboot main's plugin, since hotel-6
  measured 1.6.0.

### L1. Corrections to what 1.6.0 says (edits to existing files)

- ~~Authorizers from the first stub~~ and ~~`allowed_origins` outside
  `rbt dev run`~~: fixed upstream in reboot#186.
- **The missing `OAuth` import** in the web-app auth example, still
  missing on main. It comes from `reboot.aio.auth.oauth`.
- **The API facts** in `F:skills/web-app/SKILL.md:139-203`:
  - reserved method names, as hotel-6 hit with `schedule`;
  - non-zero `Field` defaults are refused;
  - `mcp=` is required on every method;
  - no `list[Entity]` on a parent;
  - use `self.ref().state_id`;
  - never set state in `__init__`;
  - writers can't call writers;
  - a reader's changes to state are discarded;
  - `initialize` runs once per app lifetime;
  - `.rbtrc` is line-based;
  - the `allow_if` rules.
- **Version pins** for `npm create vite`, which now emits React 19 and
  TypeScript 6.

### L2. Knowledge, read only when needed

- `F:skills/python/references/errors.md`: about 258 error strings, each
  with its cause and fix. Grepped, never read whole.
- New references:
  - `lifecycle-seeding.md`
  - `auth-roles.md`
  - `auth-claims.md`
  - `patterns-cross-actor-reads.md`
- `KNOWN-ISSUES.md`: version-specific Reboot defects with their
  workarounds, in one place, without project citations. Sources: the
  fork's `findings/`, `lib/known-defects.json` and `docs/findings-ingestion.md`.
- None of these join the minimal reading path, except one line that
  says to grep `errors.md`.

### L3. Mechanisms, which cost no reading

- `F:lib/patch_reboot.py` and `known-defects.json`: the Envoy `jit.off()`
  and `rbt generate` ENOBUFS patches. Plus the installers pinned by
  SHA-256.
- Guard hooks with a real defect behind each:
  - `schema-guard`
  - `suite-guard`
  - `F:hooks-handlers/orphans.sh`
- A slim project template, aiming for under 15 files rather than the
  fork's 50:
  - `servicers/registry.py`
  - `scripts/api_lint.py`, `scripts/feature_lint.py`, `step_order.py`
  - `scripts/test.sh`, with a timeout, and treating a missing summary line
    as a failure
  - pinned versions
  - `styles.css`
  - ports per project, bound to 127.0.0.1

### L4. Experience, with care

- `F:skills/web-app/references/ui-design.md`: highly visual and highly
  interactive by default, light and dark, and a house look that is never
  Reboot's own brand. Trim it to fit the budget.
- The light Flywheel headings, from decision 2.
- The design message says "proposed" until the user accepts it, never
  "Design is set".

### L5. Deploy

- `scripts/deploy.sh` with backup and restore.
- The cloud facts:
  - `--organization` on every command;
  - secrets only after the first `up`;
  - `up` exits about 30 seconds before the app serves;
  - production denies methods without an authorizer;
  - `DOCKER_HOST` for Docker Desktop.

### L6. Packaging for the Claude app

- `F:tools/package-plugin.sh`, following the app validator's rules:
  - no top-level `bin/`;
  - skill descriptions of at most 1024 characters;
  - `.claude-plugin/plugin.json` is required.

## Left out until an eval earns them back

Each of these comes back only if hotel runs get better with it:

- the verbatim welcome;
- the six framed reports and `design/reports/`;
- step lines and `reboot-now`;
- the progress-band mod;
- `welcome.sh`, `reports.sh` and `quiet.sh`, and the long `remind.sh`;
- the banned-word lists;
- the `design.md`, `review.md`, `decisions.md` and `accepted.json`
  ceremony on a first build;
- the full red suite run before any code;
- the screenshot and page-timing passes;
- the nine-item handoff.

## The test

- **Baseline:** hotel-6, the 1.6.0 run in the Claude app on 2026-10-11.
  Transcript: `~/.claude/projects/-Users-mtrifiro-hotel-6/94861fa0-b0c3-40af-bcc9-6f644670cd79.jsonl`.
- **Prompt:** "Build an app to manage a 56 room boutique hotel with high
  end amenities", answered with "Both" and the recommendations.
- **Metrics** for every layer. Each must be no worse than the baseline:

  | Metric | hotel-6 |
  |---|---|
  | Questions before code | 3 |
  | From the last answer to the design | 47 s |
  | From the last answer to the API file | 5 min |
  | From the last answer to the first passing scenario | 10 min |
  | Words on the minimal reading path | 37,127 web-app |
  | Design message covers users, objects with their why, features with rules, screens, seed data | yes |

- **Correctness, which must improve:** errors hit during the build,
  hotel-6 had one (`schedule` is reserved). Count the scenarios that pass.
  Check that real authorizers are in place.
