# Presentation

## What was actually presented
**`Capstone Consulting Round 1.pptx`** — this is the deck presented to the teaching staff
and is the Round 1 submission artifact. It started from an earlier HTML/CSS-based design
draft (built during initial prep, kept in the fuller development repo rather than
duplicated in this trimmed Round 1 submission) and was then edited directly in Google
Slides before presenting: updated statistics, an added monetization/unit-economics
appendix, a real Tableau Public link, a real LangSmith trace screenshot, and the recorded
Round 1 decision as its closing slide.

## What changed between the draft and the presented deck

**Numbers rounded/updated, sourced from a spreadsheet the student compiled** (see
`data/README.md`'s note on `germany_private_landlord_households_2018_2022.csv` for exactly
which figures are fully traceable vs. not yet cited):
- Private-landlord households: 3.7M→5.5M+ (draft) became 3M→5M+ (presented) — rounded
- Population-share figure: 10%→13% (draft) became a single "6% of the Total population"
  (presented) — **not the same metric**: 6% = private-landlord households ÷ Germany's
  total population, computed from the student's own data; 13% was IW Köln/SOEP's own
  reported population-share metric (different base/methodology). Both are defensible, but
  they answer slightly different questions — worth being explicit about which is being
  cited if asked.
- Renter household share: 58% (draft, Zensus 2022) became 53% (presented) — different
  figure, source not confirmed for the 53% version.

**New claims added, not yet sourced — flag before treating these as citable facts:**
- Slide 2: Chleo's platform has "~0.5M MAU and 150K landlords" (a new assumption about the
  fictional company, not derived from external data — fine as a pitch assumption, just
  shouldn't be confused with a researched figure)
- Slide 3: "Foreign population growth is the sole driver of Germany's overall population
  growth" — stronger than the supporting chart actually shows (that chart shows total
  population trending up 1950–2022; it doesn't break out native vs. foreign growth to
  prove sole causation)
- Slide 4: landlords "currently spend ~€180/year on other solutions" — no source
- Slide 8: a "what landlords currently pay (eg. Immoscout)" column (€0.99M–€20M) — no
  source, and the ImmoScout24 comparison isn't substantiated

**A real bug, found and fixed:** the published Tableau dashboard's "Private landlord
households" chart (embedded as an image on the Appendix slide, screenshotted before the
fix) showed values around 39.6M–49.8M against the deck's own "~5M private-landlord
households" claim on slide 3. Cause: the dual-axis "Foreign Population Migrating to
Germany & Private Landlord Numbers are Increasing" chart had labels reading off the wrong
axis — private-landlord households (5.0M–5.5M) needed its own left axis, separate from
foreign population (39.6M–49.8M) on the right. Fixed post-presentation; see
`dashboard/dashboard_documentation.md`.

**One claim walked back from the draft, worth a second look:** the GDPR risk line changed
from "flagged now rather than later" (draft — deliberately left open, since no DPIA has
been done) to "Risk is low as the system will be GDPR compliant" (presented — stated as
settled). No GDPR compliance analysis has actually been completed yet (that's Round 2
work per `research/opportunities_risks.md`); the presented wording asserts more than has
been verified so far.

## Confirmed real (not just claimed)
- **Tableau Public dashboard**, live and published — link in `dashboard/dashboard_documentation.md`
- **LangSmith trace**, screenshot in the deck matches the actual `capstone-round1-property-extraction`
  project verified earlier (4 real traces: emi_statement, rental_contract, nebenkosten_invoice,
  rent_receipt) — see `langsmith/README.md`
- **The recorded decision** (KEEP; use Supabase; de-prioritize bank connections) — now
  written up properly in `feedback/round1_decision.md`
