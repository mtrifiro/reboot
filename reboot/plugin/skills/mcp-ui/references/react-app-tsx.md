---
title: React App.tsx — Generated Hooks and Component Patterns
impact: HIGH
impactDescription: The generated `use<Type>()` hook returns reader subscriptions and mutation functions; both go directly to the Reboot backend. Reboot snake_case Python field names become camelCase in TypeScript. Each `App.tsx` lives next to a CSS module and consumes the per-UI props passed via `UI(request=...)`.
tags: react, app-tsx, hooks, useType, css-module, snake-camel, app-tsx-example, composing-reader, pagination, ordered-map, multi-actor
---

## React App.tsx — Generated Hooks and Component Patterns

`frontend/mcp/<ui-name>/App.tsx` is the React component for one UI.

> **The generated client contract is shared with web apps** — the
> `use<Type>()` overloads, the `Use<Type>Api` surface, the three
> fields a reader returns, why mutations resolve to
> `{ response, aborted }` instead of throwing, and the typed error
> classes are all in
> [`python/references/react-generated-client.md`](../../python/references/react-generated-client.md).
> Read that for the shapes; this file covers what is specific to a
> UI rendered inside an MCP host.

```tsx
import { useCounter } from "@api/<pkg>/v1/<name>_rbt_react";

// useCounter() connects to the Counter state instance.
const counter = useCounter();

// Reader (a live subscription — pushed on every change):
const { response } = counter.useGet();
const value = response?.value ?? 0;

// Mutation (resolves to `{ response, aborted }` — it never throws):
const { aborted } = await counter.increment({ amount: 1 });

// Python from_index -> TypeScript fromIndex (camelCase).
await myType.reorderItem({ fromIndex: 0, toIndex: 1 });
```

The copied `mcp/<ui-name>/App.tsx` and `App.module.css` (from
[`react-scaffolding.md`](react-scaffolding.md)'s copy) are a complete
counter UI in this shape: the hook, a reader with `isLoading`, two
mutations behind a pending state, and a CSS module on `index.css`'s
tokens. Rewrite `App.tsx` for the app's first UI keeping that shape,
and adapt the module; the component's export name is what `main.tsx`
imports.

## Actor ID Resolution: Zero-Arg `use<Type>()` for UIs on the Type

For a `UI()` declared on an application `Type` (e.g.
`Person.show=UI(...)`, `Counter.show_clicker=UI(...)`), call the
generated `use<Type>()` hook with **no arguments**:

```tsx
// Counter.show_clicker=UI(...) → `useCounter()` auto-resolves.
const counter = useCounter();
```

The hook reads the actor ID from `toolData.ids["<pkg>.<Type>"]`,
which the framework populates from the MCP tool call's target: the
state ID the AI passes when invoking the generated `<type>_<method>`
tool. So the React UI always materializes for exactly the entity the
AI asked about, with no props plumbing and no cross-wired IDs.

For UIs declared on `User`, or any component that needs a different
entity than the tool-call target, pass an explicit `{id: ...}`:

```tsx
const relatedPerson = usePerson({ id: relationship.otherPersonId });
```

For the raw tool-call inputs (a follow-up read, a navigation chain to
another entity of the same Type), `useMcpToolData()` from
`@reboot-dev/reboot-react` returns the `{ids, ...}` object the
framework received.

## Generated React Imports

```tsx
import { type DashboardConfig, useCounter } from "@api/<pkg>/v1/<name>_rbt_react";
```

- The hook is `use<TypeName>()`: `useCounter()`, `useInventory()`.
- The import path is `@api/<pkg>/v1/<name>_rbt_react` (the `@api/*`
  alias is set up by `vite.config.ts`).
- Frontend Request/Response types are Zod-validated; the same
  `<MethodPascalCase>Request`/`<MethodPascalCase>Response` rule
  applies on the TypeScript side.

## Reading Across Many Actors — the Composing Reader

The counter is the single-actor case: one `use<Type>()` hook, one
actor, one live feed. It does **not** generalize to a collection that
has been correctly decomposed, each item its own state `Type`, indexed
by an `OrderedMap` on the parent (Shape C in
`python/references/state-collections.md`). There each item is a
separate actor, and there is no `use<Item>()` call that renders the
whole list at once.

The wrong fix is to flatten the model back into `list[Item]` on one
actor so the dashboard regains a single subscription; see "When
Correct Decomposition Fights the UI" in [`SKILL.md`](../SKILL.md). The
right fix keeps the decomposition and gives the front-door type a
**composing reader**: the UI still has exactly one subscription, and
the fan-out across item actors happens server-side.

### Backend: a composing `Reader` on the front-door type

The reader ranges the parent's `OrderedMap` for one page of IDs, reads
each item actor, and returns a page of hydrated objects plus a cursor
for the next page:

```python
# `Item` is the per-item state `Type`. `items_index_id` is the
# `OrderedMap` ID — a field on the parent's state, allocated once in
# the parent's constructor. Never synthesize the map ID inline from
# `self.ref().state_id` or `context.state_id` — see "Relationships
# Between State Types" in `python/references/state-collections.md`.
async def dashboard(
    self,
    context: ReaderContext,
    request: User.DashboardRequest,
) -> User.DashboardResponse:
    page = await OrderedMap.ref(self.state.items_index_id).range(
        context, start_key=request.cursor, limit=32,
    )
    items = []
    for entry in page.entries:
        item_id = entry.bytes.decode()
        # A Reader may call other Readers — the fan-out is
        # server-side. See `python/references/servicer-reader.md`.
        view = await Item.ref(item_id).get(context)
        items.append(
            User.DashboardItem(
                item_id=item_id,
                title=view.title,
                status=view.status,
            )
        )
    return User.DashboardResponse(
        items=items,
        next_cursor=(page.entries[-1].key if page.entries else ""),
    )
```

Declare it `mcp=None` — it feeds the UI, not the AI. The `OrderedMap`
`range` / cursor mechanics (including the inclusive `start_key`
caveat) are in `python/references/stdlib-ordered-map.md`, and the
Shape C example in `python/references/state-collections.md` shows the
parent allocating and writing the index.

### Frontend: one subscription, cursor pagination

The UI keeps a single `use<FrontDoorType>()` subscription, the same
shape as the counter, and pages by cursor:

```tsx
import { useState, type FC } from "react";
import { useUser } from "@api/<pkg>/v1/<name>_rbt_react";

export const Dashboard: FC = () => {
  const user = useUser();
  const [cursor, setCursor] = useState("");

  // One reader subscription. The composing reader fans out across
  // the item actors server-side, so the UI still sees one live
  // feed — no per-item hooks.
  const { response, isLoading } = user.useDashboard({ cursor });

  const items = response?.items ?? [];
  const nextCursor = response?.nextCursor ?? "";

  if (isLoading && response === undefined) {
    return <div>loading...</div>;
  }

  return (
    <div>
      {items.map((item) => (
        <div key={item.itemId}>
          {item.title} — {item.status}
        </div>
      ))}
      {nextCursor && (
        <button onClick={() => setCursor(nextCursor)}>Load more</button>
      )}
    </div>
  );
};
```

`setCursor(nextCursor)` advances the subscription to the next page. To
render an ever-growing list rather than one page at a time, accumulate
`response.items` into component state on each change instead of
rendering `response.items` directly.
