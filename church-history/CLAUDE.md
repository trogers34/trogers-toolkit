# Church History site: instructions for Claude

This is the project's memory. Read it fully before changing anything. It holds every rule
the user has set and the list of everyone on the site.

## What the user wants (summary of their requests)

1. A web page for each person from church history the user names, with bullet points of
   what they did, each tied to a cited source.
2. A home page with a timeline of everyone: when they were born and died, and the very
   important dates of what they accomplished. Every person must appear on every view of the
   timeline (the "All" lifespan chart, their era's zoom view, the "All key dates" table,
   and the People cards). This happens automatically from `people/`; a test guards it.
3. The full history of each person, good, bad, or indifferent, whatever the user's own
   preferences and whatever tradition is involved. Include what the person did that
   reflects badly on them (e.g. Bucer's approval of Philip of Hesse's bigamy, Chrysostom's sermons against
   the Jews, Graham's 1972 Nixon remarks), stated neutrally and sourced.
4. All arrests, trials, executions, and persecution of each person, naming who was
   responsible (organizations, jurisdictions, popes, priests, pastors, rulers, anyone).
5. All excommunications for every person.
6. Famous words and sayings, categorized as original, popularized, or misattributed (first
   requested for Tyndale: "write out all the English sayings he came up with or
   popularized").
7. An AI-generated notice at the top of every page.
8. Publish every addition: commit, merge, and build each time, without asking.
9. When the user gives a list, skip anyone already on the site ("some duplicates so ignore").
10. Keep this project memory up to date after every commit: the people list, every new
    rule or preference the user states, and the change log at the bottom. A hook in
    `.claude/settings.json` checks each `git commit` and flags commits to `church-history/`
    that did not also update this file.
11. Events as well as people (councils, schisms, massacres, trials, assemblies), shown on
    the **same timeline as the people**, in date order, marked as events. Events follow the
    same rules as people: full history, everyone responsible for violence, condemnations,
    sources, and the AI notice.
12. All seven ecumenical councils (accepted by both the Catholic and Orthodox churches) are
    on the site; each is labeled with its number ("Third Ecumenical Council") in
    `also_known_as`. Keep the set complete.

## Adding a person

When the user names a person from church history, add them to the site:

1. Create `people/<slug>.json` (lowercase, hyphenated name). Match the structure of the
   existing files; the field reference is in `README.md`.
2. Add them to the "People on the site" list below (a test fails if you forget).
3. Run `python3 build.py`, then `python3 -m unittest discover tests`. Both must pass.
4. Commit the JSON file, the regenerated `site/`, and this file together.
5. Publish without asking first (the user's standing instruction): push the branch, open a
   pull request to `master`, wait for its "build" check to pass, merge it, then confirm the
   "Church History site" workflow run on `master` succeeded so the live site is rebuilt.
   If a check fails, fix it before merging. Report the live page URL when done.
6. If the user asks for a group (e.g. "the first generation of church fathers"), list the
   people for approval first, then add the ones approved. For anonymous writings, cover them
   on related people's pages rather than giving them their own page, unless asked.
7. If a name is ambiguous, pick the most likely church-history figure, say which one you
   chose, and offer to swap (e.g. "Nicolas" was taken as Nicholas of Myra; "Knox" as John
   Knox; "J Gresham Mencken" as J. Gresham Machen).

## Adding an event

When the user names an event, add `events/<slug>.json` (field reference in `README.md`) and
list it under "Events on the site" below in the same format as the entries there (a test checks it).
Then build, test, and publish exactly as for a person.

- Events appear automatically on the home-page timeline among the people (blue bars with an
  "Event" tag), in the era zoom views, the "All key dates" table, and the Events cards.
- Link people who took part with `participants[].person`; their pages then list the event
  under "Events" automatically. The build fails on a link to someone not on the site.
- Include `condemnations` (who was condemned, deposed, or excommunicated at or by the event,
  with status) and `persecution` incidents naming everyone responsible, as for people. Use
  `victims` for named people killed. Label tradition and disputed numbers as such.

Live site: https://trogers34.github.io/trogers-toolkit/

## People on the site

Keep this list in sync with `people/` (the tests check it). Grouped by era, oldest first.

**Early Church**
- Clement of Rome (`clement-of-rome`): Apostolic Father; most dates and his martyrdom are tradition
- Ignatius of Antioch (`ignatius-of-antioch`): Apostolic Father
- Papias of Hierapolis (`papias-of-hierapolis`): Apostolic Father
- Polycarp of Smyrna (`polycarp-of-smyrna`): Apostolic Father
- Hermas (`hermas`): Apostolic Father; author of the Shepherd
- Quadratus of Athens (`quadratus-of-athens`): Apostolic Father / earliest apologist
- Pseudo-Barnabas (`pseudo-barnabas`): anonymous author of the Epistle of Barnabas; lifespan placeholders
- Nicholas of Myra (`nicholas-of-myra`): the user wrote "Nicolas"; Nicholas of Myra was assumed
- Athanasius of Alexandria (`athanasius-of-alexandria`)
- John Chrysostom (`john-chrysostom`)
- Augustine of Hippo (`augustine-of-hippo`): starter example, added without a user request
- Leo the Great (`leo-the-great`)
- Gregory the Great (`gregory-the-great`)

**Medieval**
- Thomas Aquinas (`thomas-aquinas`)
- William of Ockham (`william-of-ockham`)
- John Wycliffe (`john-wycliffe`)
- Jan Hus (`jan-hus`)
- John Oldcastle (`john-oldcastle`)

**Reformation**
- Desiderius Erasmus (`desiderius-erasmus`)
- Thomas More (`thomas-more`): includes the list of people executed for heresy linked to him, with verification ratings
- Martin Luther (`martin-luther`): starter example
- Huldrych Zwingli (`huldrych-zwingli`): includes the Anabaptist executed in Zürich (Felix Manz), with ratings
- Thomas Cranmer (`thomas-cranmer`)
- Martin Bucer (`martin-bucer`)
- William Tyndale (`william-tyndale`): the user's first request; has the full Words and sayings list
- John Calvin (`john-calvin`): includes people executed in Geneva linked to him (Servetus etc.), with ratings
- John Knox (`john-knox`)
- Martin Chemnitz (`martin-chemnitz`)

**Modern**
- Jonathan Edwards (`jonathan-edwards`)
- George Whitefield (`george-whitefield`): the user wrote "Whitfield" (the pronunciation)
- John Wesley (`john-wesley`): starter example
- Charles Wesley (`charles-wesley`): has a Words and sayings list of hymn lines
- Charles Haddon Spurgeon (`charles-spurgeon`)
- J. Gresham Machen (`j-gresham-machen`): the user wrote "J Gresham Mencken"; Machen was assumed (H. L. Mencken wrote his obituary)
- G. K. Chesterton (`g-k-chesterton`): the user wrote "CK Chesterton"
- C. S. Lewis (`c-s-lewis`)
- Billy Graham (`billy-graham`)
- Chuck Smith (`chuck-smith`)
- R. C. Sproul (`r-c-sproul`)

## Events on the site

Keep this list in sync with `events/` (the tests check it). Oldest first.

- First Council of Nicaea, 325, 1st ecumenical (event: `council-of-nicaea`)
- First Council of Constantinople, 381, 2nd ecumenical (event: `first-council-of-constantinople`)
- Council of Ephesus, 431, 3rd ecumenical (event: `council-of-ephesus`)
- Council of Chalcedon, 451, 4th ecumenical (event: `council-of-chalcedon`)
- Second Council of Constantinople, 553, 5th ecumenical (event: `second-council-of-constantinople`)
- Third Council of Constantinople, 680–681, 6th ecumenical (event: `third-council-of-constantinople`)
- Second Council of Nicaea, 787, 7th ecumenical (event: `second-council-of-nicaea`)
- Great Schism of 1054 (event: `great-schism`)
- The Crusades, 1095–1291 (event: `the-crusades`): one event with each major crusade as a key date
- Council of Constance, 1414–1418 (event: `council-of-constance`)
- Ninety-five Theses / the Wittenberg door, 1517 (event: `ninety-five-theses`): the user asked for "Wittenberg Door"
- Diet of Worms, 1521 (event: `diet-of-worms`)
- Council of Trent, 1545–1563 (event: `council-of-trent`)
- St. Bartholomew's Day Massacre, 1572 (event: `st-bartholomews-day-massacre`)

## AI disclosure

Every page shows a notice at the top that it was generated by AI with Claude. Pages you
write are `full` by default; don't change that. Only set `"ai_generated": "partial"` when
the user says a person has reviewed or edited that page. Never remove the notice.

## Sourcing rules

- Every accomplishment, key date, birth, and death needs at least one source.
- Cite sources that actually exist: the person's own writings or an early biography
  (primary), standard scholarly biographies (scholarly), and Encyclopaedia Britannica or
  similar (reference). Aim for at least one of each type when they exist.
- Only cite a work that supports the specific claim. Never invent titles, authors,
  page numbers, or URLs. If you can't verify a URL, leave `url` out.
- Where scholars disagree on a date, use `circa: true` and/or note the range in the label
  (e.g. "c. 397–400"). Where calendars differ, say so (e.g. Old Style / New Style).
- Where the record is mostly tradition or legend (e.g. Nicholas of Myra), say so on the
  page and label each traditional claim as tradition.
- Write neutrally and descriptively. Don't judge which tradition was right.
- If you couldn't check sources online, tell the user which claims are least certain.

## Persecution, arrests, and executions (required for every person)

Every person needs a `persecution` list and a `persecution_note`. The user wants the full
record, whoever was responsible and whatever tradition they belonged to.

- Cover every recorded arrest, trial, imprisonment, excommunication, ban, exile, attack,
  and execution suffered by the person. Also cover persecution of their close associates
  or followers when it was aimed at the person's work (e.g. burning of their readers),
  and posthumous actions (exhumation, burning of remains, bans on their books).
- For each incident, name everyone responsible: popes, bishops, priests, pastors,
  theologians, kings, emperors, magistrates, councils, mobs, informers. Give each one's
  role and the jurisdiction or institution they acted under, and type them as `church`,
  `state`, `individual`, or `group`.
- Record protectors in `defended_by` when they shaped the outcome.
- Say plainly where responsibility is unknown or only suspected, and who suspects it.
  If a party had no recorded role (e.g. no direct papal involvement), say so in the summary.
- If the person was never arrested or persecuted, say so in `persecution_note` and leave
  the list empty, or include only incidents that genuinely threatened them. Mention
  opposition that fell short of persecution (e.g. denunciations) in the note.
- Stay neutral: describe who did what under which authority, without editorializing.

## Excommunications (required for every person)

Every person needs `excommunications` and `excommunication_note`. These are shown as a
table at the top of the persecution section.

- List every excommunication, anathema, deposition by a synod, or condemnation as a
  heretic, including posthumous ones and bans placing all their works on the Index.
- Give the date, who issued it, under what authority, why, and its status: whether it was
  ever lifted or reversed, and by whom. Note later apologies or expressions of regret and
  say whether they formally revoked anything.
- If the person was never excommunicated, say so explicitly in `excommunication_note`,
  so readers know it was checked.

## People executed and linked to a person (victims list)

When the user asks for the people someone is accused of having had executed (first
requested for Thomas More), add `victims_title`, `victims_intro`, and `victims`. List each
person who was actually executed, with the date, place, and manner; who condemned them;
and what the subject is accused of. Give two ratings: `execution` and `link` (the
subject's part), each `verified` (100%: records or the subject's own writings),
`partial`, `disputed`, or `unverified`, with a note explaining the rating. Include
links: a Wikipedia search link for the exact name and any source edition online.
Never invent page URLs.

## Words and sayings

When a person is known for famous words or phrases, add a `sayings` section. Use
`original` (first recorded in their writing), `popularized` (in use before them, made
famous by them), and `misattributed` (commonly credited to them but not in their
writings, such as legends, later paraphrases, or works named after them). Say where each
one is found. Be explicit that a list is a selection when it can't be complete.

## Content guidelines

- 6–10 accomplishments, each one or two sentences, most significant first.
- 5–10 key dates: turning points and major works, not every event. They must fall within
  the lifespan (the build enforces this). Posthumous events go in the persecution or
  excommunication sections instead.
- `era` is one of `Early Church` (to c. 600), `Medieval` (c. 600–1500), `Reformation`
  (c. 1500–1650), `Modern` (after c. 1650). Reuse existing era names exactly, since each
  distinct era becomes a zoom button on the timeline.

## Open questions for the user

- Whether to add a separate section on persecution these people supported or carried out
  against others (e.g. Augustine and the Donatists, Luther and the Anabaptists and Jews).
  Offered; no answer yet.

## Change log

Update this after every commit that changes the site. Newest first. PR numbers refer to
trogers34/trogers-toolkit.

- George Whitefield (his campaign for slavery in Georgia, the 1740 Charleston suspension, mobs)
  and G. K. Chesterton (Marconi affair and antisemitism charges; misattributed quotations).
  39 people, 14 events.
- **PR #69**: The Crusades (1095–1291) as one event, with violence on all sides and who was responsible
  (Rhineland 1096, Jerusalem 1099, Hattin 1187, York 1190, Acre 1191, Constantinople 1204,
  Béziers 1209, Antioch 1268). 37 people, 14 events.
- **PR #68**: John Calvin (Servetus, Gruet, and the 1545 plague trials in a victims list; linked to the Council
  of Trent) and Huldrych Zwingli (Felix Manz in a victims list; death at Kappel). 37 people, 13 events.
- **PR #67**: J. Gresham Machen (assumed for "J Gresham Mencken"), with his 1935–36 suspension from the
  PCUSA ministry. 35 people, 13 events.
- **PR #66**: Jonathan Edwards (including his slaveholding and the 1750 dismissal) and Charles Wesley
  (hymns, the Grace Murray episode, mob attacks). 34 people, 13 events.
- **PR #65**: Ninety-five Theses ("Wittenberg Door"), with the debate over whether they were actually
  posted on the door. 32 people, 13 events.
- **PR #64**: all seven ecumenical councils: added Constantinople I, Ephesus, Constantinople II,
  Constantinople III, Nicaea II; Nicaea renamed "First Council of Nicaea". 32 people, 12 events.
- **PR #63**: **Events** added, on the same timeline as people (user: "I would want these on the same
  timeline as the people"): event pages, Events section on linked people's pages, Events
  cards, events in the key-dates table. First 7: Nicaea, Chalcedon, the 1054 schism,
  Constance, Worms, Trent, St. Bartholomew's Day. 32 people, 7 events.
- Charles Haddon Spurgeon added (Surrey Gardens false alarm, sermons burned in the American South,
  Baptist Union censure in the Down-Grade Controversy). 32 people.
- **Memory upkeep**: rule to update this file after every commit; a PostToolUse hook
  (`.claude/hooks/check-memory-updated.sh`) flags commits to `church-history/` that skip it;
  this change log started.
- **PR #61**: the Apostolic Fathers (Clement of Rome, Ignatius, Papias, Polycarp, Hermas,
  Quadratus, Pseudo-Barnabas); rule to list group requests for approval first. 31 people.
- **PR #60**: Thomas More, with the reusable `victims` section (executed people linked to a
  person, with execution and link verification ratings and links). 24 people.
- **PR #59**: Thomas Aquinas, John Oldcastle, R. C. Sproul; this file rewritten as the
  project memory with the full rules and people list; roster test added. 23 people.
- **PR #58**: Nicholas of Myra (assumed for "Nicolas"), Athanasius, Chrysostom, Leo the Great,
  Gregory the Great, Cranmer, Bucer, Chemnitz, Erasmus, Chuck Smith; AI-generated notice on
  every page (`ai_generated`). 20 people.
- **PR #57**: John Knox. **PR #56**: C. S. Lewis. **PR #55**: Billy Graham.
- **PR #54**: William of Ockham; `misattributed` sayings category; standing instruction to
  commit, merge, and build each new person without asking.
- **PR #53**: John Wycliffe and Jan Hus; required `excommunications` section for everyone.
- **PR #52**: required persecution section (who was responsible, jurisdiction, church/state).
- **PR #51**: initial site (Augustine, Luther, Wesley as starter examples; William Tyndale with
  Words and sayings), timeline with era zoom, build checks, tests, and GitHub Pages publishing.

