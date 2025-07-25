from typing import List, Dict, Any, Optional
from uuid import UUID
import chromadb
from chromadb.config import Settings as ChromaSettings
from sentra_rag_worker.core.config import settings
from sentra_rag_worker.core.logging import get_logger

logger = get_logger(__name__)


class VectorStoreService:
    """Manage document chunks in ChromaDB vector store."""

    def __init__(self):
        self.client = None
        self.collection = None

    def connect(self):
        """Connect to ChromaDB server."""
        try:
            # Parse ChromaDB URL
            chroma_host = settings.chroma_url.replace('http://', '').replace('https://', '')
            host, port = chroma_host.split(':') if ':' in chroma_host else (chroma_host, '8000')
            
            logger.info(f"Connecting to ChromaDB at {host}:{port}")
            
            self.client = chromadb.HttpClient(
                host=host,
                port=int(port)
            )
            
            # Get or create collection for document chunks
            collection_name = "document_chunks"
            self.collection = self.client.get_or_create_collection(
                name=collection_name,
                metadata={"description": "Document chunks for RAG"}
            )
            
            logger.info(f"Connected to ChromaDB collection: {collection_name}")
            
        except Exception as e:
            logger.error(f"Failed to connect to ChromaDB: {e}")
            raise

    def index_document_chunks(
        self, 
        document_id: UUID, 
        knowledge_source_id: UUID,
        chunks: List[str], 
        embeddings: List[List[float]],
        filename: str,
        source_type: str = "file"
    ) -> int:
        """Index document chunks into ChromaDB.
        
        Args:
            document_id: UUID of the document
            knowledge_source_id: UUID of the knowledge source
            chunks: List of text chunks
            embeddings: List of embedding vectors
            filename: Name of the source file
            source_type: Type of source (file, folder, etc.)
            
        Returns:
            Number of chunks indexed
        """
        if not self.collection:
            self.connect()

        if len(chunks) != len(embeddings):
            raise ValueError("Number of chunks must match number of embeddings")

        try:
            document_id_str = str(document_id)
            knowledge_source_id_str = str(knowledge_source_id)
            
            # Prepare data for ChromaDB
            ids = []
            metadatas = []
            
            for i, chunk in enumerate(chunks):
                chunk_id = f"{document_id_str}_chunk_{i}"
                ids.append(chunk_id)
                
                metadata = {
                    "document_id": document_id_str,
                    "knowledge_source_id": knowledge_source_id_str,
                    "chunk_index": i,
                    "filename": filename,
                    "source_type": source_type,
                    "chunk_length": len(chunk)
                }
                metadatas.append(metadata)

            # Add to ChromaDB collection
            self.collection.add(
                ids=ids,
                embeddings=embeddings,
                documents=chunks,
                metadatas=metadatas
            )
            
            logger.info(f"Indexed {len(chunks)} chunks for document {document_id}")
            return len(chunks)
            
        except Exception as e:
            logger.error(f"Failed to index chunks for document {document_id}: {e}")
            raise

    def delete_document_chunks(self, document_id: UUID) -> int:
        """Delete all chunks for a document.
        
        Args:
            document_id: UUID of the document
            
        Returns:
            Number of chunks deleted
        """
        if not self.collection:
            self.connect()

        try:
            document_id_str = str(document_id)
            
            # Query for all chunks with this document_id
            results = self.collection.get(
                where={"document_id": document_id_str}
            )
            
            chunk_ids = results['ids']
            if chunk_ids:
                # Delete the chunks
                self.collection.delete(ids=chunk_ids)
                logger.info(f"Deleted {len(chunk_ids)} chunks for document {document_id}")
                return len(chunk_ids)
            else:
                logger.info(f"No chunks found for document {document_id}")
                return 0
                
        except Exception as e:
            logger.error(f"Failed to delete chunks for document {document_id}: {e}")
            raise

    def search_similar_chunks(
        self, 
        query_embedding: List[float], 
        knowledge_source_id: Optional[UUID] = None,
        n_results: int = 10
    ) -> List[Dict[str, Any]]:
        """Search for similar chunks.
        
        Args:
            query_embedding: Query embedding vector
            knowledge_source_id: Optional filter by knowledge source
            n_results: Number of results to return
            
        Returns:
            List of similar chunks with metadata
        """
        if not self.collection:
            self.connect()

        try:
            where_clause = {}
            if knowledge_source_id:
                where_clause["knowledge_source_id"] = str(knowledge_source_id)

            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                where=where_clause if where_clause else None
            )
            
            # Format results
            similar_chunks = []
            for i in range(len(results['ids'][0])):
                chunk = {
                    "id": results['ids'][0][i],
                    "document": results['documents'][0][i],
                    "metadata": results['metadatas'][0][i],
                    "distance": results['distances'][0][i]
                }
                similar_chunks.append(chunk)
            
            return similar_chunks
            
        except Exception as e:
            logger.error(f"Failed to search similar chunks: {e}")
            raise