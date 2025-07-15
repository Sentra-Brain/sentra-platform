# Use Case: Summarize Uploaded Case Files

**Category:** Vertical — Law Firms  
**Actors:** Authenticated User (Lawyer), Sentra Brain System  
**Priority:** High  
**Triggers:** User uploads a legal document and requests a summary  

## Description

Law firm users can upload long case files (e.g., court rulings, evidence documents, legal briefs) and request a summary via Sentra Brain.  
The system processes the document using RAG or LLM summarization workflows, helping users quickly understand large volumes of legal text.

## Basic Flow

1. User logs into Sentra Web.
2. User navigates to the Knowledge Base or Summary Tool.
3. User uploads a document (PDF, DOCX, TXT).
4. Sentra Brain API processes the file:
    - Extracts text content.
    - Splits text into chunks if necessary.
    - Stores it temporarily or indexes it if added to the Knowledge Base.
5. User clicks "Summarize This Document."
6. Sentra Brain sends the text to the LLM backend:
    - Optionally enriches with related context from ChromaDB (RAG mode).
    - Or uses pure LLM summarization based on the document content alone.
7. System presents the summary to the user:
    - Executive summary (short version).
    - Detailed section-by-section summary (optional).
8. User can download, copy, or attach the summary to other workflows.

## Extensions

- If the document is too large:
    - System prompts the user to split it or limits summarization to key sections.
- If the document was previously summarized:
    - System shows the cached summary, with an option to refresh.

## Notes

- Supports multiple languages depending on LLM model capabilities.
- Summarization can operate in two modes:
    - Chat-driven request (natural language query).
    - Dedicated summary action in the Knowledge Base UI.
- Admins can configure summary length and chunking behavior.
- Uploaded documents are handled securely and comply with privacy policies.
