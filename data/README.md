# Data sources

## `germany_private_landlord_households_2018_2022.csv`, `germany_dwellings_completed.csv`, `germany_dwellings_completed_by_building_type.csv`

Added post-presentation, sourced from a Google Sheet the student compiled during Round 1
prep: [spreadsheet](https://docs.google.com/spreadsheets/d/1r7stS82qkcaJ82YGMHm3j8kGZq_OTdmz9sL7YQrv2pY/edit).
Used for the "Foreign Population Migrating to German & Private Landlord Numbers are
Increasing" and "Number of new buildings completed" charts on the published Tableau
dashboard (see `dashboard/dashboard_documentation.md`).

**Honesty note:** the foreign-population figures in that sheet are byte-for-byte identical
to `germany_foreign_population_by_citizenship.csv` (Destatis AZR, already cited elsewhere
in this repo) — that part is fully traceable. The **private-landlord-households
(2018–2022)** and **dwellings-completed** series, however, have no source stated in the
sheet itself. The landlord figures (5.00M in 2018 → 5.50M in 2022) are directionally
consistent with `germany_private_landlord_households_trend.csv`'s cited 2022 anchor
(IW Köln/SOEP, "5.5M+" in 2022) — close enough to plausibly be drawn from the same
underlying report, but not confirmed. The dwellings-completed series is very plausibly
Destatis Baufertigstellungen (building completions) data, given the shape (2008–2010
financial-crisis dip, since recovery) matches known patterns, but isn't linked to a
specific table here. **If this goes into a graded deliverable, get the actual citation
before final submission** — right now it's usable for the pitch narrative but doesn't
meet the same sourcing bar as the rest of this repo's data.

**Known bug worth fixing:** the published Tableau dashboard's "Private landlord households"
chart shows values in the 39.6M–49.8M range — that's roughly Germany's *total dwelling
stock* (see `germany_rental_ownership_trend.csv`), not private-landlord households, which
this very file puts at 5.0M–5.5M. The chart has the wrong field wired to it.

## `germany_rental_listings_clean.csv` (full, 268,643 rows, 45.8 MB — local only, gitignored)
## `germany_rental_listings_sample_5k.csv` (5,000-row random sample — committed, for quick loads/demos)

**Source:** Real rental listings scraped from ImmoScout24 (Germany's largest property
portal) across four survey waves (Sep 2018, May 2019, Oct 2019, Feb 2020).
Originally published on Kaggle as
[`corrieaar/apartment-rental-offers-in-germany`](https://www.kaggle.com/datasets/corrieaar/apartment-rental-offers-in-germany)
(268,850 listings, 49 columns); documented academically in
[EconStor's sample documentation of ImmoScout24 data, 2007–2013](https://www.econstor.eu/handle/10419/103748).
Downloaded here via a public GitHub mirror
([northpr/GermanyRentalPrice](https://github.com/northpr/GermanyRentalPrice)) since
Kaggle's own download endpoint requires an authenticated API token.

**License/use:** Public dataset, widely used for teaching/ML demos. No personal data —
listings are anonymized property ads, not landlord or tenant identities.

**Cleaning applied:** dropped rows missing `baseRent`, `livingSpace`, `regio1`, `regio2`,
or `noRooms`; removed `baseRent` outside €0–20,000 and `livingSpace` outside 5–1,000 m²
(the raw file has a handful of corrupted rows with absurd values, e.g. `baseRent` in the
millions).

**Key columns for the dashboard:**

| Column | Meaning |
|---|---|
| `regio1` / `regio2` / `regio3` | State / county-city / district — for regional comps |
| `geo_plz` | Postal code |
| `baseRent`, `totalRent` | Cold rent / warm rent (EUR/month) |
| `serviceCharge` | **Nebenkosten** — ancillary/operating cost charged to tenant (EUR/month) |
| `heatingCosts` | Heating cost component (EUR/month) |
| `livingSpace`, `noRooms` | Size (m²) and room count |
| `yearConstructed`, `condition`, `energyEfficiencyClass` | Property characteristics — valuation inputs |
| `pricetrend` | ImmoScout24's own regional price-trend indicator |
| `date` | Survey wave (which scrape the listing is from) |

## `synthetic_landlord_portfolio.csv` (8 fictional properties — fully synthetic)

**Status update:** now used only as one-time seed data — the "Load demo portfolio" button
in `app/streamlit_app.py` inserts these 8 rows into a fresh Supabase account's `properties`
table (see `supabase/schema.sql`) so a new signup isn't empty. The app's live data source
is the `properties` table itself, not this file, once you've signed up and seeded/added
properties. Still used directly for the Tableau dashboard spec, since that's a separate
artifact from the Streamlit app.

The landlord's actual portfolio, used for the P&L/dashboard use case. **Entirely made up**
(fake street names using German placeholder-name conventions — Musterstraße/Beispielweg/
Probeallee/Testring, meaning "Example Street" etc. — no real addresses or people), but
internally consistent: purchase price is derived from each city's `region_rent_per_sqm`
× a plausible price-to-annual-rent multiple (Munich ~29x reflecting its low rental yield,
Leipzig/Dresden ~17x reflecting higher-yield secondary cities — directionally consistent
with the real ImmoScout24 rent-per-sqm patterns in the market dataset above), loan-to-value
60–70%, mortgage rate 3.2–4.0%, 25–30 year term, EMI computed with the standard amortization
formula. Columns: property details, purchase price, current valuation estimate, loan terms,
monthly EMI, monthly base rent, Nebenkosten budget, and monthly operating costs (management
fee, maintenance reserve, insurance, property tax).

## `synthetic_monthly_transactions.csv` (96 rows = 8 properties × 12 months — fully synthetic)

Monthly transaction history (Sep 2025–Aug 2026) per property: rent collected, Nebenkosten
collected vs. actually spent (small variance, since Nebenkosten is a pass-through
reconciled annually — it doesn't perfectly net to zero every month), occasional
maintenance-cost spikes, occupancy status, and net cash flow after the mortgage EMI and all
operating costs. One property (P04, Dortmund) sits vacant for two months to give the
dashboard a vacancy/occupancy story. Net result across the portfolio: most properties are
cash-flow positive before EMI, but after EMI + maintenance reserve + management fee, 6 of 8
run a modest monthly loss on paper (worst in Munich, the lowest-yield city) even though
rent nominally "covers" the mortgage — that gap between "rent vs. EMI" and "true net cash
flow" is deliberately the core insight the dashboard should surface, since it's exactly the
kind of thing a private landlord doing their own books tends to miss.

## `synthetic_maintenance_requests.csv` (8 rows — fully synthetic)

**Status update:** written for the earlier session-state-only version of the app. Now that
maintenance requests live in Supabase (`maintenance_requests` table), a new account starts
empty — there's no "load demo maintenance requests" seed button yet (unlike properties,
which does have one). Honest gap, not hidden: add one if the empty-state demo experience
matters, using the same pattern as `load_demo_portfolio_csv()` in `app/streamlit_app.py`.

Originally: seed data for the app's Maintenance Requests tab. 8 example
requests spread across the 8 properties, a mix of urgency (Low/Medium/High) and status
(New/In Progress/Resolved) so the tab isn't empty on first load. This is a plain CRUD
feature with no AI involved — it's the one "must-have" feature (per a competitive review of
landlord-focused software: Innago, TurboTenant, Landlord Studio, Baselane, etc.) that needed
zero new integrations to build, unlike rent collection (payment processor) or tenant
screening (credit bureau access, and separately out of scope — see
`research/opportunities_risks.md`).

## `germany_rental_ownership_trend.csv` (13 rows — compiled published statistics, not row-level data)

For the "why now" market chart: growth in German rental/buy-to-let housing. **Important
caveat, stated honestly rather than glossed over:** there is no single public dataset with
a smooth annual time series isolating "privately-owned rental properties." Germany's
housing census (Zensus) only runs once a decade (2011, 2022), and the annual Mikrozensus
housing supplement changed methodology in 2020, breaking direct year-to-year comparability
across that boundary. So this file is a **compiled table of individually sourced, cited
published figures** — a handful of real anchor points, not a smooth curve. Don't chart it
as if it were a dense annual series; bar/column comparisons between the actual years
(2011 vs. 2022, 2023 vs. 2024) are the honest way to show it.

Key figures compiled here:
- **Dwellings in condo ownership (WEG — Wohnungseigentümergemeinschaft)**: 8,956,419 (2011)
  → 9,277,939 (2022), +3.6%. This is the closest available official proxy for "individually
  owned units that can be rented out" (private landlords in Germany typically own via WEG,
  not entire buildings) — [VDIV coverage of the Zensus 2022 release](https://vdiv.de/presse/details/eigentumsbildung-in-gefahr-zensus-2022-belegt-wenig-wachstum-bei-wohnraum-in-weg)
- **Rented dwellings**: 53.5% of ~43.1M German dwellings (~23M units) were rented as of
  Zensus 2022 — [Destatis Zensus 2022](https://www.destatis.de/DE/Themen/Gesellschaft-Umwelt/Wohnen/_inhalt.html)
- **Tenant population share rising**: 52% (2023) → 53% (2024) —
  [Eurostat, Housing in Europe](https://ec.europa.eu/eurostat/web/interactive-publications/housing-2025)
  · Germany is the only EU country where more people rent than own (EU average: 68% owner-occupied)
- Historical owner-occupier household share: 41% (2006) → 45.1% (2011, different survey
  methodology) → 42% (2022, Zensus) — cited as-is; don't smooth over the methodology break

**What I did not do:** interpolate or smooth between these real anchor points to fake a
denser-looking trend line. If you want a visually smoother chart for the presentation, that
would need to be an explicitly labeled interpolation ("estimated, linear interpolation
between census years") — happy to add that as a separate clearly-marked column if useful,
but the sparse real data is the honest version.

## `germany_foreign_population_by_citizenship.csv` (272 rows — real annual official data, 2018–2025)

Foreign population in Germany by citizenship, every year 2018–2025 (reference date 31 Dec),
in tidy long format (`year`, `nationality`, `category`, `population`, `source`). Unlike the
ownership/rental file above, **this one is a genuine dense annual time series** — no
interpolation needed.

**Source:** Destatis, Ausländerzentralregister (Central Register of Foreigners), GENESIS-Online
statistic 12521 ("Ausländische Bevölkerung nach ausgewählten Staatsangehörigkeiten").
Pulled from the static table page (readable directly) rather than the interactive
GENESIS-Online viewer (JavaScript-rendered, not fetchable):
[destatis.de table page](https://www.destatis.de/DE/Themen/Gesellschaft-Umwelt/Bevoelkerung/Migration-Integration/Tabellen/auslaendische-bevoelkerung-staatsangehoerigkeit-jahre.html)
· [GENESIS-Online 12521](https://genesis.destatis.de/datenbank/online/statistic/12521/table)

**Why this is relevant to the pitch:** foreign nationals in Germany are disproportionately
renters rather than owners (financing/credit-history barriers, uncertain length of stay,
etc.), so growth in the foreign population is a demand driver specifically for the
*rental* market. Total foreign population grew **10,915,455 → 14,070,225 (+28.9%) from
2018 to 2025**. Some individual nationalities grew far faster — Ukraine +897% (refugee
migration post-2022) and India +151% (skilled-migration visas) — both populations that
skew heavily toward renting, especially in the first years after arrival. This pairs well
with the `germany_rental_ownership_trend.csv` file as a second, independently-sourced "why
now" argument: not just "more people rent than own in Germany," but "the renting population
is actively growing, and immigration is a measurable part of why."

## `germany_landlord_portfolio_size_trend.csv` (18 rows — real annual survey data, 2024–2026)

**This is the key dataset for the "multi-property owners" angle**, and unlike the census
data above, it's a genuine year-over-year trend, not sparse anchor points.

**Source:** IW Köln (Institut der deutschen Wirtschaft), *Deutschland.Immobilien
Vermieterreport 2026*, published in cooperation with Deutschland.Immobilien AG. Survey of
**1,002 private landlords in Germany**, fielded February 2026 via survey firm uzbonn, with
directly comparable 2024/2025/2026 figures (third edition of an annual survey). PDF:
[iwkoeln.de Vermieterreport 2026](https://www.iwkoeln.de/fileadmin/user_upload/Studien/Gutachten/PDF/2026/Deutschland.Immobilien_Vermieterreport_2026.pdf)
(page 12, chart 3-3, "Professionalisierungsgrad der privaten Vermieter (I)").

**Headline finding:** "Drei von vier privaten Vermietern besitzen höchstens zwei
Wohnungen" — about three in four private landlords own at most two rental units. Multi-
property investors (3+ units) make up roughly a quarter of the market and have been
essentially flat 2024→2026 (~23%), while the single-property share has been **rising**
(55% → 58%). Private landlords collectively own >60% of Germany's entire rental housing
stock (same report, foreword).

**Why this matters for the pitch:** it's a direct, sharper answer to "who is Chleo's
customer?" than the broader ownership-trend file above — it says most of the addressable
market is exactly the kind of small, non-professional landlord (1-2 units, vermietung as a
side income not a profession — 55%+ call rental income only a "minor" or "negligible" share
of their total income per the same report) who would benefit most from a tool that
automates bookkeeping they're currently doing manually or not doing well. It also gives you
an honest counter-argument to pre-empt: the very largest portfolios (6+ units, i.e. the
segment closest to "professional" landlords) are shrinking as a share, not growing — so the
product's natural target is the small-portfolio majority, not enterprise-scale asset
managers.

## `germany_private_landlord_households_trend.csv` (5 rows — real anchor points from a 23-year annual series)

**This directly answers "the trend of increase in private landlords in Germany."**

**Source:** Oberst, Sagner, Voigtländer, *"Private Vermieter in Deutschland"* (IW Köln,
commissioned by Kölner Haus- und Grundbesitzerverein and Haus & Grund Düsseldorf, 26 June
2025). Based on **SOEP v39** (Socio-Economic Panel, DIW Berlin — an annual household survey
running since 1984, 30,000+ respondents) combined with Zensus 2011 and Zensus 2022.
Original: [iwkoeln.de PDF](https://www.iwkoeln.de/fileadmin/user_upload/Studien/Gutachten/PDF/2025/Gutachten-Private-Vermieter-in-Deutschland.pdf) —
a copy is kept in this repo as `source_iwkoeln_private_vermieter_2025.pdf` since it's the
primary source for four of the CSVs in this folder (this file, plus the city-size and
state-level breakdowns below).

The report's **Abbildung 4-1** ("Anzahl und Anteil privater Kleinvermieter in Deutschland")
is a genuine annual bar chart, 2000–2022, 23 data points — but it's a chart image in the
PDF, not a data table, so I only extracted the values **explicitly stated in the report's
own text** rather than estimate bar heights by eye (which would risk quietly inventing
precision that isn't real). Those anchor points:

- 2000–2010: roughly stable, 3.7M–4.2M households, ~10% of the population
- From 2011: continuous rise begins
- 2017: share reaches 12%
- 2019: share reaches 13% and **stays flat through 2022** — i.e. the *rate* has plateaued,
  even as the *absolute count* keeps growing (population growth + more households)
- 2022: **5.5M+ households**, i.e. **+1.8M (+49%) vs. 2010** — this is the headline "trend
  of increase" figure

Separately, the report's introduction states **13% of all households in Germany are
landlords** (a household-share framing, distinct from the chart's population-share metric
— both land on ~13% but are not the same denominator; I kept them distinct rather than
merge them into one number).

**Full 23-year series, visually estimated:** `germany_private_landlord_households_trend_full_estimated.csv`.
I read each bar/dot position against the chart's gridlines (0–6M in 1M steps for the
household count; 0–16% in 2%-point steps for the population share) and estimated a value
per year. **Read this as approximate, not authoritative** — a `confidence` column marks
which rows are `stated_in_text` (2010, 2017, 2019, 2022 — these match the report's own
prose exactly) vs. `visual_estimate` (everything else — read off the chart image, not
published as exact numbers anywhere, and could plausibly be off by roughly ±100–150k
households or ±0.5 percentage points in either direction). The *shape* of the trend
(flat 2000–2010, dip around 2003, steady climb from 2011, accelerating from 2017) should be
directionally right since it's grounded in real gridlines rather than guessed freehand, but
don't cite the non-anchor years as precise figures in anything that gets fact-checked
closely — cite the `stated_in_text` anchor file for that, and use this fuller file only for
a smoother-looking line in the dashboard, with a footnote disclosing the estimation.

## `germany_landlord_households_by_city_size.csv` and `germany_landlord_households_by_state_2022.csv`

Same source/study as above (Oberst/Sagner/Voigtländer 2025, SOEP v39 + Zensus).

- **By city size** (Abbildung 4-2): landlord-household share rose in every settlement type
  2000→2022, but small towns (≤20,000 residents) both started and stayed highest — 11%→16%,
  vs. mid-size towns 10%→13% and big cities (100,000+) 7%→11%. Big cities are catching up
  fastest in relative terms but remain the smallest share in absolute terms.
- **By state, 2022 snapshot**: sharp east-west and city-state-vs-flächenland divide.
  Baden-Württemberg (20%) and Bavaria (17%) lead, both with 1M+ landlord households; the
  five eastern states plus Berlin cluster at 7–8%; Hamburg (9%) sits above Berlin (7%) and
  Bremen (6%) among the city-states.

## What this dataset is for — and what it isn't

This is **market/comps data**: real asking rents and Nebenkosten across Germany, useful for
benchmarking ("is this property's rent/Nebenkosten in line with similar units in its
postal code?") and for a rough valuation estimate (price-per-m² by region and condition).

It is **not** a landlord's actual portfolio — it has no owner, no mortgage/EMI, no actual
collected rent or expense history. The synthetic landlord portfolio (a handful of
properties with made-up rent/expense/EMI/Nebenkosten documents) is a separate, deliberately
synthetic dataset — see the project brief's data-source constraint (public/synthetic data
only, no real personal financial data).

## German housing-stock context (market sizing, not per-property data)

Destatis (Federal Statistical Office) table 31231, "Wohnungsbestand" — 44.0 million
dwellings in Germany at year-end 2025.
[Destatis press release](https://www.destatis.de/DE/Presse/Pressemitteilungen/2026/07/PD26_250_31231.html)
· [GENESIS-Online table 31231](https://genesis.destatis.de/datenbank/online/statistic/31231/table/31231-0001)
(the GENESIS-Online table itself requires JavaScript to browse interactively — cite the
press release's headline figures rather than trying to scrape the table).
