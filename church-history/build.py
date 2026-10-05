#!/usr/bin/env python3
"""Build the Church History site from the JSON files in people/.

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
SITE_DIR = ROOT / "site"
STATIC_DIR = ROOT / "static"

REQUIRED_FIELDS = ["name", "slug", "era", "summary", "born", "died",
                   "key_dates", "accomplishments", "persecution", "excommunications", "sources"]
PARTY_TYPES = {"church": "Church", "state": "State", "individual": "Individual", "group": "Group"}
SOURCE_TYPES = {"primary", "scholarly", "reference"}
SAYING_CATEGORIES = {
    "original": ("Original",
                 "First recorded in English in their writing, or first worded this way by them."),
    "popularized": ("Popularized",
                    "Already in English before them, but their use made it widely known."),
}


class ValidationError(Exception):
    pass


def esc(text):
    return html.escape(str(text), quote=True)


# ---------------------------------------------------------------- loading

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


def validate_person(person, file_stem):
    errors = []
    for field in REQUIRED_FIELDS:
        if field not in person:
            errors.append(f"missing required field '{field}'")
    if errors:
        return errors

    if person["slug"] != file_stem:
        errors.append(f"slug '{person['slug']}' must match file name '{file_stem}.json'")

    source_ids = set()
    for src in person["sources"]:
        if not src.get("id") or not src.get("citation"):
            errors.append(f"source needs 'id' and 'citation': {src}")
        if src.get("type") not in SOURCE_TYPES:
            errors.append(f"source '{src.get('id')}' type must be one of {sorted(SOURCE_TYPES)}")
        if src.get("id") in source_ids:
            errors.append(f"duplicate source id '{src.get('id')}'")
        source_ids.add(src.get("id"))

    def check_refs(where, item):
        refs = item.get("sources") or []
        if not refs:
            errors.append(f"{where} has no sources")
        for ref in refs:
            if ref not in source_ids:
                errors.append(f"{where} cites unknown source '{ref}'")

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
    for i, ex in enumerate(person["excommunications"]):
        where = f"excommunications[{i}]"
        for field in ("date", "by", "authority", "reason", "status"):
            if not ex.get(field):
                errors.append(f"{where} needs '{field}'")
        check_refs(where, ex)

    if not person["persecution"] and not person.get("persecution_note"):
        errors.append("'persecution' is empty: add 'persecution_note' saying none is recorded")
    for i, ev in enumerate(person["persecution"]):
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


# ---------------------------------------------------------------- rendering

def format_year(year, circa=False):
    text = f"{-year} BC" if year < 0 else str(year)
    return f"c. {text}" if circa else text


def life_year(life):
    return format_year(life["year"], life.get("circa", False))


def lifespan(person):
    return f'{life_year(person["born"])}&ndash;{life_year(person["died"])}'


def page(title, body, root=""):
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
  <span class="tagline">People, dates, and sources</span>
</header>
<main>
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


def render_person(person):
    numbers = {s["id"]: i for i, s in enumerate(person["sources"], start=1)}
    born, died = person["born"], person["died"]

    aka = f'<p class="aka">Also known as {esc(person["also_known_as"])}</p>' if person.get("also_known_as") else ""
    role = f'<p class="role">{esc(person["role"])}</p>' if person.get("role") else ""

    def life_row(label, life):
        place = f' &middot; {esc(life["place"])}' if life.get("place") else ""
        return (f'<div><dt>{label}</dt><dd>{esc(life.get("date") or life_year(life))}'
                f'{place}{cite(life["sources"], numbers)}</dd></div>')

    events = [{"year": born["year"], "label": "Born", "sources": born["sources"], "kind": "life", "circa": born.get("circa")}]
    events += [dict(kd, kind="event") for kd in person["key_dates"]]
    events.append({"year": died["year"], "label": "Died", "sources": died["sources"], "kind": "life", "circa": died.get("circa")})
    events.sort(key=lambda e: (e["year"], e["kind"] != "life" or e["label"] == "Died"))

    key_dates = "\n".join(
        f'<li class="{e["kind"]}"><span class="year">{format_year(e["year"], e.get("circa"))}</span>'
        f'<span class="label">{esc(e["label"])}{cite(e["sources"], numbers)}</span></li>'
        for e in events
    )
    accomplishments = "\n".join(
        f'<li>{esc(a["text"])}{cite(a["sources"], numbers)}</li>' for a in person["accomplishments"]
    )

    def persecution_event(ev):
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

    ex_rows = "\n".join(
        f'<tr><td class="nowrap">{esc(ex["date"])}</td><td><strong>{esc(ex["by"])}</strong></td>'
        f'<td>{esc(ex["authority"])}</td><td>{esc(ex["reason"])}{cite(ex["sources"], numbers)}</td>'
        f'<td>{esc(ex["status"])}</td></tr>'
        for ex in person["excommunications"]
    )
    ex_note = person.get("excommunication_note")
    ex_table = f'''
      <div class="table-wrap">
      <table class="responsible excomm">
        <thead><tr><th>Date</th><th>By</th><th>Authority</th><th>Reason</th><th>Status</th></tr></thead>
        <tbody>
{ex_rows}
        </tbody>
      </table>
      </div>''' if ex_rows else ""
    excommunications_html = f'''
    <div class="excommunications">
      <h3>Excommunications</h3>
      {f'<p>{esc(ex_note)}</p>' if ex_note else ""}{ex_table}
    </div>'''

    note = person.get("persecution_note")
    persecution_html = f'''
  <section>
    <h2>Persecution, arrests, and executions</h2>
    {f'<p class="intro">{esc(note)}</p>' if note else ""}{excommunications_html}{"".join(persecution_event(ev) for ev in person["persecution"])}
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

    def source_item(s):
        text = esc(s["citation"])
        if s.get("url"):
            text += f' <a href="{esc(s["url"])}" rel="noopener">{esc(s["url"])}</a>'
        return (f'<li id="src-{esc(s["id"])}"><span class="src-type {esc(s["type"])}">'
                f'{esc(s["type"])}</span> {text}</li>')

    sources = "\n".join(source_item(s) for s in person["sources"])

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
    <ul class="accomplishments">
{accomplishments}
    </ul>
  </section>
{sayings_html}{persecution_html}
  <section>
    <h2>Key dates</h2>
    <ol class="key-dates">
{key_dates}
    </ol>
  </section>

  <section>
    <h2>References</h2>
    <ol class="sources">
{sources}
    </ol>
  </section>
</article>
"""
    return page(f'{person["name"]} — Church History', body, root="../")


