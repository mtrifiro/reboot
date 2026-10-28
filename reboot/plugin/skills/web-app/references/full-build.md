---
title: Build the Whole App at Once
impact: MEDIUM
impactDescription: When the user asks for the complete app in one go, this is the order that gets a working prototype in front of them first and then finishes every feature
tags: build flow, full build, prototype, sub-agent, readiness check
---

## Build the Whole App at Once

Use this instead of the one-feature flow in `SKILL.md` when the user
chose a full prototype in the scope questions, or asked for the whole
app in one go ("build the whole thing", "the complete app"). The
design phase is the same, with every feature's methods and pages
spelled out.

### The Steps

The task list uses the items "The whole app first" in
[`app/references/task-list.md`](../../app/references/task-list.md).

**All commands run from the application directory.**

1. Create `.python-version`, `pyproject.toml`, `.rbtrc`, and
   `.mypy.ini` — same shape as in
   `python/references/lifecycle-{project-setup,rbtrc}.md`. In
   `.rbtrc`, point the React codegen at `frontend/api`:
   ```sh
   generate --react=frontend/api
   ```
2. `uv sync`.
3. Don't start the developer dashboard yet: it starts after step 5,
   once there is an API for it to show.
4. Write the API definition (`api/<pkg>/v1/<name>.py`). Pydantic
   rules live in `python/references/api-pydantic.md`; method
   marker → context-type rules in
   `python/references/api-methods.md`. Every `Reader`, `Writer`,
   `Transaction` and `Workflow` still requires the `mcp=` argument:
   write `mcp=None` on each one. Do **not** add `mcp=Tool()` or
   `UI()`; those are MCP-UI only.
5. `uv run rbt generate`. Don't read what it wrote: the signature
   your servicer must match is in `python/references/api-methods.md`
   ("The Servicer Signature Each Declaration Obliges"). Then start
   the developer dashboard — load the
   [`dashboard` skill](../../dashboard/SKILL.md) and follow it — so the
   user can watch the app come together, and go on without waiting
   for it. If it fails to come up, say so in one sentence and keep
   building; do not stop to debug it.
   The build reaches a working prototype first, then finishes the app
   one feature at a time. The prototype runs on the real API and the
   real generated hooks, so the user's changes and the finished app
   converge on the same code. The user sees it only once it works.

**The prototype, built in two parts at once.** In Claude Code and the
Claude app, which have the Agent tool, always start a sub-agent for
the frontend (steps 8 to 12) right after step 5, and do steps 6 and 7
yourself meanwhile: the pages then cost no time of their own (vet-1
handed off five features at 25 m 51 s this way; crm-15, in order, had
its first page 5.5 minutes later). Give it the proposed design with its brief, the API file,
and this skill's frontend references; tell it to work only under
`frontend/`, never to run `rbt generate`, change the API or start
the app, and to report back when `npm run build` passes or when the
API lacks something a page needs. Only a host without
the Agent tool (Codex, say) does the steps in order.

6. Write a thin servicer (`backend/src/servicers/<name>.py`),
   context-type patterns in `python/references/servicer-*.md`.
   Readers return real state; writers and transactions store what
   they are given. Leave out every rule from the feature files (no
   overlap, stock or capacity checks, no role checks beyond sign-in)
   even when one is quick to write: the rules come with each
   feature below, with their scenarios, and a prototype that waits
   for them reaches the user later.
   Write the real `authorizer()` rules now: they are short and the
   prototype needs sign-in to work.
7. Write `main.py` (`python/references/lifecycle-application-entry.md`)
   with believable demo data from `initialize`, only under
   `rbt dev run`, seeded as `python/references/lifecycle-seeding.md`
   says: a few bulk transactions, not one call per record, and a
   small set, enough that every page shows something.
8. Scaffold the frontend at `frontend/`
   (`npm create vite@latest frontend -- --template react-ts`) and
   shape it as [`references/react-client.md`](react-client.md)
   shows: the SPA's `index.html`, `src/`, and `public/` under
   `frontend/web/`, the config rooted there with the `dedupe` and
   `server.host` entries, the Reboot packages in `package.json`, and
   `frontend/web/.env.development` with `VITE_REBOOT_URL`.
9. `cd frontend && npm install`.
10. `uv run rbt generate` again — the React bindings need
    `node_modules` to resolve types correctly. (A frontend sub-agent
    asks the main agent to run it.)
