# Maison Desk: the design

Status: accepted on 2026-10-15. Every object, method, feature and rule
below links to the developer dashboard, which draws them from the code.

## Brief

Hotel staff, on a desktop or tablet at the front desk and in the back
office, keep the 56 rooms of Maison Vingt-Trois moving through
*occupied → dirty → being cleaned → clean → inspected → occupied*, and
book the stays that fill them. The main page answers one question:
**which rooms can we sell or check a guest into right now?** The
accent is plum.

## Architecture: four packages

The API is split into four packages, layered so that none imports
another in a circle ([see them on the dashboard](http://127.0.0.1:9871/#/models)):

| Package | Objects | Imports from |
| --- | --- | --- |
| `rooms.v1` | [Room](http://127.0.0.1:9871/#/models?type=rooms.v1.Room) | nothing |
| `reservations.v1` | [Reservation](http://127.0.0.1:9871/#/models?type=reservations.v1.Reservation), [Inventory](http://127.0.0.1:9871/#/models?type=reservations.v1.Inventory) | nothing |
| `staff.v1` | [Team](http://127.0.0.1:9871/#/models?type=staff.v1.Team), [User](http://127.0.0.1:9871/#/models?type=staff.v1.User) | nothing |
| `hotel.v1` | [Hotel](http://127.0.0.1:9871/#/models?type=hotel.v1.Hotel) | rooms, reservations |

The Hotel sits on top: it is the property, and its methods join rooms
and reservations for the floor plan and the front desk.

## Domain model

- **[Room](http://127.0.0.1:9871/#/models?type=rooms.v1.Room):** one per room, keyed by its number (201 to
  808). It holds the type, amenities, status, the guest, and who cleaned
  it. It is its own object because each room changes on its own, and
  Reboot runs one room's changes one at a time, so two desks can't put
  guests into the same room.
- **[Reservation](http://127.0.0.1:9871/#/models?type=reservations.v1.Reservation):** one per stay, keyed by its
  confirmation code (`MV-…`). It holds the guest, room type, dates,
  status, and the room once given.
- **[Inventory](http://127.0.0.1:9871/#/models?type=reservations.v1.Inventory):** one per room type. It counts
  the rooms booked each night, and every booking of that type goes
  through it, which is what keeps a type from being overbooked.
- **[Hotel](http://127.0.0.1:9871/#/models?type=hotel.v1.Hotel):** one per property, id `hotel`. It holds
  the room ids and an ordered index of reservations by arrival date,
  and serves the floor plan and the front desk in one read each.
- **[Team](http://127.0.0.1:9871/#/models?type=staff.v1.Team):** the staff roster, id `team`: each member's
  role (manager, front desk, housekeeping) and open invitations. Roles
  live only here, so nobody can promote themselves.
- **[User](http://127.0.0.1:9871/#/models?type=staff.v1.User):** one per signed-in person, with their name
  and verified email from sign-in.

## Features and their rules

[Staff keep every room moving from check-out to the next guest](http://127.0.0.1:9871/#/features/tests/room_status.feature)
- [A room can be checked into only once it has been inspected](http://127.0.0.1:9871/#/features/tests/room_status.feature/rules/1)
- [A walk-in is checked in before 3 pm only by a manager](http://127.0.0.1:9871/#/features/tests/room_status.feature/rules/2)
- [The person who cleaned a room cannot be the one who inspects it](http://127.0.0.1:9871/#/features/tests/room_status.feature/rules/3)
- [Check-out always sends the room back to dirty](http://127.0.0.1:9871/#/features/tests/room_status.feature/rules/4)
- [A room out of order needs a reason, and comes back into service dirty](http://127.0.0.1:9871/#/features/tests/room_status.feature/rules/5)
- [Each role does only its own part of the work](http://127.0.0.1:9871/#/features/tests/room_status.feature/rules/6)

[The front desk books stays and checks guests in and out](http://127.0.0.1:9871/#/features/tests/reservations.feature)
- [A room type is never booked beyond the rooms the hotel has of it](http://127.0.0.1:9871/#/features/tests/reservations.feature/rules/1)
- [A cancelled booking frees its nights](http://127.0.0.1:9871/#/features/tests/reservations.feature/rules/2)
- [A guest is checked in only to an inspected room of the type they booked](http://127.0.0.1:9871/#/features/tests/reservations.feature/rules/3)
- [A guest is checked in before 3 pm only with a manager's approval](http://127.0.0.1:9871/#/features/tests/reservations.feature/rules/4)

[Managers decide what each member of staff may do](http://127.0.0.1:9871/#/features/tests/staff_roles.feature)
- [An invitation is taken up only by a verified address](http://127.0.0.1:9871/#/features/tests/staff_roles.feature/rules/1)
- [Only a manager gives out roles](http://127.0.0.1:9871/#/features/tests/staff_roles.feature/rules/2)
- [The hotel always keeps at least one manager](http://127.0.0.1:9871/#/features/tests/staff_roles.feature/rules/3)

Each rule's scenarios run as the test suite: 41 in all, three of them
driving the real page in a browser, with videos on the dashboard.

## Methods

Kinds: a **Reader** changes nothing; a **Writer** changes its own
object, one change at a time; a **Transaction** changes several
objects, all or nothing.

**[Hotel](http://127.0.0.1:9871/#/models?type=hotel.v1.Hotel)**

| Method | Kind | Who may call |
| --- | --- | --- |
| [`create`](http://127.0.0.1:9871/#/models?type=hotel.v1.Hotel.create) | Writer | the app |
| [`add_floor`](http://127.0.0.1:9871/#/models?type=hotel.v1.Hotel.add_floor) | Transaction | the app |
| [`floor_plan`](http://127.0.0.1:9871/#/models?type=hotel.v1.Hotel.floor_plan) | Reader | staff |
| [`setup_front_desk`](http://127.0.0.1:9871/#/models?type=hotel.v1.Hotel.setup_front_desk) | Transaction | the app |
| [`add_bookings`](http://127.0.0.1:9871/#/models?type=hotel.v1.Hotel.add_bookings) | Transaction | the app |
| [`book`](http://127.0.0.1:9871/#/models?type=hotel.v1.Hotel.book) | Transaction | front desk, managers |
| [`cancel_booking`](http://127.0.0.1:9871/#/models?type=hotel.v1.Hotel.cancel_booking) | Transaction | front desk, managers |
| [`check_in_booking`](http://127.0.0.1:9871/#/models?type=hotel.v1.Hotel.check_in_booking) | Transaction | front desk, managers |
| [`check_out_room`](http://127.0.0.1:9871/#/models?type=hotel.v1.Hotel.check_out_room) | Transaction | front desk, managers |
| [`front_desk`](http://127.0.0.1:9871/#/models?type=hotel.v1.Hotel.front_desk) | Reader | staff |

**[Room](http://127.0.0.1:9871/#/models?type=rooms.v1.Room)**

| Method | Kind | Who may call |
| --- | --- | --- |
| [`create`](http://127.0.0.1:9871/#/models?type=rooms.v1.Room.create) | Writer | the app |
| [`get`](http://127.0.0.1:9871/#/models?type=rooms.v1.Room.get) | Reader | staff |
| [`start_cleaning`](http://127.0.0.1:9871/#/models?type=rooms.v1.Room.start_cleaning) | Writer | housekeeping, managers |
| [`mark_clean`](http://127.0.0.1:9871/#/models?type=rooms.v1.Room.mark_clean) | Writer | housekeeping, managers |
| [`inspect_room`](http://127.0.0.1:9871/#/models?type=rooms.v1.Room.inspect_room) | Writer | housekeeping, managers |
| [`check_in`](http://127.0.0.1:9871/#/models?type=rooms.v1.Room.check_in) | Writer | front desk, managers (walk-ins) |
| [`check_out`](http://127.0.0.1:9871/#/models?type=rooms.v1.Room.check_out) | Writer | front desk, managers |
| [`take_out_of_order`](http://127.0.0.1:9871/#/models?type=rooms.v1.Room.take_out_of_order) | Writer | managers |
| [`return_to_service`](http://127.0.0.1:9871/#/models?type=rooms.v1.Room.return_to_service) | Writer | managers |

**[Reservation](http://127.0.0.1:9871/#/models?type=reservations.v1.Reservation)** and **[Inventory](http://127.0.0.1:9871/#/models?type=reservations.v1.Inventory)**

| Method | Kind | Who may call |
| --- | --- | --- |
| [`create`](http://127.0.0.1:9871/#/models?type=reservations.v1.Reservation.create) | Writer | the app |
| [`get`](http://127.0.0.1:9871/#/models?type=reservations.v1.Reservation.get) | Reader | staff |
| [`mark_checked_in`](http://127.0.0.1:9871/#/models?type=reservations.v1.Reservation.mark_checked_in) | Writer | the app |
| [`approve_early_check_in`](http://127.0.0.1:9871/#/models?type=reservations.v1.Reservation.approve_early_check_in) | Writer | managers |
| [`mark_checked_out`](http://127.0.0.1:9871/#/models?type=reservations.v1.Reservation.mark_checked_out) | Writer | the app |
| [`mark_cancelled`](http://127.0.0.1:9871/#/models?type=reservations.v1.Reservation.mark_cancelled) | Writer | the app |

| Method | Kind | Who may call |
| --- | --- | --- |
| [`create`](http://127.0.0.1:9871/#/models?type=reservations.v1.Inventory.create) | Writer | the app |
| [`reserve`](http://127.0.0.1:9871/#/models?type=reservations.v1.Inventory.reserve) | Writer | the app |
| [`release`](http://127.0.0.1:9871/#/models?type=reservations.v1.Inventory.release) | Writer | the app |
| [`availability`](http://127.0.0.1:9871/#/models?type=reservations.v1.Inventory.availability) | Reader | staff |

**[Team](http://127.0.0.1:9871/#/models?type=staff.v1.Team)** and **[User](http://127.0.0.1:9871/#/models?type=staff.v1.User)**

| Method | Kind | Who may call |
| --- | --- | --- |
| [`create`](http://127.0.0.1:9871/#/models?type=staff.v1.Team.create) | Writer | the app |
| [`my_role`](http://127.0.0.1:9871/#/models?type=staff.v1.Team.my_role) | Reader | anyone signed in |
| [`member_of`](http://127.0.0.1:9871/#/models?type=staff.v1.Team.member_of) | Reader | the app |
| [`members`](http://127.0.0.1:9871/#/models?type=staff.v1.Team.members) | Reader | staff |
| [`register`](http://127.0.0.1:9871/#/models?type=staff.v1.Team.register) | Writer | the app |
| [`invite`](http://127.0.0.1:9871/#/models?type=staff.v1.Team.invite) | Writer | managers |
| [`set_role`](http://127.0.0.1:9871/#/models?type=staff.v1.Team.set_role) | Writer | managers |

| Method | Kind | Who may call |
| --- | --- | --- |
| [`profile`](http://127.0.0.1:9871/#/models?type=staff.v1.User.profile) | Reader | the user themselves |

## Pages

- `/`: the floor plan. Floors by rooms, colored by status; a click opens
  the room, with the actions the viewer's role allows.
- `/front-desk`: a day's arrivals and departures, rooms left per type
  for 14 nights, new bookings, and the next 14 days of stays.
- `/staff`: the roster; managers give out roles and invite.

## Sign-in

Staff sign in with Reboot's built-in sign-in: the development picker
locally (Alice manages, Esi is on the front desk, Carlos and Dani are
housekeeping), a real provider at deploy. Someone signed in with no
role can look but change nothing.

## Decisions

Why the design is what it is, and what was assumed, is in
[`decisions.md`](decisions.md). The design as accepted is copied to
`accepted/`; `python3 scripts/model_diff.py` lists anything changed
since.
