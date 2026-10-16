---
title: Define the Application Entry Point
impact: CRITICAL
impactDescription: Application won't start without a correctly-shaped `main`; the skeleton is copied with the project shell
tags: main, application, asyncio, servicers, libraries
---

## Define the Application Entry Point

> **Critical:** pass Servicer **classes** to `Application(servicers=[...])`,
> not instances. `[ChatRoomServicer()]` is wrong; `[ChatRoomServicer]`
> is right. Stdlib types need `libraries=[ordered_map_library(), ...]`
> registered alongside their `servicers()`.

Every Reboot Python application has an `async def main()` that
constructs an `Application` with the list of Servicer classes and any
standard-library components, then awaits `.run()`; the `__main__`
block runs it under `asyncio.run`. The copied `backend/src/main.py`
(`lifecycle-project-setup.md`) is that shape with an empty
`servicers=[]` and an `initialize` hook to fill in: one import per
servicer (`from servicers.<name> import <Name>Servicer`), the classes
in the list, and the demo data in `initialize`
(`lifecycle-seeding.md`). Reboot constructs instances per actor as
needed; a sync `main` or a servicer's own `.serve()` is not how Reboot
starts.

## Multiple Servicers and Stdlib Libraries

Combine Servicer classes from your code with stdlib `servicers()`
factories and `libraries=[...]` for stdlib state types:

```python
import reboot.thirdparty.mailgun
from reboot.aio.applications import Application
from reboot.std.collections.ordered_map.v1.ordered_map import (
    ordered_map_library,
)


async def main():
    await Application(
        servicers=[AccountServicer, BankServicer]
        + reboot.thirdparty.mailgun.servicers(),
        libraries=[ordered_map_library()],
        initialize=initialize,
    ).run()
```

A stdlib state type is registered the way its reference says; the
wiring differs per type. A `<name>_library()` factory in
`libraries=[...]` brings its own servicers along, while a type without
one (or whose library is not used) puts its `servicers()` list into
`servicers=[...]`. Forgetting the registration gives a runtime
"unknown actor type" error:

- `stdlib-ordered-map.md` — `ordered_map_library()` only
- `stdlib-queue.md` — `queue.servicers()` + the stdlib map library
  (`Queue` uses a stdlib sorted-map actor under the hood; the
  reference has the exact import)
- `stdlib-pubsub.md` — `pubsub.servicers()` (transitively pulls
  `queue.servicers()`) + the stdlib map library
- `stdlib-presence.md` — `presence.servicers()` (three Servicers; no
  library factory)

First-run setup that creates singletons or seeds state is
`lifecycle-initialize-hook.md`.
