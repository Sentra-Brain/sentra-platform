# sentra_brain_api/features/chat/agui_adapter.py

from fastapi import FastAPI
from agent_framework_ag_ui import add_agent_framework_fastapi_endpoint

from sentra.runtime.agents.registry import agent_registry


def register_sentra_agui_endpoint(app: FastAPI, path: str = "/chat/agui") -> None:
    """
    Register an AG-UI-compliant endpoint backed by the SentraAgent.

    For now:
    - We build a single ChatAgent instance from the existing AgentRegistry.
    - We disable persistence at the agent layer (persist=False) so AG-UI can
      manage threads; you can reintroduce custom stores later.

    AG-UI + agent-framework-ag-ui will:
    - Accept AG-UI RunAgentInput payloads
    - Handle SSE streaming
    - Convert Agent Framework updates -> AG-UI events
    """

    # Ensure SentraAgent template is registered (initialize_agents() already did this)
    template = agent_registry.get("sentra")

    # Minimal agent instance for AG-UI bridge.
    # user_id / conversation_id are currently not used here;
    # AG-UI manages thread IDs. You can redesign BaseAgent later to
    # derive storage keys from thread context instead of ctor arguments.
    agent = template.build(
        user_id="",
        conversation_id="",
        persist=False,  # important: avoid binding to a single convo
    )

    # Register the AG-UI endpoint. This will expose a POST+SSE endpoint at `path`
    # with fully-compliant AG-UI events (TEXT_MESSAGE_*, TOOL_CALL_*, RUN_*…)
    add_agent_framework_fastapi_endpoint(
        app=app,
        agent=agent,
        path=path,
    )
