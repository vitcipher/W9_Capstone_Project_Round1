# Cost Estimate

Scoped to the Round 1 pitch: taking the existing POC (n8n workflow + Streamlit demo) to a
pilot with a subset of Chleo's existing landlord users. Figures are in EUR unless noted;
all third-party pricing below is cited and dated (August 2026) — verify before finalizing,
since SaaS pricing changes.

**A note on method, stated up front rather than left implicit:** Chleo's company and its
user base are fictional for this pitch — there's no real MAU or document-volume data to
draw from. So this estimate is built **unit-cost-first**: every per-document and per-seat
price below is real and cited. Only the *volume* (how many landlords, how many documents)
is an assumption, and it's kept separate and clearly labeled as illustrative, so the
numbers can be recomputed live with Chleo's actual platform size rather than defended as a
fixed forecast.

## Fixed / one-time costs (volume-independent)

| Item | Estimated cost | Assumption |
|---|---|---|
| Engineering build time | Already sunk — n8n POC + Streamlit demo built during Round 1 | Pilot hardening (auth, error handling — see `n8n/workflow_documentation.md` Limits) estimated at ~2 additional engineer-weeks, ~€4,500 at a blended €150/hr, part-time |
| Tableau Creator seat (Cloud, Standard edition) | $75/user/month, billed annually ≈ $900/year (~€830/year) | 1 Creator seat to build/maintain the dashboard, regardless of how many landlords use it — Standard edition is sufficient; Enterprise's extra governance/Pulse features aren't needed at pilot scale ([source](https://www.toucantoco.com/en/blog/tableau-pricing), Aug 2026) |
| n8n hosting | €0 if self-hosted on existing infrastructure | Company already runs a listing platform with its own infra; self-hosting avoids a new SaaS line for the pilot regardless of volume |
| Sample/synthetic test documents | €0 — already produced | Covered in Round 1 scope |

## Unit economics (the real numbers — plug in your own volume)

**Per-document AI cost.** GPT-4.1 pricing is $2.00 per 1M input tokens and $8.00 per 1M
output tokens ([source](https://www.cloudzero.com/blog/openai-pricing/), Aug 2026).

| Document type | Rough size | Est. tokens (in/out) | Cost/document |
|---|---|---|---|
| Rent receipt / Nebenkosten invoice | 1 page | ~1,000–1,500 in / ~200–300 out | **~€0.005–0.01** |
| Rental contract / lease agreement | 3–5 pages | higher, multi-page | **~€0.03–0.08** |

**Per-landlord monthly AI cost**, assuming ~2 documents/month per landlord (see
assumptions): **roughly €0.02–0.04/landlord/month** for a typical mix of mostly short
financial documents with occasional contracts.

**This stays true regardless of how many landlords are actually on the platform** — that's
the point of leading with the unit cost. Whether Chleo has 200 or 20,000 landlord users,
the AI cost per landlord doesn't change; only the total does, linearly.

**One important caveat, not hidden:** this unit cost will drift with usage pattern, not
stay flat forever. Per McKinsey's *State of AI in 2026* (cited in `data/`), per-token
prices keep falling but token *consumption* per task tends to grow faster, especially if
the workflow moves from simple extraction toward more "agentic" multi-step reasoning (e.g.
cross-checking a lease against a bank statement, which is a plausible Round 2 extension).
Treat the per-document figures above as a starting estimate to validate empirically during
the pilot, not a permanent constant.

**Other per-unit costs:**
- Tableau Viewer seat: $15/user/month (~€14) each, for internal stakeholders who only view
  the dashboard — scales with headcount, not landlord count.
- LangSmith: free up to 5,000 traces/month; beyond that, $2.50 per additional 1,000 traces,
  or the $39/seat/month Plus plan ([source](https://costbench.com/software/ai-observability/langsmith/),
  Aug 2026). At ~1 trace per document extraction, the free tier alone covers roughly
  **5,000 documents/month before any LangSmith cost kicks in.**

## Illustrative scenario (not a forecast — recompute with Chleo's real numbers)

Two example volumes, to show the AI cost scales gently even as landlord count grows an
order of magnitude:

| | Small pilot: 200 landlords | Larger pilot: 2,000 landlords |
|---|---|---|
| Documents/month (~2/landlord) | ~400 | ~4,000 |
| OpenAI API cost/month | ~€8–30 | ~€80–300 |
| Hits LangSmith free-tier ceiling? | No (well under 5,000 traces) | Not quite (still under 5,000) |
| Tableau + n8n (fixed costs above) | ~€70–90/month | ~€70–90/month (unchanged) |

The headline takeaway for the pitch: **the AI usage cost itself is not the barrier at any
plausible pilot size** — the fixed SaaS/tooling costs (~€70–90/month) dominate the total
until landlord count reaches the thousands, at which point it's a "good problem" that
means the pilot succeeded.

## Note on the presented deck's monetization appendix

`presentation/Capstone Consulting Round 1.pptx` adds a revenue-side scenario not in this
file: a **75,000-landlord / 50%-capture-rate** scenario with a stated **+97% margin**, and
a comparison column for "what landlords currently pay elsewhere (e.g. ImmoScout24)" in the
€0.99M–€20M range. Both are illustrative additions for the pitch narrative, not derived
from a cited source the way the unit-economics above are:
- The 75,000-landlord figure and 50% capture rate are assumptions about Chleo's platform
  (which is itself fictional for this exercise) — treat them the same way as the
  200/2,000-landlord scenarios above: recompute-able placeholders, not researched numbers.
- The "what landlords currently pay" / ImmoScout24 comparison has no source behind it in
  this repo — don't cite it as a researched competitive figure without finding one first.
  See `presentation/README.md` for the full list of unsourced claims from the deck.

If this monetization scenario needs to go into a future graded deliverable as more than a
pitch illustration, it should get the same unit-cost-first treatment as the section above:
a real price-per-seat or take-rate assumption, clearly labeled, rather than a single
margin percentage.

## Assumptions table

| Assumption | Rationale |
|---|---|
| Illustrative volumes (200 / 2,000 landlords) are placeholders, not derived data | Chleo's actual platform size isn't known for this fictional pitch — the unit-economics section above is built to be recomputed once it is |
| ~2 documents/landlord/month | Landlords mostly own 1–2 properties (IW Köln *Vermieterreport 2026*) and generate roughly one rent/expense document per property per month |
| Pilot approach over full-rollout sizing | Matches the "run a one-workflow pilot, measure real costs and savings over one full cycle" best practice found in property-management AI ROI research |
| No dedicated new hire for the pilot | Reuses existing engineering capacity at a Medium-size company; a dedicated hire is a Round 2 discussion if the pilot succeeds |
| Self-hosted n8n, not n8n Cloud | Assumes the company already operates infrastructure for its listing platform; adjust if that's not the case |
| Human-review time isn't a company cost line | Review happens on the landlord's own time (self-service) in this design — see `n8n/workflow_documentation.md`. It becomes a real operating cost only if a future paid "concierge review" tier is added |
| Tableau Standard edition, not Enterprise | Enterprise's governance/Pulse features aren't needed for a single internal dashboard at pilot scale — revisit if the dashboard becomes customer-facing |
