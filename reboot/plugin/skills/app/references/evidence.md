---
title: Evidence for Merge and Promote
impact: MEDIUM
impactDescription: Without it a pull request or a deploy ships with no record of the rules it touched or the scenarios that passed
tags: flywheel, prove, evidence, pull request, release record, model diff, ledger
---

## Evidence for Merge and Promote

The work is in the Reboot Flywheel's Prove stage
([`flywheel.md`](flywheel.md)) and about to cross a decision the user
makes: **merge** (a pull request) or **promote** (a deploy). Evidence
is what a person can read after this session ends, tied to the
revision it describes. Agent confidence and chat output do not count.

### The project's evidence files

At the first handoff, with the acceptance record's files
([`accept-design.md`](accept-design.md)), copy these from the `app`
skill's `assets/`, keeping their paths:

| File | What it does |
| --- | --- |
| `scripts/test.sh` | The suite in the size a change needs: `changed`, `smoke`, `backend`, `<area>`, `full`. Only `full` is evidence for a merge or a deploy |
| `scripts/release_record.py` | What a deploy ships and what it rests on; appends the release record to `deploy/ledger.jsonl` |

Add `smoke` and `browser` to `pytest.ini`'s `markers` when the
feature files use those tags.

### A pull request, when the user asks for one

Commits, branches and pushes are the user's and their team's; the build
does none of them unasked. When the user asks for a pull request or its
description:

1. Run the **full** suite (`scripts/test.sh full`) on what the pull
   request holds. It writes `tests/.last-run.json`.
2. Run `python3 scripts/model_diff.py --head`, measured from the
   accepted design.
3. Write the body in this order, rules first, so a reviewer decides
   how much code to read:

```markdown
## Rules this changes
<the feature-file changes from the model diff, or "None: a code fix";
the tickets it names, when the feature files name any>

## Domain model
<the model diff's domain-model and who-may-call lines, or "No change">

## Scenarios
12 passed, 0 failed, 2 @wip, 1 @blocked (full suite at abc1234).
@blocked: <scenario>: <why>

## Design accepted
<the model diff's verdict: "Yes, on 2026-10-10", or "No, 2 design
changes since the acceptance on 2026-10-10">
```

A design change in the diff with no acceptance behind it goes back to
Design first. Push the branch or open the pull request only on the
user's yes; with no remote, hand over the body to paste.

### Before a deploy

`python3 scripts/release_record.py --dry-run` prints the commits since
the last deploy, the model diff against it, the last test run, the
accepted design, and any servicer with no authorizer. It says when the
run is not a clean, full, passing run of the commit being deployed,
and when the design carries changes nobody accepted. Show the user
that output with the **Reboot Prove · ready to deploy** card and let
them decide; the script never stops a deploy.

### The release record

After the deploy succeeds, `python3 scripts/release_record.py`
(`--revision`, `--api-url` and `--site` from the deploy's output)
appends one row to `deploy/ledger.jsonl`. The last row is the revision that is live,
and its `release` field is the record:

```json
{"tests": {"passed": 12, "failed": 0, "wip": 2, "blocked": 1,
           "full": true, "revision": "abc1234"},
 "since": "9f8e7d6",
 "commits": ["abc1234 Book several rooms in one reservation"],
 "model_diff": {"design": ["`Reservation.create` added, Transaction"],
                "prove": []},
 "unauthorized_servicers": [],
 "accepted": {"commit": "7c1d2e3...", "at": "2026-10-10T16:02:11-07:00",
              "fingerprint_ok": true, "is_base": true, "design_changes": 0}}
```

To answer "what shipped, and on what evidence?" later, read the row
for the deploy in question.

## Never

- Evidence from another revision: a test run before the last commit,
  or with uncommitted changes, is not this revision's.
- Hand-editing `deploy/ledger.jsonl`; `release_record.py` writes it.
- Committing, pushing, adding a remote or creating a repository the
  user didn't ask for.

## Limits

- The release record holds the test summary, not each scenario's
  result; failures and `@blocked` reasons go in the pull request body.
- `tests/.last-run.json` is git-ignored: it is this machine's last run,
  so run the suite again on the commit you ship.
