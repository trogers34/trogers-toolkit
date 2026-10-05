#!/usr/bin/env python3
"""Build the Church History site from the JSON files in people/ and events/.

Usage:
    python3 build.py            # validate data and write the site to site/
    python3 build.py --check    # validate only

No third-party dependencies.
"""

import argparse
import html
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PEOPLE_DIR = ROOT / "people"
EVENTS_DIR = ROOT / "events"
SITE_DIR = ROOT / "site"
STATIC_DIR = ROOT / "static"

REQUIRED_FIELDS = ["name", "slug", "era", "summary", "born", "died",
                   "key_dates", "accomplishments", "persecution", "excommunications", "sources"]
EVENT_REQUIRED_FIELDS = ["name", "slug", "era", "event_type", "start", "summary", "happened",
                         "outcomes", "sources"]
EVENT_TYPES = {
    "council": "Council", "schism": "Schism", "persecution": "Persecution", "massacre": "Massacre",
    "trial": "Trial", "war": "War", "revival": "Revival", "document": "Document",
    "assembly": "Imperial assembly", "other": "Event",
}
PARTY_TYPES = {"church": "Church", "state": "State", "individual": "Individual", "group": "Group"}
SOURCE_TYPES = {"primary", "scholarly", "reference"}
VERIFICATION_LEVELS = {
    "verified": ("100% verified", "Documented in official records or the person's own writings."),
    "partial": ("Partially verified", "Part of the claim is documented; the rest rests on hostile, later, or indirect sources."),
    "disputed": ("Disputed", "Alleged by some sources, denied or contradicted by others, and not independently confirmed."),
    "unverified": ("Unverified", "No reliable source confirms it."),
}
SAYING_CATEGORIES = {
    "original": ("Original",
                 "First recorded in their writing, or first worded this way by them."),
    "popularized": ("Popularized",
                    "Already in use before them, but their use made it widely known."),
    "misattributed": ("Misattributed",
                      "Commonly credited to them, but not found in their writings."),
}
AI_LEVELS = {"full": "fully", "partial": "partially"}


class ValidationError(Exception):
    pass


def esc(text):
    return html.escape(str(text), quote=True)


# ---------------------------------------------------------------- loading and validation

def load_people(people_dir=PEOPLE_DIR):
    people = []
    errors = []
    for path in sorted(people_dir.glob("*.json")):
        try:
            person = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            errors.append(f"{path.name}: invalid JSON ({exc})")
            continue
        errors.extend(f"{path.name}: {e}" for e in validate_person(person, path.stem))
        people.append(person)
    slugs = [p.get("slug") for p in people]
    for slug in {s for s in slugs if slugs.count(s) > 1}:
        errors.append(f"duplicate slug '{slug}'")
    if errors:
        raise ValidationError("\n".join(errors))
    return sorted(people, key=lambda p: p["born"]["year"])


def load_events(people_slugs=None, events_dir=EVENTS_DIR):
    events = []
    errors = []
    paths = sorted(events_dir.glob("*.json")) if events_dir.exists() else []
    for path in paths:
        try:
            event = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            errors.append(f"events/{path.name}: invalid JSON ({exc})")
            continue
        errors.extend(f"events/{path.name}: {e}" for e in validate_event(event, path.stem, people_slugs))
        events.append(event)
    if errors:
        raise ValidationError("\n".join(errors))
    return sorted(events, key=lambda e: e["start"]["year"])


def source_checker(item, errors):
    """Validate an item's source list; return a function that checks citations against it."""
    source_ids = set()
    for src in item["sources"]:
        if not src.get("id") or not src.get("citation"):
            errors.append(f"source needs 'id' and 'citation': {src}")
        if src.get("type") not in SOURCE_TYPES:
            errors.append(f"source '{src.get('id')}' type must be one of {sorted(SOURCE_TYPES)}")
        if src.get("id") in source_ids:
            errors.append(f"duplicate source id '{src.get('id')}'")
        source_ids.add(src.get("id"))

    def check_refs(where, entry):
        refs = entry.get("sources") or []
        if not refs:
            errors.append(f"{where} has no sources")
        for ref in refs:
            if ref not in source_ids:
                errors.append(f"{where} cites unknown source '{ref}'")
    return check_refs


