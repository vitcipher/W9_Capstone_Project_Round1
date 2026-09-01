"""
Supabase-backed persistence + auth for the Property Ledger app.

Replaces the CSV/session-state-only storage used in the earlier Round 1
POC. Properties, tenants, monthly transactions, extracted documents, and
maintenance requests are now real and persisted, and private per landlord
via Postgres Row Level Security (see supabase/schema.sql's policies) -
not just filtered here in Python, which would be one bug away from
leaking one landlord's data to another.

Setup: create a project at supabase.com, run supabase/schema.sql in its
SQL Editor, then set SUPABASE_URL and SUPABASE_ANON_KEY in .env.

Design note: this module does NOT hold a module-level cached client. The
calling Streamlit code creates one client per browser session (via
new_client()) and stores it in st.session_state. That's not just style -
a shared module-level singleton would be reused across different browser
sessions in a real deployed Streamlit server (one Python process can
serve many concurrent users), which would leak one signed-in user's
session into another user's requests. Every function here takes the
caller's client explicitly instead.
"""

import os

from supabase import Client, create_client


class DBNotConfigured(Exception):
    """Raised when SUPABASE_URL/SUPABASE_ANON_KEY aren't set."""


def is_configured() -> bool:
    return bool(os.environ.get("SUPABASE_URL")) and bool(os.environ.get("SUPABASE_ANON_KEY"))


def new_client() -> Client:
    """Creates a fresh, unauthenticated client. Call once per browser
    session (see app/streamlit_app.py's auth gate) and reuse it - don't
    create a new one per request."""
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_ANON_KEY")
    if not url or not key:
        raise DBNotConfigured(
            "Set SUPABASE_URL and SUPABASE_ANON_KEY in .env - see supabase/schema.sql "
            "header comment for setup steps."
        )
    return create_client(url, key)


# ---------------------------------------------------------------- Auth

def sign_up(client: Client, email: str, password: str):
    return client.auth.sign_up({"email": email, "password": password})


def sign_in(client: Client, email: str, password: str):
    return client.auth.sign_in_with_password({"email": email, "password": password})


def sign_out(client: Client) -> None:
    client.auth.sign_out()


def current_user(client: Client):
    """Returns the logged-in user for this client's session, or None."""
    session = client.auth.get_session()
    return session.user if session else None


# ---------------------------------------------------------------- Properties

def list_properties(client: Client, owner_id: str) -> list[dict]:
    resp = client.table("properties").select("*").eq("owner_id", owner_id).order("created_at").execute()
    return resp.data


def create_property(client: Client, owner_id: str, **fields) -> dict:
    resp = client.table("properties").insert({"owner_id": owner_id, **fields}).execute()
    return resp.data[0]


def update_property(client: Client, property_id: str, **fields) -> dict:
    resp = client.table("properties").update(fields).eq("id", property_id).execute()
    return resp.data[0]


def delete_property(client: Client, property_id: str) -> None:
    client.table("properties").delete().eq("id", property_id).execute()


# ---------------------------------------------------------------- Tenants

def list_tenants(client: Client, owner_id: str, property_id: str | None = None) -> list[dict]:
    q = client.table("tenants").select("*").eq("owner_id", owner_id)
    if property_id:
        q = q.eq("property_id", property_id)
    return q.order("created_at").execute().data


def create_tenant(client: Client, owner_id: str, **fields) -> dict:
    resp = client.table("tenants").insert({"owner_id": owner_id, **fields}).execute()
    return resp.data[0]


def update_tenant(client: Client, tenant_id: str, **fields) -> dict:
    resp = client.table("tenants").update(fields).eq("id", tenant_id).execute()
    return resp.data[0]


def delete_tenant(client: Client, tenant_id: str) -> None:
    client.table("tenants").delete().eq("id", tenant_id).execute()


# ---------------------------------------------------------------- Monthly transactions

def list_transactions(client: Client, owner_id: str, property_id: str | None = None) -> list[dict]:
    q = client.table("monthly_transactions").select("*").eq("owner_id", owner_id)
    if property_id:
        q = q.eq("property_id", property_id)
    return q.order("month").execute().data


def upsert_transaction(client: Client, owner_id: str, **fields) -> dict:
    """fields must include property_id and month - (property_id, month) is
    the unique key the schema enforces, so re-upserting the same month
    updates it rather than duplicating a row."""
    resp = (
        client.table("monthly_transactions")
        .upsert({"owner_id": owner_id, **fields}, on_conflict="property_id,month")
        .execute()
    )
    return resp.data[0]


# ---------------------------------------------------------------- Documents (confirmed AI extractions)

def list_documents(client: Client, owner_id: str, property_id: str | None = None) -> list[dict]:
    q = client.table("documents").select("*").eq("owner_id", owner_id)
    if property_id:
        q = q.eq("property_id", property_id)
    return q.order("confirmed_at", desc=True).execute().data


def create_document(client: Client, owner_id: str, **fields) -> dict:
    resp = client.table("documents").insert({"owner_id": owner_id, **fields}).execute()
    return resp.data[0]


# ---------------------------------------------------------------- Maintenance requests

def list_maintenance_requests(client: Client, owner_id: str, property_id: str | None = None) -> list[dict]:
    q = client.table("maintenance_requests").select("*").eq("owner_id", owner_id)
    if property_id:
        q = q.eq("property_id", property_id)
    return q.order("created_date", desc=True).execute().data


def create_maintenance_request(client: Client, owner_id: str, **fields) -> dict:
    resp = client.table("maintenance_requests").insert({"owner_id": owner_id, **fields}).execute()
    return resp.data[0]


def update_maintenance_request(client: Client, request_id: str, **fields) -> dict:
    resp = client.table("maintenance_requests").update(fields).eq("id", request_id).execute()
    return resp.data[0]
