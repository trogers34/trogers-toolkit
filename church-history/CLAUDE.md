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

## Persecution, arrests, and executions (required for every person)

Every person needs a `persecution` list and a `persecution_note`. The user wants the full
record, whoever was responsible and whatever tradition they belonged to.

- Cover every recorded arrest, trial, imprisonment, excommunication, ban, exile, attack,
  and execution suffered by the person. Also cover persecution of their close associates
  or followers when it was aimed at the person's work (e.g. burning of their readers).
- For each incident, name everyone responsible: popes, bishops, priests, pastors,
  theologians, kings, emperors, magistrates, councils, mobs, informers. Give each one's
  role and the jurisdiction or institution they acted under, and type them as `church`,
  `state`, `individual`, or `group`.
- Record protectors in `defended_by` when they shaped the outcome.
- Every person also needs `excommunications` and `excommunication_note`. List every
  excommunication, anathema, or condemnation as a heretic, including posthumous ones:
  who issued it, under what authority, why, and whether it was ever lifted or reversed
  (note later apologies or expressions of regret, and say whether they formally revoked
  anything). If the person was never excommunicated, say so explicitly in
  `excommunication_note`, so readers know it was checked.
- Say plainly where responsibility is unknown or only suspected, and who suspects it.
  If a party had no recorded role (e.g. no direct papal involvement), say so in the summary.
- If the person was never arrested or persecuted, say so in `persecution_note` and leave
  the list empty, or include only incidents that genuinely threatened them.
- Stay neutral: describe who did what under which authority, without editorializing.

## Content guidelines

- 6–10 accomplishments, each one or two sentences, most significant first.
- 5–10 key dates: turning points and major works, not every event. They must fall within
  the lifespan (the build enforces this).
- `era` is one of `Early Church` (to c. 600), `Medieval` (c. 600–1500), `Reformation`
  (c. 1500–1650), `Modern` (after c. 1650). Reuse existing era names exactly, since each
  distinct era becomes a zoom button on the timeline.