11. Build every page of the design from
    [`references/react-client.md`](react-client.md): the
    provider and its `url`, the generated hook/mutator/error
    declarations, sign-in, and typed errors are all written out
    there. Write the calls from that reference and do **not** open
    `frontend/api/**/*_rbt_react.ts` to check them — it is tens of
    thousands of lines that then ride along on every later turn.
12. `cd frontend && npm run build` (sanity check the bundle).
13. Start the app with the [`run` skill](../../run/SKILL.md), then
    check it is ready before telling the user anything about it,
    in a real browser: Playwright, installed as
    `python/references/testing-web-app.md` says (the web app
    scenarios need it anyway), or the browser tool the agent has:
    - the demo data has finished loading: under `rbt dev run` each
      `initialize` call runs twice to validate it, so wait until a
      page shows the whole set, not part of it;
    - every page of the design opens as a signed-in user and shows
      the demo data, with no errors in the browser console;
    - the main action of each page works once, and every filter or
      drawer it opens can be cleared or closed;
    - the main page shows its first record within 2 seconds, timed
      as [`first-paint.md`](first-paint.md) says.

    That is the whole check: don't test flows end to end by hand, and
    don't check phone width or the dark scheme yet. The scenarios
    test the flows, and the look is checked as the features are
    finished. Fix what fails and check again. Only then give the user
    the URL and a first thing to try, with a screenshot of the main
    page taken during the check, so the look is in the message; say
    that the pages and data are real and the rules are not enforced
    yet, and ask them to try it and say what to change. Don't wait for an answer; go on to the
    features.

**The features, one at a time**, in the order of the design. The
app keeps running; `rbt dev run` reloads on each change. For each
feature:

14. Write its scenarios: every action the user should be able to
    _do_ is a scenario in the built-in steps of
    `python/references/testing-features.md`, and the flows a person
    clicks through are web app scenarios per
    `python/references/testing-web-app.md` (they need `playwright`,
    `pytest-playwright`, `uv run playwright install chromium`, and
    the page's accessible markup). Every step names who calls; a
    user who must be signed in is declared with
    `"alice" is an authenticated user`, so the real authorizers are
    exercised: register the **real** servicers and never subclass
    one to weaken its `authorizer()`. Let factories make ids up.
15. Add the feature's rules to the servicer and adjust its pages,
    until its scenarios pass. When a scenario fails for a reason
    that looks like it is inside the framework, check
    `python/references/patterns-idempotency.md` and
    `patterns-common-gotchas.md` before reading `site-packages`.
16. Fold in what the user asked to change, if anything: a change to
    the design goes back to the proposed design, then into the
    feature it touches. The Flywheel's routing rule
    ([`app/references/flywheel.md`](../../app/references/flywheel.md))
    says which changes are design.
17. Test the backend only: `uv run pytest tests/<app>_test.py`, every
    feature's backend scenarios and no browser, in the background, its
    result said once ([`feature/SKILL.md`](../../feature/SKILL.md),
    "Report a full run once, at the end"), and
    `uv run mypy backend/ tests/` from the project root. After a
    failure, fix it and rerun only what failed (`--lf`), then go on;
    say in one line which feature is now finished. The browser
    scenarios (`tests/web_test.py`) wait for step 18: they start a
    browser and the frontend on every run, and the pages are finished
    last. A whole-suite run after every feature cost restaurant-3 over
    a third of its build.

**The handoff**, when every feature is done:

18. Run the whole suite once, browser scenarios included, in the
    background, its result said once, and mypy. After a failure, fix
    it and rerun only what failed (`--lf`); run the whole suite again
    only when a fix changed something several features share (an
    object's state, a method, the page shell). Then every scenario passes (or is `@blocked` with its reason) and
    mypy is green — together they are what catches contract bugs.
    Write the handoff in the shape of
    [`app/references/design-messages.md`](../../app/references/design-messages.md),
    covering every feature. Point the user at the dashboard's Features page and at the
    recordings of the browser scenarios, ask in a question dialog
    (`AskUserQuestion` where available): **<The app> works. What
    next?**, worded as `app/references/accept-design.md` says (its
    recommended next step accepts the app as built; on acceptance, record it as
    [`app/references/accept-design.md`](../../app/references/accept-design.md)
    says), and, unless they asked
    for only a web app, end with the one-line offer of an MCP UI
    (`app` skill, "At handoff").
