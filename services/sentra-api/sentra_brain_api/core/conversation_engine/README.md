# 🧠 `conversation_engine` – Conversational Core for Sentra Brain

## Purpose

This module powers the conversational capabilities of Sentra Brain, enabling a structured and extensible message-to-response pipeline. It manages user messages, conversational context, tool invocation (via MCP), prompt generation, and streaming responses from the underlying LLM (e.g., vLLM).

This engine is the "brainstem" of Sentra Brain's chat functionality.

---

## 📐 High-Level Architecture

```
User Input → Intent Parsing → Step Planning →
→ (Optional: RAG / Tool Dispatch) →
→ Prompt Generation → LLM Call →
→ Response Formatting → Return to User
```

Each part of this flow is modular, extensible, and optimized for:
- Latency (via memory caching of context)
- Tool integration (MCP dispatch)
- Future extension (RAG, tool use, streaming)

---

## 🗂 Directory Structure

```bash
conversation_engine/
├── engine.py               # Main ConversationEngine class
├── context.py              # Slot, Copilot, Permissions, Thread info
├── input_model.py          # ConversationRequest, IntentOverride, etc.
├── output_model.py         # ConversationResponse, with stream support
├── planner.py              # Flow decision (LLM only, Tool use, etc.)
├── prompt_factory.py       # Prompt creation logic
├── step_runner.py          # Executes chain of steps: LLM, RAG, Tools
├── rag.py                  # RAG connector (ChromaDB)
├── tool_dispatcher.py      # MCP tool execution
├── streaming.py            # LLM streaming response utils
├── registry/               # Declarative registries
│   ├── copilots.py
│   ├── intents.py
│   ├── context_sources.py
│   └── tools.py
```

---

## ✅ Current Scope – Phase 1: Plain Chat (No RAG, No Tools)

### Chat Flow Example

```
[User Input]
→ ConversationRequest(user_id, content, conversation_id)
→ ConversationEngine.receive_message()
  → context = get_or_create_conversation_context()
  → planner = determine_flow()
    → basic_llm_chat
  → step_runner.run() → LLM call
  → response = format_and_return()
→ ConversationResponse (content, metadata)
```

### API Contract – `/v1/chat/completions`

```json
POST /v1/chat/completions
{
  "conversation_id": "abc123",
  "parent_message_id": "msg456",
  "content": "¿Cuál es la capital de Italia?",
  "model": "sentra-brain"
}
```

### Backend Behavior

1. Retrieve conversation context from memory or MongoDB.
2. Trim previous messages to fit LLM context window.
3. Generate prompt using `prompt_factory.py`.
4. Send to vLLM (via HTTP/streaming).
5. Persist message and LLM reply.
6. Return response (optionally streamed) to frontend.

---

## 🧠 Context and Caching Strategy

### In-Memory Conversation Cache

To avoid fetching full history on every message:

- Use `cachetools.LRUCache` per instance.
- Key: `(user_id, conversation_id)`
- Value: partial context (last N messages, metadata)

```python
conversation_cache = LRUCache(maxsize=500)
```

Fallback: fetch from MongoDB or persistent store when not cached.

---

## 📌 Design Inspirations

### LangChain-Inspired Concepts

- **Steps and Chains** → `step_runner.py` orchestrates the pipeline.
- **Tool/Skill routing** → `tool_dispatcher.py` integrates with MCP.
- **Prompt abstraction** → `prompt_factory.py` mimics LangChain PromptTemplates.
- **ContextObject** → unifica estado (user, slot, copilot, tools disponibles).

---

## 🔭 Roadmap & Milestones

### ✅ Phase 1 – Basic Chat

- [x] `ConversationEngine.receive_message()`
- [x] Prompt factory for basic chat
- [x] vLLM HTTP integration
- [x] Streamed & non-streamed responses
- [x] In-memory conversation cache (per user/session)

### ⏳ Phase 2 – Tool Calls + RAG

- [ ] Step planner with tool detection
- [ ] MCP skill integration
- [ ] ChromaDB connection with filtered sources
- [ ] Copilot-specific behavior (from registry)

### 🚧 Phase 3 – Conversation Tree, Slots, Persistence

- [ ] parent_message_id graph
- [ ] Message metadata (tool calls, RAG, etc.)
- [ ] Slot and permission enforcement
- [ ] Full conversation management (titles, deletion)

---

## 🧪 Example Usage (Python)

```python
from conversation_engine.engine import ConversationEngine
from conversation_engine.input_model import ConversationRequest

engine = ConversationEngine()

request = ConversationRequest(
    user_id="user-123",
    conversation_id="conv-456",
    content="¿Cuál es la capital de Italia?",
)

response = engine.receive_message(request)
print(response.content)
```

---

## 💡 Notes for Frontend Integration (sentra-web)

- Cache `conversation_id` per tab/panel.
- Only send new message content (not full history).
- Expect streamed or non-streamed response.
- Always provide `parent_message_id` if available (for conversation threading).

---

## 👥 Contributors

- Juan G Carmona – Lead Architect
- Sentra Brain Team

---

## 🔗 Related Modules

- `mcp/` – for tool execution via MCP
- `rag/` – for document retrieval via Chroma
- `admin/` – to configure tools, slots, copilots
