import asyncio
import os
import signal
from collections import defaultdict
from contextlib import contextmanager
from reboot.settings import ENVVAR_SIGNALS_AVAILABLE
from typing import Any, Callable, NoReturn, Optional

# The one place where a Reboot process handles signals, assuming one
# event loop at a time. Reboot installs its own signal handler, and
# only that one, with `initialize()`; code reacts to a signal by
# installing a cleanup handler for it with `install_cleanup_handler()`
# (or `cleanup_handler_installed()`), which Reboot's signal handler
# runs when the signal is raised. A process that installs a cleanup
# handler without having called `initialize()` gets Reboot's signal
# handler for the process with the defaults.
#
# By default Reboot's signal handler then re-raises the signal with its
# default action, which ends the process, so a cleanup handler must
# tolerate the process exiting right after it runs. A process entry
# point that must clean up before it exits instead calls `initialize()`
# with `reraise=False` from its event loop, installs a cleanup handler
# that makes its main coroutine finish, and re-raises the signal itself
# with `raise_with_default_action()` once that coroutine has finished.
#
# Invariants, each enforced below rather than assumed:
#
# - A signal has at most one handler, Reboot's: installing Reboot's
#   fails on finding any other, and an event loop on which Reboot's
#   signal handler or a cleanup handler is installed refuses
#   `add_signal_handler()` for Reboot's signals from then on, each time
#   with an error that points to cleanup handlers rather than letting
#   Reboot's be silently replaced.
# - Whether Reboot's signal handler re-raises a signal is fixed the
#   first time it handles that signal, so later code cannot change how
#   every cleanup handler's signal ends.
# - Reboot's signal handler acts on the first signal only, so a cleanup
#   underway cannot be interrupted, and re-raises a signal that no
#   cleanup handler covers, since nothing else would end the process.
# - `SIGKILL` runs none of this, so anything that must survive it needs
#   another mechanism, such as the Envoy nanny's pipe.

# Collection of cleanup handlers that have been installed.
#
# Do not use directly, instead call 'install_cleanup_handler()'.
_cleanup_handlers: defaultdict[
    int,
    list[Callable[[], None]],
] = defaultdict(lambda: [])

# The first signal handled, if any, since the last `initialize()`.
#
# Do not use directly, instead call 'raised_signal()'.
_raised_signal: Optional[int] = None

# Whether or not signals are available, e.g., because Python might be
# embedded within a Node process.
_signals_available: bool = os.environ.get(
    ENVVAR_SIGNALS_AVAILABLE,
    'true',
).lower() == 'true'

# The signals whose default action ends the process: Ctrl-C (`SIGINT`),
# Ctrl-\ (`SIGQUIT`), the parent terminal going away (`SIGHUP`), a
# reader like `head` closing the output pipe early (`SIGPIPE`), and
# tools that run a process in the background (IDEs, agents, process
# managers, Kubernetes) stopping it (`SIGTERM`).
TERMINATING_SIGNALS: list[int] = [
    signal.SIGINT,
    signal.SIGQUIT,
    signal.SIGHUP,
    signal.SIGPIPE,
    signal.SIGTERM,
]

# The signals that Reboot's signal handler handles unless told
# otherwise: those `initialize()` installs it for when given none, and
# those the first `install_cleanup_handler()` installs it for when
# nothing has yet.
#
# NOTE: SIGINT is left to Python, which raises `KeyboardInterrupt`,
# unless `initialize()` is given it.
DEFAULT_SIGNALS: list[int] = [signal.SIGTERM, signal.SIGQUIT]

# The signals that Reboot's signal handler currently handles, each with
# whether it re-raises it; cleanup handlers can only be installed for
# these.
#
# Do not use directly, instead call 'initialize()'.
_handled_signals: dict[int, bool] = {}


def raised_signal() -> Optional[int]:
    """Returns the first signal handled since the last `initialize()`, or
    None if no signal has been handled."""
    global _raised_signal
    return _raised_signal


