# sentra_brain_api/features/chat/controller_v2.py
from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse
from sentra_brain_api.crosscutting.authorization import get_authenticated_user
from sentra_core.core.logging import get_logger
from sentra_core.domain.entities.user_entity import UserEntity
from sentra_core.infra.nosql.mongo_conversation_repository import (
    MongoConversationRepository,
    get_conversation_mongo_repository,
)
from sentra_brain_api.adapters.persistence_adapter import MongoPersistenceAdapter
from sentra_core.core.settings import settings, LLMEngine

from sentra_engine.adapters import LlamaServerAdapter, VLLMAdapter, LLMPlannerAdapter, MCPProtocolAdapter
from sentra_engine.adapters.context_service import SimpleContextService
from sentra_engine.core.tool_orchestrator import ToolOrchestrator
from sentra_engine.engine import ConversationEngine

from sentra_brain_api.features.chat.schemas import (
    ConversationRequest, ConversationMode, ConversationEvent
)
from sentra_brain_api.features.chat.mappers import engine_event_to_wire

logger = get_logger("sentra_brain_api.chat.v2")

class ChatControllerV2:
    def __init__(self):
        self.router = APIRouter()
        self._add_routes()

    def _build_llm_adapter(self, model: str):
        if settings.llm_engine == LLMEngine.LLAMA:
            return LlamaServerAdapter(
                base_url=settings.llama_server_url,
                model=model,
                request_timeout=settings.llm_request_timeout,
            )
        elif settings.llm_engine == LLMEngine.VLLM:
            return VLLMAdapter(
                base_url=settings.vllm_server_url,
                model=model,
                request_timeout=settings.llm_request_timeout,
            )
        # default
        logger.warning(f"Unknown LLM engine '{settings.llm_engine}', defaulting to LLAMA")
        return LlamaServerAdapter(
            base_url=settings.llama_server_url,
            model=model,
            request_timeout=settings.llm_request_timeout,
        )

    def _build_planner_adapter(self, model: str):
        if settings.llm_engine == LLMEngine.LLAMA:
            return LLMPlannerAdapter(base_url=settings.llama_server_url, model=model, request_timeout=settings.llm_request_timeout)
        elif settings.llm_engine == LLMEngine.VLLM:
            return LLMPlannerAdapter(base_url=settings.vllm_server_url, model=model, request_timeout=settings.llm_request_timeout)
        return LLMPlannerAdapter(base_url=settings.llama_server_url, model=model, request_timeout=settings.llm_request_timeout)

    def _build_tool_orchestrator(self, persistence: MongoPersistenceAdapter) -> ToolOrchestrator | None:
        if not settings.tools_enabled:
            return None
        mcp = MCPProtocolAdapter(settings.mcp_base_url)
        return ToolOrchestrator(mcp=mcp, persistence=persistence, telemetry=None, enabled=True)

    def _add_routes(self):
        @self.router.post(
            "/send",
            response_class=StreamingResponse,
            description="Sends a message using the selected engine mode and streams the assistant response",
        )
        async def send_message_v2(
            body: ConversationRequest,
            request: Request,
            mongo_repo: MongoConversationRepository = Depends(get_conversation_mongo_repository),
            current_user: UserEntity = Depends(get_authenticated_user),
        ):
            body.user_id = current_user.id

            persistence = MongoPersistenceAdapter(repo=mongo_repo, user_id=str(current_user.id))
            context = SimpleContextService(persistence=persistence)
            llm = self._build_llm_adapter(model=body.model or "sentra-brain")

            tool_orch = self._build_tool_orchestrator(persistence)

            if body.mode == ConversationMode.PLAN:
                planner = self._build_planner_adapter(model=body.model or "sentra-brain")
                engine = ConversationEngine(
                    context=context, llm=llm, persistence=persistence,
                    planner=planner, tool_orchestrator=tool_orch
                )
                runner = engine.run_planner
            else:
                # FAST mode with autonomous tool-use support
                engine = ConversationEngine(
                    context=context, llm=llm, persistence=persistence,
                    planner=None, tool_orchestrator=tool_orch
                )
                runner = engine.run_fast

            async def stream(): 
                try:  
                    async for ev in runner(
                        user_id=str(current_user.id),
                        conversation_id=str(body.conversation_id),
                        message_id=str(body.message_id) if body.message_id else None,
                        response_message_id=str(body.response_message_id) if body.response_message_id else None,
                        content=body.content,
                    ):
                        out = engine_event_to_wire(ev)
                        yield f"data: {out.model_dump_json()}\n\n"
                except Exception as e:
                    logger.exception("Streaming failed")
                    err_evt = ConversationEvent(
                        type="step_error",
                        task_type="chat_pipeline",
                        label="Streaming failed",
                        status="error",
                        content=str(e),
                        meta={"path": "/chat/send"},
                    )
                    yield f"data: {err_evt.model_dump_json()}\n\n"

            return StreamingResponse(
                stream(),
                media_type="text/event-stream; charset=utf-8",
                headers={
                    "Cache-Control": "no-cache, no-transform",
                    "X-Accel-Buffering": "no",
                    "Connection": "keep-alive",
                },
            )
