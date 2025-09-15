# services/sentra-api/sentra_brain_api/features/chat/controller.py
import json
from fastapi import APIRouter, Depends, Request, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.encoders import jsonable_encoder
from fastuuid import uuid4

from sentra_brain_api.adapters.persistence_adapter import MongoPersistenceAdapter
from sentra_brain_api.crosscutting.authorization import get_authenticated_user
 
from sentra_brain_api.features.chat.schemas import ChatSendRequest
from sentra.domain.entities.user_entity import UserEntity
from google.adk.events.event import Event
from google.genai import types
from sentra.infra.nosql.mongo_session_repository import MongoSessionRepository, get_session_mongo_repository
from sentra.runtime.app import run_conversation
from sentra.runtime.models import ConversationRequest as EngineRequest
from sentra_brain_api.adapters.session_service import get_session_service, APP_NAME
from sentra.runtime.memory import add_session_to_memory
from sentra.shared.logging import get_logger

logger = get_logger("sentra_brain_api.features.chat")

class ChatController:
    def __init__(self):
        self.router = APIRouter()
        self._add_routes()

    def _add_routes(self):
        @self.router.post(
            "/send",
            response_class=StreamingResponse,
            description="Sends a message using the ADK engine and streams the assistant response",
        )
        async def send_message(
            body: ChatSendRequest,
            request: Request,
            mongo_repo: MongoSessionRepository = Depends(get_session_mongo_repository),
            current_user: UserEntity = Depends(get_authenticated_user),
        ):
            adapter = MongoPersistenceAdapter(repo=mongo_repo, user_id=str(current_user.id))
            session_service = get_session_service()

            # --- Session lifecycle ---
            if body.session_id:
                conversation_id = str(body.session_id)
                try:
                    # Attempt to retrieve existing ADK session (will raise or return None if not found depending on impl)
                    adk_session = await session_service.get_session(app_name=APP_NAME, user_id=str(current_user.id), session_id=conversation_id)  # type: ignore[attr-defined]
                    if adk_session is None:
                        raise HTTPException(status_code=404, detail="Session not found")
                except Exception:
                    raise HTTPException(status_code=404, detail="Session not found")
            else:
                adk_session = await session_service.create_session(app_name=APP_NAME, user_id=str(current_user.id))  # type: ignore[attr-defined]
                conversation_id = adk_session.id  # type: ignore[attr-defined]

            # Persist raw user message to Mongo (legacy persistence path) for continuity
            await adapter.persist_user_message(
                conversation_id,
                text=body.content,
                event_id=body.event_id or uuid4(),
            )

            # Build engine request (still using recent context until full ADK runner integration replaces this)
            recent = await adapter.get_recent_context(conversation_id, limit=50)
            session_state = await adapter.get_session_state(conversation_id)
            engine_request = EngineRequest(
                messages=[*recent, body.content],
                user_id=str(current_user.id),
                conversation_id=conversation_id,
                context_source_ids=[str(cid) for cid in body.context_source_ids] if body.context_source_ids else None,
                context_document_ids=[str(cid) for cid in body.context_document_ids] if body.context_document_ids else None,
                session_state=session_state,
                agent=body.agent,
            )

            # Append the user event to ADK session explicitly (Runner currently not used directly here)
            try:
                user_event = Event(
                    author="user",
                    content=types.Content(role="user", parts=[types.Part(text=body.content)]),
                    custom_metadata={"type": "message_final", "source": "api"},
                )
                await session_service.append_event(adk_session, user_event)  # type: ignore[arg-type, attr-defined]
            except Exception:
                logger.warning("Failed to append user event to ADK session", exc_info=True)

            async def stream():
                # Emit a synthetic first envelope containing session_id for clients on first chunk
                first_payload_emitted = False
                try:
                    async for ev in run_conversation(engine_request):
                        await adapter.append_event(conversation_id, ev)                        
                        # Safe conversion to JSON-compatible types
                        try:
                            payload = jsonable_encoder(ev, by_alias=True, exclude_none=True)
                        except Exception:
                            payload = ev.model_dump(exclude_none=True)

                        # Inject session_id on first event if not already present
                        if not first_payload_emitted:
                            payload = {"session_id": conversation_id, **payload}
                            first_payload_emitted = True

                        try:
                            json_text = json.dumps(payload, ensure_ascii=False)
                        except Exception:
                            json_text = json.dumps(payload, default=str, ensure_ascii=False)

                        # If this is the final assistant message, append to ADK session & index memory
                        try:
                            meta_type = payload.get("custom_metadata", {}).get("type") if isinstance(payload, dict) else None
                            if meta_type == "message_final":
                                # Append assistant final event to ADK session to ensure full session context
                                try:
                                    await session_service.append_event(adk_session, ev)  # type: ignore[arg-type, attr-defined]
                                except Exception:
                                    logger.warning("Failed to append assistant final event to ADK session", exc_info=True)
                                # Attempt memory indexing (idempotent inside helper)
                                try:
                                    await add_session_to_memory(adk_session)  # type: ignore[arg-type]
                                except Exception:
                                    logger.warning("Failed to add session to memory service", exc_info=True)
                        except Exception:
                            logger.debug("Final message memory hook failed", exc_info=True)

                        yield f"data: {json_text}\n\n"
                except Exception as e:
                    logger.exception("Streaming failed")
                    err_evt = Event(author="system", content=types.Content(role="system", parts=[types.Part(text=str(e))]), custom_metadata={"type": "error", "status": "error", "path": "/chat/send"})
                    await adapter.append_event(conversation_id, err_evt)
                    # signal that the step ended after the error
                    end_evt = Event(author="system", content=types.Content(role="system", parts=[types.Part(text="step ended due to error")]), custom_metadata={"type": "step_end"})
                    await adapter.append_event(conversation_id, end_evt)

                    # yield error and then the step-end signal
                    try:
                        err_payload = jsonable_encoder(err_evt, by_alias=True, exclude_none=True)
                    except Exception:
                        err_payload = err_evt.model_dump(exclude_none=True)

                    try:
                        end_payload = jsonable_encoder(end_evt, by_alias=True, exclude_none=True)
                    except Exception:
                        end_payload = end_evt.model_dump(exclude_none=True)

                    # Include session_id for error envelopes as well
                    for p in (err_payload, end_payload):
                        if "session_id" not in p:
                            p["session_id"] = conversation_id
                        yield f"data: {json.dumps(p, ensure_ascii=False)}\n\n"

            return StreamingResponse(
                stream(),
                media_type="text/event-stream; charset=utf-8",
                headers={
                    "Cache-Control": "no-cache, no-transform",
                    "X-Accel-Buffering": "no",
                    "Connection": "keep-alive",
                },
            )