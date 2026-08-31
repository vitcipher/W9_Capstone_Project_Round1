"""
Round 1 POC frontend - two tabs.

Tab 1, Document Extraction (research/use_cases.md, use case 1): upload a
document, AI drafts structured fields, human confirms before anything is
saved. Human-in-the-loop by design: nothing is ever auto-saved. Two
extraction backends are supported:
  - "n8n webhook" (default) - calls the actual n8n/workflow.json POC, so this
    app is a real client of that workflow, not a separate reimplementation.
  - "Direct OpenAI API" - bypasses n8n, for quick local testing without
    standing up an n8n instance. Uses the same model/prompt as the n8n
    workflow's OpenAI Responses API call; keep the two in sync if you edit
    either one.

Tab 2, Maintenance Requests: plain CRUD, no AI involved - a landlord submits
a request, statuses get updated inline. Seeded from
data/synthetic_maintenance_requests.csv; edits live only in this session
(same in-memory pattern as the extraction tab's confirmed records, not a
real database). Scoped deliberately small - see the "buildable in 3 days"
assessment that motivated this feature: it's the one must-have from the
competitive feature landscape that needed zero new external integrations.
"""

import base64
import json
import os
from datetime import datetime
from pathlib import Path

import pandas as pd
import requests
import streamlit as st

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
PORTFOLIO_PATH = DATA_DIR / "synthetic_landlord_portfolio.csv"
MAINTENANCE_SEED_PATH = DATA_DIR / "synthetic_maintenance_requests.csv"

MAINTENANCE_STATUSES = ["New", "In Progress", "Resolved"]
MAINTENANCE_URGENCIES = ["Low", "Medium", "High"]

DOCUMENT_TYPES = {
    "Rental contract / lease agreement": "rental_contract",
    "Rent receipt": "rent_receipt",
    "EMI / mortgage statement": "emi_statement",
    "Nebenkosten invoice": "nebenkosten_invoice",
}

# Kept in sync with n8n/workflow.json's confidence threshold - see
# research/sector_research.md for why 0.70 specifically (AI Index 2026,
# MortgageTax benchmark: no frontier model exceeds ~70% on real financial-
# document extraction).
CONFIDENCE_THRESHOLD = 0.70

# Kept in sync with the "instructions" string in n8n/workflow.json's
# "Extract Fields (OpenAI)" node.
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

st.set_page_config(page_title="Document Extraction Assistant", page_icon="🏠", layout="wide")


@st.cache_data
def load_portfolio() -> pd.DataFrame:
    if PORTFOLIO_PATH.exists():
        return pd.read_csv(PORTFOLIO_PATH)
    return pd.DataFrame()


def load_maintenance_seed() -> pd.DataFrame:
    """Loaded once into session_state, not cached - the working copy is mutable
    (new requests added, statuses updated) and lives only for this session, same
    pattern as confirmed_records below."""
    if MAINTENANCE_SEED_PATH.exists():
        return pd.read_csv(MAINTENANCE_SEED_PATH)
    return pd.DataFrame(columns=["request_id", "property_id", "description", "urgency", "status", "created_date"])


def next_request_id(df: pd.DataFrame) -> str:
    if df.empty:
        return "MR001"
    nums = df["request_id"].str.extract(r"MR(\d+)").astype(int)[0]
    return f"MR{nums.max() + 1:03d}"


def call_n8n_webhook(url: str, payload: dict) -> dict:
    resp = requests.post(url, json=payload, timeout=90)
    resp.raise_for_status()
    return resp.json()


def call_openai_directly(payload: dict) -> dict:
    from openai import OpenAI

    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY not set - add it to your .env")

    client = OpenAI(api_key=api_key)
    data_uri = f"data:{payload['mime_type']};base64,{payload['file_base64']}"

    if payload["mime_type"] == "application/pdf":
        file_block = {"type": "input_file", "filename": "upload.pdf", "file_data": data_uri}
    else:
        file_block = {"type": "input_image", "image_url": data_uri}

    response = client.responses.create(
        model="gpt-4.1",
        instructions=SYSTEM_PROMPT,
        input=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": f"Document type hint: {payload['document_type_hint']}. "
                        "Extract the structured fields as JSON.",
                    },
                    file_block,
                ],
            }
        ],
    )

    extracted = json.loads(response.output_text)
    confidence = extracted.get("confidence", 0)
    needs_review = confidence < CONFIDENCE_THRESHOLD
    return {
        **extracted,
        "property_id": payload["property_id"],
        "needs_human_review": needs_review,
        "review_reason": (
            f"Confidence {confidence} below {CONFIDENCE_THRESHOLD} threshold" if needs_review else None
        ),
    }


