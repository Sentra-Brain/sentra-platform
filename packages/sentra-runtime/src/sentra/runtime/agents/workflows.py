from __future__ import annotations

"""Utilities for running agent workflows in parallel."""

import asyncio
from typing import Any, Awaitable, Iterable, List


class ParallelAgent:
    """Wrapper that executes multiple I/O-bound coroutines concurrently.

    This helper uses :func:`asyncio.gather` with ``return_exceptions=True`` so
    that a failure in one task does not cancel the others. Callers can inspect
    the returned list and handle exceptions gracefully.
    """

    async def run_parallel_tasks(self, tasks: Iterable[Awaitable[Any]]) -> List[Any]:
        """Run ``tasks`` concurrently and collect their results.

        Args:
            tasks: An iterable of awaitable objects.

        Returns:
            A list containing the result of each task. If a task raised an
            exception the exception instance is returned in its place.
        """

        return await asyncio.gather(*tasks, return_exceptions=True)
