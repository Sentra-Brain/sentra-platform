from __future__ import annotations

"""Coordinator agent that delegates to the general SentraAgent."""

from typing import AsyncGenerator

from ..models import ConversationEvent, ConversationRequest
from .sentra_agent import SentraAgent


class CoordinatorAgent:
    """Thin wrapper that forwards requests to :class:`SentraAgent`."""

    async def run(
        self, request: ConversationRequest
    ) -> AsyncGenerator[ConversationEvent, None]:
        agent = SentraAgent()
        async for event in agent.run(request):
            yield event
