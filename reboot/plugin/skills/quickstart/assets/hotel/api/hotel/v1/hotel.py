from typing import Literal, Optional

from reboot.api import (
    API,
    Exclusive,
    Field,
    Methods,
    Model,
    Reader,
    Transaction,
    Type,
    Writer,
)

RoomStatus = Literal["dirty", "clean", "occupied"]

# ---------------------------------------------------------------------------
# Room
# ---------------------------------------------------------------------------


class RoomState(Model):
    number: str = Field(
        tag=1,
        default="",
        description="The room number guests and staff use, such as "
        "\"204\"; also this room's state id.",
    )
    floor: int = Field(
        tag=2, default=0, description="The floor the room is on."
    )
    room_type: str = Field(
        tag=3,
        default="",
        description="The category the room is sold as: Deluxe King, "
        "Deluxe Twin, Junior Suite, Suite or Penthouse.",
    )
    status: RoomStatus = Field(
        tag=4,
        default="dirty",
        description="Where the room is in its cycle: dirty after a "
        "check-out, clean once housekeeping is done, occupied while a "
        "guest is in it.",
    )
    guest_name: str = Field(
        tag=5,
        default="",
        description="The guest staying in the room; empty unless the "
        "room is occupied.",
    )


class RoomView(Model):
    number: str = Field(tag=1, default="", description="The room number.")
    floor: int = Field(tag=2, default=0, description="The room's floor.")
    room_type: str = Field(
        tag=3, default="", description="The category the room is sold as."
    )
    status: RoomStatus = Field(
        tag=4, default="dirty", description="Where the room is in its cycle."
    )
    guest_name: str = Field(
        tag=5, default="", description="The guest in the room, if occupied."
    )


class RoomCreateRequest(Model):
    number: str = Field(tag=1, default="", description="The room number.")
    floor: int = Field(tag=2, default=0, description="The room's floor.")
    room_type: str = Field(
        tag=3, default="", description="The category the room is sold as."
    )
    status: RoomStatus = Field(
        tag=4, default="dirty", description="The status the room starts in."
    )
    guest_name: str = Field(
        tag=5,
        default="",
        description="The guest already in the room, when it starts "
        "occupied.",
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


class RoomNotReadyError(Model):
    status: RoomStatus = Field(
        tag=1,
        default="dirty",
        description="The status the room was in, which is not clean.",
    )


class InvalidTransitionError(Model):
    status: RoomStatus = Field(
        tag=1,
        default="dirty",
        description="The status the room was in, from which the "
        "requested step is not possible.",
    )
    action: str = Field(
        tag=2,
        default="",
        description="The step that was refused, such as \"check_out\".",
    )


class MissingGuestNameError(Model):
    pass


RoomMethods = Methods(
    create=Writer(
        request=RoomCreateRequest,
        response=None,
        factory=True,
        description="Bring a room into existence with its number, type and "
        "starting status. Called only by the hotel when it lays out its "
        "floors.",
        mcp=None,
    ),
    get=Reader(
        request=None,
        response=RoomGetResponse,
        description="The room's current status and guest.",
        mcp=None,
    ),
    mark_clean=Writer(
        request=None,
        response=None,
        errors=[InvalidTransitionError],
        description="Housekeeping finishes a dirty room; it becomes clean. "
        "Raises `InvalidTransitionError` unless the room is dirty.",
        mcp=None,
    ),
    check_in=Writer(
        request=CheckInRequest,
        response=None,
        errors=[RoomNotReadyError, MissingGuestNameError],
        description="Put a guest into a clean room. Raises "
        "`RoomNotReadyError` if the room is not clean, and "
        "`MissingGuestNameError` without a guest name.",
        mcp=None,
    ),
    check_out=Writer(
        request=None,
        response=None,
        errors=[InvalidTransitionError],
        description="The guest leaves; the room becomes dirty. Raises "
        "`InvalidTransitionError` unless it is occupied.",
        mcp=None,
    ),
)

# ---------------------------------------------------------------------------
# Hotel
# ---------------------------------------------------------------------------


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
        description="Every room in the hotel with its live status and "
        "guest: the answer to which rooms can take a guest now.",
        mcp=None,
    ),
)


api = API(
    Room=Type(
        state=RoomState,
        methods=RoomMethods,
        description="One of the hotel's rooms, keyed by its number. Each "
        "room runs its changes one at a time, which is what keeps two "
        "desks from checking guests into it at once.",
    ),
    Hotel=Type(
        state=HotelState,
        methods=HotelMethods,
        description="The property: one per hotel (id \"hotel\"), owning "
        "the list of its rooms and serving the floor plan.",
    ),
)
