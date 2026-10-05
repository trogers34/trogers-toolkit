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
    "persecution": [],
    "persecution_note": "None recorded.",
    "excommunications": [],
    "excommunication_note": "Never excommunicated.",
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

    def test_sayings_need_sources_and_known_category(self):
        errors = self.errors_for(lambda p: p.update(sayings={
            "original": [{"phrase": "x", "sources": []}],
            "invented": [],
        }))
        self.assertIn("sayings.original[0] has no sources", errors)
        self.assertTrue(any("sayings category 'invented'" in e for e in errors))

    def test_empty_persecution_needs_a_note(self):
        errors = self.errors_for(lambda p: p.pop("persecution_note"))
        self.assertTrue(any("add 'persecution_note'" in e for e in errors))

    def test_persecution_event_must_name_responsible_parties(self):
        event = {"year": 330, "title": "Arrested", "summary": "s", "outcome": "o", "sources": ["s1"],
                 "responsible": [{"name": "A Bishop", "role": "Bishop", "type": "pope-ish"}]}
        errors = self.errors_for(lambda p: p.update(persecution=[event]))
        self.assertTrue(any("responsible[0] type" in e for e in errors))
        event["responsible"] = []
        errors = self.errors_for(lambda p: p.update(persecution=[event]))
        self.assertIn("persecution[0] must list who was responsible", errors)

    def test_excommunications_required(self):
        errors = self.errors_for(lambda p: p.pop("excommunication_note"))
        self.assertTrue(any("add 'excommunication_note'" in e for e in errors))
        errors = self.errors_for(lambda p: p.update(excommunications=[{"date": "1410", "sources": ["s1"]}]))
        self.assertIn("excommunications[0] needs 'by'", errors)

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

    def test_committed_site_is_up_to_date(self):
        # Fails if someone edited people/ without re-running build.py.
        people = build.load_people()
        index = (build.SITE_DIR / "index.html").read_text(encoding="utf-8")
        self.assertEqual(index, build.render_index(people), "site/ is stale: run python3 build.py")
        for person in people:
            self.assertIn(f'href="people/{person["slug"]}.html"', index)
            page = build.SITE_DIR / "people" / f'{person["slug"]}.html'
            self.assertTrue(page.exists(), f"missing {page.name}: run python3 build.py")
            self.assertEqual(page.read_text(encoding="utf-8"), build.render_person(person),
                             f"{page.name} is stale: run python3 build.py")

    def test_claude_md_lists_every_person(self):
        # CLAUDE.md is the project's memory; its roster must match people/.
        import re
        listed = set(re.findall(r"\(`([a-z0-9-]+)`\)", (build.ROOT / "CLAUDE.md").read_text(encoding="utf-8")))
        on_site = {p.stem for p in build.PEOPLE_DIR.glob("*.json")}
        self.assertEqual(on_site - listed, set(), "add these people to CLAUDE.md")
        self.assertEqual(listed - on_site, set(), "CLAUDE.md lists people with no data file")

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
        self.assertNotIn("Words and sayings", person)

    def test_sayings_render_by_category(self):
        person = copy.deepcopy(VALID)
        person["sayings"] = {"popularized": [{"phrase": "Old phrase", "reference": "John 1:1", "sources": ["s1"]}]}
        page = build.render_person(person)
        self.assertIn("Words and sayings", page)
        self.assertIn("Popularized", page)
        self.assertNotIn("<h3>Original", page)

    def test_persecution_renders_responsible_table(self):
        person = copy.deepcopy(VALID)
        person["persecution"] = [{
            "year": 330, "title": "Arrested", "summary": "Taken.", "outcome": "Released.", "sources": ["s1"],
            "responsible": [{"name": "Governor X", "role": "Governor", "jurisdiction": "Province Y", "type": "state"}],
            "defended_by": [{"name": "Friend Z", "role": "Bishop"}],
        }]
        page = build.render_person(person)
        self.assertIn("Persecution, arrests, and executions", page)
        self.assertIn("Governor X", page)
        self.assertIn("Province Y", page)
        self.assertIn("Friend Z", page)

    def test_ai_notice_on_every_page(self):
        person = copy.deepcopy(VALID)
        self.assertIn("This page was fully generated by AI, using Claude", build.render_person(person))
        person["ai_generated"] = "partial"
        self.assertIn("This page was partially generated by AI, using Claude", build.render_person(person))
        self.assertIn("generated in whole or in part by AI, using Claude", build.render_index([VALID]))
        person["ai_generated"] = "none"
        self.assertTrue(any("'ai_generated'" in e for e in build.validate_person(person, "test-person")))

    def test_excommunications_render(self):
        person = copy.deepcopy(VALID)
        person["excommunications"] = [{"date": "3 January 1521", "by": "Pope Leo X", "authority": "Papacy",
                                       "reason": "Refused to recant", "status": "Never lifted", "sources": ["s1"]}]
        page = build.render_person(person)
        self.assertIn("<h3>Excommunications</h3>", page)
        self.assertIn("Pope Leo X", page)
        self.assertIn("Never lifted", page)


if __name__ == "__main__":
    unittest.main()
