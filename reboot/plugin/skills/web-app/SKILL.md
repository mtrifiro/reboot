---
name: web-app
description: Build complete Reboot Web Apps — a Reboot backend behind a standalone browser-facing React frontend, served at a normal URL (not embedded in an MCP host). Layers on top of the python skill for backend mechanics; covers what's specific to standalone Web Apps — no MCP front door, no UI() methods, normal React/Vite SPA scaffolding, and Reboot auth for browser users. The backend stays ready for an MCP UI.
argument-hint: [<app-description>]
allowed-tools: Bash, Read, Write, Glob, Grep, Edit
---

# web-app — Build Reboot Web Apps

> **Version notices** from `rbt` (a mismatch, a newer Reboot): the [upgrade skill](../upgrade/SKILL.md).
>
> **Errors:** grep a fragment of the string in `python/references/errors.md` (never read whole); known defects and workarounds: [`KNOWN-ISSUES.md`](../../KNOWN-ISSUES.md).

Build complete Reboot Web Apps from a user description: a Reboot
backend behind a standalone React frontend served at a normal URL.

> **Reads from `python`.** This skill is the standalone-web-frontend
> layer on top of the Reboot Python framework. Anything about
> Servicers, Reboot contexts, refs, scheduling primitives,
> backend LLM / agent calls, error types, the testing harness,
> the `.rbtrc` shape, or pydantic API defaults belongs in
> `python` — load those references for those concerns. This
> skill covers what's _specific_ to standalone Web
> Apps: a React SPA at `frontend/web/`, the generated TypeScript hooks
> from `rbt generate --react=...`, regular auth flows (login form /
> cookies / OAuth), and the cross-cutting rules unique to that
> layer.

> **Dual-frontend apps are supported.** A single app can serve both
> a standalone web SPA _and_ an MCP front door from the same
> backend — they share `oauth=...`, the same `User` actor per
> upstream identity, and the same servicer code. If your app needs
> both frontends, also load the
> [`mcp-ui` skill](../mcp-ui/SKILL.md) for the MCP-specific
> additions (`mcp=Tool()`, `UI()`, MCPJam).
> This skill alone covers the web side.

## When to Use

- Building a new Reboot Web App from a description.
- Adding features, state, or UI to an existing Reboot Web App.
- Modifying state model, methods, or React UI in a Reboot Web App.
- Running an existing Reboot Web App — e.g. at the start of a new
  session: load the [`run` skill](../run/SKILL.md), which detects
  the app type and starts the backend and frontend.
- Putting a finished Web App in production — load the
  [`deploy` skill](../deploy/SKILL.md): backend on Reboot Cloud,
  frontend on a static host under the user's own custom domain.

## How a Web App Differs From an MCP UI

The Reboot backend is identical. The deltas are all on the frontend:

| Concern      | MCP UI (`mcp-ui`)                                                                               | Web App (this skill)                                                                      |
| ------------ | ----------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------- |
| Front door   | MCP host (ChatGPT, Claude, …) creates a `User` per user.                                        | Browser user signs in via `Application(oauth=...)`; same `User` per upstream identity.    |
| API exposure | `mcp=Tool()` on writer/transaction methods.                                                     | Methods exposed only through the generated React client.                                  |
| UI shape     | `UI()` methods → artifacts embedded in the MCP host.                                            | An SPA at `frontend/web/` opened at a URL.                                                |
| Vite config  | The `mcp-ui` scaffolding's: one-file `dist/mcp/<name>/index.html` per UI, served through Envoy. | A stock Vite SPA config rooted at `web/`, built to `dist/web/` at `base: "/"`.            |
| Test surface | MCPJam inspector.                                                                               | Scenarios that drive the app through Playwright (`python/references/testing-web-app.md`). |
| `User` type  | Required — the MCP entry point.                                                                 | Required too — it owns per-user state and keeps the backend ready for an MCP UI.          |

Backend mechanics (state, methods, Servicers, workflows, refs,
scheduling, stdlib actors, errors, auth predicates, testing) are
**unchanged** — load them from `python`.

## Auth in Web Apps

