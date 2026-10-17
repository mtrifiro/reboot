---
name: quickstart
description: A guided first run of Reboot, about half an hour, on a finished boutique-hotel app. Tours its architecture, rules and tests on the developer dashboard through deep links, then makes one code change and one rule change. Teaches domain objects, packages, method kinds, rules in feature files and the scenarios that prove them, who may call, the design record, and reading stored state with rbt inspect. Use only when the user asks for it by name ("/reboot:quickstart", "the Reboot quickstart", "show me how Reboot works"); never offer it, and never use it to build the user's own app, which is the app skill's job.
allowed-tools: Bash, Read, Write, Edit, Glob, Grep, AskUserQuestion
---

# quickstart: the First Half Hour with Reboot

> **Version notices** from `rbt` (a mismatch, a newer Reboot): the [upgrade skill](../upgrade/SKILL.md).

A newcomer learns Reboot fastest from a finished app they can open,
read and change. This skill copies one, Maison Desk, the staff app of a
56-room boutique hotel, and tours it on the developer dashboard: its
architecture, its rules, and the tests that prove them, each through a
deep link that opens on exactly the thing being explained. Then the
user changes it twice.

The hotel is the same every time: hotel-23 at the commit named in
`assets/hotel/SOURCE`, copied by `dev/sync-quickstart-hotel.sh` (never
edited here; change the hotel in its own repository and sync).

| | |
| --- | --- |
| Packages | `rooms.v1` (Room), `reservations.v1` (Reservation, Inventory), `staff.v1` (Team, User), and `hotel.v1` (Hotel) on top |
| Features | `room_status.feature`, `reservations.feature`, `staff_roles.feature`: 13 rules, 41 scenarios, three with browser videos (shipped with the hotel) |
| Pages | the floor plan, the front desk, the staff roster |
| Accounts | Alice (manager), Esi (front desk), Carlos and Dani (housekeeping); Ben has no role. These are the development sign-in's five built-in people |
| Record | `design/`: the design document (every object, method and rule a dashboard link), the decisions log, and the accepted design |

Keep to the stops: a tutorial that wanders teaches nothing. Each stop
ends with something the user does and says in one sentence what it
taught, in the hotel's nouns.

