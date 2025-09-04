# main.py

# from sentra_brain_api.core.observability import instrument_app, add_correlation_id_middleware
from fastapi import FastAPI
from fastapi.concurrency import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from sentra_brain_api.core.constants import CONTACT
from sentra_brain_api.core.constants import DESCRIPTION
from sentra_brain_api.core.constants import LICENSE_INFO
from sentra_brain_api.core.constants import SWAGGER_FAVICON_URL, SWAGGER_UI_PARAMETERS, TITLE, VERSION
from sentra_brain_api.core.lifecycle_config import AppLifecycleConfig
from sentra_brain_api.features.admin.controller import AdminController
from sentra_brain_api.features.admin.settings.controller import SettingsController as AdminSettingsController
from sentra_brain_api.features.auth.controller import AuthController
from sentra_brain_api.features.session.controller import SessionController
from sentra_brain_api.features.knowledge.routes import sources, documents
from sentra_brain_api.features.llm_proxy.controller import LLMProxyController
from sentra_brain_api.features.organization.controller import router as organization_router
from sentra_brain_api.features.public.controller import PublicSettingsController
from sentra_brain_api.features.settings.controller import SettingsController
from sentra_brain_api.features.user.controller import UserController
from sentra_brain_api.middleware.error_handler import ErrorHandlerMiddleware
from sentra_core import logging
from sentra_core.infra.sql import postgres_service
from sentra_core.settings import settings
import os


logger = logging.get_logger("sentra_brain_api")

def get_lifespan(config: AppLifecycleConfig):
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        logger.info("App startup: initializing resources...")

        if config.init_mcp:
            from sentra_engine.mcp.adapters.fastmcp import get_mcp
            mcp_client = get_mcp()
            await mcp_client.startup()
            app.state.mcp_client = mcp_client

        if config.init_db:
            postgres_service.init_db()

        yield

        if config.init_mcp:
            await app.state.mcp_client.shutdown()

    return lifespan


def create_app(config: AppLifecycleConfig = AppLifecycleConfig()):
    app = FastAPI(
        title=TITLE,
        description=DESCRIPTION,
        version=VERSION,
        contact=CONTACT,
        license_info=LICENSE_INFO,
        swagger_ui_parameters=SWAGGER_UI_PARAMETERS,
        swagger_favicon_url=SWAGGER_FAVICON_URL,
        lifespan=get_lifespan(config)
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
    admin_settings_controller = AdminSettingsController()
    settings_controller = SettingsController()
    public_settings_controller = PublicSettingsController()
    session_controller = SessionController()
    llm_proxy_controller = LLMProxyController()

    app.include_router(auth_controller.router, prefix="/auth", tags=["auth"])
    app.include_router(user_controller.router, prefix="/users", tags=["users"])
    app.include_router(admin_controller.router, prefix="/admin", tags=["admin"])
    app.include_router(admin_settings_controller.router, prefix="/admin", tags=["admin"])
    app.include_router(settings_controller.router, prefix="", tags=["settings"])
    app.include_router(public_settings_controller.router, prefix="/public", tags=["public"])
    app.include_router(session_controller.router, prefix="/sessions", tags=["sessions"])
    app.include_router(sources.router, prefix="/knowledge/sources", tags=["knowledge"])
    app.include_router(documents.router, prefix="/knowledge", tags=["knowledge"])
    app.include_router(llm_proxy_controller.router, prefix="/v1", tags=["llm-proxy"])
    app.include_router(organization_router, prefix="", tags=["organization"])

    # Setup observability (only if not in test mode)
    # if os.getenv("TESTING") != "true":
        # instrument_app(app)
        # add_correlation_id_middleware(app)

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
    logger = logging.get_logger("sentra_brain_api")

    if debug_mode:
        logger.info("✅ Debug mode enabled: waiting for debugger on port 5678")
        import debugpy
        debugpy.listen(("0.0.0.0", 5678))
        debugpy.wait_for_client()

    uvicorn.run(app, host="0.0.0.0", port=8100, ws="wsproto", log_level="debug" if debug_mode else "info")
