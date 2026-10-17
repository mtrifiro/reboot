@wip
Feature: The __hub text__ keeps its __things text__
  Anyone signed in adds a __thing text__ with its details, corrects
  them, and sees every __thing text__ in the order added.

  Background:
    Given the application is up
    And "alice" is an authenticated user
    And "bob" is an authenticated user

  Scenario: Adding a __thing text__
    When "alice" does an `add___thing__` with `name="First one"` and `note="A line about it"` on `__Hub__` of "__hub__"
    And the resulting `__thing___id` is saved as "__thing text__ id"
    Then as "bob", `__things__` on the `__Hub__` for "__hub__" has `__things__` of length `1` and `__things__[0].name="First one"`
    And as "bob", `get` on the `__Thing__` for "<__thing text__ id>" has `__thing__.name="First one"` and `__thing__.note="A line about it"`

  Scenario: __Things text__ are listed in the order added
    When "alice" does an `add___thing__` with `name="First one"` and `note=""` on `__Hub__` of "__hub__"
    And "alice" does an `add___thing__` with `name="Second one"` and `note=""` on `__Hub__` of "__hub__"
    Then as "alice", `__things__` on the `__Hub__` for "__hub__" has `__things__[0].name="First one"` and `__things__[1].name="Second one"`

  Scenario: Correcting a __thing text__'s details
    Given "alice" does an `add___thing__` with `name="Frist one"` and `note=""` on `__Hub__` of "__hub__"
    And the resulting `__thing___id` is saved as "__thing text__ id"
    When "bob" does an `edit` with `name="First one"` and `note="Corrected"` on `__Thing__` of "<__thing text__ id>"
    Then as "alice", `get` on the `__Thing__` for "<__thing text__ id>" has `__thing__.name="First one"` and `__thing__.note="Corrected"`

  Rule: A __thing text__ needs a name
    A __thing text__ with no name can't be told from another, so it is
    refused.

    Scenario: A __thing text__ with no name
      When "alice" attempts an `add___thing__` with `name=""` and `note=""` on `__Hub__` of "__hub__"
      Then the attempt aborts with `Invalid__Thing__`

    Scenario: Emptying a __thing text__'s name
      Given "alice" does an `add___thing__` with `name="First one"` and `note=""` on `__Hub__` of "__hub__"
      And the resulting `__thing___id` is saved as "__thing text__ id"
      When "alice" attempts an `edit` with `name="   "` and `note=""` on `__Thing__` of "<__thing text__ id>"
      Then the attempt aborts with `Invalid__Thing__`

  Rule: Only people signed in can see or change the __things text__
    Every method has an authorizer from day one; anonymous callers are
    refused.

    Scenario: Someone not signed in looks at the __things text__
      Given "anonymous" is an unauthenticated user
      Then as "anonymous", `__things__` on the `__Hub__` for "__hub__" aborts with `Unauthenticated`
