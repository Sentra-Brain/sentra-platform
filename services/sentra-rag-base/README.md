# Sentra RAG Base Image

This directory contains the base Docker image for RAG services with ChromaDB and sentence-transformers dependencies.

## Build

```bash
docker build -t sentra-rag-base .
```

## Dependencies

- ChromaDB
- sentence-transformers  
- Basic Python RAG stack

This base image is used by:
- sentra-rag-server
- sentra-rag-worker