Feature: The front desk checks guests into rooms that are ready
  Halcyon House has 56 rooms on floors 2 to 8. Each room moves from
  dirty to clean to occupied and back to dirty when the guest leaves.
  The front desk and housekeeping share one live floor plan, so a guest
  is only ever handed the key to a room that is ready.

  Background:
    Given the application is up
    And "desk" is an unauthenticated user

  Scenario: The floor plan shows every room in the hotel
    Then as "desk", `floor_plan` on the `Hotel` for "hotel" has `rooms` of length `56`
    And as "desk", `floor_plan` on the `Hotel` for "hotel" has `rooms[0].number="201"` and `rooms[55].number="808"` and `rooms[55].room_type="Penthouse"`

  Rule: A guest is checked in only to a clean room
    A guest never walks into a room housekeeping hasn't finished.

    Scenario: Checking a guest into a dirty room
      When "desk" attempts a `check_in` with `guest_name="Mme. Laurent"` on `Room` of "201"
      Then the attempt aborts with `RoomNotReadyError` with `status="dirty"`
      And as "desk", `get` on the `Room` for "201" has `room.status="dirty"` and `room.guest_name=""`

    Scenario: A clean room takes its guest
      Given "desk" does a `mark_clean` on `Room` of "201"
      When "desk" does a `check_in` with `guest_name="Mme. Laurent"` on `Room` of "201"
      Then as "desk", `get` on the `Room` for "201" has `room.status="occupied"` and `room.guest_name="Mme. Laurent"`

    Scenario: A room with a guest in it can't take a second one
      Given "desk" does a `mark_clean` on `Room` of "201"
      And "desk" does a `check_in` with `guest_name="Mme. Laurent"` on `Room` of "201"
      When "desk" attempts a `check_in` with `guest_name="Mr. Okafor"` on `Room` of "201"
      Then the attempt aborts with `RoomNotReadyError` with `status="occupied"`

  Rule: Check-out always sends the room back to dirty
    Housekeeping cleans every room between guests.

    Scenario: A guest checks out
      Given "desk" does a `mark_clean` on `Room` of "201"
      And "desk" does a `check_in` with `guest_name="Mme. Laurent"` on `Room` of "201"
      When "desk" does a `check_out` on `Room` of "201"
      Then as "desk", `get` on the `Room` for "201" has `room.status="dirty"` and `room.guest_name=""`

    Scenario: A dirty room can't be checked into again until it is cleaned
      Given "desk" does a `mark_clean` on `Room` of "201"
      And "desk" does a `check_in` with `guest_name="Mme. Laurent"` on `Room` of "201"
      And "desk" does a `check_out` on `Room` of "201"
      When "desk" attempts a `check_in` with `guest_name="Mr. Okafor"` on `Room` of "201"
      Then the attempt aborts with `RoomNotReadyError` with `status="dirty"`
