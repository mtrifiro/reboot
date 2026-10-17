---
title: Authorizers — When to Write Them, When to Skip
impact: HIGH
impactDescription: Whether to write `authorizer()` from day one or defer it depends on how identity is wired (`oauth=` works for both MCP and web; `token_verifier=` is the custom-IdP escape hatch)
tags: servicer, authorizer, allow, allow_if, auth, authorizers, production, oauth, anonymous, token-verifier
---

## Authorizers — When to Write Them, When to Skip

> **Critical:** authorizer rules are evaluated against the caller's
> **identity**. Whether identity exists during development depends on
> how the `Application(...)` is wired. The right "when to write
> authorizers" rule follows from that — don't sprinkle `allow()`
> everywhere to paper over the difference.

A Reboot Servicer may define `def authorizer(self)` returning a rule
instance (e.g. `allow_if(all=[has_verified_token])`). Reboot evaluates
that rule against `context.auth` before each method call.

## Rules from Day One

Both front doors wire identity with `Application(oauth=...)`: every
caller has a verified `context.auth.user_id`, in dev (`Development()`
mints a stable `dev-{hash}` id from a fake account picker) as in
prod, so every Servicer gets its `allow_if(...)` rules from day one.
`token_verifier=` is the exception, for an IdP `oauth=` cannot wrap;
until it is wired no caller has identity, so `authorizer()` may wait,
and the `rbt dev` warning is the TODO list. Without `authorizer()`,
`rbt dev` allows the call and warns every ~60s; `rbt serve` and
Reboot Cloud deny it (`PermissionDenied`). A `User` Servicer is
always enforced (`state_id_is_user_id` + `is_app_internal`), in dev
too, and rarely needs a custom rule.

## Don't Default to `allow()` Everywhere

`allow()` is an unconditional rule that permits every caller from
the public internet. It is not a "safe default" — it's an explicit
"this endpoint is public, unauthenticated" declaration. See
`auth-allow-deny.md` for the narrow legitimate uses and the
anti-patterns the agent should refuse.

## When You DO Define `authorizer()` — Return an Instance, Not a Class

The single most common bug when writing one: returning the function
itself instead of calling it.

```python
# Wrong — returns the function reference, not a rule:
def authorizer(self):
    return allow

# Right — constructs a rule instance:
def authorizer(self):
    return allow()
```

## Canonical Shapes

**App using `oauth=` (write real rules from day one):**

```python
from reboot.aio.auth.authorizers import allow_if, state_id_is_user_id
from reboot.aio.contexts import ReaderContext


class CounterServicer(Counter.Servicer):

    def authorizer(self):
        # Only the user whose ID matches this Counter's state ID may
        # call its methods. An `oauth=` provider (e.g. via
        # `OAuthProviderByEnvironment`) ensures every caller has a
        # `user_id`.
        return allow_if(all=[state_id_is_user_id])

    async def value(
        self, context: ReaderContext,
    ) -> Counter.ValueResponse:
        return Counter.ValueResponse(value=self.state.value)
```

**App using `token_verifier=` before the verifier is wired (defer):**

```python
class CatalogServicer(Catalog.Servicer):
    # No `authorizer()` yet — `rbt dev` allows and warns; this is
    # the TODO list for what needs a real rule before `rbt serve`.

    async def list(
        self, context: ReaderContext,
    ) -> Catalog.ListResponse:
        return Catalog.ListResponse(items=self.state.items)
```

## One Rule, or One Rule per Method

A rule returned from `def authorizer(self)` applies to every method on
the Servicer. To give methods different rules (e.g. allow reads but
gate writes), return the generated `<Type>.Authorizer`, which takes a
rule per method; see `auth-custom-predicates.md`.
