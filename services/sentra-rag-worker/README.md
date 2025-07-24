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
CHROMA_URL=http://sentra-vector-db:8001

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

The service runs as a Docker container in the Sentra Brain ecosystem:

```dockerfile
FROM python:3.11-slim
# ... (see Dockerfile for full details)
CMD ["python", "-m", "sentra_rag_worker.main"]
```

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