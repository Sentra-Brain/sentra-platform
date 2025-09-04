# sentra_brain_api/features/chat/controller_legacy.py
from fastapi import APIRouter, Depends, Request, Query
from fastapi.responses import StreamingResponse
from sentra_brain_api.crosscutting.authorization import get_authenticated_user
from sentra_core.logging import get_logger
from sentra_core.domain.entities.user_entity import UserEntity
from sentra_core.infra.nosql.mongo_session_repository import (
    MongoSessionRepository,
    get_session_mongo_repository,
)
from sentra_brain_api.adapters.persistence_adapter import MongoPersistenceAdapter
from sentra_core.settings import settings, LLMEngine, EngineMode
from sentra_engine.planner.adapters.llm_planner import LLMPlannerAdapter
from sentra_engine.mcp.adapters.fastmcp import get_mcp
from sentra_engine.context.adapters.simple_context import SimpleContextService
from sentra_engine.tools.adapters.orchestrator import ToolOrchestrator
from sentra_engine.conversation.entrypoint.conversation_engine import ConversationEngine
from sentra_engine.llm.adapters.factory import LlmAdapterFactory
from sentra_brain_api.features.chat.schemas import (
    SessionRequest,
    SessionMode,
    SessionEvent,
)
from sentra_brain_api.features.chat.mappers import engine_event_to_wire
from datetime import datetime, timezone
from uuid import uuid4

logger = get_logger("sentra_brain_api.chat.v2")


class ChatControllerLegacy:
    def __init__(self):
        self.router = APIRouter()
        self._add_routes()
        self._mcp = get_mcp()

    def _build_planner_adapter(self, model: str):
        if settings.llm_engine == LLMEngine.LLAMA:
            return LLMPlannerAdapter(
                base_url=settings.llama_server_url,
                model=model,
                request_timeout=settings.llm_request_timeout,
            )
        elif settings.llm_engine == LLMEngine.VLLM:
            return LLMPlannerAdapter(
                base_url=settings.vllm_server_url,
                model=model,
                request_timeout=settings.llm_request_timeout,
            )
        return LLMPlannerAdapter(
            base_url=settings.llama_server_url,
            model=model,
            request_timeout=settings.llm_request_timeout,
        )

    def _build_tool_orchestrator(
        self, persistence: MongoPersistenceAdapter
    ) -> ToolOrchestrator | None:
        if not settings.tools_enabled:
            return None
        return ToolOrchestrator(
            mcp=self._mcp, persistence=persistence, telemetry=None, enabled=True
        )

    def _add_routes(self):
        @self.router.post(
            "/send",
            response_class=StreamingResponse,
            description="Sends a message using the legacy engine and streams the assistant response",
        )
        async def send_message_v2(
            body: SessionRequest,
            request: Request,
            mongo_repo: MongoSessionRepository = Depends(get_session_mongo_repository),
            current_user: UserEntity = Depends(get_authenticated_user),
            engine_mode: EngineMode | None = Query(None),
        ):
            body.user_id = current_user.id
            persistence = MongoPersistenceAdapter(
                repo=mongo_repo, user_id=str(current_user.id)
            )
            context = SimpleContextService(persistence=persistence)
            llm = LlmAdapterFactory.create_adapter(model=body.model or "sentra-brain")
            tool_orch = self._build_tool_orchestrator(persistence)

            if body.mode == SessionMode.PLAN:
                planner = self._build_planner_adapter(model=body.model or "sentra-brain")
                engine = ConversationEngine(
                    context=context,
                    llm=llm,
                    persistence=persistence,
                    planner=planner,
                    tool_orchestrator=tool_orch,
                )
                runner = engine.run_planner
            else:
                engine = ConversationEngine(
                    context=context,
                    llm=llm,
                    persistence=persistence,
                    planner=None,
                    tool_orchestrator=tool_orch,
                )
                runner = engine.run_fast

            async def stream():
                try:
                    async for ev in runner(
                        user_id=str(current_user.id),
                        conversation_id=str(body.session_id),
                        message_id=str(body.message_id) if body.message_id else None,
                        response_message_id=str(body.response_message_id)
                        if body.response_message_id
                        else None,
                        content=body.content,
                    ):
                        out = engine_event_to_wire(ev)
                        yield f"data: {out.model_dump_json()}\n\n"
                except Exception as e:
                    logger.exception("Streaming failed")
                    err_evt = SessionEvent(
                        event_id=uuid4().hex,
                        timestamp=datetime.now(timezone.utc).isoformat(),
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
