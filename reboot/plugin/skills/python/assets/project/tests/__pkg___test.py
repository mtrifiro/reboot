"""__APP_NAME__'s tests: the Gherkin scenarios in the `.feature` files
beside this module, run against the real servicers and authorizers."""

import pytest
from main import SERVICERS
from reboot.aio.applications import Application
from reboot.bdd import scenarios


@pytest.fixture
def application() -> Application:
    return Application(servicers=SERVICERS)


scenarios('__things__.feature')
