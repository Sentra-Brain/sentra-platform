from fastapi import APIRouter

from sentra.runtime.agents.agent_loader import AgentLoader


class AgentsController:
    def __init__(self):
        self.router = APIRouter()
        self._add_routes()

    def _add_routes(self):
        @self.router.get("/agents", summary="List available conversational agents")
        async def list_agents():  # noqa: D401
            loader = AgentLoader()
            # Only return agents we can load successfully to avoid exposing partial implementations
            names: list[str] = []
            for name in loader.list_agents():
                try:
                    loader.load_agent(name)
                    names.append(name)
                except Exception:
                    continue
            return {"agents": names}
