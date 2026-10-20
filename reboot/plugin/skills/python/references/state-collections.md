---
title: Pick the Right Shape for Each Collection
impact: HIGH
impactDescription: Putting an unbounded collection in-state, or flattening an entity into `list[Sub]` when it has its own identity, forces a full data-model rewrite once the app grows.
tags: state, collections, list, dict, OrderedMap, decomposition, sub-records, entity, ids
---

## Pick the Right Shape for Each Collection

> **Critical:** if a contained item has its own identity, lifecycle,
> or methods, it must be its **own state `Type`** — not a nested
> `Model` inside the parent. The parent then stores **IDs**, not the
> full objects. Choosing `list[X]` for an entity collection ("each
> user has many People") works in a 10-row demo but forces a full
> data-model rewrite the moment the collection grows or each entity
> grows its own methods / auth / lifecycle.

### Step 1: Decompose Before Choosing a Container

Before picking a container shape, consider whether the **item** wants to
be its own state `Type`. If **any** of these is true, it does:

- It has a lifecycle of its own (created, edited, deleted on its
  own schedule independent of the parent).
- It has methods you'd want to call on it directly
  (`Person.add_event(...)`, `Account.deposit(...)`).
- It needs its own authorizer (different auth from the parent).
- Multiple parents could reference it.
- It has nested collections of its own that will grow over time.
- It's a noun your domain talks about (`Person`, `Order`, `Post`,
  `Account`, `Message`, `Event`) rather than a field group
  (`Address`, `Preferences`, `LineItem`).

If yes → declare `Type(state=ItemState, methods=...)` for it and
have the parent reference items by their **string IDs**.

If no — the item is a flat sub-record that lives and dies with the
parent (an address on an Order, tags on a Post, a preferences blob
on a Guest) — keep it inline. See `state-nested-models.md`.

> **Warning signs in prompts.** Nouns combined with verbs like "add /
> remove / list / find / show one" is almost always its own state
> `Type`. "Each user has N of them" = **N actors**, not N rows on one
> actor.

> **Externally-synced collections are unbounded — and the verb
> test above misses them.** A collection mirrored from an outside
> source — a repo's issues, a mailbox's messages, a feed's entries
> — is an entity collection, unbounded by definition: size it to
> the **source**, never to the demo. Each synced item is its own
> state `Type`; the parent indexes them with Shape C below.

### Step 2: Pick the Container Shape

Three shapes show up:

| Shape                                                       | When to pick                                                                                                                                                                                            | Pitfalls                                                                                                      |
| ----------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------- |
| **A. `list[Sub]` / `dict[str, Sub]` of non-state `Model`s** | Sub-records with **no identity of their own** that live and die with the parent. Bounded — dozens at most. E.g. line items on an Order, tags on a Post, fields in a Config blob.                        | Every write rewrites the full list. No pagination. Cannot grow without bound.                                 |
| **B. `list[str]` / `dict[str, str]` of foreign state IDs**  | Items are their own state `Type` (Step 1 said yes) **and** the collection stays bounded — typically a few hundred, low thousands at most. You almost always read the whole index. No pagination needed. | Each parent write rewrites the full list of IDs. Doesn't scale past low thousands.                            |
| **C. `OrderedMap` of foreign state IDs**                    | Items are their own state `Type` **and** the collection grows without bound, **or** needs pagination, range queries, or ordered iteration.                                                              | Extra hop to a stdlib actor. Entry values use the `value` / `bytes` / `any` envelope. `range` needs `limit=`. |

> **"Bounded" is a domain fact, not a knob you control.** If you
> are reaching for `MAX_ITEMS = 40` or "keep only the latest 50"
> so a collection qualifies as bounded and lands in Shape A or B,
> stop — it is **unbounded**. The cap is a product decision and
> belongs in a reader or view, never in the state shape. A genuine
> bound is one the domain itself fixes: a board has 9 cells, an
> order has at most 100 line items.

Shapes B and C differ only in **how the parent indexes** the items;
choose C up front if the collection might grow without bound.

#### Shape A — `list[Sub]` of Non-State `Model`s

For sub-records that conceptually belong **to** the parent and have
no identity of their own:

```python
from reboot.api import API, Field, Methods, Model, Reader, Type, Writer


class LineItem(Model):
    sku: str = Field(tag=1, default="")
    quantity: int = Field(tag=2, default=0)


class OrderState(Model):
    items: list[LineItem] = Field(tag=1, default_factory=list)
```

#### Shape B — `list[str]` / `dict[str, str]` of Foreign State IDs

When Step 1 said yes **and** the collection is naturally bounded
(an Organization's board members, a House's rooms, the accounts a
Bank seeds at startup):

```python
class OrgState(Model):
    member_user_ids: list[str] = Field(tag=1, default_factory=list)


class OrgServicer(Org.Servicer):

    async def add_member(
        self, context: TransactionContext, request: Org.AddMemberRequest,
    ) -> None:
        # `User` is its own state Type.
        self.state.member_user_ids.append(request.user_id)

    async def members(
        self, context: ReaderContext,
    ) -> Org.MembersResponse:
        return Org.MembersResponse(
            user_ids=self.state.member_user_ids,
        )
```

#### Shape C — `OrderedMap` of Foreign State IDs

When the collection can grow without bound, needs pagination, or
needs ordered iteration. The parent stores the **map's ID** (once,
at construction) and forwards reads/writes through the map.

