---
name: quickstart
description: A guided first run of Reboot, about twenty-five minutes, on a finished boutique-hotel app. Tours its architecture, rules and tests on the developer dashboard through deep links, then makes one code change and one rule change. Teaches domain objects, packages, method kinds, rules in feature files and the scenarios that prove them, who may call, the design record, and reading stored state with rbt inspect. Use only when the user asks for it by name ("/reboot:quickstart", "the Reboot quickstart", "show me how Reboot works"); never offer it, and never use it to build the user's own app, which is the app skill's job.
allowed-tools: Bash, Read, Write, Edit, Glob, Grep, AskUserQuestion
---

# quickstart: the First Twenty-Five Minutes with Reboot

> **Version notices:** if `rbt` reports a version mismatch or that a
> newer Reboot is available, the [upgrade skill](../upgrade/SKILL.md)
> says how and when to react.

A newcomer learns Reboot fastest from a finished app they can open,
read and change. This skill copies one, Maison Desk, the staff app of a
56-room boutique hotel, and tours it on the developer dashboard: its
architecture, its rules, and the tests that prove them, each through a
deep link that opens on exactly the thing being explained. Then the
user changes it twice.

The hotel is the same every time:

| | |
| --- | --- |
| Packages | `rooms.v1` (Room), `reservations.v1` (Reservation, Inventory), `staff.v1` (Team, User), and `hotel.v1` (Hotel) on top |
| Features | `room_status.feature`, `reservations.feature`, `staff_roles.feature`: 14 rules, 41 scenarios, one with a browser video |
| Pages | the floor plan, the front desk, the staff roster |
| Accounts | Alice (manager), Ben (front desk), Carlos and Dani (housekeeping), from the development sign-in |
| Record | `design/`: the design, the decisions log, and the accepted design |

Keep to the stops: a tutorial that wanders teaches nothing. Each stop
ends with something the user does and says in one sentence what it
taught, in the hotel's nouns. Ask at a stop's end in a question dialog
(`AskUserQuestion` where available; elsewhere, one plain line as the
message's last). If a stop fails (the app won't start, a scenario
fails), say what failed in one line and offer to go straight to the
user's own app with the [`app` skill](../app/SKILL.md). Never offer
this skill unprompted.

**Deep links.** Every object, method, feature and rule named below is a
link to the dashboard, on the port it started on (`dashboard` skill,
"Links to an Object or a Rule"). `<dash>` below is that address,
`http://127.0.0.1:9871` by default.

## Stop 1: set up (about 3 minutes)

Start the slow part first, then explain while it runs.

1. Copy `assets/hotel/` from this skill to `./maison-desk` in the
   current folder (or a folder the user names), then from the `app`
   skill's `assets/`: `scripts/model_diff.py`, `scripts/test.sh`,
   `scripts/release_record.py` and `tests/last_run.py`;
   `chmod +x scripts/test.sh`. Create an empty `.env`.
2. In the background, in order: `uv sync`, `uv run rbt generate`,
   `npm ci` in `frontend/`, then `scripts/test.sh full` once, so the
   dashboard shows every scenario's result and the browser video.
3. Start the dashboard with the [`dashboard` skill](../dashboard/SKILL.md)
   as soon as `rbt generate` is done, and the app with the
   [`run` skill](../run/SKILL.md) once the suite has finished. If port
   9991 or 5173 is taken by another app, don't stop that app: start
   this one with `rbt dev run --port=9781 --dashboard-port=9782` and
   the frontend with `PORT=5281 VITE_REBOOT_URL=http://localhost:9781`,
   and use those ports below.
4. While they run, say in three lines what the next twenty-five
   minutes cover: a finished hotel app, its architecture and rules on
   the dashboard, one change to its code and one to its rules. Name
   what is downloading and that it is the slowest part.

## Stop 2: the app (about 3 minutes)

