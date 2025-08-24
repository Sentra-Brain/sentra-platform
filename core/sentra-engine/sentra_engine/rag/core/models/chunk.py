from uuid import UUID
from typing import Optional
from pydantic import BaseModel

class RagChunk(BaseModel):
    chunk_id: str
    content: str
    relevance_score: float
    document_id: UUID
    knowledge_source_id: UUID
    source_type: str
    filename: Optional[str] = None
    chunk_index: Optional[int] = None
    chunk_length: Optional[int] = None

    def to_prompt_block(self) -> str:
        return f"{self.content.strip()}\n(Relevance: {self.relevance_score:.2f})"
