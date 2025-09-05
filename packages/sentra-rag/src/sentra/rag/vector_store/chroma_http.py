import httpx
from typing import List, Dict, Any, Optional
from uuid import UUID
from sentra.rag.settings import rag_settings
from sentra.rag.vector_store.base import BaseVectorStore
from sentra.shared.logging import get_logger

logger = get_logger(__name__)


class ChromaHttpVectorStore(BaseVectorStore):
    def __init__(self):
        self.base_url = rag_settings.chroma_url.rstrip("/")
        self.tenant = rag_settings.chroma_tenant
        self.database = rag_settings.chroma_database
        self.collection = rag_settings.collection_name
        self._collection_id: Optional[str] = None  # Cached resolved ID

    def _resolve_collection_id_sync(self) -> str:
        url = f"{self.base_url}/api/v2/tenants/{self.tenant}/databases/{self.database}/collections"
        with httpx.Client() as client:
            response = client.get(url, timeout=10)
            response.raise_for_status()
            collections = response.json()

        for collection in collections:
            if collection["name"] == self.collection:
                resolved_id = collection["id"]
                logger.info(f"Resolved Chroma collection '{self.collection}' to ID {resolved_id}")
                return resolved_id

        raise RuntimeError(
            f"Chroma collection '{self.collection}' not found in tenant/database "
            f"{self.tenant}/{self.database}. Cannot proceed."
        )

    def _get_collection_id(self) -> str:
        if self._collection_id is None:
            self._collection_id = self._resolve_collection_id_sync()
        return self._collection_id

    def _collection_query_url(self) -> str:
        return (
            f"{self.base_url}/api/v2/tenants/{self.tenant}/databases/{self.database}/"
            f"collections/{self._get_collection_id()}/query"
        )

    async def query_similar_chunks(
        self,
        query_embedding: List[float],
        knowledge_source_id: Optional[UUID],
        limit: int,
    ) -> List[Dict[str, Any]]:
        payload = {
            "query_embeddings": [query_embedding],
            "n_results": limit,
            "include": ["distances", "documents", "metadatas"],
        }

        if knowledge_source_id:
            payload["where"] = {"knowledge_source_id": str(knowledge_source_id)}

        url = self._collection_query_url()

        try:
            async with httpx.AsyncClient() as client:
                logger.info(f"POST {url}")
                response = await client.post(url, json=payload, timeout=30.0)
                response.raise_for_status()
                results = response.json()

            return [
                {
                    "id": results["ids"][0][i],
                    "document": results["documents"][0][i],
                    "metadata": results["metadatas"][0][i],
                    "distance": results["distances"][0][i],
                }
                for i in range(len(results["ids"][0]))
            ]
        except Exception as e:
            logger.error(f"Chroma HTTP query failed: {e} — payload: {str(payload)[:500]}")
            raise

    async def index_document_chunks(
        self,
        document_id,
        knowledge_source_id,
        chunks,
        embeddings,
        filename,
        source_type="file",
    ) -> int:
        raise NotImplementedError("Indexing is not supported over HTTP API v2.")

    async def delete_document_chunks(self, document_id) -> int:
        raise NotImplementedError("Deletion is not supported over HTTP API v2.")
