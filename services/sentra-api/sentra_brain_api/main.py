# main.py
from fastapi import FastAPI
from fastapi.concurrency import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from sentra_brain_api.core.constants import CONTACT
from sentra_brain_api.core.constants import DESCRIPTION
from sentra_brain_api.core.constants import LICENSE_INFO
from sentra_brain_api.core.constants import SWAGGER_FAVICON_URL, SWAGGER_UI_PARAMETERS, TITLE
from sentra_brain_api.crosscutting import logging
from sentra_brain_api.features.admin.controller import AdminController
from sentra_brain_api.features.admin.settings.controller import SettingsController
from sentra_brain_api.features.auth.controller import AuthController
from sentra_brain_api.features.conversation.controller import ConversationController
from sentra_brain_api.features.public.controller import PublicSettingsController
from sentra_brain_api.features.user.controller import UserController
from sentra_brain_api.infra import postgres_service
import os

from sentra_brain_api.middleware.error_handler import ErrorHandlerMiddleware

logger = logging.get_logger("sentra_brain_api")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("App startup: initializing resources...")
    postgres_service.init_db()
    yield

def create_app(
        mediator=None,
        auth_service=None,
        notification_service=None):
    app = FastAPI(
        title=TITLE,
        description=DESCRIPTION,
        version="0.1",
        contact=CONTACT,
        license_info=LICENSE_INFO,
        swagger_ui_parameters=SWAGGER_UI_PARAMETERS,
        swagger_favicon_url=SWAGGER_FAVICON_URL,
        lifespan=lifespan
    )

    app.add_middleware(ErrorHandlerMiddleware)

    app.add_middleware(
        CORSMiddleware,
        allow_origin_regex=r"https?://(127\.0\.0\.1|localhost)(:\d{1,5})?",
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"]
    )

    auth_controller = AuthController()
    user_controller = UserController()
    admin_controller = AdminController()
    settings_controller = SettingsController()
    public_settings_controller = PublicSettingsController()
    conversation_controller = ConversationController()

    app.include_router(auth_controller.router, prefix="/auth", tags=["auth"])
    app.include_router(user_controller.router, prefix="/users", tags=["users"])
    app.include_router(admin_controller.router, prefix="/admin", tags=["admin"])
    app.include_router(settings_controller.router, prefix="/admin", tags=["admin"])
    app.include_router(public_settings_controller.router, prefix="/public", tags=["public"])
    app.include_router(conversation_controller.router, prefix="/conversations", tags=["conversations"])

    return app

app = create_app()

@app.get("/", include_in_schema=False, response_class=RedirectResponse)
async def redirect_to_swagger():
    logger.info("Redirect to swagger...")
    return RedirectResponse(url="/docs")


if __name__ == "__main__":
    import uvicorn
    debug_mode = os.getenv("DEBUG_MODE", "false").lower() == "true"
    logging.configure_logging(debug=debug_mode)

    if debug_mode:
        logger.info("✅ Debug mode enabled: waiting for debugger on port 5678")
        import debugpy
        debugpy.listen(("0.0.0.0", 5678))
        debugpy.wait_for_client()

    uvicorn.run(app, host="0.0.0.0", port=8100, log_level="debug" if debug_mode else "info")
