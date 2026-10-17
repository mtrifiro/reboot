import asyncio
import logging

from __pkg__.v1.__pkg___rbt import __Hub__
from reboot.aio.applications import Application
from reboot.aio.auth.oauth import OAuth
from reboot.aio.auth.oauth_providers import (
    Development,
    OAuthProviderByEnvironment,
)
from reboot.aio.external import InitializeContext
from servicers.__hub__ import HUB_ID, __Hub__Servicer
from servicers.__thing__ import __Thing__Servicer
from servicers.user import UserServicer

logging.basicConfig(level=logging.INFO)

# The servicer classes, never instances; the tests import this list.
SERVICERS = [UserServicer, __Hub__Servicer, __Thing__Servicer]


async def initialize(context: InitializeContext):
    # Runs on every start, so everything here is safe to run twice.
    # The one __hub text__, so its list reads empty, not missing.
    await __Hub__.ref(HUB_ID).open(context)
    # Demo data, under `rbt dev run` only and in batches:
    # `lifecycle-seeding.md`.


async def main():
    await Application(
        servicers=SERVICERS,
        initialize=initialize,
        oauth=OAuth(
            provider=OAuthProviderByEnvironment(
                # The development picker: Alice, Ben, Carlos, Dani, Esi.
                dev=Development(),
                # A real provider is chosen at deploy.
                prod=None,
            ),
        ),
    ).run()


if __name__ == '__main__':
    asyncio.run(main())
