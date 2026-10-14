"""The building: 56 rooms on floors 2 to 8, eight to a floor.

Floors 2-5 are Deluxe King and Deluxe Twin rooms with a Junior Suite at
the end of each corridor; floors 6-7 are Junior Suites and Suites; the
eighth floor holds the top suites and the Penthouse, 808.
"""

from rooms.v1.rooms import RoomCreateRequest

HOTEL_NAME = "Maison Vingt-Trois"
FLOORS = range(2, 9)

FEATURES: dict[str, list[str]] = {
    "Deluxe King": ["King bed", "Rain shower", "Frette linens"],
    "Deluxe Twin": ["Two queen beds", "Rain shower", "Frette linens"],
    "Junior Suite": ["Soaking tub", "Separate lounge", "Espresso bar"],
    "Suite": ["Soaking tub", "Terrace", "Butler pantry", "Dining for six"],
    "Penthouse": [
        "Private terrace with plunge pool",
        "Fireplace",
        "Steinway grand",
        "Dedicated butler",
    ],
}

# The order the front desk lists room types in.
ROOM_TYPES = list(FEATURES)


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
    rooms = []
    for n in range(1, 9):
        room_type = _room_type(floor, n)
        features = list(FEATURES[room_type])
        if n in (1, 8) and room_type != "Penthouse":
            features.append("Corner, two exposures")
        rooms.append(
            RoomCreateRequest(
                number=f"{floor}{n:02d}",
                floor=floor,
                room_type=room_type,
                features=features,
            )
        )
    return rooms


def room_counts() -> dict[str, int]:
    counts = {room_type: 0 for room_type in ROOM_TYPES}
    for floor in FLOORS:
        for room in floor_rooms(floor):
            counts[room.room_type] += 1
    return counts
