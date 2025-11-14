# sentra/runtime/executor/entity_discovery.py
from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Optional, Literal

from sentra.runtime.agents.registry import AgentRegistry, agent_registry
from sentra.runtime.workflows.registry import WorkflowRegistry, workflow_registry

logger = logging.getLogger(__name__)


@dataclass
class EntityInfo:
    """Descriptive metadata for an executable entity (agent or workflow)."""

    id: str
    type: Literal["agent", "workflow"]
    name: str
    description: str
    model_id: Optional[str] = None

class SentraEntityDiscovery:
    """Unified discovery layer for Sentra agents and workflows."""

    def __init__(
        self,
        ag_registry: AgentRegistry | None = None,
        wf_registry: WorkflowRegistry | None = None,
    ) -> None:
        self.agent_registry = ag_registry or agent_registry
        self.workflow_registry = wf_registry or workflow_registry


    async def discover_entities(self) -> list[EntityInfo]:
        """Return all registered entities across agents and workflows."""
        entities: list[EntityInfo] = []

        # --- Agents
        try:
            for t in self.agent_registry._templates.values():
                entities.append(
                    EntityInfo(
                        id=t.key,
                        type="agent",
                        name=t.name,
                        description=t.description,
                        model_id=t.default_model_id,
                    )
                )
        except Exception as e:
            logger.warning(f"Failed to list agents: {e}")

        # --- Workflows (optional)
        if self.workflow_registry:
            try:
                for key, wf in self.workflow_registry.items():
                    entities.append(
                        EntityInfo(
                            id=key,
                            type="workflow",
                            name=getattr(wf, "name", key),
                            description=getattr(wf, "description", ""),
                            model_id=None,
                        )
                    )
            except Exception as e:
                logger.warning(f"Failed to list workflows: {e}")

        return entities

    def get_entity_info(self, entity_id: str) -> Optional[EntityInfo]:
        """Return metadata for a given entity id."""
        if self.agent_registry and entity_id in self.agent_registry._templates:
            t = self.agent_registry._templates[entity_id]
            return EntityInfo(
                id=t.key,
                type="agent",
                name=t.name,
                description=t.description,
                model_id=t.default_model_id,
            )

        if self.workflow_registry and entity_id in self.workflow_registry:
            wf = self.workflow_registry[entity_id]
            return EntityInfo(
                id=entity_id,
                type="workflow",
                name=getattr(wf, "name", entity_id),
                description=getattr(wf, "description", ""),
            )

        return None

    async def load_entity(self, entity_id: str) -> Any:
        """Return a live agent or workflow instance."""
        info = self.get_entity_info(entity_id)
        if not info:
            raise ValueError(f"Entity '{entity_id}' not found.")

        if info.type == "agent":
            template = self.agent_registry.get(entity_id)
            return template  # caller decides when to .build()

        if info.type == "workflow":
            wf_factory = self.workflow_registry[entity_id]
            return wf_factory() if callable(wf_factory) else wf_factory

        raise ValueError(f"Unsupported entity type for '{entity_id}'.")
