# Church History

A small static website of people and events from church history. Each person gets a page
with bullet points of what they did, and each event a page on what happened, every point
tied to a cited source. The home page is one timeline of everyone and every event:
lifespans, event dates, key dates, and a chronological table.

## How it works

```
people/<slug>.json   one data file per person
events/<slug>.json   one data file per event
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

The build fails if a person has no persecution or excommunication section, if a persecution incident doesn't say who was responsible, if a bullet or date has no source, cites a source id that isn't
listed, or has a key date outside the person's lifespan.

## Publishing

The site is published with GitHub Pages at
**https://trogers34.github.io/trogers-toolkit/**.

`.github/workflows/church-history-pages.yml` runs the tests, rebuilds the site, and
deploys it on every push to `master` that touches `church-history/`. Pull requests run
the tests only. A failing test blocks the deploy, so the live site only changes when
the data is valid.

One-time setup (repo admin): **Settings → Pages → Build and deployment → Source:
GitHub Actions**.

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
| `born` / `died` | `year` (integer; negative for BC), `date` (display text), `place`, `sources`, optional `circa: true`. `died` also needs `cause` (how they died; "Unknown" if it is). The home page shows date, place, and cause |
| `key_dates` | `year`, `label`, `sources`, optional `circa: true`. Shown on the home-page timeline |
| `accomplishments` | `text`, `sources`. The bullet points on the person's page |
| `sayings` | optional. `{"original": [...], "popularized": [...], "misattributed": [...]}`, each item `phrase`, `reference`, `note`, `sources`. Shown as "Words and sayings". `sayings_intro` adds a lead-in paragraph |
| `persecution` | required list (may be empty). Each item: `year` and/or `date`, `title`, `summary`, `responsible` (each `name`, `role`, `jurisdiction`, `type`: `church` / `state` / `individual` / `group`), optional `defended_by` (`name`, `role`), `outcome`, `sources` |
| `persecution_note` | short overview of the person's arrests, trials, and persecution; required if `persecution` is empty (e.g. "None recorded") |
| `excommunications` | required list (may be empty). Each item: `date`, `by`, `authority`, `reason`, `status` (e.g. "Never lifted"), `sources`. Shown as a table at the top of the persecution section |
| `excommunication_note` | overview of the person's excommunications; required if `excommunications` is empty (e.g. "Never excommunicated") |
| `ai_generated` | optional: `full` (default) or `partial`. Controls the AI notice at the top of the page; set `partial` once a person has reviewed and edited the page |
| `victims` | optional, with `victims_title` and `victims_intro`. People executed whose deaths are linked to this person. Each item: `name`, `executed`, `condemned_by`, `allegation`, `verification` (`execution` and `link`: `verified` / `partial` / `disputed` / `unverified`), `verification_note`, `links` (`label`, `url`), `sources` |
| `sources` | `id`, `type` (`primary` / `scholarly` / `reference`), `citation`, optional `url` |

## Adding an event

Copy an existing file in `events/`. Fields shared with people (`sources`, `key_dates`,
`persecution`, `victims`, `ai_generated`) work the same way. Event key dates must fall
between `start` and `end`.

| Field | Notes |
|---|---|
| `name`, `slug`, `also_known_as`, `era`, `summary` | as for people |
| `event_type` | `council`, `schism`, `persecution`, `massacre`, `trial`, `war`, `revival`, `document`, `assembly`, `denomination` (a church's beginnings and splits), `other` |
| `start` / `end` | `year`, `date`, `label` (short summary of what happened then; required), `sources`, optional `circa`. `end` is optional for one-day events |
| `place` | optional |
| `background`, `happened`, `outcomes` | bullet lists of `text` and `sources`; `happened` and `outcomes` are required |
| `participants` | optional. `name`, `role`, and `person` (a person's slug) to link both pages |
| `condemnations` | optional, same fields as `excommunications`, with `condemnations_note` |
| `persecution`, `persecution_note` | optional, same format as for people |
| `victims`, `victims_title`, `victims_intro`, `victims_subject` | optional; `victims_subject` replaces the person's name in "What … is accused of" |
