# The last run's results, in tests/.last-run.json (tests/last_run.py).
from last_run import (  # noqa: F401
    pytest_sessionstart,
    pytest_terminal_summary,
    pytest_unconfigure,
)

from reboot.bdd import given, parsers, when
from reboot.bdd.fixtures import World


@when(parsers.parse('"{user}" signs in as "{email}", verified {verified}'))
@given(parsers.parse('"{user}" signs in as "{email}", verified {verified}'))
async def _signs_in(world: World, user: str, email: str, verified: str) -> None:
    """A sign-in that delivers claims, as a real provider does, so the
    app's own `set_claims` and the roster's `register` run."""
    assert world.rbt is not None
    world.declare_user(
        user,
        await world.rbt.make_valid_oauth_access_token(
            user_id=user,
            claims={
                "email": email,
                "email_verified": verified == "yes",
                "name": user.capitalize(),
            },
        ),
    )


from datetime import datetime
from typing import Iterator
from unittest import mock
from zoneinfo import ZoneInfo

import clock
import pytest


class HotelClock:
    """The time at the hotel during a scenario: 4 pm on 1 March 2027
    unless a step sets it, so no scenario depends on the real time."""

    def __init__(self) -> None:
        self.now = datetime(
            2027, 3, 1, 16, 0, tzinfo=ZoneInfo(clock.HOTEL_TIME_ZONE)
        )

    def __call__(self) -> datetime:
        return self.now


@pytest.fixture(autouse=True)
def hotel_clock() -> Iterator[HotelClock]:
    fake = HotelClock()
    with mock.patch("clock.hotel_now", new=fake):
        yield fake


@given(parsers.parse('it is "{moment}" at the hotel'))
def _it_is(hotel_clock: HotelClock, moment: str) -> None:
    hotel_clock.now = datetime.fromisoformat(moment).replace(
        tzinfo=ZoneInfo(clock.HOTEL_TIME_ZONE)
    )
