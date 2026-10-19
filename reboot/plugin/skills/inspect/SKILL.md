---
name: inspect
description: Inspect the live state of a running Reboot application from the command line with `rbt inspect`. Lists the application's state types, lists the state IDs (actor IDs) for a type, and prints a single actor's state as JSON. Works against both a local `rbt dev run` backend and a deployed Reboot Cloud app via `--application-url` and `--admin-credential`. Use this to answer "what state types does this app have?", "which actors of this type exist?", or "what is stored in this actor right now?" — i.e. to debug persisted state from the terminal instead of the `/__/inspect` web dashboard.
argument-hint: "[type list | state list --type=<full.Name> | state get --type=<full.Name> --id=<id>]"
allowed-tools: Bash, Read
---

# inspect — Inspect a Running Reboot Application's State

> **Version notices** from `rbt` (a mismatch, a newer Reboot): the [upgrade skill](../upgrade/SKILL.md).

`rbt inspect` reads the persisted state of a **running** Reboot
application — what the `/__/inspect` page (linked from `rbt dev run`
and `rbt cloud up` output) shows beside recent calls, but from the
terminal, scriptable and pipeable. Reach for it when the question is
about _runtime state_ rather than code: "did `create` actually persist
this field?", "which account IDs exist?", "what does actor `alice`
look like right now?". It only reads.

> This skill **inspects** a running app; it does not start one — the
> [run skill](../run/SKILL.md) does. To change what an app stores,
> the [python skill](../python/SKILL.md).

This is the Reboot Flywheel's **Observe** stage
([`app/references/flywheel.md`](../app/references/flywheel.md)). The
readable history is the history the design chose to record, so a
question the stored state can't answer is a gap in the design. A finding goes back by the
routing rule there: a code fix to Prove, a missing or wrong rule to
Design.

## From a finding to a scenario

A report names a reservation, a room or a person: a state ID. From
the report to the state ID, to the stored state (below), to the rule
it breaks. Then the fix starts as a scenario, by the
[`feature` skill](../feature/SKILL.md)'s "A fix, a bug report, a
review finding":

- Name the state ID and the revision that was live (the last row of
  `deploy/ledger.jsonl`, [`app/references/evidence.md`](../app/references/evidence.md))
  in the scenario's description.
- Reproduce the stored state through the methods that produce it,
  never by writing state directly: a state no method can reach proves
  nothing about the app.
- Put the scenario under the rule it breaks. When no rule says what
  should have happened, the rule is the gap: write it, and it goes to
  Design for acceptance before the fix.

## The three operations

```sh
# 1. List the application's registered state types (full names).
rbt inspect type list --application-url=<url>

# 2. List the known state IDs (actor IDs) for one type.
rbt inspect state list --type=<full.Type.Name> --application-url=<url>

# 3. Print a single actor's state as JSON.
rbt inspect state get --type=<full.Type.Name> --id=<state-id> \
  --application-url=<url>
```

Drill down: `type list` for the exact name to pass to `--type`, then
`state list` for the `--id`, then `state get`.

- `--type` takes the **full, package-qualified** type name exactly as
  `type list` prints it (e.g. `bank.v1.Account`, `tests.reboot.Echo`)
  — not the bare Python class name.
- `--id` is the actor's state ID: the string passed to
  `<Type>.ref(id)` / `<Type>.create(context, id, ...)`.
- `state get` prints the state as a JSON object. Pipe it to `jq` or a
  file like any other JSON.

## Connecting: `--application-url` and `--admin-credential`

Both flags match `rbt export` / `rbt import` (see
`../python/references/lifecycle-reboot-cloud.md`).

- `--application-url` is the app's API URL — **not** the `/__/inspect`
  page URL. It is the address printed as **"Your API is available
  at:"** when the app starts.
  - **Local dev:** the URL `rbt dev run` prints (e.g.
    `https://<app>.localhost` under `--portless`, else
    `http://localhost:9991`).
  - **Reboot Cloud:** the URL `rbt cloud up` prints (e.g.
    `https://<application-id>.prod1.rbt.cloud:9991`).
- `--admin-credential` is the app's admin secret, stored under the
  `SECRET_REBOOT_ADMIN_TOKEN` secret.
  - **Local dev:** defaults to `dev`, so it may be omitted.
  - **Reboot Cloud:** required — the value set for
    `SECRET_REBOOT_ADMIN_TOKEN` (see
    `../python/references/lifecycle-secrets.md`).

### Examples

Local `rbt dev run` (admin credential defaults to `dev`):

```sh
rbt inspect type list --application-url=http://localhost:9991

rbt inspect state list \
  --type=bank.v1.Account \
  --application-url=http://localhost:9991

rbt inspect state get \
  --type=bank.v1.Account --id=alice \
  --application-url=http://localhost:9991
```

Reboot Cloud (admin credential required):

```sh
rbt inspect state get \
  --type=bank.v1.Account --id=alice \
  --application-url=https://<application-id>.prod1.rbt.cloud:9991 \
  --admin-credential="$SECRET_REBOOT_ADMIN_TOKEN"
```

## Notes

- **Read-only.** `rbt inspect` never mutates state; it is safe to run
  against production.
- **`state get` routes to the actor's host automatically**, even in a
  multi-server deployment, and reassembles large states transparently.
- **Pipeable output.** `type list` and `state list` print one entry
  per line; `state get` prints a single JSON object. Nothing is
  colorized when the output is not a TTY, so it composes with `grep`,
  `jq`, etc.
