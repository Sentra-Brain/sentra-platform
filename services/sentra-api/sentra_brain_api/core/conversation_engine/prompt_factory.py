# updated PromptFactory to accept RAG chunks and build final payload with optimal ordering
from typing import Optional, List, Dict
from sentra_brain_api.core.constants import CONTEXT_WINDOW_SIZE, SYSTEM_PROMPT
from sentra_brain_api.core.conversation_engine.rag.rag_formatting import format_chunks_grouped
from sentra_brain_api.core.conversation_engine.rag.rag_chunk import RagChunk

class PromptFactory:
    def __init__(self):
        self.default_system_prompt = SYSTEM_PROMPT

    def build_payload(
        self,
        context: List[Dict],
        new_message: Dict,
        rag_chunks: Optional[List[RagChunk]] = None,
        tool_context: Optional[str] = None,
        tools: Optional[list[dict]] = None,  
        *,
        temperature: float = 0.7,
        top_p: float = 0.95,
        presence_penalty: float = 0.0,
        frequency_penalty: float = 0.0,
        max_tokens: int = 1024,
    ) -> Dict:
        """
        Constructs the final payload for the LLM server, including:
        1. System prompt
        2. Optional: RAG context (formatted)
        3. Optional: Initial user intent (first user message)
        4. Context window (trimmed to fit)
        5. Current user message
        """
        messages: List[Dict] = []

        # 1. System prompt
        messages.append({"role": "system", "content": self.default_system_prompt})

        # 2. Inject RAG context if present
        if rag_chunks:
            messages.append({
                "role": "system",
                "content": "You may use the following internal documents to answer. **Do not copy them verbatim.**\n\n" + format_chunks_grouped(rag_chunks),
            })

        if tool_context:
            messages.append({
                "role": "system",
                "content": "You may use the following tool results if relevant:\n\n" + tool_context
            })

        # 3. Highlight initial user intent (optional)
        first_user = next((m for m in context if m["role"] == "user"), None)
        if first_user:
            messages.append({
                "role": "user",
                "content": f"(initial intent) {first_user['content']}"
            })

        # 4. Context window trimming
        trimmed_context = context[-CONTEXT_WINDOW_SIZE:]
        messages.extend(trimmed_context)

        # 5. Append new user message
        messages.append(new_message)

        # Final payload
        payload =  {
            "messages": messages,
            "stream": True,
            "temperature": temperature,
            "top_p": top_p,
            "presence_penalty": presence_penalty,
            "frequency_penalty": frequency_penalty,
            "max_tokens": max_tokens
        }
        if tools:
            payload["tools"] = tools
            payload["tool_choice"] = "auto"
        return payload
