# Halcyon House: the design

Status: accepted on 2026-10-14.

## Brief

The front desk and housekeeping of Halcyon House, a 56-room boutique
hotel, share one floor plan on a desktop. It answers one question:
**which rooms can take a guest right now?**

## Domain model

- **Hotel:** one per property, id `hotel`. It holds the hotel's name and
  the ids of its 56 rooms as a plain list, because the building fixes
  the room count. Its one reader serves the whole floor plan.
- **Room:** one per room, keyed by room number. It holds the floor, the
  room type, the status (dirty, clean or occupied) and the guest. It is
  its own object because each room changes on its own, one change at a
  time, which is what stops two desks from checking guests into the
  same room at once.

## The review table

| Domain object | ID | Rule | Method | Kind | Who may call | Scenario |
| --- | --- | --- | --- | --- | --- | --- |
| `Room` | room number | A guest is checked in only to a clean room | `check_in` | Writer | anyone at the desk | "Checking a guest into a dirty room" |
| `Room` | room number | Check-out always sends the room back to dirty | `check_out` | Writer | anyone at the desk | "A guest checks out" |
| `Room` | room number | (housekeeping) | `mark_clean` | Writer | anyone at the desk | "A clean room takes its guest" |
| `Hotel` | `hotel` | (the floor plan) | `floor_plan` | Reader | anyone at the desk | "The floor plan shows every room in the hotel" |
| `Hotel` | `hotel` | (laying out the building) | `add_floor` | Transaction | the app itself | (seeded at start) |

## Pages

- `/`: the floor plan, floors by rooms, colored by status. A click opens
  the room: mark it clean, check a guest in or out.