def validate_shared_sections(item, errors, check_refs, excomm_key):
    """Checks for sections people and events share: AI notice, condemnations, persecution, victims."""
    if item.get("ai_generated", "full") not in AI_LEVELS:
        errors.append(f"'ai_generated' must be one of {list(AI_LEVELS)}")

    for i, ex in enumerate(item.get(excomm_key) or []):
        where = f"{excomm_key}[{i}]"
        for field in ("date", "by", "authority", "reason", "status"):
            if not ex.get(field):
                errors.append(f"{where} needs '{field}'")
        check_refs(where, ex)

    for i, ev in enumerate(item.get("persecution") or []):
        where = f"persecution[{i}]"
        for field in ("title", "summary", "outcome"):
            if not ev.get(field):
                errors.append(f"{where} needs '{field}'")
        if not ev.get("date") and not isinstance(ev.get("year"), int):
            errors.append(f"{where} needs a 'year' or 'date'")
        if not ev.get("responsible"):
            errors.append(f"{where} must list who was responsible")
        for j, party in enumerate(ev.get("responsible", []) + ev.get("defended_by", [])):
            if not party.get("name") or not party.get("role"):
                errors.append(f"{where} party {j} needs 'name' and 'role'")
        for j, party in enumerate(ev.get("responsible", [])):
            if party.get("type") not in PARTY_TYPES:
                errors.append(f"{where}.responsible[{j}] type must be one of {list(PARTY_TYPES)}")
        check_refs(where, ev)

    for i, v in enumerate(item.get("victims") or []):
        where = f"victims[{i}]"
        for field in ("name", "executed", "condemned_by", "allegation"):
            if not v.get(field):
                errors.append(f"{where} needs '{field}'")
        ver = v.get("verification", {})
        for key in ("execution", "link"):
            if ver.get(key) not in VERIFICATION_LEVELS:
                errors.append(f"{where}.verification.{key} must be one of {list(VERIFICATION_LEVELS)}")
        for link in v.get("links", []):
            if not link.get("label") or not str(link.get("url", "")).startswith("https://"):
                errors.append(f"{where} links need a label and an https url")
        check_refs(where, v)
    if item.get("victims") and not item.get("victims_title"):
        errors.append("'victims' needs a 'victims_title'")


def validate_person(person, file_stem):
    errors = []
    for field in REQUIRED_FIELDS:
        if field not in person:
            errors.append(f"missing required field '{field}'")
    if errors:
        return errors

    if person["slug"] != file_stem:
        errors.append(f"slug '{person['slug']}' must match file name '{file_stem}.json'")

    check_refs = source_checker(person, errors)

    for key in ("born", "died"):
        life = person[key]
        if not isinstance(life.get("year"), int):
            errors.append(f"'{key}.year' must be an integer")
        check_refs(key, life)

    born, died = person["born"].get("year"), person["died"].get("year")
    if isinstance(born, int) and isinstance(died, int) and born > died:
        errors.append("born year is after died year")

    for i, kd in enumerate(person["key_dates"]):
        where = f"key_dates[{i}]"
        if not isinstance(kd.get("year"), int):
            errors.append(f"{where}.year must be an integer")
        elif isinstance(born, int) and isinstance(died, int) and not born <= kd["year"] <= died:
            errors.append(f"{where} year {kd['year']} is outside lifespan {born}-{died}")
        if not kd.get("label"):
            errors.append(f"{where} needs a label")
        check_refs(where, kd)

    if not person["accomplishments"]:
        errors.append("needs at least one accomplishment")
    for i, acc in enumerate(person["accomplishments"]):
        if not acc.get("text"):
            errors.append(f"accomplishments[{i}] needs text")
        check_refs(f"accomplishments[{i}]", acc)

    if not person["excommunications"] and not person.get("excommunication_note"):
        errors.append("'excommunications' is empty: add 'excommunication_note' saying none is recorded")
    if not person["persecution"] and not person.get("persecution_note"):
        errors.append("'persecution' is empty: add 'persecution_note' saying none is recorded")
    validate_shared_sections(person, errors, check_refs, "excommunications")

    sayings = person.get("sayings", {})
    for category in sayings:
        if category not in SAYING_CATEGORIES:
            errors.append(f"sayings category '{category}' must be one of {list(SAYING_CATEGORIES)}")
            continue
        for i, item in enumerate(sayings[category]):
            where = f"sayings.{category}[{i}]"
            if not item.get("phrase"):
                errors.append(f"{where} needs a phrase")
            check_refs(where, item)

    return errors


