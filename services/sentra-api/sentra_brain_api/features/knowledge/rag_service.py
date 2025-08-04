# sentra_brain_api/features/knowledge/rag_service.py

from typing import List, Dict, Any, Optional
from uuid import UUID
import httpx
import os
from sentence_transformers import SentenceTransformer

from sentra_core.core.logging import get_logger

logger = get_logger(__name__)


class RAGQueryService:
    """Service for performing RAG queries against the ChromaDB vector store."""

    def __init__(self):
        self.embedding_model = None
        self.chroma_client = None

    def _get_embedding_model(self):
        """Lazy load the embedding model."""
        if self.embedding_model is None:
            # Use the same model as the RAG worker for consistency
            model_name = os.getenv('EMBEDDING_MODEL', 'BAAI/bge-base-en-v1.5')
            logger.info(f"Loading embedding model: {model_name}")
            self.embedding_model = SentenceTransformer(model_name)
        return self.embedding_model

    async def search_documents(
        self,
        query: str,
        knowledge_source_id: Optional[UUID] = None,
        limit: int = 10
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
        try:
            # Generate embedding for the query
            model = self._get_embedding_model()
            query_embedding = model.encode(query).tolist()
            
            # Prepare ChromaDB query
            chroma_url = os.getenv('CHROMA_URL', 'http://chroma:8000')
            collection_name = "document_chunks"
            
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
                    f"{chroma_url}/api/v1/collections/{collection_name}/query",
                    json=query_request,
                    timeout=30.0
                )
                
                if response.status_code != 200:
                    logger.error(f"ChromaDB query failed: {response.status_code} - {response.text}")
                    return []
                
                results = response.json()
            
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
            
            logger.info(f"Found {len(formatted_results)} relevant chunks for query")
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error searching documents: {e}")
            return []

    async def get_context_for_query(
        self,
        query: str,
        knowledge_source_id: Optional[UUID] = None,
        max_tokens: int = 4000
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
        try:
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
                logger.info(f"Generated context with {estimated_tokens} estimated tokens from {len(context_parts)} chunks")
                return context
            else:
                return ""
                
        except Exception as e:
            logger.error(f"Error generating context for query: {e}")
            return ""