**Ask nothing to get going.** The user asked for the quickstart: from
the introduction through setup and the tours, install, start and open
everything without a question, confirmation or choice (not where to
put the hotel, not which port, not "ready?"). Say what was done, then
the next stop. A stop with a *Your turn* ends with one plain line,
**Try it, then say next.**, never a question or a dialog ("Did it get
refused?", "Ready for the architecture?"); whatever the user says next
starts the next stop, and anything they ask is answered first. The quickstart asks the user two things in all: the yes
for the rule change in the rule-change stop, which is that stop's
lesson, and what to do at the end. If a stop fails (the app won't start, a scenario
fails), say what failed in one line and offer to go straight to the
user's own app with the [`app` skill](../app/SKILL.md). Never offer
this skill unprompted.

**Deep links.** Every object, method, feature and rule named below is a
link to the dashboard, on the port it started on (`dashboard` skill,
"Links to an Object or a Rule"). `<dash>` below is that address,
`http://127.0.0.1:9871` by default.

## Stop 1: what Reboot is (about 2 minutes)

**This message is the quickstart's first output, before any tool call:
no reading, no copying, no installing first.** It tells the user what
Reboot is and what they are about to see, so they know what to look
for. Only once it is sent does setup (stop 2) begin.

Say it in this shape, in plain words, under about 200 words:

1. **What Reboot is.** You describe your app as **domain objects**
   (a room, a reservation) and the **rules** they keep. Reboot keeps
   each object's state safe on its own, with no database to set up;
   runs one object's changes one at a time, so two people can't break
   a rule by acting at once; makes a change across several objects
   all-or-nothing; and pushes every change to every open page, live.
2. **What you'll see.** A finished app for a 56-room boutique hotel:
   the floor plan, the front desk and the staff roster, with real
   rules such as "a room is never booked twice". Then its whole
   architecture, drawn on a dashboard from the code, and every rule
   with the tests that prove it, including a video of one test driving
   the real page.
3. **What you'll do.** Make two changes: one to the code, which the
   tests prove, and one to a rule, which waits for your yes and is
   recorded with its reason.
4. **What to watch for,** three moments: two people can't take the
   last room; a rule, written in plain English, runs as a test; and a
   rule change needs your yes before any code.

Then show [`assets/note-from-ben.md`](assets/note-from-ben.md) word
for word, under the heading **A note from Ben**, without its HTML
comment. It is Ben Hindman's own note, Reboot's founder; never write,
reword or add to it.

Ask nothing: the user asked for the quickstart, so go straight on to
stop 2. Last line: setting up the hotel now, which takes a few
minutes the first time.

## Stop 2: set up (about 3 minutes)

Start the slow part first.

1. Copy `assets/hotel/` from this skill to `./maison-desk` in the
   current folder. If that already exists, use `./maison-desk-2`, then
   `-3`, and so on: never move, rename, overwrite or delete anything
   already in the user's folder. Then from the `app`
   skill's `assets/`: `scripts/model_diff.py`, `scripts/test.sh`,
   `scripts/release_record.py` and `tests/last_run.py`;
   `chmod +x scripts/test.sh`. Create an empty `.env`.
2. In the background, in order: `uv sync`, `uv run rbt generate`,
   `npm ci` in `frontend/`. Don't run the suite here: the hotel ships
   with its last run's browser recordings (`tests/*.recordings/`), so
   the dashboard shows the videos from the start. The suite runs where
   it teaches something, after each change.
3. Start the dashboard with the [`dashboard` skill](../dashboard/SKILL.md)
   as soon as `rbt generate` is done, and the app with the
   [`run` skill](../run/SKILL.md) once `npm ci` has finished. If port
   9991 or 5173 is taken by another app, don't stop that app: start
   this one with `rbt dev run --port=9781 --dashboard-port=9782` and
   the frontend with `PORT=5281 VITE_REBOOT_URL=http://localhost:9781`,
   and use those ports below.
4. While they run, say in one line what is still downloading and
   that it is the slowest part.

## Stop 3: the design (about 3 minutes)

Show the hotel's design document, `design/design.md` in the copied
hotel, in the chat as it is, with its links. If the dashboard started
on a port other than 9871, rewrite `127.0.0.1:9871` in the links to its
port as you show it. Then say in two lines how to read it: every object,
method, feature and rule is a link that opens the dashboard on exactly
that thing, and the next stops walk through it.

*Your turn:* open two links, an object and a rule.

*Taught:* the design is the app's map: what it keeps, what it does, the
rules it keeps, and who may do what.

## Stop 4: the app (about 3 minutes)

Open the floor plan (http://localhost:5173). *Your turn:* sign in as
**Esi** (front desk), open a room marked Dirty, and try to check a
guest in. It's refused: the room hasn't been cleaned and inspected.
Then open the **Front desk** page: today's arrivals and departures, and
what's left to sell.

*Taught:* this is a working app with real rules; next, where they live.

## Stop 5: the architecture (about 4 minutes)

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

## Stop 6: the rules and their proof (about 4 minutes)

Open [Features](<dash>/#/features/tests/reservations.feature). Each
feature file is a set of rules in plain English, and each rule has the
scenarios that prove it, run as tests.

- [A room type is never booked beyond the rooms the hotel has of it](<dash>/#/features/tests/reservations.feature/rules/1):
  open "The Penthouse booked twice for an overlapping night" and read
  its steps.
- [The person who cleaned a room cannot be the one who inspects it](<dash>/#/features/tests/room_status.feature/rules/3).
- [The hotel always keeps at least one manager](<dash>/#/features/tests/staff_roles.feature/rules/3).
- The three scenarios with a **VIDEO** badge drove the real page in a
  browser. Start with "A manager approves an early check-in on the
  front desk page", where a manager and the front desk are recorded
  side by side.

*Your turn:* play the video.

*Taught:* rules are the app's specification, and the scenarios under
each rule are its proof.

## Stop 7: who may call (about 2 minutes)

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

## Stop 8: a code change (about 3 minutes)

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

## Stop 9: a rule change (about 5 minutes)

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
   says: `design/design.md` gains the rule under its feature, linked to
   `reservations.feature/rules/2` (renumber the links of the rules after
   it), `design/decisions.md` an
   entry with the user's words, and `model_diff.py --accept` updates
   `design/accepted.json` and `design/accepted/`.
5. Show the new rule on the dashboard,
   [reservations rule 2](<dash>/#/features/tests/reservations.feature/rules/2),
   with its two passing scenarios, and the new decisions entry.

*Taught:* a rule changes only with the user's yes; the scenarios prove
it, and the decisions log keeps why.

## Stop 10: look inside (about 2 minutes)

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

## Stop 11: your app

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
