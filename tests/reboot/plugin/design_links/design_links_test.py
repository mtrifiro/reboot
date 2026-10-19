"""`scripts/design_links.py` checks design/design.md's dashboard links
against the code: links to nothing, rule links renumbered by a rule
added above them, and what the code has that the document doesn't link.

Run in a throwaway project with both scripts copied into its
`scripts/`, as an app has them. The tests are not copied into apps.
"""

import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(os.environ.get(
    "MODEL_DIFF_DIR",
    str(Path(__file__).resolve().parents[4] / "reboot/plugin/skills/app/assets/scripts"),
))

API = '''
from reboot.api import API, Field, Methods, Model, Reader, Type, Writer

class RoomState(Model):
    nights: list[str] = Field(tag=1, default_factory=list, description="Booked.")

RoomMethods = Methods(
    availability=Reader(request=None, response=None, description="Free?", mcp=None),
    book=Writer(request=None, response=None, description="Book.", mcp=None),
)

api = API(Room=Type(state=RoomState, methods=RoomMethods, description="A room."))
'''

FEATURE = """Feature: Guests book rooms

  Rule: A room is booked at most once per night

    Scenario: A second guest asks for a booked night
      Given a booked room

  Rule: A cancelled booking frees its night

    Scenario: Cancel, then book again
      Given a booked room
"""

D = "http://127.0.0.1:9871/#/"

DOCUMENT = f"""# Rooms: the design

- **[Room]({D}models?type=hotel.v1.Room):** one per room.

[Guests book rooms]({D}features/tests/booking.feature)
- [A room is booked at most once per night]({D}features/tests/booking.feature/rules/1)
- [A cancelled booking frees its night]({D}features/tests/booking.feature/rules/2)

| [`availability`]({D}models?type=hotel.v1.Room.availability) | Reader |
| [`book`]({D}models?type=hotel.v1.Room.book) | Writer |
"""


class DesignLinks(unittest.TestCase):

    def setUp(self) -> None:
        self.root = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.root)
        (self.root / "scripts").mkdir()
        for name in ("model_diff.py", "design_links.py"):
            shutil.copy(SCRIPTS / name, self.root / "scripts" / name)
        self.write("api/hotel/v1/hotel.py", API)
        self.write("tests/booking.feature", FEATURE)
        self.write("design/design.md", DOCUMENT)

    def write(self, path: str, text: str) -> None:
        (self.root / path).parent.mkdir(parents=True, exist_ok=True)
        (self.root / path).write_text(text)

    def run_it(self, *args: str) -> subprocess.CompletedProcess:
        return subprocess.run(
            [sys.executable, "-B", "scripts/design_links.py", *args],
            cwd=self.root, capture_output=True, text=True,
        )

    def test_a_document_that_matches_the_code(self) -> None:
        r = self.run_it()
        self.assertEqual(r.returncode, 0, r.stdout)
        self.assertIn("everything in the code is linked", r.stdout)

    def test_portless_links_are_checked_the_same(self) -> None:
        named = (self.root / "design/design.md").read_text().replace(D, "https://dashboard.hotel.localhost/#/")
        self.write("design/design.md", named)
        self.assertEqual(self.run_it().returncode, 0)
        self.write("design/design.md", named.replace("Room.book)", "Room.reserve)"))
        self.assertIn("no object or method `hotel.v1.Room.reserve`", self.run_it().stdout)

    def test_base_moves_every_link_to_another_dashboard(self) -> None:
        before = (self.root / "design/design.md").read_text()
        r = self.run_it("--base", "https://dashboard.hotel.localhost")
        self.assertEqual(r.returncode, 0, r.stdout)
        text = (self.root / "design/design.md").read_text()
        self.assertNotIn("127.0.0.1", text)
        self.assertIn("https://dashboard.hotel.localhost/#/models?type=hotel.v1.Room)", text)
        self.run_it("--base", "http://127.0.0.1:9871")
        self.assertEqual((self.root / "design/design.md").read_text(), before)

    def test_a_link_to_a_method_that_does_not_exist(self) -> None:
        self.write("design/design.md", DOCUMENT.replace("Room.book)", "Room.reserve)"))
        r = self.run_it()
        self.assertEqual(r.returncode, 1)
        self.assertIn("no object or method `hotel.v1.Room.reserve`", r.stdout)
        self.assertIn("method `hotel.v1.Room.book`", r.stdout)

    def test_a_rule_added_above_renumbers_the_links(self) -> None:
        self.write("tests/booking.feature", FEATURE.replace(
            "  Rule: A room is booked",
            "  Rule: A night is booked only in the future\n\n"
            "    Scenario: Yesterday\n      Given yesterday\n\n"
            "  Rule: A room is booked",
        ))
        r = self.run_it()
        self.assertEqual(r.returncode, 1)
        self.assertIn("rules/1): that rule is now /rules/2", r.stdout)
        self.assertIn("rules/2): that rule is now /rules/3", r.stdout)
        self.assertIn("rules/1`: A night is booked only in the future", r.stdout)

    def test_a_rule_number_past_the_end(self) -> None:
        self.write("design/design.md", DOCUMENT.replace("rules/2)", "rules/5)"))
        r = self.run_it()
        self.assertIn("`tests/booking.feature` has 2 rules", r.stdout)

    def test_an_object_left_unlinked(self) -> None:
        self.write("design/design.md", DOCUMENT.replace(
            f"[Room]({D}models?type=hotel.v1.Room)", "Room"))
        r = self.run_it()
        self.assertIn("object `hotel.v1.Room`", r.stdout)

    def test_port_rewrites_every_link(self) -> None:
        r = self.run_it("--port", "9873")
        self.assertEqual(r.returncode, 0, r.stdout)
        text = (self.root / "design/design.md").read_text()
        self.assertNotIn(":9871/", text)
        self.assertEqual(text.count(":9873/#/"), 6)

    def test_no_document(self) -> None:
        (self.root / "design/design.md").unlink()
        self.assertEqual(self.run_it().returncode, 2)


