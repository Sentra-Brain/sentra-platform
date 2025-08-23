import pytest

from sentra_engine.core.tool_intent import ToolCallDelta, ToolIntent
from sentra_engine.tooling.assembler import ToolCallAssembler
from sentra_engine.tooling.args_coercion import ArgsCoercer


def test_assembler_merges_and_preserves_id():
    assembler = ToolCallAssembler()
    assembler.add(ToolCallDelta(index=0, id="123", name="echo", arguments_fragment='{"x":'))
    assembler.add(ToolCallDelta(index=0, id="123", name=None, arguments_fragment='1}'))
    intents = assembler.finalize()
    assert intents == [ToolIntent(id="123", name="echo", arguments={"x": 1})]


def test_assembler_raises_on_bad_json():
    assembler = ToolCallAssembler()
    assembler.add(ToolCallDelta(index=None, id=None, name="bad", arguments_fragment="{"))
    with pytest.raises(ValueError):
        assembler.finalize()


def test_args_coercer_coerces_and_validates():
    schema = {"type": "object", "properties": {"k": {"type": "integer"}}, "required": ["k"]}
    coerced = ArgsCoercer(schema).coerce({"k": "5"})
    assert coerced["k"] == 5
    with pytest.raises(Exception):
        ArgsCoercer(schema).coerce({"k": "oops"})

