---
title: "The Authorizer's Rules: `allow_if` and the Built-In Predicates"
impact: HIGH
impactDescription: All non-trivial authorization is composed from `allow_if` and predicates; the three shipped predicates cover most auth needs without custom code
tags: auth, allow_if, predicate, all, any, composition, has_verified_token, is_app_internal, state_id_is_user_id
---

## The Authorizer's Rules: `allow_if` and the Built-In Predicates

> **Critical:** pass exactly one of `all=` **or** `any=` to `allow_if`
> (passing both asserts at runtime). For `all=`, list cheap
> auth-establishing predicates first — short-circuiting + later
> predicates can rely on earlier `Ok` results. Three shipped predicates
> cover most needs: `has_verified_token` (any verified caller),
> `is_app_internal` (only same-app internal calls — the right gate for
> stdlib-style helpers), `state_id_is_user_id` (per-user resources
> where actor IDs are user IDs).

## Compose Predicates with `allow_if(all=...)` / `allow_if(any=...)`

`allow_if` composes a list of predicate callables into an authorizer
rule. Pass `all=[...]` to require every predicate to return `Ok`, or
`any=[...]` to require at least one. The two are mutually exclusive —
exactly one keyword is allowed.

**Incorrect (passing both `all` and `any`):**

```python
allow_if(all=[has_verified_token], any=[is_app_internal])  # asserts at runtime
```

**Correct (one or the other):**

```python
from reboot.aio.auth.authorizers import (
    allow_if, has_verified_token, is_app_internal,
)


def authorizer(self):
    # Caller must be authenticated AND match some other condition.
    return allow_if(all=[has_verified_token, my_predicate])


def authorizer(self):
    # Either internal-app calls OR authenticated user-facing calls work.
    return allow_if(any=[is_app_internal, has_verified_token])
```

## Evaluation Order Matters for `all`

Predicates are invoked one at a time. For `all=[...]`, list cheap or
authentication-establishing predicates first — later predicates can rely
on earlier ones having returned `Ok` (so e.g. a predicate that reads
`context.auth.user_id` can come after `has_verified_token`).

## Short-Circuiting

`all` short-circuits on the first `PermissionDenied` or
`Unauthenticated`. `any` short-circuits on the first `Ok`.

## Aggregated Decision

When `any=[...]` runs out without finding an `Ok`:

- If at least one predicate returned `PermissionDenied`, the aggregate
  is `PermissionDenied`.
- Otherwise (all returned `Unauthenticated`), the aggregate is
  `Unauthenticated`.

This shape lets callers know whether to retry with auth (the call was
unauthenticated) or stop trying entirely (denied).

## Stdlib Uses It Internally

`OrderedMapServicer` defaults to
`allow_if(all=[is_app_internal])` — only other Reboot code in the same
app can call it. Apply the same pattern when a stdlib-style helper
shouldn't be reachable from outside.

## Built-In Authorizer Predicates

`reboot.aio.auth.authorizers` ships three predicate callables. Each takes
keyword args and returns one of `Ok` / `Unauthenticated` /
`PermissionDenied`. Compose them via `allow_if`.

### `has_verified_token`

```python
def has_verified_token(*, context: ReaderContext, **kwargs):
    if context.auth is None:
        return Unauthenticated()
    return Ok()
```

Returns `Ok` when the caller has any verified auth token. It does **not**
verify that the token's user is registered with the application — only
that the token itself is valid. Use it as a baseline gate; combine with
other predicates for "authenticated AND \_\_\_". A call made from inside
another servicer method on behalf of a verified caller also passes:
`context.auth` follows the call (`auth-context-propagation.md`).

```python
return allow_if(all=[has_verified_token, can_access_resource])
```

### `is_app_internal`

```python
def is_app_internal(*, context: ReaderContext, **kwargs):
    if context.app_internal:
        return Ok()
    return PermissionDenied()
```

Returns `Ok` when the call originates from inside the same Reboot app
(another Servicer calling this one). External clients always get
`PermissionDenied`. This is the right gate for stdlib-style internal
helpers. An app-internal call may still carry a `context.auth` — the
signed-in person the calling method ran for — so `is_app_internal` and
an owner rule can both match the same call. It holds for every call
made from inside the app's own code, nested calls included (a
transaction's calls into other actors, a `User.set_claims` the
framework invokes), and never for an external client, so a type that
other actors call into and signed-in people also reach gates with
`allow_if(any=[is_app_internal, <the user rule>])`.

```python
# The OrderedMap servicer's default:
return allow_if(all=[is_app_internal])
```

### `state_id_is_user_id`

```python
def state_id_is_user_id(*, context: ReaderContext, **kwargs):
    if context.auth is None or context.auth.user_id is None:
        return Unauthenticated()
    if context.auth.user_id == context.state_id:
        return Ok()
    return PermissionDenied()
```

Returns `Ok` only when the actor's `state_id` equals the caller's
authenticated `user_id`. Use this when an actor _is_ a user — e.g.
`UserProfileServicer` whose state IDs are user IDs.

```python
return allow_if(all=[state_id_is_user_id])
```

## Common Compositions

```python
# Internal-only:
allow_if(all=[is_app_internal])

# Public to authenticated users:
allow_if(all=[has_verified_token])

# Authenticated and matching the actor's user-keyed identity:
allow_if(all=[state_id_is_user_id])  # implies has_verified_token

# Either internal call or authenticated user:
allow_if(any=[is_app_internal, has_verified_token])
```

## Self-Scheduled Workflows Need `is_app_internal`

If your Servicer has methods that schedule workflows on the
**same actor** (`self.ref().schedule().<workflow>(context)`),
the workflow runs **app-internally** — it has no bearer token and no
`context.auth`, even when the original transaction was authenticated
as a user. (A call made directly, not scheduled, does carry the
caller's `context.auth`; see `auth-context-propagation.md`.)
Authorizers gated only on user identity will deny the framework's
scheduled call:

```python
# WRONG — user-only auth blocks the framework's scheduled
# workflow on the same actor.
def authorizer(self):
    return allow_if(all=[state_id_is_user_id])

async def place(self, context: TransactionContext, request):
    # Place is called by the user (alice), but `pay` is scheduled
    # — runs as an app-internal workflow with no token.
    await self.ref().schedule().pay(context)
    # → at workflow launch, auth check on `Pay` raises
    #   `Unauthenticated`; `Place` gets aborted.

# RIGHT — accept either the owner OR an internal call.
def authorizer(self):
    return allow_if(any=[state_id_is_user_id, is_app_internal])
```

Use `any=[state_id_is_user_id, is_app_internal]` whenever the
actor has self-scheduled workflows. The pattern is canonical
for "user-owned actors with background work."

## Predicates Always Take `**kwargs`

Predicates receive `context`, `state`, and `request` keyword args. Always
include `**kwargs` in the signature so newly-added args don't break the
predicate. The shipped predicates follow this convention; mirror it in
your own (see `auth-custom-predicates.md`).
