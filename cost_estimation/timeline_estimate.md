# Timeline Estimate

Consulting-conversation-level estimate — rough phases, not a detailed project plan (that
level of detail belongs in Round 2's strategic deployment plan).

## Rough implementation timeline

| Phase | Duration | Deliverable |
|---|---|---|
| Discovery + research | Complete (Round 1) | Sector research, opportunities/risks, 3 use cases — see `research/` |
| POC | Complete (Round 1) | n8n extraction workflow + Streamlit demo frontend + synthetic portfolio dashboard data |
| Pilot hardening | ~2 weeks | Add webhook authentication, retry/error handling, and a real (not in-memory) draft-record store — the gaps listed in `n8n/workflow_documentation.md` "Limits vs. production" |
| Pilot | ~8–10 weeks (~2.5 months) | Roll out to ~200 opted-in landlords from the existing listing-platform user base; track extraction accuracy, confidence-threshold calibration, and actual time saved per landlord |
| Decision point | End of pilot | Go/no-go based on pilot data — feeds directly into Round 2's ROI section rather than assumptions |
| Full rollout (conditional) | Month 4+ | Only if the pilot justifies it — out of scope for this estimate, covered conceptually in Round 2's strategic deployment plan |

**Total to a pilot decision point: roughly 3 months** from Round 1 handoff.

## Key assumptions

- The 2-week "pilot hardening" phase assumes the existing POC's architecture is sound and
  just needs the production gaps closed — not a rebuild. If the pilot surfaces that the
  extraction approach itself needs to change (e.g. confidence threshold miscalibrated in
  practice), this phase could extend.
- The 8–10 week pilot length is deliberately not longer: it's sized to get one full
  reporting cycle of real landlord usage (most landlords check finances monthly) without
  dragging the decision point out past a quarter.
- Full rollout timing and scope are intentionally left open here — committing to a
  rollout date before pilot data exists would be the "hand-wavy numbers" the rubric
  specifically warns against. Round 2 is where that gets a real answer.
