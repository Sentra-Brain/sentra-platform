from datetime import datetime, timezone


def utc_now_iso() -> str:
    """UTC timestamp in ISO-8601 (with timezone)."""
    return datetime.now(timezone.utc).isoformat()
