"""The scenarios that open __APP_NAME__'s web app in a real browser."""

from typing import Iterator

import pytest
from main import SERVICERS, initialize
from reboot.aio.applications import Application
from reboot.aio.auth.oauth import OAuth
from reboot.aio.auth.oauth_providers import (
    Development,
    OAuthProviderByEnvironment,
)
from reboot.bdd import scenarios
from reboot.bdd.frontend import Frontend
from reboot.bdd.vite import vite


@pytest.fixture
def frontend() -> Iterator[Frontend]:
    with vite(directory='frontend') as frontend:
        yield frontend


@pytest.fixture
def application() -> Application:
    development = Development()
    return Application(
        servicers=SERVICERS,
        initialize=initialize,
        # The harness is neither `rbt dev run` nor `rbt serve`, so
        # name the Development picker for both.
        oauth=OAuth(
            provider=OAuthProviderByEnvironment(
                dev=development,
                prod=development,
            ),
            # The web app is served at the backend's own origin, so
            # no other origin may act on its session cookie.
            allowed_origins=[],
        ),
    )


scenarios('__pkg___web.feature')
