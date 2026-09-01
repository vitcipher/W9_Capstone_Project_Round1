# Dashboard Documentation

## Tool
Tableau Public (built and published here — not Tableau Cloud as originally spec'd below;
Tableau Public was used instead since it's free/no-license and the goal was a shareable
public link, which is what Tableau Public is for).

## Status
**Built and published.** The build spec below was written before building, as an exact,
unambiguous recipe (data sources, joins/blends, calculated-field formulas, chart types,
layout) — it mostly held up, with one known issue flagged below.

## Where to view it
- **Published link (Tableau Public):**
  https://public.tableau.com/views/Capstone_Dashboard_Vittal/Dashboard1?:language=en-GB&:sid=&:redirect=auth&:display_count=n&:origin=viz_share_link
- **Local backup:** `dashboard/dashboard.twbx` (optional, in case the link becomes
  unreachable). Openable in Tableau Desktop or Tableau Public.

## Known bug — fix before further grading
The "Private landlord households" chart shows values around 39.6M–49.8M. The correct
range, per `data/germany_private_landlord_households_2018_2022.csv`, is 5.0M–5.5M — the
39.6M–49.8M range is close to Germany's *total dwelling stock* instead (see
`germany_rental_ownership_trend.csv`), which strongly suggests the wrong field got wired
into that chart in the workbook. This directly contradicts the "~5M private-landlord
households" figure used on slide 3 of the presentation deck, so worth fixing before this
link is shared again. See `presentation/README.md` for the full writeup of how this was
found.

## Data sources to connect

| # | File | Grain | Role |
|---|---|---|---|
| 1 | `data/synthetic_landlord_portfolio.csv` | 1 row per property (8 rows) | Primary — property details, purchase price, loan terms |
| 2 | `data/synthetic_monthly_transactions.csv` | 1 row per property × month (96 rows) | Primary — the actual P&L data |
| 3 | `data/germany_rental_listings_sample_5k.csv` | 1 row per market listing (5,000 rows) | Secondary — real market comps for the rent-competitiveness metric |
| 4 | `data/germany_private_landlord_households_trend.csv` | 1 row per year | Secondary — "why now" context tile |

**Relationships:**
- Source 1 ↔ Source 2: relate/join on `property_id` (1-to-many).
- Source 1/2 ↔ Source 3: these don't share a key at the same grain — **use a data blend**,
  not a join. Blend on `region` (portfolio) ↔ `regio1` (market listings). This compares a
  property's rent against the *regional average* from real listings, not a row-level match.
- Source 4 stands alone, feeding one KPI tile — no join needed.

## Metrics shown (7, stakeholder-relevant)

| # | Metric | Why it matters to Chleo | Source | Chart type |
|---|---|---|---|---|
| 1 | Portfolio net cash flow (monthly trend) | The single top-line number — is the portfolio actually making money, month over month | 2 | Line chart, `month` on columns, `SUM([net_cashflow])` on rows |
| 2 | Net profit/loss per property | Which specific properties are winners vs. losers — not obvious from rent alone | 2 | Horizontal bar, one bar per `property_id`, colored by sign (green/red) |
| 3 | **The hidden-cost gap** (naive vs. true profit) | The core insight the tool exists to surface — see calculated field below | 2 | Bar chart, two bars per property: "Rent − EMI" vs. "True net cash flow" |
| 4 | Occupancy rate | Vacancy is invisible in a simple spreadsheet until it's already hurt cash flow | 2 | KPI tile + small multiples by property |
| 5 | Portfolio value & equity growth | Total appreciation since purchase — the "is this still a good investment" question | 1 | KPI tile: `SUM([current_valuation_estimate])` vs. `SUM([purchase_price])`, plus % delta |
| 6 | Rent competitiveness vs. regional market | Is each property under/over-priced vs. real comparable listings — differentiator vs. a generic bookkeeping app | 1 blended with 3 | Bar chart: landlord's €/m² vs. regional avg €/m², one pair per property |
| 7 | "Why now" context tile | Private-landlord households grew +49% (2010→2022) — the market-growth hook, not a P&L number | 4 | Single KPI/sparkline: latest value + trend, small supporting element, not the main focus |

## Calculated fields (exact formulas)

Define these in Tableau (right-click a data source → Create Calculated Field):

```
# On synthetic_monthly_transactions.csv

Naive Profit (Rent − EMI)
SUM([rent_collected]) - SUM([mortgage_emi])

Hidden Cost Gap
[Naive Profit (Rent − EMI)] - SUM([net_cashflow])
# This is the number that should surprise Chleo: everything the naive
# "rent minus mortgage" math misses — management fee, maintenance
# reserve, insurance, property tax, and any Nebenkosten shortfall.

Occupancy Rate
SUM(IF [occupancy] = "Occupied" THEN 1 ELSE 0 END) / COUNT([occupancy])


# On synthetic_landlord_portfolio.csv

Equity Growth
SUM([current_valuation_estimate]) - SUM([purchase_price])

Equity Growth %
[Equity Growth] / SUM([purchase_price])

Landlord Rent per sqm
SUM([monthly_base_rent]) / SUM([living_space_sqm])


# On germany_rental_listings_sample_5k.csv (used via the region blend)

Market Rent per sqm
AVG([baseRent] / [livingSpace])
# Filter this data source to the relevant regio1 value(s) before blending,
# or use a filter action so it recalculates per selected property's region.
```

## How to navigate
Two tabs/pages:

1. **Portfolio Overview** (primary tab, opens first) — metrics 1–4: the monthly trend line
   at the top, per-property profit/loss and the hidden-cost-gap bars side by side below,
   occupancy as a small KPI strip. A `property_id` filter (multi-select) lets Chleo drill
   into one property.
2. **Market Context** (secondary tab) — metrics 5–7: equity growth KPI, rent-vs-market
   comparison, and the "why now" tile. This tab supports the pitch narrative rather than
   day-to-day portfolio management.

## Build steps (Tableau Desktop, then publish to Cloud)

1. Connect all four CSVs listed above (Data → New Data Source → Text File).
2. Set up the property_id relationship between sources 1 and 2 (Tableau will likely
   auto-detect it; verify the join type is left/inner as appropriate — no properties should
   be dropped).
3. Set up the region blend to source 3 (Data → Edit Relationships, or use it as a secondary
   source with `region`/`regio1` set as the linking field).
4. Create the six calculated fields above, on the data source noted in each formula.
5. Build each worksheet per the chart-type column in the metrics table.
6. Assemble the two dashboard tabs per the navigation section above; add the `property_id`
   filter and apply it to all relevant sheets (Filter → Apply to Worksheets → Selected
   Worksheets).
7. Publish to Tableau Cloud (Server → Publish Workbook); set permissions to "anyone with
   the link can view."
8. Export a `.twbx` packaged workbook as the local backup in this folder.
9. Take screenshots of both tabs for this doc once built.

## Screenshots
A screenshot of the published dashboard is embedded in `presentation/Capstone Consulting
Round 1.pptx` (Appendix slide) — no separate PNG export in this folder yet.
