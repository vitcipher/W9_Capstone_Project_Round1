# Round 1 Decision

**Not yet fillable — this file needs the real presentation to happen first.** Everything
below except the last section is intentionally left blank rather than invented; slide 12
of `presentation/slides.html` says the same thing to the room. Fill in after presenting to
the teaching staff.

## Feedback summary (3–5 bullets)
- (what landed)
- (what confused people)
- (what felt risky)
- (whether the industry/use case should change)

## Decision: KEEP | CHANGE

## If CHANGE
What changed (industry / sector / size / use case / approach) and why:

## What I'll deepen in Round 2
*(Pre-filled from the research pack — adjust if the decision above is CHANGE rather than KEEP.)*
- **Use case:** the rent/expense/lease document extraction assistant (`research/use_cases.md`,
  use case 1) becomes a working MVP — document upload → AI draft → human confirmation →
  live portfolio dashboard, running end to end rather than a POC.
- **First idea for MVP scope:** harden the existing n8n workflow + Streamlit demo (auth,
  persistence, retry handling — see `n8n/workflow_documentation.md` "Limits vs.
  production") and run the pilot outlined in `cost_estimation/timeline_estimate.md`; use
  case 3 (market valuation, `research/use_cases.md`) stays a documented Round 2/pilot-phase
  stretch goal rather than being pulled into the MVP.
