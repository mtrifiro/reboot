# tests/conftest.py
# The last run's results, in tests/.last-run.json (tests/last_run.py).
from last_run import (  # noqa: F401
    pytest_runtest_logreport,
    pytest_sessionstart,
    pytest_terminal_summary,
    pytest_unconfigure,
)
