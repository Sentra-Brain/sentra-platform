from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import RedirectResponse
from sentra.shared import logging
from sentra_rag_server.rag_engine import RAGEngine
from sentra_rag_server.schemas import (
    SearchRequest,
    SearchResponse,
    SearchResult,
    ContextRequest,
    ContextResponse,
    MemorizeRequest,
    MemorizeResponse,
    SearchMemoriesRequest,
)
from typing import Optional
import os
import uvicorn

logging.configure_logging()
logger = logging.get_logger("sentra_rag_server")

# Initialize RAG engine
rag_engine = RAGEngine()

# Create FastAPI app
app = FastAPI(
    title="Sentra RAG Server",
    description="REST API for RAG (Retrieval-Augmented Generation) operations",
    version="1.0.0"
)

# Routes
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "Sentra.Rag.Server"}


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
        context, chunk_count = await rag_engine.get_context(
            query=request.query,
            knowledge_source_id=request.knowledge_source_id,
            max_tokens=request.max_tokens
        )
        
        return ContextResponse(
            query=request.query,
            context=context,
            chunk_count=chunk_count
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Context generation failed: {str(e)}")


@app.post("/memorize", response_model=MemorizeResponse)
async def memorize(request: MemorizeRequest):
    """Store a user memory in the dedicated collection."""
    try:
        memory_id = await rag_engine.memorize(
            user_id=request.user_id,
            session_id=request.session_id,
            text=request.text,
        )
        return MemorizeResponse(status="ok", memory_id=memory_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Memorize failed: {str(e)}")


@app.post("/search_memories", response_model=SearchResponse)
async def search_memories(request: SearchMemoriesRequest):
    """Search user-scoped memories."""
    try:
        results = await rag_engine.search_memories(
            user_id=request.user_id,
            query=request.query,
            limit=request.limit,
        )
        search_results = [SearchResult(**r) for r in results]
        return SearchResponse(
            query=request.query,
            results=search_results,
            total_results=len(search_results),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search memories failed: {str(e)}")


@app.get("/", include_in_schema=False, response_class=RedirectResponse)
async def redirect_to_swagger():
    logger.info("Redirect to swagger...")
    return RedirectResponse(url="/docs")
    
if __name__ == "__main__":
    import uvicorn
    debug_mode = os.getenv("DEBUG_MODE", "false").lower() == "true"
    logging.configure_logging(debug=debug_mode)
    logger = logging.get_logger("sentra_rag_server")

    if debug_mode:
        logger.info("✅ Debug mode enabled: waiting for debugger on port 5680")
        import debugpy
        debugpy.listen(("0.0.0.0", 5680))
        debugpy.wait_for_client()
    port = int(os.getenv("PORT", "9100"))

    uvicorn.run(app, host="0.0.0.0", port=port, log_level="debug" if debug_mode else "info")
