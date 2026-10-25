from datetime import datetime, timezone
from typing import Any

import clock
import rbt.v1alpha1.errors_pb2 as errors

from rooms.v1.rooms import (
    EarlyCheckInError,
    InvalidTransitionError,
    MissingDetailError,
    RoomNotReadyError,
    RoomView,
    SameInspectorError,
)
from rooms.v1.rooms_rbt import Room
from staff.v1.staff_rbt import Team
from reboot.aio.auth.authorizers import (
    Authorizer,
    allow_if,
    is_app_internal,
)
from reboot.aio.contexts import ReaderContext, WriterContext
from servicers.auth import (
    TEAM_ID,
    caller_role,
    has_role_for_method,
    is_staff,
)


def walk_ins_only(
    *,
    context: ReaderContext,
    request: Any = None,
    **kwargs: Any,
) -> Authorizer.Decision:
    """Only the hotel's own check-in of a booked guest, which has already
    applied the 3 pm rule, may tie a check-in to a reservation."""
    if context.app_internal:
        return errors.Ok()
    if getattr(request, "reservation_id", ""):
        return errors.PermissionDenied()
    return errors.Ok()


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


class RoomServicer(Room.Servicer):

    def authorizer(self):
        return Room.Authorizer(
            create=allow_if(all=[is_app_internal]),
            get=allow_if(all=[is_staff]),
            check_in=allow_if(all=[walk_ins_only, has_role_for_method]),
            _default=allow_if(all=[has_role_for_method]),
        )

    async def _caller(self, context: WriterContext) -> tuple[str, str]:
        """The calling user's id and display name."""
        if context.auth is None or context.auth.user_id is None:
            return "", ""
        user_id = context.auth.user_id
        member = await Team.ref(TEAM_ID).member_of(context, user_id=user_id)
        return user_id, member.name or "Staff"

    def _changed(self, name: str) -> None:
        self.state.last_changed_by_name = name
        self.state.last_changed_at = _now()

    async def create(
        self,
        context: WriterContext,
        request: Room.CreateRequest,
    ) -> None:
        self.state.number = request.number
        self.state.floor = request.floor
        self.state.room_type = request.room_type
        self.state.features = list(request.features)
        self.state.status = request.status
        self.state.guest_name = request.guest_name
        self.state.cleaned_by_name = request.cleaned_by_name
        self.state.out_of_order_reason = request.out_of_order_reason
        self.state.reservation_id = request.reservation_id
        self.state.last_changed_by_name = "Opening setup"
        self.state.last_changed_at = _now()

    async def get(self, context: ReaderContext) -> Room.GetResponse:
        s = self.state
        return Room.GetResponse(
            room=RoomView(
                number=s.number,
                floor=s.floor,
                room_type=s.room_type,
                features=list(s.features),
                status=s.status,
                guest_name=s.guest_name,
                cleaned_by_name=s.cleaned_by_name,
                out_of_order_reason=s.out_of_order_reason,
                last_changed_by_name=s.last_changed_by_name,
                last_changed_at=s.last_changed_at,
                reservation_id=s.reservation_id,
            )
        )

    async def start_cleaning(self, context: WriterContext) -> None:
        if self.state.status != "vacant_dirty":
            raise Room.StartCleaningAborted(
                InvalidTransitionError(
                    status=self.state.status, action="start_cleaning"
                )
            )
        self.state.status = "cleaning"
        self._changed((await self._caller(context))[1])

    async def mark_clean(self, context: WriterContext) -> None:
        if self.state.status not in ("cleaning", "vacant_dirty"):
            raise Room.MarkCleanAborted(
                InvalidTransitionError(
                    status=self.state.status, action="mark_clean"
                )
            )
        user_id, name = await self._caller(context)
        self.state.status = "vacant_clean"
        self.state.cleaned_by_user_id = user_id
        self.state.cleaned_by_name = name
        self._changed(name)

    async def inspect_room(self, context: WriterContext) -> None:
        if self.state.status != "vacant_clean":
            raise Room.InspectRoomAborted(
                InvalidTransitionError(
                    status=self.state.status, action="inspect_room"
                )
            )
        user_id, name = await self._caller(context)
        if user_id and user_id == self.state.cleaned_by_user_id:
            raise Room.InspectRoomAborted(
                SameInspectorError(cleaned_by_name=self.state.cleaned_by_name)
            )
        self.state.status = "inspected"
        self._changed(name)

    async def check_in(
        self,
        context: WriterContext,
        request: Room.CheckInRequest,
    ) -> None:
        guest_name = request.guest_name.strip()
        if not guest_name:
            raise Room.CheckInAborted(MissingDetailError(detail="guest_name"))
        if self.state.status != "inspected":
            raise Room.CheckInAborted(
                RoomNotReadyError(status=self.state.status)
            )
        # A booked guest's check-in comes through the hotel, which has
        # applied the 3 pm rule; a walk-in arrives today.
        if (
            not request.reservation_id
            and not clock.check_in_open(clock.today())
            and await caller_role(context) != "manager"
        ):
            raise Room.CheckInAborted(
                EarlyCheckInError(
                    check_in_time=clock.CHECK_IN_TIME.strftime("%H:%M"),
                    time_zone=clock.HOTEL_TIME_ZONE,
                )
            )
        self.state.status = "occupied"
        self.state.guest_name = guest_name
        self.state.reservation_id = request.reservation_id
        self._changed((await self._caller(context))[1])

    async def check_out(self, context: WriterContext) -> None:
        if self.state.status != "occupied":
            raise Room.CheckOutAborted(
                InvalidTransitionError(
                    status=self.state.status, action="check_out"
                )
            )
        self.state.status = "vacant_dirty"
        self.state.guest_name = ""
        self.state.reservation_id = ""
        self.state.cleaned_by_user_id = ""
        self.state.cleaned_by_name = ""
        self._changed((await self._caller(context))[1])

    async def take_out_of_order(
        self,
        context: WriterContext,
        request: Room.TakeOutOfOrderRequest,
    ) -> None:
        reason = request.reason.strip()
        if not reason:
            raise Room.TakeOutOfOrderAborted(
                MissingDetailError(detail="reason")
            )
        if self.state.status == "occupied":
            raise Room.TakeOutOfOrderAborted(
                InvalidTransitionError(
                    status=self.state.status, action="take_out_of_order"
                )
            )
        self.state.status = "out_of_order"
        self.state.out_of_order_reason = reason
        self._changed((await self._caller(context))[1])

    async def return_to_service(self, context: WriterContext) -> None:
        if self.state.status != "out_of_order":
            raise Room.ReturnToServiceAborted(
                InvalidTransitionError(
                    status=self.state.status, action="return_to_service"
                )
            )
        # Back into the cycle dirty: whatever the repair left behind is
        # cleaned and inspected before the room is sold again.
        self.state.status = "vacant_dirty"
        self.state.out_of_order_reason = ""
        self.state.cleaned_by_user_id = ""
        self.state.cleaned_by_name = ""
        self._changed((await self._caller(context))[1])
