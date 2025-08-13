import asyncio
import json
import logging
from typing import AsyncGenerator
from datetime import datetime, timezone
from uuid import UUID, uuid4

from sentra_brain_api.core.conversation_engine.mcp.sentra_mcp_client import SentraMCPClient
from sentra_brain_api.core.conversation_engine.mcp.tool_mapping import mcp_tools_to_openai_tools
from sentra_brain_api.core.conversation_engine.models.input_model import ConversationRequest
from sentra_brain_api.core.conversation_engine.models.output_model import ConversationEvent
from sentra_brain_api.core.conversation_engine.prompt_factory import PromptFactory
from sentra_brain_api.core.conversation_engine.conversations_cache import ConversationsCache
from sentra_brain_api.core.conversation_engine.rag.rag_client import RagClient
from sentra_brain_api.core.constants import CONTEXT_WINDOW_SIZE, USER_CONVERSATION_CACHE_SIZE
from sentra_brain_api.core.exceptions import SentraHTTPException
from sentra_core.infra.nosql.mongo_conversation_repository import get_conversation_mongo_repository
from sentra_core.core.settings import settings
from sentra_brain_api.core.conversation_engine.llm.factory import build_llm_client
from sentra_brain_api.crosscutting.json_sanitize import json_safe


logger = logging.getLogger("sentra_brain_engine")

MAX_TOOL_ROUNDS = 3
MAX_TOOL_OUTPUT_CHARS = 8000