LOG = f"""# Decisions

## 2026-10-14: Design accepted: Booking

- **Decided by the build:** [`book`]({D}models?type=hotel.v1.Room.book)
  is a Writer; see [the rule]({D}features/tests/booking.feature/rules/1).

## 2026-10-15: Design accepted: Cancelling & rebooking

- **Decided by the build:** [Room]({D}models?type=hotel.v1.Room) keeps
  its nights; [cancelling]({D}features/tests/booking.feature) frees one.
"""

ENTRIES = """
- [Booking](decisions.md#2026-10-14-design-accepted-booking): a Writer.
- [Cancelling](decisions.md#2026-10-15-design-accepted-cancelling--rebooking): frees a night.
"""


class TheDecisionsLog(DesignLinks):

    def setUp(self) -> None:
        super().setUp()
        self.write("design/decisions.md", LOG)
        self.write("design/design.md", DOCUMENT + ENTRIES)

    def test_every_entry_linked(self) -> None:
        r = self.run_it()
        self.assertEqual(r.returncode, 0, r.stdout)

    def test_an_entry_left_unlinked(self) -> None:
        self.write("design/design.md", DOCUMENT + ENTRIES.splitlines()[1])
        r = self.run_it()
        self.assertIn('decisions entry "2026-10-15: Design accepted: Cancelling & rebooking"', r.stdout)

    def test_a_link_to_no_entry(self) -> None:
        self.write("design/design.md", DOCUMENT + ENTRIES + "- [Old](decisions.md#2026-01-01-gone)\n")
        r = self.run_it()
        self.assertIn("no entry in decisions.md has the anchor #2026-01-01-gone", r.stdout)

    def test_the_newest_entry_links_rules_by_their_feature(self) -> None:
        # The older entry's rule-number link is history and is left alone.
        r = self.run_it()
        self.assertNotIn("not rule 1", r.stdout)
        self.write("design/decisions.md", LOG + f"  See [it]({D}features/tests/booking.feature/rules/2).\n")
        r = self.run_it()
        self.assertIn("link the feature file, not rule 2", r.stdout)

    def test_port_rewrites_the_log_too(self) -> None:
        self.run_it("--port", "9873")
        log = (self.root / "design/decisions.md").read_text()
        self.assertEqual(log.count(":9873/#/"), 4)
        self.assertNotIn(":9871/", log)

    def test_the_newest_entry_links_to_nothing(self) -> None:
        self.write("design/decisions.md", LOG.replace("type=hotel.v1.Room)", "type=hotel.v1.Rooms)"))
        r = self.run_it()
        self.assertIn("newest entry: [Room]", r.stdout)
        self.assertIn("no object or method `hotel.v1.Rooms`", r.stdout)


if __name__ == "__main__":
    unittest.main()