def validate_event(event, file_stem, people_slugs=None):
    errors = []
    for field in EVENT_REQUIRED_FIELDS:
        if field not in event:
            errors.append(f"missing required field '{field}'")
    if errors:
        return errors

    if event["slug"] != file_stem:
        errors.append(f"slug '{event['slug']}' must match file name '{file_stem}.json'")
    if event["event_type"] not in EVENT_TYPES:
        errors.append(f"event_type must be one of {list(EVENT_TYPES)}")

    check_refs = source_checker(event, errors)

    start, end = event["start"], event.get("end", event["start"])
    for key, when in (("start", start), ("end", end)):
        if not isinstance(when.get("year"), int):
            errors.append(f"'{key}.year' must be an integer")
    check_refs("start", start)
    if "end" in event:
        check_refs("end", end)
    years_ok = isinstance(start.get("year"), int) and isinstance(end.get("year"), int)
    if years_ok and start["year"] > end["year"]:
        errors.append("start year is after end year")
    for i, kd in enumerate(event.get("key_dates", [])):
        where = f"key_dates[{i}]"
        if not isinstance(kd.get("year"), int):
            errors.append(f"{where}.year must be an integer")
        elif years_ok and not start["year"] <= kd["year"] <= end["year"]:
            errors.append(f"{where} year {kd['year']} is outside the event's dates")
        if not kd.get("label"):
            errors.append(f"{where} needs a label")
        check_refs(where, kd)

    for key in ("background", "happened", "outcomes"):
        if key != "background" and not event.get(key):
            errors.append(f"'{key}' needs at least one item")
        for i, entry in enumerate(event.get(key) or []):
            if not entry.get("text"):
                errors.append(f"{key}[{i}] needs text")
            check_refs(f"{key}[{i}]", entry)

    for i, part in enumerate(event.get("participants", [])):
        if not part.get("name") or not part.get("role"):
            errors.append(f"participants[{i}] needs 'name' and 'role'")
        if part.get("person") and people_slugs is not None and part["person"] not in people_slugs:
            errors.append(f"participants[{i}] links to unknown person '{part['person']}'")

    validate_shared_sections(event, errors, check_refs, "condemnations")
    return errors


# ---------------------------------------------------------------- shared rendering

def format_year(year, circa=False):
    text = f"{-year} BC" if year < 0 else str(year)
    return f"c. {text}" if circa else text


def life_year(life):
    return format_year(life["year"], life.get("circa", False))


def lifespan(person):
    return f'{life_year(person["born"])}&ndash;{life_year(person["died"])}'


def event_span(event):
    start = event["start"]
    end = event.get("end")
    if not end or end["year"] == start["year"]:
        return life_year(start)
    return f"{life_year(start)}&ndash;{life_year(end)}"


def ai_notice(level=None):
    if level is None:
        text = ("The content on this site is generated in whole or in part by AI, using Claude "
                "(by Anthropic). It may contain errors. Check the cited sources before relying on any detail.")
    else:
        text = (f"This page was {AI_LEVELS[level]} generated by AI, using Claude (by Anthropic). "
                "It may contain errors. Check the cited sources before relying on any detail.")
    return f'<p class="ai-notice" role="note"><strong>AI-generated content.</strong> {text}</p>'


def page(title, body, root="", notice=None):
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<link rel="stylesheet" href="{root}style.css">
</head>
<body>
<header class="site-header">
  <a class="brand" href="{root}index.html">Church History</a>
  <span class="tagline">People, events, dates, and sources</span>
