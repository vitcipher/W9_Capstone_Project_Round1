# Round 1 Decision

Recorded after presenting `presentation/Capstone Consulting Round 1.pptx` to the teaching
staff (the presented deck — adapted from an earlier working draft, with updated statistics
and a monetization/unit-economics appendix; see `presentation/README.md` for what changed
between draft and presented versions).

## Feedback summary
- Overall verdict: **keep** — the sector, use case, and company-size framing landed as
  presented, no pivot requested.
- Specific technical direction given: use **Supabase (Postgres)** for real
  persistence/auth rather than continuing with the session-state/CSV-only POC.
- Scope guidance: **de-prioritize direct bank-account connections** — confirmed as a
  "nice to have," not something to invest further build time in right now. This matches
  where it already sat in the MoSCoW backlog (slide 10/15 of the draft deck) — the
  feedback validated that prioritization rather than changing it.

## Decision: KEEP

Industry (real estate / PropTech for private landlords), use case (rent/expense/lease
document extraction → portfolio dashboard), and company size (Medium) all carry forward
into Round 2 unchanged.

## What I'll deepen in Round 2
- **Use Supabase for real persistence + auth** — acted on already, not just planned, in
  the working prototype built alongside this pitch (not duplicated in this trimmed Round 1
  submission repo). Properties, confirmed document extractions, and maintenance requests
  are real Postgres rows behind Row Level Security (`owner_id = auth.uid()`), not
  session-state/CSV. Landlords sign up/log in with a real email + password; one landlord's
  tenants/documents/properties are private from another's at the database layer, not just
  filtered in app code.
- **Reduce bank-connection scope accordingly** — the Enable Banking Mock ASPSP integration
  in that prototype stays as a working, de-risked demo (proof the technical path is
  viable) but is deliberately *not* being built out further or wired into Supabase yet,
  per the feedback above.
- **Use case:** the rent/expense/lease document extraction assistant
  (`research/use_cases.md`, use case 1) continues toward a working MVP — document upload →
  AI draft → human confirmation → live portfolio dashboard, now backed by real data
  instead of a POC.
- **Next MVP scope:** finish hardening what's already built (auth edge cases, retry
  handling on the extraction call — see `n8n/workflow_documentation.md` "Limits vs.
  production"), add a maintenance-requests demo-seed path (properties has one, maintenance
  doesn't yet), and wire the Tableau dashboard to live Supabase data instead of the static
  synthetic CSVs it currently reads. Use case 3 (market valuation, `research/use_cases.md`)
  stays a documented stretch goal, not pulled into the MVP.
