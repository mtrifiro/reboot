---
name: web-app
description: Build complete Reboot Web Apps — a Reboot backend behind a standalone browser-facing React frontend, served at a normal URL (not embedded in an MCP host). Layers on top of the python skill for backend mechanics; covers what's specific to standalone Web Apps — no MCP front door, no UI() methods, a React/Vite SPA rendered from the starter, and Reboot auth for browser users. The backend stays ready for an MCP UI.
argument-hint: [<app-description>]
allowed-tools: Bash, Read, Write, Glob, Grep, Edit
---

# web-app — Build Reboot Web Apps

> **Version notices** from `rbt` (a mismatch, a newer Reboot): the [upgrade skill](../upgrade/SKILL.md).
>
> **Errors:** grep a fragment of the string in `python/references/errors.md` (never read whole); known defects and workarounds: [`KNOWN-ISSUES.md`](../../KNOWN-ISSUES.md).

Build complete Reboot Web Apps from a user description: a Reboot
backend behind a standalone React frontend at a normal URL.

> **Reads from `python`.** This skill is the web-frontend layer on
> the Reboot Python framework. Servicers, contexts, refs, scheduling
> primitives, backend LLM / agent calls, error types, the testing
> harness, the `.rbtrc` shape and pydantic API defaults belong to
> `python`: load its references for those. Here: the React SPA at
> `frontend/web/`, the TypeScript hooks from
> `rbt generate --react=...`, browser auth (login form / cookies /
> OAuth), and that layer's cross-cutting rules.

> **Dual-frontend apps are supported.** One backend can serve a web
> SPA _and_ an MCP front door, sharing `oauth=...`, the `User` actor
> per upstream identity and the servicer code. For both, also load
> the [`mcp-ui` skill](../mcp-ui/SKILL.md) for the MCP additions
> (`mcp=Tool()`, `UI()`, MCPJam); this skill alone covers the web
> side.

## When to Use

- Building a new Reboot Web App from a description.
- Adding features, state or UI to an existing Reboot Web App.
- Modifying its state model, methods or React UI.
- Running an existing Reboot Web App, e.g. at the start of a
  session: the [`run` skill](../run/SKILL.md) detects the app type
  and starts backend and frontend.
- Putting a finished Web App in production: the
  [`deploy` skill](../deploy/SKILL.md), backend on Reboot Cloud,
  frontend on a static host under the user's own domain.

## Auth in Web Apps

Web apps wire identity via
`Application(oauth=OAuth(provider=OAuthProviderByEnvironment(dev=Development(), prod=Google(...))))`,
as MCP UIs do. Reboot mounts its OAuth Authorization Server at
`/__/oauth/*` and brokers sign-in against the upstream IdP. The
session is an HttpOnly `rbt_session` cookie set by
`/__/oauth/finish`, read as a bearer on every RPC, so user code sees
only `context.auth.user_id`, as under MCP.

> **`token_verifier=` is the escape hatch, not the default.** Only
> for an IdP the built-in `oauth=` providers don't cover (an
> enterprise SAML/OIDC broker no `OAuthProvider` subclass can wrap)
> or for custom token semantics; Google/GitHub/Auth0/anonymous
> sign-in uses `oauth=...`. The two compose: Reboot's verifier runs
> first, and a token that is not a Reboot-minted access JWT falls
> through to yours.

The imports:

```python
from reboot.aio.applications import Application
from reboot.aio.auth.oauth import OAuth
from reboot.aio.auth.oauth_providers import (
    Development,
    Google,                       # or GitHub, Auth0, …
    OAuthProviderByEnvironment,
)
```

The sequence:

1. **Early development (no provider chosen yet):**
   `oauth=OAuth(provider=OAuthProviderByEnvironment(dev=Development(), prod=None))`.
   `Development()` is a built-in fake account picker: sign in as any
   identity at `/__/oauth/start`. `prod=None` fails fast
   if `rbt serve` runs before a real provider is chosen. Every caller
   already has a verified `context.auth.user_id`, so **write
   `authorizer()` on every Servicer from day one**, with
   `allow_if(...)` rules that run in dev as in production
   (`python/references/servicer-authorizer.md`,
   `python/references/auth-rules.md`). Never paper
   over a missing rule with `allow()`; `allow()` means "public,
   unauthenticated internet endpoint" and survives into production.
