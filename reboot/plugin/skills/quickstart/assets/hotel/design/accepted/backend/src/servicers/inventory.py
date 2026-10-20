from datetime import date, timedelta

from reservations.v1.reservations import NightLeft, SoldOutError
from reservations.v1.reservations_rbt import Inventory
from reboot.aio.auth.authorizers import allow_if
from reboot.aio.contexts import ReaderContext, WriterContext
from servicers.auth import is_staff


def nights(arrival: str, departure: str) -> list[str]:
    """Every night of a stay: from arrival up to, not including, departure."""
    start, end = date.fromisoformat(arrival), date.fromisoformat(departure)
    return [
        (start + timedelta(days=n)).isoformat()
        for n in range((end - start).days)
    ]


class InventoryServicer(Inventory.Servicer):

    def authorizer(self):
        # `reserve` and `release` only through the Hotel's booking and
        # cancellation; reading what's left is open to staff.
        return Inventory.Authorizer(availability=allow_if(all=[is_staff]))

    async def create(
        self,
        context: WriterContext,
        request: Inventory.CreateRequest,
    ) -> None:
        self.state.room_type = request.room_type
        self.state.total_rooms = request.total_rooms
        self.state.booked = dict(request.booked)

    async def reserve(
        self,
        context: WriterContext,
        request: Inventory.ReserveRequest,
    ) -> None:
        stay = nights(request.arrival, request.departure)
        for night in stay:
            if self.state.booked.get(night, 0) >= self.state.total_rooms:
                raise Inventory.ReserveAborted(
                    SoldOutError(room_type=self.state.room_type, night=night)
                )
        for night in stay:
            self.state.booked[night] = self.state.booked.get(night, 0) + 1

    async def release(
        self,
        context: WriterContext,
        request: Inventory.ReleaseRequest,
    ) -> None:
        for night in nights(request.arrival, request.departure):
            left = self.state.booked.get(night, 0) - 1
            if left > 0:
                self.state.booked[night] = left
            else:
                self.state.booked.pop(night, None)

    async def availability(
        self,
        context: ReaderContext,
        request: Inventory.AvailabilityRequest,
    ) -> Inventory.AvailabilityResponse:
        start = date.fromisoformat(request.start)
        end = (start + timedelta(days=request.days)).isoformat()
        return Inventory.AvailabilityResponse(
            room_type=self.state.room_type,
            total_rooms=self.state.total_rooms,
            nights=[
                NightLeft(
                    date=night,
                    left=self.state.total_rooms
                    - self.state.booked.get(night, 0),
                )
                for night in nights(request.start, end)
            ],
        )
