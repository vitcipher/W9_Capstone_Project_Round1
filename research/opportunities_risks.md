# Opportunities & Risks

## Opportunities

| Opportunity | Why it fits this sector/size | Rough impact |
|---|---|---|
| Cross-sell a PM module to an existing landlord user base | Chleo's company already has the target customer as listing-platform users — no new customer acquisition needed to launch | Low-cost distribution; fastest path to first users |
| Automate rent/expense/EMI/Nebenkosten bookkeeping | ~75% of private landlords own ≤2 units and treat rental income as a side activity (Vermieterreport 2026) — they lack time/expertise for proper books | Addresses the #1 real pain point of the actual majority customer, not a hypothetical power user |
| Portfolio P&L visibility | Landlords currently estimate profitability informally; hidden costs (maintenance reserve, management fees) are easy to miss | Can reveal properties that look profitable (rent > EMI) but aren't once full costs are counted — a genuinely useful, non-obvious insight |
| Use Chleo's own listing data for valuation/market comps | The company already holds the comps data (its own listings) that a standalone PropTech competitor would have to buy or scrape | Differentiator vs. generic bookkeeping apps |
| Ride a structurally growing market | Private landlord households: 3.7M (2010, 10% of pop.) → 5.5M+ (2022, 13%); renter share of the population also rising (58% of households, Zensus 2022) | Market is growing on both the supply side (more landlords) and demand side (more renters), independent of the product itself |
| Close a documented trust gap | 78% of property managers don't trust their current software's AI (AppFolio 2026); AI adopters see 31% vs. 12% portfolio growth | A transparent, honestly-caveated tool is a differentiator, not just a feature — directly answers Chleo's own "AI isn't transparent" fear |

## Risks

| Risk | Category | Mitigation |
|---|---|---|
| Document extraction isn't reliable enough to fully automate | Technical | AI Index 2026's MortgageTax benchmark: best frontier model tops out at 69.4% accuracy extracting structured data from real financial documents, none break 70%. Design as a draft-then-review assistant, not autonomous data entry — state this limit explicitly rather than overselling |
| Uploaded documents are sensitive financial data (bank/mortgage statements) | Regulatory / ethical | GDPR applies directly (legal basis, DPIA candidate, third-party processor question if an LLM API is used) — deep dive is a Round 2 deliverable; Round 1 should acknowledge it up front. **Note:** the presented deck states "Risk is low as the system will be GDPR compliant" — that's stronger than what's actually been verified (no DPIA or compliance analysis has been done yet); the hedged version in this row is the accurate one, see `presentation/README.md` |
| Low landlord willingness to pay / low tech sophistication | Operational | Target customer is non-professional and price-sensitive (rental income is negligible/minor for 55%+ per Vermieterreport). Keep the MVP lightweight; don't build for power users who don't represent the majority |
| Cost and data-security concerns are the most-cited adoption barriers in adjacent finance-AI contexts (both 43%, BILL) | Operational | Lead with transparency about what the tool does/doesn't do with data; keep architecture simple enough to explain in plain language |
| Scope creep toward tenant-facing decisions (e.g. screening) | Regulatory / ethical | Out of scope for this pitch. Colorado's AI Act (2024) explicitly names housing decisions as a discrimination-risk domain alongside hiring and medical care — a clear signal that anything touching *who gets housing* is a much higher-risk category than *how an owner tracks their own numbers*. State this boundary explicitly rather than letting it drift into scope later |
| Regulatory environment for German rental market generally | Regulatory | Doesn't block a bookkeeping tool directly, but private landlords behave cautiously under Mietpreisbremse and tenant-protection law — worth knowing as context, not a blocker |

## Transparency considerations

Chleo's core fear is that "AI isn't transparent." This pitch answers that on three levels:

1. **The use case itself is inherently explainable.** A tool that extracts fields from a
   document and shows its work (which document, which field, what confidence) is far
   easier to reason about than a black-box recommendation engine — the AI's job is
   narrow and checkable.
2. **We state the technical limit out loud, with a citation.** Rather than claim the
   extraction is accurate, the pitch leads with the MortgageTax benchmark finding (no
   frontier model exceeds ~70% on real financial-document extraction) and designs the
   workflow around it — a human reviews and confirms before anything is saved. Showing
   Chleo the failure mode we designed around is more convincing than a demo that hides it.
3. **LangSmith monitoring makes the AI's behavior inspectable**, not just its output —
   the dashboard doesn't just show a P&L number, it shows what was AI-extracted vs.
   human-confirmed, which is the concrete answer to "how would I know if it's wrong."
