# sentra_brain_api/features/knowledge/routes/rag.py

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from uuid import UUID

from sentra_core.infra.sql.postgres_service import get_db
from sentra_core.domain.entities.user_entity import UserEntity
from sentra_core.domain.repository.knowledge_source_repository import KnowledgeSourceRepository

from sentra_brain_api.features.knowledge.rag_service import RAGQueryService
from sentra_brain_api.features.knowledge.schemas import (
    RAGSearchRequest,
    RAGSearchResponse,
    RAGContextRequest, 
    RAGContextResponse,
    DocumentChunkResponse
)
from sentra_brain_api.crosscutting.authorization import get_authenticated_user

router = APIRouter()

def _get_rag_service() -> RAGQueryService:
    return RAGQueryService()

def _get_knowledge_repo(db: Session = Depends(get_db)) -> KnowledgeSourceRepository:
    return KnowledgeSourceRepository(db)

@router.post("/search", response_model=RAGSearchResponse)
async def search_knowledge(
    request: RAGSearchRequest,
    user: UserEntity = Depends(get_authenticated_user),
    rag_service: RAGQueryService = Depends(_get_rag_service),
    knowledge_repo: KnowledgeSourceRepository = Depends(_get_knowledge_repo)
):
    """
    Search for relevant document chunks based on a query.
    """
    try:
        # Validate knowledge source access if specified
        if request.knowledge_source_id:
            knowledge_source = knowledge_repo.find_by_id(request.knowledge_source_id)
            if not knowledge_source:
                raise HTTPException(status_code=404, detail="Knowledge source not found")
            # TODO: Add proper access control check based on user permissions
        
        # Perform the search
        chunks = await rag_service.search_documents(
            query=request.query,
            knowledge_source_id=request.knowledge_source_id,
            limit=request.limit
        )
        
        # Convert to response format
        chunk_responses = [
            DocumentChunkResponse(
                chunk_id=chunk["chunk_id"],
                content=chunk["content"],
                metadata=chunk["metadata"],
                relevance_score=chunk["relevance_score"]
            )
            for chunk in chunks
        ]
        
        return RAGSearchResponse(
            query=request.query,
            chunks=chunk_responses,
            total_results=len(chunk_responses)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@router.post("/context", response_model=RAGContextResponse)
async def get_rag_context(
    request: RAGContextRequest,
    user: UserEntity = Depends(get_authenticated_user),
    rag_service: RAGQueryService = Depends(_get_rag_service),
    knowledge_repo: KnowledgeSourceRepository = Depends(_get_knowledge_repo)
):
    """
    Get formatted context for RAG-enhanced LLM queries.
    """
    try:
        # Validate knowledge source access if specified
        if request.knowledge_source_id:
            knowledge_source = knowledge_repo.find_by_id(request.knowledge_source_id)
            if not knowledge_source:
                raise HTTPException(status_code=404, detail="Knowledge source not found")
            # TODO: Add proper access control check based on user permissions
        
        # Generate context
        context = await rag_service.get_context_for_query(
            query=request.query,
            knowledge_source_id=request.knowledge_source_id,
            max_tokens=request.max_tokens
        )
        
        # Count sources and estimate tokens
        sources_used = context.count("Source:") if context else 0
        estimated_tokens = len(context) // 4 if context else 0  # Rough estimate
        
        return RAGContextResponse(
            query=request.query,
            context=context,
            sources_used=sources_used,
            estimated_tokens=estimated_tokens
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Context generation failed: {str(e)}")


# Convenience endpoint for quick searches
@router.get("/search", response_model=RAGSearchResponse) 
async def quick_search(
    q: str = Query(..., description="Search query", min_length=1),
    knowledge_source_id: Optional[str] = Query(None, description="Knowledge source ID filter"),
    limit: int = Query(10, description="Max results", ge=1, le=50),
    user: UserEntity = Depends(get_authenticated_user),
    rag_service: RAGQueryService = Depends(_get_rag_service),
    knowledge_repo: KnowledgeSourceRepository = Depends(_get_knowledge_repo)
):
    """
    Quick search endpoint using query parameters.
    """
    # Convert knowledge_source_id string to UUID if provided
    knowledge_source_uuid = None
    if knowledge_source_id:
        try:
            knowledge_source_uuid = UUID(knowledge_source_id)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid knowledge source ID format")
    
    # Use the same logic as POST search
    request = RAGSearchRequest(
        query=q,
        knowledge_source_id=knowledge_source_uuid,
        limit=limit
    )
    
    return await search_knowledge(request, user, rag_service, knowledge_repo)