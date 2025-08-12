# sentra_brain_api/core/app_state.py
from pydantic import BaseModel
from sentra_brain_api.core.conversation_engine.engine import ConversationEngine

class AppState:
    def __init__(self, conversation_engine: ConversationEngine | None = None):
        self.conversation_engine: ConversationEngine | None = conversation_engine
