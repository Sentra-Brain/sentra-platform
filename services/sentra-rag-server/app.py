from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from uuid import UUID
from rag_engine import RAGEngine
import uvicorn


app = FastAPI(
    title="Sentra RAG Server",
    description="REST API for RAG (Retrieval-Augmented Generation) operations",
    version="1.0.0"
)

# Initialize RAG engine
rag_engine = RAGEngine()


# Pydantic models for request/response
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


# Routes
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "sentra-rag-server"}


@app.get("/settings")
async def get_settings():
    """Get current RAG settings."""
    return rag_engine.get_settings()


@app.post("/search", response_model=SearchResponse)
async def search_knowledge_post(request: SearchRequest):
    """Search for relevant knowledge chunks using POST."""
    try:
        results = await rag_engine.search_knowledge(
            query=request.query,
            knowledge_source_id=request.knowledge_source_id,
            limit=request.limit
        )
        
        search_results = [SearchResult(**result) for result in results]
        
        return SearchResponse(
            query=request.query,
            results=search_results,
            total_results=len(search_results)
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@app.get("/search", response_model=SearchResponse)
async def search_knowledge_get(
    query: str = Query(..., description="Search query"),
    knowledge_source_id: Optional[str] = Query(None, description="Optional knowledge source filter"),
    limit: Optional[int] = Query(10, description="Maximum number of results")
):
    """Search for relevant knowledge chunks using GET."""
    try:
        results = await rag_engine.search_knowledge(
            query=query,
            knowledge_source_id=knowledge_source_id,
            limit=limit
        )
        
        search_results = [SearchResult(**result) for result in results]
        
        return SearchResponse(
            query=query,
            results=search_results,
            total_results=len(search_results)
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@app.post("/context", response_model=ContextResponse)
async def get_rag_context(request: ContextRequest):
    """Generate formatted context for LLM injection."""
    try:
        context = await rag_engine.get_context(
            query=request.query,
            knowledge_source_id=request.knowledge_source_id,
            max_tokens=request.max_tokens
        )
        
        # Count chunks in context (rough estimation)
        chunk_count = context.count("Source:") if context else 0
        
        return ContextResponse(
            query=request.query,
            context=context,
            chunk_count=chunk_count
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Context generation failed: {str(e)}")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)