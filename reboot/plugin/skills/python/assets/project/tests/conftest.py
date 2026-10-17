# tests/conftest.py
# The last run's results, in tests/.last-run.json (tests/last_run.py).
import sys

from last_run import (  # noqa: F401
    pytest_runtest_logreport,
    pytest_sessionstart,
    pytest_terminal_summary,
    pytest_unconfigure,
)

# On macOS the harness, bound to every address, can be handed a port an
# IPv4 listener already holds; calls then fail with "Method not found"
# or hang (the plugin's KNOWN-ISSUES.md, "Harness tests on macOS").
if sys.platform == "darwin":
    from reboot.controller import server_managers

    server_managers.EVERY_LOCAL_NETWORK_ADDRESS = "127.0.0.1"