</header>
<main>
{notice or ai_notice()}
{body}
</main>
<footer class="site-footer">Every statement on this site is tied to a cited source. Check the references before relying on a detail.</footer>
</body>
</html>
"""


def cite(refs, numbers):
    links = "".join(
        f'<a href="#src-{esc(r)}" class="cite">[{numbers[r]}]</a>' for r in refs
    )
    return f'<sup class="cites">{links}</sup>'


def source_numbers(item):
    return {s["id"]: i for i, s in enumerate(item["sources"], start=1)}


def render_bullets(items, numbers, css_class="accomplishments"):
    lis = "\n".join(f'<li>{esc(a["text"])}{cite(a["sources"], numbers)}</li>' for a in items)
    return f'<ul class="{css_class}">\n{lis}\n    </ul>'


def render_incident(ev, numbers):
    when = ev.get("date") or format_year(ev["year"], ev.get("circa", False))
    rows = "\n".join(
        f'<tr><td><strong>{esc(r["name"])}</strong></td><td>{esc(r["role"])}</td>'
        f'<td>{esc(r.get("jurisdiction", ""))}</td>'
        f'<td><span class="party {esc(r["type"])}">{PARTY_TYPES[r["type"]]}</span></td></tr>'
        for r in ev["responsible"]
    )
    defended = ""
    if ev.get("defended_by"):
        names = "; ".join(f'{esc(d["name"])} ({esc(d["role"])})' for d in ev["defended_by"])
        defended = f'<p class="defended"><strong>Protected or defended by:</strong> {names}</p>'
    return f'''
    <div class="incident">
      <p class="when">{esc(when)}</p>
      <h3>{esc(ev["title"])}</h3>
      <p>{esc(ev["summary"])}{cite(ev["sources"], numbers)}</p>
      <div class="table-wrap">
      <table class="responsible">
        <caption>Who was responsible</caption>
        <thead><tr><th>Who</th><th>Role</th><th>Jurisdiction / institution</th><th>Type</th></tr></thead>
        <tbody>
{rows}
        </tbody>
      </table>
      </div>
      {defended}
      <p class="outcome"><strong>Outcome:</strong> {esc(ev["outcome"])}</p>
    </div>'''


def render_condemnations(entries, note, numbers, title):
    rows = "\n".join(
        f'<tr><td class="nowrap">{esc(ex["date"])}</td><td><strong>{esc(ex["by"])}</strong></td>'
        f'<td>{esc(ex["authority"])}</td><td>{esc(ex["reason"])}{cite(ex["sources"], numbers)}</td>'
        f'<td>{esc(ex["status"])}</td></tr>'
        for ex in entries
    )
    table = f'''
      <div class="table-wrap">
      <table class="responsible excomm">
        <thead><tr><th>Date</th><th>By</th><th>Authority</th><th>Reason</th><th>Status</th></tr></thead>
        <tbody>
{rows}
        </tbody>
      </table>
      </div>''' if rows else ""
    return f'''
    <div class="excommunications">
      <h3>{esc(title)}</h3>
      {f'<p>{esc(note)}</p>' if note else ""}{table}
    </div>'''


def render_victims(item, numbers, subject_short):
    if not item.get("victims"):
        return ""

    def badge(level, prefix):
        label = VERIFICATION_LEVELS[level][0]
        return f'<span class="verify {esc(level)}">{esc(prefix)}: {esc(label)}</span>'

    legend = "".join(
        f'<li><span class="verify {k}">{esc(v[0])}</span> {esc(v[1])}</li>' for k, v in VERIFICATION_LEVELS.items()
    )
    cards = []
    for v in item["victims"]:
        links = " · ".join(
            f'<a href="{esc(l["url"])}" rel="noopener">{esc(l["label"])}</a>' for l in v.get("links", [])
        )
        note = f'<p class="note">{esc(v["verification_note"])}</p>' if v.get("verification_note") else ""
        cards.append(f'''
    <div class="incident victim">
      <h3>{esc(v["name"])}</h3>
      <p class="when">{esc(v["executed"])}</p>
      <p><strong>Condemned by:</strong> {esc(v["condemned_by"])}</p>
      <p><strong>What {esc(subject_short)} is accused of:</strong> {esc(v["allegation"])}{cite(v["sources"], numbers)}</p>
      <p class="badges">{badge(v["verification"]["execution"], "Execution")} {badge(v["verification"]["link"], "Link to " + subject_short)}</p>
      {note}
      {f'<p class="links"><strong>Links:</strong> {links}</p>' if links else ""}
    </div>''')
    intro = f'<p class="intro">{esc(item["victims_intro"])}</p>' if item.get("victims_intro") else ""
    return f'''
  <section>
    <h2>{esc(item["victims_title"])}</h2>
    {intro}
    <details class="legend"><summary>How the verification ratings work</summary><ul>{legend}</ul></details>
    {"".join(cards)}
  </section>
'''


def render_key_dates(entries, numbers):
    lis = "\n".join(
        f'<li class="{e["kind"]}"><span class="year">{format_year(e["year"], e.get("circa"))}</span>'
        f'<span class="label">{esc(e["label"])}{cite(e["sources"], numbers)}</span></li>'
        for e in entries
    )
    return f'''
  <section>
    <h2>Key dates</h2>
    <ol class="key-dates">
{lis}
    </ol>
  </section>
'''


def render_sources(item):
    def source_item(s):
        text = esc(s["citation"])
        if s.get("url"):
            text += f' <a href="{esc(s["url"])}" rel="noopener">{esc(s["url"])}</a>'
        return (f'<li id="src-{esc(s["id"])}"><span class="src-type {esc(s["type"])}">'
                f'{esc(s["type"])}</span> {text}</li>')

    items = "\n".join(source_item(s) for s in item["sources"])
    return f'''
  <section>
    <h2>References</h2>
    <ol class="sources">
{items}
    </ol>
  </section>
'''


def events_for_person(slug, events):
    """Events the person took part in, with their role."""
    found = []
    for ev in events:
        for part in ev.get("participants", []):
            if part.get("person") == slug:
                found.append((ev, part["role"]))
                break
    return found


# ---------------------------------------------------------------- person page

def render_person(person, events=()):
    numbers = source_numbers(person)
    born, died = person["born"], person["died"]

    aka = f'<p class="aka">Also known as {esc(person["also_known_as"])}</p>' if person.get("also_known_as") else ""
    role = f'<p class="role">{esc(person["role"])}</p>' if person.get("role") else ""

    def life_row(label, life):
        place = f' &middot; {esc(life["place"])}' if life.get("place") else ""
        return (f'<div><dt>{label}</dt><dd>{esc(life.get("date") or life_year(life))}'
                f'{place}{cite(life["sources"], numbers)}</dd></div>')

    dates = [{"year": born["year"], "label": "Born", "sources": born["sources"], "kind": "life", "circa": born.get("circa")}]
    dates += [dict(kd, kind="event") for kd in person["key_dates"]]
    dates.append({"year": died["year"], "label": "Died", "sources": died["sources"], "kind": "life", "circa": died.get("circa")})
    dates.sort(key=lambda e: (e["year"], e["kind"] != "life" or e["label"] == "Died"))

    related = events_for_person(person["slug"], events)
    events_html = ""
    if related:
        lis = "\n".join(
            f'<li><a href="../events/{esc(ev["slug"])}.html"><strong>{esc(ev["name"])}</strong></a> '
            f'<span class="ref">{event_span(ev)} &middot; {EVENT_TYPES[ev["event_type"]]}</span>'
            f'<p class="note">{esc(role_text)}</p></li>'
            for ev, role_text in related
        )
        events_html = f'''
  <section>
    <h2>Events</h2>
    <ul class="sayings event-links">
{lis}
    </ul>
  </section>
'''

    excomm = render_condemnations(person["excommunications"], person.get("excommunication_note"),
                                  numbers, "Excommunications")
    note = person.get("persecution_note")
    persecution_html = f'''
  <section>
    <h2>Persecution, arrests, and executions</h2>
    {f'<p class="intro">{esc(note)}</p>' if note else ""}{excomm}{"".join(render_incident(ev, numbers) for ev in person["persecution"])}
  </section>
'''

    sayings_html = ""
    if person.get("sayings"):
        groups = []
        for category, (title, description) in SAYING_CATEGORIES.items():
            items = person["sayings"].get(category, [])
            if not items:
                continue
            lis = "\n".join(
                f'<li><span class="phrase">{esc(s["phrase"])}</span>'
                + (f' <span class="ref">{esc(s["reference"])}</span>' if s.get("reference") else "")
                + cite(s["sources"], numbers)
                + (f'<p class="note">{esc(s["note"])}</p>' if s.get("note") else "")
                + "</li>"
                for s in items
            )
            groups.append(f'''
    <div class="saying-group {category}">
      <h3>{title} <span class="count">{len(items)}</span></h3>
      <p class="saying-desc">{esc(description)}</p>
      <ul class="sayings">
{lis}
      </ul>
    </div>''')
        intro = f'<p class="intro">{esc(person["sayings_intro"])}</p>' if person.get("sayings_intro") else ""
        sayings_html = f'''
  <section>
    <h2>Words and sayings</h2>
    {intro}{"".join(groups)}
  </section>
'''

    body = f"""
