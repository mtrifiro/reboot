# This is a separate function (rather than just being in `__main__`) so that we
# can refer to it as a `script` in our `pyproject.rbt.toml` file.
def main():
    try:
        # We are doing lazy imports because we want to quit
        # quietly in case of `KeyboardInterrupt` and not print the stack trace,
        # otherwise users can bump into the stack trace when they do `Ctrl+C`
        # during the import of the `reboot` packages.
        # If it becomes a problem later, we could tweak the `SCRIPT_TEMPLATE` at
        # https://github.com/pypa/pip/blob/762faa776d47ed0415424623bc63aade57facd9b/src/pip/_vendor/distlib/scripts.py#L43
        import asyncio
        import os
        import platform
        import reboot.aio.tracing
        import sys
        from reboot.aio.signals import (
            TERMINATING_SIGNALS,
            initialize,
            install_cleanup_handler,
            raise_with_default_action,
            raised_signal,
        )
        from reboot.cli.common.cli import cli

        # We ignore _known_ warnings from
        # `multiprocessing.resource_tracker` that we know are harmless so
        # that we don't spam stdout. See #2793.
        #
        # We do this via an environment variable instead of using
        # `warnings.filterwarnings()` because we fork/exec multiple
        # processes and need to make sure all of those processes ignore
        # these warnings.
        warnings = os.environ.get('PYTHONWARNINGS')
        if warnings is not None:
            warnings += ','
        else:
            warnings = ''

        warnings += (
            'ignore:resource_tracker:UserWarning:multiprocessing.resource_tracker'
        )

        os.environ['PYTHONWARNINGS'] = warnings

        if sys.platform == "darwin" and platform.machine() == "x86_64":
            print(
                "Reboot no longer supports MacOS x86_64. "
                "Please reach out and let us know your use case if this "
                "is important for you!"
            )
            sys.exit(1)

        async def cancellable_cli() -> int:
            # Reboot's signal handler runs the cleanup handlers of the
            # first signal that would kill us without re-raising it, and
            # ours cancels `cli()`, so that its cleanup context managers
            # terminate the subprocesses it started.
            initialize(TERMINATING_SIGNALS, reraise=False)

            # Only now, since tracing installs a cleanup handler, which
            # would otherwise fix Reboot's signal handler to re-raise.
            reboot.aio.tracing.start("reboot cli")

            task = asyncio.current_task()
            assert task is not None

            def cancel_cli() -> None:
                task.cancel()

            install_cleanup_handler(TERMINATING_SIGNALS, cancel_cli)
            return await cli()

        try:
            returncode = asyncio.run(cancellable_cli())
        finally:
            # Only now that `cli()` has finished, however it finished,
            # does the signal that cancelled it take its default action.
            # A cancellation without a signal behind it is a bug, which
            # propagates as a traceback.
            signum = raised_signal()
            if signum is not None:
                raise_with_default_action(signum)
        sys.exit(returncode)
    except KeyboardInterrupt:
        # A Ctrl-C before `initialize()` took over SIGINT, i.e., during
        # the imports above: exit without a stack trace.
        import sys
        sys.exit(2)


if __name__ == '__main__':
    main()