Open the floor plan (http://localhost:5173). *Your turn:* sign in as
**Ben** (front desk), open a room marked Dirty, and try to check a
guest in. It's refused: the room hasn't been cleaned and inspected.
Then open the **Front desk** page: today's arrivals and departures, and
what's left to sell.

*Taught:* this is a working app with real rules; next, where they live.

## Stop 3: the architecture (about 4 minutes)

Open [Models](<dash>/#/models). It draws the whole API from the code.

- **Packages.** Four boxes: `rooms.v1`, `reservations.v1`, `staff.v1`,
  and `hotel.v1` on top. The Hotel imports from rooms and reservations,
  and nothing imports the Hotel, so the layers never loop.
- **Domain objects.** [Room](<dash>/#/models?type=rooms.v1.Room) is
  one per room, keyed by its number. It is its own object because each
  room changes on its own. Reboot stores each object as it is, with no
  database to set up.
- **Method kinds, by color** (the legend):
  - [`Room.check_in`](<dash>/#/models?type=rooms.v1.Room.check_in)
    is a **Writer**. Reboot runs one Room's writers one at a time, so
    two desks can't put guests into the same room.
  - [`Hotel.book`](<dash>/#/models?type=hotel.v1.Hotel.book) is a
    **Transaction**. It reserves the nights on the room type's
    Inventory and creates the Reservation, both or neither.
  - [`Hotel.front_desk`](<dash>/#/models?type=hotel.v1.Hotel.front_desk)
    is a **Reader**. It changes nothing, and the page it feeds updates
    live.
- **The call graph.** The lines from the Hotel are its calls into the
  other packages: the front desk reaching rooms and reservations.

*Your turn:* click any method in the graph and follow one of its
lines.

*Taught:* objects, packages and method kinds, drawn from the code.

## Stop 4: the rules and their proof (about 4 minutes)

Open [Features](<dash>/#/features/tests/reservations.feature). Each
feature file is a set of rules in plain English, and each rule has the
scenarios that prove it, run as tests.

- [A room type is never booked beyond the rooms the hotel has of it](<dash>/#/features/tests/reservations.feature/rules/1):
  open "The Penthouse booked twice for an overlapping night" and read
  its steps.
- [The person who cleaned a room cannot be the one who inspects it](<dash>/#/features/tests/room_status.feature/rules/3).
- [The hotel always keeps at least one manager](<dash>/#/features/tests/staff_roles.feature/rules/3).
- The scenario with a **VIDEO** badge, "The front desk books a stay and
  checks the guest in on the day", drove the real page in a browser.

*Your turn:* play the video.

*Taught:* rules are the app's specification, and the scenarios under
each rule are its proof.

## Stop 5: who may call (about 2 minutes)

*Your turn:* sign out, sign in as **Carlos** (housekeeping), and open
a room that's ready. There's no **Check in** for him: housekeeping
cleans and inspects, and the front desk checks in. The page only hides
the button; the backend refuses the call too, which the scenario
"Housekeeping cannot take bookings" proves.

Show the rule behind it,
[Each role does only its own part of the work](<dash>/#/features/tests/room_status.feature/rules/6),
and where it's enforced: each servicer's `authorizer()` in
`backend/src/servicers/`, with the roles in `auth.py`. Roles live only
on the Team, so nobody can promote themselves.

*Taught:* who may call each method is part of the design, enforced on
every call.

## Stop 6: a code change (about 3 minutes)

*Your turn:* ask for "Show the floor plan with the top floor first,
like the building."

1. Run `python3 scripts/model_diff.py` and show its line: no change to
   the domain model, who may call, or the feature files.
2. Change the page (`floors` in `frontend/web/src/pages/FloorPlan.tsx`
   sorts ascending; make it descending).
3. Stop `rbt dev run` (the `run` skill, "Stopping the App"), run
   `scripts/test.sh full`, and start it again. Show the count: every
   scenario still passes.

Ask nothing before building it: no rule changes, so the scenarios are
the proof. The dashboard's [Changelog](<dash>/#/changelog) shows
nothing new: the API didn't change.

*Taught:* a change no rule notices is just code; the same scenarios
prove every promise still holds.

## Stop 7: a rule change (about 5 minutes)

*Your turn:* ask for "A stay can't be booked for a night that has
already passed."

1. Say plainly that this adds a rule, so it needs the user's yes
   before any code. Show it in the feature file's words, under the
   reservations feature: `Rule: A stay can't be booked for a night that
   has already passed`, with two scenarios, each starting
   `Given it is "2027-03-02T10:00" at the hotel`: booking a stay that
   arrives yesterday is refused with `InvalidDatesError`; one that
   arrives today is booked. The hotel's time is the user's own; don't
   ask.
2. Ask one question: build this rule as written, or change it first.
3. On a yes: add the rule and its scenarios to
   `tests/reservations.feature`, after the first rule, tagged `@wip`;
   run them red. In `Hotel.book` (`backend/src/servicers/hotel.py`),
   after the check that departure is after arrival, refuse an arrival
   before `clock.today()` with
   `InvalidDatesError(reason="Arrival can't be in the past.")`. Stop
   the dev loop, run `scripts/test.sh full` (43 pass), take `@wip` off,
   start it again.
4. Run `python3 scripts/model_diff.py`: one change, the new rule,
   listed as needing the user's yes, and no change to the API. Record
   the acceptance as
   [`app/references/accept-design.md`](../app/references/accept-design.md)
   says: `design/design.md` gains the rule, `design/decisions.md` an
   entry with the user's words, and `model_diff.py --accept` updates
   `design/accepted.json` and `design/accepted/`.
5. Show the new rule on the dashboard,
   [reservations rule 2](<dash>/#/features/tests/reservations.feature/rules/2),
   with its two passing scenarios, and the new decisions entry.

*Taught:* a rule changes only with the user's yes; the scenarios prove
it, and the decisions log keeps why.

## Stop 8: look inside (about 2 minutes)

Run:

```shell
rbt inspect state get --type=rooms.v1.Room --id=<a room number> \
  --application-url=http://localhost:9991
```

Show the stored state behind the page: the room's status, guest, and
who cleaned it. The same command works against a deployed app.
(`rbt inspect` prints a status as `Status_occupied`; it is `occupied`
in the API.)

*Taught:* the state is real and inspectable; a question about
production starts here.

## Stop 9: your app

Recap in three lines:
- domain objects hold their own state and run their own changes,
  grouped into packages;
- rules in plain words, proven by scenarios, are the spec;
- a code change is proven by the suite, a rule change waits for your
  yes, and both are recorded.

Then ask in a question dialog: **Build your own app** (recommended:
ask what it should do, then load the [`app` skill](../app/SKILL.md)
with that brief), **Keep the hotel to explore**, or **Remove the
hotel** (stop its processes with the `run` skill and the dashboard,
then delete the folder after one more yes).

## Notes

- `hotel.v1` keeps its own copy of six errors its methods pass on
  from rooms and reservations: Reboot 1.6.0 can't declare an error
  from another package on a method (reboot#258). Say so if the user
  asks why the errors appear twice.
- Never commit, push or create a repository for the hotel unless the
  user asks.
- The hotel's busy afternoon (guests, bookings, rooms in every state)
  is seeded only under `rbt dev run`; the scenarios start from an
  empty building at 4 pm on 1 March 2027.
