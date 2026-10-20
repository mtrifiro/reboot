import asyncio
import logging
import os

from reboot.aio.applications import Application
from reboot.aio.auth.oauth import OAuth
from reboot.aio.auth.oauth_providers import (
    Development,
    OAuthProviderByEnvironment,
)
from reboot.aio.external import InitializeContext
from reboot.run_environments import running_rbt_dev
from reboot.std.collections.ordered_map.v1.ordered_map import (
    ordered_map_library,
)
from seed import seed_demo_staff, seed_hotel
from servicers.hotel import HotelServicer
from servicers.inventory import InventoryServicer
from servicers.reservation import ReservationServicer
from servicers.room import RoomServicer
from servicers.team import TeamServicer, allowlist_configured
from servicers.user import UserServicer

logging.basicConfig(level=logging.INFO)

SERVICERS = [
    HotelServicer,
    InventoryServicer,
    ReservationServicer,
    RoomServicer,
    TeamServicer,
    UserServicer,
]
LIBRARIES = [ordered_map_library()]
CLAIMS = ["email", "email_verified", "name"]


async def initialize(context: InitializeContext) -> None:
    # The building exists in every environment; the busy afternoon and
    # the invited demo staff only under `rbt dev run`.
    await seed_hotel(context, demo=running_rbt_dev())
    if running_rbt_dev():
        await seed_demo_staff(context)


async def main() -> None:
    if os.environ.get("GOOGLE_OAUTH_CLIENT_ID") and not allowlist_configured():
        raise SystemExit(
            "GOOGLE_OAUTH_CLIENT_ID is set but no ADMIN_EMAILS / "
            "ALLOWED_EMAILS / ALLOWED_EMAIL_DOMAINS; set one so sign-in "
            "is limited to the hotel's staff."
        )
    await Application(
        servicers=SERVICERS,
        libraries=LIBRARIES,
        oauth=OAuth(
            provider=OAuthProviderByEnvironment(
                dev=Development(claims=CLAIMS),
                prod=None,  # Chosen at deploy.
            ),
        ),
        initialize=initialize,
    ).run()


if __name__ == "__main__":
    asyncio.run(main())
