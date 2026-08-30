# Cost Estimate

Scoped to the Round 1 pitch: taking the existing POC (n8n workflow + Streamlit demo) to a
3-month pilot with a subset of Chleo's existing landlord users. Figures are in EUR unless
noted; all third-party pricing below is cited and dated (August 2026) — verify before
finalizing, since SaaS pricing changes.

## Upfront costs

| Item | Estimated cost | Assumption |
|---|---|---|
| Engineering build time | Already sunk — n8n POC + Streamlit demo built during Round 1 | No separate line item; pilot hardening (auth, error handling — see `n8n/workflow_documentation.md` Limits) estimated at ~2 additional engineer-weeks, ~€4,500 at a blended €150/hr, part-time |
| Tableau Creator seat (Cloud, Standard edition) | $75/user/month, billed annually ≈ $900/year (~€830/year) | 1 Creator seat to build/maintain the dashboard; Standard edition is sufficient — Enterprise's extra governance/Tableau Pulse features aren't needed at pilot scale ([pricing source](https://www.toucantoco.com/en/blog/tableau-pricing), Aug 2026) |
| n8n hosting | €0 if self-hosted on existing infrastructure | Company already runs a listing platform with its own infra; self-hosting n8n avoids a new SaaS line entirely for the pilot |
| Sample/synthetic test documents | €0 — already produced | Covered in Round 1 scope, no ongoing cost |

## Ongoing costs (monthly, at pilot scale)

**Assumption driving this section:** 200 landlords in the pilot, each uploading ~2
documents/month (mix of rent receipts, Nebenkosten invoices, and occasional rental
contracts) → **~400 documents/month**.

| Item | Estimated monthly cost | Basis |
|---|---|---|
| OpenAI API (document extraction) | **~€8–30/month** | See calculation below |
| Tableau Creator (1 seat) | ~$75/month (~€70) | As above |
| Tableau Viewer seats (2–3, for internal stakeholders) | ~$15/user/month each (~€14) | Read-only access to the dashboard for non-builders |
| n8n hosting | €0–20/month | €0 if self-hosted; ~€20/month if n8n Cloud Starter is used instead |
| LangSmith | **€0/month** | Free tier covers 5,000 traces/month — 400 documents/month is well within that, with headroom to ~10x the pilot before hitting the free-tier ceiling ([pricing source](https://costbench.com/software/ai-observability/langsmith/), Aug 2026) |
| Ongoing engineering maintenance | ~0.1 FTE | Prompt tuning, confidence-threshold adjustment, bug fixes based on pilot feedback |

**OpenAI cost calculation (shown, not just asserted):** GPT-4.1 pricing is $2.00 per 1M
input tokens and $8.00 per 1M output tokens ([source](https://www.cloudzero.com/blog/openai-pricing/),
Aug 2026). A short document (rent receipt, Nebenkosten invoice — 1 page) runs roughly
1,000–1,500 input tokens (system prompt + document) and ~200–300 output tokens (the JSON
extraction) → **~€0.005–0.01/document**. A longer document (a multi-page rental contract)
runs higher, plausibly **~€0.03–0.08/document**. Blended across a realistic pilot mix
(mostly short financial documents, occasional contracts), **~400 documents/month lands
around €8–30/month** in raw API spend — genuinely small at this scale.

**This number will grow with scale and complexity, not stay flat — say so explicitly.**
Per McKinsey's *State of AI in 2026* (cited in `data/`), per-token prices keep falling but
token *consumption* per task tends to grow faster, especially once a workflow moves from
simple extraction toward more "agentic" multi-step reasoning (e.g. cross-checking a lease
against a bank statement). Revisit this estimate quarterly during the pilot rather than
treating it as fixed.

## Assumptions table

| Assumption | Rationale |
|---|---|
| Pilot scale = 200 landlords, ~400 documents/month | Matches the "run a one-workflow pilot, measure real costs and savings over one full cycle" best practice found in property-management AI ROI research, rather than sizing for a hypothetical full rollout |
| ~2 documents/landlord/month | Landlords mostly own 1–2 properties (IW Köln *Vermieterreport 2026*) and generate roughly one rent/expense document per property per month |
| No dedicated new hire for the pilot | Reuses existing engineering capacity at a Medium-size company; a dedicated hire is a Round 2 discussion if the pilot succeeds |
| Self-hosted n8n, not n8n Cloud | Assumes the company already operates infrastructure for its listing platform; adjust if that's not the case |
| Human-review time isn't a company cost line | Review happens on the landlord's own time (self-service) in this design — see `n8n/workflow_documentation.md`. It becomes a real operating cost only if a future paid "concierge review" tier is added |
| Tableau Standard edition, not Enterprise | Enterprise's governance/Pulse features aren't needed for a single internal dashboard at pilot scale — revisit if the dashboard becomes customer-facing at scale |
