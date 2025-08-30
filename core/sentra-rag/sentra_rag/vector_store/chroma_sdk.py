import chromadb
from typing import List, Dict, Any, Optional
from uuid import UUID
from sentra_rag.settings import rag_settings
from sentra_rag.vector_store.base import BaseVectorStore
from asyncio import to_thread


class ChromaSdkVectorStore(BaseVectorStore):
    def __init__(self):
        chroma_host = rag_settings.chroma_url.replace("http://", "").replace("https://", "")
        host, port = chroma_host.split(":") if ":" in chroma_host else (chroma_host, "8000")

        try:
            self.client = chromadb.HttpClient(host=host, port=int(port))
            self.client.list_collections()
        except Exception as e:
            raise RuntimeError(
                f"❌ Chroma database '{rag_settings.chroma_database}' not found at {host}:{port}. "
                f"Asegúrate de crearla antes de iniciar el worker."
            ) from e

        self.collection = self.client.get_or_create_collection(
            name=rag_settings.collection_name
        )

    async def index_document_chunks(
        self, document_id, knowledge_source_id, chunks, embeddings, filename, source_type="file"
    ) -> int:
        def _index():
            ids = [f"{document_id}_chunk_{i}" for i in range(len(chunks))]
            metadatas = [{
                "document_id": str(document_id),
                "knowledge_source_id": str(knowledge_source_id),
                "chunk_index": i,
                "filename": filename,
                "source_type": source_type,
                "chunk_length": len(chunks[i])
            } for i in range(len(chunks))]
            self.collection.add(ids=ids, embeddings=embeddings, documents=chunks, metadatas=metadatas)
            return len(chunks)

        return await to_thread(_index)

    async def delete_document_chunks(self, document_id: UUID) -> int:
        def _delete():
            result = self.collection.get(where={"document_id": str(document_id)})
            ids = result.get("ids", [])
            if ids:
                self.collection.delete(ids=ids)
            return len(ids)

        return await to_thread(_delete)

    async def query_similar_chunks(
        self, query_embedding: List[float], knowledge_source_id: Optional[UUID], limit: int
    ) -> List[Dict[str, Any]]:
        def _query():
            where = {"knowledge_source_id": str(knowledge_source_id)} if knowledge_source_id else None
            result = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=limit,
                where=where
            )
            chunks = []
            for i in range(len(result["ids"][0])):
                chunks.append({
                    "id": result["ids"][0][i],
                    "document": result["documents"][0][i],
                    "metadata": result["metadatas"][0][i],
                    "distance": result["distances"][0][i]
                })
            return chunks

        return await to_thread(_query)
