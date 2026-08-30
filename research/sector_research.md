# Sector Research

## Sector & company size
- **Sector:** Real estate — PropTech / property management, specifically for private
  landlords who rent out residential property
- **Company size:** Medium — Chleo runs an established property **listing** platform
  (comparable in concept to ImmoScout24, but not at that scale): a working product,
  an existing base of private-landlord users, and engineering capacity to ship a new
  feature — but not the resources of a market leader
- **Why this scenario:** Chleo's company already has the target customer (private
  landlords) as users on the listing side. The pitch is an **adjacent expansion**, not a
  new market: a Property Management module that turns the existing landlord relationship
  into a second product, using data the company is already close to (market comps from its
  own listings).

## Data sources

| Source | What it contains | Link | Why it's relevant |
|---|---|---|---|
| ImmoScout24 rental listings (via Kaggle, mirrored on GitHub) | 268,850 real German rental listings: rent, Nebenkosten, size, location, condition, energy class, 2018–2020 | `data/germany_rental_listings_sample_5k.csv` (full file local, gitignored) | Market/comps data for valuation and rent-competitiveness benchmarking |
| Destatis, Zensus 2011/2022 + Eurostat Housing in Europe | German dwelling stock, owner-occupier vs. tenant household share | `data/germany_rental_ownership_trend.csv` | Germany is majority-renter (58% of households, Zensus 2022) and the tenant share is rising |
| Destatis, Ausländerzentralregister (GENESIS-Online 12521) | Foreign population in Germany by citizenship, annual, 2018–2025 | `data/germany_foreign_population_by_citizenship.csv` | Foreign nationals disproportionately rent; a structurally growing renter demand driver |
| IW Köln, *Deutschland.Immobilien Vermieterreport 2026* (1,002 landlords surveyed) | Landlord portfolio-size distribution, 2024–2026; demographics; satisfaction | `data/germany_landlord_portfolio_size_trend.csv` | Defines exactly who the customer is: ~75% of private landlords own ≤2 units |
| IW Köln, *Private Vermieter in Deutschland* (Oberst/Sagner/Voigtländer, June 2025), SOEP v39 + Zensus | 23-year time series of private-landlord households, plus city-size and state breakdowns | `data/germany_private_landlord_households_trend.csv`, `..._by_city_size.csv`, `..._by_state_2022.csv`, primary source PDF also in `data/` | The core "why now" growth evidence |
| AI Index Report 2026 (Stanford HAI) | Cross-industry AI adoption/hiring data; a dedicated finance-document benchmark (MortgageTax) | course material, cited inline below | Real estate AI hiring +93.5% YoY (2nd-fastest of any sector); honest technical limits on document extraction |
| BILL, *The 2026 State of AI in Finance* (500 finance leaders, small/midsize orgs) | Where AI is used in finance/back-office functions | course material, cited inline below | Budgeting & reporting are the top AI use areas in any finance function — generalizes to a landlord's own books |
| AppFolio, *2026 Property Manager Benchmark Report* | Property-management-industry AI adoption survey | web research, cited inline below | AI adopters report 31% vs. 12% portfolio growth; 78% don't trust their current PM software's AI — a trust gap this pitch can close |
| Synthetic landlord portfolio (fabricated) | 8 fictional properties + 12 months of P&L transactions | `data/synthetic_landlord_portfolio.csv`, `synthetic_monthly_transactions.csv` | Stands in for a landlord's actual books — no real financial data used, per the brief's data constraint |

## Sector context

- **Market size / trends:** The global PropTech market is roughly $51–55B (2026),
  growing ~16% CAGR. Private landlords collectively own **>60% of all German rental
  housing** and >5.5 million German households now earn rental income (13% of the
  population), up from ~3.7 million (10%) as recently as 2010 — a genuine structural
  shift, not a blip (IW Köln, SOEP v39, `data/germany_private_landlord_households_trend.csv`).
  Renter demand is growing in parallel: Germany is already Europe's only majority-renter
  country (58% of households rent, Zensus 2022), and the tenant population share keeps
  rising (52%→53%, 2023→2024, Eurostat). Immigration adds directly to that demand: total
  foreign population grew 28.9% from 2018 to 2025 (Destatis AZR), with populations that
  skew heavily toward renting (Ukraine +897%, India +151% over the same period).

- **How AI is currently used in this sector:** Real estate AI hiring grew +93.5%
  year-over-year in 2025 — the second-fastest of any sector tracked in the AI Index 2026,
  though it's still starting from a low absolute base (2.08% of postings vs. 13.2% for the
  information sector), so this is an early-but-accelerating story, not a mature one. In
  finance/back-office functions broadly (which is what a landlord's bookkeeping actually
  is), AI usage is highest for budgeting & financial planning (56%) and financial reporting
  (54%) — ahead of more complex or externally-facing processes (BILL, 2026 State of AI in
  Finance). In property management specifically, AppFolio's 2026 benchmark found AI
  adoption among property managers jumped from 20% to 58% in one year, but 78% of
  respondents still don't trust the AI features in their current software — a real
  trust gap.

- **Typical pain points for a company this size:** For Chleo's listing platform: adding a
  second product without a large build. For the end customer (the private landlord): per
  the Vermieterreport 2026, rental income is a **minor or negligible** share of total
  income for over half of private landlords — this is a side activity for most of them,
  not a profession, so they lack the time, tooling, or expertise to do proper bookkeeping.
  The report's own top-cited AI adoption barriers in adjacent finance contexts are cost of
  implementation and data security concerns (both 43%, BILL) — relevant since this product
  would touch landlords' bank/mortgage documents directly.

## Notes

- Germany's rental market is heavily regulated (Mietpreisbremse, strong tenant
  protections) — this doesn't block a bookkeeping/analytics tool, but it's part of why
  private landlords in Germany specifically behave cautiously (per the Vermieterreport:
  most raise rent only moderately or not at all, and 51% keep prices stable at
  re-letting) and is useful context for the pitch narrative.
- Company-size assumption: "Medium" for Chleo's own company is a judgment call, not
  something explicitly fixed by the brief — flagged here for Chleo/the teaching staff to
  push back on if a different size reads better for the pitch.
