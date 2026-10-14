"""The hotel's scenarios: every `.feature` file beside this module, run
against the application with its real authorizers."""

import pytest
from main import SERVICERS
from reboot.aio.applications import Application
from reboot.aio.external import InitializeContext
from reboot.bdd import scenarios
from seed import seed_hotel


async def initialize(context: InitializeContext) -> None:
    # The real building, without the busy afternoon.
    await seed_hotel(context, demo=False)


@pytest.fixture
def application() -> Application:
    return Application(servicers=SERVICERS, initialize=initialize)


scenarios("rooms.feature")