Web apps wire identity via
`Application(oauth=OAuth(provider=OAuthProviderByEnvironment(dev=Development(), prod=Google(...))))`
— the same parameter MCP UIs use. Reboot mounts its
built-in OAuth Authorization Server at `/__/oauth/*` and brokers
sign-in against the configured upstream IdP. Browser sessions
are carried in an HttpOnly `rbt_session` cookie set by
`/__/oauth/finish`; the framework reads it as a bearer on every
RPC, so user code only sees `context.auth.user_id` (same shape
as MCP).

> **`token_verifier=` is the escape hatch, not the default.** Use
> it only when you need to integrate with an IdP that the
> built-in `oauth=` providers don't cover (e.g. an enterprise
> SAML/OIDC broker you can't wrap as an `OAuthProvider`
> subclass), or when you need custom token semantics. For
> standard Google/GitHub/Auth0/anonymous sign-in, prefer
> `oauth=...`. The two compose: when both are set, Reboot's own
> verifier runs first and any token it has no opinion on
> (anything that is not a Reboot-minted access JWT) falls
> through to yours.

The imports, so you don't have to go looking for them:

```python
from reboot.aio.applications import Application
from reboot.aio.auth.oauth import OAuth
from reboot.aio.auth.oauth_providers import (
    Development,
    Google,                       # or GitHub, Auth0, …
    OAuthProviderByEnvironment,
)
```

Recommended sequence:

1. **Early development (no provider chosen yet):** configure
   `oauth=OAuth(provider=OAuthProviderByEnvironment(dev=Development(), prod=None))`.
   `Development()` is a built-in fake account picker that lets
   you sign in as any identity at `/__/oauth/start`; `prod=None`
   fails fast at startup if you accidentally `rbt serve` without
   choosing a real provider. Because every caller already has a
   verified `context.auth.user_id` under `Development()`, **write
   `authorizer()` on every Servicer from day one**, with
   `allow_if(...)` rules that run in dev exactly as in production
   (see `python/references/servicer-authorizer.md`,
   `python/references/auth-allow-if.md`, and
   `python/references/auth-built-in-predicates.md`). Do **not**
   paper over a missing rule with `allow()`; `allow()` means
   "public, unauthenticated internet endpoint" and survives into
   production.
