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


StaffRole = Literal["", "manager", "front_desk", "housekeeping"]


class Member(Model):
    user_id: str = Field(
        tag=1, default="", description="The member's signed-in user id."
    )
    email: str = Field(
        tag=2,
        default="",
        description="The member's verified work address, lower-cased.",
    )
    name: str = Field(
        tag=3, default="", description="The member's display name."
    )
    role: StaffRole = Field(
        tag=4,
        default="",
        description="What the member may do: manager, front_desk or "
        "housekeeping; empty until a manager assigns one, which lets them "
        "look but change nothing.",
    )


class Invitation(Model):
    email: str = Field(
        tag=1,
        default="",
        description="The address invited, lower-cased; taken up only by a "
        "sign-in whose provider verified it.",
    )
    role: StaffRole = Field(
        tag=2,
        default="",
        description="The role the invitee takes on arrival.",
    )


class TeamState(Model):
    members: list[Member] = Field(
        tag=1,
        default_factory=list,
        description="Everyone on staff who has signed in, with their "
        "role. Bounded by the size of the staff.",
    )
    invitations: list[Invitation] = Field(
        tag=2,
        default_factory=list,
        description="Addresses invited by a manager who have not signed "
        "in yet.",
    )


class MemberOfRequest(Model):
    user_id: str = Field(
        tag=1, default="", description="The user id to look up."
    )


class MemberOfResponse(Model):
    member: bool = Field(
        tag=1,
        default=False,
        description="Whether the user is on the staff roster.",
    )
    role: StaffRole = Field(
        tag=2, default="", description="The member's role, if any."
    )
    name: str = Field(
        tag=3, default="", description="The member's display name."
    )


class MembersResponse(Model):
    members: list[Member] = Field(
        tag=1, default_factory=list, description="Everyone on staff."
    )
    invitations: list[Invitation] = Field(
        tag=2,
        default_factory=list,
        description="Invitations not yet taken up.",
    )


class RegisterRequest(Model):
    user_id: str = Field(
        tag=1, default="", description="The user signing in."
    )
    email: str = Field(
        tag=2, default="", description="The address their provider gave."
    )
    email_verified: bool = Field(
        tag=3,
        default=False,
        description="Whether the provider verified that address.",
    )
    name: str = Field(
        tag=4, default="", description="Their display name."
    )


class InviteRequest(Model):
    email: str = Field(
        tag=1, default="", description="The work address to invite."
    )
    role: StaffRole = Field(
        tag=2, default="", description="The role they take on arrival."
    )


class SetRoleRequest(Model):
    user_id: str = Field(
        tag=1, default="", description="The member whose role changes."
    )
    role: StaffRole = Field(
        tag=2,
        default="",
        description="Their new role; empty takes every permission away.",
    )


class LastManagerError(Model):
    pass


class NotAMemberError(Model):
    user_id: str = Field(
        tag=1, default="", description="The user id that isn't on staff."
    )


TeamMethods = Methods(
    create=Writer(
        request=None,
        response=None,
        factory=True,
        description="Bring the empty staff roster into existence. Called "
        "once by the app at first start.",
        mcp=None,
    ),
    my_role=Reader(
        request=None,
        response=MemberOfResponse,
        description="Whether the caller is on staff, and their role, so "
        "the app shows only the actions they may take.",
        mcp=None,
    ),
    member_of=Reader(
        request=MemberOfRequest,
        response=MemberOfResponse,
        description="Whether a given user is on staff, and their role. "
        "Called only by the app's own permission checks.",
        mcp=None,
    ),
    members=Reader(
        request=None,
        response=MembersResponse,
        description="The whole roster and the open invitations. Any "
        "member of staff may read it.",
        mcp=None,
    ),
    register=Writer(
        request=RegisterRequest,
        response=None,
        description="Record a sign-in: take up an invitation for a "
        "verified address, or add the person with no role. Called only by "
        "the app on each sign-in.",
        mcp=None,
    ),
    invite=Writer(
        request=InviteRequest,
        response=None,
        description="Invite a work address with a role, which a verified "
        "sign-in from that address takes up. Managers only.",
        mcp=None,
    ),
    set_role=Writer(
        request=SetRoleRequest,
        response=None,
        errors=[LastManagerError, NotAMemberError],
        description="Change a member's role. Raises `LastManagerError` if "
        "it would leave the hotel with no manager. Managers only.",
        mcp=None,
    ),
)

class UserState(Model):
    email: str = Field(
        tag=1,
        default="",
        description="The address the sign-in provider gave for this user.",
    )
    email_verified: bool = Field(
        tag=2,
        default=False,
        description="Whether the provider verified that address.",
    )
    name: str = Field(
        tag=3, default="", description="The user's display name."
    )


class ProfileResponse(Model):
    email: str = Field(tag=1, default="", description="The user's address.")
    name: str = Field(tag=2, default="", description="The user's name.")


UserMethods = Methods(
    profile=Reader(
        request=None,
        response=ProfileResponse,
        description="The signed-in user's own name and address.",
        mcp=None,
    ),
)


api = API(
    Team=Type(
        state=TeamState,
        methods=TeamMethods,
        description="The staff roster (id \"team\"): the only place a "
        "role is kept, so nobody can promote themselves.",
    ),
    User=Type(
        state=UserState,
        methods=UserMethods,
        description="One signed-in member of staff, created by Reboot at "
        "first sign-in; holds what the sign-in provider said about them.",
    ),
)
