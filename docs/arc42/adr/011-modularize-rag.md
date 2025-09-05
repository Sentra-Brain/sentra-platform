# 011 – Modularize RAG with Dedicated Package and Services

## Status

Accepted

## Context

Sentra Brain is evolving to support Retrieval-Augmented Generation (RAG) capabilities, both for indexing knowledge sources and retrieving contextual information during user conversations.

Currently:

* `sentra-rag-worker` performs document indexing via RabbitMQ.
* The `sentra-api` is beginning to support RAG-based prompting.

However, using sentence-transformers and ChromaDB within the API introduces significant image bloat, longer build times, and tight coupling between conversational logic and heavy ML infrastructure. Reusing embedding and vector store logic is also problematic as it’s currently isolated inside the worker.

## Decision

We will modularize the RAG subsystem into three distinct but coordinated components:

```
core/
├── sentra-core/            # Common infra (DB, settings, etc.)
├── sentra-rag/             # RAG logic: embeddings, vector store, chunking

services/
├── sentra-rag-base/        # Shared Docker image with heavy RAG dependencies
├── sentra-rag-server/      # Lightweight API for RAG retrieval
├── sentra-rag-worker/      # Async document indexer via RabbitMQ
```

A shared **Docker base image** (`Dockerfile`) already exists within `sentra-rag-worker` as `Dockerfile.base` and `requirements.rag.txt`. This base image will be **moved to `services/sentra-rag-base/`** to serve as the foundation for both the server and worker.

The shared Python package `packages/sentra-rag/` will include:

* Embedding providers (sentence-transformers)
* VectorStoreService (ChromaDB)
* Chunking logic
* Shared DTOs and filters

The API (`sentra-api`) will offload embedding and retrieval to `sentra-rag-server` over HTTP, keeping its own image lightweight and fast to deploy.

## Consequences

### ✅ Pros

* API remains lightweight and free of heavy ML/NLP dependencies.
* RAG logic is centralized, testable, and shared across services.
* Flexible deployment: RAG components can scale or move independently.
* Reduced Docker layer duplication via shared base image.
* Cleaner separation of concerns (API vs indexing vs retrieval).

### ❗️ Cons

* Requires maintaining and deploying an additional service (`rag-server`).
* Introduces inter-service network dependency between API and RAG.

## Alternatives Considered

### ❌ Keep all RAG logic inside sentra-api

* Too heavy and slow to build.
* Not scalable if embedding backend or vector DB changes.

### ❌ Place embedding logic in sentra-core

* Violates `core`’s purpose (infrastructure, not ML pipelines).
* Makes downstream services heavier by default.

### ❌ Duplicate code between worker and API

* Leads to inconsistencies and maintenance burden.

## Implementation Plan

1. Create `packages/sentra-rag` as internal shared library.
2. Move embedding and vector store logic from `sentra-rag-worker` into `sentra-rag`.
3. Build `sentra-rag-server` as a minimal FastAPI service with `/retrieve` and `/embed` endpoints.
4. Move `Dockerfile.base` and `requirements.rag.txt` into `services/sentra-rag-base/` and standardize the build.
5. Update both `rag-server` and `rag-worker` to use the base image.
6. Update `sentra-api` to query `rag-server` when RAG is requested in a conversation.

## References

* [ChromaDB](https://www.trychroma.com/)
* [SentenceTransformers](https://www.sbert.net/)
* [ADR Format](https://adr.github.io/)
