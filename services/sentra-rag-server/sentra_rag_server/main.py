from fastapi import FastAPI, HTTPException, Query
from sentra_core.core import logging
from sentra_rag.vector_store.chroma_http import ChromaHttpVectorStore
from sentra_rag_server.rag_engine import RAGEngine
from sentra_rag_server.schemas import SearchRequest, SearchResponse, SearchResult, ContextRequest, ContextResponse
from typing import AsyncGenerator, Optional
import os
import uvicorn

logging.configure_logging()
logger = logging.get_logger("sentra_rag_server")

# Initialize RAG engine
rag_engine = RAGEngine()

async def app_lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    logger.info("🔧 Initializing RAG engine...")
    # Startup: init Chroma vector store if needed
    if isinstance(rag_engine.rag_service.vector_store, ChromaHttpVectorStore):
        logger.info("🔧 Initializing Chroma HTTP Vector Store...")
        await rag_engine.rag_service.vector_store.init()
        logger.info("✅ Chroma HTTP Vector Store initialized")
    yield
    # No teardown needed

app = FastAPI(
    title="Sentra RAG Server",
    description="REST API for RAG (Retrieval-Augmented Generation) operations",
    version="1.0.0"
)

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

    uvicorn.run(app, host="0.0.0.0", port=9100, log_level="debug" if debug_mode else "info")