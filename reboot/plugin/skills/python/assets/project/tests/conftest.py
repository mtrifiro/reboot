# tests/conftest.py
import os

# Effect validation stays on. QUIET logs each method's "Re-running
# method ... to validate effects" once, not on every call, so a
# failure's captured log is short enough to read whole.
os.environ.setdefault("RBT_EFFECT_VALIDATION", "QUIET")

# The last run's results, in tests/.last-run.json (tests/last_run.py).
from last_run import (  # noqa: F401
    pytest_runtest_logreport,
    pytest_sessionstart,
    pytest_terminal_summary,
    pytest_unconfigure,
)
