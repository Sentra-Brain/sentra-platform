# features/agents/controller.py
from fastapi import APIRouter
from sentra.runtime.agents.registry import agent_registry
from sentra.shared.logging import get_logger

logger = get_logger("sentra_brain_api.agents")

class AgentsController:
    def __init__(self):
        self.router = APIRouter()
        self._add_routes()

    def _add_routes(self):
        @self.router.get("/agents", summary="List available Sentra agents")
        async def list_agents():
            """Return all registered Sentra agent templates."""
            try:
                templates = [
                    {
                        "key": key,
                        "name": tmpl.name,
                        "description": tmpl.description,
                        "model": tmpl.default_model_id,
                    }
                    for key, tmpl in agent_registry.templates.items() 
                ]
                return {"agents": templates}
            except Exception as e:
                logger.exception("Failed to list agents: %s", e)
                return {"agents": [], "error": str(e)}
