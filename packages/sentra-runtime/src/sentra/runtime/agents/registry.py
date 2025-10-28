# sentra/runtime/agents/registry.py
from dataclasses import dataclass
from typing import Callable, Optional, Type, Dict
from agent_framework import ChatAgent
from sentra.runtime.agents.base_agent import BaseAgent

@dataclass(frozen=True)
class AgentTemplate:
    key: str
    name: str
    description: str
    instructions: str
    default_model_id: Optional[str]
    agent_cls: Type[BaseAgent]
    provide_tools: Optional[Callable[[], list]] = None

    def build(
        self, *,
        user_id: str,
        conversation_id: str,
        model_id: Optional[str] = None,
        **kwargs,
    ) -> ChatAgent:
        tools = self.provide_tools() if self.provide_tools else None
        return self.agent_cls(
            name=self.name,
            description=self.description,
            instructions=self.instructions,
            user_id=user_id,
            conversation_id=conversation_id,
            model_id=model_id or self.default_model_id,
            tools=tools,
            **kwargs,
        )

class AgentRegistry:
    def __init__(self) -> None:
        self._templates: Dict[str, AgentTemplate] = {}

    def register(self, template: AgentTemplate) -> None:
        if template.key in self._templates:
            raise ValueError(f"Agent template '{template.key}' already registered")
        self._templates[template.key] = template

    def get(self, key: str) -> AgentTemplate:
        try:
            return self._templates[key]
        except KeyError:
            raise ValueError(f"Unknown agent template: {key}. Available: {list(self._templates)}")

    def list_templates(self) -> list[dict[str, str]]:
        return [
            {
                "key": t.key,
                "name": t.name,
                "description": t.description,
                "instructions": t.instructions,
                "model_id": t.default_model_id or "default",
            }
            for t in self._templates.values()
        ]

agent_registry = AgentRegistry()
