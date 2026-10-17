from __pkg__.v1.__pkg__ import (
    Invalid__Thing__,
    __Thing__Details,
    __Thing__State,
    __Thing__View,
)
from __pkg__.v1.__pkg___rbt import __Thing__
from reboot.aio.auth.authorizers import (
    allow_if,
    has_verified_token,
    is_app_internal,
)
from reboot.aio.contexts import ReaderContext, WriterContext


def details_problem(details: __Thing__Details) -> str | None:
    """Why the details can't be accepted, or None when they can."""
    if details.name.strip() == "":
        return "a __thing text__ needs a name"
    return None


def view(__thing___id: str, state: __Thing__State) -> __Thing__View:
    return __Thing__View(
        __thing___id=__thing___id,
        name=state.name,
        note=state.note,
    )


class __Thing__Servicer(__Thing__.Servicer):

    def authorizer(self):
        return __Thing__.Authorizer(
            # Created only by the __hub text__'s `add___thing__`, so every
            # __thing text__ is on its list.
            create=allow_if(all=[is_app_internal]),
            # Anyone signed in, or the __hub text__ reading its list.
            _default=allow_if(any=[has_verified_token, is_app_internal]),
        )

    def _apply(self, details: __Thing__Details) -> None:
        # Callers check `details_problem` first.
        state: __Thing__State = self.state
        state.name = details.name.strip()
        state.note = details.note.strip()

    async def create(
        self,
        context: WriterContext,
        request: __Thing__.CreateRequest,
    ) -> None:
        details: __Thing__Details = request
        problem = details_problem(details)
        if problem is not None:
            raise __Thing__.CreateAborted(Invalid__Thing__(problem=problem))
        self._apply(details)

    async def get(self, context: ReaderContext) -> __Thing__.GetResponse:
        return __Thing__.GetResponse(
            __thing__=view(self.ref().state_id, self.state)
        )

    async def edit(
        self,
        context: WriterContext,
        request: __Thing__.EditRequest,
    ) -> None:
        details: __Thing__Details = request
        problem = details_problem(details)
        if problem is not None:
            raise __Thing__.EditAborted(Invalid__Thing__(problem=problem))
        self._apply(details)
