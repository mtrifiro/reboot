"""The building: 56 rooms on floors 2 to 8, eight to a floor.

Floors 2-5 are Deluxe King and Deluxe Twin rooms with a Junior Suite at
the end of each corridor; floors 6-7 are Junior Suites and Suites; the
eighth floor holds the top suites and the Penthouse, 808.
"""

from hotel.v1.hotel import RoomCreateRequest

HOTEL_NAME = "Halcyon House"
HOTEL_ID = "hotel"
FLOORS = range(2, 9)


def _room_type(floor: int, n: int) -> str:
    if floor <= 5:
        if n <= 5:
            return "Deluxe King"
        if n <= 7:
            return "Deluxe Twin"
        return "Junior Suite"
    if floor == 6:
        return "Junior Suite" if n <= 6 else "Suite"
    if floor == 7:
        return "Junior Suite" if n <= 4 else "Suite"
    if n == 8:
        return "Penthouse"
    return "Junior Suite" if n <= 4 else "Suite"


def floor_rooms(floor: int) -> list[RoomCreateRequest]:
    return [
        RoomCreateRequest(
            number=f"{floor}{n:02d}",
            floor=floor,
            room_type=_room_type(floor, n),
        )
        for n in range(1, 9)
    ]
