# Use Case: Chat with LLM + Knowledge Base (RAG)

**Category:** Core  
**Actors:** Authenticated User, Sentra Brain System  
**Priority:** High  
**Triggers:** User sends a chat message with Knowledge Base enrichment enabled  

## Description

When this mode is active, Sentra Brain enriches the LLM prompt with relevant information retrieved from the organization’s indexed Knowledge Base using RAG (Retrieval-Augmented Generation).

The user experience remains similar to normal chat, but the system performs an internal search in ChromaDB before forwarding the final prompt to the LLM backend.

## Basic Flow

1. User logs into Sentra Web.
2. User opens the chat interface and selects "Knowledge Base" mode.
3. User types a message and sends it.
4. Sentra Brain API receives the message:
    - Verifies authentication and slot availability.
    - Queries ChromaDB using embeddings generated from the user message.
    - Retrieves top N relevant documents or chunks.
    - Injects retrieved context into the system prompt or chat history.
5. Sentra Brain forwards the enriched prompt to the LLM backend.
6. LLM generates the response considering both the user’s message and the injected context.
7. Sentra Brain API relays the response to the frontend.
8. The frontend displays the response, optionally showing a "Knowledge Base Assisted" indicator.

## Extensions

- If no relevant documents are found:
    - System proceeds with plain LLM chat, optionally displaying a notice.
- If ChromaDB is unavailable:
    - System logs the error and optionally disables Knowledge Base mode for that session.

## Notes

- Context injection format depends on LLM backend limitations (context size, token limits).
- Retrieval parameters (e.g., top_k, similarity threshold) are configurable_
