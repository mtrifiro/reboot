## 2026-10-14: Design accepted: Rooms on one floor plan

- **Decided by the build:** each Room is its own domain object, keyed by
  its number; `check_in`, `check_out` and `mark_clean` are Writers on it.
- **Why:** a Writer on one Room runs one at a time, so two desks can't
  check guests into the same room at once.
- **Decided by the build:** the Hotel holds its room ids as a plain list,
  and `add_floor` lays out each floor in one Transaction.
- **Why:** the building fixes the room count; a floor is created
  completely or not at all.
- **Set aside:** rooms as a list inside the Hotel: every check-in would
  wait on every other.
- **Assumed:** 56 rooms on floors 2 to 8, eight to a floor; no sign-in,
  so anyone at the desk may use the app. Nobody was asked; check these
  first.
- **Left open:** who signs in and with which roles; reservations,
  amenities and billing, not built.
- **The user's words:** none. This hotel was prepared for the
  quickstart.
- **Replaces:** nothing (first design).
