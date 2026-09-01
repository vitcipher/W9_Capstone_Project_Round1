# Use Case Proposals (3)

## Use case 1: Rent/Expense/EMI Document Extraction Assistant
- **Problem:** Private landlords receive rent receipts, mortgage/EMI statements, and
  Nebenkosten invoices as unstructured documents (PDFs, scans, emails) and currently
  transcribe them into spreadsheets manually, if they track them at all.
- **Proposed AI solution:** Landlord uploads a document; an LLM extracts structured
  fields (amount, date, category, property) and pre-fills the record. Every extraction
  is flagged with a confidence indicator and routed to the landlord for a quick
  confirm/correct step before it's saved — a drafting assistant, not an autonomous
  system.
- **Why it fits this company size:** Low build cost (one workflow, one document type
  category) for a medium-size company without a large engineering team; distributes
  through the existing listing-platform user base at no extra acquisition cost.
- **Data needed:** Synthetic sample documents (fake rent receipts, EMI statements,
  Nebenkosten invoices) — no real financial data, per the brief's constraint.
- **Rough effort/complexity:** Low-medium. This is the n8n POC.
- **Honest limit, stated up front:** AI Index 2026's MortgageTax benchmark shows even
  frontier models extracting structured data from real financial/legal documents don't
  reliably exceed ~70% accuracy. This shapes the design (human review required) rather
  than being hidden.

## Use case 2: Portfolio Profit & Loss Dashboard
- **Problem:** Landlords generally know their rent and their mortgage payment, but
  rarely see the *true* net picture once management fees, maintenance reserve,
  insurance, property tax, and Nebenkosten shortfalls are counted — so a property can
  look profitable and not be.
- **Proposed AI solution:** Not AI-driven itself — a BI dashboard (Tableau Cloud) built
  on the structured data that use case 1 populates, showing per-property and
  portfolio-level net cash flow, occupancy, and expense breakdown. This is the
  "communication layer" the dashboard requirement asks for.
- **Why it fits this company size:** Directly reuses the output of use case 1; no
  additional data pipeline needed.
- **Data needed:** Synthetic 8-property portfolio + 12 months of transactions
  (`data/synthetic_landlord_portfolio.csv`, `synthetic_monthly_transactions.csv`) —
  deliberately built so that most properties look fine on rent-vs-EMI alone but several
  run a real monthly loss once full costs are counted, which is exactly the insight the
  dashboard should surface.
- **Rough effort/complexity:** Low. This is the Round 1 dashboard focus.

## Use case 3: Market/Valuation Benchmarking
- **Problem:** Landlords don't know whether their rent is competitive or what their
  property might currently be worth, and typically rely on guesswork or an expensive
  formal appraisal.
- **Proposed AI solution:** Compare a landlord's property (size, location, condition)
  against real market listings to estimate a fair rent range and a rough valuation.
  Chleo's company is unusually well-positioned here since it already holds this data
  from its own listing platform — a real differentiator vs. a standalone competitor.
- **Why it fits this company size:** Reuses data the company already owns; doesn't
  require buying third-party market data.
- **Data needed:** Real ImmoScout24 listing data (`data/germany_rental_listings_sample_5k.csv`
  / full clean file), grouped by region/size/condition.
- **Rough effort/complexity:** Medium — kept as a documented stretch goal / Round 2
  roadmap item rather than built into the Round 1 POC, to keep the MVP scope small (per
  the brief: "one capability you can finish rather than a product you can only
  describe").

## Round 2 backlog (MoSCoW, as presented)

Presented on the "Additional features (scoping for Round 2)" slide of
`presentation/Capstone Consulting Round 1.pptx`:

| Feature | Priority | Relation to the use cases above |
|---|---|---|
| Manage the costs and profits | **Must have** | This *is* use case 2 (Portfolio P&L Dashboard) — already the Round 1 dashboard focus, carrying straight into Round 2 as the MVP core |
| Tax Savings Advisor Bot | Should have | New scope, not covered by use cases 1–3 — would need its own problem/data/effort writeup before Round 2 build |
| Direct Bank Connections (automatic statement pull, rent-received checks, tenant reminders) | Nice to have | Already de-prioritized per `feedback/round1_decision.md` — the Enable Banking Mock ASPSP integration in the working prototype built alongside this pitch is a de-risking proof of concept, not something being built out further right now |
| Tenants complaints management | Could have | Related to, but not identical to, the maintenance-requests tracking already built in that prototype (landlord-logged issues vs. tenant-submitted complaints) — worth clarifying which one this becomes before Round 2 |
| Automated Rental Contract Generation | Could have | New scope, not covered by use cases 1–3 — generation is a materially different (and higher-liability) capability than the extraction/reading use cases above, since it means the AI drafts a legal document rather than reading one |

## Which use case becomes the POC / dashboard focus?

- **n8n POC → Use case 1** (document extraction assistant, with the human-review step
  and the MortgageTax caveat built in from the start)
- **BI dashboard (Tableau Cloud) → Use case 2** (portfolio P&L), using the synthetic
  portfolio data and, for market-context metrics, the real ImmoScout24 comps data
- **Use case 3 stays on the roadmap** — mentioned in the cost/timeline estimate and the
  Round 2 strategic plan as the natural next phase (pilot → full deployment), not
  something claimed as working in Round 1
