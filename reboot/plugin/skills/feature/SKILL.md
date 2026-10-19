---
name: feature
description: Specify a Reboot application's feature before and while building it, as a Gherkin `.feature` file the tests run and the dashboard shows. Use whenever the user asks for a new capability or a change to one ("add transfers", "users should be able to..."), before touching the API or code; and when converting an existing test suite to feature files. Agrees on the feature in plain English first, writes it down tagged `@wip`, builds it with the `python` / `web-app` / `mcp-app` skills, then iterates on scenarios with the user until they agree to take the tag off.
argument-hint: [<feature-description>]
allowed-tools: Bash, Read, Write, Glob, Grep, Edit, AskUserQuestion
---

# feature — Specify a Feature, Then Build It

> **Version notices** from `rbt` (a mismatch, a newer Reboot): the [upgrade skill](../upgrade/SKILL.md).

A feature of a Reboot application is written down once, as a
`.feature` file in `tests/`, and that one file is the
specification the developer reviews, the tests `pytest` runs, and
the card the dashboard's Features page shows. This skill is the
order of work that keeps the file true while the feature is built:
agree on it in English, write it down before any code, tag what is
unfinished, and take the tag off only when the developer says so.

The mechanics of feature files, the built-in steps and their
spelling, custom steps, and the web app steps are in the `python`
skill's references; read them at the step that needs them:

- `../python/references/testing-features.md` — **read before
  writing any scenario**: the step vocabulary, who calls, saved
  values, assertions, `@wip` / `@blocked`.
- `../python/references/testing-custom-steps.md` — when a scenario
  needs a step the built-in steps don't have.
- `../python/references/testing-web-app.md` — read when a scenario
  opens the web app: the `frontend` fixture, the web app steps, the
  accessible markup the page needs, recordings.
- `../python/references/testing-project-setup.md` — the files a
  suite needs (`reboot[dev]`, `pytest.ini`, `.gitignore`).

## Step 1 — Propose the feature in English

Before any file changes, tell the user what you understand the
feature to be, as a person would describe it, not as an API:

- **Its name**, a sentence about the activity: "Customers can
  transfer money between accounts".
- **What it is for**, a short paragraph: who does it, why, what
  they see when it worked.
- **Its rules**, only where there is a clear business rule or an
  invariant of the whole system, the kind one would want to verify
  formally: money is conserved by a transfer; a balance never goes
  below zero; a customer sees only their own accounts. Most features
  have one or two; many have none. Do not dress up "the button
  works" as a rule.
- **The job, start to finish:** who does it and what they are
  trying to get done (the user story), then each step from the job's
  start to its end, not the first click. Each thing the feature adds
  gets its whole lifecycle: created, seen in a list and on its own,
  found, changed (an edit for every field a person could get wrong),
  corrected (undo, cancel) and ended (done, cancelled, archived,
  deleted, as the domain says). A part left for later is named, never
  silently absent; "edit" is the part builds miss most.
- **A few example situations** in prose, one line each: "a
  transfer between two customers' accounts"; "a transfer for more
  than the source holds".
- **Whether the web app is part of it**, when the app has one: the
  flow a person clicks through, if that is how the feature is used.

Ask the user whether that is the feature. Iterate on the English
until they agree; the file follows the words, so the words come
first. In a build, a feature the user chose or asked for in their own
words needs no question: say it in a few lines and go on; they judge
it running at the next handoff (`app/references/accept-design.md`).

## Step 2 — Write it down, tagged `@wip`

Once agreed, create `tests/<capability>.feature`, named for
the activity (`transfers.feature`, not `bank.feature`), with the
agreed name and description, and the rules with their descriptions
where the user agreed on some. It may have no scenarios yet; write
it anyway, with `@wip` on the whole feature:

```gherkin
@wip
Feature: Customers can transfer money between accounts
  A customer moves money from one of their accounts to another
  account of the bank in one step.

  Rule: A transfer that would overdraw the source leaves both accounts unchanged
    A transfer is one transaction, so money is never created by a
    failed transfer.
```

(The full shape, with `Background:` and scenarios, is in
`testing-features.md`.)

Add the file to the `scenarios(...)` call of the test module whose
application it runs against, or create the module
(`testing-features.md` shows the minimal one). If the project has
no test suite yet, set one up per `testing-project-setup.md`, which
includes `reboot[dev]` in the dev dependencies and `*.recordings/`
in `.gitignore`.

Once the file is written, give the user a direct link to inspect it,
in one line. After that, every message that names a feature file or
one of its rules (a summary, a status line, the handoff) links it,
on the dashboard once it runs (a rule adds `/rules/<n>`, `dashboard`
skill, "Links to an Object or a Rule"), never as a bare path in code:

- **The dashboard is running** (the `dashboard` skill): the feature
  shows up on its Features page at once, marked as work in progress.
  Link it there, at the URL the dashboard started on
  (`https://dashboard.<app>.localhost` under portless, else
  `http://127.0.0.1:<port>`):
  "[Room status floor plan](https://dashboard.hotel.localhost/#/features/tests/room_status.feature)
  is written: its rules, as scenarios, ready to read."
- **Not yet** (the first feature is written before the dashboard
  starts): link the file itself, `tests/<name>.feature`, and say the
  dashboard shows it once it is up; the dashboard's first line then
  links it again.

## Step 3 — Build the feature

Change the API, the servicers, and the frontend with the `python`
skill and, for the frontend, the `web-app` or `mcp-app` skill. Two
rules of theirs matter most here: **every property gets a
`description=`** on its `Field(...)` (`api-pydantic.md`; the
dashboard shows it beside the property, and asks for one where it is
missing), and **a web app page is built with accessible markup** from
the start (`testing-web-app.md`), which is what lets a scenario drive
it.

