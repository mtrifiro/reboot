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


ReservationStatus = Literal["booked", "checked_in", "checked_out", "cancelled"]


class BookingStateError(Model):
    status: ReservationStatus = Field(
        tag=1,
        default="booked",
        description="The status the reservation was in, from which the "
        "step is not possible.",
    )


class ReservationState(Model):
    guest_name: str = Field(
        tag=1, default="", description="The guest the stay is booked for."
    )
    room_type: str = Field(
        tag=2,
        default="",
        description="The room type booked; the room itself is chosen at "
        "check-in.",
    )
    arrival: str = Field(
        tag=3,
        default="",
        description="The first night of the stay, as YYYY-MM-DD.",
    )
    departure: str = Field(
        tag=4,
        default="",
        description="The morning the guest leaves, as YYYY-MM-DD; that "
        "night is not part of the stay.",
    )
    status: ReservationStatus = Field(
        tag=5,
        default="booked",
        description="booked until the guest arrives, checked_in while they "
        "stay, checked_out after, or cancelled.",
    )
    room_number: str = Field(
        tag=6,
        default="",
        description="The room the guest was given at check-in; empty "
        "before.",
    )
    booked_by_name: str = Field(
        tag=7, default="", description="Who took the booking."
    )
    booked_at: str = Field(
        tag=8,
        default="",
        description="When the booking was taken, ISO 8601 UTC.",
    )
    early_check_in_approved_by_name: str = Field(
        tag=9,
        default="",
        description="The manager who let the guest check in before 3 pm; "
        "empty unless one did.",
    )
    early_check_in_approved_at: str = Field(
        tag=10,
        default="",
        description="When the early check-in was approved, ISO 8601 UTC.",
    )


class ReservationView(Model):
    reservation_id: str = Field(
        tag=1,
        default="",
        description="The reservation's id, also its confirmation code.",
    )
    guest_name: str = Field(tag=2, default="", description="The guest.")
    room_type: str = Field(
        tag=3, default="", description="The room type booked."
    )
    arrival: str = Field(
        tag=4, default="", description="First night, YYYY-MM-DD."
    )
    departure: str = Field(
        tag=5, default="", description="Departure morning, YYYY-MM-DD."
    )
    status: ReservationStatus = Field(
        tag=6, default="booked", description="Where the stay is."
    )
    room_number: str = Field(
        tag=7, default="", description="The room given at check-in."
    )
    booked_by_name: str = Field(
        tag=8, default="", description="Who took the booking."
    )
    early_check_in_approved_by_name: str = Field(
        tag=9,
        default="",
        description="The manager who approved an early check-in, if any.",
    )


class ReservationCreateRequest(Model):
    guest_name: str = Field(tag=1, default="", description="The guest.")
    room_type: str = Field(
        tag=2, default="", description="The room type booked."
    )
    arrival: str = Field(
        tag=3, default="", description="First night, YYYY-MM-DD."
    )
    departure: str = Field(
        tag=4, default="", description="Departure morning, YYYY-MM-DD."
    )
    status: ReservationStatus = Field(
        tag=5,
        default="booked",
        description="The status it starts in; checked_in only for stays "
        "already in house when the app is set up.",
    )
    room_number: str = Field(
        tag=6,
        default="",
        description="The room, for a stay that starts checked in.",
    )
    booked_by_name: str = Field(
        tag=7, default="", description="Who took the booking."
    )


class ReservationGetResponse(Model):
    reservation: Optional[ReservationView] = Field(
        tag=1, default=None, description="The reservation as it is now."
    )


class MarkCheckedInRequest(Model):
    room_number: str = Field(
        tag=1, default="", description="The room the guest was given."
    )
    early_check_in_approved_by_name: str = Field(
        tag=2,
        default="",
        description="The manager checking the guest in before 3 pm, whose "
        "doing so approves it; empty otherwise.",
    )


