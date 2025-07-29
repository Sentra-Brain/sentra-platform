# ADR: Replace `llama-server` with `vLLM` as LLM Inference Runtime

## Status

✅ Accepted

## Context

Sentra Brain currently uses `llama-server` (based on `llama.cpp`) as its local inference server for LLMs. While this setup has worked for basic tasks like chat and RAG indexing with low concurrency, it exhibits significant limitations for scaling to:

* Agentic AI runtimes with multiple concurrent agents
* Multi-user real-time usage
* Concurrent workloads from FastAPI services, RAG worker, and knowledge tools
* Compatibility with emerging agent frameworks like AutoGen, LangGraph, or CrewAI

**Key limitations of `llama-server`:**

* Synchronous, single-threaded inference (no batching)
* No session or concurrency control
* Poor GPU resource efficiency under load
* Non-standard API (WebSocket-based, no OpenAI compatibility)
* Limited observability or queueing mechanisms

As Sentra evolves toward more advanced, concurrent agent orchestration and local copilots, a more scalable, standardized inference backend is required.

## Decision

We will replace `llama-server` with [`vLLM`](https://github.com/vllm-project/vllm) as the primary inference runtime for local LLMs.

### Why vLLM?

* ✅ **OpenAI-compatible API** (chat/completions/stream)
* ✅ **Dynamic batching + high concurrency support**
* ✅ **GPU memory-efficient** (paged attention, KV cache)
* ✅ **Fast, production-grade, and container-ready**
* ✅ Seamless integration with agent frameworks (LangGraph, AutoGen, CrewAI)
* ✅ Supports HuggingFace models like LLaMA 2, Mistral, Qwen, etc.

We will migrate from `.gguf`-formatted models (for `llama.cpp`) to equivalent `.bin` or `.safetensors` models from HuggingFace Transformers.

### Example Docker Compose service:

```yaml
services:
  vllm:
    image: vllm/vllm-openai
    container_name: vllm
    ports:
      - "8002:8000"  # External port 8002, internal remains 8000
    volumes:
      - D:\models:/models:ro
    command: >
      --model /models/llama-2-13b
      --dtype float16
      --gpu-memory-utilization 0.9
    networks:
      - sentrabrain-dev-net
    deploy:
      resources:
        reservations:
          devices:
            - capabilities: [gpu]
    runtime: nvidia
```

## Consequences

### Positive:

* 🔄 Drop-in OpenAI API compatibility (for LangChain, tools, agents, UI)
* ⚡ Significantly improved performance for multi-agent and multi-user loads
* 🧠 Foundation for agent orchestration (Agentic AI, concurrent copilots)
* 🧰 Better compatibility with observability tools and standardized API gateways

### Trade-offs:

* ❗ Requires GPU and more memory than `llama.cpp` builds
* 🔄 Models must be migrated to HuggingFace formats (`.bin`, `.safetensors`)
* 📦 Existing WebSocket-based consumers may need adaptation
* 🛠️ Services using `llama-server` directly must update base URLs and headers

## Required Changes

### 1. Replace LLM client implementation:

A new `VLLMClient` class should be introduced with streaming support, similar to the current `LlamaServerClient`:

```python
import httpx
from typing import AsyncGenerator

class VLLMClient:
    def __init__(self, base_url: str):
        self.base_url = base_url

    async def chat_completion(self, payload: dict) -> AsyncGenerator[str, None]:
        url = f"{self.base_url}/v1/chat/completions"

        async with httpx.AsyncClient(timeout=None) as client:
            async with client.stream("POST", url, json=payload) as response:
                if response.status_code >= 400:
                    body = await response.aread()
                    raise RuntimeError(f"LLM error {response.status_code}: {body.decode(errors='replace')}")

                async for line in response.aiter_lines():
                    yield line
```

This client will be used by the `ConversationEngine`, replacing the old llama.cpp streaming logic.

### 2. Ensure concurrent streaming is supported:

FastAPI endpoints should allow **asynchronous, concurrent** streaming per user request using `StreamingResponse`, which is already in place in Sentra Brain. Example:

```python
@router.post("/send", response_class=StreamingResponse)
async def send_message(...):
    ...
    return StreamingResponse(stream(), media_type="text/event-stream")
```

Each agent or user-triggered request must invoke an isolated `engine.run()` pipeline, ensuring non-blocking execution.

### 3. Add lightweight wrapper for LLM access:

To decouple LLM usage, we should introduce a minimal interface or decorator that standardizes access to any OpenAI-compatible LLM engine, abstracting client and payload construction.

## Alternatives Considered

* **Keeping `llama-server` with queue-based proxying** → rejected due to complexity and no batching/memory efficiency.
* **`LocalAI`** (OpenAI-compatible + llama.cpp) → promising, lightweight, but lacks batching and large-scale inference capabilities.
* **`TGI` (HuggingFace)** → strong alternative but less GPU-efficient than `vLLM`; limited GGUF support.

## Related Tasks

* [ ] Benchmark `vLLM` memory usage and latency on A6000
* [ ] Update `sentra_rag_worker`, `conversation_engine`, and `fastapi` agents to use new client and/or endpoint
* [ ] Add auth config and observability integration to `vLLM` container (Prometheus or OTel)
* [ ] Implement new `VLLMClient` with proper error streaming and fallback logic