## Step 4 — Iterate on the scenarios with the user

After the API and code change, turn the example situations into
scenarios and run them; then keep going with the user: show them
each scenario, ask what else the feature must do, write that down,
run it. Concretely:

- **Write each scenario in the built-in steps** (`testing-features.md`),
  named for the situation, under the rule it illustrates, or at the
  feature's top level when it illustrates no rule.
- **Let a factory make the id up**: `"alice" creates an `Account`via`open``and`the resulting state id is saved as "account
id"`, then `<account id>`. Give an id only when it means something
  to the application (a user id, a singleton the code refers to).
- **Move `@wip` down as scenarios land**: once a rule or scenario
  is written, put `@wip` on it and take it off the feature, so the
  dashboard shows exactly what is still being worked on.
- **Tag `@blocked` what cannot pass yet**: a scenario the
  application cannot pass (a declared error it does not raise yet),
  or one that needs a person to act first (a credential to obtain,
  a decision to make, an external system to set up). Say why in the
  paragraph under the `Scenario:` line; that paragraph is the skip
  reason and what the dashboard shows. Do not delete or weaken a
  scenario to make the suite green.
- **Suggest a web app scenario** when the feature is something a
  person does in the app: the clicks and what they see, with
  backend assertions on the state it left behind
  (`testing-web-app.md`). Running it records a video and screenshots
  the user can watch on the Features page.
- **Suggest a rule only for a real invariant**, one that would be
  worth formal verification; when a scenario shows what an
  operation does and nothing more, leave it at the top level.
- **Run the suite** with `rbt dev run` stopped (`run` skill,
  "Stopping the App") (`uv run pytest`, or `-m wip` for
  what is in progress) and `uv run mypy backend/ tests/`; fix what fails.
  While it runs, don't regenerate code, start another `rbt dev run` or
  edit `api/`, `backend/` or `web/`: a suite run beside those changes
  has failed with errors that look like Reboot's. The full run at
  the commit being proposed is the Flywheel's Prove evidence; a
  `-m wip` or `-k` run is not
  ([`app/references/flywheel.md`](../app/references/flywheel.md)).
- **Never filter a run's output.** No `| grep`, `| head` or `| tail`
  on a suite run: they print nothing until the run ends, so a hang
  looks like silence and the failing scenario's name is lost. Run it
  as it is, or in the background and read `tests/.progress.jsonl`
  (below). If a run hangs anyway, stop it and rerun with `-x`, which
  stops at the first failure, unfiltered: the per-test `timeout` in
  `pytest.ini` names the scenario that hung.
- **A feature's own scenarios run in the foreground.** While a
  feature is being built, run its own files (`uv run pytest
  tests/<feature>_test.py`, or `-m wip`, `-k`) as a plain foreground
  command: the per-test `timeout = 180` in `pytest.ini` bounds a hang
  and names the scenario, so no `sleep`, no polling loop and no
  monitor. One line before it says what runs ("Backend: running the
  room booking's 14 scenarios."); when it ends, one line from
  `tests/.last-run.json`: every rule kept, or which rules aren't kept
  yet, by the rule in plain words, then the fix.
- **Report a full run once, at the end.** The whole suite
  (`scripts/test.sh full`, or `uv run pytest`) runs once, at a
  handoff or the whole-app end, in the background while the handoff
  is written, after the same one line. A line per rule as each
  finishes is noise: post nothing per scenario and don't watch it
  with a monitor that reports each test. Never wait on it (`sleep`,
  an `until` loop): write the handoff while it runs; its completion
  notice comes on its own. Only if the handoff is written and the run
  is past about three minutes, check `tests/.progress.jsonl`
  (`tests/last_run.py` writes a line per scenario) and say once that
  it is still running, with the count done. When it ends, its result the
  same way, once.
- **Suggest reviewing in the dashboard** after each round: the
  feature's card, its rules, the methods it uses and the ones no
  feature uses, and the recordings.

## Step 5 — Ask before taking `@wip` off

When every scenario passes (or is `@blocked` with a reason) and the
user has said the feature does what they meant, ask whether to
remove the `@wip` tags (in a build, the handoff's question is that
ask: `app/references/accept-design.md`). Take them off only with their agreement;
`@blocked` tags stay until the blocking is resolved.

## A fix, a bug report, a review finding

"Fix this", or a list of review findings, is a request to change
behavior, not permission to skip the feature. For each:

1. Say in one line what the app does now and what it should do.
2. Write that as a scenario under the rule it breaks, tagged `@wip`,
   in the feature that owns the behavior, the ticket's id in its name
   when there is one.
3. Route it by the Flywheel's routing rule
   ([`app/references/flywheel.md`](../app/references/flywheel.md));
   `python3 scripts/model_diff.py HEAD` sorts it.
   A new scenario under an existing rule is a code fix: it stays in
   Prove. A new or reworded rule, a changed scenario, or a fix that
   needs an API change or changes who may call a method is a design
   change: say so, show the model diff, and take it through
   [`app/references/accept-design.md`](../app/references/accept-design.md)
   before any code.
4. Show the user the scenario and run it red before any code.
5. Fix, run the full suite green, and ask before taking `@wip` off.
   Close with the **Reboot Prove · the fix is in** card
   ([`app/references/flywheel.md`](../app/references/flywheel.md)):
   in full the first time, one line after.

Only a change no scenario could see (a typo in a comment, a rename
inside one function) skips this, and you say so.

## Converting an existing test suite

When an application has `unittest` / `IsolatedAsyncioTestCase`
tests and the user wants them as feature files, or the `upgrade`
skill's migration notes ask for it:
[`references/converting-tests.md`](references/converting-tests.md).
