from __future__ import annotations

"""Retry utilities for tool calls."""

import asyncio
import logging
from collections.abc import Awaitable, Callable
from typing import TypeVar

from sentra_engine.models import ConversationEvent
from sentra_engine.telemetry import emit_event_log

T = TypeVar("T")


async def retry_with_backoff(
    func: Callable[[], Awaitable[T]],
    *,
    max_retries: int = 3,
    base_delay: float = 0.5,
    exceptions: tuple[type[BaseException], ...] = (Exception,),
    logger: logging.Logger | None = None,
    label: str | None = None,
) -> T | None:
    """Execute ``func`` with retries and exponential backoff.

    Args:
        func: Coroutine function to execute.
        max_retries: Maximum number of attempts.
        base_delay: Initial delay in seconds before retrying.
        exceptions: Exception types that trigger a retry.
        logger: Optional logger for warning messages.
        label: Optional operation label used in telemetry messages.

    Returns:
        The return value of ``func`` when successful, otherwise ``None``.
    """

    delay = base_delay
    for attempt in range(1, max_retries + 1):
        try:
            return await func()
        except exceptions as exc:  # pragma: no cover - branch exercised in tests
            name = label or getattr(func, "__name__", "operation")
            if logger:
                logger.warning(
                    "%s attempt %d/%d failed: %s", name, attempt, max_retries, exc
                )
            emit_event_log(
                ConversationEvent(
                    type="message_delta",
                    content=f"{name} failed (attempt {attempt}/{max_retries})",
                )
            )
            if attempt >= max_retries:
                emit_event_log(
                    ConversationEvent(
                        type="message_delta",
                        content=f"{name} failed after {max_retries} attempts",
                    )
                )
                return None
            await asyncio.sleep(delay)
            delay *= 2
    return None


__all__ = ["retry_with_backoff"]
