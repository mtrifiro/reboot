@wip
Feature: The __things text__ in the web app
  On the one page, someone signed in adds a __thing text__ and sees it
  on the list at once.

  Background:
    Given the application is up

  Scenario: Adding a __thing text__ in the web app
    Given "alice" is an authenticated user
    When "alice" opens the web app in light mode
    And "alice" fills "Name" in the web app with `"First one"`
    And "alice" fills "Note" in the web app with `"A line about it"`
    And "alice" clicks the "Add" button in the web app
    Then "alice" eventually sees "First one" in the "__Things text__" table in the web app within 10 seconds
    And as "alice", `__things__` on the `__Hub__` for "__hub__" has `__things__` of length `1` and `__things__[0].name="First one"`

  Scenario: Signing in with the Development picker
    Given "ben" is an unauthenticated user
    When "ben" opens the web app in dark mode
    And "ben" clicks the "Sign in" button in the web app
    And "ben" clicks the "Ben" link in the web app
    Then "ben" is signed in to the web app with their user id saved as "ben user id"
    And "ben" eventually sees "__Things text__" in the web app within 10 seconds
