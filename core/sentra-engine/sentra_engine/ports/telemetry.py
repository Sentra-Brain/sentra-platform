# sentra_engine/ports/telemetry.py
from abc import ABC, abstractmethod
from typing import Optional


class TelemetryPort(ABC):
    @abstractmethod
    def step_start(self, step_id: str, meta: Optional[dict] = None) -> None:
        """Mark a step start with optional metadata."""
        raise NotImplementedError

    @abstractmethod
    def step_end(self, step_id: str, success: bool, meta: Optional[dict] = None) -> None:
        """Mark a step end with status and optional metadata."""
        raise NotImplementedError

    @abstractmethod
    def record_exception(self, exc: Exception, meta: Optional[dict] = None) -> None:
        """Record an exception with optional metadata."""
        raise NotImplementedError
