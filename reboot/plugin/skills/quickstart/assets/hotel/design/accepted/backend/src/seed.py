"""Laying out the hotel, and the busy afternoon shown under `rbt dev run`."""

from hotel.v1.hotel import RoomCreateRequest
from hotel.v1.hotel_rbt import Hotel
from layout import FLOORS, HOTEL_ID, HOTEL_NAME, floor_rooms
from reboot.aio.external import ExternalContext

GUESTS = [
    "Mme. Laurent", "Mr. Okafor", "Ms. Varga", "Mr. & Mrs. Sato",
    "Dr. Haddad", "Ms. Lindqvist", "Mr. Moreau", "The Alvarez family",
    "Ms. Chen", "Mr. Abernathy", "Sra. Ortega", "Mr. Kowalski",
    "Ms. Ferreira", "Mr. Nakamura", "Mme. Dubois", "Mr. Petrov",
    "Ms. O'Connell", "Mr. Rossi", "Dr. Mbeki", "Ms. Andersen",
    "Mr. Castellano", "Ms. Iyer", "Mr. Whitfield", "Mme. Girard",
    "Mr. Takahashi", "Ms. Novak", "Mr. Dumont", "Ms. Reyes",
    "Mr. Lambert", "Ms. Kaur", "Mr. Brennan", "Ms. Johansson",
    "Mr. Farouk", "Ms. Bianchi",
]

# Status for each room by its position in the building: a believable
# early afternoon, most rooms occupied and housekeeping halfway through
# the departures.
PATTERN = ["occupied"] * 34 + ["dirty"] * 12 + ["clean"] * 10


def _demo(room: RoomCreateRequest, i: int, guests: list[str]) -> None:
    # A spread that doesn't cluster: walk the pattern with a stride
    # coprime to its length.
    status = PATTERN[(i * 23) % len(PATTERN)]
    room.status = status  # type: ignore[assignment]
    if status == "occupied":
        room.guest_name = guests.pop(0)


async def seed_hotel(context: ExternalContext, *, demo: bool) -> None:
    await Hotel.create(context, HOTEL_ID, name=HOTEL_NAME)
    hotel = Hotel.ref(HOTEL_ID)
    guests = list(GUESTS)
    i = 0
    for floor in FLOORS:
        rooms = floor_rooms(floor)
        if demo:
            for room in rooms:
                _demo(room, i, guests)
                i += 1
        # One floor per transaction, each with its own alias, so a
        # restart skips the floors already laid out.
        await hotel.idempotently(f"floor-{floor}").add_floor(
            context, rooms=rooms
        )
