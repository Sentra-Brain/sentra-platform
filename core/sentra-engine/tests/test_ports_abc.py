import pytest
from abc import ABCMeta

import sentra_engine.ports.llm as llm
import sentra_engine.ports.mcp as mcp
import sentra_engine.ports.rag as rag
import sentra_engine.ports.persistence as persistence
import sentra_engine.ports.context as context
import sentra_engine.ports.planner as planner
import sentra_engine.ports.telemetry as telemetry


@pytest.mark.parametrize("cls", [
    llm.LLMPort,
    mcp.MCPPort,
    rag.RAGPort,
    persistence.PersistencePort,
    context.ContextPort,
    planner.PlannerPort,
    telemetry.TelemetryPort,
])
def test_ports_are_abstract(cls):
    """Ports should be abstract base classes."""
    assert isinstance(cls, ABCMeta)
    with pytest.raises(TypeError):
        cls()  # Cannot instantiate without implementing abstract methods
