# Maison Desk — design

Status: features 1 (Rooms & housekeeping floor plan) and 2 (Reservations &
front desk) accepted on 2026-10-14.

## Brief

Hotel staff, on a desktop or tablet at the front desk and in the back
office, keep all 56 rooms of Maison Vingt-Trois moving through
occupied → dirty → being cleaned → clean → inspected → occupied. The main
page answers: which rooms can we sell or check into right now, and which
still need work? Accent: plum.

## Domain model

- **Room** (id = room number, 201–808): type, amenities, status, guest,
  who cleaned it, who last changed it. Its own object so each room's
  changes run one at a time.
- **Hotel** (id `hotel`): name and the list of its 56 room ids; serves
  the floor plan in one read.
- **Team** (id `team`): the staff roster — members with roles
  (manager, front desk, housekeeping, or none yet) and invitations.
- **User**: one per signed-in person; name and verified email from
  sign-in.
- **Reservation** (id = confirmation code, `MV-XXXXXX`): one stay —
  guest, room type, arrival, departure, status (booked, checked_in,
  checked_out, cancelled), room once given. Indexed by the Hotel in an
  OrderedMap keyed `<arrival>/<id>`.
- **Inventory** (one per room type): rooms booked per night; every
  booking of the type goes through it.
- **Room** also keeps the reservation id of the stay in it.

## Rules (feature 1)

- A room can be checked into only once it has been inspected.
- The person who cleaned a room cannot be the one who inspects it.
- Check-out always sends the room back to dirty.
- Out of order needs a reason; a room returns to service dirty.
- Housekeeping cleans and inspects; the front desk checks in and out;
  managers do all of it and put rooms out of order.
- An invitation is taken up only by a verified address; only managers
  assign roles; the hotel always keeps at least one manager.

## Rules (feature 2)

- A room type is never booked beyond the rooms the hotel has of it, on
  any night (the departure night is not counted).
- A cancelled booking frees its nights.
- A guest is checked in only to an inspected room of the type they
  booked.

## Rules (early check-in)

- Check-in opens at 3 pm hotel time (the computer's own time zone) on arrival day.
  Before then a booked guest is checked in only once a manager approves
  an early check-in on the reservation, or by a manager, whose check-in
  records the approval.
- Before 3 pm a walk-in is checked in only by a manager; only the
  hotel's own check-in may tie a room to a reservation.

## Pages

- `/` — floor plan: floors × rooms colored by status, status tiles that
  filter, search and type filters, a drawer per room with the actions
  the viewer's role allows.
- `/front-desk` — a day's arrivals (assign a ready room, check in),
  departures (check out), rooms left per type for 14 nights, new
  booking, the next 14 days of bookings (cancel).
- `/staff` — the roster; managers assign roles and invite.

## Features, in build order

1. Rooms & housekeeping floor plan — **accepted**
2. Reservations & front desk — **accepted**
3. Amenity bookings — next
4. Guest profiles & preferences
5. Concierge requests
6. Folio & billing
