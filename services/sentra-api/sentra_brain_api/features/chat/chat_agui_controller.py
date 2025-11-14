"""FastAPI router exposing AG-UI compliant chat endpoints."""
from fastapi import APIRouter
from agents.integrations.agui import AGUIAdapter
from sentra.runtime.agents.registry import agent_registry

# Build the default Sentra agent template once at import time.
template = agent_registry.get("sentra")
agent = template.build()

adapter = AGUIAdapter(agent)
router: APIRouter = adapter.router
