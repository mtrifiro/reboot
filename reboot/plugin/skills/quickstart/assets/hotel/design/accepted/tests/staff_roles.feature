Feature: Managers decide what each member of staff may do
  A manager invites staff by their work address and gives each one a
  role: manager, front desk or housekeeping. The roster is the only place
  a role is kept, so nobody can give themselves more access than a
  manager granted.

  Background:
    Given the application is up
    And "alice" signs in as "alice@maison.test", verified yes

  Scenario: The first person to sign in to a new hotel runs the roster
    Then as "alice", `my_role` on the `Team` for "team" has `member=true` and `role="manager"`

  Rule: An invitation is taken up only by a verified address

    Scenario: An invited housekeeper arrives
      Given "alice" does an `invite` with `email="hugo@maison.test"` and `role="housekeeping"` on `Team` of "team"
      When "hugo" signs in as "hugo@maison.test", verified yes
      Then as "hugo", `my_role` on the `Team` for "team" has `role="housekeeping"`

    Scenario: Someone signs in claiming an invited address the provider did not verify
      Given "alice" does an `invite` with `email="hugo@maison.test"` and `role="housekeeping"` on `Team` of "team"
      When "mallory" signs in as "hugo@maison.test", verified no
      Then as "mallory", `my_role` on the `Team` for "team" has `role=""`

  Rule: Only a manager gives out roles

    Scenario: The front desk tries to promote themselves
      Given "alice" does an `invite` with `email="fiona@maison.test"` and `role="front_desk"` on `Team` of "team"
      And "fiona" signs in as "fiona@maison.test", verified yes
      When "fiona" attempts a `set_role` with `user_id="fiona"` and `role="manager"` on `Team` of "team"
      Then the attempt aborts with `PermissionDenied`

    Scenario: A manager moves someone to the front desk
      Given "gus" signs in as "gus@maison.test", verified yes
      When "alice" does a `set_role` with `user_id="gus"` and `role="front_desk"` on `Team` of "team"
      Then as "gus", `my_role` on the `Team` for "team" has `role="front_desk"`

  Rule: The hotel always keeps at least one manager

    Scenario: The only manager tries to step down
      When "alice" attempts a `set_role` with `user_id="alice"` and `role="housekeeping"` on `Team` of "team"
      Then the attempt aborts with `LastManagerError`
