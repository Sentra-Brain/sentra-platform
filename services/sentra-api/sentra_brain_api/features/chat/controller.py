# services/sentra-api/sentra_brain_api/features/chat/controller.py
from fastapi import APIRouter, Depends, Request, HTTPException
from fastapi import Depends
from fastapi.encoders import jsonable_encoder
from fastapi.responses import StreamingResponse
from google.adk.events.event import Event 
from google.adk.sessions import DatabaseSessionService
from google.genai import types
from sentra_brain_api.crosscutting.authorization import get_authenticated_user
from sentra_brain_api.features.chat.schemas import ChatSendRequest
from sentra.domain.entities.user_entity import UserEntity
from sentra.runtime.adapters.adk_session_service import get_adk_session_service, APP_NAME
from sentra.runtime.app import run_conversation
from sentra.runtime.memory import add_session_to_memory
from sentra.runtime.models import ConversationRequest
from sentra.shared.logging import get_logger
import json

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
            session_service: DatabaseSessionService = Depends(get_adk_session_service),
            current_user: UserEntity = Depends(get_authenticated_user),
        ):
            # --- Session lifecycle ---
            if body.session_id:
                conversation_id = str(body.session_id)
                try:
                    adk_session = await session_service.get_session(app_name=APP_NAME, user_id=str(current_user.id), session_id=conversation_id)
                    if adk_session is None:
                        raise HTTPException(status_code=404, detail="Session not found")
                except Exception:
                    raise HTTPException(status_code=404, detail="Session not found")
            else:
                adk_session = await session_service.create_session(app_name=APP_NAME, user_id=str(current_user.id))
                conversation_id = adk_session.id

            # --- Conversation request ---
            # Build conversation request (context retrieval and state management should use ADK)
            conversation_request = ConversationRequest(
                messages=[body.content],
                user_id=str(current_user.id),
                conversation_id=conversation_id,
                context_source_ids=[str(cid) for cid in body.context_source_ids] if body.context_source_ids else None,
                context_document_ids=[str(cid) for cid in body.context_document_ids] if body.context_document_ids else None,
                session_state=None,
                agent=body.agent,
            )

            try:
                user_event = Event(
                    author="user",
                    content=types.Content(role="user", parts=[types.Part(text=body.content)]),
                    custom_metadata={"type": "message_final", "source": "api"},
                )
                await session_service.append_event(adk_session, user_event)
            except Exception:
                logger.warning("Failed to append user event to ADK session", exc_info=True)

            async def stream():
                first_payload_emitted = False
                try:
                    async for ev in run_conversation(conversation_request):                     
                        try:
                            payload = jsonable_encoder(ev, by_alias=True, exclude_none=True)
                        except Exception:
                            payload = ev.model_dump(exclude_none=True)

                        if not first_payload_emitted:
                            payload = {"session_id": conversation_id, **payload}
                            first_payload_emitted = True

                        try:
                            json_text = json.dumps(payload, ensure_ascii=False)
                        except Exception:
                            json_text = json.dumps(payload, default=str, ensure_ascii=False)

                        try:
                            meta_type = payload.get("custom_metadata", {}).get("type") if isinstance(payload, dict) else None
                            if meta_type == "message_final":
                                try:
                                    await session_service.append_event(adk_session, ev)
                                except Exception:
                                    logger.warning("Failed to append assistant final event to ADK session", exc_info=True)
                                try:
                                    await add_session_to_memory(adk_session)
                                except Exception:
                                    logger.warning("Failed to add session to memory service", exc_info=True)
                        except Exception:
                            logger.debug("Final message memory hook failed", exc_info=True)

                        yield f"data: {json_text}\n\n"
                except Exception as e:
                    logger.exception("Streaming failed")
                    err_payload = {"session_id": conversation_id, "error": str(e)}
                    yield f"data: {json.dumps(err_payload, ensure_ascii=False)}\n\n"

            return StreamingResponse(
                stream(),
                media_type="text/event-stream; charset=utf-8",
                headers={
                    "Cache-Control": "no-cache, no-transform",
                    "X-Accel-Buffering": "no",
                    "Connection": "keep-alive",
                },
            )