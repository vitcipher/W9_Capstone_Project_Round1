# LangSmith Monitoring Sample

## Status
**Done — real trace captured and verified.** `run_monitoring_sample.py` ran against the
live OpenAI API and all 4 runs were confirmed present in LangSmith via the API (not just
inferred from an absence of errors) — session `capstone-round1-property-extraction`,
4/4 runs with `status: success` and real outputs.

**Setup gotcha worth documenting:** if your LangSmith workspace is EU-hosted, the default
`LANGSMITH_API_KEY` alone isn't enough — the SDK talks to `api.smith.langchain.com` (US) by
default, and a EU-workspace key gets a **403 Forbidden** there even though the key itself
is valid. Fix: also set `LANGSMITH_ENDPOINT=https://eu.api.smith.langchain.com` in `.env`.
This cost real debugging time (confirmed by curl-testing the same key against both hosts —
US: 403, EU: 200 — before it was clear this was a region mismatch, not a bad key), so it's
called out explicitly here and in `.env.example` rather than left to be rediscovered.

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
- Project name: `capstone-round1-property-extraction` — open in the LangSmith web UI at
  **eu.smith.langchain.com** (note the `eu.` — the EU workspace, matching the endpoint
  above) → Projects → search by that name.
- **TODO:** if instructors need direct link access without a LangSmith login on this
  workspace, either invite them to the workspace or export/screenshot the trace view and
  attach it in this folder instead — LangSmith projects aren't public by default.

## What it shows about transparency/observability
This is the concrete answer to Chleo's "AI isn't transparent" concern: for every
extraction, LangSmith records exactly what the model was shown, what it returned, its
self-reported confidence, and latency — so a low-confidence or wrong extraction isn't a
mystery, it's inspectable. The `messy_scan_low_confidence` sample specifically demonstrates
that the system's review-routing isn't just a UI label — it's driven by a real, traceable
model output that can be pulled up and shown to a skeptical stakeholder.
