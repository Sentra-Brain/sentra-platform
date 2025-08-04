from typing import List, Dict, Any, Optional
from uuid import UUID
from sentra_rag.embeddings.provider import get_embedding_provider
from sentra_rag.vector_store.service import VectorStoreService
from sentra_rag.core.settings import rag_settings


class RAGQueryService:
    """Service for performing RAG queries against the vector store."""

    def __init__(self):
        self.embedding_provider = get_embedding_provider()
        self.vector_store = VectorStoreService()

    async def search_documents(
        self,
        query: str,
        knowledge_source_id: Optional[UUID] = None,
        limit: int = None
    ) -> List[Dict[str, Any]]:
        """
        Search for relevant document chunks based on a query.
        
        Args:
            query: The search query
            knowledge_source_id: Optional filter by knowledge source
            limit: Maximum number of results to return
            
        Returns:
            List of relevant document chunks with metadata
        """
        if limit is None:
            limit = rag_settings.default_search_limit
            
        # Generate embedding for the query
        query_embedding = self.embedding_provider.embed_query(query)
        
        # Query the vector store
        results = await self.vector_store.query_similar_documents(
            query_embedding=query_embedding,
            knowledge_source_id=knowledge_source_id,
            limit=limit
        )
        
        # Format results for API response
        formatted_results = []
        if results.get('ids') and len(results['ids']) > 0:
            for i in range(len(results['ids'][0])):
                chunk_data = {
                    "chunk_id": results['ids'][0][i],
                    "content": results['documents'][0][i],
                    "metadata": results['metadatas'][0][i],
                    "relevance_score": 1.0 - results['distances'][0][i]  # Convert distance to similarity
                }
                formatted_results.append(chunk_data)
        
        return formatted_results

    async def get_context_for_query(
        self,
        query: str,
        knowledge_source_id: Optional[UUID] = None,
        max_tokens: int = None
    ) -> str:
        """
        Get formatted context for RAG-enhanced LLM queries.
        
        Args:
            query: The user query
            knowledge_source_id: Optional filter by knowledge source
            max_tokens: Maximum tokens to include in context
            
        Returns:
            Formatted context string ready for LLM injection
        """
        if max_tokens is None:
            max_tokens = rag_settings.max_context_tokens
            
        # Search for relevant chunks
        chunks = await self.search_documents(
            query=query,
            knowledge_source_id=knowledge_source_id,
            limit=20  # Get more chunks initially
        )
        
        if not chunks:
            return ""
        
        # Format context with estimated token limiting
        context_parts = []
        estimated_tokens = 0
        
        for chunk in chunks:
            content = chunk['content']
            metadata = chunk['metadata']
            
            # Estimate tokens (rough approximation: 1 token ≈ 4 characters)
            chunk_tokens = len(content) // 4
            
            if estimated_tokens + chunk_tokens > max_tokens:
                break
            
            # Format chunk with source information
            filename = metadata.get('filename', 'Unknown')
            chunk_index = metadata.get('chunk_index', 0)
            
            formatted_chunk = f"Source: {filename} (chunk {chunk_index})\n{content}\n"
            context_parts.append(formatted_chunk)
            estimated_tokens += chunk_tokens
        
        if context_parts:
            context = "Relevant information from your knowledge base:\n\n" + "\n---\n".join(context_parts)
            return context
        else:
            return ""