def tick_step(span):
    for step in (10, 25, 50, 100, 200, 500):
        if span / step <= 10:
            return step
    return 1000


def timeline_bounds(people):
    """Year range for the axis, rounded out to whole tick steps."""
    start = min(p["born"]["year"] for p in people)
    end = max(p["died"]["year"] for p in people)
    step = tick_step(max(end - start, 1))
    start = (start // step) * step
    end = -(-end // step) * step
    if end == start:
        end += step
    return start, end, tick_step(end - start)


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


def render_timeline(people):
    start, end, step = timeline_bounds(people)
    span = end - start

    def pct(year):
        return f"{(year - start) / span * 100:.3f}%"

    marks = range(start, end + 1, step)
    ticks = "".join(f'<span class="tick" style="left:{pct(y)}">{format_year(y)}</span>' for y in marks)
    gridlines = "".join(f'<span class="grid" style="left:{pct(y)}"></span>' for y in marks)

    eras = []
    for p in people:
        if p["era"] not in eras:
            eras.append(p["era"])
    buttons = [f'<button type="button" aria-pressed="true" data-start="{start}" data-end="{end}" data-step="{step}">All</button>']
    if len(eras) > 1:
        for era in eras:
            e_start, e_end, e_step = timeline_bounds([p for p in people if p["era"] == era])
            buttons.append(f'<button type="button" aria-pressed="false" data-start="{e_start}" '
                           f'data-end="{e_end}" data-step="{e_step}">{esc(era)}</button>')

    rows = []
    for p in people:
        b, d = p["born"]["year"], p["died"]["year"]
        width = f"{max((d - b) / span * 100, 0.4):.3f}%"
        dots = "".join(
            f'<a class="dot" href="people/{esc(p["slug"])}.html" data-year="{kd["year"]}" style="left:{pct(kd["year"])}" '
            f'data-tip="{format_year(kd["year"], kd.get("circa"))}: {esc(kd["label"])}" '
            f'aria-label="{format_year(kd["year"])}: {esc(kd["label"])}"></a>'
            for kd in p["key_dates"]
        )
        rows.append(f"""
    <div class="row" data-born="{b}" data-died="{d}">
      <a class="row-name" href="people/{esc(p["slug"])}.html">{esc(p["name"])}<small>{lifespan(p)}</small></a>
      <div class="track">{gridlines}
        <a class="bar" href="people/{esc(p["slug"])}.html" style="left:{pct(b)};width:{width}"
           data-tip="{esc(p["name"])} ({lifespan(p)})" aria-label="{esc(p["name"])} lifespan"></a>{dots}
      </div>
    </div>""")

    return f"""
<div class="zoom" role="group" aria-label="Zoom timeline to an era">{"".join(buttons)}</div>
<section class="timeline" aria-label="Lifespan timeline">
  <div class="row axis"><span class="row-name"></span><div class="track">{ticks}</div></div>
  {"".join(rows)}
</section>
{TIMELINE_JS}"""


def render_index(people):
    if not people:
        return page("Church History", "<h1>Church History</h1><p>No people added yet.</p>")

    events = []
    for p in people:
        events.append((p["born"]["year"], 0, p, "Born", p["born"].get("circa", False), "life"))
        for kd in p["key_dates"]:
            events.append((kd["year"], 1, p, kd["label"], kd.get("circa", False), "event"))
        events.append((p["died"]["year"], 2, p, "Died", p["died"].get("circa", False), "life"))
    events.sort(key=lambda e: (e[0], e[1], e[2]["name"]))

    event_rows = "\n".join(
        f'<tr class="{kind}"><td class="year">{format_year(year, circa)}</td>'
        f'<td><a href="people/{esc(p["slug"])}.html">{esc(p["name"])}</a></td>'
        f'<td>{esc(label)}</td></tr>'
        for year, _, p, label, circa, kind in events
    )

    cards = "\n".join(
        f'<li><a href="people/{esc(p["slug"])}.html"><strong>{esc(p["name"])}</strong>'
        f'<span>{lifespan(p)} &middot; {esc(p["era"])}</span>'
        f'<p>{esc(p["summary"])}</p></a></li>'
        for p in people
    )

    body = f"""
<h1>Timeline</h1>
<p class="intro">{len(people)} {"person" if len(people) == 1 else "people"} from church history. Bars show each lifespan; dots mark key events (hover for details). Zoom to an era to spread them out, or select a name for the full page with sources.</p>
{render_timeline(people)}

<section>
  <h2>All key dates</h2>
  <div class="table-wrap">
  <table class="events">
    <thead><tr><th>Year</th><th>Person</th><th>Event</th></tr></thead>
    <tbody>
{event_rows}
    </tbody>
  </table>
  </div>
</section>

<section>
  <h2>People</h2>
  <ul class="cards">
{cards}
  </ul>
</section>
"""
    return page("Church History", body)


# ---------------------------------------------------------------- main

def build(people, site_dir=SITE_DIR):
    people_out = site_dir / "people"
    if people_out.exists():
        shutil.rmtree(people_out)
    people_out.mkdir(parents=True)
    shutil.copy(STATIC_DIR / "style.css", site_dir / "style.css")
    (site_dir / "index.html").write_text(render_index(people), encoding="utf-8")
    for person in people:
        (people_out / f'{person["slug"]}.html').write_text(render_person(person), encoding="utf-8")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--check", action="store_true", help="validate data without writing the site")
    args = parser.parse_args(argv)
    try:
        people = load_people()
    except ValidationError as exc:
        print("Validation failed:\n" + str(exc), file=sys.stderr)
        return 1
    if args.check:
        print(f"OK: {len(people)} people valid")
        return 0
    build(people)
    print(f"Built {len(people)} people into {SITE_DIR.relative_to(ROOT)}/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
