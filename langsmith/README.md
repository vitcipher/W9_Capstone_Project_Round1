# LangSmith Monitoring Sample

## Status
**Script written, real OpenAI calls verified, LangSmith trace not yet captured.**
`run_monitoring_sample.py` was actually run against the live OpenAI API (not just
syntax-checked) and produced real, correct results — see "Verified so far" below. What's
missing is `LANGSMITH_API_KEY`, so no trace has actually landed in a LangSmith project yet.
Add it to `.env` (see `.env.example` — `LANGSMITH_API_KEY`, `LANGSMITH_PROJECT`,
`LANGSMITH_TRACING=true`) and re-run `python langsmith/run_monitoring_sample.py`, then
paste the resulting project link below.

## What was monitored
`run_monitoring_sample.py` wraps the same extraction logic used in `n8n/workflow.json` and
`app/streamlit_app.py` (same system prompt, same schema, same 0.70 confidence threshold —
kept in sync intentionally) with LangSmith's `@traceable` decorator, and runs it against 4
small synthetic samples:

| Sample | Document type | Designed to show |
|---|---|---|
| `clean_rent_receipt` | rent_receipt | A clean, high-confidence extraction |
| `clean_nebenkosten_invoice` | nebenkosten_invoice | Same, different document type/schema |
| `clean_rental_contract_excerpt` | rental_contract | The lease-specific field schema (tenant, deposit, dates) |
| `messy_scan_low_confidence` | emi_statement | A deliberately garbled input, to demonstrate the low-confidence review path actually triggering — not just the easy cases |

**Note on the inputs:** these are lightweight text stand-ins for what a vision-based read
of an actual document image/PDF would produce (the production n8n workflow and Streamlit
app send real document files, not text). Using text here keeps this monitoring sample
runnable on its own, without needing the synthetic document image/PDF files as a
prerequisite.

## Verified so far (actually run, not just written)
```
[OK] clean_rent_receipt: confidence=0.98
[OK] clean_nebenkosten_invoice: confidence=0.98
[OK] clean_rental_contract_excerpt: confidence=0.98
[NEEDS REVIEW] messy_scan_low_confidence: confidence=0.5
```
This confirms the extraction logic genuinely works end-to-end against the real OpenAI API,
and that the confidence-based review flag genuinely fires on a bad input rather than always
returning "OK" — real behavior, not a scripted demo.

## Link or export
- Dataset/experiment link (accessible to instructors): **TODO** — fill in after running
  with `LANGSMITH_API_KEY` set.
- If link sharing is blocked: run the script, then export/screenshot the trace view from
  the LangSmith project and attach it in this folder instead.

## What it shows about transparency/observability
This is the concrete answer to Chleo's "AI isn't transparent" concern: for every
extraction, LangSmith records exactly what the model was shown, what it returned, its
self-reported confidence, and latency — so a low-confidence or wrong extraction isn't a
mystery, it's inspectable. The `messy_scan_low_confidence` sample specifically demonstrates
that the system's review-routing isn't just a UI label — it's driven by a real, traceable
model output that can be pulled up and shown to a skeptical stakeholder.
