> **Community Fair-Use:** Sentra Brain CE is AGPL-3.0.  
> Free **internal use up to 5 seats** per organization; commercial license required beyond that.  
> See **`COMMUNITY-TERMS.md`** and **`LICENSE`**.
# Sentra RAG Base Image

This directory contains the base Docker image for RAG services with ChromaDB and sentence-transformers dependencies.

## Build

```bash
docker build -t Sentra.Rag.Base .
```

## Dependencies

- ChromaDB
- sentence-transformers  
- Basic Python RAG stack

This base image is used by:
- Sentra.Rag.Server
- Sentra.Rag.Worker