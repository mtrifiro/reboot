"""Tests for hooks/skill-gate.py: an edit under a Reboot project's own
folders is denied until a skill carrying that folder's rules has been
loaded in the session; everything else decides nothing.

The hook runs as a subprocess with a mocked PreToolUse payload. The
session's list of loaded skills is a file in the system temp dir, so
each test uses its own temp dir as TMPDIR and its own session id.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HOOK = os.environ.get("SKILL_GATE_PY") or str(
    Path(__file__).resolve().parents[4] / "reboot" / "plugin" / "hooks" / "skill-gate.py")


def run_hook(tool_name: str, tool_input: dict, *, session: str, tmp: str, cwd: str | None = None) -> str:
    payload: dict = {"tool_name": tool_name, "tool_input": tool_input, "session_id": session,
                     "permission_mode": "default"}
    if cwd is not None:
        payload["cwd"] = cwd
    env = {**os.environ, "TMPDIR": tmp, "TMP": tmp, "TEMP": tmp}
    result = subprocess.run([sys.executable, HOOK], input=json.dumps(payload),
                            capture_output=True, text=True, env=env)
    assert result.returncode == 0, result.stderr
    return result.stdout


def decision(stdout: str) -> str:
    if not stdout.strip():
        return "none"
    return json.loads(stdout)["hookSpecificOutput"]["permissionDecision"]


class SkillGateTest(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = self._tmp.name
        self.project = Path(self.tmp) / "hotel-1"
        for d in ("api/hotel/v1", "backend/src/servicers", "frontend/web/src", "frontend/mcp/desk", "tests", "docs"):
            (self.project / d).mkdir(parents=True)
        (self.project / ".rbtrc").write_text("--application-name=hotel-1\n")
        self.session = "s-" + Path(self.tmp).name

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def load(self, skill: str) -> None:
        out = run_hook("Skill", {"skill": f"reboot:{skill}"}, session=self.session, tmp=self.tmp)
        self.assertEqual(decision(out), "none")

    def edit(self, rel: str, tool: str = "Edit", cwd: str | None = None, path: str | None = None) -> str:
        p = path if path is not None else str(self.project / rel)
        return decision(run_hook(tool, {"file_path": p, "old_string": "a", "new_string": "b"},
                                 session=self.session, tmp=self.tmp, cwd=cwd))

    def test_api_edit_denied_until_a_skill_is_loaded(self) -> None:
        self.assertEqual(self.edit("api/hotel/v1/hotel.py"), "deny")
        self.load("python")
        self.assertEqual(self.edit("api/hotel/v1/hotel.py"), "none")

    def test_denial_names_the_skill(self) -> None:
        out = run_hook("Write", {"file_path": str(self.project / "api/hotel/v1/hotel.py"), "content": ""},
                       session=self.session, tmp=self.tmp)
        reason = json.loads(out)["hookSpecificOutput"]["permissionDecisionReason"]
        self.assertIn("reboot:python", reason)
        self.assertIn("api/hotel/v1/hotel.py", reason)
        self.assertIn("feature", reason)

    def test_web_app_skill_covers_the_api_and_the_page(self) -> None:
        self.load("web-app")
        self.assertEqual(self.edit("api/hotel/v1/hotel.py"), "none")
        self.assertEqual(self.edit("backend/src/servicers/hotel.py"), "none")
        self.assertEqual(self.edit("frontend/web/src/App.tsx"), "none")
        self.assertEqual(self.edit("tests/hotel.feature"), "none")
        self.assertEqual(self.edit("frontend/mcp/desk/index.html"), "deny")

    def test_the_page_needs_web_app_not_python(self) -> None:
        self.load("python")
        self.assertEqual(self.edit("frontend/web/src/App.tsx"), "deny")
        self.assertEqual(self.edit("frontend/web/src/components/Board.tsx", tool="Write"), "deny")
        self.load("web-app")
        self.assertEqual(self.edit("frontend/web/src/components/Board.tsx", tool="Write"), "none")

    def test_feature_file_needs_feature_or_a_build_skill(self) -> None:
        self.assertEqual(self.edit("tests/hotel.feature"), "deny")
        self.assertEqual(self.edit("tests/hotel_test.py"), "none")  # a test module is not gated
        self.load("feature")
        self.assertEqual(self.edit("tests/hotel.feature"), "none")
        self.assertEqual(self.edit("api/hotel/v1/hotel.py"), "none")

    def test_other_files_and_other_projects_are_not_gated(self) -> None:
        self.assertEqual(self.edit("docs/notes.md"), "none")
        self.assertEqual(self.edit("AGENTS.md"), "none")
        self.assertEqual(self.edit("frontend/package.json"), "none")
        outside = Path(self.tmp) / "elsewhere" / "api" / "x.py"
        outside.parent.mkdir(parents=True)
        self.assertEqual(self.edit("", path=str(outside)), "none")

    def test_relative_path_resolves_against_cwd(self) -> None:
        self.assertEqual(self.edit("", path="api/hotel/v1/hotel.py", cwd=str(self.project)), "deny")
        self.assertEqual(self.edit("", path="frontend/web/src/App.tsx", cwd=str(self.project / "backend")), "none")
        self.assertEqual(self.edit("", path="../frontend/web/src/App.tsx", cwd=str(self.project / "backend")), "deny")

    def test_sessions_do_not_share_skills(self) -> None:
        self.load("web-app")
        other = decision(run_hook("Edit", {"file_path": str(self.project / "frontend/web/src/App.tsx")},
                                  session="someone-else", tmp=self.tmp))
        self.assertEqual(other, "deny")

    def test_multiedit_and_notebook(self) -> None:
        self.assertEqual(self.edit("backend/src/main.py", tool="MultiEdit"), "deny")
        out = run_hook("NotebookEdit", {"notebook_path": str(self.project / "api/hotel/v1/n.ipynb")},
                       session=self.session, tmp=self.tmp)
        self.assertEqual(decision(out), "deny")

    def test_bad_input_decides_nothing(self) -> None:
        env = {**os.environ, "TMPDIR": self.tmp}
        result = subprocess.run([sys.executable, HOOK], input="not json", capture_output=True, text=True, env=env)
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout.strip(), "")


if __name__ == "__main__":
    unittest.main()
