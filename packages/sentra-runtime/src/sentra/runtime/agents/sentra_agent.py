"""SentraAgent - MAF-based general-purpose conversational agent."""

from sentra.runtime.agents.base_agent import BaseAgent
from sentra.runtime.tools.mcp_tools import search_duckduckgo, fetch_webpage
from sentra.runtime.tools.filesystem import all_tools
from sentra.runtime.tools.rag_tool import rag_search_tool


class SentraAgent(BaseAgent):
    """Main Sentra conversational agent."""

    def __init__(self, user_id: str, conversation_id: str):
        super().__init__(
            name="SentraAgent",
            description="Root Sentra conversational agent.",
            instructions=(
                "You are Sentra, a private and secure AI copilot. "
                "Always use memory, retrieved knowledge, and reasoning "
                "to deliver precise and concise answers."
            ),
            user_id=user_id,
            conversation_id=conversation_id,
            tools=[search_duckduckgo, fetch_webpage, rag_search_tool] + all_tools,
        )


def build_sentra_agent(user_id: str, conversation_id: str) -> SentraAgent:
    """Convenience builder."""
    return SentraAgent(user_id=user_id, conversation_id=conversation_id)
