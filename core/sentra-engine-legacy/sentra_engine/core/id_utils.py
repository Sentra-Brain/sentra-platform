# sentra_engine/engine/id_utils.py
from uuid import UUID, uuid4
from typing import Optional

def normalize_message_id(value: Optional[object], *, prefer_hex: bool = True) -> str:
    if value is None:
        return uuid4().hex if prefer_hex else str(uuid4())
    if isinstance(value, UUID):
        return value.hex if prefer_hex else str(value)
    s = str(value).strip()
    # If caller sent dashed UUID and we prefer hex, convert.
    if prefer_hex and "-" in s:
        try:
            return UUID(s).hex
        except Exception:
            pass
    return s
