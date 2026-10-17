---
title: Drive the Web App from Scenarios
impact: MEDIUM
impactDescription: A user-facing flow that is only tested at the backend leaves the page, the session cookie, and CORS untested; a page without accessible markup cannot be driven at all
tags: testing, bdd, web-app, playwright, frontend, vite, aria, accessible-name, recordings, sign-in
---

## Drive the Web App from Scenarios

> **Critical:** the web app steps find things the way a person
> does: a button by what it says, a field by its label, a table by
> its caption. They never take a CSS selector. A page the steps
> cannot find things on has an accessibility bug, and the fix is in
> the markup, not in the scenario.

A scenario opens the application's web app in a real browser, run
through Playwright, against the same backend its backend steps call.
Backend steps and web app steps mix in one scenario, so a scenario
can set up through the API, act in the browser, and assert on
state:

```gherkin
Scenario: Opening a first account in the web app
  Given "alice" is an authenticated user
  When "alice" opens the web app in light mode
  Then "alice" sees "Signed in as alice" in the web app
  When "alice" fills "Initial Deposit ($)" in the web app with `1000`
  And "alice" clicks the "Open Account" button in the web app
  Then "alice" eventually sees "$1000" in the "Your Accounts" table in the web app within 10 seconds
  When "alice" saves the text of the "account-id" element in the web app as "account id"
  Then as "alice", `balance` on the `Account` for "<account id>" has `amount=1000.0`
```