ReservationMethods = Methods(
    create=Writer(
        request=ReservationCreateRequest,
        response=None,
        factory=True,
        description="Record a booked stay. Called only by the hotel once "
        "the nights are secured.",
        mcp=None,
    ),
    get=Reader(
        request=None,
        response=ReservationGetResponse,
        description="The stay's guest, dates, status and room. Any member "
        "of staff may read it.",
        mcp=None,
    ),
    mark_checked_in=Writer(
        request=MarkCheckedInRequest,
        response=None,
        description="Record that the guest arrived and which room they "
        "were given. Called only by the hotel's check-in.",
        mcp=None,
    ),
    approve_early_check_in=Writer(
        request=None,
        response=None,
        errors=[BookingStateError],
        description="Let a booked guest be checked in before 3 pm on "
        "arrival day, recording who approved it. Raises "
        "`BookingStateError` unless the stay is booked. Managers only.",
        mcp=None,
    ),
    mark_checked_out=Writer(
        request=None,
        response=None,
        description="Record that the guest left. Called only by the "
        "hotel's check-out.",
        mcp=None,
    ),
    mark_cancelled=Writer(
        request=None,
        response=None,
        description="Record that the booking was cancelled. Called only by "
        "the hotel, which frees the nights in the same step.",
        mcp=None,
    ),
)

class InventoryState(Model):
    room_type: str = Field(
        tag=1, default="", description="The room type this counts."
    )
    total_rooms: int = Field(
        tag=2,
        default=0,
        description="How many rooms of this type the hotel has.",
    )
    booked: dict[str, int] = Field(
        tag=3,
        default_factory=dict,
        description="Stays booked or in house per night (YYYY-MM-DD), never "
        "above `total_rooms`. One entry per night with any booking, a few "
        "hundred a year.",
    )


class InventoryCreateRequest(Model):
    room_type: str = Field(tag=1, default="", description="The room type.")
    total_rooms: int = Field(
        tag=2, default=0, description="How many rooms of it there are."
    )
    booked: dict[str, int] = Field(
        tag=3,
        default_factory=dict,
        description="Nights already booked when the app is set up.",
    )


class NightsRequest(Model):
    arrival: str = Field(
        tag=1, default="", description="First night, YYYY-MM-DD."
    )
    departure: str = Field(
        tag=2,
        default="",
        description="Departure morning, YYYY-MM-DD (not counted).",
    )


class AvailabilityRequest(Model):
    start: str = Field(
        tag=1, default="", description="The first night, YYYY-MM-DD."
    )
    days: int = Field(
        tag=2, default=0, description="How many nights to report."
    )


class NightLeft(Model):
    date: str = Field(tag=1, default="", description="The night, YYYY-MM-DD.")
    left: int = Field(
        tag=2,
        default=0,
        description="Rooms of the type still free to book that night.",
    )


class TypeAvailability(Model):
    room_type: str = Field(tag=1, default="", description="The room type.")
    total_rooms: int = Field(
        tag=2, default=0, description="How many rooms of it there are."
    )
    nights: list[NightLeft] = Field(
        tag=3,
        default_factory=list,
        description="Rooms left per night, in date order.",
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


InventoryMethods = Methods(
    create=Writer(
        request=InventoryCreateRequest,
        response=None,
        factory=True,
        description="Start counting one room type. Called only by the hotel "
        "when the front desk is set up.",
        mcp=None,
    ),
    reserve=Writer(
        request=NightsRequest,
        response=None,
        errors=[SoldOutError],
        description="Take one room of this type for each night of a stay, "
        "or raise `SoldOutError` naming the first full night and take "
        "none. Called only by the hotel's booking.",
        mcp=None,
    ),
    release=Writer(
        request=NightsRequest,
        response=None,
        description="Give back one room of this type for each night of a "
        "stay. Called only by the hotel's cancellation.",
        mcp=None,
    ),
    availability=Reader(
        request=AvailabilityRequest,
        response=TypeAvailability,
        description="Rooms of this type still free on each of the coming "
        "nights. Any member of staff may read it.",
        mcp=None,
    ),
)


api = API(
    Reservation=Type(
        state=ReservationState,
        methods=ReservationMethods,
        description="One guest's stay, from booking to check-out. Its id is "
        "the confirmation code given to the guest.",
    ),
    Inventory=Type(
        state=InventoryState,
        methods=InventoryMethods,
        description="One room type's booked nights. Every booking of the "
        "type goes through this one object, which is what keeps it from "
        "being booked beyond its rooms.",
    ),
)
