from __future__ import annotations

import json
import logging
from collections.abc import AsyncGenerator
from typing import Any, Optional

from sentra.runtime.agents.registry import AgentRegistry, agent_registry
from sentra.runtime.adapters.hybrid_chat_message_store import ChatMessageStoreHybrid
from sentra.runtime.executor.protocols import ExecutorProtocol
from sentra.runtime.executor.entity_discovery import SentraEntityDiscovery
from sentra.runtime.workflows.registry import WorkflowRegistry

logger = logging.getLogger(__name__)


class SentraExecutor(ExecutorProtocol):
    """
    Unified runtime executor for Sentra entities (agents & workflows).

    Responsibilities:
    - Resolve entity definitions via SentraEntityDiscovery.
    - Execute agents (streaming or sync) with full persistence.
    - Persist thread state between runs via ChatMessageStoreHybrid.
    - Yield structured, JSON-serializable event dictionaries.
    """

    def __init__(
        self,
        *,
        agent_registry: Optional[AgentRegistry] = None,
        workflow_registry: Optional[WorkflowRegistry] = None,
    ) -> None:
        self.discovery = SentraEntityDiscovery(
            ag_registry=agent_registry or agent_registry,
            wf_registry=workflow_registry,
        )
  
  
    # ---------------------------------------------------------------------
    # 🎯 Public API
    # ---------------------------------------------------------------------

    async def execute_streaming(
        self,
        user_id: str,
        conversation_id: str,
        message: str,
        entity_id: str = "sentra",
    ) -> AsyncGenerator[dict[str, Any], None]:
        """
        Execute a Sentra entity (typically an agent) in streaming mode.

        Yields:
            Stream of structured JSON-like event dictionaries.
        """
        # Resolve entity (agent or workflow)
        entity_info = self.discovery.get_entity_info(entity_id)
        if not entity_info:
            yield self._error_event(f"Unknown entity '{entity_id}'")
            return

        if entity_info.type != "agent":
            yield self._error_event(f"Entity type '{entity_info.type}' not yet supported")
            return

        # Instantiate agent
        template = self.discovery.agent_registry.get(entity_id)
        agent = template.build(user_id=user_id, conversation_id=conversation_id)

        # Prepare chat persistence layer
        store = ChatMessageStoreHybrid(conversation_id, user_id)
        serialized = await store.load_thread_state()
        thread = await agent.deserialize_thread(serialized) if serialized else agent.get_new_thread()

        # Execute agent loop
        try:
            async for update in agent.run_stream(message, thread=thread):
                yield self._format_event(update)

            # Explicit completion event
            yield {
                "type": "complete",
                "conversation_id": conversation_id,
                "entity": entity_info.id,
            }

        except Exception as e:
            logger.exception("Agent execution failed")
            yield self._error_event(str(e))
        finally:
            try:
                serialized_state = await thread.serialize()
                await store.save_thread_state(serialized_state)
            except Exception as persist_err:
                logger.warning(f"Failed to persist thread state: {persist_err}")

    async def execute_sync(
        self,
        user_id: str,
        conversation_id: str,
        message: str,
        entity_id: str = "sentra",
    ) -> dict[str, Any]:
        """
        Execute a Sentra entity synchronously (non-streaming).

        Returns:
            Final event (usually completion or error).
        """
        last_event: dict[str, Any] | None = None
        async for event in self.execute_streaming(user_id, conversation_id, message, entity_id):
            last_event = event
        return last_event or {"status": "no_output"}

    async def list_entities(self) -> list[dict[str, Any]]:
        """
        List all discoverable entities (agents and workflows).
        """
        entities = await self.discovery.discover_entities()
        return [e.__dict__ for e in entities]

    # ---------------------------------------------------------------------
    # 🧱 Internal helpers
    # ---------------------------------------------------------------------

    def _format_event(self, update: Any) -> dict[str, Any]:
        """Normalize an agent update into a JSON-serializable dictionary."""
        try:
            if isinstance(update, dict):
                return update
            if hasattr(update, "to_dict"):
                return update.to_dict()
            # Fallback to naive serialization
            return json.loads(json.dumps(update, default=str))
        except Exception as e:
            logger.debug(f"Failed to format update: {e}")
            return {"type": "unknown", "content": str(update)}

    def _error_event(self, message: str) -> dict[str, Any]:
        """Create a standardized error event."""
        return {"type": "error", "message": message}
