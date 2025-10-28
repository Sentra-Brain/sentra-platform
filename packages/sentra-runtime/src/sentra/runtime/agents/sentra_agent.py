# sentra/runtime/agents/sentra_agent.py
from sentra.runtime.agents.base_agent import BaseAgent
from sentra.runtime.agents.registry import AgentTemplate, agent_registry
from sentra.runtime.tools.mcp import search_duckduckgo, fetch_webpage
from sentra.runtime.tools.filesystem import all_tools
from sentra.runtime.tools.rag_tool import rag_search_tool
from sentra.shared.settings import settings

def _sentra_tools() -> list:
    return [search_duckduckgo, fetch_webpage, rag_search_tool] + all_tools

class SentraAgent(BaseAgent):
    # Intentionally thin: accepts the same params as BaseAgent.
    pass

# Self-register on import with full, matching metadata
agent_registry.register(
    AgentTemplate(
        key="sentra",
        name="SentraAgent",
        description="Core Sentra conversational agent with RAG + tools.",
        instructions=(
            "You are Sentra, a private and secure AI copilot. "
            "Always use memory, retrieved knowledge, and reasoning "
            "to deliver precise and concise answers."
        ),
        default_model_id=settings.model_id,
        agent_cls=SentraAgent,
        provide_tools=_sentra_tools,
    )
)