class ConversationEngine:
    def __init__(self, mongo_repo=None, llm_client=None, rag_client=None, mcp_client=None):

        self.mongo_repo = mongo_repo or get_conversation_mongo_repository()
        self.llm_client = llm_client or build_llm_client(
            engine=settings.llm_engine,
            vllm_url=settings.vllm_server_url,
            llama_url=settings.llama_server_url,
            request_timeout=None,
        )
        self.rag_client = rag_client or RagClient()
        self.prompt_factory = PromptFactory()
        self.cache = ConversationsCache(
            capacity=USER_CONVERSATION_CACHE_SIZE,
            on_evict=self._on_cache_evict
        )
        self.mcp_client = mcp_client or SentraMCPClient()
        self._mcp_tools_cache: list[dict] | None = None

    async def run(self, request: ConversationRequest) -> AsyncGenerator[ConversationEvent, None]:
        """
        Single-turn execution of the conversation engine with:
        - Optional RAG context retrieval (emits step_start/step_end events).
        - Tool-use orchestrated by the LLM (OpenAI-style tools, via MCP).
        - SSE-style streaming of assistant tokens (message_delta) until finalization (message_final).
        - Persistence of user/assistant messages and step events in Mongo.
        - LRU cache update for the conversation window.
        """
        logger.info(f"[Engine] Starting run: user={request.user_id}, conversation={request.conversation_id}")
        now = datetime.now(timezone.utc).isoformat()

        # --------------------------------------------
        # 1) RAG step (optional) + step events
        # --------------------------------------------
        task_run_id = None
        if request.context_source_ids or request.context_document_ids:
            task_run_id = uuid4().hex
            step_start_event = ConversationEvent(
                type="step_start",
                task_type="rag_search",
                task_run_id=task_run_id,
                label="Searching Knowledge Base",
                status="searching",
                content="Searching in the Knowledge Base..."
            )
            yield step_start_event
            await self._persist_step_event(request, step_start_event)

        rag_chunks = await self.rag_client.retrieve_relevant_chunks(
            query=request.content,
            source_ids=request.context_source_ids,
            document_ids=request.context_document_ids
        )

        if task_run_id:
            step_end_event = ConversationEvent(
                type="step_end",
                task_type="rag_search",
                task_run_id=task_run_id,
                label="Knowledge Base Search Complete",
                status="completed",
                content=f"Found {len(rag_chunks)} relevant chunks",
                meta={
                    "chunks_found": len(rag_chunks),
                    "source_ids": request.context_source_ids,
                    "document_ids": request.context_document_ids
                }
            )
            yield step_end_event
            await self._persist_step_event(request, step_end_event)

        # --------------------------------------------
        # 2) Load/trim context and persist incoming user message
        # --------------------------------------------
        context = await self._load_context(request.user_id, request.conversation_id)
        user_msg = self._make_message("user", request.content, now, message_id=request.message_id)
        await self._persist_user_message(request, user_msg)

        # --------------------------------------------
        # 3) Prepare MCP tools (converted to OpenAI tools schema)
        # --------------------------------------------
        try:
            mcp_tools = await self._ensure_mcp_tools()
        except Exception as e:
            logger.warning(f"[MCP] list_tools failed: {e}")
            mcp_tools = []
        openai_tools = mcp_tools_to_openai_tools(mcp_tools)
        logger.info(f"[Engine] MCP tools available: {[t['function']['name'] for t in openai_tools]}")

        # Conversation state we actually send to the LLM (we manage it across tool rounds)
        conversation_messages = context[-CONTEXT_WINDOW_SIZE:] + [user_msg]

        # Accumulates streamed assistant text between tool calls
        assistant_text_buffer = ""
        rounds = 0

        # --------------------------------------------
        # 4) Tool-use loop: stream → (maybe) tool_call → execute MCP → continue
        # --------------------------------------------
        while True:
            # Build payload with tools and RAG; overwrite messages with our running conversation state
            payload = self.prompt_factory.build_payload(
                context=context,
                new_message=user_msg,
                rag_chunks=rag_chunks,
                tool_context=None,
                tools=openai_tools
            )
            payload["messages"] = conversation_messages
            payload["model"] = request.model or "sentra-brain"  # make sure the backend receives an explicit model

            # This captures a single pending tool call if the model emits one (arguments may arrive chunked).
            pending_tool = {"id": None, "name": None, "args": ""}

            # Stream assistant deltas until either completion or a tool call appears
            async for line in self.llm_client.chat_completion(payload):
                raw = (line or "").strip()
                if not raw:
                    continue
                if raw.lower().startswith("data:"):
                    raw = raw[5:].strip()
                if raw == "[DONE]":
                    break

                try:
                    delta = self._extract_delta(raw)
                    if not delta:
                        continue

                    # Regular token content → forward as message_delta and buffer it
                    if delta.get("content"):
                        chunk = delta["content"]
                        assistant_text_buffer += chunk
                        yield ConversationEvent(type="message_delta", content=chunk)

                    # Tool call (OpenAI-style tool_calls or legacy function_call) → accumulate name/args
                    tc = self._tool_call_from_delta(delta)
                    if tc and tc.get("name"):
                        if tc.get("id"):
                            pending_tool["id"] = tc["id"]
                        pending_tool["name"] = tc["name"]
                        pending_tool["args"] += tc.get("arguments_chunk") or ""

                    # End-of-turn conditions; if a tool has been requested, break to execute it
                    if delta.get("finish_reason") in ("stop", "length", "tool_calls", "tool_call"):
                        if pending_tool["name"]:
                            break
                except Exception as e:
                    logger.error(f"Stream parse error: {e}")

            # If the model requested a tool, execute it and feed the result back before looping again
            if pending_tool["name"]:
                if rounds >= MAX_TOOL_ROUNDS:
                    logger.warning("Max tool rounds reached; skipping further tool calls.")
                    # We stop calling more tools; the partially built answer (if any) will be finalized below.
                    break

                rounds += 1
                # Parse tool arguments as JSON (fall back to raw string if needed)
                try:
                    args = json.loads(pending_tool["args"] or "{}")
                except json.JSONDecodeError:
                    args = {"_raw": pending_tool["args"]}

                # If we streamed some assistant text already, seal it into the transcript
                if assistant_text_buffer:
                    conversation_messages.append({"role": "assistant", "content": assistant_text_buffer})
                    assistant_text_buffer = ""

                # The assistant must record the tool call (no content), so the model can link the subsequent tool result
                tool_call_id = pending_tool.get("id") or uuid4().hex
                assistant_toolcall_msg = {
                    "role": "assistant",
                    "content": None,
                    "tool_calls": [{
                        "id": tool_call_id,
                        "type": "function",
                        "function": {
                            "name": pending_tool["name"],
                            "arguments": json.dumps(args, ensure_ascii=False)
                        }
                    }]
                }
                conversation_messages.append(assistant_toolcall_msg)

                # Emit/persist step events around MCP execution
                t_run_id = uuid4().hex
                step_start = ConversationEvent(
                    type="step_start",
                    task_type=f"mcp:{pending_tool['name']}",
                    task_run_id=t_run_id,
                    label=f"Calling tool: {pending_tool['name']}",
                    status="running",
                    content=f"Executing tool {pending_tool['name']}..."
                )
                yield step_start
                await self._persist_step_event(request, step_start)

                # Execute tool via MCP
                try:
                    tool_output = await self._call_mcp_tool(pending_tool["name"], args)
                    step_end = ConversationEvent(
                        type="step_end",
                        task_type=f"mcp:{pending_tool['name']}",
                        task_run_id=t_run_id,
                        label=f"Tool {pending_tool['name']} completed",
                        status="completed",
                        content=f"Tool returned {len(tool_output)} chars."
                    )
                    yield step_end
                    await self._persist_step_event(request, step_end)
                except Exception as e:
                    tool_output = f"[tool_error] {e}"
                    step_end = ConversationEvent(
                        type="step_end",
                        task_type=f"mcp:{pending_tool['name']}",
                        task_run_id=t_run_id,
                        label=f"Tool {pending_tool['name']} failed",
                        status="failed",
                        content=str(e)
                    )
                    yield step_end
                    await self._persist_step_event(request, step_end)

                # (Optional) Persist the tool call summary as a system message for auditability
                try:
                    self.mongo_repo.append_message(
                        conversation_id=request.conversation_id,
                        user_id=request.user_id,
                        message={
                            "id": uuid4().hex,
                            "role": "system",
                            "content": f"[tool_call] {pending_tool['name']} args={args}",
                            "timestamp": datetime.now(timezone.utc).isoformat(),
                            "type": "tool_call",
                            "tool_name": pending_tool["name"],
                            "tool_args": json_safe(args),
                        }
                    )
                except Exception:
                    pass

                # Provide the tool result back to the model, linked by tool_call_id
                conversation_messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call_id,
                    "content": tool_output
                })

                # Reset and continue another LLM round (the while loop restarts with updated transcript)
                pending_tool = {"id": None, "name": None, "args": ""}
                continue

            # No pending tool: the model considered the turn complete → exit the tool loop
            break

        # --------------------------------------------
        # 5) Finalize assistant message, persist, cache, and signal completion
        # --------------------------------------------
        final_text = assistant_text_buffer.strip()
        if not final_text:
            logger.warning(f"No LLM response for user={request.user_id} conv={request.conversation_id}")
            yield ConversationEvent(type="message_final", content="(No answer provided by the assistant)")
            return

        assistant_msg = self._make_message("assistant", final_text, now, message_id=request.response_message_id)
        await self._persist_assistant_message(request, assistant_msg)

        context.append(assistant_msg)
        self.cache.put(request.user_id, request.conversation_id, context[-CONTEXT_WINDOW_SIZE:])

        yield ConversationEvent(type="message_final", content="")
        logger.info(f"[Engine] Completed run: user={request.user_id}, conversation={request.conversation_id}")

    async def _stream_llm(self, payload: dict):
        async for line in self.llm_client.chat_completion(payload):
            if not line:
                continue

            # normalize and remove 'data:' prefix
            raw = line.strip()
            if not raw:
                continue
            if raw.lower().startswith("data:"):
                raw = raw[5:].strip()
                
            if raw == "[DONE]":
                break

            if not raw or raw.startswith(":"):
                continue

            try:
                data = json.loads(raw)
                delta = data.get("choices", [{}])[0].get("delta", {}).get("content", "")
                if delta:
                    yield delta
            except json.JSONDecodeError:
                logger.debug(f"Streaming non-JSON line ignored: {raw!r}")
            except Exception as e:
                logger.error(f"Unexpected error in streaming loop: {e}")

    async def _load_context(self, user_id: UUID, conversation_id: UUID) -> list[dict]:
        try:
            cached = self.cache.get(user_id, conversation_id)
            if cached is not None:
                logger.debug(f"[Cache HIT] user={user_id}, conversation={conversation_id}")
                return list(cached)
            
            logger.debug(f"[Cache MISS] user={user_id}, conversation={conversation_id}")
            doc = self.mongo_repo.get_conversation_by_id(conversation_id, user_id)
            if not doc:
                raise SentraHTTPException(
                    status_code=404,
                    code="CONVERSATION_NOT_FOUND",
                    message="Conversation not found.",
                    details=f"Conversation ID: {conversation_id}",
                    path="/chat/send",
                    suggestion="Verify the conversation_id is correct."
                )
            messages = doc.get("messages", [])
            if not isinstance(messages, list):
                raise SentraHTTPException(
                    status_code=500,
                    code="INVALID_CONVERSATION_DATA",
                    message="Invalid messages format in conversation",
                    details=f"Expected list, got: {type(messages).__name__}",
                    path="/chat/send"
                )
            trimmed = messages[-CONTEXT_WINDOW_SIZE:]
            self.cache.put(user_id, conversation_id, trimmed)
            return trimmed
        except SentraHTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to load context: {e}")
            raise SentraHTTPException(
                status_code=500,
                code="CONTEXT_LOAD_FAILED",
                message="Failed to load conversation context.",
                details=str(e),
                path="/chat/send",
                suggestion="Try again or contact support."
            )

    def _make_message(self, role: str, content: str, timestamp: str, **extra) -> dict:
        mid = extra.pop("message_id", None)
        rid = extra.pop("response_message_id", None)
        final_id = str(mid or rid or uuid4().hex)

        safe_extra = {k: json_safe(v) for k, v in extra.items() if v is not None}

        return {
            "id": final_id,
            "role": role,
            "content": content,
            "timestamp": timestamp,
            **safe_extra
        }        

    def _extract_delta(self, raw_line: str) -> dict | None:
        # assumes 'data: {...}' normalized JSON format
        try:
            data = json.loads(raw_line)
            # OpenAI format
            choice = (data.get("choices") or [{}])[0]
            delta = choice.get("delta") or {}
            return {
                "content": delta.get("content"),
                "tool_calls": delta.get("tool_calls"),                 # new
                "function_call": delta.get("function_call"),           # legacy
                "finish_reason": choice.get("finish_reason"),
            }
        except Exception:
            return None

    def _tool_call_from_delta(self, delta: dict) -> dict | None:
        # Supports both OpenAI tool calls and legacy function_call format
        if not delta:
            return None
        # New: tool_calls [{id, function: {name, arguments}}]
        tcs = delta.get("tool_calls")
        if isinstance(tcs, list) and tcs:
            tc = tcs[0]  # support only the first tool call for now
            fn = (tc.get("function") or {})
            return {
                "id": tc.get("id"),
                "name": fn.get("name"),
                "arguments_chunk": fn.get("arguments", ""),
                "is_chunked": True
            }
        # Legacy: function_call chunked {name, arguments}
        fc = delta.get("function_call")
        if isinstance(fc, dict) and (fc.get("name") or fc.get("arguments") is not None):
            return {
                "id": None,
                "name": fc.get("name"),
                "arguments_chunk": fc.get("arguments") or "",
                "is_chunked": True
            }
        return None

    async def _ensure_mcp_tools(self) -> list[dict]:
        if self._mcp_tools_cache is None:
            self._mcp_tools_cache = await self.mcp_client.list_tools()
        return self._mcp_tools_cache

    async def _call_mcp_tool(self, tool_name: str, arguments: dict) -> str:
        res = await self.mcp_client.call_tool(tool_name, arguments)
        if isinstance(res, (dict, list, tuple)):
            txt = json.dumps(res, ensure_ascii=False, indent=2)
        else:
            txt = str(res)
        if len(txt) > MAX_TOOL_OUTPUT_CHARS:
            txt = txt[:MAX_TOOL_OUTPUT_CHARS] + "\n\n[truncated]"
        return txt

    async def _persist_user_message(self, request: ConversationRequest, message: dict):
        try:
            self.mongo_repo.append_message(
                conversation_id=request.conversation_id,
                user_id=request.user_id,
                message=message
            )
        except Exception as e:
            logger.error(f"Failed to persist user message: {e}")
            raise SentraHTTPException(
                status_code=500,
                code="USER_MESSAGE_STORE_FAILED",
                message="Failed to store user message.",
                details=str(e),
                path="/chat/send"
            )

    async def _persist_assistant_message(self, request: ConversationRequest, message: dict):
        try:
            self.mongo_repo.append_message(
                conversation_id=request.conversation_id,
                user_id=request.user_id,
                message=message
            )
        except Exception as e:
            logger.error(f"Failed to persist assistant message: {e}")
            raise SentraHTTPException(
                status_code=500,
                code="ASSISTANT_MESSAGE_STORE_FAILED",
                message="Failed to store assistant response.",
                details=str(e),
                path="/chat/send"
            )

    async def _persist_step_event(self, request: ConversationRequest, event: ConversationEvent):
        try:
            system_message = {
                "id": event.event_id,
                "role": "system",
                "content": event.content,
                "timestamp": event.timestamp,
                "type": event.type,
                "event_type": event.type,
                "task_type": event.task_type,
                "task_run_id": event.task_run_id,
                "step_id": event.step_id,
                "label": event.label,
                "status": event.status,
                "meta": json_safe(event.meta) if event.meta is not None else None,
            }
            self.mongo_repo.append_message(
                conversation_id=request.conversation_id,
                user_id=request.user_id,
                message=system_message
            )
        except Exception as e:
            logger.error(f"Failed to persist step event: {e}")

    def _on_cache_evict(self, user_id: str, conversation_id: str, messages: list[dict]):
        logger.info(f"[Cache] Evicted: user_id={user_id}, conversation_id={conversation_id}, messages={len(messages)}")
        logger.debug(f"[Cache] Last messages before eviction: {messages[-3:]}")
