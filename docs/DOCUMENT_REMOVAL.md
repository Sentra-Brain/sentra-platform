# Document Removal Feature

This document describes the new document removal functionality added to the Sentra Brain system.

## Overview

The document removal feature provides asynchronous processing of document deletion requests through a dedicated RabbitMQ queue. This allows the system to safely remove documents from both the vector store (ChromaDB) and the file system while maintaining proper status tracking.

## Architecture

The removal system consists of several components:

1. **RemoveDocumentJob Schema** - Defines the structure of removal job messages
2. **RemovalJobPublisher** - Publishes removal jobs to the dedicated queue
3. **RemovalJobConsumer** - Consumes messages from the removal queue
4. **DocumentRemovalProcessor** - Handles the actual removal logic
5. **Updated RAGWorker** - Extended to handle both indexing and removal queues

## Components

### 1. RemoveDocumentJob Schema

Located at: `libs/sentra-shared/sentra_shared/model/remove_document_job.py`

```python
from sentra_shared.model.remove_document_job import RemoveDocumentJob
from uuid import uuid4

job = RemoveDocumentJob(
    document_id=uuid4(),
    knowledge_source_id=uuid4(),
    user_id=uuid4()
)
```

### 2. RemovalJobPublisher

Located at: `libs/sentra-shared/sentra_shared/domain/services/removal_job_publisher.py`

```python
from sentra_shared.domain.services.removal_job_publisher import RemovalJobPublisher
from sentra_shared.model.remove_document_job import RemoveDocumentJob

# Create a removal job
job = RemoveDocumentJob(
    document_id=document_id,
    knowledge_source_id=knowledge_source_id,
    user_id=user_id
)

# Publish the job
with RemovalJobPublisher() as publisher:
    success = publisher.publish_remove_document_job(job)
```

### 3. Document Status Updates

The system now supports additional document statuses:

```python
from sentra_shared.domain.enums.document import DocumentStatus

# New statuses for removal workflow
DocumentStatus.TO_BE_REMOVED  # "to_be_removed"
DocumentStatus.REMOVED        # "removed"
```

### 4. RAG Worker Integration

The `sentra-rag-worker` now handles both indexing and removal queues:

- **Indexing Queue**: `indexation_queue` (default)
- **Removal Queue**: `removal_jobs`

## Removal Workflow

When a document removal job is processed, the following steps occur:

1. **Status Update**: Document status → `TO_BE_REMOVED`
2. **Vector Store Cleanup**: Remove all chunks from ChromaDB
3. **File System Cleanup**: Remove the physical file from disk
4. **Final Status Update**: Document status → `REMOVED` (or `FAILED` if errors occur)

## Queue Configuration

The removal system uses a dedicated RabbitMQ queue:

- **Queue Name**: `removal_jobs`
- **Durability**: True (messages persist across restarts)
- **Isolation**: Separate from indexing jobs for better fault tolerance

## Error Handling

The removal processor includes comprehensive error handling:

- **Missing Document**: Marks job as failed if document not found in database
- **Vector Store Errors**: Continues with file removal even if ChromaDB cleanup fails
- **File System Errors**: Continues to mark as removed even if file deletion fails
- **Database Errors**: Properly handles database connection and transaction failures

## Testing

Several test files are provided to validate the functionality:

1. **Basic Tests**: `services/sentra-rag-worker/test_removal.py`
   - Tests core schemas and imports
   
2. **CLI Test Tool**: `services/sentra-rag-worker/cli_test_removal.py`
   - Manual testing of job creation and message formatting
   
3. **Standalone Tests**: `services/sentra-rag-worker/test_removal_standalone.py`
   - Comprehensive tests with mocked dependencies

### Running Tests

```bash
# Basic functionality tests
cd services/sentra-rag-worker
python test_removal.py

# CLI test tool
python cli_test_removal.py <document_id> <knowledge_source_id> <user_id>

# Standalone comprehensive tests
python test_removal_standalone.py
```

## Usage Examples

### Publishing a Removal Job

```python
from sentra_shared.domain.services.removal_job_publisher import RemovalJobPublisher
from sentra_shared.model.remove_document_job import RemoveDocumentJob
from uuid import UUID

# Create the job
job = RemoveDocumentJob(
    document_id=UUID("550e8400-e29b-41d4-a716-446655440000"),
    knowledge_source_id=UUID("550e8400-e29b-41d4-a716-446655440001"),
    user_id=UUID("550e8400-e29b-41d4-a716-446655440002")
)

# Publish using context manager
with RemovalJobPublisher() as publisher:
    success = publisher.publish_remove_document_job(job)
    if success:
        print("Removal job published successfully")
    else:
        print("Failed to publish removal job")
```

### Batch Publishing

```python
from sentra_shared.domain.services.removal_job_publisher import RemovalJobPublisher
from sentra_shared.model.remove_document_job import RemoveDocumentJob

jobs = [
    RemoveDocumentJob(document_id=doc_id1, knowledge_source_id=ks_id, user_id=user_id),
    RemoveDocumentJob(document_id=doc_id2, knowledge_source_id=ks_id, user_id=user_id),
    # ... more jobs
]

with RemovalJobPublisher() as publisher:
    published_count = publisher.publish_multiple_removal_jobs(jobs)
    print(f"Published {published_count}/{len(jobs)} removal jobs")
```

## Configuration

The removal system uses the same RabbitMQ configuration as the indexing system:

```env
RABBITMQ_HOST=localhost
RABBITMQ_PORT=5672
RABBITMQ_USER=sentra
RABBITMQ_PASSWORD=sentra
```

No additional configuration is required as the removal queue name is hardcoded to `removal_jobs`.

## Monitoring and Logging

The system provides comprehensive logging for:

- Job publishing success/failure
- Removal workflow progress
- Error conditions and recovery
- Performance metrics (chunks removed, files processed)

All logs include correlation IDs for tracing individual removal jobs through the system.

## Integration with Existing System

The removal feature is designed to integrate seamlessly with the existing Sentra Brain system:

- **No Breaking Changes**: Existing indexing functionality remains unchanged
- **Shared Infrastructure**: Uses the same RabbitMQ and database connections
- **Status Compatibility**: New document statuses are additive to existing ones
- **Error Handling**: Follows existing patterns for consistency

## Future Enhancements

Potential improvements for the removal system:

1. **Batch Processing**: Support for bulk document removal
2. **Soft Delete**: Option to mark documents as deleted without physical removal
3. **Audit Trail**: Detailed logging of what was removed and when
4. **Recovery**: Ability to restore accidentally removed documents
5. **Permissions**: Integration with user permissions system for removal authorization