st.title("🏠 Property Ledger — Round 1 POC")
st.caption(
    "Two features in this demo: document extraction (upload → AI draft → human "
    "confirmation) and maintenance request tracking. Nothing in either tab auto-saves "
    "beyond this browser session."
)

portfolio = load_portfolio()

if "maintenance_requests" not in st.session_state:
    st.session_state.maintenance_requests = load_maintenance_seed()

tab_extract, tab_maintenance = st.tabs(["📄 Document Extraction", "🔧 Maintenance Requests"])

with st.sidebar:
    st.header("Settings")
    backend = st.radio(
        "Extraction backend",
        ["n8n webhook", "Direct OpenAI API (no n8n needed)"],
        index=0,
        help="n8n webhook calls the actual n8n/workflow.json POC. Direct mode bypasses "
        "n8n for quick local testing and needs OPENAI_API_KEY in your .env.",
    )
    n8n_url = ""
    if backend == "n8n webhook":
        n8n_url = st.text_input(
            "n8n webhook URL",
            value=os.environ.get("N8N_WEBHOOK_URL", "http://localhost:5678/webhook/document-upload"),
        )
    st.markdown("---")
    st.caption(
        f"Confidence threshold: **{CONFIDENCE_THRESHOLD}** — matches the AI Index 2026 "
        "MortgageTax benchmark ceiling cited in the research pack, not an arbitrary number."
    )

with tab_extract:
    if "confirmed_records" not in st.session_state:
        st.session_state.confirmed_records = []
    if "last_result" not in st.session_state:
        st.session_state.last_result = None

    col1, col2 = st.columns(2)
    with col1:
        if not portfolio.empty:
            property_label = st.selectbox(
                "Property",
                portfolio.apply(lambda r: f"{r['property_id']} — {r['nickname']} ({r['city']})", axis=1),
            )
            property_id = property_label.split(" — ")[0]
        else:
            property_id = st.text_input("Property ID", value="P01")
    with col2:
        doc_type_label = st.selectbox("Document type", list(DOCUMENT_TYPES.keys()))
        document_type_hint = DOCUMENT_TYPES[doc_type_label]

    uploaded_file = st.file_uploader("Upload document", type=["pdf", "png", "jpg", "jpeg"])
    if uploaded_file is not None:
        st.caption(f"{uploaded_file.name} — {uploaded_file.size / 1024:.1f} KB")

    if st.button("Extract with AI", type="primary", disabled=uploaded_file is None):
        file_bytes = uploaded_file.read()
        mime_type = uploaded_file.type or (
            "application/pdf" if uploaded_file.name.lower().endswith(".pdf") else "image/png"
        )
        payload = {
            "property_id": property_id,
            "document_type_hint": document_type_hint,
            "mime_type": mime_type,
            "file_base64": base64.b64encode(file_bytes).decode("utf-8"),
        }
        with st.spinner("Extracting..."):
            try:
                if backend == "n8n webhook":
                    st.session_state.last_result = call_n8n_webhook(n8n_url, payload)
                else:
                    st.session_state.last_result = call_openai_directly(payload)
            except Exception as exc:  # noqa: BLE001 - surface any backend error to the reviewer
                st.error(f"Extraction failed: {exc}")
                st.session_state.last_result = None

    result = st.session_state.last_result
    if result:
        st.subheader("Draft extraction — please review")
        confidence = result.get("confidence")
        if result.get("needs_human_review"):
            st.warning(
                f"⚠️ Low confidence ({confidence}). {result.get('review_reason', '')} "
                "Please check every field carefully before confirming."
            )
        else:
            st.success(f"✅ High confidence ({confidence}). Please glance over the fields below, then confirm.")

        extracted_fields = result.get("extracted_fields", {})
        edited_fields = {}
        for key, value in extracted_fields.items():
            if isinstance(value, list):
                edited_text = st.text_area(key, value="\n".join(str(v) for v in value))
                edited_fields[key] = [line for line in edited_text.split("\n") if line.strip()]
            else:
                edited_fields[key] = st.text_input(key, value=str(value))

        if st.button("✅ Confirm & Save (this session only)"):
            st.session_state.confirmed_records.append(
                {
                    "property_id": result.get("property_id", property_id),
                    "document_type": document_type_hint,
                    "confirmed_at": datetime.now().isoformat(timespec="seconds"),
                    **edited_fields,
                }
            )
            st.session_state.last_result = None
            st.rerun()

    if st.session_state.confirmed_records:
        st.subheader("Confirmed records (this session)")
        st.caption(
            "In-memory demo table only. In the real MVP this would write to the landlord's "
            "portfolio database, feeding the P&L dashboard."
        )
        st.dataframe(pd.DataFrame(st.session_state.confirmed_records))

