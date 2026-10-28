"""Tests for hooks/say-design-first.py: the first Write that creates a
project's design/decisions.md is refused once per session, so the
design summary is sent in the chat first; every other call decides
nothing.

The hook runs as a subprocess with a mocked PreToolUse payload. Its
once-a-session marker is a file in the system temp dir, so each test
uses its own temp dir as TMPDIR and its own session id.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HOOK = os.environ.get("SAY_DESIGN_FIRST_PY") or str(
    Path(__file__).resolve().parents[4] / "reboot" / "plugin" / "hooks" / "say-design-first.py")


class SayDesignFirstTest(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = self._tmp.name
        self.project = Path(self.tmp) / "hotel-1"
        (self.project / "design").mkdir(parents=True)
        self.session = "s-" + Path(self.tmp).name

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def run_hook(self, tool: str, file_path: str, session: str | None = None) -> str:
        payload = {"tool_name": tool, "tool_input": {"file_path": file_path, "content": "x"},
                   "session_id": session or self.session, "cwd": str(self.project)}
        env = {**os.environ, "TMPDIR": self.tmp, "TMP": self.tmp, "TEMP": self.tmp}
        result = subprocess.run([sys.executable, HOOK], input=json.dumps(payload),
                                capture_output=True, text=True, env=env)
        self.assertEqual(result.returncode, 0, result.stderr)
        return result.stdout

    def decision(self, stdout: str) -> str:
        if not stdout.strip():
            return "none"
        return json.loads(stdout)["hookSpecificOutput"]["permissionDecision"]

    def test_first_write_is_refused_once(self) -> None:
        path = str(self.project / "design" / "decisions.md")
        out = self.run_hook("Write", path)
        self.assertEqual(self.decision(out), "deny")
        self.assertIn("message text", json.loads(out)["hookSpecificOutput"]["permissionDecisionReason"])
        self.assertEqual(self.decision(self.run_hook("Write", path)), "none")

    def test_relative_path_resolves_against_cwd(self) -> None:
        self.assertEqual(self.decision(self.run_hook("Write", "design/decisions.md")), "deny")

    def test_existing_log_is_not_refused(self) -> None:
        (self.project / "design" / "decisions.md").write_text("# log\n")
        self.assertEqual(self.decision(self.run_hook("Write", str(self.project / "design" / "decisions.md"))), "none")

    def test_other_files_and_tools_decide_nothing(self) -> None:
        self.assertEqual(self.decision(self.run_hook("Write", str(self.project / "design" / "interview.md"))), "none")
        self.assertEqual(self.decision(self.run_hook("Write", str(self.project / "decisions.md"))), "none")
        self.assertEqual(self.decision(self.run_hook("Edit", str(self.project / "design" / "decisions.md"))), "none")

    def test_another_session_is_refused_again(self) -> None:
        path = str(self.project / "design" / "decisions.md")
        self.assertEqual(self.decision(self.run_hook("Write", path)), "deny")
        self.assertEqual(self.decision(self.run_hook("Write", path, session=self.session + "-2")), "deny")

    def test_bad_input_decides_nothing(self) -> None:
        env = {**os.environ, "TMPDIR": self.tmp}
        result = subprocess.run([sys.executable, HOOK], input="not json", capture_output=True, text=True, env=env)
        self.assertEqual((result.returncode, result.stdout), (0, ""))


if __name__ == "__main__":
    unittest.main()