def raise_with_default_action(signum: int) -> NoReturn:
    """Raises `signum` again with its default action, which for the
    signals Reboot handles ends the process."""
    signal.signal(signum, signal.SIG_DFL)
    os.kill(os.getpid(), signum)
    raise AssertionError(f"Signal {signum} did not end the process")


def _reboot_signal_handler(
    signum: int, frame: Any, reraise: bool = True
) -> None:
    """Reboot's signal handler: for the first signal only, runs the
    cleanup handlers installed for `signum` and then, if `reraise`,
    raises it again with its default action. A signal that is not
    re-raised is re-raised anyway if no cleanup handler covers it, since
    nothing else would end the process."""
    global _cleanup_handlers
    global _raised_signal

    # A further signal while the first one is being handled, e.g., a
    # second Ctrl-C, would interrupt the cleanup underway and start it
    # over.
    if _raised_signal is not None:
        return
    _raised_signal = signum

    handlers = list(_cleanup_handlers[signum])
    for handler in handlers:
        handler()

    if reraise or len(handlers) == 0:
        raise_with_default_action(signum)


def _foreign_signal_handler_error(signum: int) -> RuntimeError:
    return RuntimeError(
        f"Reboot handles {signal.Signals(signum).name} itself and does not "
        "expect your own signal handler for it; install a cleanup handler "
        "with `install_cleanup_handler()` or `cleanup_handler_installed()` "
        "from `reboot.aio.signals` instead, which Reboot's signal handler "
        "runs when the signal is raised"
    )


def _forbid_foreign_signal_handlers_on_loop(
    loop: asyncio.AbstractEventLoop
) -> None:
    """Makes `loop.add_signal_handler()` raise for every signal that
    Reboot's signal handler handles, now or later, with an error that
    points to cleanup handlers, and pass any other signal on to the loop.
    Idempotent."""
    if 'add_signal_handler' in vars(loop):
        return

    add_signal_handler = loop.add_signal_handler

    def add_signal_handler_for_other_signals(
        signum: int,
        callback: Callable[..., object],
        *args: Any,
    ) -> None:
        if signum in _handled_signals:
            raise _foreign_signal_handler_error(signum)
        add_signal_handler(signum, callback, *args)

    setattr(loop, 'add_signal_handler', add_signal_handler_for_other_signals)


def _running_loop() -> Optional[asyncio.AbstractEventLoop]:
    try:
        return asyncio.get_running_loop()
    except RuntimeError:
        return None


def initialize(
    signums: Optional[list[int]] = None,
    *,
    reraise: bool = True,
) -> None:
    """Installs Reboot's signal handler for `signums`, `DEFAULT_SIGNALS`
    if not given, so that it runs a signal's cleanup handlers and then,
    only if `reraise`, re-raises it with its default action. It goes on
    the running event loop if there is one, for the rest of that loop's
    life, and the loop refuses `add_signal_handler()` for Reboot's
    signals afterwards; otherwise it goes on the process, where it
    always re-raises, so `reraise` must hold. Must be called from the
    main thread.

    On a loop, assumes the process ends when that loop does: nothing
    reinstates Reboot's signal handler for the process after the loop
    closes, and a signal that was not re-raised leaves any later one
    ignored until the process re-raises it.

    Fails on a signal with a handler other than Reboot's: react to a
    signal with `install_cleanup_handler()` or
    `cleanup_handler_installed()` instead. Also fails on a signal that
    Reboot's signal handler already handles with the other `reraise`,
    including the default it gets from the first
    `install_cleanup_handler()`, so call this before anything installs a
    cleanup handler."""
    if not _signals_available:
        return

    loop = _running_loop()
    if loop is None and not reraise:
        raise ValueError(
            "`reraise=False` is only supported on a running event loop; for "
            "the process, Reboot's signal handler always re-raises"
        )

    _install_signal_handler(
        signums or DEFAULT_SIGNALS,
        loop=loop,
        reraise=reraise,
    )


