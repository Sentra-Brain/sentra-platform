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
from sentra_brain_api.core.conversation_engine.models.input_model import ConversationRequest, ConversationMode
from sentra_brain_api.core.conversation_engine.models.output_model import ConversationEvent
from sentra_core.core.settings import settings, LLMEngine
from sentra_engine.adapters import LlamaServerAdapter, VLLMAdapter, LLMPlannerAdapter
from sentra_engine.adapters.context_service import SimpleContextService
from sentra_engine.engine import ConversationEngine


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
                request_timeout=None,
            )
        elif settings.llm_engine == LLMEngine.VLLM:
            return VLLMAdapter(
                base_url=settings.vllm_server_url,
                model=model,
                request_timeout=None,
            )
        else:
            # Default to LLAMA if engine not recognized
            logger.warning(f"Unknown LLM engine '{settings.llm_engine}', defaulting to LLAMA")
            return LlamaServerAdapter(
                base_url=settings.llama_server_url,
                model=model,
                request_timeout=None,
            )

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
            # Ensure user_id in body for consistency with existing model usage
            body.user_id = current_user.id

            # Wire per-request adapters
            persistence = MongoPersistenceAdapter(repo=mongo_repo, user_id=str(current_user.id))
            context = SimpleContextService(persistence=persistence)
            llm = self._build_llm_adapter(model=body.model or "sentra-brain")

            # Choose engine path from body.mode
            if body.mode == ConversationMode.FAST:
                engine = ConversationEngine(context=context, llm=llm, persistence=persistence)
                runner = engine.run_fast
            elif body.mode == ConversationMode.PLAN:
                planner = self._build_planner_adapter(model=body.model or "sentra-brain")
                engine = ConversationEngine(context=context, llm=llm, persistence=persistence, planner=planner)
                runner = engine.run_planner
            else:
                # Fallback: default to FAST
                engine = ConversationEngine(context=context, llm=llm, persistence=persistence)
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
                        if ev.type == "message_delta":
                            out = ConversationEvent(type="message_delta", content=ev.content)
                        else:
                            out = ConversationEvent(type="message_final", content="")
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

    def _build_planner_adapter(self, model: str):
        if settings.llm_engine == LLMEngine.LLAMA:
            return LLMPlannerAdapter(base_url=settings.llama_server_url, model=model)
        elif settings.llm_engine == LLMEngine.VLLM:
            return LLMPlannerAdapter(base_url=settings.vllm_server_url, model=model)
        # default
        return LLMPlannerAdapter(base_url=settings.llama_server_url, model=model)