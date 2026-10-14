import asyncio
import logging

from reboot.aio.applications import Application
from reboot.aio.external import InitializeContext
from reboot.run_environments import running_rbt_dev
from seed import seed_hotel
from servicers.hotel import HotelServicer
from servicers.room import RoomServicer

logging.basicConfig(level=logging.INFO)

SERVICERS = [HotelServicer, RoomServicer]


async def initialize(context: InitializeContext) -> None:
    # The building exists in every environment; the busy afternoon only
    # under `rbt dev run`.
    await seed_hotel(context, demo=running_rbt_dev())


async def main() -> None:
    await Application(servicers=SERVICERS, initialize=initialize).run()


if __name__ == "__main__":
    asyncio.run(main())
