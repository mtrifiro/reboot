from typing import Literal, Optional

from reboot.api import (
    API,
    Exclusive,
    Field,
    Methods,
    Model,
    Reader,
    Shared,
    Transaction,
    Type,
    Writer,
)
from reservations.v1.reservations import (
    ReservationStatus,
    InventoryCreateRequest,
    ReservationCreateRequest,
    ReservationView,
    TypeAvailability,
)
from rooms.v1.rooms import (
    RoomStatus,
    RoomCreateRequest,
    RoomView,
)


class HotelState(Model):
    name: str = Field(
        tag=1, default="", description="The hotel's name, shown to staff."
    )
    room_ids: list[str] = Field(
        tag=2,
        default_factory=list,
        description="The state ids (room numbers) of every Room, in floor "
        "and number order. A plain list because the building fixes the "
        "room count.",
    )
    reservations_index_id: str = Field(
        tag=3,
        default="",
        description="The OrderedMap of every Reservation, keyed by "
        "\"<arrival>/<reservation id>\" so the front desk reads them by "
        "date. An OrderedMap because bookings accumulate without bound.",
    )
    inventory_ids: dict[str, str] = Field(
        tag=4,
        default_factory=dict,
        description="The Inventory that counts each room type's booked "
        "nights, by room type.",
    )


class HotelCreateRequest(Model):
    name: str = Field(tag=1, default="", description="The hotel's name.")


class AddFloorRequest(Model):
    rooms: list[RoomCreateRequest] = Field(
        tag=1,
        default_factory=list,
        description="The rooms of one floor, each created as its own "
        "Room. A room that already exists is skipped.",
    )


class FloorPlanResponse(Model):
    hotel_name: str = Field(
        tag=1, default="", description="The hotel's name."
    )
    rooms: list[RoomView] = Field(
        tag=2,
        default_factory=list,
        description="Every room, in floor and number order.",
    )


class SetupFrontDeskRequest(Model):
    inventories: list[InventoryCreateRequest] = Field(
        tag=1,
        default_factory=list,
        description="One per room type, with its room count and any nights "
        "already booked.",
    )


class AddBookingsRequest(Model):
    reservation_ids: list[str] = Field(
        tag=1,
        default_factory=list,
        description="The ids to give the reservations, one per booking.",
    )
    bookings: list[ReservationCreateRequest] = Field(
        tag=2,
        default_factory=list,
        description="Stays already booked when the app is set up, whose "
        "nights the inventories already count.",
    )


class BookRequest(Model):
    guest_name: str = Field(
        tag=1, default="", description="The guest; required."
    )
    room_type: str = Field(
        tag=2, default="", description="The room type to book."
    )
    arrival: str = Field(
        tag=3, default="", description="First night, YYYY-MM-DD."
    )
    departure: str = Field(
        tag=4,
        default="",
        description="Departure morning, YYYY-MM-DD; after the arrival.",
    )


class BookResponse(Model):
    reservation_id: str = Field(
        tag=1,
        default="",
        description="The new reservation's id and confirmation code, "
        "such as \"MV-3F9C2A\".",
    )


class ReservationIdRequest(Model):
    reservation_id: str = Field(
        tag=1, default="", description="The reservation to act on."
    )


class CheckInBookingRequest(Model):
    reservation_id: str = Field(
        tag=1, default="", description="The booked stay arriving."
    )
    room_number: str = Field(
        tag=2,
        default="",
        description="The inspected room of the booked type to give them.",
    )


class RoomNumberRequest(Model):
    room_number: str = Field(
        tag=1, default="", description="The room to act on."
    )


class FrontDeskRequest(Model):
    date: str = Field(
        tag=1,
        default="",
        description="The day the front desk is working, YYYY-MM-DD.",
    )


class FrontDeskResponse(Model):
    arrivals: list[ReservationView] = Field(
        tag=1,
        default_factory=list,
        description="Stays arriving that day, booked or already checked in.",
    )
    departures: list[ReservationView] = Field(
        tag=2,
        default_factory=list,
        description="Guests in house due to leave that day or earlier.",
    )
    upcoming: list[ReservationView] = Field(
        tag=3,
        default_factory=list,
        description="Booked stays arriving in the 14 days after that day.",
    )
    availability: list[TypeAvailability] = Field(
        tag=4,
        default_factory=list,
        description="Rooms left per room type for the 14 nights from that "
        "day, in the hotel's room-type order.",
    )
    ready_rooms: list[RoomView] = Field(
        tag=5,
        default_factory=list,
        description="Inspected rooms a guest can be given now.",
    )
    in_house: int = Field(
        tag=6, default=0, description="Rooms occupied right now."
    )
    time_zone: str = Field(
        tag=7,
        default="",
        description="The hotel's time zone, which check-in time is "
        "measured in.",
    )
    check_in_time: str = Field(
        tag=8,
        default="",
        description="When check-in opens on arrival day, HH:MM hotel time.",
    )


class InvalidDatesError(Model):
    reason: str = Field(
        tag=1, default="", description="What is wrong with the dates."
    )


class WrongRoomTypeError(Model):
    booked: str = Field(
        tag=1, default="", description="The room type the guest booked."
    )
    room_type: str = Field(
        tag=2, default="", description="The type of the room offered."
    )



