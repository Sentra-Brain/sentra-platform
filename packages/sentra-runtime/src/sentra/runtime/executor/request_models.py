# sentra/runtime/executor/request_models.py
from pydantic import BaseModel

class ExecutorRequest(BaseModel):
    user_id: str
    conversation_id: str
    input: str
    agent_name: str = "sentra"
    stream: bool = True
