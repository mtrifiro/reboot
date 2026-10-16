import asyncio
import logging
from reboot.aio.applications import Application
from reboot.aio.external import InitializeContext
# One import per servicer: `from servicers.<name> import <Name>Servicer`.

logging.basicConfig(level=logging.INFO)


async def initialize(context: InitializeContext):
    # Demo data, under `rbt dev run` only and idempotent on restart:
    # `lifecycle-seeding.md`.
    pass


async def main():
    await Application(
        servicers=[],  # The servicer classes, never instances.
        initialize=initialize,
    ).run()


if __name__ == '__main__':
    asyncio.run(main())
