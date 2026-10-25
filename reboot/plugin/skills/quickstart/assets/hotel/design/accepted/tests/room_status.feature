Feature: Staff keep every room moving from check-out to the next guest
  The front desk, housekeeping and the managers share one floor plan of
  the hotel's 56 rooms. Each room moves through dirty, being cleaned,
  clean, inspected and occupied, or is taken out of order for repairs.
  Everyone sees the same live status, so the front desk only ever hands a
  guest a key to a room that is truly ready.

  Background:
    Given the application is up
    And "alice" signs in as "alice@maison.test", verified yes
    And "alice" does an `invite` with `email="fiona@maison.test"` and `role="front_desk"` on `Team` of "team"
    And "alice" does an `invite` with `email="hugo@maison.test"` and `role="housekeeping"` on `Team` of "team"
    And "alice" does an `invite` with `email="ines@maison.test"` and `role="housekeeping"` on `Team` of "team"
    And "fiona" signs in as "fiona@maison.test", verified yes
    And "hugo" signs in as "hugo@maison.test", verified yes
    And "ines" signs in as "ines@maison.test", verified yes

  Scenario: The floor plan shows every room in the hotel
    Then as "fiona", `floor_plan` on the `Hotel` for "hotel" has `rooms` of length `56`
    And as "fiona", `floor_plan` on the `Hotel` for "hotel" has `rooms[0].number="201"` and `rooms[55].number="808"` and `rooms[55].room_type="Penthouse"`

  Rule: A room can be checked into only once it has been inspected
    A guest at this level of service never walks into a room that has not
    been cleaned and then checked by a second person.

    Scenario: Checking a guest into a room that is still dirty
      When "fiona" attempts a `check_in` with `guest_name="Mme. Laurent"` on `Room` of "201"
      Then the attempt aborts with `RoomNotReadyError` with `status="vacant_dirty"`
      And as "fiona", `get` on the `Room` for "201" has `room.status="vacant_dirty"` and `room.guest_name=""`

    Scenario: Checking a guest into a room that is clean but not yet inspected
      Given "hugo" does a `start_cleaning` on `Room` of "201"
      And "hugo" does a `mark_clean` on `Room` of "201"
      When "fiona" attempts a `check_in` with `guest_name="Mme. Laurent"` on `Room` of "201"
      Then the attempt aborts with `RoomNotReadyError` with `status="vacant_clean"`

    Scenario: A cleaned and inspected room takes its guest
      Given "hugo" does a `start_cleaning` on `Room` of "201"
      And "hugo" does a `mark_clean` on `Room` of "201"
      And "ines" does an `inspect_room` on `Room` of "201"
      When "fiona" does a `check_in` with `guest_name="Mme. Laurent"` on `Room` of "201"
      Then as "fiona", `get` on the `Room` for "201" has `room.status="occupied"` and `room.guest_name="Mme. Laurent"`

  Rule: A walk-in is checked in before 3 pm only by a manager
    Check-in opens at 3 pm at the hotel, in its own time zone, for walk-ins as
    for booked guests; before then only a manager may check one in.

    Background:
      Given "hugo" does a `start_cleaning` on `Room` of "201"
      And "hugo" does a `mark_clean` on `Room` of "201"
      And "ines" does an `inspect_room` on `Room` of "201"
      And it is "2027-03-01 10:30" at the hotel

    Scenario: The front desk checks a walk-in in at half past ten
      When "fiona" attempts a `check_in` with `guest_name="Mr. Arden"` on `Room` of "201"
      Then the attempt aborts with `EarlyCheckInError` with `check_in_time="15:00"`

    Scenario: A manager checks a walk-in in at half past ten
      When "alice" does a `check_in` with `guest_name="Mr. Arden"` on `Room` of "201"
      Then as "alice", `get` on the `Room` for "201" has `room.status="occupied"` and `room.guest_name="Mr. Arden"`

    Scenario: A walk-in check-in may not claim a reservation
      The reservation link is set only by the hotel's own check-in of a
      booked guest, which has already applied the 3 pm rule.

      When "fiona" attempts a `check_in` with `guest_name="Mr. Arden"` and `reservation_id="MV-FAKE01"` on `Room` of "201"
      Then the attempt aborts with `PermissionDenied`

  Rule: The person who cleaned a room cannot be the one who inspects it

    Scenario: A housekeeper tries to inspect their own work
      Given "hugo" does a `start_cleaning` on `Room` of "202"
      And "hugo" does a `mark_clean` on `Room` of "202"
      When "hugo" attempts an `inspect_room` on `Room` of "202"
      Then the attempt aborts with `SameInspectorError`
      And as "hugo", `get` on the `Room` for "202" has `room.status="vacant_clean"` and `room.cleaned_by_name="Hugo"`

  Rule: Check-out always sends the room back to dirty

    Scenario: A guest checks out
      Given "hugo" does a `start_cleaning` on `Room` of "203"
      And "hugo" does a `mark_clean` on `Room` of "203"
      And "ines" does an `inspect_room` on `Room` of "203"
      And "fiona" does a `check_in` with `guest_name="Mr. Okafor"` on `Room` of "203"
      When "fiona" does a `check_out` on `Room` of "203"
      Then as "fiona", `get` on the `Room` for "203" has `room.status="vacant_dirty"` and `room.guest_name=""` and `room.cleaned_by_name=""`

  Rule: A room out of order needs a reason, and comes back into service dirty

    Scenario: Taking a room out of order without saying why
      When "alice" attempts a `take_out_of_order` with `reason=""` on `Room` of "204"
      Then the attempt aborts with `MissingDetailError` with `detail="reason"`

    Scenario: A room goes out of order for repairs
      When "alice" does a `take_out_of_order` with `reason="Leak under the vanity"` on `Room` of "204"
      Then as "fiona", `get` on the `Room` for "204" has `room.status="out_of_order"` and `room.out_of_order_reason="Leak under the vanity"`

    Scenario: A repaired room comes back into service dirty
      Given "alice" does a `take_out_of_order` with `reason="Leak under the vanity"` on `Room` of "204"
      When "alice" does a `return_to_service` on `Room` of "204"
      Then as "fiona", `get` on the `Room` for "204" has `room.status="vacant_dirty"` and `room.out_of_order_reason=""`

    Scenario: An occupied room cannot be taken out of order
      Given "hugo" does a `start_cleaning` on `Room` of "205"
      And "hugo" does a `mark_clean` on `Room` of "205"
      And "ines" does an `inspect_room` on `Room` of "205"
      And "fiona" does a `check_in` with `guest_name="Ms. Varga"` on `Room` of "205"
      When "alice" attempts a `take_out_of_order` with `reason="Noisy minibar"` on `Room` of "205"
      Then the attempt aborts with `InvalidTransitionError` with `status="occupied"`

  Rule: Each role does only its own part of the work
    Housekeeping cleans and inspects, the front desk checks guests in and
    out, and managers may do all of it and also put rooms out of order.

    Scenario: A housekeeper tries to check a guest in
      Given "hugo" does a `start_cleaning` on `Room` of "206"
      And "hugo" does a `mark_clean` on `Room` of "206"
      And "ines" does an `inspect_room` on `Room` of "206"
      When "hugo" attempts a `check_in` with `guest_name="Mr. Sato"` on `Room` of "206"
      Then the attempt aborts with `PermissionDenied`

    Scenario: The front desk tries to put a room out of order
      When "fiona" attempts a `take_out_of_order` with `reason="Broken lamp"` on `Room` of "207"
      Then the attempt aborts with `PermissionDenied`

    Scenario: Someone signed in but not yet given a role can look but not change anything
      Given "gus" signs in as "gus@maison.test", verified yes
      Then as "gus", `floor_plan` on the `Hotel` for "hotel" has `rooms` of length `56`
      When "gus" attempts a `start_cleaning` on `Room` of "208"
      Then the attempt aborts with `PermissionDenied`

  Scenario: The front desk checks a guest in from the floor plan
    Given "hugo" does a `start_cleaning` on `Room` of "201"
    And "hugo" does a `mark_clean` on `Room` of "201"
    And "ines" does an `inspect_room` on `Room` of "201"
    When "fiona" opens the web app
    And "fiona" clicks the "Room 202, Deluxe King, Dirty" button in the web app
    And "fiona" fills "Guest name" in the web app with `"Mme. Laurent"`
    And "fiona" clicks the "Check in" button in the web app
    Then "fiona" eventually sees "This room isn't ready for a guest" in the web app within 10 seconds
    When "fiona" clicks the "Done" button in the web app
    And "fiona" clicks the "Room 201, Deluxe King, Ready" button in the web app
    And "fiona" fills "Guest name" in the web app with `"Mme. Laurent"`
    And "fiona" clicks the "Check in" button in the web app
    Then "fiona" eventually sees "Mme. Laurent is checked in." in the web app within 10 seconds
    And as "fiona", `get` on the `Room` for "201" has `room.status="occupied"` and `room.guest_name="Mme. Laurent"`