`testing-features.md` covers the backend steps and the shape of a
feature; this reference covers what the browser adds. The
[`reboot-bank-pydantic`](https://github.com/reboot-dev/reboot-bank-pydantic)
example's `tests/web_test.py`, `opening_accounts.feature`,
`transfers.feature`, and `sign_in.feature` are the reference.

## What the Project Installs

Add Playwright to the dev group next to `reboot[dev]`, then install
a browser once:

```toml
[dependency-groups]
dev = [
    "reboot[dev]==<version>",
    "playwright>=1.55.0",
    "pytest-playwright>=0.7.1",
    ...
]
```

```sh
uv sync
uv run playwright install chromium
cd frontend && npm install   # the web app's own dependencies
```

With `playwright` and `pytest-playwright` present, the `reboot`
pytest plugin registers the web app steps and records every browser
scenario; without them the backend steps still work.

## The `frontend` Fixture and the Application

Each scenario serves the web app fresh, once its backend is up. The
starter's `tests/web_test.py` (rendered with `--web`) defines both
fixtures: `frontend`, from `reboot.bdd.vite.vite` with the directory
`frontend`; and `application`, which takes `frontend`, passes
`SERVICERS` and `initialize` from `main`, names the Development picker
for both `dev` and `prod` (the harness is neither `rbt dev run` nor
`rbt serve`), and sets `allowed_origins=[frontend.origin]`: the app's
origin is the only one Envoy lets read `/whoami` cross-origin, as a
deployment lists its host. Its `scenarios(...)` names the web feature
files; every one runs from this module.

The app is served the way it is deployed: from its own origin (a
Vite dev server on `localhost`), calling the backend cross-origin at
its `127.0.0.1` address, so the session cookie, the `whoami` probe,
and Envoy's CORS allow-list are exercised the way production
exercises them. The `application` fixture takes `frontend` so the
app can allow that origin.

A project that serves its web app some other way defines
`frontend` against its own `Frontend` subclass. A mobile app or an
MCP host would get its own phrase against its own fixture; `in the web app` always means this one.

## The Steps

Every step names the user acting, a user the scenario declared.
**Each user gets a browser of their own**, so two users can be in
the app in one scenario.

| Step                                                                          | What it does                                                                                                                       |
| ----------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------- |
| `"alice" opens the web app in light mode`                                     | Opens the app's origin in alice's browser, in that color scheme (`light` or `dark`; `at "/path"` before the mode for another page) |
| `"alice" clicks the "Open Account" button in the web app`                     | Clicks the element of that role and accessible name                                                                                |
| `"alice" fills "Amount ($)" in the web app with `250``                        | Fills the field with that label                                                                                                    |
| `"alice" fills "Guest name" in the web app with `"Mme. Laurent"``             | The same, with text: a JSON string, quoted inside the backticks                                                                    |
| `"alice" selects "<first account id>" in "From Account" in the web app`       | Picks an option in the select with that label                                                                                      |
| `"alice" checks "Remember me" in the web app` / `unchecks`                    | Sets the checkbox with that label                                                                                                  |
| `"alice" presses "Enter" in the web app`                                      | Presses a key in the focused element                                                                                               |
| `"alice" sees "$1000" in the web app`                                         | Asserts the text is visible now                                                                                                    |
| `"alice" sees "$1000" in the "Your Accounts" table in the web app`            | Asserts the text within that element                                                                                               |
| `"alice" eventually sees "$1000" in the web app within 10 seconds`            | Waits for the text, at most that long                                                                                              |
| `"alice" does not see "<carol account id>" in the web app`                    | Asserts the text is absent                                                                                                         |
| `"alice" sees the "Sign in" button in the web app is enabled` / `is disabled` | Asserts the element's state                                                                                                        |
| `"alice" sees the web app at "/accounts"`                                     | Asserts the page's path                                                                                                            |
| `"alice" saves the text of the "account-id" element in the web app as "id"`   | Reads an element by test id into a saved value                                                                                     |
| `"bob" is signed in to the web app with their user id saved as "bob id"`      | Binds bob's browser session to bob (below)                                                                                         |
| `"bob" is signed out of the web app`                                          | Waits for bob's session to end (below)                                                                                             |

- The **roles** a step may name are a closed list: `button`,
  `link`, `tab`, `checkbox`, `radio`, `menuitem`, `option`, `row`,
  `table`. The name is the element's accessible name, matched
  exactly.
- **The value after `with` is JSON,** like every step value: text
  in quotes inside the backticks, `with `"Mme. Laurent"``; a number
  bare, `with `250``. Unquoted text fails with "must be JSON".
- **`sees "<text>"` must match one element.** It finds the text
  anywhere on the page, part of an element's text included, and fails
  ("strict mode violation") when more than one element shows it: a
  status word that is also in a legend, a heading or a menu. Name the
  element it is in, `sees "Waiting" in the "Room 204" row`, with a
  role from the list above, or check words only that element shows.
- **Quoted text may say `<name>`** for a saved value: `sees "<alice account id>" in the "Your Accounts" table`.
- `eventually sees` takes `within`; `sees` looks now and takes
  none. A backend change the page shows after a reactive read is
  always `eventually`.
- The one step that reads a value out of the page, `saves the text of the "..." element`, names it by `data-testid`; nothing else
  does.

## Signing In Is Clicked Through, Then Bound

An unauthenticated user signs in the way a person does, and then a
binding step ties their browser's session to their name:

```gherkin
Scenario: Signing in and out with the Development picker
  Given "ben" is an unauthenticated user
  When "ben" opens the web app in light mode
  And "ben" clicks the "Sign in" button in the web app
  And "ben" clicks the "Ben" link in the web app
  Then "ben" is signed in to the web app with their user id saved as "ben user id"
  When "ben" fills "Initial Deposit ($)" in the web app with `500`
  And "ben" clicks the "Open Account" button in the web app
  Then "ben" eventually sees "$500" in the "Your Accounts" table in the web app within 10 seconds
  And as "ben", `balances` on the `User` for "<ben user id>" eventually has `balances` of length `1` and `balances[0].balance=500.0` within 10 seconds
  When "ben" clicks the "Sign out" button in the web app
  Then "ben" is signed out of the web app
  And as "ben", `balances` on the `User` for "<ben user id>" aborts with `Unauthenticated`
```

- The Development picker lists its accounts as links named by
  identity, so `clicks the "Ben" link` picks one. A custom identity
  provider's login page is driven with the same generic steps; only
  the binding step is Reboot's.
- `is signed in to the web app` waits for the browser to come back
  to the app and asks the backend who the session is; from then on
  `as "ben",` backend steps call as the signed-in user, and `<ben user id>` is their opaque id. The `with their user id saved as`
  part is optional.
- `is signed out of the web app` waits for the session to end and
  returns the user to calling with no token.
- A scenario that does not test sign-in itself declares its people
  with `is an authenticated user`; their browsers arrive signed in.

## The App Must Have Accessible Markup

The steps locate elements through the accessibility tree, so the
page exposes one; the markup, with the React for each rule, is in
[`react-client.md`](../../web-app/references/react-client.md),
where the page is built. What a scenario counts on: a field's label
is paired with it, so `fills "Amount ($)"` finds the input and a
placeholder does not count; a button, link, tab, or menu item says
what it does, matched exactly; a table or region a step names has a
`<caption>` or a labelled heading; and `data-testid` sits only on
the element whose text is a value the backend made up, for `saves
the text of`. The web steps don't drag: a drag has its click fallback
on the page (`web-app/references/ui-design.md`, "Drag and Drop,
Wherever Something Moves"), and that is what a scenario drives.

## Recordings

Every browser scenario is recorded: a video of each user's browser,
and a screenshot after the step that opened the app for them and
after each assertion step, with the asserted element outlined. They
land beside the feature file in
`tests/<feature>.recordings/<scenario>/<digest>/` (`alice.webm`,
`2.png`). The digest is of what the scenario runs, so an older
version's recordings read as stale and a run keeps only the current
one; an outline's examples share the files, the last example's kept.

The browser is paced so the video can be followed:
`--recording-slowmo` (milliseconds after each browser operation,
default 500) and `--recording-dwell` (how long an assertion's result
stays on screen, default 1000); `0` turns either off. Only the
browser is paced. It emulates the `prefers-color-scheme` the step
names, whatever the developer's OS theme, so the recording shows
what the scenario says.

## Running

```sh
uv run pytest tests/web_test.py
uv run pytest tests/web_test.py -k "first account"
uv run pytest tests/web_test.py --recording-slowmo=0 --recording-dwell=0
```

A CI script without a browser or `node_modules` runs the backend
suite with `--ignore=tests/web_test.py`, as the bank's
`.tests/test.sh` does.
