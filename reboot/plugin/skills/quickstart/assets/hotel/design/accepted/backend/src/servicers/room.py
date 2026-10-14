from hotel.v1.hotel import (
    InvalidTransitionError,
    MissingGuestNameError,
    RoomNotReadyError,
    RoomView,
)
from hotel.v1.hotel_rbt import Room
from reboot.aio.auth.authorizers import allow, allow_if, is_app_internal
from reboot.aio.contexts import ReaderContext, WriterContext


class RoomServicer(Room.Servicer):

    def authorizer(self):
        # Only the app lays out rooms; anyone at the desk may use them.
        # A real hotel signs its staff in: your own build asks who.
        return Room.Authorizer(
            create=allow_if(all=[is_app_internal]),
            _default=allow(),
        )

    async def create(
        self,
        context: WriterContext,
        request: Room.CreateRequest,
    ) -> None:
        self.state.number = request.number
        self.state.floor = request.floor
        self.state.room_type = request.room_type
        self.state.status = request.status
        self.state.guest_name = request.guest_name

    async def get(self, context: ReaderContext) -> Room.GetResponse:
        s = self.state
        return Room.GetResponse(
            room=RoomView(
                number=s.number,
                floor=s.floor,
                room_type=s.room_type,
                status=s.status,
                guest_name=s.guest_name,
            )
        )

    async def mark_clean(self, context: WriterContext) -> None:
        if self.state.status != "dirty":
            raise Room.MarkCleanAborted(
                InvalidTransitionError(
                    status=self.state.status, action="mark_clean"
                )
            )
        self.state.status = "clean"

    async def check_in(
        self,
        context: WriterContext,
        request: Room.CheckInRequest,
    ) -> None:
        guest_name = request.guest_name.strip()
        if not guest_name:
            raise Room.CheckInAborted(MissingGuestNameError())
        # The rule: a guest is checked in only to a clean room.
        if self.state.status != "clean":
            raise Room.CheckInAborted(
                RoomNotReadyError(status=self.state.status)
            )
        self.state.status = "occupied"
        self.state.guest_name = guest_name

    async def check_out(self, context: WriterContext) -> None:
        if self.state.status != "occupied":
            raise Room.CheckOutAborted(
                InvalidTransitionError(
                    status=self.state.status, action="check_out"
                )
            )
        # The rule: check-out always sends the room back to dirty.
        self.state.status = "dirty"
        self.state.guest_name = ""
