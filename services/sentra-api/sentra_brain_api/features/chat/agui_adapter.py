# sentra_brain_api/features/chat/agui_adapter.py

from fastapi import FastAPI
from agent_framework_ag_ui import add_agent_framework_fastapi_endpoint

from sentra.runtime.agents.registry import agent_registry


def register_sentra_agui_endpoint(app: FastAPI, path: str = "/chat/agui") -> None:
    """
    Register an AG-UI-compliant endpoint backed by the SentraAgent.
   
    - We build a single ChatAgent instance from the existing AgentRegistry.
    - Accept AG-UI RunAgentInput payloads
    - Handle SSE streaming
    - Convert Agent Framework updates -> AG-UI events
    """
    template = agent_registry.get("sentra")

    agent = template.build(
        user_id="",
        conversation_id="",
        persist=True,  
    )

    # Register the AG-UI endpoint. This will expose a POST+SSE endpoint at `path`
    # with fully-compliant AG-UI events (TEXT_MESSAGE_*, TOOL_CALL_*, RUN_*…)
    add_agent_framework_fastapi_endpoint(
        app=app,
        agent=agent,
        path=path,
    )