<article class="person">
  <p class="crumb"><a href="../index.html">&larr; Timeline</a></p>
  <h1>{esc(person["name"])}</h1>
  <p class="lifespan">{lifespan(person)} &middot; <span class="era">{esc(person["era"])}</span></p>
  {aka}{role}
  <p class="summary">{esc(person["summary"])}</p>
  <dl class="life">
    {life_row("Born", born)}
    {life_row("Died", died)}
  </dl>

  <section>
    <h2>What they did</h2>
    {render_bullets(person["accomplishments"], numbers)}
  </section>
{events_html}{sayings_html}{render_victims(person, numbers, person["name"].split()[-1])}{persecution_html}{render_key_dates(dates, numbers)}{render_sources(person)}</article>
"""
    notice = ai_notice(person.get("ai_generated", "full"))
    return page(f'{person["name"]} — Church History', body, root="../", notice=notice)


# ---------------------------------------------------------------- event page

def render_event(event, people=()):
    numbers = source_numbers(event)
    start, end = event["start"], event.get("end")
    people_by_slug = {p["slug"]: p for p in people}

    def when_row(label, when):
        return (f'<div><dt>{label}</dt><dd>{esc(when.get("date") or life_year(when))}'
                f'{cite(when["sources"], numbers)}</dd></div>')

    rows = when_row("Began" if end else "Date", start)
    if end:
        rows += when_row("Ended", end)
    if event.get("place"):
        rows += f'<div><dt>Place</dt><dd>{esc(event["place"])}</dd></div>'

    background = ""
    if event.get("background"):
        background = f'''
  <section>
    <h2>Background</h2>
    {render_bullets(event["background"], numbers)}
  </section>
'''

    participants = ""
    if event.get("participants"):
        lis = []
        for part in event["participants"]:
            name = esc(part["name"])
            if part.get("person") in people_by_slug:
                name = f'<a href="../people/{esc(part["person"])}.html">{name}</a>'
            lis.append(f'<li><strong>{name}</strong> <span class="note">{esc(part["role"])}</span></li>')
        participants = f'''
  <section>
    <h2>Key participants</h2>
    <ul class="participants">
{chr(10).join(lis)}
    </ul>
  </section>
'''

    condemnations = ""
    if event.get("condemnations") is not None:
        condemnations = f'''
  <section>
    <h2>Condemnations and excommunications</h2>
    {render_condemnations(event["condemnations"], event.get("condemnations_note"), numbers, "Condemned at or by this event")}
  </section>
'''

    persecution = ""
    if event.get("persecution") or event.get("persecution_note"):
        note = event.get("persecution_note")
        persecution = f'''
  <section>
    <h2>Violence, persecution, and who was responsible</h2>
    {f'<p class="intro">{esc(note)}</p>' if note else ""}{"".join(render_incident(ev, numbers) for ev in event.get("persecution", []))}
  </section>
'''

    dates = [{"year": start["year"], "label": "Began" if end else event["name"], "sources": start["sources"],
              "kind": "life", "circa": start.get("circa")}]
    dates += [dict(kd, kind="event") for kd in event.get("key_dates", [])]
    if end:
        dates.append({"year": end["year"], "label": "Ended", "sources": end["sources"], "kind": "life",
                      "circa": end.get("circa")})
    dates.sort(key=lambda e: (e["year"], e["label"] == "Ended"))
    key_dates = render_key_dates(dates, numbers) if len(dates) > 1 else ""

    body = f"""