> **Anti-pattern — do not synthesize the map ID inline from the
> parent's `state_id`** (e.g.
> `OrderedMap.ref(f"{self.ref().state_id}-people")` or
> `OrderedMap.ref(f"{context.state_id}-people")` inside a workflow).
> **Always** add a `<thing>_index_id: str` field to the parent's
> state, allocate it once in the constructor (`uuid4()`), and
> reference the map via `OrderedMap.ref(self.state.<id>)`. The
> general rule — for any cross-`Type` reference — is in
> "Relationships Between State Types" below.

```python
from reboot.std.collections.ordered_map.v1.ordered_map import (
    OrderedMap, ordered_map_library,
)
from uuid import uuid4
from reboot.uuidv7 import uuid7


class UserState(Model):
    # ID of the OrderedMap actor that indexes this user's People.
    # Allocated once at User construction; never changes.
    people_index_id: str = Field(tag=1, default="")


class UserServicer(User.Servicer):

    # The auto-constructed `User`'s constructor, a `Transaction`
    # Reboot adds to the API and calls when the user first signs in.
    # A constructor never runs on an existing state, so the body
    # needs no `context.constructor` check; see gotcha 21 in
    # `patterns-common-gotchas.md`.
    async def create(self, context: TransactionContext) -> None:
        # Just allocate the ID — the OrderedMap is constructed
        # implicitly on the first `insert`. Until then, reading it
        # aborts with `StateNotConstructed`; see
        # `stdlib-ordered-map.md`.
        self.state.people_index_id = str(uuid4())

    async def add_person(
        self,
        context: TransactionContext,
        request: User.AddPersonRequest,
    ) -> User.AddPersonResponse:
        # `Person` is its own state Type with `factory=True` `create`.
        person, _ = await Person.create(
            context,
            name=request.name,
            birthday=request.birthday,
        )
        # UUIDv7 keys iterate in time order; for
        # name-sorted iteration, use a name-prefixed key instead.
        await OrderedMap.ref(self.state.people_index_id).insert(
            context,
            key=str(uuid7()),
            bytes=person.state_id.encode(),
        )
        return User.AddPersonResponse(person_id=person.state_id)

    async def list_people(
        self,
        context: ReaderContext,
        request: User.ListPeopleRequest,
    ) -> User.ListPeopleResponse:
        page = await OrderedMap.ref(
            self.state.people_index_id,
        ).range(
            context, start_key=request.cursor, limit=32,
        )
        return User.ListPeopleResponse(
            person_ids=[e.bytes.decode() for e in page.entries],
            next_cursor=(
                page.entries[-1].key if page.entries else ""
            ),
        )
```

Register `ordered_map_library()` in `Application(libraries=[...])`
— see `stdlib-ordered-map.md` for the full method surface and the
value-field options (`value` / `bytes` / `any`).

### Relationships Between State Types

The rule for `OrderedMap` IDs is one instance of a general rule:
**any reference from one state `Type` to another must be a persisted
ID field on the parent — never a string derived inline from the
owner's `state_id`.** This applies equally to user-defined `Type`s
(a User pointing at a Profile actor; an Order pointing at an
Invoice actor) and to every stdlib state type (`OrderedMap`,
`Queue`, `Item`, `Presence`, `Topic`).

The reasoning behind these rules, with the correct and wrong form
side by side, is [`state-collections-why.md`](state-collections-why.md);
read it when a rule is in doubt.

### Deleting a State

Reboot has no call that deletes a state. "Deleting" a todo, a
document, or a person means removing its id from every collection
that references it (`OrderedMap.remove`, or dropping it from a
`list[str]`), in the same `Transaction` that decides to delete it.
The state itself stays behind, unreachable through the app. If its
contents must actually go (personal data, a secret), also call a
writer on it that clears its fields, and have its readers treat the
cleared state as gone.

### Decision Flow (Summary)

1. **Does the item have identity / lifecycle / its own methods?**
   - **No** → Shape A (`list[Sub]` of non-state `Model`s).
   - **Yes** → Make it its own `Type(state=...)`, then continue.
2. **How many?**
   - Bounded, ≲ low thousands, always read whole → **Shape B**
     (`list[str]` of IDs).
   - Unbounded, or needs pagination / range / ordered iteration →
     **Shape C** (`OrderedMap`).

### Anti-Patterns

- `UserState.people: list[Person]` when `Person` is a domain
  entity: promote it to its own `Type`, Shape B or C.
- `Type(state=X)` _and_ `list[X]` / `dict[str, X]` as a state
  field: state inside state (`state-nested-models.md`).
- `list[str]` for an unbounded collection: Shape C from the start.
- A `MAX_ITEMS` cap invented to qualify for Shape A or B: Shape C,
  and cap the _view_ in a reader.
- An externally-synced collection held in-state: each synced item
  its own `Type`, indexed with Shape C.
- `OrderedMap` for a sub-dozen, domain-bounded collection: Shape A
  or B.
- A related actor's ID synthesized from the parent's `state_id`: a
  persisted `<thing>_index_id` field and
  `OrderedMap.ref(self.state.<id>)`.

### See Also

- `state-nested-models.md` — state inside state, from the
  nested-`Model` angle.
- `state-actor-decomposition.md` — one `Type` per concern.
- `stdlib-ordered-map.md` — Shape C's API.
- `mcp-app/references/api-state-shapes.md` — the MCP App corollary.
