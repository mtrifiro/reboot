from datetime import datetime, timezone

from reservations.v1.reservations import BookingStateError, ReservationView
from reservations.v1.reservations_rbt import Reservation
from staff.v1.staff_rbt import Team
from reboot.aio.auth.authorizers import allow_if
from reboot.aio.contexts import ReaderContext, WriterContext
from servicers.auth import TEAM_ID, has_role_for_method, is_staff


class ReservationServicer(Reservation.Servicer):

    def authorizer(self):
        # Every other change goes through the Hotel, which checks the
        # dates, the inventory and the room together.
        return Reservation.Authorizer(
            get=allow_if(all=[is_staff]),
            approve_early_check_in=allow_if(all=[has_role_for_method]),
        )

    def view(self) -> ReservationView:
        s = self.state
        return ReservationView(
            reservation_id=self.ref().state_id,
            guest_name=s.guest_name,
            room_type=s.room_type,
            arrival=s.arrival,
            departure=s.departure,
            status=s.status,
            room_number=s.room_number,
            booked_by_name=s.booked_by_name,
            early_check_in_approved_by_name=s.early_check_in_approved_by_name,
        )

    async def create(
        self,
        context: WriterContext,
        request: Reservation.CreateRequest,
    ) -> None:
        self.state.guest_name = request.guest_name
        self.state.room_type = request.room_type
        self.state.arrival = request.arrival
        self.state.departure = request.departure
        self.state.status = request.status
        self.state.room_number = request.room_number
        self.state.booked_by_name = request.booked_by_name
        self.state.booked_at = datetime.now(timezone.utc).isoformat()

    async def get(self, context: ReaderContext) -> Reservation.GetResponse:
        return Reservation.GetResponse(reservation=self.view())

    async def mark_checked_in(
        self,
        context: WriterContext,
        request: Reservation.MarkCheckedInRequest,
    ) -> None:
        self.state.status = "checked_in"
        self.state.room_number = request.room_number
        if request.early_check_in_approved_by_name:
            self.state.early_check_in_approved_by_name = (
                request.early_check_in_approved_by_name
            )
            self.state.early_check_in_approved_at = datetime.now(
                timezone.utc
            ).isoformat()

    async def approve_early_check_in(self, context: WriterContext) -> None:
        if self.state.status != "booked":
            raise Reservation.ApproveEarlyCheckInAborted(
                BookingStateError(status=self.state.status)
            )
        name = "Manager"
        if context.auth is not None and context.auth.user_id is not None:
            member = await Team.ref(TEAM_ID).member_of(
                context, user_id=context.auth.user_id
            )
            name = member.name or name
        self.state.early_check_in_approved_by_name = name
        self.state.early_check_in_approved_at = datetime.now(
            timezone.utc
        ).isoformat()

    async def mark_checked_out(self, context: WriterContext) -> None:
        self.state.status = "checked_out"

    async def mark_cancelled(self, context: WriterContext) -> None:
        self.state.status = "cancelled"