with tab_maintenance:
    st.caption(
        "Plain CRUD, no AI involved — seeded from data/synthetic_maintenance_requests.csv, "
        "edits live only in this browser session (same in-memory pattern as the extraction "
        "tab's confirmed records, not a database)."
    )

    mreq = st.session_state.maintenance_requests

    status_counts = mreq["status"].value_counts()
    metric_cols = st.columns(len(MAINTENANCE_STATUSES))
    for col, status in zip(metric_cols, MAINTENANCE_STATUSES):
        col.metric(status, int(status_counts.get(status, 0)))

    st.divider()

    filter_col1, filter_col2 = st.columns(2)
    with filter_col1:
        property_filter = st.multiselect(
            "Filter by property", sorted(mreq["property_id"].unique()), default=[]
        )
    with filter_col2:
        status_filter = st.multiselect("Filter by status", MAINTENANCE_STATUSES, default=[])

    filtered = mreq.copy()
    if property_filter:
        filtered = filtered[filtered["property_id"].isin(property_filter)]
    if status_filter:
        filtered = filtered[filtered["status"].isin(status_filter)]

    st.caption("Update status directly in the table below — changes apply immediately.")
    edited = st.data_editor(
        filtered,
        column_config={
            "request_id": st.column_config.TextColumn("ID", disabled=True),
            "property_id": st.column_config.TextColumn("Property", disabled=True),
            "description": st.column_config.TextColumn("Description", disabled=True, width="large"),
            "urgency": st.column_config.SelectboxColumn("Urgency", options=MAINTENANCE_URGENCIES),
            "status": st.column_config.SelectboxColumn("Status", options=MAINTENANCE_STATUSES),
            "created_date": st.column_config.TextColumn("Created", disabled=True),
        },
        hide_index=True,
        use_container_width=True,
        key="maintenance_editor",
    )
    # Write edits (urgency/status changes) back into the full (unfiltered) session table
    if not edited.equals(filtered):
        st.session_state.maintenance_requests.update(edited)
        st.rerun()

    st.divider()
    st.subheader("Submit a new request")
    with st.form("new_maintenance_request", clear_on_submit=True):
        req_col1, req_col2 = st.columns(2)
        with req_col1:
            if not portfolio.empty:
                new_property_label = st.selectbox(
                    "Property",
                    portfolio.apply(lambda r: f"{r['property_id']} — {r['nickname']} ({r['city']})", axis=1),
                    key="new_request_property",
                )
                new_property_id = new_property_label.split(" — ")[0]
            else:
                new_property_id = st.text_input("Property ID", value="P01", key="new_request_property_id")
        with req_col2:
            new_urgency = st.selectbox("Urgency", MAINTENANCE_URGENCIES, index=1)
        new_description = st.text_area("What's the issue?")
        submitted = st.form_submit_button("Submit request")
        if submitted:
            if not new_description.strip():
                st.error("Please describe the issue before submitting.")
            else:
                new_row = pd.DataFrame([{
                    "request_id": next_request_id(st.session_state.maintenance_requests),
                    "property_id": new_property_id,
                    "description": new_description.strip(),
                    "urgency": new_urgency,
                    "status": "New",
                    "created_date": datetime.now().strftime("%Y-%m-%d"),
                }])
                st.session_state.maintenance_requests = pd.concat(
                    [st.session_state.maintenance_requests, new_row], ignore_index=True
                )
                st.success("Request submitted.")
                st.rerun()
