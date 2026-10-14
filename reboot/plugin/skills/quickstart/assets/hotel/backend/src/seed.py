"""Laying out the hotel, and the demo day shown under `rbt dev run`."""

from datetime import date, timedelta

from reservations.v1.reservations import InventoryCreateRequest, ReservationCreateRequest
from rooms.v1.rooms import RoomCreateRequest
from staff.v1.staff import StaffRole
from hotel.v1.hotel_rbt import Hotel
from staff.v1.staff_rbt import Team
from layout import FLOORS, HOTEL_NAME, ROOM_TYPES, floor_rooms, room_counts
from reboot.aio.external import ExternalContext
from servicers.auth import HOTEL_ID, TEAM_ID
from servicers.inventory import nights

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
ARRIVING = [
    "Mr. & Mrs. Hartley", "Ms. Okonkwo", "Herr Brandt", "Ms. Delacroix",
    "Mr. Villanueva", "Dr. Aoki", "The Whitmore party",
]
LATER = [
    "Mr. Quint", "Ms. Halvorsen", "Mr. Esposito", "Ms. Park", "Dr. Ruiz",
    "Mr. Lindgren", "Ms. Abara", "Mr. Collier", "Mme. Fontaine",
    "Mr. Grady", "Ms. Tanaka", "Mr. Oyelaran", "Ms. Silva", "Mr. Beaumont",
    "Ms. Rahman", "Mr. Kessler", "Ms. Moretti", "Mr. Achebe",
    "Ms. Lund", "Mr. Navarro", "Ms. Whitaker", "Mr. Ivanov",
]

# Status for each room by its position in the building, a believable
# early afternoon: most rooms occupied, housekeeping halfway through the
# departures, two rooms down for repairs.
PATTERN = (
    ["occupied"] * 34
    + ["vacant_dirty"] * 8
    + ["cleaning"] * 3
    + ["vacant_clean"] * 4
    + ["inspected"] * 5
    + ["out_of_order"] * 2
)
REPAIRS = ["Shower valve replacement", "Repainting after a leak"]
CLEANERS = ["Carlos", "Dani"]
BATCH = 10


class DemoDay:
    """The demo afternoon, worked out in full before anything is written,
    so every occupied room has a stay behind it and every inventory
    already counts the nights its stays take."""

    def __init__(self, today: date) -> None:
        self.today = today
        self.ids: list[str] = []
        self.bookings: list[ReservationCreateRequest] = []
        self.totals = room_counts()
        self.booked: dict[str, dict[str, int]] = {t: {} for t in ROOM_TYPES}
        self.counters: dict[str, int] = {}

    def _day(self, offset: int) -> str:
        return (self.today + timedelta(days=offset)).isoformat()

    def _take(
        self, booking: ReservationCreateRequest, *, force: bool = False
    ) -> bool:
        counts = self.booked[booking.room_type]
        stay = nights(booking.arrival, booking.departure)
        if not force and any(
            counts.get(n, 0) >= self.totals[booking.room_type] for n in stay
        ):
            return False
        for n in stay:
            counts[n] = counts.get(n, 0) + 1
        self.ids.append(f"MV-D{len(self.ids) + 1:04d}")
        self.bookings.append(booking)
        return True

    def room(self, room: RoomCreateRequest, i: int) -> None:
        # A spread that doesn't cluster: walk the pattern with a stride
        # coprime to its length.
        status = PATTERN[(i * 23) % len(PATTERN)]
        n = self.counters.get(status, 0)
        self.counters[status] = n + 1
        room.status = status  # type: ignore[assignment]
        if status == "occupied":
            room.guest_name = GUESTS[n % len(GUESTS)]
            # Arrived one to three nights ago; about one in six leaves
            # today, the rest over the next four days.
            arrived = -(1 + n % 3)
            leaves = 0 if n % 6 == 0 else 1 + n % 4
            self._take(
                ReservationCreateRequest(
                    guest_name=room.guest_name,
                    room_type=room.room_type,
                    arrival=self._day(arrived),
                    departure=self._day(leaves),
                    status="checked_in",
                    room_number=room.number,
                    booked_by_name="Esi",
                ),
                force=True,
            )
            room.reservation_id = self.ids[-1]
        if status in ("vacant_clean", "inspected"):
            room.cleaned_by_name = CLEANERS[n % len(CLEANERS)]
        if status == "out_of_order":
            room.out_of_order_reason = REPAIRS[n % len(REPAIRS)]

    def future(self) -> None:
        for n, guest in enumerate(ARRIVING):
            self._take(
                ReservationCreateRequest(
                    guest_name=guest,
                    room_type=ROOM_TYPES[n % len(ROOM_TYPES)],
                    arrival=self._day(0),
                    departure=self._day(2 + n % 3),
                    booked_by_name="Esi",
                )
            )
        for n, guest in enumerate(LATER):
            start = 1 + (n * 5) % 13
            self._take(
                ReservationCreateRequest(
                    guest_name=guest,
                    room_type=ROOM_TYPES[(n * 3) % len(ROOM_TYPES)],
                    arrival=self._day(start),
                    departure=self._day(start + 1 + n % 4),
                    booked_by_name="Alice" if n % 3 == 0 else "Esi",
                )
            )


async def seed_hotel(
    context: ExternalContext, *, demo: bool, today: date | None = None
) -> None:
    await Team.create(context, TEAM_ID)
    await Hotel.create(context, HOTEL_ID, name=HOTEL_NAME)
    hotel = Hotel.ref(HOTEL_ID)
    day = DemoDay(today or date.today())
    i = 0
    for floor in FLOORS:
        rooms = floor_rooms(floor)
        if demo:
            for room in rooms:
                day.room(room, i)
                i += 1
        # One floor per transaction, one at a time, each with its own
        # alias so a restart skips the floors already laid out.
        await hotel.idempotently(f"floor-{floor}").add_floor(
            context, rooms=rooms
        )
    if demo:
        day.future()

    await hotel.setup_front_desk(
        context,
        inventories=[
            InventoryCreateRequest(
                room_type=room_type,
                total_rooms=total,
                booked=day.booked[room_type],
            )
            for room_type, total in day.totals.items()
        ],
    )
    for start in range(0, len(day.bookings), BATCH):
        await hotel.idempotently(f"bookings-{start}").add_bookings(
            context,
            reservation_ids=day.ids[start:start + BATCH],
            bookings=day.bookings[start:start + BATCH],
        )


# The Development sign-in's five people, invited so each arrives with a
# role to try: Alice manages, Esi is on the front desk, Carlos and Dani
# are housekeeping, and Ben arrives with no role yet.
DEMO_STAFF: list[tuple[str, StaffRole]] = [
    ("alice@example.com", "manager"),
    ("esi@example.com", "front_desk"),
    ("carlos@example.com", "housekeeping"),
    ("dani@example.com", "housekeeping"),
]


async def seed_demo_staff(context: ExternalContext) -> None:
    team = Team.ref(TEAM_ID)
    for email, role in DEMO_STAFF:
        await team.idempotently(f"invite-{email}").invite(
            context, email=email, role=role
        )
