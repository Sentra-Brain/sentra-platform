# sentra_brain_api/crosscutting/json_sanitize.py
from typing import List, Optional
from uuid import UUID
from datetime import datetime, date
from decimal import Decimal
from enum import Enum

def json_safe(value):
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, (UUID,)):
        return str(value)
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, dict):
        return {str(k): json_safe(v) for k, v in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [json_safe(v) for v in value]
    # último recurso: string
    return str(value)


def as_str_list(values: Optional[List[UUID]]) -> list[str]:
    if not values:
        return []
    return [str(v) for v in values]