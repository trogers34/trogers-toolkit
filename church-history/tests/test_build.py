import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import build  # noqa: E402

VALID = {
    "name": "Test Person",
    "slug": "test-person",
    "era": "Early Church",
    "summary": "A test.",
    "born": {"year": 300, "sources": ["s1"]},
    "died": {"year": 360, "sources": ["s1"]},
    "key_dates": [{"year": 330, "label": "Did a thing", "sources": ["s1"]}],
    "accomplishments": [{"text": "Accomplished something.", "sources": ["s1"]}],
    "sources": [{"id": "s1", "type": "scholarly", "citation": "A Book."}],
}


class ValidatePersonTest(unittest.TestCase):
    def errors_for(self, mutate):
        person = copy.deepcopy(VALID)
        mutate(person)
        return build.validate_person(person, "test-person")

    def test_valid_person_has_no_errors(self):
        self.assertEqual(build.validate_person(copy.deepcopy(VALID), "test-person"), [])

    def test_accomplishment_without_sources(self):
        errors = self.errors_for(lambda p: p["accomplishments"][0].update(sources=[]))
        self.assertIn("accomplishments[0] has no sources", errors)

    def test_unknown_source_reference(self):
        errors = self.errors_for(lambda p: p["key_dates"][0].update(sources=["nope"]))
        self.assertIn("key_dates[0] cites unknown source 'nope'", errors)

    def test_key_date_outside_lifespan(self):
        errors = self.errors_for(lambda p: p["key_dates"][0].update(year=400))
        self.assertTrue(any("outside lifespan" in e for e in errors))

    def test_slug_must_match_file(self):
        errors = self.errors_for(lambda p: p.update(slug="other"))
        self.assertTrue(any("must match file name" in e for e in errors))

    def test_missing_field(self):
        errors = self.errors_for(lambda p: p.pop("summary"))
        self.assertEqual(errors, ["missing required field 'summary'"])


class TimelineTest(unittest.TestCase):
    def test_bounds_round_to_tick_step(self):
        people = [{"born": {"year": 354}, "died": {"year": 430}},
                  {"born": {"year": 1703}, "died": {"year": 1791}}]
        self.assertEqual(build.timeline_bounds(people), (200, 1800, 200))

    def test_bounds_for_single_lifespan(self):
        people = [{"born": {"year": 1483}, "died": {"year": 1546}}]
        self.assertEqual(build.timeline_bounds(people), (1480, 1550, 10))

    def test_bc_years(self):
        self.assertEqual(build.format_year(-4), "4 BC")
        self.assertEqual(build.format_year(397, circa=True), "c. 397")


class BuildTest(unittest.TestCase):
    def test_repository_data_is_valid(self):
        people = build.load_people()
        self.assertGreater(len(people), 0)

    def test_build_writes_pages(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            people_dir = tmp / "people"
            people_dir.mkdir()
            (people_dir / "test-person.json").write_text(json.dumps(VALID))
            people = build.load_people(people_dir)
            build.build(people, tmp / "site")
            index = (tmp / "site" / "index.html").read_text()
            person = (tmp / "site" / "people" / "test-person.html").read_text()
        self.assertIn("people/test-person.html", index)
        self.assertIn("Did a thing", index)
        self.assertIn('id="src-s1"', person)
        self.assertIn('href="#src-s1"', person)


if __name__ == "__main__":
    unittest.main()
