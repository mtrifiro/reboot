"""The hotel's clock: the time at the hotel, and when check-in opens.

Servicers call `clock.hotel_now()` through the module, so tests can set
the hotel's time by patching it.
"""

import os
from datetime import datetime, time
from zoneinfo import ZoneInfo

def _local_time_zone() -> str:
    """The computer's own IANA time zone, such as "America/Chicago": the
    hotel keeps the user's time unless told otherwise."""
    target = os.path.realpath("/etc/localtime")
    return target.split("zoneinfo/", 1)[1] if "zoneinfo/" in target else "UTC"


HOTEL_TIME_ZONE = os.environ.get("HOTEL_TIME_ZONE") or _local_time_zone()
CHECK_IN_TIME = time(15, 0)


def hotel_now() -> datetime:
    return datetime.now(ZoneInfo(HOTEL_TIME_ZONE))


def check_in_open(arrival: str) -> bool:
    """Whether check-in has opened for a stay arriving on `arrival`
    (YYYY-MM-DD): from 3 pm, hotel time, that day."""
    opens = datetime.combine(
        datetime.fromisoformat(arrival).date(),
        CHECK_IN_TIME,
        tzinfo=ZoneInfo(HOTEL_TIME_ZONE),
    )
    return hotel_now() >= opens


def today() -> str:
    return hotel_now().date().isoformat()
