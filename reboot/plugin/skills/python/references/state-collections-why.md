---
title: Why the Collection Rules Hold
impact: MEDIUM
impactDescription: The reasoning behind `state-collections.md`; a rule applied without it gets bent the first time it is inconvenient
tags: state, collections, OrderedMap, ids, rationale, migration, anti-patterns
---

## Why the Collection Rules Hold

The rules are in [`state-collections.md`](state-collections.md).
This is the reasoning behind them, read when a rule is in doubt.

### Why Decompose Before Choosing a Container

When each item is its own state `Type` referenced by ID, each
container mutation touches only the parent's index, not the full
payload of every item; each item edit touches only that item.

Shape A fits an Order's line items because they have no lifecycle of
their own, are bounded in practice, and are always read alongside
the parent; a Shape A mutation rewrites the parent's list:

```python
async def add_item(
    self, context: WriterContext, request: Order.AddItemRequest,
) -> None:
    self.state.items.append(
        LineItem(sku=request.sku, quantity=request.quantity),
    )
```

In Shape B each member is fully addressable as
`User.ref(user_id)`, and the Org's state grows linearly with member
count, which is fine up to low thousands. Past that, the per-add
write cost of rewriting the full list becomes noticeable — switch to
Shape C.

### Why the Shape Is Chosen Up Front

Shapes B and C agree on the underlying decomposition — items are
their own state `Type` referenced by ID. They differ only in **how
the parent indexes** them. Migrating B → C later is a real piece of
work (every method that touches the index changes shape); choose C
up front if the collection might grow without bound. Migrating A →
B/C is much harder still — every method moves to a different actor.

### Why the Map ID Is Never Synthesized Inline

`OrderedMap.ref(f"{self.ref().state_id}-people")` runs. Even though
this "works", it hides the parent → map relationship from the state
schema: nothing on `UserState` says this user owns a People index,
so [`rbt inspect`](../../inspect/SKILL.md), the `/__/inspect` page,
and the cloud console see only scalar fields and the relationship
lives as a string-formatting convention inside the servicer. It also
repeats the magic string at every callsite — every reader, writer,
and workflow that touches the map — so renaming the suffix, sharding
the index, or migrating to a per-concern owner actor (see
`state-actor-decomposition.md`) means finding and editing every
callsite. And it silently skips the constructor allocation step: no
place in the code marks "this `User` owns a People index", only an
eventual implicit construction on the first `insert`.

### The Persisted-ID Rule, Correct and Wrong

**Correct (the reference lives in the schema):**

```python
class UserState(Model):
    # The reference is a first-class field. Allocated once in `create`;
    # persisted forever; visible to `rbt inspect`, the `/__/inspect`
    # page, and the cloud console.
    profile_id: str = Field(tag=1, default="")
    drafts_index_id: str = Field(tag=2, default="")
    inbox_queue_id: str = Field(tag=3, default="")


class UserServicer(User.Servicer):

    async def create(self, context: TransactionContext) -> None:
        self.state.profile_id = str(uuid4())
        self.state.drafts_index_id = str(uuid4())
        self.state.inbox_queue_id = str(uuid4())

    async def add_draft(
        self, context: TransactionContext, request: User.AddDraftRequest,
    ) -> None:
        await OrderedMap.ref(self.state.drafts_index_id).insert(
            context, key=str(uuid7()), bytes=request.draft_id.encode(),
        )
```

**Wrong (the reference only exists as a string-formatting
convention in the servicer source):**

```python
# Nothing on `UserState` says this user owns a drafts index.
await OrderedMap.ref(
    f"{self.ref().state_id}-drafts",
).insert(context, ...)

# Same anti-pattern inside a workflow.
await OrderedMap.ref(
    f"{context.state_id}-drafts",
).insert(context, ...)
```

Why the persisted-ID rule matters, even though the inline
form runs:

1. **The state schema documents the actor graph.** Reading
   `UserState` should be enough to see which other actors this user
   owns or points at. `rbt inspect`, the `/__/inspect` page, and the
   cloud console show the state, not the servicer source — without a
   persisted ID, the relationship is invisible at runtime.
2. **One place to change, not N.** The persisted ID centralizes
   the parent → child edge in a single field. Renaming, sharding,
   or moving the index to a per-concern owner (see
   `state-actor-decomposition.md`) is one edit. The inline form
   spreads `f"{state_id}-<suffix>"` across every reader, writer,
   and workflow that touches it.
3. **Multiple references scale.** A `User` that owns drafts,
   monitored chats, and a profile actor naturally degrades under
   the inline convention to `"-drafts"`, `"-monitored"`,
   `"-profile"` suffixes pasted at every callsite. With persisted
   IDs they're three first-class fields.
4. **Construction is an event.** Allocating `uuid4()` in the
   constructor marks "this actor now owns that one." The inline
   convention has no such moment; the related actor is
   constructed by whichever method touches it first.

### The Anti-Patterns, at Length

- **`UserState.people: list[Person]`** when `Person` looks like a
  domain entity (has methods, lifecycle, nested events). Flattens
  N actors into one. Promote `Person` to its own `Type` and switch
  to Shape B or C.
- **`Type(state=X)` _and_ `list[X]` (or `dict[str, X]`) somewhere
  as a state field.** The "state inside state" regression —
  `state-nested-models.md` covers the same rule from the nested-
  Models angle.
- **`list[str]` for an unbounded collection** because it is
  simpler at first; the later migration rewrites
  every method that touches the parent. Use Shape C from the start
  if the collection can grow without bound.
- **Inventing a size cap to qualify for Shape A or B.** Adding a
  `MAX_ITEMS` constant to a synced or open-ended collection so it
  "fits" a `list`. The cap truncates the collection; it does not
  make the domain bounded. Model as Shape C and cap the _view_ in
  a reader, never the _state_. An invented cap is a Shape C
  collection in disguise — model it as Shape C and let the product
  decide later whether to display only the first 40.
- **An externally-synced collection held in-state.** A repo's
  issues, an inbox's mail, or a feed's entries as `list[Sub]` on
  one parent actor: every sync rewrites the whole list, editing
  one item rewrites all of them, and the parent actor grows
  toward Reboot's per-actor state-size limit. Promote each synced
  item to its own `Type` and index them with Shape C. Such a
  collection never shows up with the user "add"-ing to it, so the
  verb test in Step 1 does not fire; size it to the **source** (a
  repo has thousands of issues; an inbox has tens of thousands of
  messages), never to the demo you happen to test against.
- **`OrderedMap` for a clearly bounded, sub-dozen collection.** The
  extra hop is wasted; `list[Sub]` (Shape A) or `list[str]`
  (Shape B) is fine.
- **Synthesizing a related actor's ID inline from the parent's
  `state_id`** — `OrderedMap.ref(f"{self.ref().state_id}-drafts")`
  / `OrderedMap.ref(f"{context.state_id}-drafts")`. Hides the
  parent → map edge from the state schema, repeats the magic
  string at every callsite, and skips the constructor allocation
  that marks ownership. Add a `<thing>_index_id` field and
  reference via `OrderedMap.ref(self.state.<id>)`. The same rule
  applies to every cross-`Type` reference, stdlib or user-defined.

### See Also

- `state-actor-decomposition.md` — the orthogonal decomposition:
  splitting **one actor** that has accreted multiple unrelated
  concerns into one `Type` per concern. Same "store the ID, not the
  object" principle, applied to responsibilities rather than
  collection items.
- `mcp-app/references/api-state-shapes.md` (`mcp-app` skill) — the
  MCP-App-specific corollary: `list[Item]` is for sub-records,
  not for application-type instances.