<article class="person event-page">
  <p class="crumb"><a href="../index.html">&larr; Timeline</a></p>
  <p class="event-kind">Event &middot; {EVENT_TYPES[event["event_type"]]}</p>
  <h1>{esc(event["name"])}</h1>
  <p class="lifespan">{event_span(event)} &middot; <span class="era">{esc(event["era"])}</span></p>
  {f'<p class="aka">Also known as {esc(event["also_known_as"])}</p>' if event.get("also_known_as") else ""}
  <p class="summary">{esc(event["summary"])}</p>
  <dl class="life">
    {rows}
  </dl>
{background}
  <section>
    <h2>What happened</h2>
    {render_bullets(event["happened"], numbers)}
  </section>
{participants}
  <section>
    <h2>Outcomes and significance</h2>
    {render_bullets(event["outcomes"], numbers)}
  </section>
{condemnations}{render_victims(event, numbers, event.get("victims_subject", "it"))}{persecution}{key_dates}{render_sources(event)}</article>
"""
    notice = ai_notice(event.get("ai_generated", "full"))
    return page(f'{event["name"]} — Church History', body, root="../", notice=notice)


# ---------------------------------------------------------------- timeline and home page

def tick_step(span):
    for step in (10, 25, 50, 100, 200, 500):
        if span / step <= 10:
            return step
    return 1000


def span_bounds(spans):
    """Axis range covering (start, end) year pairs, rounded out to whole tick steps."""
    start = min(s for s, _ in spans)
    end = max(e for _, e in spans)
    step = tick_step(max(end - start, 1))
    start = (start // step) * step
    end = -(-end // step) * step
    if end == start:
        end += step
    return start, end, tick_step(end - start)


def timeline_bounds(people):
    return span_bounds([(p["born"]["year"], p["died"]["year"]) for p in people])


def timeline_items(people, events):
    """People and events as one chronological list of timeline rows."""
    items = []
    for p in people:
        items.append({
            "kind": "person", "name": p["name"], "era": p["era"], "href": f'people/{p["slug"]}.html',
            "start": p["born"]["year"], "end": p["died"]["year"], "sub": lifespan(p), "dates": p["key_dates"],
        })
    for e in events:
        items.append({
            "kind": "event", "name": e["name"], "era": e["era"], "href": f'events/{e["slug"]}.html',
            "start": e["start"]["year"], "end": e.get("end", e["start"])["year"],
            "sub": f'{event_span(e)} &middot; {EVENT_TYPES[e["event_type"]]}', "dates": e.get("key_dates", []),
        })
    return sorted(items, key=lambda i: (i["start"], i["kind"] == "event", i["name"]))


# Re-lays out the timeline when an era button is pressed. The server-rendered
# positions are the "All" view, so the page still works without JavaScript.
TIMELINE_JS = """
<script>
(function () {
  var tl = document.querySelector('.timeline');
  var buttons = document.querySelectorAll('.zoom button');
  function fmt(y) { return y < 0 ? (-y) + ' BC' : String(y); }
  function layout(start, end, step) {
    var span = end - start;
    function pct(y) { return ((y - start) / span * 100) + '%'; }
    var marks = [];
    for (var y = start; y <= end; y += step) marks.push(y);
    tl.querySelector('.axis .track').innerHTML = marks.map(function (y) {
      return '<span class="tick" style="left:' + pct(y) + '">' + fmt(y) + '</span>';
    }).join('');
    tl.querySelectorAll('.row:not(.axis)').forEach(function (row) {
      var b = +row.dataset.born, d = +row.dataset.died;
      row.hidden = d < start || b > end;
      var track = row.querySelector('.track');
      track.querySelectorAll('.grid').forEach(function (g) { g.remove(); });
      track.insertAdjacentHTML('afterbegin', marks.map(function (y) {
        return '<span class="grid" style="left:' + pct(y) + '"></span>';
      }).join(''));
      var bar = row.querySelector('.bar');
      bar.style.left = pct(b);
      bar.style.width = Math.max((d - b) / span * 100, 0.4) + '%';
      row.querySelectorAll('.dot').forEach(function (dot) { dot.style.left = pct(+dot.dataset.year); });
    });
  }
  buttons.forEach(function (btn) {
    btn.addEventListener('click', function () {
      buttons.forEach(function (b) { b.setAttribute('aria-pressed', b === btn); });
      layout(+btn.dataset.start, +btn.dataset.end, +btn.dataset.step);
    });
  });
})();
</script>"""


def render_timeline(people, events=()):
    items = timeline_items(people, events)
    start, end, step = span_bounds([(i["start"], i["end"]) for i in items])
    span = end - start

    def pct(year):
        return f"{(year - start) / span * 100:.3f}%"

    marks = range(start, end + 1, step)
    ticks = "".join(f'<span class="tick" style="left:{pct(y)}">{format_year(y)}</span>' for y in marks)
    gridlines = "".join(f'<span class="grid" style="left:{pct(y)}"></span>' for y in marks)

    eras = []
    for i in items:
        if i["era"] not in eras:
            eras.append(i["era"])
    buttons = [f'<button type="button" aria-pressed="true" data-start="{start}" data-end="{end}" data-step="{step}">All</button>']
    if len(eras) > 1:
        for era in eras:
            e_start, e_end, e_step = span_bounds([(i["start"], i["end"]) for i in items if i["era"] == era])
            buttons.append(f'<button type="button" aria-pressed="false" data-start="{e_start}" '
                           f'data-end="{e_end}" data-step="{e_step}">{esc(era)}</button>')

    rows = []
    for i in items:
        b, d = i["start"], i["end"]
        width = f"{max((d - b) / span * 100, 0.4):.3f}%"
        dots = "".join(
            f'<a class="dot" href="{esc(i["href"])}" data-year="{kd["year"]}" style="left:{pct(kd["year"])}" '
            f'data-tip="{format_year(kd["year"], kd.get("circa"))}: {esc(kd["label"])}" '
            f'aria-label="{format_year(kd["year"])}: {esc(kd["label"])}"></a>'
            for kd in i["dates"]
        )
        tag = '<span class="event-tag">Event</span>' if i["kind"] == "event" else ""
        what = "dates" if i["kind"] == "event" else "lifespan"
        rows.append(f"""
    <div class="row {i["kind"]}-row" data-born="{b}" data-died="{d}">
      <a class="row-name" href="{esc(i["href"])}">{tag}{esc(i["name"])}<small>{i["sub"]}</small></a>
      <div class="track">{gridlines}
        <a class="bar" href="{esc(i["href"])}" style="left:{pct(b)};width:{width}"
           data-tip="{esc(i["name"])} ({i["sub"]})" aria-label="{esc(i["name"])} {what}"></a>{dots}
      </div>
    </div>""")

    return f"""
