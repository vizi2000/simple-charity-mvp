import base64
import datetime as dt
import hmac
import hashlib
import os
from typing import Dict, Tuple
from zoneinfo import ZoneInfo


REQUIRED_FIELDS_ORDER = [
    # alphabetical by field name used in Combined Page for hash composition
    # do NOT include hash_algorithm nor hashExtended in the hash string
    "chargetotal",
    "checkoutoption",
    "currency",
    "oid",
    "storename",
    "timezone",
    "txndatetime",
    "txntype",
]


def warsaw_now_str() -> str:
    """Return current Warsaw time in Fiserv required format YYYY:MM:DD-HH:MM:SS."""
    now = dt.datetime.now(ZoneInfo("Europe/Warsaw"))
    return now.strftime("%Y:%m:%d-%H:%M:%S")


def compose_hash_string(payload: Dict[str, str]) -> str:
    """
    Compose the 'values-only' string for HMAC based on alphabetical order of field names.
    This uses REQUIRED_FIELDS_ORDER to ensure stable ordering independent of dict order.
    """
    values = []
    for key in REQUIRED_FIELDS_ORDER:
        if key not in payload:
            raise ValueError(f"Missing required field for hash: {key}")
        values.append(str(payload[key]))
    return "|".join(values)


def compute_hash_extended(payload: Dict[str, str], shared_secret: str) -> str:
    """
    Compute Base64-encoded HMAC-SHA256 of the values-only pipe-joined string.
    """
    to_sign = compose_hash_string(payload)
    mac = hmac.new(shared_secret.encode("utf-8"), to_sign.encode("utf-8"), hashlib.sha256).digest()
    return base64.b64encode(mac).decode("utf-8")


def build_combined_page_payload(
    *,
    storename: str,
    oid: str,
    chargetotal: str,
    success_url: str,
    fail_url: str,
    notify_url: str,
    currency: str = "985",
    checkoutoption: str = "combinedpage",
    txntype: str = "sale",
    timezone: str = "Europe/Warsaw",
    hash_algorithm: str = "HMACSHA256",
    bname: str | None = None,
    bemail: str | None = None,
) -> Dict[str, str]:
    """
    Build a complete payload for Combined Page with current Warsaw time and 3 URLs.
    Does NOT include hashExtended; caller should compute it with compute_hash_extended().
    """
    txndatetime = warsaw_now_str()
    payload: Dict[str, str] = {
        "storename": storename,
        "txntype": txntype,
        "timezone": timezone,
        "txndatetime": txndatetime,
        "hash_algorithm": hash_algorithm,
        "chargetotal": chargetotal,
        "currency": currency,
        "checkoutoption": checkoutoption,
        "oid": oid,
        "responseSuccessURL": success_url,
        "responseFailURL": fail_url,
        "transactionNotificationURL": notify_url,
    }
    if bname:
        payload["bname"] = bname
    if bemail:
        payload["bemail"] = bemail
    return payload


def validate_payload_ready(payload: Dict[str, str]) -> Tuple[bool, str]:
    """
    Basic validation before submit: required fields for hash, algorithm value, and URLs presence.
    """
    # required for hash
    for f in REQUIRED_FIELDS_ORDER:
        if not payload.get(f):
            return False, f"Missing required field: {f}"
    # algorithm
    if payload.get("hash_algorithm") != "HMACSHA256":
        return False, "hash_algorithm must equal 'HMACSHA256'"
    # URLs
    missing_urls = [u for u in ("responseSuccessURL", "responseFailURL", "transactionNotificationURL") if not payload.get(u)]
    if missing_urls:
        return False, f"Missing URL fields: {', '.join(missing_urls)}"
    # timezone formatting quick check
    if payload.get("timezone") != "Europe/Warsaw":
        return False, "timezone must be 'Europe/Warsaw' for support alignment"
    # txndatetime quick shape check
    t = payload.get("txndatetime", "")
    if len(t) != 19 or t[4] != ":" or t[7] != ":" or t[10] != "-" or t[13] != ":" or t[16] != ":":
        return False, "txndatetime must be formatted as YYYY:MM:DD-HH:MM:SS"
    return True, "ok"


def finalize_payload_with_hash(payload: Dict[str, str], shared_secret: str) -> Dict[str, str]:
    """
    Validate and attach hashExtended to payload. Returns a copy including hashExtended.
    """
    ok, msg = validate_payload_ready(payload)
    if not ok:
        raise ValueError(f"Payload validation failed: {msg}")
    out = dict(payload)
    out["hashExtended"] = compute_hash_extended(payload, shared_secret)
    return out
