# tests/test_tool_adapter.py
import json
import copy
import pytest

# --- Minimal stub to avoid coupling tests to your package import path ---
from dataclasses import dataclass
from typing import Any, Dict, Optional

@dataclass
class ToolSchemaStub:
    name: str
    description: Optional[str] = None
    title: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None

# Import functions under test (adjust import path to your module)
from sentra_engine.llm.adapters.openai_stream import (
    with_guidance,
    _normalize_tool_name,
    _downgrade_json_schema,
    apply_tools,
)

def test_with_guidance_prepends_system():
    msgs = [{"role": "user", "content": "hi"}]
    out = with_guidance(msgs, "Use web_search")
    assert out[0]["role"] == "system"
    assert "Use web_search" in out[0]["content"]
    assert out[1:] == msgs

def test_with_guidance_noop_when_none():
    msgs = [{"role": "user", "content": "hi"}]
    out = with_guidance(msgs, None)
    assert out == msgs

@pytest.mark.parametrize("raw,expected", [
    ("web.search.v1", "web_search_v1"),
    ("csv.from_json", "csv_from_json"),
    ("fs.write_text", "fs_write_text"),
    ("already_ok", "already_ok"),
    ("", "tool"),
    ("a"*100, "a"*64),  # truncate
])
def test_normalize_tool_name(raw, expected):
    assert _normalize_tool_name(raw) == expected

def test_downgrade_schema_strips_unsupported_fields_and_anyof_null():
    schema = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": "abc",
        "$defs": {},
        "type": "object",
        "required": ["query", "flags"],
        "properties": {
            "query": {"type": "string"},
            "flags": {
                "anyOf": [
                    {"type": "array", "items": {"type": "string"}},
                    {"type": "null"},
                ]
            }
        }
    }
    out = _downgrade_json_schema(schema)
    assert "$schema" not in out and "$id" not in out and "$defs" not in out
    assert out["type"] == "object"
    assert out["properties"]["flags"] == {"type": "array", "items": {"type": "string"}}
    # flags should no longer be required (was optional via null)
    assert "flags" not in out["required"]
    assert out["additionalProperties"] is False

def test_downgrade_wraps_non_object():
    schema = {"type": "string"}
    out = _downgrade_json_schema(schema)
    assert out["type"] == "object"
    assert "value" in out["properties"]
    assert out["required"] == ["value"]

def test_apply_tools_builds_payload_and_map():
    payload = {"model": "sentra-brain"}
    tools = [
        ToolSchemaStub(
            name="web.search.v1",
            description="Search the web",
            parameters={
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "flags": {
                        "anyOf": [
                            {"type": "array", "items": {"type": "string"}},
                            {"type": "null"}
                        ]
                    }
                },
                "required": ["query", "flags"]
            },
        ),
        ToolSchemaStub(
            name="web.search.v1",  # intentional collision to test uniqueness post-normalization
            description="Search the web (alt)",
            parameters={"type": "object", "properties": {}},
        ),
    ]

    tool_map = apply_tools(payload, tools)

    # payload mutated
    assert "tools" in payload and isinstance(payload["tools"], list)
    assert payload["tool_choice"] == "auto"

    # two tools present
    assert len(payload["tools"]) == 2
    f1 = payload["tools"][0]["function"]
    f2 = payload["tools"][1]["function"]

    # names normalized and unique
    assert f1["name"].startswith("web_search_v1")
    assert f2["name"].startswith("web_search_v1")
    assert f1["name"] != f2["name"]

    # schema downgraded: flags anyOf->array (and optional)
    flags = f1["parameters"]["properties"]["flags"]
    assert flags == {"type": "array", "items": {"type": "string"}}
    assert "flags" not in f1["parameters"].get("required", [])

    # routing map connects LLM names back to MCP names
    assert tool_map[f1["name"]] == "web.search.v1"
    assert tool_map[f2["name"]] == "web.search.v1"

def test_description_truncation_and_defaults():
    payload = {}
    long_desc = "x" * 10_000
    tools = [
        ToolSchemaStub(
            name="fs.write_text",
            description=long_desc,
            parameters={"type": "object", "properties": {"path": {"type": "string"}}},
        ),
        ToolSchemaStub(
            name="uuid.new",
            title="UUID Generator",
            parameters=None,  # test defaulting path
        ),
    ]
    _map = apply_tools(payload, tools)
    assert len(payload["tools"]) == 2

    f0 = payload["tools"][0]["function"]
    f1 = payload["tools"][1]["function"]

    # name normalized
    assert f0["name"] == "fs_write_text"
    assert f1["name"] == "uuid_new"

    # description truncated to <= 512
    assert len(f0["description"]) <= 512
    # second tool uses title as description fallback
    assert f1["description"] == "UUID Generator"

    # parameters default to object schema if None provided
    assert f1["parameters"]["type"] == "object"
    assert "properties" in f1["parameters"]
    # assert f1["parameters"]["additionalProperties"] is False
