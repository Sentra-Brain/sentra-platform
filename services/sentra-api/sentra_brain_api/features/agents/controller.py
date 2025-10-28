from fastapi import APIRouter

from sentra_brain_api.core import app_state
from sentra.shared.logging import get_logger

logger = get_logger("sentra_brain_api.agents")

class AgentsController:
    def __init__(self):
        self.router = APIRouter()
        self._add_routes()

    def _add_routes(self):
        @self.router.get("/agents", summary="List available conversational agents")
        async def list_agents():  # noqa: D401
            """
            Returns a list of all available registered agents
            from the global AgentFactory instance.
            """
            if not app_state.agent_factory:
                logger.warning("AgentFactory not initialized.")
                return {"agents": []}

            try:
                agents = [agent.name for agent in app_state.agent_factory.all()]
                return {"agents": agents}
            except Exception as e:
                logger.exception("Failed to list agents: %s", e)
                return {"agents": [], "error": str(e)}