# Errors the Hotel's methods pass on from the objects they call. Reboot
# 1.6.0 can't declare an error from another API package on a method,
# so the Hotel package keeps its own copy of each, same name and fields.


class BookingStateError(Model):
    status: ReservationStatus = Field(
        tag=1,
        default="booked",
        description="The status the reservation was in, from which the "
        "step is not possible.",
    )


class SoldOutError(Model):
    room_type: str = Field(
        tag=1, default="", description="The room type that is full."
    )
    night: str = Field(
        tag=2,
        default="",
        description="The first night of the stay with no room of that type "
        "left, YYYY-MM-DD.",
    )


class EarlyCheckInError(Model):
    check_in_time: str = Field(
        tag=1,
        default="",
        description="When check-in opens on arrival day, HH:MM hotel time.",
    )
    time_zone: str = Field(
        tag=2,
        default="",
        description="The hotel's time zone, such as America/Chicago.",
    )


class InvalidTransitionError(Model):
    status: RoomStatus = Field(
        tag=1,
        default="vacant_dirty",
        description="The status the room was in, from which the "
        "requested step is not possible.",
    )
    action: str = Field(
        tag=2,
        default="",
        description="The step that was refused, such as \"mark_clean\".",
    )


class MissingDetailError(Model):
    detail: str = Field(
        tag=1,
        default="",
        description="The name of the request property that was left "
        "empty.",
    )


class RoomNotReadyError(Model):
    status: RoomStatus = Field(
        tag=1,
        default="vacant_dirty",
        description="The status the room was in, which is not inspected.",
    )


HotelMethods = Methods(
    create=Writer(
        request=HotelCreateRequest,
        response=None,
        factory=True,
        description="Bring the hotel into existence with its name and no "
        "rooms yet. Called once by the app at first start.",
        mcp=None,
    ),
    add_floor=Transaction(
        mode=Exclusive(),
        request=AddFloorRequest,
        response=None,
        description="Create one floor's rooms and add them to the hotel, "
        "all together or none. Called only by the app when it lays out "
        "the building.",
        mcp=None,
    ),
    floor_plan=Reader(
        request=None,
        response=FloorPlanResponse,
        description="Every room in the hotel with its live status, guest "
        "and who last touched it: the answer to which rooms can be sold "
        "or checked into now. Any member of staff may read it.",
        mcp=None,
    ),
    setup_front_desk=Transaction(
        mode=Exclusive(),
        request=SetupFrontDeskRequest,
        response=None,
        description="Create the reservations index and one Inventory per "
        "room type, once. Called only by the app at start.",
        mcp=None,
    ),
    add_bookings=Transaction(
        mode=Shared(),
        request=AddBookingsRequest,
        response=None,
        description="Record stays already booked when the app is set up. "
        "Called only by the app.",
        mcp=None,
    ),
    book=Transaction(
        mode=Shared(),
        request=BookRequest,
        response=BookResponse,
        errors=[SoldOutError, InvalidDatesError, MissingDetailError],
        description="Book a guest into a room type for a run of nights. "
        "Raises `SoldOutError` if any night has no room of that type left, "
        "`InvalidDatesError` unless departure is after arrival (at most 60 "
        "nights), `MissingDetailError` without a guest. Front desk or "
        "managers only.",
        mcp=None,
    ),
    cancel_booking=Transaction(
        mode=Shared(),
        request=ReservationIdRequest,
        response=None,
        errors=[BookingStateError],
        description="Cancel a booked stay and free its nights. Raises "
        "`BookingStateError` once the guest has checked in. Front desk or "
        "managers only.",
        mcp=None,
    ),
    check_in_booking=Transaction(
        mode=Shared(),
        request=CheckInBookingRequest,
        response=None,
        errors=[
            RoomNotReadyError,
            WrongRoomTypeError,
            BookingStateError,
            EarlyCheckInError,
        ],
        description="Give an arriving guest a room and check them in. "
        "Raises `RoomNotReadyError` unless the room is inspected, "
        "`WrongRoomTypeError` unless it is the type they booked, "
        "`BookingStateError` unless the stay is booked, and "
        "`EarlyCheckInError` before 3 pm hotel time on arrival day unless "
        "a manager approved it or is the one checking in (which records "
        "their approval). Front desk or managers only.",
        mcp=None,
    ),
    check_out_room=Transaction(
        mode=Shared(),
        request=RoomNumberRequest,
        response=None,
        errors=[InvalidTransitionError],
        description="Check out whoever is in a room: the room goes to "
        "housekeeping as dirty and the guest's stay is closed. Raises "
        "`InvalidTransitionError` unless the room is occupied. Front desk "
        "or managers only.",
        mcp=None,
    ),
    front_desk=Reader(
        request=FrontDeskRequest,
        response=FrontDeskResponse,
        description="A day at the front desk: arrivals, departures, the "
        "next two weeks of bookings, rooms left per type, and the "
        "inspected rooms ready to give out. Any member of staff may read "
        "it.",
        mcp=None,
    ),
)


api = API(
    Hotel=Type(
        state=HotelState,
        methods=HotelMethods,
        description="The property: one per hotel (id \"hotel\"), owning "
        "the list of its rooms and serving the floor plan.",
    ),
)