2. **Before `rbt serve` / Reboot Cloud:** set `prod=Google(...)`
   (or `GitHub(...)`, `Auth0(...)`, an own `OAuthProvider`
   subclass); the authorizers need no second pass. Until then every
   build keeps `prod=None`; the [`deploy` skill](../deploy/SKILL.md)
   sets the provider. The providers, their arguments, `scopes=`,
   `store_tokens=`, `claims=`
   ([`auth-claims.md`](../python/references/auth-claims.md)), the
   redirect URI and why the choice is for keeps:
   [`auth-oauth-providers.md`](../mcp-ui/references/auth-oauth-providers.md),
   read at deploy.

   Tests build their own `Application(...)`, not `main.py`'s, whose
   `prod=None` arm and missing `allowed_origins` start only under
   `rbt dev run`: the same servicers and authorizers, identity wired
   per `python/references/testing-harness.md` ("Identity Wiring in
   Tests") — no `oauth=` for backend scenarios; `Development()` for
   both arms plus `allowed_origins=[frontend.origin]` for scenarios
   that open the web app, as `python/references/testing-web-app.md`
   shows.

3. **Public, unauthenticated endpoints** (health checks, public
   sign-up, public catalog reads): mark them with `allow()`, its one
   legitimate use.

### Feeding the user's identity into hooks

With `Application(oauth=...)` the signed-in user's own state needs
no id-threading: call the `User` hook with **no arguments**. An
explicit-id hook's `id` must be real on every render, never a
placeholder ([`references/react-client.md`](references/react-client.md)).

### Calling external APIs on the user's behalf

To act **as the user** at an external service, store its OAuth tokens
in an `OAuthTokenManager` and call it inside a `Workflow`:
`python/references/auth-external-api-calls.md` (Path A, the sign-in
provider's `store_tokens=True`; Path B, another service's own OAuth
flow; Path C, a pasted API key through `Ciphertext`). Never a plain
`str` token field or a hand-rolled `Ciphertext`
(`python/references/stdlib-oauth-tokens.md`).

### Browser-side wiring (React)

The provider and its `url`, the hook surface, sign-in/sign-out and
typed errors: [`references/react-client.md`](references/react-client.md),
read at the frontend step, never from memory.

## Which References to Read, and When

Everything read is re-sent on every later turn, so **read each reference at the step that needs it** —
not all of them up front — and read each one **once**. The groups
are in build order; each reference appears in one. Never a whole
generated or installed file (`*_rbt.py`, `*_rbt_react.ts`,
`site-packages/`, `node_modules/`), and any search bounded hard:
[`front-door-common.md`](../app/references/front-door-common.md),
"Never Read Generated or Installed Source in the Main Thread".

> **Never read `mcp-ui/references/*` for a web app** (they produce `mcp=Tool()` markers and `UI()` methods in an app with no MCP frontend; the web equivalent is [`references/react-client.md`](references/react-client.md)), except [`auth-oauth-providers.md`](../mcp-ui/references/auth-oauth-providers.md), which is frontend-neutral: read it when you pick a real provider.

**Before the API definition:**

- `python/references/patterns-common-gotchas.md` — recurring trips.
- `python/references/api-pydantic.md` — pydantic API rules.
- `python/references/api-methods.md` — factory → context type mapping.
- `python/references/api-errors.md` — typed errors, when the API
  declares any.
- `python/references/state-collections.md` — **always when the app
  has a "list of X".**
- `python/references/state-nested-models.md` — only when a state
  nests a non-state `Model`.

**Before the project shell** (`.rbtrc`, `pyproject.toml`,
`.mypy.ini`, `main.py`):

- `python/references/lifecycle-{project-setup,rbtrc,application-entry}.md`
  — the layout, the CLI flags, `Application(...)`.

**Before the servicer:**

- `python/references/servicer-{reader,writer,transaction,constructor}.md` — one per context type declared.
- `python/references/rpc-calls.md` — kwargs, not Request wrappers;
  `Service.create(context, id)`.
- `python/references/servicer-workflow.md` — only when a `Workflow`
  is declared, then top to bottom.

**Before the authorizers** (dev-vs-prod sequence: "Auth in Web
Apps" above):

- `python/references/servicer-authorizer.md` — **start here**:
  `oauth=` vs. `token_verifier=`.
- `python/references/auth-rules.md` — the predicate machinery.
- `python/references/auth-custom-predicates.md` — only when the
  built-in predicates don't cover a rule.
- `python/references/auth-allow-deny.md` — only when the design has
  a public, unauthenticated endpoint.
- `python/references/auth-external-api-calls.md` and
  `python/references/stdlib-oauth-tokens.md` — **calling an external
  service's API as the user** (web apps: Path B).

**Before `main.py`:**

- `python/references/lifecycle-seeding.md` — demo data from
  `initialize`, under `rbt dev run` only, idempotent on restart;
  always.

**Before the tests:**

- `python/references/testing-project-setup.md` — always.
- `python/references/testing-features.md` — the built-in steps'
  spelling; always.
- `python/references/lifecycle-seeding-troubleshooting.md` — only
  when `IdempotencyUncertainError` appears or a seed stalls, hangs or
  errors.
- `python/references/testing-harness.md` and
  `testing-external-context.md` — for custom steps.
- `python/references/testing-custom-steps.md` — for custom steps.
- `testing-failure-recovery.md` — whenever the app has a spawned
  task, a `Workflow`, or `schedule()`d work.
- [`feature/SKILL.md`](../feature/SKILL.md) — the order of work
  around the feature files.

**The two parts.** Every group above this line is the backend part.
The groups from here on are the frontend part: read them only when the
frontend part starts, once the feature's backend passes its scenarios
(on the whole-app paths, every feature's), never before, and not at
all when the user stops after the backend.

**Before the frontend:**

- [`references/ui-design.md`](references/ui-design.md) — the primary
  view and the house look.
- [`references/react-client.md`](references/react-client.md) — the
  `frontend/` shell, `VITE_REBOOT_URL`, sign-in, typed errors.
- `python/references/react-generated-client.md` — what
  `rbt generate --react=` emits.

**Before the browser tests** (the frontend part):
`python/references/testing-web-app.md` (the `frontend` fixture, the web
app steps, the page's accessible markup).

**Before running the app:** the [`run` skill](../run/SKILL.md).

## Workflow: Propose the Design, Then Build

**Always work out the design before writing code.** The design is a
proposal until the user accepts it, and the first stage of the Reboot
Flywheel:
[`front-door-common.md`](../app/references/front-door-common.md),
"The Design Is a Proposal".

### Design Phase

0. List the app's features, one sentence each, in build order. Each
   is agreed in plain English and written as a `@wip` feature file by
   the [`feature` skill](../feature/SKILL.md) when its turn comes,
   before its part of the API exists.
1. Analyze the description with the State Model Assessment below.
2. The scope round, as
   [`front-door-common.md`](../app/references/front-door-common.md)
   ("The Scope Round") says. The first question's options: "One
   feature at a time, so you understand each part as it's built"
   (recommended), "A full working prototype first, then finished
   feature by feature", or "Prompt by prompt: I say what to build at each step; ask me nothing".
3. Read the API references, then show the proposed design, word for
   word in the shape of
   [`app/references/design-messages.md`](../app/references/design-messages.md),
   with the answers in it, before writing the API. It decides the
   brief (who uses the app, on what screen, the task, the one
   question its main page answers, the accent); the domain model,
   one line per type, what it is and how it relates to the others;
   the features in build order, the first marked and why. The first
   feature shows the central object and its main behavior on one
   page, with at least one rule the user can see it keep (a hotel:
   rooms and their status on a floor plan, where a room can't be
   checked into until it's clean). For the first feature only, or
   every feature when the user chose a full prototype:
   - Application types: state shape (fields, types, tags).
   - Method map, one line per method: its type
     (Reader/Writer/Transaction/Workflow) and its role for an AI
     caller (a tool, a `UI()` view, or for people only), though the
     MCP UI comes later.
   - Route surface: the SPA's pages, each page's primary view (the
     domain's own shape — floor plan, board, timeline, calendar —
     worked on directly; a filtered list for lookup) and the methods
     it calls. A page of many records reads them all through one
     reader on their parent.
   - `User` type: always. It owns per-user state, routes creation,
     and is the MCP front door if an MCP UI is added later.
   - Auth: who signs in, and what an anonymous visitor may read.
   - Ready for an MCP UI: each method's `description=` written for
     an AI caller from the start. `mcp=None` until an MCP UI is
     added; then only `mcp=` changes, which a deployed app allows
     (`python/references/api-schema-evolution.md`).
4. Build it as the user chose: one feature at a time by the
   Step-by-Step Build Flow below, or the full prototype by
   [`references/full-build.md`](references/full-build.md).

Updates to existing apps work the design first too: read the current
state, state the changes, then modify. Write it for a person who
hasn't read these skills:
[`front-door-common.md`](../app/references/front-door-common.md),
"Writing the Design for a Human Reader".

## State Model Assessment

Before writing code, analyze the request:

1. **Application types** — decompose per
   `python/references/state-collections.md` Step 1: every entity the
   user adds, edits, lists or finds is its own `Type`, never a
   `list[Todo]` on one parent.
2. **Per-user state?** If yes, declare a `User` type and route
   creation through it as `mcp-ui` does; the pattern is independent
   of MCP. An anonymous or shared-state app skips `User`.
3. **Container shape for each collection** — per
   `python/references/state-collections.md` Step 2: parents store
   references, not objects.
4. **State shape (per type)**: fields and types (lists, nested
   objects, primitives), each with `Field(tag=N)`. A nested `Model`
   owned 1:1 by a parent state is
   `Optional[X] = Field(tag=N, default=None)`, hydrated in the
   parent's factory `create` Writer; a non-Optional `Model` field
   rejects `default=` / `default_factory=`. Full rules:
   `python/references/api-pydantic.md`.
5. **Operations**: map to the right method type:
   - `Reader` — read-only queries.
   - `Writer` — single-state mutations.
   - `Transaction` — multi-state atomic operations.
   - `Workflow` — long-running control flow: loops, scheduling,
     idempotency helpers.
6. **Pages / routes**: which SPA routes exist and which methods each
   page calls, through the hooks `rbt generate --react=...` emits.
7. **Auth**: anonymous-only, public-read + authed-write, fully
   locked down, …? See `python/references/auth-*.md`.
8. **Names** — for what each type holds and is for, never for its
   key: [`front-door-common.md`](../app/references/front-door-common.md),
   "Names".

## Project Layout

The layout is the one every Reboot app has, `frontend/` included
(`python/references/lifecycle-project-setup.md`); a web app fills
`frontend/web/` and has no `frontend/mcp/`:

```
<project-root>/
├── .python-version
├── .rbtrc
├── .mypy.ini                # Type-check config (python skill)
├── pytest.ini               # testpaths: tests; pythonpath: backend/src backend/api api
├── pyproject.toml
├── api/
│   └── <pkg>/v1/
│       └── <name>.py        # API definition (pydantic)
├── backend/
│   └── src/
│       ├── main.py          # Application entrypoint
│       └── servicers/
│           └── <name>.py    # Servicer implementation
├── tests/
│   ├── <capability>.feature  # One feature per capability
│   ├── <name>_test.py       # `application` fixture + `scenarios(...)`
│   └── web_test.py          # The scenarios that open the app
└── frontend/
    ├── package.json
    ├── tsconfig.json
    ├── tsconfig.app.json
    ├── tsconfig.node.json
    ├── vite.config.ts       # Stock Vite SPA config, rooted at `web/`
    ├── api/                 # Generated TypeScript client
    │                        # (output of `rbt generate --react=`)
    └── web/
        ├── .env.development # VITE_REBOOT_URL=http://localhost:9991
        ├── index.html       # The single SPA entry
        ├── public/
        └── src/
            ├── main.tsx     # RebootClientProvider entry
            ├── App.tsx      # Routes + top-level component
            ├── vite-env.d.ts
            └── pages/
                └── <page>.tsx
```

The Vite dev server (`cd frontend && npm run dev`) serves the SPA at
its own origin, `http://localhost:5173/` by default; the SPA calls
the backend at `VITE_REBOOT_URL`. Built, it lands in
`frontend/dist/web/` with `base: "/"`, served at `/` by a static
host or the backend. An app that later adds an MCP frontend keeps
this tree, adds `frontend/mcp/<name>/` beside `web/`, and swaps in
the `mcp-ui` skill's `vite.config.ts` and `build.mjs`, which serve
both through Envoy.

## Step-by-Step Build Flow

The build's task list, where one is kept, uses the items in
[`app/references/task-list.md`](../app/references/task-list.md), word
for word.

**All commands run from the application directory.** **A file that exists is changed with the Edit tool,** the lines that change and nothing more, never a `sed -i`, a `python3 -` script or a heredoc that rewrites it ([`front-door-common.md`](../app/references/front-door-common.md), "A Change Is an Edit, Never a Rewrite"). The build
finishes one feature, with one page, and shows it; the user chooses
the next, and the loop below adds it. Each feature is built whole,
rules and scenarios included, so what the user sees works as in the
finished app.

**The first feature:**

1. Render the project from the starter
   (`python/references/lifecycle-project-setup.md`):
   `python3 '<the python skill>/assets/render.py' --app '<App Name>'
   --pkg <pkg> --hub <Hub> --thing <Thing> --web .` (single quotes, as
   written), the hub the
   design's one hub object and the thing the first feature's central
   object. It writes the shell, a working backend in that shape (a
   `User`, the hub, the thing, their servicers and tests) and the
   whole frontend (Vite, React, the house look, one page that lists
   and adds the thing, signed in), all named for the design; `.rbtrc`
   already points the React codegen at `frontend/api`. To the user it
   is the app's first working version in the design's own names,
   never a "starter" or a "template": "Backend: Hotel, Room and User
   as Reboot objects, already running and tested; next, the floor
   plan's rules." Then give the
   project `AGENTS.md` and `CLAUDE.md` with the
   [`agents-md` skill](../agents-md/SKILL.md), naming the API and
   servicer files it wrote.
2. `uv sync`.
3. Edit the starter's feature file (`tests/<things>.feature`, `@wip`)
   into the first feature's with the
   [`feature` skill](../feature/SKILL.md): its rules and scenarios in
   the same built-in steps, renamed for the activity when the name
   doesn't fit; then the API (`api/<pkg>/v1/<pkg>.py`) for that
   feature only: the design's fields on the starter's objects, its
   methods beside the starter's, in the same shape, and nothing the
   design doesn't name; later features add to it. Pydantic rules:
   `python/references/api-pydantic.md`; method marker → context type:
   `python/references/api-methods.md`. Every `Reader`, `Writer`,
   `Transaction` and `Workflow` still requires the `mcp=` argument:
   write `mcp=None` on each one.
4. `uv run rbt generate`. Don't read what it wrote: the signature
   your servicer must match is in `python/references/api-methods.md`
   ("The Servicer Signature Each Declaration Obliges"). Start the
   developer dashboard by the
   [`dashboard` skill](../dashboard/SKILL.md) without waiting for
   it; if it fails to come up, say so in one sentence and keep
   building. Built from the `guided` skill, the first
   feature instead waits for it and asks "Build on this domain model?" (the model check;
   not on the prompt-by-prompt path, which asks nothing)
   ([`app/references/design-first.md`](../app/references/design-first.md),
   "The domain model, once") before step 5.
5. Edit the starter's servicers into the feature's: its rules, its
   methods, its real `authorizer()` (the starter's: anyone signed in,
   `create` and `open` internal); context-type patterns in
   `python/references/servicer-*.md`.
6. Add any new servicer to `main.py`'s `SERVICERS`
   (`python/references/lifecycle-application-entry.md`) and
   believable demo data for this feature's objects to `initialize`,
   under `rbt dev run` only, as
   `python/references/lifecycle-seeding.md` says. Write the
   feature's scenarios in the built-in steps of
   `python/references/testing-features.md`; run `uv run pytest` as the [`feature` skill](../feature/SKILL.md)'s step 4 says (the feature's own files, in the foreground, its output never piped through `grep` or `tail`) and
   `uv run mypy backend/ tests/` with `rbt dev run` stopped (`run`
   skill, "Stopping the App"); fix what fails before any page.
7. The frontend is in place from step 1
   ([`references/react-client.md`](references/react-client.md) says
   what each file is for): `cd frontend && npm install`, then
   `uv run rbt generate` again for the React bindings, and
   `cd frontend && npm run build` to prove the starter's page compiles
   against them.
8. Edit the starter's page (`frontend/web/src/App.tsx`: sign-in, one
   reader, a form, a table) into the feature's one page from
   [`references/react-client.md`](references/react-client.md) and
   [`references/ui-design.md`](references/ui-design.md): its primary
   view in the house look, leading with what the design's page line
   says, the resting state plain and the accent on one action. When
   `design/comp/index.html` exists
   ([`references/comp.md`](references/comp.md)), the page is the comp
   made live: the same classes and composition, its rows from the
   reader. Write the calls from the reference and do
   **not** open `frontend/api/**/*_rbt_react.ts`.
   `cd frontend && npm run build`.
9. Edit the starter's browser scenario (`tests/<pkg>_web.feature`,
   run by `tests/web_test.py`, which starts the frontend) into the
   page's, per `python/references/testing-web-app.md`
   (`uv run playwright install chromium` once); every web feature
   file runs from that one module. Run `uv run pytest` again, as the [`feature` skill](../feature/SKILL.md)'s step 4 says, unfiltered.
10. Start the app with the [`run` skill](../run/SKILL.md) (stopping
    the comp's server first when `design/.comp.pid` exists) and check
    the page in a headless browser (Playwright; in the Claude app never
    the Browser pane, which is for the user at the handoff): signed
    in, it shows all the demo data, its main action works, every
    filter or drawer it opens can be cleared or closed, no console
    errors, its first record shows within 2 seconds, timed per
    [`references/first-paint.md`](references/first-paint.md), and
    the layout checks in
    [`references/ui-design.md`](references/ui-design.md) ("Measure
    what can be measured") pass at desktop and phone width.
11. Run the whole suite once, in the background while the handoff is
    written (`feature` skill, "Report a full run once, at the end"),
    its result said once. Show what was built so the user can judge
    it, not admire it, word for word in the handoff's shape in
    [`app/references/design-messages.md`](../app/references/design-messages.md),
    each rule linked to the dashboard's Features page (`dashboard`
    skill, "Links to an Object or a Rule"), closing with its **Your
    turn** section and the dialog **What should I build next?**, the
    recommended feature first (on the prompt-by-prompt path no dialog: **Your
    turn** ends with the plain line "Say what's next."), as
    [`app/references/accept-design.md`](../app/references/accept-design.md)
    says. Open it with the Flywheel heading **Reboot Design · ready for
    your review**. Choosing or asking for a next feature, or keeping
    this one, accepts it (its `@wip`: the
    [`feature` skill](../feature/SKILL.md)); each acceptance is
    recorded as `accept-design.md` says.

**Each next feature**, when the user chooses it:

12. Say it in plain English in a few lines, with no question (the
    user chose it), write its `@wip` feature file
    ([`feature` skill](../feature/SKILL.md)), and show the part of
    the domain model it adds. If it changes the shape of existing
    data, say the demo data will be reset, and why.
13. Add its types and methods to the API (additive only, per
    `python/references/api-schema-evolution.md`), `rbt generate`,
    then its servicer with its rules, its demo data, its page or page
    change, and its scenarios. Before a non-additive change, stop the
    app with the `run` skill; start it again once the scenarios pass.
14. Stop `rbt dev run` (`run` skill, "Stopping the App") for the
    suite only: run the feature's own scenarios as the
    [`feature` skill](../feature/SKILL.md)'s step 4 says (in the
    foreground) and `uv run mypy backend/ tests/`, start it again, and
    check in the browser as in step 10 only the pages this feature
    added or changed (first paint and layout checks too). Then show
    what it changed as in step 11, with the same links: the objects
    added or changed, its actions and rules with their scenarios, the
    API change (the dashboard's changelog), and what is still to
    come; then the next question.

When the user says the app is done, offer an MCP UI in one line
(`app` skill, "At handoff"), unless they asked for only a web app.

## Update Flow

To change an existing app, read `AGENTS.md`, `.rbtrc`, the API, the
servicers, `main.py` and `frontend/web/src/App.tsx`, route the
change as
[`front-door-common.md`](../app/references/front-door-common.md)
("Routing a Change") says, and follow steps 12 to 14. An app with
persisted or deployed state follows
`python/references/api-schema-evolution.md`. Under `rbt dev run`,
edits (and `.env`) reload it; no restart. If the change moved a file,
added a state type or a page, changed a command or taught a rule,
update `AGENTS.md` in the same change
([`agents-md` skill](../agents-md/SKILL.md)).
