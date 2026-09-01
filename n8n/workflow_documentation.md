# n8n POC Documentation

## What it does
A landlord's app POSTs an uploaded document (a rental contract, rent receipt,
EMI/mortgage statement, or Nebenkosten invoice — base64-encoded, PDF or image) plus a
`property_id` to a webhook (in the fuller working prototype built alongside this pitch,
that caller is a Streamlit app — not included in this trimmed Round 1 submission; see
"How to run it" below for a standalone way to trigger it). The workflow
sends the document to OpenAI (via the Responses API, so PDFs can be sent directly without a
separate image-conversion step) with an extraction prompt, parses the structured JSON
response, applies a confidence threshold, and returns a **draft record** to the app for the
landlord to review and confirm — nothing is auto-saved to their books.

Trigger: `POST /webhook/document-upload` with
`{ property_id, document_type_hint, mime_type, file_base64 }`.

## Which use case it demonstrates
Use case 1 in `research/use_cases.md` — the Rent/Expense/EMI Document Extraction
Assistant.

## Why it fits
It's a single, narrow workflow (one trigger, one LLM call, one branch) that's honest about
what it can and can't do — exactly the "light POC" Round 1 asks for, and it directly
demonstrates the transparency story the pitch is built on (see
`research/opportunities_risks.md`, "Transparency considerations").

## Design decisions worth calling out

- **Confidence threshold is 0.70, not an arbitrary round number.** This matches the AI
  Index 2026's MortgageTax benchmark finding that no frontier model exceeds ~70% accuracy
  extracting structured data from real financial documents (see
  `research/sector_research.md`). Below that, the record is flagged as needing a closer
  look; above it, the landlord still confirms, just with a lighter-touch UI message.
- **Every path ends at a human, not a database write.** Both the "low confidence" and
  "high confidence" branches converge on `Return Draft Record to App` — the workflow's job
  ends at producing a reviewable draft. Saving to the landlord's actual books is a
  separate, human-triggered action deliberately kept outside this workflow, so the AI
  never silently writes financial data.
- **The model is asked to self-report its own confidence** (in the extraction prompt)
  rather than us inferring it after the fact — a simpler design for a Round 1 POC, with
  the known limitation that it relies on the model's own calibration rather than an
  independent check (see Limits below).

## Limits vs. production

- **Self-reported confidence isn't independently verified.** A production version would
  want a second, independent signal (e.g. a lightweight classifier, or cross-checking
  extracted totals against bank data) rather than trusting the same model's self-assessment.
- **No retry/error handling for a failed or malformed model response** beyond the basic
  `extraction_failed` status in the parsing code node — production would need retries,
  a dead-letter path, and alerting.
- **No authentication on the webhook.** Production needs the landlord's app to
  authenticate the request (e.g. a signed token) before this workflow processes anything.
- **Single document type per call.** A production version would likely batch multi-page
  documents or handle multiple documents per upload.
- **No persistence layer wired up.** The workflow returns the draft record to the caller;
  it doesn't write anywhere. A production version adds a database write *after* the
  landlord confirms, plus the LangSmith trace this POC's design assumes but doesn't wire
  up in this Round 1 slice (see `langsmith/README.md`).

## How to run it

1. Import `n8n/workflow.json` into n8n (Workflows → Import from File).
2. Create an HTTP Header Auth credential named to match `OpenAI API Key (Authorization:
   Bearer header)` in the `Extract Fields (OpenAI)` node, with header name
   `Authorization` and value `Bearer <your OpenAI API key>` — see `.env.example` (never
   commit real keys).
3. Activate the workflow and copy its webhook URL.
4. Trigger it directly with curl (or Postman/Insomnia):
```bash
curl -X POST https://<your-n8n-instance>/webhook/document-upload \
  -H "Content-Type: application/json" \
  -d '{"property_id":"P01","document_type_hint":"rent_receipt","mime_type":"application/pdf","file_base64":"<base64 PDF>"}'
```
Expected output: a JSON draft record with `extracted_fields`, `confidence`,
`needs_human_review`, and a `ui_message` telling the reviewer what to check.

(In the fuller working prototype built alongside this pitch, a Streamlit app is the
actual caller — upload a document in its UI instead of hand-building the curl payload.
That app isn't included in this trimmed Round 1 submission repo.)

## Screenshots
Add annotated screenshots here once you've run it against a real (synthetic) sample
document — a good pair to include: one high-confidence extraction and one that gets
flagged for review, to show the branching behavior.
