import asyncio

import clock
from datetime import date, timedelta
from uuid import uuid4

from hotel.v1.hotel import (
    BookingStateError,
    EarlyCheckInError,
    InvalidDatesError,
    InvalidTransitionError,
    MissingDetailError,
    RoomNotReadyError,
    SoldOutError,
    WrongRoomTypeError,
)
from reservations.v1 import reservations
from reservations.v1.reservations import ReservationView
from rooms.v1.rooms import RoomView
from hotel.v1.hotel_rbt import Hotel
from reservations.v1.reservations_rbt import Inventory, Reservation
from rooms.v1.rooms_rbt import Room
from staff.v1.staff_rbt import Team
from layout import ROOM_TYPES
from reboot.aio.auth.authorizers import allow_if
from reboot.aio.contexts import ReaderContext, TransactionContext, WriterContext
from reboot.std.collections.ordered_map.v1.ordered_map import OrderedMap
from reboot.std.item.v1.item import Item
from servicers.auth import (
    TEAM_ID,
    caller_role,
    has_role_for_method,
    is_staff,
)

MAX_NIGHTS = 60
FRONT_DESK_DAYS = 14


def _index_key(arrival: str, reservation_id: str) -> str:
    # Arrival first, so a range over the map reads stays in date order.
    return f"{arrival}/{reservation_id}"


