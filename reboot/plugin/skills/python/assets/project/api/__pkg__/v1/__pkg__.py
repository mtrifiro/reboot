"""__APP_NAME__'s API: what it keeps track of and what can be done to it.

The starter's shape: a `User` (one per person who signs in), one
`__Hub__` (the app's one hub, with the fixed id "__hub__") that holds
the `__Thing__`s, and a `__Thing__` per thing it keeps track of. Each
`__Thing__` is its own object because it changes on its own; the hub
adds one in a transaction, so the hub and the new `__Thing__` change
together or not at all. Replace `name` and `note` with the design's
fields, and add its methods beside these, in the same shape.
"""

from reboot.api import (
    API,
    Exclusive,
    Field,
    Methods,
    Model,
    Reader,
    Transaction,
    Type,
    Writer,
)

# ---------------------------------------------------------------------------
# __Thing__


class __Thing__State(Model):
    name: str = Field(
        tag=1,
        default="",
        description="What the __thing text__ is called; never empty.",
    )
    note: str = Field(
        tag=2,
        default="",
        description="A line about the __thing text__; may be empty.",
    )


class __Thing__View(Model):
    __thing___id: str = Field(
        tag=1, default="", description="The __thing text__'s state id."
    )
    name: str = Field(tag=2, default="", description="What it is called.")
    note: str = Field(tag=3, default="", description="A line about it.")


class __Thing__Details(Model):
    name: str = Field(
        tag=1, default="", description="What it is called; required."
    )
    note: str = Field(tag=2, default="", description="A line about it.")


class Get__Thing__Response(Model):
    __thing__: __Thing__View = Field(
        tag=1, description="The __thing text__ as it stands now."
    )


class Invalid__Thing__(Model):
    problem: str = Field(
        tag=1,
        default="",
        description="What is wrong with the details, in plain words.",
    )


__Thing__Methods = Methods(
    create=Writer(
        request=__Thing__Details,
        response=None,
        factory=True,
        errors=[Invalid__Thing__],
        description="Bring a __thing text__ into existence with its "
        "details. Internal: only the __hub text__'s `add___thing__` "
        "calls it, so every __thing text__ is on the __hub text__'s list.",
        mcp=None,
    ),
    get=Reader(
        request=None,
        response=Get__Thing__Response,
        description="The __thing text__'s details.",
        mcp=None,
    ),
    edit=Writer(
        request=__Thing__Details,
        response=None,
        errors=[Invalid__Thing__],
        description="Correct the __thing text__'s details. Refused with "
        "`Invalid__Thing__` when the name is empty.",
        mcp=None,
    ),
)

# ---------------------------------------------------------------------------
# __Hub__


class __Hub__State(Model):
    __thing___ids: list[str] = Field(
        tag=1,
        default_factory=list,
        description="Every __thing text__, in the order added. Bounded by "
        "the domain; a list that grows without limit is an `OrderedMap` "
        "or its own objects (`state-collections.md`).",
    )


class Add__Thing__Response(Model):
    __thing___id: str = Field(
        tag=1, default="", description="The id of the __thing text__ just added."
    )


class __Things__Response(Model):
    __things__: list[__Thing__View] = Field(
        tag=1,
        default_factory=list,
        description="Every __thing text__, in the order added.",
    )


__Hub__Methods = Methods(
    open=Writer(
        request=None,
        response=None,
        description="Bring the __hub text__ into existence, empty; does "
        "nothing to an existing one. Internal: the application calls it "
        "at start, so the list reads empty, not missing.",
        mcp=None,
    ),
    add___thing__=Transaction(
        mode=Exclusive(),
        request=__Thing__Details,
        response=Add__Thing__Response,
        errors=[Invalid__Thing__],
        description="Add a __thing text__ and put it on the list, both or "
        "neither. Refused with `Invalid__Thing__` when the name is empty.",
        mcp=None,
    ),
    __things__=Reader(
        request=None,
        response=__Things__Response,
        description="Every __thing text__ with its details, in the order "
        "added.",
        mcp=None,
    ),
)

# ---------------------------------------------------------------------------
# User


class UserState(Model):
    pass


api = API(
    User=Type(
        state=UserState,
        methods=Methods(),
        description="One signed-in person, constructed by Reboot at "
        "first sign-in; the front door uses it to know who is signed in.",
    ),
    __Hub__=Type(
        state=__Hub__State,
        methods=__Hub__Methods,
        description="The one __hub text__, with the state id \"__hub__\": "
        "the list of every __thing text__.",
    ),
    __Thing__=Type(
        state=__Thing__State,
        methods=__Thing__Methods,
        description="One __thing text__ and its details.",
    ),
)
