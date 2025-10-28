# agents/agent_factory.py
from agent_framework import ChatAgent
from agent_framework.openai import OpenAIChatClient

from sentra.runtime.agents.collector_agent import build_collector_agent
from sentra.runtime.agents.dev_helper_agent import build_dev_helper_agent
from sentra.runtime.agents.fetch_agent import build_fetch_agent
from sentra.runtime.agents.file_organizer_agent import build_file_organizer_agent
from sentra.runtime.agents.folder_manager_agent import build_folder_manager_agent
from sentra.runtime.agents.general_agent import build_general_agent
from sentra.runtime.agents.markdown_summarizer_agent import build_markdown_summarizer_agent
from sentra.runtime.agents.pure_fetch_agent import build_pure_fetch_agent
from sentra.runtime.agents.research_aggregator_agent import build_research_aggregator_agent
from sentra.runtime.agents.search_agent import build_search_agent
from sentra.runtime.agents.sentra_agent import build_sentra_agent
from sentra.runtime.agents.summarizer_agent import build_summarizer_agent
from sentra.runtime.agents.sys_exec_agent import build_sys_exec_agent
from sentra.runtime.agents.system_inspector_agent import build_system_inspector_agent
from sentra.runtime.agents.title_generator_agent import build_title_generator_agent
from sentra.shared.logging import get_logger
from sentra.shared.settings import settings

logger = get_logger("agent_factory")

DEFAULT_AGENT_NAME = "SentraAgent"

class AgentFactory:
    """
    Central registry and factory for all ChatAgents.
    Keeps model configuration consistent and allows discovery by name.
    """

    def __init__(self):
        self._client = OpenAIChatClient(
            endpoint=settings.open_api_base,
            api_key=settings.open_api_key or "none",
            ai_model_id=settings.model_id,
        )
        self._registry: dict[str, object] = {}
        
    def init_defaults(self):
        builders = {
            DEFAULT_AGENT_NAME: build_sentra_agent,
            "CollectorAgent": build_collector_agent,
            "DevHelperAgent": build_dev_helper_agent,
            "FetchAgent": build_fetch_agent,
            "FileOrganizerAgent": build_file_organizer_agent,
            "FolderManagerAgent": build_folder_manager_agent,
            "GeneralAgent": build_general_agent,
            "MarkdownSummarizerAgent": build_markdown_summarizer_agent,
            "PureFetcherAgent": build_pure_fetch_agent,
            "ResearchAggregatorAgent": build_research_aggregator_agent,   
            "SearchAgent": build_search_agent,
            "SummarizerAgent": build_summarizer_agent,
            "SysExecAgent": build_sys_exec_agent,
            "SystemInspectorAgent": build_system_inspector_agent,
            "TitleGeneratorAgent": build_title_generator_agent,
        }
        for name, builder in builders.items():
            agent = builder(self._client)
            self._registry[name] = agent
        return self

    def get(self, name: str) -> ChatAgent:
        try:
            if name in self._registry:
                return self._registry[name]
            else:
                logger.error(f"Agent '{name}' not found in factory.")
                return self._registry[DEFAULT_AGENT_NAME]
        except KeyError:
            raise KeyError(f"Agent '{name}' not registered in factory. Available: {list(self._registry)}")

    def all(self) -> list[ChatAgent]:
        return list(self._registry.values())
