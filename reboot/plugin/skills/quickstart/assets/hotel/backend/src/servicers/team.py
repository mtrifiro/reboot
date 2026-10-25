import os
from typing import Any, Optional

import rbt.v1alpha1.errors_pb2 as errors
from staff.v1.staff import (
    Invitation,
    LastManagerError,
    Member,
    NotAMemberError,
    TeamState,
)
from staff.v1.staff_rbt import Team
from reboot.aio.auth.authorizers import (
    Authorizer,
    allow_if,
    has_verified_token,
)
from reboot.aio.contexts import ReaderContext, WriterContext


def _env_list(name: str) -> set[str]:
    return {
        part.strip().lower()
        for part in os.environ.get(name, "").split(",")
        if part.strip()
    }


def admin_emails() -> set[str]:
    return _env_list("ADMIN_EMAILS")


def allowlist_configured() -> bool:
    return bool(
        admin_emails()
        or _env_list("ALLOWED_EMAILS")
        or _env_list("ALLOWED_EMAIL_DOMAINS")
    )


def _allowed(email: str, verified: bool) -> bool:
    """May this address join the roster at all?

    With no allowlist (development and tests) anyone may; once one is
    set, only a verified address on it.
    """
    if not allowlist_configured():
        return True
    if not verified:
        return False
    domain = email.rsplit("@", 1)[-1]
    return (
        email in admin_emails()
        or email in _env_list("ALLOWED_EMAILS")
        or domain in _env_list("ALLOWED_EMAIL_DOMAINS")
    )


def _find(state: TeamState, user_id: str) -> Optional[Member]:
    return next((m for m in state.members if m.user_id == user_id), None)


def is_staff_on_roster(
    *,
    context: ReaderContext,
    state: Optional[TeamState] = None,
    **kwargs: Any,
) -> Authorizer.Decision:
    if context.app_internal:
        return errors.Ok()
    if context.auth is None or context.auth.user_id is None:
        return errors.Unauthenticated()
    if state is not None and _find(state, context.auth.user_id) is not None:
        return errors.Ok()
    return errors.PermissionDenied()


def is_manager_on_roster(
    *,
    context: ReaderContext,
    state: Optional[TeamState] = None,
    **kwargs: Any,
) -> Authorizer.Decision:
    if context.app_internal:
        return errors.Ok()
    if context.auth is None or context.auth.user_id is None:
        return errors.Unauthenticated()
    member = _find(state, context.auth.user_id) if state else None
    if member is not None and member.role == "manager":
        return errors.Ok()
    return errors.PermissionDenied()


class TeamServicer(Team.Servicer):

    def authorizer(self):
        # `create`, `member_of` and `register` are left out, so only the
        # app itself may call them.
        return Team.Authorizer(
            my_role=allow_if(all=[has_verified_token]),
            members=allow_if(all=[is_staff_on_roster]),
            invite=allow_if(all=[is_manager_on_roster]),
            set_role=allow_if(all=[is_manager_on_roster]),
        )

    def _answer(self, user_id: str) -> Team.MyRoleResponse:
        member = _find(self.state, user_id)
        if member is None:
            return Team.MyRoleResponse(member=False)
        return Team.MyRoleResponse(
            member=True, role=member.role, name=member.name
        )

    async def create(self, context: WriterContext) -> None:
        pass

    async def my_role(self, context: ReaderContext) -> Team.MyRoleResponse:
        assert context.auth is not None and context.auth.user_id is not None
        return self._answer(context.auth.user_id)

    async def member_of(
        self,
        context: ReaderContext,
        request: Team.MemberOfRequest,
    ) -> Team.MemberOfResponse:
        answer = self._answer(request.user_id)
        return Team.MemberOfResponse(
            member=answer.member, role=answer.role, name=answer.name
        )

    async def members(self, context: ReaderContext) -> Team.MembersResponse:
        return Team.MembersResponse(
            members=list(self.state.members),
            invitations=list(self.state.invitations),
        )

    async def register(
        self,
        context: WriterContext,
        request: Team.RegisterRequest,
    ) -> None:
        email = request.email.strip().lower()
        verified = request.email_verified
        name = request.name or email.split("@", 1)[0].capitalize()

        existing = _find(self.state, request.user_id)
        if existing is not None:
            existing.name = name
            if verified:
                existing.email = email
            return

        if not _allowed(email, verified):
            return

        invited = None
        if email and verified:
            invited = next(
                (i for i in self.state.invitations if i.email == email), None
            )

        if invited is not None:
            role = invited.role
            self.state.invitations = [
                i for i in self.state.invitations if i.email != email
            ]
        elif verified and email in admin_emails():
            role = "manager"
        elif not allowlist_configured() and not any(
            m.role == "manager" for m in self.state.members
        ):
            # Development and tests only: with no allowlist, the first
            # to arrive runs the roster. `main.py` refuses to start a
            # real provider without an allowlist.
            role = "manager"
        else:
            role = ""

        self.state.members.append(
            Member(
                user_id=request.user_id,
                email=email if verified else "",
                name=name,
                role=role,  # type: ignore[arg-type]
            )
        )

    async def invite(
        self,
        context: WriterContext,
        request: Team.InviteRequest,
    ) -> None:
        email = request.email.strip().lower()
        if not email:
            return
        self.state.invitations = [
            i for i in self.state.invitations if i.email != email
        ]
        member = next(
            (m for m in self.state.members if m.email == email), None
        )
        if member is not None:
            # Already on staff: their role changes through `set_role`,
            # which keeps the last-manager rule.
            return
        self.state.invitations.append(
            Invitation(email=email, role=request.role)
        )

    async def set_role(
        self,
        context: WriterContext,
        request: Team.SetRoleRequest,
    ) -> None:
        member = _find(self.state, request.user_id)
        if member is None:
            raise Team.SetRoleAborted(NotAMemberError(user_id=request.user_id))
        managers = [m for m in self.state.members if m.role == "manager"]
        if (
            member.role == "manager"
            and request.role != "manager"
            and len(managers) == 1
        ):
            raise Team.SetRoleAborted(LastManagerError())
        member.role = request.role
