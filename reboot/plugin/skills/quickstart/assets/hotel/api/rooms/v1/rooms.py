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


RoomStatus = Literal[
    "vacant_dirty",
    "cleaning",
    "vacant_clean",
    "inspected",
    "occupied",
    "out_of_order",
]

class RoomState(Model):
    number: str = Field(
        tag=1,
        default="",
        description="The room number guests and staff use, such as "
        "\"204\"; also this room's state id.",
    )
    floor: int = Field(
        tag=2,
        default=0,
        description="The floor the room is on; the first digit of its "
        "number.",
    )
    room_type: str = Field(
        tag=3,
        default="",
        description="The category the room is sold as: Deluxe King, "
        "Deluxe Twin, Junior Suite, Suite or Penthouse.",
    )
    features: list[str] = Field(
        tag=4,
        default_factory=list,
        description="The room's signature amenities, shown to staff so "
        "they can describe the room to a guest (a soaking tub, a "
        "terrace).",
    )
    status: RoomStatus = Field(
        tag=5,
        default="vacant_dirty",
        description="Where the room is in its cycle: vacant_dirty after "
        "a check-out, cleaning while housekeeping works on it, "
        "vacant_clean when cleaned, inspected once a second person has "
        "checked it, occupied while a guest is in it, or out_of_order "
        "while it can't be sold.",
    )
    guest_name: str = Field(
        tag=6,
        default="",
        description="The guest staying in the room; empty unless the "
        "room is occupied.",
    )
    cleaned_by_user_id: str = Field(
        tag=7,
        default="",
        description="Who cleaned the room since its last check-out; "
        "empty until it is cleaned. That person may not inspect it.",
    )
    cleaned_by_name: str = Field(
        tag=8,
        default="",
        description="The display name of whoever cleaned the room, for "
        "the floor plan.",
    )
    out_of_order_reason: str = Field(
        tag=9,
        default="",
        description="Why the room can't be sold; set only while it is "
        "out_of_order.",
    )
    last_changed_by_name: str = Field(
        tag=10,
        default="",
        description="Who last changed the room's status.",
    )
    last_changed_at: str = Field(
        tag=11,
        default="",
        description="When the room's status last changed, as an ISO 8601 "
        "UTC timestamp.",
    )
    reservation_id: str = Field(
        tag=12,
        default="",
        description="The Reservation of the stay in the room; empty when "
        "vacant, or for a walk-in checked in from the floor plan.",
    )


class RoomView(Model):
    number: str = Field(tag=1, default="", description="The room number.")
    floor: int = Field(tag=2, default=0, description="The room's floor.")
    room_type: str = Field(
        tag=3, default="", description="The category the room is sold as."
    )
    features: list[str] = Field(
        tag=4,
        default_factory=list,
        description="The room's signature amenities.",
    )
    status: RoomStatus = Field(
        tag=5,
        default="vacant_dirty",
        description="Where the room is in its cycle; see the Room's "
        "`status`.",
    )
    guest_name: str = Field(
        tag=6, default="", description="The guest in the room, if occupied."
    )
    cleaned_by_name: str = Field(
        tag=7,
        default="",
        description="Who cleaned the room since its last check-out.",
    )
    out_of_order_reason: str = Field(
        tag=8,
        default="",
        description="Why the room can't be sold, while out of order.",
    )
    last_changed_by_name: str = Field(
        tag=9, default="", description="Who last changed the status."
    )
    last_changed_at: str = Field(
        tag=10,
        default="",
        description="When the status last changed, ISO 8601 UTC.",
    )
    reservation_id: str = Field(
        tag=11,
        default="",
        description="The Reservation of the stay in the room, if any.",
    )


class RoomCreateRequest(Model):
    number: str = Field(tag=1, default="", description="The room number.")
    floor: int = Field(tag=2, default=0, description="The room's floor.")
    room_type: str = Field(
        tag=3, default="", description="The category the room is sold as."
    )
    features: list[str] = Field(
        tag=4,
        default_factory=list,
        description="The room's signature amenities.",
    )
    status: RoomStatus = Field(
        tag=5,
        default="vacant_dirty",
        description="The status the room starts in.",
    )
    guest_name: str = Field(
        tag=6,
        default="",
        description="The guest already in the room, when it starts "
        "occupied.",
    )
    cleaned_by_name: str = Field(
        tag=7,
        default="",
        description="Who already cleaned it, when it starts clean or "
        "inspected.",
    )
    out_of_order_reason: str = Field(
        tag=8,
        default="",
        description="Why it can't be sold, when it starts out of order.",
    )
    reservation_id: str = Field(
        tag=9,
        default="",
        description="The Reservation of the stay already in the room, when "
        "it starts occupied.",
    )


