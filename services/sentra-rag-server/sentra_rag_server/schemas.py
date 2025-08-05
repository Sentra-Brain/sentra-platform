# /sentra-rag-server/sentra_rag_server/schemas.py
# Pydantic models for request/response
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class SearchRequest(BaseModel):
    query: str = Field(..., description="Search query")
    knowledge_source_id: Optional[str] = Field(None, description="Optional knowledge source filter")
    limit: Optional[int] = Field(10, description="Maximum number of results")


class ContextRequest(BaseModel):
    query: str = Field(..., description="Query for context generation")
    knowledge_source_id: Optional[str] = Field(None, description="Optional knowledge source filter")  
    max_tokens: Optional[int] = Field(4000, description="Maximum tokens in context")


class SearchResult(BaseModel):
    chunk_id: str
    content: str
    metadata: Dict[str, Any]
    relevance_score: float


class SearchResponse(BaseModel):
    query: str
    results: List[SearchResult]
    total_results: int


class ContextResponse(BaseModel):
    query: str
    context: str
    chunk_count: int