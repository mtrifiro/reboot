from staff.v1.staff_rbt import Team, User
from reboot.aio.contexts import ReaderContext, TransactionContext
from servicers.auth import TEAM_ID


class UserServicer(User.Servicer):
    # No `authorizer()`: the framework's default for `User` lets only the
    # user themselves (and the app) call it.

    async def set_claims(
        self,
        context: TransactionContext,
        request: User.SetClaimsRequest,
    ) -> None:
        # A full replace: each delivery is the whole truth.
        self.state.email = str(request.claims.get("email", "")).lower()
        self.state.email_verified = bool(
            request.claims.get("email_verified", False)
        )
        self.state.name = str(request.claims.get("name", ""))
        await Team.ref(TEAM_ID).register(
            context,
            user_id=self.ref().state_id,
            email=self.state.email,
            email_verified=self.state.email_verified,
            name=self.state.name,
        )

    async def profile(self, context: ReaderContext) -> User.ProfileResponse:
        return User.ProfileResponse(
            email=self.state.email, name=self.state.name
        )
