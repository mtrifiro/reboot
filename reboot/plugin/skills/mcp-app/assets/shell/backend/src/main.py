import asyncio
import logging
from example_prompts import example_prompts
from reboot.aio.applications import Application
from servicers.<name> import (
    CounterServicer,
    UserServicer,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)


async def main() -> None:
    application = Application(
        title="Chat Counter",
        description=(
            "Lets a chat client create, list, increment, and "
            "show counters on your behalf."
        ),
        servicers=[UserServicer, CounterServicer],
        example_prompts=example_prompts,
    )
    await application.run()


if __name__ == "__main__":
    asyncio.run(main())
