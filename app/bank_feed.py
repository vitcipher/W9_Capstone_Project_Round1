"""
Enable Banking (https://enablebanking.com) integration - the "bank-feed"
stretch feature discussed after the must-have-features review. Uses their
Mock ASPSP (fake test bank, no real bank account or credentials needed) so
this is genuinely a free-tier demo, not something that touches real
financial data.

Flow (PSD2-style consent, verified against Enable Banking's own docs before
writing this - see the JWT/auth shape below):
  1. Every request is authenticated with a JWT (RS256), signed with the
     private key you get when you register an application at
     enablebanking.com/cp/applications.
  2. POST /auth targeting an ASPSP (bank) starts a consent session and
     returns a URL for the user to "authorize" at.
  3. The bank (Mock ASPSP: no real login) redirects back to our
     redirect_url with a `code` query param.
  4. POST /sessions with that code exchanges it for account IDs.
  5. GET /accounts/{id}/transactions and /balances fetch the actual data.

Setup required (see README/.env.example) - this module does nothing useful
without:
  ENABLE_BANKING_APP_ID           - from the app registration
  ENABLE_BANKING_PRIVATE_KEY_PATH - path to the downloaded .pem file
"""

import os
import time
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path

import jwt
import requests

API_BASE = "https://api.enablebanking.com"


class BankFeedNotConfigured(Exception):
    """Raised when the required Enable Banking env vars aren't set."""


def _get_credentials() -> tuple[str, str]:
    app_id = os.environ.get("ENABLE_BANKING_APP_ID")
    key_path = os.environ.get("ENABLE_BANKING_PRIVATE_KEY_PATH")
    if not app_id or not key_path:
        raise BankFeedNotConfigured(
            "Set ENABLE_BANKING_APP_ID and ENABLE_BANKING_PRIVATE_KEY_PATH in .env "
            "(register an app at enablebanking.com/cp/applications first)."
        )
    key_file = Path(key_path).expanduser()
    if not key_file.exists():
        raise BankFeedNotConfigured(f"Private key file not found: {key_file}")
    return app_id, key_file.read_text()


def is_configured() -> bool:
    try:
        _get_credentials()
        return True
    except BankFeedNotConfigured:
        return False


def generate_jwt() -> str:
    """Builds the RS256 JWT Enable Banking requires on every request.
    Short-lived (5 min) by design - generate a fresh one per call rather
    than caching, since these are cheap to create and caching adds a class
    of expiry bugs we don't need for a demo integration."""
    app_id, private_key = _get_credentials()
    now = int(time.time())
    payload = {"iss": "enablebanking.com", "aud": "api.enablebanking.com", "iat": now, "exp": now + 300}
    headers = {"typ": "JWT", "alg": "RS256", "kid": app_id}
    return jwt.encode(payload, private_key, algorithm="RS256", headers=headers)


def _request(method: str, path: str, **kwargs) -> dict:
    token = generate_jwt()
    headers = kwargs.pop("headers", {})
    headers["Authorization"] = f"Bearer {token}"
    resp = requests.request(method, f"{API_BASE}{path}", headers=headers, timeout=30, **kwargs)
    resp.raise_for_status()
    return resp.json()


def list_aspsps(country: str = "DE") -> list[dict]:
    """Lists available banks for a country - use this to find the exact
    Mock ASPSP name/country your Enable Banking account uses, rather than
    guessing it (it can vary by account/region)."""
    return _request("GET", "/aspsps", params={"country": country}).get("aspsps", [])


def start_authorization(aspsp_name: str, aspsp_country: str, redirect_url: str) -> dict:
    """Step 1 of the consent flow. Returns a dict with a 'url' field - send
    the user (landlord) there to "authorize" (Mock ASPSP: no real login)."""
    state = str(uuid.uuid4())
    valid_until = (datetime.now(timezone.utc) + timedelta(days=10)).isoformat()
    body = {
        "access": {"valid_until": valid_until},
        "aspsp": {"name": aspsp_name, "country": aspsp_country},
        "state": state,
        "redirect_url": redirect_url,
        "psu_type": "personal",
    }
    result = _request("POST", "/auth", json=body)
    result["state"] = state
    return result


def create_session(code: str) -> dict:
    """Step 2: exchanges the callback `code` for account access. Returns
    the session dict, including an 'accounts' list with 'uid' per account."""
    return _request("POST", "/sessions", json={"code": code})


def get_balances(account_uid: str) -> dict:
    return _request("GET", f"/accounts/{account_uid}/balances")


def get_transactions(account_uid: str) -> list[dict]:
    return _request("GET", f"/accounts/{account_uid}/transactions").get("transactions", [])
