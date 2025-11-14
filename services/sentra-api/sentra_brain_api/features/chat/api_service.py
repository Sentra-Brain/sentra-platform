# services/sentra-api/sentra_brain_api/features/chat/api_service.py
from sentra.runtime.executor.sentra_executor import SentraExecutor

class ChatApiService:
    def __init__(self):
        self.executor = SentraExecutor()

    async def send_message_stream(self, user_id: str, conversation_id: str, message: str):
        async for event in self.executor.execute_streaming(user_id, conversation_id, message):
            yield event