<div class="zoom" role="group" aria-label="Zoom timeline to an era">{"".join(buttons)}</div>
<section class="timeline" aria-label="Timeline of people and events">
  <div class="row axis"><span class="row-name"></span><div class="track">{ticks}</div></div>
  {"".join(rows)}
</section>
{TIMELINE_JS}"""


def render_index(people, events=()):
    if not people:
        return page("Church History", "<h1>Church History</h1><p>No people added yet.</p>")

    entries = []
    for p in people:
        link = f'<a href="people/{esc(p["slug"])}.html">{esc(p["name"])}</a>'
        entries.append((p["born"]["year"], 0, p["name"], link, "Born", p["born"].get("circa", False), "life"))
        for kd in p["key_dates"]:
            entries.append((kd["year"], 1, p["name"], link, kd["label"], kd.get("circa", False), "event"))
        entries.append((p["died"]["year"], 2, p["name"], link, "Died", p["died"].get("circa", False), "life"))
    for e in events:
        link = f'<span class="event-tag">Event</span><a href="events/{esc(e["slug"])}.html">{esc(e["name"])}</a>'
        end = e.get("end")
        entries.append((e["start"]["year"], 1, e["name"], link, "Began" if end else EVENT_TYPES[e["event_type"]],
                        e["start"].get("circa", False), "evt"))
        for kd in e.get("key_dates", []):
            entries.append((kd["year"], 1, e["name"], link, kd["label"], kd.get("circa", False), "evt"))
        if end and end["year"] != e["start"]["year"]:
            entries.append((end["year"], 1, e["name"], link, "Ended", end.get("circa", False), "evt"))
    entries.sort(key=lambda x: (x[0], x[1], x[2]))

    table_rows = "\n".join(
        f'<tr class="{kind}"><td class="year">{format_year(year, circa)}</td>'
        f'<td>{link}</td><td>{esc(label)}</td></tr>'
        for year, _, _, link, label, circa, kind in entries
    )

    cards = "\n".join(
        f'<li><a href="people/{esc(p["slug"])}.html"><strong>{esc(p["name"])}</strong>'
        f'<span>{lifespan(p)} &middot; {esc(p["era"])}</span>'
        f'<p>{esc(p["summary"])}</p></a></li>'
        for p in people
    )
    event_cards = ""
    if events:
        cards_html = "\n".join(
            f'<li><a href="events/{esc(e["slug"])}.html"><strong>{esc(e["name"])}</strong>'
            f'<span>{event_span(e)} &middot; {EVENT_TYPES[e["event_type"]]} &middot; {esc(e["era"])}</span>'
            f'<p>{esc(e["summary"])}</p></a></li>'
            for e in events
        )
        event_cards = f"""
