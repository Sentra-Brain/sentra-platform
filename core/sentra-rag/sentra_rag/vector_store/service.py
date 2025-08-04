from typing import List, Dict, Any, Optional
from uuid import UUID
import httpx
from sentra_rag.core.settings import rag_settings


class VectorStoreService:
    """Service for interacting with ChromaDB vector store."""

    def __init__(self):
        self.chroma_url = rag_settings.chroma_url
        self.collection_name = rag_settings.collection_name

    async def query_similar_documents(
        self,
        query_embedding: List[float],
        knowledge_source_id: Optional[UUID] = None,
        limit: int = None
    ) -> Dict[str, Any]:
        """
        Query ChromaDB for similar documents based on embedding.
        
        Args:
            query_embedding: The embedding vector to search with
            knowledge_source_id: Optional filter by knowledge source
            limit: Maximum number of results to return
            
        Returns:
            ChromaDB query results
        """
        if limit is None:
            limit = rag_settings.default_search_limit
            
        # Build the query request
        query_request = {
            "query_embeddings": [query_embedding],
            "n_results": limit
        }
        
        # Add knowledge source filter if specified
        if knowledge_source_id:
            query_request["where"] = {"knowledge_source_id": str(knowledge_source_id)}
        
        # Make HTTP request to ChromaDB
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.chroma_url}/api/v1/collections/{self.collection_name}/query",
                json=query_request,
                timeout=30.0
            )
            
            if response.status_code != 200:
                raise RuntimeError(f"ChromaDB query failed: {response.status_code} - {response.text}")
            
            return response.json()

    async def get_collection_info(self) -> Dict[str, Any]:
        """Get information about the ChromaDB collection."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.chroma_url}/api/v1/collections/{self.collection_name}",
                timeout=10.0
            )
            
            if response.status_code != 200:
                raise RuntimeError(f"Failed to get collection info: {response.status_code} - {response.text}")
            
            return response.json()