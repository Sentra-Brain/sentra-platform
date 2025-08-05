# Sentra RAG Worker

A background service for ingesting and indexing documents into a vector database. This worker is responsible for extracting content, chunking text, generating embeddings, and indexing into **ChromaDB**, powered by **async processing** and modular architecture.

## 🚀 Features

* 📨 **Message Processing**: Consumes document indexation jobs from RabbitMQ.
* 📄 **Document Extraction**: Supports PDF, DOCX, TXT, MD, EML, MSG, EPUB, HTML.
* 🧹 **Text Chunking**: Configurable sentence-aware chunking with overlap.
* 🧠 **Embedding Generation**: Uses a local BGE model via `sentence-transformers`.
* 🧠 **Pluggable Embedding Provider**: Shared with the RAG server (via `sentra-rag`).
* 📦 **Vector Indexing**: Stores chunks in ChromaDB with metadata.
* 📂 **Folder Scanning**: Scans auto-indexable knowledge sources on disk.
* 🧾 **Status Tracking**: Updates document state and error info in PostgreSQL.
* 🔄 **Linear, Idempotent Processing**: No retries or duplicates — process once.
* 🔍 **Observability**: Prometheus metrics and OpenTelemetry tracing.

## 🧱️ Architecture Overview

```
[RabbitMQ Queue]
        ↓
[DocumentProcessor] → [EmbeddingProvider]
        ↓                     ↓
[Chunker]              [ChromaDB Vector Store]
        ↓
[PostgreSQL (status + metadata)]
```

## 🔧 Configuration

Set via `.env` or environment variables:

```env
# Database
DATABASE_URL=postgresql://...

# RabbitMQ
RABBITMQ_HOST=rabbitmq
RABBITMQ_PORT=5672
RABBITMQ_USER=sentra
RABBITMQ_PASSWORD=sentra
RABBITMQ_QUEUE=indexation_queue

# ChromaDB
CHROMA_URL=http://chroma:8000
VECTOR_STORE_MODE=sdk  # ← Important: 'sdk' for worker, 'http' for server

# Knowledge & Embedding
KNOWLEDGE_ROOT=/mnt/sentra_knowledge
FOLDER_SCAN_INTERVAL=60
EMBEDDING_MODEL=BAAI/bge-base-en-v1.5
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
```

---

## ⚙️ Processing Pipeline

Each message is processed in the following steps:

1. ✅ **Validation**: Ensures metadata and file consistency
2. 📤 **Extraction**: Extracts text via format-specific parsers
3. ✂️ **Chunking**: Splits text into overlapping sentence-aware segments
4. 🧠 **Embedding**: Uses shared embedding provider (`sentra-rag`) for BGE vectors
5. 🧠 **Indexing**: Uploads chunks to ChromaDB via SDK (local vector store)
6. ✅ **Status Update**: Updates document status in the DB (success/failure)

---

## 📦 Components

| Component            | Role                                                             |
| -------------------- | ---------------------------------------------------------------- |
| `DocumentProcessor`  | Main async pipeline for processing and indexing                  |
| `EmbeddingProvider`  | Abstract interface; uses `SentenceTransformersEmbeddingProvider` |
| `VectorStoreService` | Injects/retrieves chunks via ChromaDB (sdk mode)                 |
| `TextChunker`        | Chunking strategy with overlap + break heuristics                |
| `DocumentExtractor`  | Format-specific file content extraction                          |
| `FolderScanner`      | Detects new or missing documents in folder sources               |
| `RabbitMQConsumer`   | Delivers jobs to `_process_indexing_message_linear` (no retries) |

---

## 📬 Message Format

Example indexation job sent to the queue:

```json
{
  "document_id": "uuid",
  "knowledge_source_id": "uuid",
  "filepath": "/mnt/sentra_knowledge/uploads/user123/file.pdf",
  "filename": "file.pdf",
  "display_name": "User Contract",
  "uploaded_by": "user-uuid",
  "filetype": "pdf"
}
```

---

## 🐳 Docker Deployment

The worker uses a **two-stage Docker build** optimized for CI/CD:

### 🔹 `Dockerfile.base` (heavy dependencies)

```dockerfile
FROM python:3.13-slim
RUN apt-get update && apt-get install -y build-essential libmagic1 poppler-utils tesseract-ocr libpq-dev
COPY requirements.rag.txt .
RUN pip install -r requirements.rag.txt
```

### 🔹 `Dockerfile` (application code)

```dockerfile
FROM sentra-rag-base:py3.13
WORKDIR /app
COPY core/sentra-core /core/sentra-core
RUN pip install -e /core/sentra-core
COPY services/sentra-rag-worker /app
CMD ["python", "-m", "sentra_rag_worker.main"]
```

---

## 🧪 Development & Testing

```bash
# Setup
cp .env.example .env
pip install -r requirements.txt

# Run worker
python -m sentra_rag_worker.main

# Run tests
pytest tests/
```

---

## 🕵️‍♂️ Monitoring

* ✅ **OpenTelemetry** traces via OTLP exporter (`OTEL_EXPORTER_OTLP_ENDPOINT`)
* ✅ **Prometheus** metrics (`/metrics` via `prometheus_client`)
* ✅ Structured logging with document IDs, chunk counts, and processing times

---

## 🧠 Notes

* The **embedding engine is shared** with `sentra-rag` (used by both worker and server).
* The **vector store logic is unified**, selecting between `sdk` and `http` based on mode.
* The processing is **intentionally linear**, with no requeue or retry logic.
* All external dependencies (ChromaDB, PostgreSQL, RabbitMQ) are expected to be reachable at startup.
