Feature: The front desk books stays and checks guests in and out
  A reservations agent books a guest into a room type for a run of
  nights, without choosing the room yet. On the day, the front desk sees
  who is arriving and leaving, gives each arriving guest an inspected room
  of the type they booked, and checks departing guests out, which sends
  their rooms to housekeeping.

  Background:
    Given the application is up
    And "alice" signs in as "alice@maison.test", verified yes
    And "alice" does an `invite` with `email="fiona@maison.test"` and `role="front_desk"` on `Team` of "team"
    And "alice" does an `invite` with `email="hugo@maison.test"` and `role="housekeeping"` on `Team` of "team"
    And "alice" does an `invite` with `email="ines@maison.test"` and `role="housekeeping"` on `Team` of "team"
    And "fiona" signs in as "fiona@maison.test", verified yes
    And "hugo" signs in as "hugo@maison.test", verified yes
    And "ines" signs in as "ines@maison.test", verified yes

  Scenario: Booking a Junior Suite for three nights
    When "fiona" does a `book` with `guest_name="Mme. Laurent"` and `room_type="Junior Suite"` and `arrival="2027-03-01"` and `departure="2027-03-04"` on `Hotel` of "hotel"
    And the resulting `reservation_id` is saved as "stay"
    Then as "fiona", `get` on the `Reservation` for "<stay>" has `reservation.status="booked"` and `reservation.guest_name="Mme. Laurent"` and `reservation.room_number=""`
    And as "fiona", `front_desk` with `date="2027-03-01"` on the `Hotel` for "hotel" has `arrivals` of length `1` and `arrivals[0].guest_name="Mme. Laurent"`

  Scenario: A stay must leave after it arrives
    When "fiona" attempts a `book` with `guest_name="Mr. Okafor"` and `room_type="Suite"` and `arrival="2027-03-04"` and `departure="2027-03-04"` on `Hotel` of "hotel"
    Then the attempt aborts with `InvalidDatesError`

  Scenario: Housekeeping cannot take bookings
    When "hugo" attempts a `book` with `guest_name="Mr. Okafor"` and `room_type="Suite"` and `arrival="2027-03-01"` and `departure="2027-03-02"` on `Hotel` of "hotel"
    Then the attempt aborts with `PermissionDenied`

  Rule: A room type is never booked beyond the rooms the hotel has of it
    On every night, the stays booked into a room type, counting those
    already checked in, are at most the number of rooms of that type.

    Scenario: The Penthouse booked twice for an overlapping night
      Given "fiona" does a `book` with `guest_name="Ms. Varga"` and `room_type="Penthouse"` and `arrival="2027-03-01"` and `departure="2027-03-03"` on `Hotel` of "hotel"
      When "fiona" attempts a `book` with `guest_name="Mr. Sato"` and `room_type="Penthouse"` and `arrival="2027-03-02"` and `departure="2027-03-04"` on `Hotel` of "hotel"
      Then the attempt aborts with `SoldOutError` with `room_type="Penthouse"` and `night="2027-03-02"`
      And as "fiona", `front_desk` with `date="2027-03-02"` on the `Hotel` for "hotel" has `availability[4].room_type="Penthouse"` and `availability[4].nights[0].left=0`

    Scenario: The Penthouse booked from the morning the last guest leaves
      Given "fiona" does a `book` with `guest_name="Ms. Varga"` and `room_type="Penthouse"` and `arrival="2027-03-01"` and `departure="2027-03-03"` on `Hotel` of "hotel"
      When "fiona" does a `book` with `guest_name="Mr. Sato"` and `room_type="Penthouse"` and `arrival="2027-03-03"` and `departure="2027-03-05"` on `Hotel` of "hotel"
      Then the result has `reservation_id` containing `"MV-"`

  Rule: A cancelled booking frees its nights

    Scenario: The Penthouse rebooked after a cancellation
      Given "fiona" does a `book` with `guest_name="Ms. Varga"` and `room_type="Penthouse"` and `arrival="2027-03-01"` and `departure="2027-03-03"` on `Hotel` of "hotel"
      And the resulting `reservation_id` is saved as "first stay"
      When "fiona" does a `cancel_booking` with `reservation_id=<first stay>` on `Hotel` of "hotel"
      And "fiona" does a `book` with `guest_name="Mr. Sato"` and `room_type="Penthouse"` and `arrival="2027-03-01"` and `departure="2027-03-03"` on `Hotel` of "hotel"
      Then as "fiona", `get` on the `Reservation` for "<first stay>" has `reservation.status="cancelled"`

  Rule: A guest is checked in only to an inspected room of the type they booked

    Scenario: Checking a booked guest into a dirty room
      Given "fiona" does a `book` with `guest_name="Mme. Laurent"` and `room_type="Deluxe King"` and `arrival="2027-03-01"` and `departure="2027-03-03"` on `Hotel` of "hotel"
      And the resulting `reservation_id` is saved as "stay"
      When "fiona" attempts a `check_in_booking` with `reservation_id=<stay>` and `room_number="201"` on `Hotel` of "hotel"
      Then the attempt aborts with `RoomNotReadyError` with `status="vacant_dirty"`
      And as "fiona", `get` on the `Reservation` for "<stay>" has `reservation.status="booked"`

    Scenario: Checking a Deluxe King guest into a Junior Suite
      Given "fiona" does a `book` with `guest_name="Mme. Laurent"` and `room_type="Deluxe King"` and `arrival="2027-03-01"` and `departure="2027-03-03"` on `Hotel` of "hotel"
      And the resulting `reservation_id` is saved as "stay"
      And "hugo" does a `start_cleaning` on `Room` of "208"
      And "hugo" does a `mark_clean` on `Room` of "208"
      And "ines" does an `inspect_room` on `Room` of "208"
      When "fiona" attempts a `check_in_booking` with `reservation_id=<stay>` and `room_number="208"` on `Hotel` of "hotel"
      Then the attempt aborts with `WrongRoomTypeError` with `booked="Deluxe King"` and `room_type="Junior Suite"`

    Scenario: A booked guest takes an inspected room
      Given "fiona" does a `book` with `guest_name="Mme. Laurent"` and `room_type="Deluxe King"` and `arrival="2027-03-01"` and `departure="2027-03-03"` on `Hotel` of "hotel"
      And the resulting `reservation_id` is saved as "stay"
      And "hugo" does a `start_cleaning` on `Room` of "201"
      And "hugo" does a `mark_clean` on `Room` of "201"
      And "ines" does an `inspect_room` on `Room` of "201"
      When "fiona" does a `check_in_booking` with `reservation_id=<stay>` and `room_number="201"` on `Hotel` of "hotel"
      Then as "fiona", `get` on the `Room` for "201" has `room.status="occupied"` and `room.guest_name="Mme. Laurent"`
      And as "fiona", `get` on the `Reservation` for "<stay>" has `reservation.status="checked_in"` and `reservation.room_number="201"`

    Scenario: A second guest given a room that is already taken
      Given "fiona" does a `book` with `guest_name="Mme. Laurent"` and `room_type="Deluxe King"` and `arrival="2027-03-01"` and `departure="2027-03-03"` on `Hotel` of "hotel"
      And the resulting `reservation_id` is saved as "first stay"
      And "fiona" does a `book` with `guest_name="Mr. Okafor"` and `room_type="Deluxe King"` and `arrival="2027-03-01"` and `departure="2027-03-02"` on `Hotel` of "hotel"
      And the resulting `reservation_id` is saved as "second stay"
      And "hugo" does a `start_cleaning` on `Room` of "201"
      And "hugo" does a `mark_clean` on `Room` of "201"
      And "ines" does an `inspect_room` on `Room` of "201"
      And "fiona" does a `check_in_booking` with `reservation_id=<first stay>` and `room_number="201"` on `Hotel` of "hotel"
      When "fiona" attempts a `check_in_booking` with `reservation_id=<second stay>` and `room_number="201"` on `Hotel` of "hotel"
      Then the attempt aborts with `RoomNotReadyError` with `status="occupied"`

  Scenario: A booked guest checks out
    Given "fiona" does a `book` with `guest_name="Mme. Laurent"` and `room_type="Deluxe King"` and `arrival="2027-03-01"` and `departure="2027-03-03"` on `Hotel` of "hotel"
    And the resulting `reservation_id` is saved as "stay"
    And "hugo" does a `start_cleaning` on `Room` of "201"
    And "hugo" does a `mark_clean` on `Room` of "201"
    And "ines" does an `inspect_room` on `Room` of "201"
    And "fiona" does a `check_in_booking` with `reservation_id=<stay>` and `room_number="201"` on `Hotel` of "hotel"
    When "fiona" does a `check_out_room` with `room_number="201"` on `Hotel` of "hotel"
    Then as "fiona", `get` on the `Room` for "201" has `room.status="vacant_dirty"` and `room.guest_name=""`
    And as "fiona", `get` on the `Reservation` for "<stay>" has `reservation.status="checked_out"`

  Scenario: The front desk books a stay and checks the guest in on the day
    Given "hugo" does a `start_cleaning` on `Room` of "805"
    And "hugo" does a `mark_clean` on `Room` of "805"
    And "ines" does an `inspect_room` on `Room` of "805"
    When "fiona" opens the web app at "/front-desk"
    And "fiona" fills "Day" in the web app with `"2027-03-01"`
    And "fiona" fills "Guest" in the web app with `"Dr. Haddad"`
    And "fiona" selects "Suite" in "Room type" in the web app
    And "fiona" fills "Arrival" in the web app with `"2027-03-01"`
    And "fiona" fills "Departure" in the web app with `"2027-03-04"`
    And "fiona" clicks the "Book stay" button in the web app
    Then "fiona" eventually sees "Booked Dr. Haddad" in the web app within 10 seconds
    And "fiona" eventually sees "Dr. Haddad" in the "Arrivals" table in the web app within 10 seconds
    When "fiona" clicks the "Check in Dr. Haddad" button in the web app
    Then "fiona" eventually sees "Dr. Haddad is in room 805." in the web app within 10 seconds
    And as "fiona", `get` on the `Room` for "805" has `room.status="occupied"` and `room.guest_name="Dr. Haddad"`

  Rule: A guest is checked in before 3 pm only with a manager's approval
    On arrival day, check-in opens at 3 pm at the hotel, in its own time zone.
    Before then a manager approves an early check-in on the reservation,
    and from then on the front desk may check the guest in. A manager
    checking a guest in early is recorded as approving it.

    Background:
      Given "fiona" does a `book` with `guest_name="Mme. Laurent"` and `room_type="Deluxe King"` and `arrival="2027-03-01"` and `departure="2027-03-03"` on `Hotel` of "hotel"
      And the resulting `reservation_id` is saved as "stay"
      And "hugo" does a `start_cleaning` on `Room` of "201"
      And "hugo" does a `mark_clean` on `Room` of "201"
      And "ines" does an `inspect_room` on `Room` of "201"

    Scenario: The front desk checks a guest in at 11 in the morning
      Given it is "2027-03-01 11:00" at the hotel
      When "fiona" attempts a `check_in_booking` with `reservation_id=<stay>` and `room_number="201"` on `Hotel` of "hotel"
      Then the attempt aborts with `EarlyCheckInError` with `check_in_time="15:00"`
      And as "fiona", `get` on the `Room` for "201" has `room.status="inspected"`

    Scenario: A manager approves an early check-in for the front desk
      Given it is "2027-03-01 11:00" at the hotel
      When "alice" does an `approve_early_check_in` on `Reservation` of "<stay>"
      And "fiona" does a `check_in_booking` with `reservation_id=<stay>` and `room_number="201"` on `Hotel` of "hotel"
      Then as "fiona", `get` on the `Reservation` for "<stay>" has `reservation.status="checked_in"` and `reservation.early_check_in_approved_by_name="Alice"`

    Scenario: A manager checks a guest in early themselves
      Given it is "2027-03-01 11:00" at the hotel
      When "alice" does a `check_in_booking` with `reservation_id=<stay>` and `room_number="201"` on `Hotel` of "hotel"
      Then as "alice", `get` on the `Reservation` for "<stay>" has `reservation.status="checked_in"` and `reservation.early_check_in_approved_by_name="Alice"`

    Scenario: The front desk tries to approve an early check-in
      Given it is "2027-03-01 11:00" at the hotel
      When "fiona" attempts an `approve_early_check_in` on `Reservation` of "<stay>"
      Then the attempt aborts with `PermissionDenied`

    Scenario: The front desk checks a guest in at 3 pm
      Given it is "2027-03-01 15:00" at the hotel
      When "fiona" does a `check_in_booking` with `reservation_id=<stay>` and `room_number="201"` on `Hotel` of "hotel"
      Then as "fiona", `get` on the `Reservation` for "<stay>" has `reservation.status="checked_in"` and `reservation.early_check_in_approved_by_name=""`

    Scenario: A manager approves an early check-in on the front desk page
      Given it is "2027-03-01 11:00" at the hotel
      When "alice" opens the web app at "/front-desk"
      And "alice" fills "Day" in the web app with `"2027-03-01"`
      And "alice" clicks the "Approve early check-in for Mme. Laurent" button in the web app
      Then "alice" eventually sees "Early check-in approved by Alice" in the "Arrivals" table in the web app within 10 seconds
      When "fiona" opens the web app at "/front-desk"
      And "fiona" fills "Day" in the web app with `"2027-03-01"`
      And "fiona" clicks the "Check in Mme. Laurent" button in the web app
      Then "fiona" eventually sees "Mme. Laurent is in room 201." in the web app within 10 seconds
      And as "fiona", `get` on the `Reservation` for "<stay>" has `reservation.status="checked_in"` and `reservation.early_check_in_approved_by_name="Alice"`
