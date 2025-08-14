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
        Single-turn execution with optional RAG + LLM tools (MCP).
        Streams assistant tokens, detects real tool calls, and also recovers when
        the model prints a tool-call JSON in content (schema echo with "parameters").
        """
        logger.info(f"[Engine] Starting run: user={request.user_id}, conversation={request.conversation_id}")
        now = datetime.now(timezone.utc).isoformat()

        # ------- 1) Optional RAG step (events) -------
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

        # ------- 2) Context + persist user message -------
        context = await self._load_context(request.user_id, request.conversation_id)
        user_msg = self._make_message("user", request.content, now, message_id=request.message_id)
        await self._persist_user_message(request, user_msg)

        # ------- 3) Tools (MCP -> OpenAI schema) -------
        try:
            mcp_tools = await self._ensure_mcp_tools()
        except RuntimeError:
            # open a session lazily if needed
            try:
                async with self.mcp_client:
                    mcp_tools = await self._ensure_mcp_tools()
            except Exception as e:
                logger.warning(f"[MCP] list_tools failed after open: {e}")
                mcp_tools = []
        except Exception as e:
            logger.warning(f"[MCP] list_tools failed: {e}")
            mcp_tools = []

        openai_tools = mcp_tools_to_openai_tools(mcp_tools)
        tool_names = {t["function"]["name"] for t in openai_tools}
        logger.info(f"[Engine] MCP tools available: {sorted(tool_names)}")

        # ------- helpers (local) -------
        def _looks_like_tool_schema_chunk(chunk: str) -> bool:
            """Detect chunks that look like schema/printed tool-call JSON so we don't stream them."""
            if not chunk:
                return False
            s = chunk.strip()
            if not s:
                return False
            # common tell-tales from llama-server jinja template mode
            # - top-level {"type":"function", "function":{...}}
            # - {"name":"...", "parameters":{...}}
            # - large 'properties/required' schema blocks
            keys = ('"type":"function"', '"parameters"', '"function":{', '"properties"', '"required"')
            if s.startswith("{") and '"name"' in s and '"parameters"' in s:
                return True
            return any(k in s for k in keys)

        def _extract_json_objects(s: str):
            """Yield JSON objects found in a string by bracket matching."""
            objs = []
            stack = 0
            start = None
            for i, ch in enumerate(s):
                if ch == '{':
                    if stack == 0:
                        start = i
                    stack += 1
                elif ch == '}':
                    if stack > 0:
                        stack -= 1
                        if stack == 0 and start is not None:
                            candidate = s[start:i+1]
                            objs.append(candidate)
                            start = None
            return objs

        def _salvage_tool_call_from_text(text: str):
            """
            Try to parse a tool call that the model printed as content.
            Accepts shapes:
            A) {"name":"web.search","parameters":{...}}
            B) {"type":"function","function":{"name":"...","parameters":{...}}}
            C) {"type":"function","function":{"name":"...","arguments":{...}}}
            Returns (name:str, args:dict) or None.
            """
            if not text:
                return None
            for cand in reversed(_extract_json_objects(text)):
                try:
                    obj = json.loads(cand)
                except Exception:
                    continue

                # shape A
                if isinstance(obj, dict) and "name" in obj and isinstance(obj.get("parameters"), dict):
                    name = obj["name"]
                    if name in tool_names:
                        return name, obj["parameters"]

                # shape B / C
                if isinstance(obj, dict) and obj.get("type") == "function" and isinstance(obj.get("function"), dict):
                    fn = obj["function"]
                    name = fn.get("name")
                    if name in tool_names:
                        params = fn.get("parameters")
                        args = fn.get("arguments")
                        if isinstance(params, dict):
                            return name, params
                        if isinstance(args, str):
                            try:
                                args = json.loads(args)
                            except Exception:
                                args = {"_raw": args}
                        if isinstance(args, dict):
                            return name, args

            return None

        # ------- 4) Tool-use loop -------
        conversation_messages = context[-CONTEXT_WINDOW_SIZE:] + [user_msg]
        assistant_text_buffer = ""
        suppressed_tool_json_buffer = ""
        rounds = 0

        while True:
            payload = self.prompt_factory.build_payload(
                context=context,
                new_message=user_msg,
                rag_chunks=rag_chunks,
                tool_context=None,
                tools=openai_tools
            )
            payload["messages"] = conversation_messages
            payload["model"] = request.model or "sentra-brain"

            pending_tool = {"id": None, "name": None, "args": ""}

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

                    # content chunk
                    if delta.get("content"):
                        chunk = delta["content"]
                        if _looks_like_tool_schema_chunk(chunk):
                            suppressed_tool_json_buffer += chunk
                            # do NOT stream this to the user
                        else:
                            assistant_text_buffer += chunk
                            yield ConversationEvent(type="message_delta", content=chunk)

                    # OpenAI-style tool call (or legacy)
                    tc = self._tool_call_from_delta(delta)
                    if tc and tc.get("name"):
                        if tc.get("id"):
                            pending_tool["id"] = tc["id"]
                        pending_tool["name"] = tc["name"]
                        pending_tool["args"] += tc.get("arguments_chunk") or ""

                    # End-of-turn?
                    if delta.get("finish_reason") in ("stop", "length", "tool_calls", "tool_call"):
                        if pending_tool["name"]:
                            break
                except Exception as e:
                    logger.error(f"Stream parse error: {e}")

            # If stream ended without a formal tool call, try to salvage from printed JSON
            if not pending_tool["name"]:
                salvaged = _salvage_tool_call_from_text(suppressed_tool_json_buffer)
                if not salvaged:
                    salvaged = _salvage_tool_call_from_text(assistant_text_buffer)  # last resort
                    if salvaged:
                        # remove the printed JSON from what the user sees
                        assistant_text_buffer = ""
                if salvaged:
                    pending_tool["name"], args_obj = salvaged
                    pending_tool["args"] = json.dumps(args_obj, ensure_ascii=False)

            # Execute tool if requested / salvaged
            if pending_tool["name"]:
                if rounds >= MAX_TOOL_ROUNDS:
                    logger.warning("Max tool rounds reached; skipping further tool calls.")
                    break

                rounds += 1

                # Parse args
                try:
                    args = json.loads(pending_tool["args"] or "{}")
                except json.JSONDecodeError:
                    args = {"_raw": pending_tool["args"]}

                # Seal any assistant text produced so far into transcript (not the suppressed JSON)
                if assistant_text_buffer:
                    conversation_messages.append({"role": "assistant", "content": assistant_text_buffer})
                    assistant_text_buffer = ""
                suppressed_tool_json_buffer = ""

                # Record tool call (OpenAI-style)
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

                # Step events around MCP execution
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

                # Execute MCP tool
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

                # Optional audit system message
                try:
                    self.mongo_repo.append_message(
                        conversation_id=request.conversation_id,
                        user_id=request.user_id,
                        message={
                            "id": uuid4().hex,
                            "role": "system",
                            "content": f"[tool_call] {pending_tool['name']} args={json_safe(args)}",
                            "timestamp": datetime.now(timezone.utc).isoformat(),
                            "type": "tool_call",
                            "tool_name": pending_tool["name"],
                            "tool_args": json_safe(args),
                        }
                    )
                except Exception:
                    pass

                # Feed tool result back
                conversation_messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call_id,
                    "content": tool_output
                })

                # Next LLM round
                pending_tool = {"id": None, "name": None, "args": ""}
                continue  # restart while-loop with updated transcript

            # No tool to execute -> end tool loop
            break

        # ------- 5) Finalize, persist, cache, complete -------
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
