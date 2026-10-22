"""Tests for what builds read of the reading path (`read_marks.py`).

`testdata/` holds two small projects' transcripts, written for these
tests, in Claude Code's folder layout:

* `hotel/web_app_build.jsonl`, with a sub-agent beside it in
  `hotel/web_app_build/subagents/agent-a1.jsonl`: a web app build that
  loads the `app` and `web-app` skills, reads two references whole and
  one in part, greps a conditional one, `cat`s another conditional one
  and `ls`es a third, then writes its API file; a line that is not a
  record; the sub-agent reads one more reference whole;
* `other_package/other.jsonl`: a build that loads a `build` skill this
  checkout doesn't have, then `web-app`.
"""

import os
import unittest
from pathlib import Path
from tests.reboot.plugin.read_marks import read_marks

TESTDATA = Path(
    os.environ.get(
        "READ_MARKS_TESTDATA", "tests/reboot/plugin/read_marks/testdata"
    )
)
SKILLS = Path(os.environ.get("REBOOT_PLUGIN_SKILLS", "reboot/plugin/skills"))

P = "/Users/dev/.claude/plugins/cache/reboot/reboot/plugin/skills"


class ToolCalls(unittest.TestCase):

    def marks(self, name: str, args: dict) -> list[tuple[str, str]]:
        return list(read_marks.call_marks(name, args))

    def test_the_skill_tool_reads_the_skill(self) -> None:
        self.assertEqual(
            self.marks("Skill", {"skill": "reboot:web-app"}),
            [("web-app/SKILL.md", "read")],
        )

    def test_read_with_a_range_is_part(self) -> None:
        path = f"{P}/python/references/api-methods.md"
        self.assertEqual(
            self.marks("Read", {"file_path": path}),
            [("python/references/api-methods.md", "read")],
        )
        self.assertEqual(
            self.marks("Read", {"file_path": path, "limit": 40}),
            [("python/references/api-methods.md", "part")],
        )

    def test_each_shell_segment_marks_its_own_files(self) -> None:
        command = (
            f"cat {P}/python/references/a-b.md && "
            f"head -20 {P}/python/references/c-d.md; "
            f"grep -n x {P}/web-app/SKILL.md"
        )
        self.assertEqual(
            self.marks("Bash", {"command": command}),
            [
                ("python/references/a-b.md", "read"),
                ("python/references/c-d.md", "part"),
                ("web-app/SKILL.md", "searched"),
            ],
        )

    def test_a_file_outside_the_skills_is_not_marked(self) -> None:
        self.assertEqual(
            self.marks("Read", {"file_path": "/tmp/hotel/README.md"}), []
        )


class ASession(unittest.TestCase):

    def setUp(self) -> None:
        self.session = read_marks.read_session(
            TESTDATA / "hotel" / "web_app_build.jsonl"
        )

    def test_skills_come_from_the_tool_and_the_body(self) -> None:
        self.assertEqual(self.session.skills, {"app", "web-app"})
        self.assertEqual(self.session.started, "2026-10-20")

    def test_the_sub_agent_reads_count(self) -> None:
        self.assertEqual(
            self.session.marks["python/references/state-collections.md"],
            {"read"},
        )

    def test_the_strongest_mark_wins(self) -> None:
        self.assertEqual(read_marks.strongest({"searched", "part"}), "part")
        self.assertEqual(read_marks.strongest(set()), "never")


class TheReport(unittest.TestCase):

    def setUp(self) -> None:
        sessions = read_marks.sessions_since(TESTDATA, "2026-10-01")
        self.report = read_marks.report(SKILLS, sessions, 1, "all")
        self.rows = {
            r["path"]: r
            for r in self.report["every_build"] + self.report["conditional"]
        }

    def test_builds_are_split_by_the_plugin_they_ran(self) -> None:
        self.assertEqual(
            self.report["builds_by_plugin"], {"this": 1, "other": 1}
        )
        [this] = [b for b in self.report["builds"] if b["plugin"] == "this"]
        self.assertEqual(this["project"], "hotel")
        self.assertEqual(this["doors"], ["web-app"])

    def test_each_item_gets_its_mark(self) -> None:
        def mark(path: str) -> str:
            row = self.rows[path]
            this = [m for m in read_marks.MARKS if row[m]]
            # The other package's build read only web-app's SKILL.md.
            return this[0]

        self.assertEqual(mark("web-app/SKILL.md"), "read")
        self.assertEqual(mark("python/references/api-pydantic.md"), "read")
        self.assertEqual(mark("python/references/api-methods.md"), "part")
        self.assertEqual(mark("python/references/rpc-calls.md"), "searched")
        self.assertEqual(mark("dashboard/SKILL.md"), "never")

    def test_conditional_references_are_reported_apart(self) -> None:
        conditional = {r["path"] for r in self.report["conditional"]}
        self.assertIn("python/references/api-errors.md", conditional)
        self.assertIn("python/references/servicer-workflow.md", conditional)
        self.assertNotIn("python/references/api-pydantic.md", conditional)
        self.assertEqual(
            self.rows["python/references/api-errors.md"]["read"], 1
        )

    def test_too_few_reads_is_not_a_build(self) -> None:
        sessions = read_marks.sessions_since(TESTDATA, "2026-10-01")
        report = read_marks.report(SKILLS, sessions, 100, "all")
        self.assertEqual(report["builds"], [])


if __name__ == "__main__":
    unittest.main()
