# # sentra_brain_api/features/chat/controller.py
# from fastapi import APIRouter, Depends, Request
# from fastapi.responses import StreamingResponse
# from sentra_brain_api.crosscutting.authorization import get_authenticated_user
# from sentra_core.core.logging import get_logger
# from sentra_core.domain.entities.user_entity import UserEntity
# import json

# logger = get_logger("sentra_brain_api")


# class ChatController:
#     def __init__(self):
#         self.router = APIRouter()
#         self._add_routes()

#     def _add_routes(self):
#         @self.router.post(
#             "/send_old",
#             response_class=StreamingResponse,
#             description="Sends a message to the assistant and streams the response"
#         )
#         async def send_message(
#             body: ConversationRequest,
#             request: Request,
#             current_user: UserEntity = Depends(get_authenticated_user)
#         ):
#             body.user_id = current_user.id
            
#             app_state: AppState = request.app.state._sentra
#             engine = app_state.conversation_engine

#             async def stream():
#                 try:
#                     async for event in engine.run(body):
#                         yield f"data: {event.model_dump_json()}\n\n"
#                 except Exception as e:
#                     logger.error(f"Error occurred while streaming response: {e}")
#                     err_evt = ConversationEvent(
#                         type="step_error",
#                         task_type="chat_pipeline",
#                         label="Streaming failed",
#                         status="error",
#                         content=str(e),
#                         meta={"path": "/chat/send"}
#                     )
#                     yield f"data: {err_evt.model_dump_json()}\n\n"

#             return StreamingResponse(
#                 stream(),
#                 media_type="text/event-stream; charset=utf-8",
#                 headers={
#                     "Cache-Control": "no-cache, no-transform",
#                     "X-Accel-Buffering": "no",      # Nginx
#                     "Connection": "keep-alive",
#                 },
#             )

