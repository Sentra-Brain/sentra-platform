# sentra/runtime/executor/protocols.py
from abc import ABC, abstractmethod
from collections.abc import AsyncGenerator
from typing import Any

class ExecutorProtocol(ABC):
    """Generic interface for Sentra executors."""

    @abstractmethod
    async def execute_streaming(self, *args, **kwargs) -> AsyncGenerator[Any, None]:
        ...

    @abstractmethod
    async def execute_sync(self, *args, **kwargs) -> Any:
        ...