class RoomGetResponse(Model):
    room: Optional[RoomView] = Field(
        tag=1, default=None, description="The room as it is now."
    )


class CheckInRequest(Model):
    guest_name: str = Field(
        tag=1,
        default="",
        description="The name of the guest taking the room; required.",
    )
    reservation_id: str = Field(
        tag=2,
        default="",
        description="The Reservation being checked in, when the guest "
        "booked; empty for a walk-in.",
    )


class OutOfOrderRequest(Model):
    reason: str = Field(
        tag=1,
        default="",
        description="Why the room can't be sold, for engineering and the "
        "front desk; required.",
    )


class RoomNotReadyError(Model):
    status: RoomStatus = Field(
        tag=1,
        default="vacant_dirty",
        description="The status the room was in, which is not inspected.",
    )


class SameInspectorError(Model):
    cleaned_by_name: str = Field(
        tag=1,
        default="",
        description="Who cleaned the room, and so may not inspect it.",
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


class MissingDetailError(Model):
    detail: str = Field(
        tag=1,
        default="",
        description="The name of the request property that was left "
        "empty.",
    )


RoomMethods = Methods(
    create=Writer(
        request=RoomCreateRequest,
        response=None,
        factory=True,
        description="Bring a room into existence with its number, type, "
        "amenities and starting status. Called only by the hotel when it "
        "lays out its floors.",
        mcp=None,
    ),
    get=Reader(
        request=None,
        response=RoomGetResponse,
        description="The room's current status, guest and who last "
        "touched it. Any member of staff may read it.",
        mcp=None,
    ),
    start_cleaning=Writer(
        request=None,
        response=None,
        errors=[InvalidTransitionError],
        description="Housekeeping starts cleaning a vacant dirty room. "
        "Raises `InvalidTransitionError` from any other status. "
        "Housekeeping or managers only.",
        mcp=None,
    ),
    mark_clean=Writer(
        request=None,
        response=None,
        errors=[InvalidTransitionError],
        description="Housekeeping finishes cleaning; the room becomes "
        "vacant clean and remembers who cleaned it. Raises "
        "`InvalidTransitionError` unless the room is being cleaned or "
        "dirty. Housekeeping or managers only.",
        mcp=None,
    ),
    inspect_room=Writer(
        request=None,
        response=None,
        errors=[InvalidTransitionError, SameInspectorError],
        description="A second person signs off a clean room as ready to "
        "sell. Raises `SameInspectorError` if the caller cleaned it, and "
        "`InvalidTransitionError` unless it is vacant clean. Housekeeping "
        "or managers only.",
        mcp=None,
    ),
    check_in=Writer(
        request=CheckInRequest,
        response=None,
        errors=[RoomNotReadyError, MissingDetailError, EarlyCheckInError],
        description="Put a walk-in guest into an inspected room. Raises "
        "`RoomNotReadyError` if the room is not inspected, "
        "`MissingDetailError` without a guest name, and "
        "`EarlyCheckInError` before 3 pm hotel time unless the caller is "
        "a manager. Front desk or managers only; a `reservation_id` may "
        "be given only by the hotel's own check-in.",
        mcp=None,
    ),
    check_out=Writer(
        request=None,
        response=None,
        errors=[InvalidTransitionError],
        description="The guest leaves; the room becomes vacant dirty. "
        "Raises `InvalidTransitionError` unless it is occupied. Front "
        "desk or managers only.",
        mcp=None,
    ),
    take_out_of_order=Writer(
        request=OutOfOrderRequest,
        response=None,
        errors=[InvalidTransitionError, MissingDetailError],
        description="Stop selling a room, with a reason. Raises "
        "`MissingDetailError` without a reason and "
        "`InvalidTransitionError` if a guest is in it. Managers only.",
        mcp=None,
    ),
    return_to_service=Writer(
        request=None,
        response=None,
        errors=[InvalidTransitionError],
        description="Put an out-of-order room back into the cycle as "
        "vacant dirty, so housekeeping cleans it before it is sold. "
        "Managers only.",
        mcp=None,
    ),
)


api = API(
    Room=Type(
        state=RoomState,
        methods=RoomMethods,
        description="One of the hotel's rooms, keyed by its number. Each "
        "room changes status one step at a time, which is what keeps two "
        "people from checking guests into it at once.",
    ),
)
