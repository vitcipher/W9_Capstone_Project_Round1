"""
LangSmith monitoring sample for the Rent/Lease Document Extraction Assistant
(research/use_cases.md, use case 1; see also n8n/workflow.json and
app/streamlit_app.py, which this script's prompt/schema is kept in sync with).

Run this after setting OPENAI_API_KEY, LANGSMITH_API_KEY, and LANGSMITH_TRACING=true
in .env (copy from .env.example). It sends a small set of synthetic extraction
requests through the same prompt/schema used in production, traced to LangSmith,
so you can inspect exactly what the model saw and returned for each one -
including the one deliberately designed to trigger the low-confidence review path.

Note: these are lightweight TEXT stand-ins for what a vision-based extraction
would read from an actual document image/PDF (which the production n8n workflow
and Streamlit app send instead). Using plain text here keeps this monitoring
sample runnable standalone, without needing real synthetic document image/PDF
files as a prerequisite.
"""

import json
import os

from dotenv import load_dotenv
from langsmith import traceable
from openai import OpenAI

load_dotenv()

# Kept in sync with n8n/workflow.json and app/streamlit_app.py
CONFIDENCE_THRESHOLD = 0.70

SYSTEM_PROMPT = (
    "You extract structured data from German landlord documents. Return ONLY "
    "valid JSON with fields: document_type, category, confidence (0-1, your "
    "own honest estimate of extraction reliability for THIS document), and "
    "extracted_fields (an object). For rent receipts, EMI/mortgage "
    "statements, or Nebenkosten invoices, extracted_fields should include "
    "amount_eur, currency, issue_date. For rental contracts/lease "
    "agreements, extracted_fields should include tenant_name, "
    "landlord_name, property_address, monthly_rent_eur, deposit_eur, "
    "lease_start_date, lease_end_date_or_notice_period, special_clauses "
    "(array of strings). If a field cannot be read confidently, omit it "
    "rather than guessing."
)

# A small "dataset" of synthetic document text, standing in for what a
# vision-based read of an actual document would produce. Deliberately
# includes one messy/ambiguous sample to demonstrate the low-confidence
# review path, not just the easy cases - the point of this sample is to
# show both branches of the workflow's behavior, not just a happy path.
SAMPLE_DOCUMENTS = [
    {
        "name": "clean_rent_receipt",
        "document_type_hint": "rent_receipt",
        "document_text": (
            "MIETQUITTUNG\nMieter: Anna Muster\nObjekt: Musterstrasse 12, Berlin\n"
            "Zeitraum: August 2026\nKaltmiete: 782,00 EUR\nEingegangen am: 03.08.2026"
        ),
    },
    {
        "name": "clean_nebenkosten_invoice",
        "document_type_hint": "nebenkosten_invoice",
        "document_text": (
            "NEBENKOSTENABRECHNUNG\nObjekt: Beispielweg 4, Leipzig\n"
            "Abrechnungszeitraum: 01.2026\nBetrag: 158,40 EUR\nFaellig: 15.08.2026"
        ),
    },
    {
        "name": "clean_rental_contract_excerpt",
        "document_type_hint": "rental_contract",
        "document_text": (
            "MIETVERTRAG (Auszug)\nVermieter: Beispiel Immobilien GmbH\n"
            "Mieter: Jonas Beispiel\nMietobjekt: Probeallee 7, Muenchen\n"
            "Kaltmiete: 1.230,00 EUR/Monat\nKaution: 2.460,00 EUR\n"
            "Mietbeginn: 01.09.2026\nKuendigungsfrist: 3 Monate"
        ),
    },
    {
        "name": "messy_scan_low_confidence",
        "document_type_hint": "emi_statement",
        "document_text": (
            # Deliberately garbled/ambiguous, simulating a poor-quality scan -
            # this should produce a low confidence score and trip the review
            # threshold, the same way a real bad scan would.
            "K??DITR?TE ... Objek? Testri.. 21 ... Betr.g ??? EUR ... "
            "F?lli. am ..08.2026 (teilweise unleserlich)"
        ),
    },
]


@traceable(name="extract_document_fields", run_type="chain")
def extract_document_fields(document_type_hint: str, document_text: str) -> dict:
    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    response = client.responses.create(
        model="gpt-4.1",
        instructions=SYSTEM_PROMPT,
        input=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": (
                            f"Document type hint: {document_type_hint}. "
                            f"Document text:\n{document_text}\n\n"
                            "Extract the structured fields as JSON."
                        ),
                    }
                ],
            }
        ],
    )
    extracted = json.loads(response.output_text)
    confidence = extracted.get("confidence", 0)
    extracted["needs_human_review"] = confidence < CONFIDENCE_THRESHOLD
    return extracted


def main():
    project = os.environ.get("LANGSMITH_PROJECT", "(default)")
    print(f"Running {len(SAMPLE_DOCUMENTS)} sample extractions, traced to LangSmith "
          f"project '{project}'...\n")
    for sample in SAMPLE_DOCUMENTS:
        result = extract_document_fields(
            document_type_hint=sample["document_type_hint"],
            document_text=sample["document_text"],
        )
        flag = "NEEDS REVIEW" if result.get("needs_human_review") else "OK"
        print(f"[{flag}] {sample['name']}: confidence={result.get('confidence')}")
    print("\nDone. Open your LangSmith project to inspect the traces:")
    print("https://smith.langchain.com/")


if __name__ == "__main__":
    main()
