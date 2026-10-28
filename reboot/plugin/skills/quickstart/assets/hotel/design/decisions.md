## 2026-10-14: Design accepted: Rooms & housekeeping floor plan

- **Decided by you:** build one feature at a time; staff only, with
  roles (front desk, housekeeping, manager); a realistic room mix picked
  for you.
- **Why:** the answers to the scope questions.
- **Decided by the build:** each Room is its own domain object keyed by
  its number, with one Writer per status change.
- **Why:** each room's changes then run one at a time, so two people
  can't check guests into the same room, and a refused step rolls back.
- **Decided by the build:** Hotel holds its room ids as a plain list and
  serves the whole floor plan from one reader.
- **Why:** the building fixes the count at 56; one subscription keeps
  the page's totals consistent as rooms change.
- **Decided by the build:** roles live only on the Team roster; a role
  table per Room method decides who may call it.
- **Why:** nobody can promote themselves; the table is the whole
  permission story in one place.
- **Decided by the build:** the cleaner may not inspect their own room;
  a "being cleaned" step; unassigned staff may look but not act.
- **Why:** a second pair of eyes at this level of service; the board
  shows work in progress; sign-in alone grants no power.
- **Set aside:** rooms as a list inside Hotel — every change would lock
  the whole hotel.
- **Assumed:** hotel name "Maison Vingt-Trois", app name "Maison Desk",
  plum accent; floors 2–8, eight rooms each (20 Deluxe King, 8 Deluxe
  Twin, 18 Junior Suites, 9 Suites, Penthouse 808); the amenity lists;
  the demo afternoon's statuses and guest names. Nobody was asked; check
  these first.
- **Left open:** the production sign-in provider and the
  ADMIN_EMAILS / ALLOWED_EMAIL_DOMAINS allowlist, at deploy; features
  2–6, not built yet.
- **The user's words:** "One feature at a time" (how to build); "Staff
  only, with roles" (who signs in); "I'll pick a realistic mix" (room
  layout); "Keep going" (review); "Reservations & front desk" (what
  next).
- **Replaces:** nothing (first design).

## 2026-10-14: Design accepted: Reservations & front desk

- **Decided by you:** book by room type and assign the room at check-in;
  no rates until Folio & billing; changes straight onto main.
- **Why:** the answers to the feature's questions.
- **Decided by the build:** Reservation is its own domain object, its id
  the guest's confirmation code; the Hotel indexes reservations in an
  OrderedMap keyed by arrival date.
- **Why:** each stay has its own lifecycle; bookings accumulate without
  bound and the front desk reads them by date range.
- **Decided by the build:** one Inventory per room type counts booked
  nights; `Hotel.book` reserves through it before the Reservation exists.
- **Why:** one object per type serializes every booking of that type,
  so no night is sold beyond its rooms, while bookings of different
  types run side by side.
- **Decided by the build:** check-in and check-out of booked guests are
  Hotel transactions over the Room and the Reservation together; the
  floor plan's check-out uses the same one.
- **Why:** the room and the stay change together or not at all.
- **Assumed:** the departure night isn't counted; stays of at most 60
  nights; "today" is the browser's local date; the demo bookings and
  guest names. Nobody was asked; check these first.
- **Left open:** walk-ins checked in from the floor plan don't count
  against bookings; check-in isn't held to the arrival date; the
  hotel's time zone.
- **The user's words:** "Yes, build it" (the feature); "Not yet, with
  billing" (rates); "Straight onto main" (workflow); "Keep going"
  (review); next: "sort the room list by room number".
- **Replaces:** nothing.

## 2026-10-14: Design accepted: Early check-in needs a manager

- **Decided by you:** no check-in before 3 pm unless a manager approves;
  approval is a step on the reservation, after which the front desk
  checks the guest in; a manager checking in early counts as approving;
  hotel time is Europe/Paris; walk-ins follow the rule too.
- **Why:** your request and the answers to its questions.
- **Decided by the build:** the approval lives on Reservation
  (`approve_early_check_in`, managers only, booked stays only); the 3 pm
  check sits in `Hotel.check_in_booking` and, for walk-ins, in
  `Room.check_in`; a check-in from outside the app may not carry a
  reservation id.
