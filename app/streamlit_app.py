"""
Property Ledger — frontend, now with real auth + persistence.

Auth + persistence: landlords sign up / log in via Supabase Auth. Every
table (properties, tenants, documents, maintenance_requests,
monthly_transactions) has an owner_id scoped by Postgres Row Level
Security (see supabase/schema.sql) - so one landlord's data is private
from another at the database layer, not just filtered in this file.
Setup: create a Supabase project, run supabase/schema.sql in its SQL
Editor, set SUPABASE_URL/SUPABASE_ANON_KEY in .env. See app/db.py.

Tab 1, Document Extraction (research/use_cases.md, use case 1): upload a
document, AI drafts structured fields, human confirms before anything is
saved to the documents table. Human-in-the-loop by design: nothing is
ever auto-saved. Two extraction backends are supported:
  - "n8n webhook" (default) - calls the actual n8n/workflow.json POC, so this
    app is a real client of that workflow, not a separate reimplementation.
  - "Direct OpenAI API" - bypasses n8n, for quick local testing without
    standing up an n8n instance. Uses the same model/prompt as the n8n
    workflow's OpenAI Responses API call; keep the two in sync if you edit
    either one.

Tab 2, Maintenance Requests: plain CRUD, no AI involved - now backed by
the maintenance_requests table (was session_state-only in the earlier
POC). It's the one must-have from the competitive feature landscape that
needed zero new external integrations - see the "buildable in 3 days"
assessment that motivated it.

Tab 3, Bank Feed: the deliberate exception to "no new integrations" - a
real PSD2-style open banking connection via Enable Banking's Mock ASPSP
(fake test bank, no real bank account needed). See app/bank_feed.py for
the auth flow and README/.env.example for setup. Explicitly a stretch
feature, not a Round 1 core deliverable - stays session-only for now,
not yet written to Supabase.

Not yet migrated - a clear next step, not silently skipped: the
monthly_transactions and tenants tables exist in supabase/schema.sql but
have no UI here yet.
"""

import base64
import json
import os
from pathlib import Path

import bank_feed
import db
import pandas as pd
import requests
import streamlit as st

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
DEMO_PORTFOLIO_PATH = DATA_DIR / "synthetic_landlord_portfolio.csv"

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

st.set_page_config(page_title="Property Ledger", page_icon="🏠", layout="wide")


def _to_native(value):
    """Pandas/numpy scalars (int64, float64, ...) aren't JSON-serializable
    as-is, which breaks Supabase inserts silently-ish (a confusing
    serialization error, not an obvious one) - convert to plain Python
    types before sending, and NaN to None."""
    if pd.isna(value):
        return None
    return value.item() if hasattr(value, "item") else value


def load_demo_portfolio_csv() -> pd.DataFrame:
    """The original synthetic 8-property seed - now used only to populate a
    brand-new Supabase account on request, not as the app's live data source."""
    if DEMO_PORTFOLIO_PATH.exists():
        return pd.read_csv(DEMO_PORTFOLIO_PATH)
    return pd.DataFrame()


def get_properties_df(client, owner_id: str) -> pd.DataFrame:
    rows = db.list_properties(client, owner_id)
    return pd.DataFrame(rows) if rows else pd.DataFrame()


def get_maintenance_df(client, owner_id: str) -> pd.DataFrame:
    rows = db.list_maintenance_requests(client, owner_id)
    return pd.DataFrame(rows) if rows else pd.DataFrame(
        columns=["id", "property_id", "description", "urgency", "status", "created_date"]
    )


def get_documents_df(client, owner_id: str) -> pd.DataFrame:
    rows = db.list_documents(client, owner_id)
    return pd.DataFrame(rows) if rows else pd.DataFrame()


def property_selector(properties_df: pd.DataFrame, key: str, label: str = "Property"):
    """Returns the selected property's UUID id, or None if there are no properties."""
    if properties_df.empty:
        return None
    options = {row["id"]: f"{row['nickname']} ({row['city']})" for _, row in properties_df.iterrows()}
    return st.selectbox(label, list(options.keys()), format_func=lambda pid: options[pid], key=key)


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


# ==================================================================
# Auth gate - nothing below this renders until Supabase is configured
# and the visitor is logged in.
# ==================================================================

