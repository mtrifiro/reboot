from uuid import uuid4

from __pkg__.v1.__pkg__ import __Hub__State, __Thing__Details, Invalid__Thing__
from __pkg__.v1.__pkg___rbt import __Hub__, __Thing__
from reboot.aio.auth.authorizers import (
    allow_if,
    has_verified_token,
    is_app_internal,
)
from reboot.aio.contexts import (
    ReaderContext,
    TransactionContext,
    WriterContext,
)
from servicers.__thing__ import details_problem

# The one __hub text__: its id is fixed, so every caller finds it.
HUB_ID = "__hub__"


class __Hub__Servicer(__Hub__.Servicer):

    def authorizer(self):
        return __Hub__.Authorizer(
            # Opened by the application at start, never by a user.
            open=allow_if(all=[is_app_internal]),
            # Anyone signed in can do everything; roles come with
            # "Who may do what". Never `any=[has_verified_token,
            # is_app_internal]` here: `is_app_internal` denies, so a
            # caller not signed in gets `PermissionDenied`, not the
            # `Unauthenticated` its scenario expects (9 of 14 builds,
            # hotel-300 to 338). Another servicer that calls this one
            # gets its own method rule with `is_app_internal`.
            _default=allow_if(all=[has_verified_token]),
        )

    async def open(self, context: WriterContext) -> None:
        pass

    async def add___thing__(
        self,
        context: TransactionContext,
        request: __Hub__.Add__Thing__Request,
    ) -> __Hub__.Add__Thing__Response:
        state: __Hub__State = self.state
        details: __Thing__Details = request
        problem = details_problem(details)
        if problem is not None:
            raise __Hub__.Add__Thing__Aborted(
                Invalid__Thing__(problem=problem)
            )
        # One transaction: the __thing text__ exists and is on the list,
        # or neither.
        __thing__, _ = await __Thing__.create(
            context,
            str(uuid4()),
            name=details.name,
            note=details.note,
        )
        state.__thing___ids.append(__thing__.state_id)
        return __Hub__.Add__Thing__Response(__thing___id=__thing__.state_id)

    async def __things__(
        self, context: ReaderContext
    ) -> __Hub__.__Things__Response:
        state: __Hub__State = self.state
        # One read for the whole list: the page subscribes to this
        # reader once, not to each __thing text__.
        responses = await __Thing__.forall(state.__thing___ids).get(context)
        return __Hub__.__Things__Response(
            __things__=[r.__thing__ for r in responses]
        )