2. **Before `rbt serve` / Reboot Cloud:** set `prod=Google(...)`
   (or `GitHub(...)`, `Auth0(...)`, your own `OAuthProvider`
   subclass). The authorizers need no second pass. The providers
   and what each needs:

   All arguments are keyword-only.

   | provider        | required arguments                        |
   | --------------- | ----------------------------------------- |
   | `Development()` | none — dev only, sign in as any identity  |
   | `Anonymous()`   | none — every visitor is a fresh identity  |
   | `Google(...)`   | `client_id=`, `client_secret=`            |
   | `GitHub(...)`   | `client_id=`, `client_secret=`            |
   | `Auth0(...)`    | `domain=`, `client_id=`, `client_secret=` |
   | `Ory(...)`      | `domain=`, `client_id=`, `client_secret=` |

   The registered providers (everything but `Development` and
   `Anonymous`) also take `scopes=` and `store_tokens=`; register
   `/__/oauth/callback` as the redirect URI with the provider.
   Every provider but `Anonymous` takes `claims=`, `Development()`
   included ([`auth-claims.md`](../python/references/auth-claims.md)).

   Add `claims=[...]` when you need identity fields such as the
   user's email, and `store_tokens=True` only when you will call
   that provider's own API as the user. **Choose it at deploy, not
   during the design**: the design and every build before deploy keep
   `prod=None`, and the [`deploy` skill](../deploy/SKILL.md) sets the
   provider. Choose deliberately then, before real users exist:
   `context.auth.user_id` is namespaced per provider, so switching
   providers after launch strands every existing user's state. Only
   reach for
   [mcp-ui/references/auth-oauth-providers.md](../mcp-ui/references/auth-oauth-providers.md)
   if you need to write a custom provider or debug a specific
   provider's flow.

   Tests build their own `Application(...)` rather than running
   `main.py`'s, whose `prod=None` arm and missing `allowed_origins`
   refuse to start anywhere but `rbt dev run`. List the same
   servicers, with the same authorizers, and wire identity per
   `python/references/testing-harness.md` ("Identity Wiring in
   Tests"): omit `oauth=` for backend scenarios, and for scenarios
   that open the web app use `Development()` for both arms plus
   `allowed_origins=[frontend.origin]`, as
   `python/references/testing-web-app.md` shows.

3. **Public, unauthenticated endpoints** (health checks, public
   sign-up, public catalog reads): mark these explicitly with
   `allow()`. That's the one legitimate use.

### Feeding the user's identity into hooks

With `Application(oauth=...)` the signed-in user's own state needs
no id-threading: call the `User` hook with **no arguments**. For
explicit-id hooks the rule is that the id must be real on every
render — never a placeholder — which is covered with the rest of
the hook mechanics in
[`references/react-client.md`](references/react-client.md).

### Calling external APIs on the user's behalf

To act **as the user** at an external service (call their Slack,
Google, a partner API), store that service's OAuth tokens encrypted in
an `OAuthTokenManager` and make the call inside a `Workflow`. When the
API belongs to the identity provider you already sign in with via
`Application(oauth=...)` (`Google` / `GitHub` / `Auth0`), use the
`store_tokens=True` shortcut: add the extra `scopes=[...]` your calls
need and the OAuth server captures the provider's tokens at sign-in
(Path A in `python/references/auth-external-api-calls.md`). For any
other service, run that service's OAuth flow yourself with your own
authorize/callback HTTP endpoints (a callback registered
`app_internal=True`) and call `OAuthTokenManager.store`. The full
host-agnostic recipe — endpoints, storage, reading tokens back, the
in-`Workflow` call, refresh, and erasure — is
`python/references/auth-external-api-calls.md` (Path B). Never store
tokens in a plain `str` field or hand-roll `Ciphertext`
(`python/references/stdlib-oauth-tokens.md`). If the service doesn't do
OAuth at all and the user pastes an **API key** instead, that key goes
through `Ciphertext` (the ciphertext id kept in state) — Path C in the
same recipe.

### Browser-side wiring (React)

All of it — the provider (and the `url` it must be given), the
generated hook surface, sign-in/sign-out, reading typed errors, and
why a hook's `id` must be real on every render — is in
[`references/react-client.md`](references/react-client.md). Read it
at the frontend step; don't reconstruct it from memory here.

## Which References to Read, and When

Everything you read stays in the conversation and is re-sent on
every later turn, so **read each reference at the step that needs
it** — not all of them up front — and read each one **once**. The
groups below are in build order, and each reference appears in
exactly one of them — the step that needs it.

> **Never read `mcp-ui/references/*` for a web app.** They cover
> the MCP frontend — `UI()` artifacts, the MCPJam inspector,
> `mcp/<name>/index.html` entries, the `vite.config.ts` and
> `build.mjs` that serve MCP UIs through Envoy, `mcp=Tool()`
> markers, popping a widget out into a web app. Reaching into them
> costs context and produces MCP-UI-shaped code (`mcp=Tool()`
> markers and `UI()` methods in an app with no MCP frontend). The
> web equivalents are
> [`references/react-client.md`](references/react-client.md) and the
> `python` references named below. The single exception is
> [mcp-ui/references/auth-oauth-providers.md](../mcp-ui/references/auth-oauth-providers.md),
> which is frontend-neutral: read it when you pick a real provider.

**Before the API definition:**

- `python/references/patterns-common-gotchas.md` — recurring trips
  (`self.ref().state_id`, kwargs convention, a `ref()` belongs to
  one context, the auto-constructed `User` type, `--name` vs.
  `--application-name`).
- `python/references/api-pydantic.md` — pydantic API rules (every
  Field needs a zero-value default; non-Optional `Model`-typed
  fields can't take defaults).
- `python/references/api-methods.md` — factory → context type
  mapping (Reader/Writer/Transaction/Workflow).
- `python/references/api-errors.md` — typed errors, when the API
  declares any.
- `python/references/state-collections.md` — **always read when the
  app has any "list of X" concept.** Decides whether each X should
  be its own state `Type` (most of the time, yes) and picks between
  in-state `list[Sub]`, in-state `list[str]` of foreign IDs, or an
  `OrderedMap` of foreign IDs. The trap is defaulting to
  `list[Todo]`/`list[Document]`/etc. on one parent for entity
  collections — see Step 1 of that reference.
- `python/references/state-nested-models.md` — the same rule from
  the nested-`Model` angle.

**Before the project shell** (`.rbtrc`, `pyproject.toml`,
`.mypy.ini`, `main.py`):

- `python/references/lifecycle-{project-setup,rbtrc,application-entry,initialize-hook}.md` — the canonical layout, the CLI flags, the
  `Application(...)` constructor, the `initialize` hook.

**Before the servicer:**

- `python/references/servicer-{reader,writer,transaction,constructor}.md` — one per context type you actually declared.
- `python/references/rpc-refs.md` — `self.ref().state_id` (never
  `self.state_id`); `self.ref().schedule(...)`.
- `python/references/rpc-calls.md` — kwargs, not Request wrappers.
- `python/references/rpc-constructor-calls.md` —
  `Service.create(context, id)` semantics.
- `python/references/servicer-workflow.md` — only when you declared
  a `Workflow`, and then top to bottom: the `@classmethod` /
  `WorkflowContext` declaration shape, the call-classification
  decision tree (Reboot scopes vs. `at_least_once` vs.
  `at_most_once`), `context.loop`, inline state writes,
  `until` / `until_changes`, and workflow exit semantics.

**Before the authorizers** (browser users — see "Auth in Web Apps"
above for the dev-vs-prod sequence):

- `python/references/servicer-authorizer.md` — **start here**.
  Explains `oauth=` (the default, with rules from day one) vs.
  `token_verifier=` (the escape hatch for custom IdPs, where rules
  may wait until the verifier is wired).
- `python/references/auth-allow-if.md`,
  `python/references/auth-built-in-predicates.md`,
  `python/references/auth-custom-predicates.md` — the predicate
  machinery once you're ready to write rules.
- `python/references/auth-allow-deny.md` — narrow uses of
  unconditional rules; specifically, when **not** to reach for
  `allow()`.
- `python/references/auth-external-api-calls.md` and
  `python/references/stdlib-oauth-tokens.md` — **calling an external
  service's API as the user**: custom OAuth endpoints (web apps use
  Path B — no `store_tokens=True` shortcut) → `OAuthTokenManager.store`
  → read back + call inside a `Workflow`. Never a plain `str` token
  field.

**Before the tests:**

- `python/references/testing-project-setup.md` — always.
- `python/references/testing-features.md` — the built-in steps'
  spelling; always.
- `python/references/patterns-idempotency.md` — it explains
  `IdempotencyUncertainError`, which is otherwise the one runtime
  error whose cause is not in any reference you have read.
- `python/references/testing-harness.md` and
  `testing-external-context.md` — for custom steps.
- `testing-failure-recovery.md` — the one to read whenever the app
  has a spawned task, a `Workflow`, or `schedule()`d work: it covers
  restarting the app under test and asserting that work survived.
- [`feature/SKILL.md`](../feature/SKILL.md) — the order of work
  around the feature files (agree in English, tag `@wip`, iterate on
  scenarios).

**The two parts.** Every group above this line is the backend part.
The groups from here on are the frontend part: read them only when the
frontend part starts, once the user says to build the frontend (or, on
the automatic paths, once every feature's backend passes), never
before, and not at all when the user stops after the backend.

**Before the frontend:**

- [`references/ui-design.md`](references/ui-design.md) — the
  primary view for each task, and the house look: copy the
  stylesheet and theme toggle, set the design's accent, build the
  pages from its classes; the sidebar layout, a brand, logo and
  favicon, and the checks.
- [`references/react-client.md`](references/react-client.md) — the
  `frontend/` shell (the stock Vite config rooted at `web/`,
  including the `server.host` the browser needs), the backend URL
  (`VITE_REBOOT_URL` — the default detection resolves to Vite's
  origin, not the backend's), sign-in/sign-out, and how a typed
  backend error becomes a message the user sees.
- `python/references/react-generated-client.md` — what
  `rbt generate --react=` emits: the `use<Type>()` overloads, the
  three-field reader return, why mutations resolve to
  `{ response, aborted }` instead of throwing, the typed error
  classes, and the snake→camel naming rules.

**Before the browser tests** (the frontend part):
`python/references/testing-web-app.md` (the `frontend` fixture, the web
app steps, and the accessible markup the page needs).

**Before running the app:** the [`run` skill](../run/SKILL.md).

If you find yourself grepping the framework's installed source or a
generated file to answer a question, the next section is for you —
do not explore it in the main conversation.

## Never Read Generated or Installed Source in the Main Thread

Never a whole generated or installed file (`*_rbt.py`,
`*_rbt_react.ts`, `site-packages/`, `node_modules/`): use the
references, and bound any search hard
([`app/references/front-door-common.md`](../app/references/front-door-common.md)).

## Workflow: Propose the Design, Then Build

**Always work out the design before writing code.** The state model
is the foundation — getting entities, field types, or method types
wrong means regenerating everything across the project.
The design is a proposal until the user accepts it: call it, and
every part of it such as the data model, proposed, never settled, set
or final, in the design and in every status line. Ask one round of
scope questions before it (step 2 below), then build without
waiting. The question of how to build has two answers: one feature at a time,
where after each the user sees it running, understands it and
chooses the next, so the design is accepted piece by piece; or a
full prototype first, accepted at its handoff.

This is the first stage of the **Reboot Flywheel**: Design, then
Prove, then Observe, each ending in a decision that is the user's.
[`app/references/flywheel.md`](../app/references/flywheel.md) has
the stages, the heading each decision opens with, and the routing
rule that sends a change to the design back to Design.

### Design Phase

0. List the app's features, one sentence each, in the order they
   will be built. Each is agreed in plain English and written down as
   a `@wip` feature file by the
   [`feature` skill](../feature/SKILL.md) when its turn comes, before
   its part of the API exists.
1. Analyze the user's description using the State Model Assessment
   below.
2. Ask one round of scope questions first, from the prompt alone,
   before reading any reference or showing a design: one question
   dialog (`AskUserQuestion` where available). Built from the
   [`app` skill](../app/SKILL.md), its opening round replaces this
   one: nothing else is asked before the design, and **How should it
   be built?** comes once, after the design
   ([`app/references/design-first.md`](../app/references/design-first.md),
   section 3). Invoked directly, the first question is how to build
   it, unless the prompt already says: "One feature at a time, so you
   understand each part as it's built" (recommended) or "A full
   working prototype first, then finished feature by feature". Then
   at most three more, on what the prompt
   left open and an answer would change most, such as who signs in
   with which roles and what the app keeps track of. Give each question two to four options, the simplest
   first and marked as recommended, so accepting every
   recommendation is one answer. Never an option that only
   means "say what": every dialog has its own free answer. Don't ask about the look: when the
   user named no brand, pick the accent that suits the domain from
   the ones [`references/ui-design.md`](references/ui-design.md)
   lists, and say in
   the brief that it was picked for them and is easy to change later,
   to another color or to their brand. Name the app too, unless the
   prompt gives a name, and say the same of it. Don't ask what the design can
   decide well on its own. Never ask about time zones: every date
   and time is in the user's own time zone unless they say otherwise,
   and it goes under **Assumed** in the decisions log. Ask nothing more until the handoff.
3. Read the references for the API, then show the proposed design,
   word for word in the shape of
   [`app/references/design-messages.md`](../app/references/design-messages.md),
   with the answers in it, before writing the API. What it decides: the brief (who
   uses the app and on what screen, the task, the one question its
   main page answers, the accent); the whole domain model, one line
   per type, saying what it is and how it relates to the others; the
   features in build order, the first marked and why it comes first.
   The first feature is the one that shows the app's central object
   and its main behavior on one page, with at least one rule the
   user can see it keep (for a hotel, the rooms and their status on
   a floor plan, where a room can't be checked into until it's
   clean). For the first feature only, or for every feature when the
   user chose a full prototype:
   - Application types: state shape (fields, types, tags).
   - Method map, one line per method: its method type
     (Reader/Writer/Transaction/Workflow) and its role for an AI
     caller (a tool the AI calls, a `UI()` view, or for people only),
     even though the MCP UI comes later.
   - Route surface: which pages does the SPA need, each page's
     primary view (the domain's own shape, such as a floor plan, a
     board, a timeline or a calendar, worked on directly; a filtered
     list for lookup), and which methods each page calls. A page of
     many records reads them all through one reader on their parent.
   - `User` type: always. It owns per-user state and routes creation,
     and it is the MCP front door if an MCP UI is added later.
   - Auth: who signs in, and what an anonymous visitor may read.
   - Ready for an MCP UI: each method's `description=` written for
     an AI caller from the start. A web app keeps `mcp=None` until an
     MCP UI is added; then only `mcp=` changes, which a deployed app
     allows (`python/references/api-schema-evolution.md`).
4. Then build it the way the user chose: one feature at a time, by
   the Step-by-Step Build Flow below, or the full prototype, by
   [`references/full-build.md`](references/full-build.md).

For updates to existing apps, still work the design first: read
current state, state the changes, then modify.

### Writing the Design for a Human Reader

Write the design for a person who hasn't read these skills: no
skill-internal terms, and for every choice the what and a one-clause
why in the domain's terms, as
[`app/references/front-door-common.md`](../app/references/front-door-common.md)
says, with its examples.

## State Model Assessment

Before writing code, analyze the user's request:

1. **Application types — decompose aggressively.** List every
   distinct entity the user is going to add / edit / list / find
   over time (todos, documents, posts, accounts, people, …).
   **Each entity becomes its own `Type` with its own state**, even
   when "each user only has a few of them". Anything you can
   imagine being `add`-ed / `remove`-d / `find`-ed by name has its
   own identity and belongs in its own actor. The default wrong
   move is packing everything into one parent's state as
   `list[Todo]` (or `list[Document]`, `list[Post]`, …) — that
   flattens N actors into one, prevents per-entity auth/methods,
   and forces a full rewrite when the collection grows. See
   `python/references/state-collections.md` Step 1 for the full
   decomposition signal list.
2. **Per-user state?** If yes, declare a `User` type and route
   creation through it the same way `mcp-ui` does — the
   `User`-front-door pattern is independent of MCP. If the app is
   anonymous or all users share state, skip `User`.
3. **Container shape for each collection.** Once an entity is its
   own `Type`, parents store **references**, not objects. Three
   shapes (full table + worked example in
   `python/references/state-collections.md`):
   - `list[Sub]` of non-state `Model`s — bounded sub-records with
     no identity of their own (line items on an Order, tags on a
     Post). NOT for entity collections.
   - `list[str]` of foreign state IDs — bounded entity collection
     (low hundreds, occasionally low thousands) you always read
     whole.
   - `OrderedMap` of foreign state IDs — collection grows without
     bound, needs pagination / range queries / ordered iteration.
     The default choice for any "list of things the user keeps
     adding to".
4. **State shape (per type)**: Fields, types — lists, nested
   objects, primitives. Each gets `Field(tag=N)`. Nested `Model`
   sub-objects owned 1:1 by a parent state must be
   `Optional[X] = Field(tag=N, default=None)` and hydrated in the
   parent's factory `create` Writer; non-Optional `Model`-typed
   fields reject `default=` / `default_factory=`. Full rules in
   `python/references/api-pydantic.md`.
5. **Operations**: Map to the right method type:
   - `Reader` — read-only queries.
   - `Writer` — single-state mutations.
   - `Transaction` — multi-state atomic operations.
   - `Workflow` — long-running control flows with loops, scheduling,
     and idempotency helpers.
6. **Pages / routes**: Which SPA routes exist? Which methods does
   each page call? React hooks generated by `rbt generate --react=...`
   wrap the calls.
7. **Auth**: Anonymous-only, public-read + authed-write, fully
   locked down, …? See `python/references/auth-*.md`.
8. **Names**: Name each type for what it holds and is for, in
   the domain's own words, never for its key or its time period.
   A type keyed by a gate and a date is `GateSchedule` (one gate's
   flights and closures for a day), not `GateDay`; a type keyed by
   a date is `DispatchBoard` (the day's flights, and the rule that
   no aircraft or pilot is double-booked), not `DispatchDay` or
   `Day`. The key says how an instance is found; the name says
   what it is. Test each name: would someone in the domain know
   what it holds without being told its id? If not, rename it
   before the API is written, when a rename costs one line.

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

In development the Vite dev server (`cd frontend && npm run dev`)
serves the SPA at its own origin, `http://localhost:5173/` by
default, and the SPA calls the backend at `VITE_REBOOT_URL`. Built,
it lands in `frontend/dist/web/` with `base: "/"`, which a static
host, or the backend, can serve at `/`. An app that later adds an
MCP frontend keeps this tree, adds `frontend/mcp/<name>/` beside
`web/`, and swaps in the `mcp-ui` skill's `vite.config.ts` and
`build.mjs`, which serve both frontends through Envoy.

## Step-by-Step Build Flow

The build's task list, where the agent keeps one, uses the items in
[`app/references/task-list.md`](../app/references/task-list.md), word
for word.

**All commands run from the application directory.** The build
finishes one feature, with one page, and shows it; then the user
chooses the next feature, and the loop below adds it. Each feature is
built whole, with its rules and scenarios, so what the user sees
works as it will in the finished app.

**The first feature:**

1. Create `.python-version`, `pyproject.toml`, `.rbtrc`, and
   `.mypy.ini` — same shape as in
   `python/references/lifecycle-{project-setup,rbtrc}.md`. In
   `.rbtrc`, point the React codegen at `frontend/api`:
   ```sh
   generate --react=frontend/api
   ```
   Then give the project its `AGENTS.md` and `CLAUDE.md` with the
   [`agents-md` skill](../agents-md/SKILL.md), naming the API and
   servicer files the design settled on.
2. `uv sync`.
3. Write the first feature's `@wip` feature file with the
   [`feature` skill](../feature/SKILL.md), then the API for that
   feature only (`api/<pkg>/v1/<name>.py`): the types and methods it
   needs, plus `User`. Later features add to it. Pydantic rules live
   in `python/references/api-pydantic.md`; method marker →
   context-type rules in `python/references/api-methods.md`. Every
   `Reader`, `Writer`, `Transaction` and `Workflow` still requires
   the `mcp=` argument: write `mcp=None` on each one.
4. `uv run rbt generate`. Don't read what it wrote: the signature
   your servicer must match is in `python/references/api-methods.md`
   ("The Servicer Signature Each Declaration Obliges"). Then start
   the developer dashboard — load the
   [`dashboard` skill](../dashboard/SKILL.md) and follow it — and go
   on without waiting for it. If it fails to come up, say so in one
   sentence and keep building. Built from the `app` skill, the first
   feature instead waits for it and asks "Build on this domain model?" (the model check)
   ([`app/references/design-first.md`](../app/references/design-first.md),
   "The domain model, once") before step 5.
5. Write the servicer for the feature, with its rules and its real
   `authorizer()`, context-type patterns in
   `python/references/servicer-*.md`.
6. Write `main.py` (`python/references/lifecycle-application-entry.md`)
   with believable demo data for this feature's objects from
   `initialize`, only under `rbt dev run`, seeded as
   `python/references/lifecycle-seeding.md` says. Then write the
   feature's scenarios in the built-in steps of
   `python/references/testing-features.md`, run `uv run pytest` as [`feature/SKILL.md`](../feature/SKILL.md)'s "Report a full run once, at the end" says and
   `uv run mypy backend/ tests/` with `rbt dev run` stopped (`run`
   skill, "Stopping the App"), and fix what fails before any page.
7. Scaffold the frontend at `frontend/`
   (`npm create vite@latest frontend -- --template react-ts`), shape
   it as [`references/react-client.md`](references/react-client.md)
   shows, `cd frontend && npm install`, and run `uv run rbt generate`
   again for the React bindings.
8. Build the feature's one page from
   [`references/react-client.md`](references/react-client.md) and
   [`references/ui-design.md`](references/ui-design.md): its primary
   view in the house look, with sign-in. Write the calls from the
   reference and do **not** open `frontend/api/**/*_rbt_react.ts`.
   `cd frontend && npm run build`.
9. Add one web app scenario for the page per
   `python/references/testing-web-app.md` (it installs Playwright).
   Every feature file then runs from the one test module that
   starts the frontend. Run `uv run pytest` again, as [`feature/SKILL.md`](../feature/SKILL.md)'s "Report a full run once, at the end" says.
10. Start the app with the [`run` skill](../run/SKILL.md) and check
    the page in a headless browser (Playwright; in the Claude app never
    the Browser pane, which is for the user at the handoff): signed
    in, it shows the whole demo data, its main action works, every
    filter or drawer it opens can be cleared or closed, no console
    errors, the main page shows its first record within 2 seconds,
    timed as [`references/first-paint.md`](references/first-paint.md)
    says, and the layout checks in
    [`references/ui-design.md`](references/ui-design.md) ("Measure
    what can be measured") pass at desktop and phone width.
11. Show what was built so the user can judge it, not admire it,
    word for word in the handoff's shape in
    [`app/references/design-messages.md`](../app/references/design-messages.md):
    what it keeps track of, what it does with each rule linked to the
    dashboard's Features page (`dashboard` skill, "Links to an Object
    or a Rule"), how to check it, what's not built yet, and notes.
    Last, close as
    [`app/references/accept-design.md`](../app/references/accept-design.md)
    says: it ends with the **Your turn** section of
    [`app/references/design-messages.md`](../app/references/design-messages.md),
    what to try, where to look, and the features to ask for next, the
    recommended one first, then the dialog **What should I build next?**
    with those features as its options. The user's choosing or asking for a next
    feature (or saying to keep this one) accepts this one (its
    `@wip`: the [`feature` skill](../feature/SKILL.md)). Open it with the
    Flywheel heading **Reboot Design · ready for your review**; the
    first time, record it as `app/references/accept-design.md` says; each
    acceptance is recorded the same way
    ([`app/references/accept-design.md`](../app/references/accept-design.md)).

**Each next feature**, when the user chooses it:

12. Say it in plain English in a few lines, with no question (the
    user chose it), and write its `@wip` feature file
    ([`feature` skill](../feature/SKILL.md)); show the part of the
    domain model it adds. If it changes the shape of existing
    data, say the demo data will be reset, and why.
13. Add its types and methods to the API (additive only, per
    `python/references/api-schema-evolution.md`), `rbt generate`,
    then its servicer with its rules, its demo data, its page or the
    change to an existing page, and its scenarios. Before a change
    that isn't additive, stop the app with the `run` skill; start it
    again once the scenarios pass.
14. Stop `rbt dev run` (`run` skill, "Stopping the App"), run
    `uv run pytest` as [`feature/SKILL.md`](../feature/SKILL.md)'s "Report a full run once, at the end" says and `uv run mypy backend/ tests/`, start it again, check the
    page in the browser as in step 10, and show what this feature
    changed as in step 11, with the same links: the objects it added
    or changed, its actions and rules with their scenarios, what
    changed in the API
    (the dashboard's changelog), and what is still to come; then the
    next question.

When the user says the app is done, offer an MCP UI in one line
(`app` skill, "At handoff"), unless they asked for only a web app.

## Update Flow

To change an existing app, read `AGENTS.md`, `.rbtrc`, the API, the servicers,
`main.py` and `frontend/web/src/App.tsx`, then route the change by
the Flywheel's routing rule (`app/references/flywheel.md`;
`python3 scripts/model_diff.py` sorts it): a change
to a domain object, a rule or who may call goes back to Design;
anything else stays in Prove. A design change the user asked for is
built and judged at the next handoff; one they didn't ask for is shown
and asked about before code
([`app/references/accept-design.md`](../app/references/accept-design.md)). Then follow
steps 12 to 14.
An app with persisted or deployed state follows
`python/references/api-schema-evolution.md`. Under `rbt dev run`,
edits (and `.env`) reload it; no restart.
If the change moved a file, added a state type or a page, changed a
command, or taught a rule, update `AGENTS.md` in the same change
([`agents-md` skill](../agents-md/SKILL.md)).
