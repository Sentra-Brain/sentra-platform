# Use Case: Upload Document to Knowledge Base

**Category:** Core  
**Actors:** Authenticated User, Administrator, Sentra Brain System  
**Priority:** High  
**Triggers:** User uploads a document through Sentra Web  

## Description

Users can upload documents to be indexed into Sentra Brain's knowledge base. Once processed, documents are available for RAG (Retrieval-Augmented Generation) enrichment during chat interactions.

Documents are shared across all users and linked to the organization’s central ChromaDB instance.  

## Basic Flow

1. User logs into Sentra Web.
2. User accesses the "Knowledge Base" section.
3. User selects "Upload Document".
4. System accepts supported file types (PDF, TXT, DOCX, Markdown).
5. System shows upload progress and stores the file securely.
6. Sentra Brain API processes the document:
    - Extracts text content.
    - Splits into chunks suitable for embeddings.
    - Generates embeddings and stores them in ChromaDB.
7. System confirms successful indexation to the user.
8. Uploaded document appears in the Knowledge Base list with metadata:
    - Filename
    - Upload date
    - Uploaded by
    - Processing status

## Extensions

- If file format is unsupported:
    - System shows an error message.
- If embedding service or ChromaDB is unavailable:
    - System queues the document for later processing.
    - User is notified of delayed availability.

## Notes

- Maximum file size limit is defined in configuration (e.g., 20 MB).
- Uploaded files may be stored temporarily or permanently depending on organization policy.
- Metadata about uploaded documents is stored in db-auth-users or equivalent admin database.
- Admins may have permissions to delete or re-index documents (future phase).
- Sentra Brain does not expose uploaded documents to external systems without explicit user or admin action.
