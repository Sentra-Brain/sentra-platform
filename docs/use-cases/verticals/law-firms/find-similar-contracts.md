# Use Case: Find Similar Contracts in Knowledge Base

**Category:** Vertical — Law Firms  
**Actors:** Authenticated User (Lawyer), Sentra Brain System  
**Priority:** High  
**Triggers:** User submits a contract excerpt or uploads a document for similarity search  

## Description

Law firm users can search for contracts or legal documents similar to a given example or text excerpt.  
Sentra Brain uses ChromaDB similarity search based on embeddings to retrieve relevant documents already indexed in the Knowledge Base.  

This helps lawyers quickly find precedent agreements, reuse templates, or verify consistency.

## Basic Flow

1. User logs into Sentra Web.
2. User navigates to the Knowledge Base section or opens the chat interface.
3. User pastes a text excerpt or uploads a document.
4. System extracts the text (if necessary) and generates embeddings.
5. Sentra Brain queries ChromaDB for similar entries:
    - Uses configured similarity threshold and top_k parameters.
6. System displays the list of most similar documents:
    - Document name
    - Similarity score
    - Preview snippet
    - Link to full document view.

## Extensions

- If no similar contracts are found:
    - System informs the user and suggests uploading new documents.
- If multiple highly similar results exist:
    - System allows sorting or filtering by date, uploader, or metadata.

## Notes

- Similarity threshold and number of results are configurable per installation.
- Uploaded or pasted text is not automatically stored—only used for search unless saved manually.
- Admin UI allows managing indexing priority and datasets.
- This feature depends on ChromaDB availability and up-to-date indexing.
