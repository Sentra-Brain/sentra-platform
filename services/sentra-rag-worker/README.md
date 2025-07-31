# Sentra RAG Worker

A background service for processing document ingestion jobs sent via RabbitMQ. This worker is responsible for extracting content from documents, chunking text, generating embeddings, and indexing into ChromaDB.

## Features

- **Message Processing**: Consumes indexation jobs from RabbitMQ
- **Document Extraction**: Extracts text content from PDF, DOCX, TXT, and MD files
- **Text Chunking**: Intelligent text chunking with configurable overlap
- **Embedding Generation**: Uses BGE model for high-quality embeddings
- **Vector Indexing**: Stores embeddings in ChromaDB for similarity search
- **Folder Scanning**: Periodically scans folder-type knowledge sources for new files
- **Status Tracking**: Updates document processing status in PostgreSQL
- **Error Handling**: Comprehensive logging and error recovery

## Architecture

```
RabbitMQ Queue → Document Processor → ChromaDB
                       ↓
                 PostgreSQL (status updates)
```

### Components

- **DocumentProcessor**: Main orchestrator for the processing pipeline
- **DocumentExtractor**: Extracts content from various file formats
- **TextChunker**: Splits text into overlapping chunks
- **EmbeddingService**: Generates embeddings using BGE model
- **VectorStoreService**: Manages ChromaDB indexing operations
- **FolderScanner**: Scans folder sources for new documents
- **RabbitMQConsumer**: Processes messages from the indexation queue

## Configuration

Environment variables (see `.env.example`):

```env
# Database
DATABASE_URL=postgresql://sentra:sentra@sentra-sql-db:5432/sentra_brain

# RabbitMQ
RABBITMQ_HOST=rabbitmq
RABBITMQ_PORT=5672
RABBITMQ_USER=sentra
RABBITMQ_PASSWORD=sentra
RABBITMQ_QUEUE=indexation_queue

# ChromaDB
CHROMA_URL=http://sentra-vector-db:8000

# Processing
KNOWLEDGE_ROOT=/mnt/sentra_knowledge
FOLDER_SCAN_INTERVAL=60
EMBEDDING_MODEL=BAAI/bge-base-en-v1.5
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
```

## Message Format

Indexation jobs received from RabbitMQ:

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

## Processing Pipeline

1. **Validation**: Verify file exists and matches metadata
2. **Extraction**: Extract clean text content using appropriate parser
3. **Chunking**: Split text into overlapping chunks with smart boundaries
4. **Embedding**: Generate vector embeddings using BGE model
5. **Indexing**: Store chunks and embeddings in ChromaDB
6. **Status Update**: Mark document as indexed with chunk count

## Docker Deployment

The service uses a **two-layer Docker build** strategy for optimal CI/CD performance:

1. **Base Image** (`Dockerfile.base`): Contains heavy dependencies and system packages
2. **Application Image** (`Dockerfile`): Contains application code and builds FROM the base image

### CI/CD Pipeline

The GitHub Actions pipeline automatically:

1. **Detects Changes**: Checks if `requirements.rag.txt` has been modified
2. **Base Image Build**: If requirements changed, builds and pushes `sentra-rag-base:py3.13` to ACR
3. **Application Build**: Builds the final application image using the ACR base image
4. **Optimization**: Skips base image rebuild when only application code changes

### Base Image (`Dockerfile.base`)

```dockerfile
FROM python:3.13-slim

ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    build-essential \
    libmagic1 \
    poppler-utils \
    tesseract-ocr \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /base
COPY requirements.rag.txt .
RUN pip install --no-cache-dir -r requirements.rag.txt

ENV PYTHONUNBUFFERED=1
```

### Application Image (`Dockerfile`)

```dockerfile
ARG BASE_IMAGE=sentra-rag-base:py3.13
FROM ${BASE_IMAGE}

WORKDIR /app

COPY core/sentra-core /core/sentra-core
RUN pip install -e /core/sentra-core
COPY services/sentra-rag-worker/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY services/sentra-rag-worker /app

CMD ["python", "-m", "sentra_rag_worker.main"]
```

### Local Development

For local development, you can still build the traditional way:

```bash
# Build base image locally (one-time setup)
docker build -f Dockerfile.base -t sentra-rag-base:py3.13 .

# Build application image
docker build -f Dockerfile -t sentra-rag-worker:local .
```

### Benefits

- **Faster CI/CD**: Base image only rebuilds when dependencies change
- **Smaller Layers**: Application code changes don't trigger base layer rebuild  
- **Cache Efficiency**: Docker layer caching works optimally
- **ACR Integration**: Base images are centrally managed in Azure Container Registry


## Development

### Running Tests

```bash
# Basic component tests
python tests/test_basic.py

# Integration tests
python tests/test_integration.py
```

### Local Development

1. Copy `.env.example` to `.env` and configure
2. Install dependencies: `pip install -r requirements.txt`
3. Run the worker: `python -m sentra_rag_worker.main`

## Folder Scanning

The worker periodically scans folder-type knowledge sources:

- Discovers new supported files (PDF, DOCX, TXT, MD)
- Creates document entries in the database
- Queues indexation jobs for new files
- Marks missing files as failed

## Error Handling

- Comprehensive logging for all processing steps
- Graceful failure handling with status updates
- Message requeuing for transient failures
- Proper resource cleanup and connection management

## Performance Considerations

- Processes one message at a time to avoid resource contention
- Efficient text chunking with sentence/word boundary detection
- Normalized embeddings for optimal similarity search
- Configurable chunk sizes and overlap for different use cases

## Monitoring

The worker provides structured logging for monitoring:

- Document processing status and timing
- Error details with context
- Folder scan results
- System resource usage