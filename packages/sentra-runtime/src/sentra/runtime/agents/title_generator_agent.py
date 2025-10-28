# sentra/runtime/agents/title_generator_agent.py
from sentra.runtime.agents.base_agent import BaseAgent
from sentra.runtime.agents.registry import AgentTemplate, agent_registry

class TitleGeneratorAgent(BaseAgent):
    """Generates concise titles from provided text."""
    pass

agent_registry.register(
    AgentTemplate(
        key="title_generator",
        name="TitleGeneratorAgent",
        description="Generates short, human-readable titles summarizing input text.",
        instructions=(
            "Given a short text or the first exchange of a conversation, "
            "produce a concise, clear title (≤ 8 words)."
        ),
        default_model_id="ai/smollm3:Q8_0",
        agent_cls=TitleGeneratorAgent,
        provide_tools=None,
    )
)