if not db.is_configured():
    st.title("🏠 Property Ledger")
    st.error(
        "**Supabase not configured.** Create a project at "
        "[supabase.com](https://supabase.com), run `supabase/schema.sql` in its SQL "
        "Editor, then set `SUPABASE_URL` and `SUPABASE_ANON_KEY` in `.env`."
    )
    st.stop()

if "sb_client" not in st.session_state:
    st.session_state.sb_client = db.new_client()
if "sb_user" not in st.session_state:
    st.session_state.sb_user = None

sb = st.session_state.sb_client

if st.session_state.sb_user is None:
    st.title("🏠 Property Ledger")
    st.caption(
        "Sign in to continue. Your properties, documents, and maintenance requests are "
        "private to your account — enforced at the database level via Postgres Row "
        "Level Security, not just filtered in this app."
    )
    mode = st.radio("Mode", ["Log in", "Sign up"], horizontal=True, label_visibility="collapsed")
    with st.form("auth_form"):
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button(mode)
        if submitted:
            if not email or not password:
                st.error("Enter both email and password.")
            else:
                try:
                    if mode == "Sign up":
                        resp = db.sign_up(sb, email, password)
                        if resp.session is None:
                            st.info(
                                "Account created. If your Supabase project requires email "
                                'confirmation, check your inbox, then switch to "Log in".'
                            )
                        else:
                            st.session_state.sb_user = resp.user
                            st.rerun()
                    else:
                        resp = db.sign_in(sb, email, password)
                        st.session_state.sb_user = resp.user
                        st.rerun()
                except Exception as exc:  # noqa: BLE001
                    st.error(f"{mode} failed: {exc}")
    st.stop()

owner_id = st.session_state.sb_user.id

with st.sidebar:
    st.caption(f"Logged in as **{st.session_state.sb_user.email}**")
    if st.button("Log out"):
        db.sign_out(sb)
        st.session_state.sb_user = None
        st.session_state.pop("sb_client", None)
        st.rerun()
    st.divider()

# ==================================================================
# Main app (logged in)
# ==================================================================

st.title("🏠 Property Ledger")
st.caption(
    "Document extraction (upload → AI draft → human confirmation) and maintenance "
    "request tracking are saved to your account. The bank-feed connection stays "
    "session-only."
)

portfolio = get_properties_df(sb, owner_id)

if portfolio.empty:
    st.info("No properties yet.")
    if st.button("Load demo portfolio (8 example properties)"):
        demo_df = load_demo_portfolio_csv()
        if demo_df.empty:
            st.error("Demo seed file not found at data/synthetic_landlord_portfolio.csv.")
        else:
            with st.spinner("Creating demo properties..."):
                for _, row in demo_df.drop(columns=["property_id"], errors="ignore").iterrows():
                    fields = {k: _to_native(v) for k, v in row.items()}
                    db.create_property(sb, owner_id, **fields)
            st.rerun()

tab_extract, tab_maintenance, tab_bank = st.tabs(
    ["📄 Document Extraction", "🔧 Maintenance Requests", "🏦 Bank Feed"]
)