<section>
  <h2>Events</h2>
  <ul class="cards event-cards">
{cards_html}
  </ul>
</section>
"""

    n_people = f'{len(people)} {"person" if len(people) == 1 else "people"}'
    n_events = f' and {len(events)} {"event" if len(events) == 1 else "events"}' if events else ""
    body = f"""
<h1>Timeline</h1>
<p class="intro">{n_people}{n_events} from church history. Bars show each lifespan or event; dots mark key dates (hover for details). Events are marked in a different color. Zoom to an era to spread them out, or select a name for the full page with sources.</p>
{render_timeline(people, events)}

<section>
  <h2>All key dates</h2>
  <div class="table-wrap">
  <table class="events">
    <thead><tr><th>Year</th><th>Person or event</th><th>What happened</th></tr></thead>
    <tbody>
{table_rows}
    </tbody>
  </table>
  </div>
</section>
{event_cards}
<section>
  <h2>People</h2>
  <ul class="cards">
{cards}
  </ul>
</section>
"""
    return page("Church History", body)


# ---------------------------------------------------------------- main

def build(people, site_dir=SITE_DIR, events=()):
    for sub in ("people", "events"):
        out = site_dir / sub
        if out.exists():
            shutil.rmtree(out)
        out.mkdir(parents=True)
    shutil.copy(STATIC_DIR / "style.css", site_dir / "style.css")
    (site_dir / "index.html").write_text(render_index(people, events), encoding="utf-8")
    for person in people:
        (site_dir / "people" / f'{person["slug"]}.html').write_text(render_person(person, events), encoding="utf-8")
    for event in events:
        (site_dir / "events" / f'{event["slug"]}.html').write_text(render_event(event, people), encoding="utf-8")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--check", action="store_true", help="validate data without writing the site")
    args = parser.parse_args(argv)
    try:
        people = load_people()
        events = load_events({p["slug"] for p in people})
    except ValidationError as exc:
        print("Validation failed:\n" + str(exc), file=sys.stderr)
        return 1
    if args.check:
        print(f"OK: {len(people)} people and {len(events)} events valid")
        return 0
    build(people, events=events)
    print(f"Built {len(people)} people and {len(events)} events into {SITE_DIR.relative_to(ROOT)}/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
