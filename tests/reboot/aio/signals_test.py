import asyncio
import signal
import subprocess
import sys
import unittest
from reboot.aio import signals
from reboot.aio.signals import (
    initialize,
    install_cleanup_handler,
    uninstall_cleanup_handler,
)


def _run_python(code: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, '-c', code],
        stdout=subprocess.PIPE,
        text=True,
        timeout=30,
    )


async def _initialize_sighup() -> None:
    initialize([signal.SIGHUP], reraise=False)


# Imitates an entry point like `rbt`'s: Reboot's signal handler runs the
# cleanup handlers without re-raising, ours cancels the main task, and
# the signal takes its default action once the main task has finished.
_ENTRY_POINT = '''
import asyncio, os, signal
from reboot.aio.signals import (
    TERMINATING_SIGNALS, initialize, install_cleanup_handler,
    raise_with_default_action, raised_signal,
)

async def cancellable(main):
    initialize(TERMINATING_SIGNALS, reraise=False)
    task = asyncio.current_task()

    def cancel():
        task.cancel()

    install_cleanup_handler(TERMINATING_SIGNALS, cancel)
    await main()

try:
    asyncio.run(cancellable(main))
finally:
    signum = raised_signal()
    if signum is not None:
        raise_with_default_action(signum)
print("unreachable", flush=True)
'''