def _install_signal_handler(
    signums: list[int],
    *,
    loop: Optional[asyncio.AbstractEventLoop],
    reraise: bool,
) -> None:
    global _handled_signals
    global _raised_signal

    for signum in signums:
        # A handler installed on an event loop is installed with
        # `signal.signal()` too, so this finds one installed either way.
        # Python itself starts with `default_int_handler` on SIGINT.
        if signal.getsignal(signum) not in (
            signal.SIG_DFL,
            signal.SIG_IGN,
            None,
            signal.default_int_handler,
            _reboot_signal_handler,
        ):
            raise _foreign_signal_handler_error(signum)

        # Every cleanup handler for the signal relies on how it ends, so
        # that is fixed once Reboot's signal handler handles it.
        handled_reraise = _handled_signals.get(signum, reraise)
        if handled_reraise != reraise:
            raise RuntimeError(
                "Reboot's signal handler already "
                f"{'re-raises' if handled_reraise else 'does not re-raise'} "
                f"{signal.Signals(signum).name}, and that cannot change; "
                "call `initialize()` before anything installs a cleanup "
                "handler for it"
            )

    if loop is None:
        for signum in signums:
            signal.signal(signum, _reboot_signal_handler)
            _handled_signals[signum] = reraise
        return

    _raised_signal = None
    for signum in signums:
        # Through the class, since an earlier
        # `install_cleanup_handler()` may have made this loop refuse
        # Reboot's signals already.
        type(loop).add_signal_handler(
            loop, signum, _reboot_signal_handler, signum, None, reraise
        )
        _handled_signals[signum] = reraise
    _forbid_foreign_signal_handlers_on_loop(loop)


def install_cleanup_handler(signums: list[int], handler: Callable[[], None]):
    """Installs a cleanup handler, a callable that Reboot's signal handler
    runs when one of `signums` is raised. Installs Reboot's signal handler
    for the process with the defaults first if it handles none of the
    `DEFAULT_SIGNALS` yet. From then on the running event loop, if
    any, refuses `add_signal_handler()` for Reboot's signals."""
    global _signals_available
    global _cleanup_handlers
    global _handled_signals

    if not _signals_available:
        return

    # A process that never calls `initialize()` still needs Reboot's
    # signal handler, or its cleanup handlers would never run. Install
    # it for the process rather than on the running loop, so that it
    # outlives every loop the process runs, and only for the signals it
    # does not handle yet, so that an earlier `initialize()` stays as it
    # is.
    unhandled = [
        signum for signum in DEFAULT_SIGNALS if signum not in _handled_signals
    ]
    if len(unhandled) > 0:
        _install_signal_handler(unhandled, loop=None, reraise=True)

    loop = _running_loop()
    if loop is not None:
        _forbid_foreign_signal_handlers_on_loop(loop)

    for signum in signums:
        if signum not in _handled_signals:
            raise ValueError(f'Signal {signum} is not handled by Reboot')
        elif handler in _cleanup_handlers[signum]:
            raise ValueError('Cleanup handler already installed')
        _cleanup_handlers[signum].append(handler)


def uninstall_cleanup_handler(signums: list[int], handler: Callable[[], None]):
    """Uninstalls a cleanup handler that should already have been
    installed via 'install_cleanup_handler()'."""
    global _signals_available
    global _cleanup_handlers

    if not _signals_available:
        return

    for signum in signums:
        if handler not in _cleanup_handlers[signum]:
            raise ValueError('Cleanup handler not installed')
        _cleanup_handlers[signum].remove(handler)


@contextmanager
def cleanup_handler_installed(
    signums: list[int], *, handler: Callable[[], None]
):
    """Helper context manager that installs and uninstalls a cleanup
    handler on the callers behalf."""
    install_cleanup_handler(signums, handler)
    try:
        yield
    finally:
        uninstall_cleanup_handler(signums, handler)