class HotelServicer(Hotel.Servicer):

    def authorizer(self):
        # `create`, `add_floor`, `setup_front_desk` and `add_bookings`
        # are left out, so only the app itself may call them.
        staff = allow_if(all=[is_staff])
        by_role = allow_if(all=[has_role_for_method])
        return Hotel.Authorizer(
            floor_plan=staff,
            front_desk=staff,
            book=by_role,
            cancel_booking=by_role,
            check_in_booking=by_role,
            check_out_room=by_role,
        )

    async def _rooms(self, context: ReaderContext) -> list[RoomView]:
        responses = await asyncio.gather(
            *(Room.ref(room_id).get(context) for room_id in self.state.room_ids)
        )
        return [r.room for r in responses if r.room is not None]

    async def _reservations(
        self, context: ReaderContext, ids: list[str]
    ) -> list[ReservationView]:
        responses = await asyncio.gather(
            *(Reservation.ref(rid).get(context) for rid in ids)
        )
        return [r.reservation for r in responses if r.reservation is not None]

    async def _reservation(
        self, context: TransactionContext, reservation_id: str
    ) -> ReservationView:
        response = await Reservation.ref(reservation_id).get(context)
        assert response.reservation is not None
        return response.reservation

    async def _room(self, context: TransactionContext, number: str) -> RoomView:
        response = await Room.ref(number).get(context)
        assert response.room is not None
        return response.room

    # -- Setup ---------------------------------------------------------------

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
                features=list(spec.features),
                status=spec.status,
                guest_name=spec.guest_name,
                cleaned_by_name=spec.cleaned_by_name,
                out_of_order_reason=spec.out_of_order_reason,
                reservation_id=spec.reservation_id,
            )
            self.state.room_ids.append(spec.number)

    async def setup_front_desk(
        self,
        context: TransactionContext,
        request: Hotel.SetupFrontDeskRequest,
    ) -> None:
        if self.state.reservations_index_id:
            return
        self.state.reservations_index_id = str(uuid4())
        # Constructed up front: the front desk reads it before the first
        # booking.
        await OrderedMap.ref(self.state.reservations_index_id).create(context)
        for spec in request.inventories:
            inventory_id = str(uuid4())
            await Inventory.create(
                context,
                inventory_id,
                room_type=spec.room_type,
                total_rooms=spec.total_rooms,
                booked=dict(spec.booked),
            )
            self.state.inventory_ids[spec.room_type] = inventory_id

    async def add_bookings(
        self,
        context: TransactionContext,
        request: Hotel.AddBookingsRequest,
    ) -> None:
        entries: dict[str, Item] = {}
        for reservation_id, b in zip(request.reservation_ids, request.bookings):
            await Reservation.create(
                context,
                reservation_id,
                guest_name=b.guest_name,
                room_type=b.room_type,
                arrival=b.arrival,
                departure=b.departure,
                status=b.status,
                room_number=b.room_number,
                booked_by_name=b.booked_by_name,
            )
            entries[_index_key(b.arrival, reservation_id)] = Item(
                bytes=reservation_id.encode()
            )
        if entries:
            await OrderedMap.ref(self.state.reservations_index_id).insert(
                context, entries=entries
            )

    # -- Floor plan ------------------------------------------------------------

    async def floor_plan(
        self,
        context: ReaderContext,
    ) -> Hotel.FloorPlanResponse:
        return Hotel.FloorPlanResponse(
            hotel_name=self.state.name, rooms=await self._rooms(context)
        )

    # -- Front desk ------------------------------------------------------------

    async def book(
        self,
        context: TransactionContext,
        request: Hotel.BookRequest,
    ) -> Hotel.BookResponse:
        guest_name = request.guest_name.strip()
        if not guest_name:
            raise Hotel.BookAborted(MissingDetailError(detail="guest_name"))
        inventory_id = self.state.inventory_ids.get(request.room_type)
        if inventory_id is None:
            raise Hotel.BookAborted(MissingDetailError(detail="room_type"))
        try:
            arrival = date.fromisoformat(request.arrival)
            departure = date.fromisoformat(request.departure)
        except ValueError:
            raise Hotel.BookAborted(
                InvalidDatesError(reason="Dates must be given as YYYY-MM-DD.")
            )
        if departure <= arrival:
            raise Hotel.BookAborted(
                InvalidDatesError(reason="Departure must be after arrival.")
            )
        if (departure - arrival).days > MAX_NIGHTS:
            raise Hotel.BookAborted(
                InvalidDatesError(
                    reason=f"A stay is at most {MAX_NIGHTS} nights."
                )
            )

        try:
            await Inventory.ref(inventory_id).reserve(
                context,
                arrival=request.arrival,
                departure=request.departure,
            )
        except Inventory.ReserveAborted as aborted:
            if isinstance(aborted.error, reservations.SoldOutError):
                # The Hotel package's own copy of the error (see its API).
                raise Hotel.BookAborted(
                    SoldOutError(**aborted.error.model_dump())
                )
            raise

        booked_by = ""
        if context.auth is not None and context.auth.user_id is not None:
            member = await Team.ref(TEAM_ID).member_of(
                context, user_id=context.auth.user_id
            )
            booked_by = member.name

        reservation_id = f"MV-{uuid4().hex[:6].upper()}"
        await Reservation.create(
            context,
            reservation_id,
            guest_name=guest_name,
            room_type=request.room_type,
            arrival=request.arrival,
            departure=request.departure,
            booked_by_name=booked_by,
        )
        await OrderedMap.ref(self.state.reservations_index_id).insert(
            context,
            key=_index_key(request.arrival, reservation_id),
            bytes=reservation_id.encode(),
        )
        return Hotel.BookResponse(reservation_id=reservation_id)

    async def cancel_booking(
        self,
        context: TransactionContext,
        request: Hotel.CancelBookingRequest,
    ) -> None:
        stay = await self._reservation(context, request.reservation_id)
        if stay.status != "booked":
            raise Hotel.CancelBookingAborted(
                BookingStateError(status=stay.status)
            )
        await Inventory.ref(self.state.inventory_ids[stay.room_type]).release(
            context, arrival=stay.arrival, departure=stay.departure
        )
        await Reservation.ref(request.reservation_id).mark_cancelled(context)

    async def check_in_booking(
        self,
        context: TransactionContext,
        request: Hotel.CheckInBookingRequest,
    ) -> None:
        stay = await self._reservation(context, request.reservation_id)
        if stay.status != "booked":
            raise Hotel.CheckInBookingAborted(
                BookingStateError(status=stay.status)
            )
        room = await self._room(context, request.room_number)
        # The room's own rule, checked here first so the refusal names
        # this method's error.
        if room.status != "inspected":
            raise Hotel.CheckInBookingAborted(
                RoomNotReadyError(status=room.status)
            )
        if room.room_type != stay.room_type:
            raise Hotel.CheckInBookingAborted(
                WrongRoomTypeError(
                    booked=stay.room_type, room_type=room.room_type
                )
            )
        approved_by = ""
        if (
            not stay.early_check_in_approved_by_name
            and not clock.check_in_open(stay.arrival)
        ):
            if await caller_role(context) != "manager":
                raise Hotel.CheckInBookingAborted(
                    EarlyCheckInError(
                        check_in_time=clock.CHECK_IN_TIME.strftime("%H:%M"),
                        time_zone=clock.HOTEL_TIME_ZONE,
                    )
                )
            # A manager checking a guest in early approves it.
            assert context.auth is not None and context.auth.user_id
            member = await Team.ref(TEAM_ID).member_of(
                context, user_id=context.auth.user_id
            )
            approved_by = member.name or "Manager"
        await Room.ref(request.room_number).check_in(
            context,
            guest_name=stay.guest_name,
            reservation_id=request.reservation_id,
        )
        await Reservation.ref(request.reservation_id).mark_checked_in(
            context,
            room_number=request.room_number,
            early_check_in_approved_by_name=approved_by,
        )

    async def check_out_room(
        self,
        context: TransactionContext,
        request: Hotel.CheckOutRoomRequest,
    ) -> None:
        room = await self._room(context, request.room_number)
        if room.status != "occupied":
            raise Hotel.CheckOutRoomAborted(
                InvalidTransitionError(status=room.status, action="check_out")
            )
        await Room.ref(request.room_number).check_out(context)
        if room.reservation_id:
            await Reservation.ref(room.reservation_id).mark_checked_out(context)

    async def front_desk(
        self,
        context: ReaderContext,
        request: Hotel.FrontDeskRequest,
    ) -> Hotel.FrontDeskResponse:
        day = request.date or clock.today()
        end = (
            date.fromisoformat(day) + timedelta(days=FRONT_DESK_DAYS)
        ).isoformat()

        rooms = await self._rooms(context)
        in_house = [r for r in rooms if r.status == "occupied"]

        upcoming_ids: list[str] = []
        if self.state.reservations_index_id:
            page = await OrderedMap.ref(self.state.reservations_index_id).range(
                context, start_key=day, limit=1000
            )
            upcoming_ids = [
                e.bytes.decode() for e in page.entries if e.key < end
            ]
        upcoming, staying = await asyncio.gather(
            self._reservations(context, upcoming_ids),
            self._reservations(
                context, [r.reservation_id for r in in_house if r.reservation_id]
            ),
        )

        availability = await asyncio.gather(
            *(
                Inventory.ref(self.state.inventory_ids[room_type]).availability(
                    context, start=day, days=FRONT_DESK_DAYS
                )
                for room_type in ROOM_TYPES
                if room_type in self.state.inventory_ids
            )
        )

        return Hotel.FrontDeskResponse(
            arrivals=[
                s
                for s in upcoming
                if s.arrival == day and s.status in ("booked", "checked_in")
            ],
            departures=[
                s
                for s in staying
                if s.departure <= day and s.status == "checked_in"
            ],
            upcoming=[
                s for s in upcoming if s.arrival > day and s.status == "booked"
            ],
            availability=list(availability),
            ready_rooms=[r for r in rooms if r.status == "inspected"],
            in_house=len(in_house),
            time_zone=clock.HOTEL_TIME_ZONE,
            check_in_time=clock.CHECK_IN_TIME.strftime("%H:%M"),
        )