- **Why:** the approval belongs to the stay; the hotel's check-in is the
  one path for booked guests, so the walk-in path must not be a way
  around it.
- **Decided by the build:** the time comes from one `clock` module the
  tests patch; the page works out "early" in the browser from the
  hotel's time zone and check-in time.
- **Why:** scenarios can be run at any hour; the page changes at 3 pm
  without a reload.
- **Assumed:** check-in time 15:00 and the zone are constants in code,
  not settings a manager can change.
- **Left open:** a setting for the check-in hour; Reboot 1.6.0 treats
  a reworded method description as incompatible, so descriptions
  should be final before production data exists.
- **The user's words:** "Guests can't be checked in before 3 pm unless a
  manager approves an early check-in"; "Yes, as described";
  "Europe/Paris"; "Yes, walk-ins too"; "Keep going" (review); next: no
  preference.
- **Replaces:** nothing; adds to "Reservations & front desk".

## 2026-10-14: Design accepted: Four packages, and the hotel's own time zone

- **Decided by the build:** the API in four packages, layered so none
  imports another in a circle: `rooms.v1` (Room), `reservations.v1`
  (Reservation, Inventory) and `staff.v1` (Team, User) import nothing
  else; `hotel.v1` (Hotel) sits on top and imports rooms and
  reservations.
- **Why:** the dashboard's Models page groups the architecture by
  package, so each area reads on its own and the Hotel's calls between
  them show as the joins.
- **Decided by the build:** `hotel.v1` keeps its own copy of the six
  errors its methods pass on, with the same names and fields.
- **Why:** Reboot 1.6.0 can't declare an error from another package on
  a method (reboot#258).
- **Decided by the build:** the hotel's time zone is the computer's own
  (or `HOTEL_TIME_ZONE` when set), not Europe/Paris.
- **Why:** a time such as 3 pm is in the user's own time zone unless
  they say otherwise.
- **Assumed:** nothing new.
- **Left open:** as before.
- **The user's words:** none; prepared for the quickstart.
- **Replaces:** "Early check-in needs a manager", its "hotel time is
  Europe/Paris" only.

## 2026-10-15: Design accepted: Rush cleaning

- **Decided by you:** the front desk can rush a vacant room of a booked
  arrival's type that is still dirty or awaiting inspection, so the
  guest waits briefly instead of taking another type; housekeeping sees
  it first; it is held for that guest until they check in or the rush
  is cancelled; front desk and managers only.
- **Why:** built in the hotel-23 session, then accepted as a whole.
- **Decided by the build:** the rush lives on the Room (`mark_rush`,
  `clear_rush`, called only by the app) and is echoed on the
  Reservation (`mark_rush_room`); `Hotel.rush_room` and `cancel_rush`
  change both together, as Transactions; a guest has one rushed room at
  a time, and rushing another moves it.
- **Why:** the room is what housekeeping and check-in act on; the stay
  needs to know which room it is waiting for; the two must never
  disagree.
- **Decided by the build:** `hotel.v1` keeps its own copies of
  `RoomHeldError` and `RoomNotRushableError`.
- **Why:** reboot#258.
- **Assumed:** a rush never skips cleaning or inspection.
- **Left open:** nothing new.
- **The user's words:** "accept the design" (2026-10-15).
- **Replaces:** nothing; adds to "Reservations & front desk".

## 2026-10-15: Design accepted: Rush cleaning backed out

- **Decided by you:** take rush cleaning out of the app entirely.
- **Why:** it made the call graph harder to read: 5 more methods and 15
  more calls between objects (34 to 49), most of them the same three
  calls repeated wherever a rush ends, because the rush was recorded on
  both the Room and the Reservation.
- **Decided by the build:** a revert of the feature's code and its part
  of `design.md`; the floor plan keeps printing each room's status on
  its card, with the guest on a line of its own, which came in with the
  same commit but was asked for separately.
- **Why:** that change is about the floor plan, not the rush.
- **Assumed:** nothing.
- **Left open:** a rush done again, if wanted, recorded only on the
  Room so ending one is a single call.
- **The user's words:** "back out the rush functionality" (2026-10-15).
- **Replaces:** "Rush cleaning".