class SignalsTest(unittest.TestCase):

    def test_initialize_without_loop_installs_for_process(self) -> None:
        # Twice, since installing it again must leave it as it is.
        for _ in range(2):
            initialize()
            self.assertIs(
                signal.getsignal(signal.SIGTERM),
                signals._reboot_signal_handler,
            )

    def test_initialize_without_loop_refuses_to_not_reraise(self) -> None:
        with self.assertRaises(ValueError):
            initialize([signal.SIGHUP], reraise=False)

    def test_initialize_without_loop_refuses_foreign_handler(self) -> None:
        previous = signal.signal(signal.SIGHUP, lambda signum, frame: None)
        try:
            with self.assertRaisesRegex(RuntimeError, "cleanup handler"):
                initialize([signal.SIGHUP])
        finally:
            signal.signal(signal.SIGHUP, previous)

    def test_initialize_refuses_to_change_reraise(self) -> None:

        def cleanup() -> None:
            pass

        async def initialize_without_reraise() -> None:
            initialize([signal.SIGTERM], reraise=False)

        # The first cleanup handler makes Reboot's signal handler
        # re-raise `SIGTERM` for the process.
        install_cleanup_handler([signal.SIGTERM], cleanup)
        try:
            with self.assertRaisesRegex(RuntimeError, "already re-raises"):
                asyncio.run(initialize_without_reraise())
        finally:
            uninstall_cleanup_handler([signal.SIGTERM], cleanup)

    def test_initialize_refuses_foreign_handler(self) -> None:
        previous = signal.signal(signal.SIGHUP, lambda signum, frame: None)
        try:
            with self.assertRaisesRegex(RuntimeError, "cleanup handler"):
                asyncio.run(_initialize_sighup())
        finally:
            signal.signal(signal.SIGHUP, previous)

    def test_initialize_refuses_handler_on_another_event_loop(self) -> None:
        loop = asyncio.new_event_loop()
        try:
            loop.add_signal_handler(signal.SIGHUP, lambda: None)
            with self.assertRaises(RuntimeError):
                asyncio.run(_initialize_sighup())
        finally:
            loop.close()

    def test_initialize_refuses_second_call_on_one_loop(self) -> None:

        async def initialize_twice() -> None:
            await _initialize_sighup()
            await _initialize_sighup()

        with self.assertRaises(RuntimeError):
            asyncio.run(initialize_twice())

    def _assert_loop_refuses_only_reboot_signals(
        self,
        refused: int,
    ) -> None:
        loop = asyncio.get_running_loop()
        with self.assertRaisesRegex(RuntimeError, "cleanup handler"):
            loop.add_signal_handler(refused, lambda: None)
        # Signals that Reboot does not handle stay the loop's business.
        loop.add_signal_handler(signal.SIGUSR1, lambda: None)
        loop.remove_signal_handler(signal.SIGUSR1)

    def test_loop_refuses_reboot_signals_after_initialize(self) -> None:

        async def add_signal_handlers() -> None:
            await _initialize_sighup()
            self._assert_loop_refuses_only_reboot_signals(signal.SIGHUP)

        asyncio.run(add_signal_handlers())

    def test_loop_refuses_reboot_signals_after_install_cleanup(self) -> None:

        def cleanup() -> None:
            pass

        async def add_signal_handlers() -> None:
            install_cleanup_handler([signal.SIGTERM], cleanup)
            try:
                self._assert_loop_refuses_only_reboot_signals(signal.SIGTERM)
            finally:
                uninstall_cleanup_handler([signal.SIGTERM], cleanup)

        asyncio.run(add_signal_handlers())

    def test_install_cleanup_refuses_signal_reboot_does_not_handle(
        self,
    ) -> None:
        with self.assertRaises(ValueError):
            install_cleanup_handler([signal.SIGUSR1], lambda: None)

    def test_without_reraise_main_task_finishes_first(self) -> None:
        process = _run_python(
            '''
import asyncio, os, signal
from reboot.aio.signals import install_cleanup_handler

async def main():
    install_cleanup_handler(
        [signal.SIGTERM], lambda: print("cleanup", flush=True)
    )
    try:
        os.kill(os.getpid(), signal.SIGTERM)
        await asyncio.sleep(60)
    finally:
        # Further signals while unwinding must not interrupt this.
        os.kill(os.getpid(), signal.SIGTERM)
        os.kill(os.getpid(), signal.SIGINT)
        await asyncio.sleep(0.1)
        print("unwound", flush=True)
''' + _ENTRY_POINT
        )
        # The cleanup handlers ran once, when the first signal arrived,
        # the main task unwound undisturbed by the further signals, and
        # only then the first signal ended the process.
        self.assertEqual(process.stdout, "cleanup\nunwound\n")
        self.assertEqual(process.returncode, -signal.SIGTERM)

    def test_cleanup_can_let_the_cancelled_main_task_finish(self) -> None:
        process = _run_python(
            '''
import asyncio, os, signal
from reboot.aio.signals import install_cleanup_handler

async def main():
    # Stands in for, e.g., stopping something that the main task's own
    # cleanup waits for.
    stopped = asyncio.Event()
    install_cleanup_handler([signal.SIGTERM], stopped.set)
    try:
        os.kill(os.getpid(), signal.SIGTERM)
        await asyncio.sleep(60)
    finally:
        await stopped.wait()
        print("unwound", flush=True)
''' + _ENTRY_POINT
        )
        self.assertEqual(process.stdout, "unwound\n")
        self.assertEqual(process.returncode, -signal.SIGTERM)

    def test_with_reraise_signal_ends_process_after_cleanup(self) -> None:
        process = _run_python(
            '''
import asyncio, os, signal
from reboot.aio.signals import (
    TERMINATING_SIGNALS, initialize, install_cleanup_handler,
)

async def main():
    initialize(TERMINATING_SIGNALS, reraise=True)
    install_cleanup_handler(
        [signal.SIGTERM], lambda: print("cleanup", flush=True)
    )
    try:
        os.kill(os.getpid(), signal.SIGTERM)
        await asyncio.sleep(60)
    finally:
        print("unwound", flush=True)

asyncio.run(main())
'''
        )
        self.assertEqual(process.stdout, "cleanup\n")
        self.assertEqual(process.returncode, -signal.SIGTERM)

    def test_second_signal_does_not_restart_cleanup(self) -> None:
        process = _run_python(
            '''
import os, signal, threading, time
from reboot.aio.signals import initialize, install_cleanup_handler

def slow_cleanup():
    print("cleanup started", flush=True)
    time.sleep(0.5)
    print("cleanup finished", flush=True)

initialize()
install_cleanup_handler([signal.SIGTERM], slow_cleanup)

def send_second_signal():
    time.sleep(0.2)
    os.kill(os.getpid(), signal.SIGTERM)

threading.Thread(target=send_second_signal).start()
os.kill(os.getpid(), signal.SIGTERM)
time.sleep(5)
'''
        )
        # Without a loop, Python can run the handler for the second
        # signal in the middle of the first one's cleanup.
        self.assertEqual(process.stdout, "cleanup started\ncleanup finished\n")
        self.assertEqual(process.returncode, -signal.SIGTERM)

    def test_signal_no_cleanup_handler_covers_is_reraised(self) -> None:
        process = _run_python(
            '''
import asyncio, os, signal
from reboot.aio.signals import initialize

async def main():
    initialize([signal.SIGHUP], reraise=False)
    try:
        os.kill(os.getpid(), signal.SIGHUP)
        await asyncio.sleep(60)
    finally:
        print("unwound", flush=True)

asyncio.run(main())
'''
        )
        # Not re-raising it would have left nothing to end the process.
        self.assertEqual(process.stdout, "")
        self.assertEqual(process.returncode, -signal.SIGHUP)


if __name__ == '__main__':
    unittest.main()
