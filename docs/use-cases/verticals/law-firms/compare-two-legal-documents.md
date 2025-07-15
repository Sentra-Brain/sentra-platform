# Use Case: Compare Two Legal Documents

**Category:** Vertical — Law Firms  
**Actors:** Authenticated User (Lawyer), Sentra Brain System  
**Priority:** High  
**Triggers:** User selects two legal documents from Knowledge Base  

## Description

Law firm users can compare two legal documents—such as contracts, rulings, or clauses—directly through Sentra Web.  
Sentra Brain retrieves both documents, processes them, and generates a similarity or difference report using RAG embeddings and/or LLM summarization.  

This helps legal professionals detect contractual changes, highlight differences in clauses, or validate standard template integrity.

## Basic Flow

1. User logs into Sentra Web.
2. User navigates to the Knowledge Base.
3. User selects two existing documents:
    - Document A
    - Document B
4. User clicks "Compare Documents".
5. Sentra Brain API retrieves full content for both documents.
6. Sentra Brain processes both texts:
    - Generates embeddings and calculates similarity metrics.
    - Optionally sends both texts to the LLM for structured difference analysis.
7. System presents results to the user:
    - Overall similarity score.
    - Highlighted textual differences.
    - Suggested summary of key changes (if applicable).

## Extensions

- If documents are too large:
    - System limits comparison to first N tokens or chunks.
- If one document is not indexed:
    - System shows an error and prompts re-indexing.

## Notes

- Comparisons use both ChromaDB similarity search and LLM-based text comparison.
- Admin can configure maximum document size and processing limits.
- UI must clearly show:
    - Original document previews.
    - Differences side by side.
    - Summary notes or suggestions from the LLM.
- This feature operates fully offline and does not depend on external APIs.