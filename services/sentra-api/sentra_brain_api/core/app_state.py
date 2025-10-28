# sentra_brain_api/core/app_state.py
from typing import Optional
from sentra.runtime.agents.agent_factory import AgentFactory

agent_factory: Optional[AgentFactory] = None