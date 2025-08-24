# core/sentra-engine/tests/test_id_utils.py
import uuid
from sentra_engine.core.id_utils import normalize_message_id

def test_normalize_uuid_variants():
    u = uuid.uuid4()
    assert normalize_message_id(u) == u.hex
    assert len(normalize_message_id(None)) == 32  # generated hex
    dashed = str(u)
    assert normalize_message_id(dashed) == u.hex
    already_hex = u.hex
    assert normalize_message_id(already_hex) == already_hex