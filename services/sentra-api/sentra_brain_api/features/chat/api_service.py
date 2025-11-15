# services/sentra-api/sentra_brain_api/features/chat/api_service.py
from sentra.runtime.executor.sentra_executor import SentraExecutor

class ChatApiService:
    def __init__(self):
        self.executor = SentraExecutor()

    async def send_message_stream(self, user_id: str, conversation_id: str, message: str):
        async for event in self.executor.execute_streaming(user_id, conversation_id, message):
            yield event

    async def send_message_agui_stream(self, user_id: str, conversation_id: str, message: str):
        async for event in self.executor.execute_streaming(user_id, conversation_id, message):
            yield self._to_agui_event(event)

    def _to_agui_event(self, event: dict) -> dict:
        t = event.get("type")

        if t == "agent_run_response_update":
            return {
                "type": "TEXT_MESSAGE_CONTENT",
                "delta": event.get("contents", ""),
            }

        if t == "tool_call":
            return {
                "type": "TOOL_CALL_START",
                "toolCallId": event.get("id", "call1"),
                "toolCallName": event.get("name"),
            }

        if t == "tool_result":
            return {
                "type": "TOOL_CALL_RESULT",
                "toolCallId": event.get("id", "call1"),
                "content": event.get("result"),
            }

        if t == "complete":
            return { "type": "RUN_FINISHED" }

        if t == "error":
            return {
                "type": "RUN_ERROR",
                "message": event.get("message"),
            }

        # Fallback (wrap unexpected internal event)
        return { "type": "RAW", "data": event }
