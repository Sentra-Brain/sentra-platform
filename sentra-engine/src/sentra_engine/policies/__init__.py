"""Routing and fallback policies."""
from __future__ import annotations

from typing import Any


def route_event(event: Any) -> str:
    """Select an orchestrator route for a conversation event.

    Args:
        event: Placeholder event data.

    Returns:
        The name of the orchestrator to use. Defaults to ``"default"``.
    """
    # TODO: implement routing logic
    return "default"


__all__ = ["route_event"]
