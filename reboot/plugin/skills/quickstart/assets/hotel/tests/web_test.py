"""The hotel's scenarios: every `.feature` file beside this module, run
against the application with its real authorizers and with the web app
served, so a scenario can act in the browser as well as through the API."""

from typing import Iterator

import pytest
from main import CLAIMS, LIBRARIES, SERVICERS
from reboot.aio.applications import Application
from reboot.aio.auth.oauth import OAuth
from reboot.aio.auth.oauth_providers import (
    Development,
    OAuthProviderByEnvironment,
)
from reboot.aio.external import InitializeContext
from reboot.bdd import scenarios
from reboot.bdd.frontend import Frontend
from reboot.bdd.vite import vite
from seed import seed_hotel


async def initialize(context: InitializeContext) -> None:
    # The real building, without the demo afternoon.
    await seed_hotel(context, demo=False)


@pytest.fixture
def frontend() -> Iterator[Frontend]:
    with vite(directory="frontend") as frontend:
        yield frontend


@pytest.fixture
def application(frontend: Frontend) -> Application:
    assert frontend.origin is not None
    # The harness is neither `rbt dev run` nor `rbt serve`, so the
    # Development picker serves both arms.
    development = Development(claims=CLAIMS)
    return Application(
        servicers=SERVICERS,
        libraries=LIBRARIES,
        initialize=initialize,
        oauth=OAuth(
            provider=OAuthProviderByEnvironment(
                dev=development, prod=development
            ),
            allowed_origins=[frontend.origin],
        ),
    )


scenarios(
    "room_status.feature", "staff_roles.feature", "reservations.feature"
)
