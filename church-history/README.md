# Church History

A small static website of people from church history. Each person gets a page with
bullet points of what they did, every point tied to a cited source. The home page
is a timeline of everyone: lifespans, key dates, and a chronological table.

## How it works

```
people/<slug>.json   one data file per person (the only thing you edit)
static/style.css     site styles
build.py             validates the data and generates the site
site/                generated HTML (committed so it can be opened or hosted directly)
tests/               unit tests for the build
```

```bash
python3 build.py           # validate + regenerate site/
python3 build.py --check   # validate only
python3 -m unittest discover tests
```

Open `site/index.html` in a browser. No server or third-party packages are needed
(Python 3.8+).

The build fails if a bullet or date has no source, cites a source id that isn't
listed, or has a key date outside the person's lifespan.

## Adding a person

Ask Claude: *"Add Athanasius of Alexandria to the church history site."* Claude
follows the rules in [`CLAUDE.md`](CLAUDE.md), writes `people/<slug>.json`, rebuilds,
and commits.

To add one by hand, copy an existing file in `people/` and edit it. Field reference:

| Field | Notes |
|---|---|
| `name`, `slug` | `slug` must match the file name (`martin-luther` → `martin-luther.json`) |
| `also_known_as`, `role` | optional |
| `era` | groups people into the timeline zoom buttons: `Early Church`, `Medieval`, `Reformation`, `Modern` |
| `summary` | one sentence |
| `born` / `died` | `year` (integer; negative for BC), `date` (display text), `place`, `sources`, optional `circa: true` |
| `key_dates` | `year`, `label`, `sources`, optional `circa: true`. Shown on the home-page timeline |
| `accomplishments` | `text`, `sources`. The bullet points on the person's page |
| `sayings` | optional. `{"original": [...], "popularized": [...]}`, each item `phrase`, `reference`, `note`, `sources`. Shown as "Words and sayings". `sayings_intro` adds a lead-in paragraph |
| `sources` | `id`, `type` (`primary` / `scholarly` / `reference`), `citation`, optional `url` |
