# Church History site: instructions for Claude

When the user names a person from church history, add them to the site:

1. Create `people/<slug>.json` (lowercase, hyphenated name). Match the structure of the
   existing files; the field reference is in `README.md`.
2. Run `python3 build.py`, then `python3 -m unittest discover tests`. Both must pass.
3. Commit the JSON file and the regenerated `site/` together.

## Sourcing rules

- Every accomplishment, key date, birth, and death needs at least one source.
- Cite sources that actually exist: the person's own writings or an early biography
  (primary), standard scholarly biographies (scholarly), and Encyclopaedia Britannica or
  similar (reference). Aim for at least one of each type when they exist.
- Only cite a work that supports the specific claim. Never invent titles, authors,
  page numbers, or URLs. If you can't verify a URL, leave `url` out.
- Where scholars disagree on a date, use `circa: true` and/or note the range in the label
  (e.g. "c. 397–400"). Where calendars differ, say so (e.g. Old Style / New Style).
- Write neutrally and descriptively. Don't judge which tradition was right.

## Content guidelines

- 6–10 accomplishments, each one or two sentences, most significant first.
- 5–10 key dates: turning points and major works, not every event. They must fall within
  the lifespan (the build enforces this).
- `era` is one of `Early Church` (to c. 600), `Medieval` (c. 600–1500), `Reformation`
  (c. 1500–1650), `Modern` (after c. 1650). Reuse existing era names exactly, since each
  distinct era becomes a zoom button on the timeline.
