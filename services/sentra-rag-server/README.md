# Sentra RAG Server

REST API microservice for RAG (Retrieval-Augmented Generation) operations.

## Features

- **GET/POST /search** - Semantic search using embeddings
- **POST /context** - Generate formatted context for LLM injection
- **GET /health** - Health check endpoint
- **GET /settings** - Current RAG configuration

## Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Run the server
python app.py
```

## Docker

```bash
# Build base image first
cd ../sentra-rag-base
docker build -t sentra-rag-base .

# Build and run RAG server
cd ../sentra-rag-server
docker build -t sentra-rag-server .
docker run -p 8000:8000 sentra-rag-server
```

## Environment Variables

- `CHROMA_URL` - ChromaDB URL (default: http://chroma:8000)
- `CHROMA_COLLECTION_NAME` - Collection name (default: document_chunks)
- `EMBEDDING_MODEL` - Model name (default: BAAI/bge-base-en-v1.5)
- `MAX_CONTEXT_TOKENS` - Max context tokens (default: 4000)