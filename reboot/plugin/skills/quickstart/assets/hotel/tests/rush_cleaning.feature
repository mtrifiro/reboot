Feature: The front desk asks housekeeping to rush a room for a guest who will wait
  When an arriving guest's room type has no inspected room, but one of
  that type is vacant and still dirty or awaiting inspection, the front
  desk can offer the guest a short wait and rush that room for them.
  Housekeeping sees the rushed room flagged first on the floor plan with
  the guest's name, cleans and inspects it, and the front desk checks the
  guest into it. Only the front desk and managers rush a room, only for a
  booked arrival, and a rush lasts until the guest checks in or the rush
  is cancelled.

  Background:
    Given the application is up
    And "alice" signs in as "alice@maison.test", verified yes
    And "alice" does an `invite` with `email="fiona@maison.test"` and `role="front_desk"` on `Team` of "team"
    And "alice" does an `invite` with `email="hugo@maison.test"` and `role="housekeeping"` on `Team` of "team"
    And "alice" does an `invite` with `email="ines@maison.test"` and `role="housekeeping"` on `Team` of "team"
    And "fiona" signs in as "fiona@maison.test", verified yes
    And "hugo" signs in as "hugo@maison.test", verified yes
    And "ines" signs in as "ines@maison.test", verified yes

  @wip
  Scenario: The front desk rushes a dirty room for a guest who will wait
    Given "fiona" does a `book` with `guest_name="Dr. Aoki"` and `room_type="Deluxe King"` and `arrival="2027-03-01"` and `departure="2027-03-05"` on `Hotel` of "hotel"
    And the resulting `reservation_id` is saved as "stay"
    When "fiona" does a `rush_room` with `reservation_id=<stay>` and `room_number="202"` on `Hotel` of "hotel"
    Then as "hugo", `get` on the `Room` for "202" has `room.status="vacant_dirty"` and `room.rush_guest_name="Dr. Aoki"` and `room.rush_requested_by_name="Fiona"`
    And as "fiona", `get` on the `Reservation` for "<stay>" has `reservation.rush_room_number="202"`
    And as "fiona", `front_desk` with `date="2027-03-01"` on the `Hotel` for "hotel" has `arrivals[0].rush_room_number="202"`

  @wip
  Scenario: A room awaiting inspection is rushed
    Given "fiona" does a `book` with `guest_name="Dr. Aoki"` and `room_type="Deluxe King"` and `arrival="2027-03-01"` and `departure="2027-03-05"` on `Hotel` of "hotel"
    And the resulting `reservation_id` is saved as "stay"
    And "hugo" does a `start_cleaning` on `Room` of "202"
    And "hugo" does a `mark_clean` on `Room` of "202"
    When "fiona" does a `rush_room` with `reservation_id=<stay>` and `room_number="202"` on `Hotel` of "hotel"
    Then as "fiona", `get` on the `Room` for "202" has `room.status="vacant_clean"` and `room.rush_guest_name="Dr. Aoki"`

  @wip
  Scenario: Housekeeping tries to rush a room
    Given "fiona" does a `book` with `guest_name="Dr. Aoki"` and `room_type="Deluxe King"` and `arrival="2027-03-01"` and `departure="2027-03-05"` on `Hotel` of "hotel"
    And the resulting `reservation_id` is saved as "stay"
    When "hugo" attempts a `rush_room` with `reservation_id=<stay>` and `room_number="202"` on `Hotel` of "hotel"
    Then the attempt aborts with `PermissionDenied`

  @wip
  Scenario: Rushing an occupied room
    Given "fiona" does a `book` with `guest_name="Dr. Aoki"` and `room_type="Deluxe King"` and `arrival="2027-03-01"` and `departure="2027-03-05"` on `Hotel` of "hotel"
    And the resulting `reservation_id` is saved as "stay"
    And "hugo" does a `start_cleaning` on `Room` of "201"
    And "hugo" does a `mark_clean` on `Room` of "201"
    And "ines" does an `inspect_room` on `Room` of "201"
    And "fiona" does a `check_in` with `guest_name="Mr. Arden"` on `Room` of "201"
    When "fiona" attempts a `rush_room` with `reservation_id=<stay>` and `room_number="201"` on `Hotel` of "hotel"
    Then the attempt aborts with `RoomNotRushableError` with `status="occupied"`

  @wip
  Scenario: Rushing a Junior Suite for a Deluxe King guest
    Given "fiona" does a `book` with `guest_name="Dr. Aoki"` and `room_type="Deluxe King"` and `arrival="2027-03-01"` and `departure="2027-03-05"` on `Hotel` of "hotel"
    And the resulting `reservation_id` is saved as "stay"
    When "fiona" attempts a `rush_room` with `reservation_id=<stay>` and `room_number="208"` on `Hotel` of "hotel"
    Then the attempt aborts with `WrongRoomTypeError` with `booked="Deluxe King"` and `room_type="Junior Suite"`

  @wip
  Scenario: Rushing a second room moves the rush
    Given "fiona" does a `book` with `guest_name="Dr. Aoki"` and `room_type="Deluxe King"` and `arrival="2027-03-01"` and `departure="2027-03-05"` on `Hotel` of "hotel"
    And the resulting `reservation_id` is saved as "stay"
    And "fiona" does a `rush_room` with `reservation_id=<stay>` and `room_number="202"` on `Hotel` of "hotel"
    When "fiona" does a `rush_room` with `reservation_id=<stay>` and `room_number="203"` on `Hotel` of "hotel"
    Then as "fiona", `get` on the `Room` for "202" has `room.rush_reservation_id=""`
    And as "fiona", `get` on the `Room` for "203" has `room.rush_guest_name="Dr. Aoki"`
    And as "fiona", `get` on the `Reservation` for "<stay>" has `reservation.rush_room_number="203"`

  @wip
  Scenario: The guest gives up waiting
    Given "fiona" does a `book` with `guest_name="Dr. Aoki"` and `room_type="Deluxe King"` and `arrival="2027-03-01"` and `departure="2027-03-05"` on `Hotel` of "hotel"
    And the resulting `reservation_id` is saved as "stay"
    And "fiona" does a `rush_room` with `reservation_id=<stay>` and `room_number="202"` on `Hotel` of "hotel"
    When "fiona" does a `cancel_rush` with `reservation_id=<stay>` on `Hotel` of "hotel"
    Then as "fiona", `get` on the `Room` for "202" has `room.rush_reservation_id=""` and `room.rush_guest_name=""`
    And as "fiona", `get` on the `Reservation` for "<stay>" has `reservation.rush_room_number=""`

  @wip
  Scenario: A cancelled booking frees its rushed room
    Given "fiona" does a `book` with `guest_name="Dr. Aoki"` and `room_type="Deluxe King"` and `arrival="2027-03-01"` and `departure="2027-03-05"` on `Hotel` of "hotel"
    And the resulting `reservation_id` is saved as "stay"
    And "fiona" does a `rush_room` with `reservation_id=<stay>` and `room_number="202"` on `Hotel` of "hotel"
    When "fiona" does a `cancel_booking` with `reservation_id=<stay>` on `Hotel` of "hotel"
    Then as "fiona", `get` on the `Room` for "202" has `room.rush_reservation_id=""`

  @wip
  Scenario: The front desk rushes a room on the front desk page and checks the guest in once it is ready
    Given "fiona" does a `book` with `guest_name="Dr. Aoki"` and `room_type="Deluxe King"` and `arrival="2027-03-01"` and `departure="2027-03-05"` on `Hotel` of "hotel"
    And the resulting `reservation_id` is saved as "stay"
    When "fiona" opens the web app at "/front-desk"
    And "fiona" fills "Day" in the web app with `"2027-03-01"`
    Then "fiona" eventually sees "No Deluxe King inspected yet" in the "Arrivals" table in the web app within 10 seconds
    When "fiona" selects "202 · Dirty" in "Room to rush for Dr. Aoki" in the web app
    And "fiona" clicks the "Rush room for Dr. Aoki" button in the web app
    Then "fiona" eventually sees "Waiting on 202" in the "Arrivals" table in the web app within 10 seconds
    And as "fiona", `get` on the `Room` for "202" has `room.rush_guest_name="Dr. Aoki"`
    When "hugo" does a `start_cleaning` on `Room` of "202"
    And "hugo" does a `mark_clean` on `Room` of "202"
    And "ines" does an `inspect_room` on `Room` of "202"
    And "fiona" clicks the "Check in Dr. Aoki" button in the web app
    Then "fiona" eventually sees "Dr. Aoki is in room 202." in the web app within 10 seconds
    And as "fiona", `get` on the `Room` for "202" has `room.status="occupied"` and `room.guest_name="Dr. Aoki"` and `room.rush_reservation_id=""`

  @wip
  Scenario: Housekeeping sees the rushed room first on the floor plan
    Given "fiona" does a `book` with `guest_name="Dr. Aoki"` and `room_type="Deluxe King"` and `arrival="2027-03-01"` and `departure="2027-03-05"` on `Hotel` of "hotel"
    And the resulting `reservation_id` is saved as "stay"
    And "fiona" does a `rush_room` with `reservation_id=<stay>` and `room_number="202"` on `Hotel` of "hotel"
    When "hugo" opens the web app at "/"
    Then "hugo" eventually sees "Dr. Aoki" in the "Rushed rooms" table in the web app within 10 seconds

  @wip
  Rule: A rush skips no step
    A rushed room is still cleaned and then inspected by a second person
    before its guest is checked in; the rush changes what housekeeping
    does first, not what ready means.

    Scenario: Checking a guest into the room rushed for them while it is still dirty
      Given "fiona" does a `book` with `guest_name="Dr. Aoki"` and `room_type="Deluxe King"` and `arrival="2027-03-01"` and `departure="2027-03-05"` on `Hotel` of "hotel"
      And the resulting `reservation_id` is saved as "stay"
      And "fiona" does a `rush_room` with `reservation_id=<stay>` and `room_number="202"` on `Hotel` of "hotel"
      When "fiona" attempts a `check_in_booking` with `reservation_id=<stay>` and `room_number="202"` on `Hotel` of "hotel"
      Then the attempt aborts with `RoomNotReadyError` with `status="vacant_dirty"`

    Scenario: The rushed room, cleaned and inspected, takes its guest
      Given "fiona" does a `book` with `guest_name="Dr. Aoki"` and `room_type="Deluxe King"` and `arrival="2027-03-01"` and `departure="2027-03-05"` on `Hotel` of "hotel"
      And the resulting `reservation_id` is saved as "stay"
      And "fiona" does a `rush_room` with `reservation_id=<stay>` and `room_number="202"` on `Hotel` of "hotel"
      And "hugo" does a `start_cleaning` on `Room` of "202"
      And "hugo" does a `mark_clean` on `Room` of "202"
      And "ines" does an `inspect_room` on `Room` of "202"
      When "fiona" does a `check_in_booking` with `reservation_id=<stay>` and `room_number="202"` on `Hotel` of "hotel"
      Then as "fiona", `get` on the `Room` for "202" has `room.status="occupied"` and `room.guest_name="Dr. Aoki"` and `room.rush_reservation_id=""`
      And as "fiona", `get` on the `Reservation` for "<stay>" has `reservation.status="checked_in"` and `reservation.rush_room_number=""`

  @wip
  Rule: A rushed room is held for its guest
    Until its guest checks in or the rush is cancelled, no other arrival
    or walk-in is checked into it.

    Background:
      Given "fiona" does a `book` with `guest_name="Dr. Aoki"` and `room_type="Deluxe King"` and `arrival="2027-03-01"` and `departure="2027-03-05"` on `Hotel` of "hotel"
      And the resulting `reservation_id` is saved as "stay"
      And "fiona" does a `rush_room` with `reservation_id=<stay>` and `room_number="202"` on `Hotel` of "hotel"

    Scenario: Another arriving guest given the rushed room once it is ready
      Given "fiona" does a `book` with `guest_name="Mr. Okafor"` and `room_type="Deluxe King"` and `arrival="2027-03-01"` and `departure="2027-03-02"` on `Hotel` of "hotel"
      And the resulting `reservation_id` is saved as "other stay"
      And "hugo" does a `start_cleaning` on `Room` of "202"
      And "hugo" does a `mark_clean` on `Room` of "202"
      And "ines" does an `inspect_room` on `Room` of "202"
      When "fiona" attempts a `check_in_booking` with `reservation_id=<other stay>` and `room_number="202"` on `Hotel` of "hotel"
      Then the attempt aborts with `RoomHeldError` with `guest_name="Dr. Aoki"`
      And as "fiona", `get` on the `Room` for "202" has `room.status="inspected"`

    Scenario: A walk-in given the rushed room once it is ready
      Given "hugo" does a `start_cleaning` on `Room` of "202"
      And "hugo" does a `mark_clean` on `Room` of "202"
      And "ines" does an `inspect_room` on `Room` of "202"
      When "fiona" attempts a `check_in` with `guest_name="Mr. Arden"` on `Room` of "202"
      Then the attempt aborts with `RoomHeldError` with `guest_name="Dr. Aoki"`

    Scenario: Rushing the room for a second guest
      Given "fiona" does a `book` with `guest_name="Mr. Okafor"` and `room_type="Deluxe King"` and `arrival="2027-03-01"` and `departure="2027-03-02"` on `Hotel` of "hotel"
      And the resulting `reservation_id` is saved as "other stay"
      When "fiona" attempts a `rush_room` with `reservation_id=<other stay>` and `room_number="202"` on `Hotel` of "hotel"
      Then the attempt aborts with `RoomHeldError` with `guest_name="Dr. Aoki"`

    Scenario: The guest is given another room that came free first
      Given "hugo" does a `start_cleaning` on `Room` of "201"
      And "hugo" does a `mark_clean` on `Room` of "201"
      And "ines" does an `inspect_room` on `Room` of "201"
      When "fiona" does a `check_in_booking` with `reservation_id=<stay>` and `room_number="201"` on `Hotel` of "hotel"
      Then as "fiona", `get` on the `Room` for "202" has `room.rush_reservation_id=""`