with st.sidebar:
    st.header("Extraction settings")
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
    if "last_result" not in st.session_state:
        st.session_state.last_result = None

    col1, col2 = st.columns(2)
    with col1:
        selected_property_id = property_selector(portfolio, key="extract_property")
    with col2:
        doc_type_label = st.selectbox("Document type", list(DOCUMENT_TYPES.keys()))
        document_type_hint = DOCUMENT_TYPES[doc_type_label]

    uploaded_file = st.file_uploader(
        "Upload document", type=["pdf", "png", "jpg", "jpeg"], disabled=portfolio.empty
    )
    if uploaded_file is not None:
        st.caption(f"{uploaded_file.name} — {uploaded_file.size / 1024:.1f} KB")

    if st.button(
        "Extract with AI", type="primary", disabled=uploaded_file is None or selected_property_id is None
    ):
        file_bytes = uploaded_file.read()
        mime_type = uploaded_file.type or (
            "application/pdf" if uploaded_file.name.lower().endswith(".pdf") else "image/png"
        )
        payload = {
            "property_id": selected_property_id,
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

        if st.button("✅ Confirm & Save"):
            db.create_document(
                sb,
                owner_id,
                property_id=result.get("property_id", selected_property_id),
                document_type=document_type_hint,
                extracted_fields=edited_fields,
                confidence=confidence,
                needs_human_review=result.get("needs_human_review", False),
            )
            st.session_state.last_result = None
            st.success("Saved to your account.")
            st.rerun()

    documents_df = get_documents_df(sb, owner_id)
    if not documents_df.empty:
        st.subheader("Confirmed documents")
        st.caption("Saved to your account (documents table) — persists across sessions.")
        st.dataframe(documents_df, use_container_width=True)

with tab_maintenance:
    st.caption(
        "Plain CRUD, no AI involved — saved to your account (maintenance_requests "
        "table), persists across sessions."
    )

    if portfolio.empty:
        st.info("Add properties first (above) before creating maintenance requests.")
    else:
        mreq = get_maintenance_df(sb, owner_id)

        status_counts = mreq["status"].value_counts() if not mreq.empty else pd.Series(dtype=int)
        metric_cols = st.columns(len(MAINTENANCE_STATUSES))
        for col, status in zip(metric_cols, MAINTENANCE_STATUSES):
            col.metric(status, int(status_counts.get(status, 0)))

        st.divider()

        if not mreq.empty:
            id_to_label = {row["id"]: row["nickname"] for _, row in portfolio.iterrows()}
            mreq = mreq.copy()
            mreq["property"] = mreq["property_id"].map(id_to_label)

            filter_col1, filter_col2 = st.columns(2)
            with filter_col1:
                property_filter = st.multiselect(
                    "Filter by property", sorted(mreq["property"].dropna().unique()), default=[]
                )
            with filter_col2:
                status_filter = st.multiselect("Filter by status", MAINTENANCE_STATUSES, default=[])

            filtered = mreq.copy()
            if property_filter:
                filtered = filtered[filtered["property"].isin(property_filter)]
            if status_filter:
                filtered = filtered[filtered["status"].isin(status_filter)]

            st.caption("Update status directly in the table below — changes save immediately.")
            display_cols = ["property", "description", "urgency", "status", "created_date"]
            indexed = filtered.set_index("id")[display_cols]
            edited = st.data_editor(
                indexed,
                column_config={
                    "property": st.column_config.TextColumn("Property", disabled=True),
                    "description": st.column_config.TextColumn("Description", disabled=True, width="large"),
                    "urgency": st.column_config.SelectboxColumn("Urgency", options=MAINTENANCE_URGENCIES),
                    "status": st.column_config.SelectboxColumn("Status", options=MAINTENANCE_STATUSES),
                    "created_date": st.column_config.TextColumn("Created", disabled=True),
                },
                hide_index=True,
                use_container_width=True,
                key="maintenance_editor",
            )
            changed_ids = [
                req_id
                for req_id in indexed.index
                if edited.loc[req_id, "urgency"] != indexed.loc[req_id, "urgency"]
                or edited.loc[req_id, "status"] != indexed.loc[req_id, "status"]
            ]
            if changed_ids:
                for req_id in changed_ids:
                    db.update_maintenance_request(
                        sb,
                        req_id,
                        urgency=edited.loc[req_id, "urgency"],
                        status=edited.loc[req_id, "status"],
                    )
                st.rerun()

        st.divider()
        st.subheader("Submit a new request")
        with st.form("new_maintenance_request", clear_on_submit=True):
            req_col1, req_col2 = st.columns(2)
            with req_col1:
                new_property_id = property_selector(portfolio, key="new_request_property")
            with req_col2:
                new_urgency = st.selectbox("Urgency", MAINTENANCE_URGENCIES, index=1)
            new_description = st.text_area("What's the issue?")
            submitted = st.form_submit_button("Submit request")
            if submitted:
                if not new_description.strip():
                    st.error("Please describe the issue before submitting.")
                else:
                    db.create_maintenance_request(
                        sb,
                        owner_id,
                        property_id=new_property_id,
                        description=new_description.strip(),
                        urgency=new_urgency,
                        status="New",
                    )
                    st.success("Request submitted.")
                    st.rerun()

with tab_bank:
    st.caption(
        "Real PSD2-style open banking via Enable Banking's Mock ASPSP (fake test bank, no "
        "real bank account needed). A deliberate stretch feature beyond Round 1's core "
        "scope — see app/bank_feed.py for the auth flow, README/.env.example for setup. "
        "Session-only for now, not yet written to Supabase."
    )

    REDIRECT_URL = os.environ.get("ENABLE_BANKING_REDIRECT_URL", "http://localhost:8501")

    if not bank_feed.is_configured():
        st.warning(
            "**Not configured yet.**\n\n"
            f"1. Register an app at [enablebanking.com/cp/applications](https://enablebanking.com/cp/applications) "
            f"with redirect URL `{REDIRECT_URL}`\n"
            "2. In the Control Panel, add some test accounts/transactions under the **Mock ASPSP** tab\n"
            "3. Add `ENABLE_BANKING_APP_ID` and `ENABLE_BANKING_PRIVATE_KEY_PATH` to `.env`, then reload this page"
        )
    else:
        if "bank_accounts" not in st.session_state:
            st.session_state.bank_accounts = None

        # Handle the consent-flow callback: Enable Banking redirects the user
        # back here with ?code=...&state=... after "authorizing" at the (mock) bank.
        query_params = st.query_params
        if "code" in query_params and st.session_state.bank_accounts is None:
            with st.spinner("Completing bank connection..."):
                try:
                    session = bank_feed.create_session(query_params["code"])
                    st.session_state.bank_accounts = session.get("accounts", [])
                    st.query_params.clear()
                    st.success(f"Connected — {len(st.session_state.bank_accounts)} account(s) found.")
                except Exception as exc:  # noqa: BLE001
                    st.error(f"Failed to complete connection: {exc}")

        if not st.session_state.bank_accounts:
            with st.expander("Find your Mock ASPSP's exact name (needed below)"):
                discover_country = st.text_input("Country code", value="DE", key="discover_country")
                if st.button("Discover banks"):
                    try:
                        aspsps = bank_feed.list_aspsps(discover_country)
                        st.dataframe(pd.DataFrame(aspsps))
                    except Exception as exc:  # noqa: BLE001
                        st.error(f"Could not list banks: {exc}")

            st.subheader("Connect a bank")
            conn_col1, conn_col2 = st.columns(2)
            with conn_col1:
                aspsp_name = st.text_input(
                    "Bank name (exact — from Discover banks above, or your Control Panel's Mock ASPSP tab)",
                    placeholder="e.g. Mock ASPSP",
                )
            with conn_col2:
                aspsp_country = st.text_input("Bank country code", value="DE")

            if st.button("Start authorization", type="primary", disabled=not aspsp_name):
                try:
                    auth = bank_feed.start_authorization(aspsp_name, aspsp_country, REDIRECT_URL)
                    st.session_state.bank_auth_state = auth.get("state")
                    st.link_button("Authorize with bank →", auth["url"])
                    st.caption(
                        "Opens the (mock) bank's consent page in a new tab. You'll be "
                        "redirected back here automatically once you approve."
                    )
                except Exception as exc:  # noqa: BLE001
                    st.error(f"Could not start authorization: {exc}")
        else:
            st.success(f"{len(st.session_state.bank_accounts)} account(s) connected.")
            account_options = {
                a.get("uid"): f"{a.get('uid')} — {a.get('product', a.get('name', 'account'))}"
                for a in st.session_state.bank_accounts
            }
            selected_uid = st.selectbox(
                "Account", list(account_options.keys()), format_func=lambda uid: account_options[uid]
            )

            bcol1, bcol2 = st.columns(2)
            with bcol1:
                if st.button("Fetch balances"):
                    try:
                        st.json(bank_feed.get_balances(selected_uid))
                    except Exception as exc:  # noqa: BLE001
                        st.error(f"Could not fetch balances: {exc}")
            with bcol2:
                if st.button("Fetch transactions"):
                    try:
                        txns = bank_feed.get_transactions(selected_uid)
                        st.dataframe(pd.DataFrame(txns))
                    except Exception as exc:  # noqa: BLE001
                        st.error(f"Could not fetch transactions: {exc}")

            if st.button("Disconnect"):
                st.session_state.bank_accounts = None
                st.rerun()
