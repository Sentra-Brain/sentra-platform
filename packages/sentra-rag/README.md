# Sentra RAG

RAG-specific logic for Sentra Brain including:

- Embedding providers and models
- Vector store operations  
- Document chunking strategies
- RAG query services

## Installation

```bash
pip install -e .
```

## Usage

```python
from sentra.rag.embeddings import get_embedding_provider
from sentra.rag.services import RAGQueryService

# Get embedding provider
provider = get_embedding_provider()
embeddings = provider.embed_query("example query")

# Use RAG service
rag_service = RAGQueryService()
results = await rag_service.search_documents("query")
```