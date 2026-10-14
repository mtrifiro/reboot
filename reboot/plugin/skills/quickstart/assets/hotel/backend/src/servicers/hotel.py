import asyncio

from hotel.v1.hotel import RoomView
from hotel.v1.hotel_rbt import Hotel, Room
from reboot.aio.auth.authorizers import allow
from reboot.aio.contexts import ReaderContext, TransactionContext, WriterContext


class HotelServicer(Hotel.Servicer):

    def authorizer(self):
        # `create` and `add_floor` are left out, so only the app itself
        # may call them.
        return Hotel.Authorizer(floor_plan=allow())

    async def create(
        self,
        context: WriterContext,
        request: Hotel.CreateRequest,
    ) -> None:
        self.state.name = request.name

    async def add_floor(
        self,
        context: TransactionContext,
        request: Hotel.AddFloorRequest,
    ) -> None:
        for spec in request.rooms:
            if spec.number in self.state.room_ids:
                continue
            await Room.create(
                context,
                spec.number,
                number=spec.number,
                floor=spec.floor,
                room_type=spec.room_type,
                status=spec.status,
                guest_name=spec.guest_name,
            )
            self.state.room_ids.append(spec.number)

    async def floor_plan(
        self,
        context: ReaderContext,
    ) -> Hotel.FloorPlanResponse:
        responses = await asyncio.gather(
            *(Room.ref(room_id).get(context) for room_id in self.state.room_ids)
        )
        rooms: list[RoomView] = [r.room for r in responses if r.room is not None]
        return Hotel.FloorPlanResponse(hotel_name=self.state.name, rooms=rooms)
