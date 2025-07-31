from typing import List
from sentence_transformers import SentenceTransformer
from sentra_rag_worker.core.config import settings
from sentra_core.core.logging import get_logger

logger = get_logger(__name__)


class EmbeddingService:
    """Generate embeddings using BGE model."""

    def __init__(self, model_name: str = None):
        self.model_name = model_name or settings.embedding_model
        self._model = None

    @property
    def model(self) -> SentenceTransformer:
        """Lazy load the embedding model."""
        if self._model is None:
            logger.info(f"Loading embedding model: {self.model_name}")
            self._model = SentenceTransformer(self.model_name)
            logger.info("Embedding model loaded successfully")
        return self._model

    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for a list of texts.
        
        Args:
            texts: List of text strings to embed
            
        Returns:
            List of embedding vectors (normalized)
        """
        if not texts:
            return []

        try:
            logger.info(f"Generating embeddings for {len(texts)} texts")
            
            # Generate embeddings
            embeddings = self.model.encode(
                texts,
                normalize_embeddings=True,  # Normalize for better similarity search
                show_progress_bar=False
            )
            
            # Convert to list of lists for JSON serialization
            embeddings_list = embeddings.tolist()
            
            logger.info(f"Generated {len(embeddings_list)} embeddings of dimension {len(embeddings_list[0])}")
            return embeddings_list
            
        except Exception as e:
            logger.error(f"Failed to generate embeddings: {e}")
            raise

    def generate_single_embedding(self, text: str) -> List[float]:
        """Generate embedding for a single text.
        
        Args:
            text: Text string to embed
            
        Returns:
            Embedding vector (normalized)
        """
        embeddings = self.generate_embeddings([text])
        return embeddings[0] if embeddings else []