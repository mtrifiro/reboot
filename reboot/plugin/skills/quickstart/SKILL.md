---
name: quickstart
description: A guided first run of Reboot, about twenty minutes, on a prepared 56-room hotel. Teaches domain objects, rules in feature files, the scenarios that prove them, method kinds, a code change against a rule change, and reading stored state with rbt inspect, by changing a working app. Use only when the user asks for it by name ("/reboot:quickstart", "the Reboot quickstart", "show me how Reboot works"); never offer it, and never use it to build the user's own app, which is the app skill's job.
allowed-tools: Bash, Read, Write, Edit, Glob, Grep, AskUserQuestion
---

# quickstart: the First Twenty Minutes with Reboot

> **Version notices:** if `rbt` reports a version mismatch or that a
> newer Reboot is available, the [upgrade skill](../upgrade/SKILL.md)
> says how and when to react.

A newcomer learns Reboot faster by changing a working app than by
watching one being built. This skill copies a small, finished hotel
app, Halcyon House, and walks the user through seven stops. Each stop
ends with something the user does, and says in one sentence what it
taught, in the hotel's own nouns.

The hotel is the same every time: two domain objects (`Hotel`,
`Room`), one feature file with two rules and their scenarios, one
page (the floor plan), demo data, and a design already accepted
(`design/`). Keep to the stops: a tutorial that wanders teaches
nothing. If a stop fails (the app won't start, a scenario fails), say
what failed in one line and offer to go straight to the user's own app
with the [`app` skill](../app/SKILL.md).

Ask at each stop's end in a question dialog (`AskUserQuestion` where
available; elsewhere, one plain line as the message's last). Never
offer this skill unprompted.

## Stop 1: set up (about 2 minutes)

Start the slow part first, then explain while it runs.

1. Copy `assets/hotel/` from this skill to `./halcyon-house` in the
   current folder (or a folder the user names), then from the `app`
   skill's `assets/`: `scripts/model_diff.py`, `scripts/test.sh`,
   `scripts/release_record.py` and `tests/last_run.py`;
   `chmod +x scripts/test.sh`. Create an empty `.env`.
2. In the background: `uv sync`, `uv run rbt generate`, and
   `npm ci` in `frontend/`.
3. While those run, say in three lines what the next twenty minutes
   cover: a hotel already running, two of its rules, one change to its
   code and one to its rules, and where its data lives. Name what is
   downloading (Python packages, Node packages, and on a first run
   Reboot's own tools) and that it is the slowest part.

## Stop 2: look (about 3 minutes)

Start the app with the [`run` skill](../run/SKILL.md). If port 9991 or
5173 is already taken by another app, don't stop that app: start this
one with `rbt dev run --port=9781 --dashboard-port=9782` and the
frontend with `PORT=5281 VITE_REBOOT_URL=http://localhost:9781`, and
use those ports below.

Show the floor plan (http://localhost:5173) and the dashboard, then
explain, in this order:

- **Domain objects.** `Room` is one per room, keyed by its number;
  `Hotel` is one per property and serves the floor plan. Each is
  stored by Reboot as it is, with no database to set up. Open
  `api/hotel/v1/hotel.py` at `RoomState`: five fields.
- **A rule, in words.** Open `tests/rooms.feature` at
  `Rule: A guest is checked in only to a clean room`. Rules are the
  app's promises, in plain English.
- **Scenarios prove it.** Under the rule, "Checking a guest into a
  dirty room": one concrete example that runs as a test.

*Your turn:* open a room marked Dirty, enter a guest's name and press
**Check in**. It's refused: "This room can't take a guest: it's dirty."

*Taught:* a domain object, a rule, and the scenario that proves it.

## Stop 3: why it holds (about 2 minutes)

Open `backend/src/servicers/room.py` at `check_in`, and the API's
`check_in=Writer(...)`.

- `check_in` is a **Writer** on one `Room`. Reboot runs one Room's
  writers one at a time, so two desks pressing Check in on the last
  clean room can't both succeed: the second sees it occupied.
- `floor_plan` is a **Reader** on `Hotel`: it changes nothing, and the
  page stays live because Reboot pushes every change to it.
- `add_floor` is a **Transaction**: a whole floor of rooms is created
  together or not at all.
- The `authorizer()` says who may call each method: here only the app
  lays out rooms, and anyone at the desk may use them. A real hotel
  signs its staff in; the user's own build asks who.

*Your turn:* in a second browser tab, open the same room; mark it
clean in one tab and watch the other update.

*Taught:* method kinds, and what Reboot guarantees about them.

## Stop 4: a code change (about 3 minutes)

*Your turn:* ask for "Sort the floor plan from the lowest floor to
the highest."

1. Run `python3 scripts/model_diff.py` first and show its line: no
   change to the domain model, who may call, or the feature files.
2. Change the page (`floors` in `frontend/web/src/pages/FloorPlan.tsx`
   sorts descending; make it ascending).
3. Stop `rbt dev run` (the `run` skill, "Stopping the App"), run
   `scripts/test.sh full`, and start it again. Show the count: every
   scenario still passes.
4. Run `python3 scripts/model_diff.py` again: still nothing that needs
   the user's yes.

Ask nothing before building it: no rule changes, so the scenarios are
the proof.

*Taught:* a change no rule notices is just code; the same scenarios
prove it still keeps every promise.

## Stop 5: a rule change (about 5 minutes)

*Your turn:* ask for "No check-in before 3 pm."

1. Say plainly that this changes a rule, so it needs the user's yes
   before any code. Show it in the feature file's words:
   `Rule: A guest is checked in only after 3 pm`, with two scenarios
   ("Checking a guest in at 11:00", refused; "Checking a guest in at
   15:00", allowed). 3 pm is in the user's own time zone; don't ask.
2. Ask one question: build this rule as written, or change it first.
3. On a yes: write the rule and its scenarios in
   `tests/rooms.feature`, tagged `@wip`, each starting
   `Given it is 11:00 at the hotel` (or 15:00); run them red. Then:
   - `backend/src/clock.py`: `def now() -> datetime:` returning
     `datetime.now().astimezone()`, the one place the app reads the
     time;
   - in `check_in`, refuse before 15:00 with a new declared error,
     `TooEarlyError`, added to the method's `errors=` (additive);
   - in `tests/conftest.py`, the step `it is {hhmm} at the hotel`,
     which patches `clock.now` with `unittest.mock.patch` for the
     scenario, plus a default of 16:00 for every other scenario so the
     existing ones don't depend on the real time
     (`python/references/testing-external-context.md`, "mock.patch for
     plain Python helpers");
   - the page's message for `TooEarlyError` in `errors.ts`.

   Run `rbt generate`, then `scripts/test.sh full` with the dev loop
   stopped, and take `@wip` off.
4. Run `python3 scripts/model_diff.py`: the new rule is listed as
   needing the user's yes, and was given one. Record the acceptance as
   [`app/references/accept-design.md`](../app/references/accept-design.md)
   says: `design/design.md` gains the rule's row, `design/decisions.md`
   an entry with the user's words, and `model_diff.py --accept`
   updates `design/accepted.json` and `design/accepted/`.
5. Show the new decisions entry.

*Taught:* rules are the specification, and code follows them. A rule
changes only with the user's yes, and the decisions log keeps why.

## Stop 6: look inside (about 2 minutes)

Run:

```shell
rbt inspect state get --type=hotel.v1.Room --id=<the room checked in> \
  --application-url=http://localhost:9991
```

Show the stored state behind the page: the room's status and guest.
Point out that this is what the page reads, and that the same command
works against a deployed app. (`rbt inspect` prints the status as
`Status_occupied`; it is `occupied` in the API.)

*Taught:* the state is real and inspectable; a question about
production starts here.

## Stop 7: your app

Recap in three lines:
- a domain object holds its own state and runs its own changes;
- a rule in plain words, proven by scenarios, is the spec;
- a code change is proven by the suite, a rule change waits for your
  yes, and both are recorded.

Then ask in a question dialog: **Build your own app** (recommended:
ask what it should do, then load the [`app` skill](../app/SKILL.md)
with that brief), **Keep the hotel to explore**, or **Remove the
hotel** (stop its processes with the `run` skill, then delete the
folder after one more yes).

## Notes

- The browser console shows a `/__/oauth/whoami` CORS error on every
  load: the hotel has no sign-in, and Reboot 1.6.0's client probes for
  one anyway. Nothing breaks (`python/references/errors.md`). Say so if
  the user opens the console.
- Never commit, push or create a repository for the hotel unless the
  user asks.
- The hotel's demo afternoon (34 rooms occupied, 12 dirty, 10 clean)
  is seeded only under `rbt dev run`; the scenarios start from an empty
  building.
