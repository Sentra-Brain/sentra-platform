# sentra_engine/ports/planner.py
from abc import ABC, abstractmethod
from sentra_engine.core.models import PlanStep, Transcript
from sentra_engine.core.plan import Plan, Step


class PlannerPort(ABC):
    @abstractmethod
    async def plan(self, transcript: Transcript, context: str) -> PlanStep:
        """Legacy single-step plan; kept for compatibility."""
        raise NotImplementedError

    async def plan_structured(self, transcript: Transcript, context: str) -> Plan:
        """
        Return a structured Plan. Default shim wraps the legacy single-step Respond
        into a Plan with one LLM.Respond step.
        """
        ps = await self.plan(transcript, context)
        guidance = (ps.params or {}).get("guidance") if hasattr(ps, "params") else None
        return Plan(
            schema_version=1,
            steps=[Step(id="respond", kind="LLM.Respond", params={"guidance": guidance} if guidance else {})],
            entry="respond",
            guidance=guidance or None,
        )
