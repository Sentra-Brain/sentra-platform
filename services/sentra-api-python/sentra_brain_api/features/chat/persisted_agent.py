from agent_framework_ag_ui._agent import AgentFrameworkAgent
from agent_framework_ag_ui._orchestrators import ExecutionContext
from ag_ui.core import BaseEvent
from collections.abc import AsyncGenerator


class PersistedAgent(AgentFrameworkAgent):
    """AG-UI wrapper that restores full thread context from agent's message store."""

    async def run_agent(
        self,
        input_data: dict,
    ) -> AsyncGenerator[BaseEvent, None]:
        # Create execution context (normally based only on input_data)
        context = ExecutionContext(
            input_data=input_data,
            agent=self.agent,
            config=self.config,
            confirmation_strategy=self.confirmation_strategy,
        )

        # Restore full message history from the agent’s store
        try:
            thread = self.agent.get_new_thread()
            history = await thread.message_store.list_messages() if thread.message_store else []
            latest = context.messages or []
            context._messages = history + latest 
        except Exception:
            context._messages = context.messages 

        # Delegate to orchestrators
        for orchestrator in self.orchestrators:
            if orchestrator.can_handle(context):
                async for event in orchestrator.run(context):
                    yield event
                return

        raise RuntimeError("No orchestrator matched – invalid configuration?")
