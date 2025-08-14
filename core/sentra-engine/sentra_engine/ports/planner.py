# sentra_engine/ports/planner.py
from abc import ABC, abstractmethod
from sentra_engine.core.models import PlanStep, Transcript


class PlannerPort(ABC):
    @abstractmethod
    async def plan(self, transcript: Transcript, context: str) -> PlanStep:
        """Produce a plan for the next step given transcript and prompt context."""
        raise NotImplementedError
