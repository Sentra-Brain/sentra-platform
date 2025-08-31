from __future__ import annotations

"""Coordinator agent that delegates to the general SentraAgent."""

from typing import AsyncGenerator

from ..context import build_context
from ..models import ConversationEvent, ConversationRequest
from .sentra_agent import SentraAgent
from ..orchestrators import route_legal_intent, route_real_estate_intent
from .legal.use_case_contract_drafting import run_contract_drafting_agent
from .real_estate.use_case_listings_search import run_listings_search_agent


class CoordinatorAgent:
    """Thin wrapper that forwards requests to :class:`SentraAgent`."""

    async def run(
        self, request: ConversationRequest
    ) -> AsyncGenerator[ConversationEvent, None]:
        msg = request.messages[-1]

        if route_legal_intent(msg):
            context = await build_context(request)
            async for event in run_contract_drafting_agent(request, context):
                yield event
            return

        if route_real_estate_intent(msg):
            context = await build_context(request)
            async for event in run_listings_search_agent(request, context):
                yield event
            return

        agent = SentraAgent()
        async for event in agent.run(request):
            yield event
