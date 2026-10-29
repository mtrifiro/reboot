"""Who may do what: the predicates the servicers' authorizers use.

Access ("are you on staff at all") is asked of the `Team` roster; the
role a method needs comes from `ROLES`, keyed by the method's PascalCase
name as `context.method` spells it.
"""

from typing import Any

import rbt.v1alpha1.errors_pb2 as errors
from staff.v1.staff_rbt import Team
from reboot.aio.auth.authorizers import Authorizer
from reboot.aio.contexts import (
    ReaderContext,
    TransactionContext,
    WriterContext,
)

TEAM_ID = "team"
HOTEL_ID = "hotel"

ROLES: dict[str, set[str]] = {
    "StartCleaning": {"housekeeping", "manager"},
    "MarkClean": {"housekeeping", "manager"},
    "InspectRoom": {"housekeeping", "manager"},
    "CheckIn": {"front_desk", "manager"},
    "CheckOut": {"front_desk", "manager"},
    "TakeOutOfOrder": {"manager"},
    "ReturnToService": {"manager"},
    "Book": {"front_desk", "manager"},
    "CancelBooking": {"front_desk", "manager"},
    "CheckInBooking": {"front_desk", "manager"},
    "CheckOutRoom": {"front_desk", "manager"},
    "ApproveEarlyCheckIn": {"manager"},
}


async def caller_role(
    context: ReaderContext | WriterContext | TransactionContext,
) -> str:
    """The calling user's role on the roster; empty without one."""
    if context.auth is None or context.auth.user_id is None:
        return ""
    response = await Team.ref(TEAM_ID).member_of(
        context, user_id=context.auth.user_id
    )
    return response.role if response.member else ""


async def is_staff(
    *,
    context: ReaderContext,
    **kwargs: Any,
) -> Authorizer.Decision:
    """Anyone on the roster, with or without a role."""
    if context.app_internal:
        return errors.Ok()
    if context.auth is None or context.auth.user_id is None:
        return errors.Unauthenticated()
    response = await Team.ref(TEAM_ID).member_of(
        context, user_id=context.auth.user_id
    )
    return errors.Ok() if response.member else errors.PermissionDenied()


async def has_role_for_method(
    *,
    context: ReaderContext,
    **kwargs: Any,
) -> Authorizer.Decision:
    """A member whose role `ROLES` allows to call this method."""
    if context.app_internal:
        return errors.Ok()
    if context.auth is None or context.auth.user_id is None:
        return errors.Unauthenticated()
    allowed = ROLES.get(context.method.rsplit(".", 1)[-1], set())
    response = await Team.ref(TEAM_ID).member_of(
        context, user_id=context.auth.user_id
    )
    if response.member and response.role in allowed:
        return errors.Ok()
    return errors.PermissionDenied()
