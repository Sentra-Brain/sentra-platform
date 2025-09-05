# Sentra Engine (ADK-Based)

## Overview
Sentra Engine is a modular conversation orchestrator powered by agents and tools. It supports RAG, domain-specific logic, and can run locally or in production.

## Layout
- `agents/`: Main LLM agents and use-case logic
- `tools/`: RAG, DB, and other tool wrappers
- `orchestrators/`: Routing logic per vertical
- `context/`: Prompt context builder
- `models/`: Conversation request/response models
- `policies/`: Guardrails, retries, source scoping
- `config.py`: Feature flags, budgets, defaults
- `app.py`: Public API entrypoint: `run_conversation(request)`

## Running Tests
```bash
pytest
```

## Dummy Conversation (for quick test)

Use the `USE_DUMMY=true` env var or override in `config.py` to activate the dummy response path.

## Stream from Python

```python
from sentra.runtime import run_conversation
from sentra.runtime.models import ConversationRequest

async def main():
    request = ConversationRequest(messages=["Hello, what can you do?"])
    async for event in run_conversation(request):
        print(event)
```
