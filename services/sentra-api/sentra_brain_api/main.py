# main.py

from fastapi import FastAPI
from fastapi.concurrency import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from sentra_brain_api.core.app_state import AppState
from sentra_brain_api.core.constants import CONTACT
from sentra_brain_api.core.constants import DESCRIPTION
from sentra_brain_api.core.constants import LICENSE_INFO
from sentra_brain_api.core.constants import SWAGGER_FAVICON_URL, SWAGGER_UI_PARAMETERS, TITLE, VERSION
from sentra_brain_api.core.conversation_engine.engine import ConversationEngine
from sentra_brain_api.core.observability import instrument_app, add_correlation_id_middleware
from sentra_brain_api.features.admin.controller import AdminController
from sentra_brain_api.features.admin.settings.controller import SettingsController as AdminSettingsController
from sentra_brain_api.features.auth.controller import AuthController
from sentra_brain_api.features.chat.controller import ChatController
from sentra_brain_api.features.conversation.controller import ConversationController
from sentra_brain_api.features.knowledge.routes import sources, documents
from sentra_brain_api.features.llm_proxy.controller import LLMProxyController
from sentra_brain_api.features.organization.controller import router as organization_router
from sentra_brain_api.features.public.controller import PublicSettingsController
from sentra_brain_api.features.settings.controller import SettingsController
from sentra_brain_api.features.user.controller import UserController
from sentra_brain_api.middleware.error_handler import ErrorHandlerMiddleware
from sentra_core.core import logging
from sentra_core.infra.sql import postgres_service
import asyncio
import os

logger = logging.get_logger("sentra_brain_api")

# main.py (fragmentos relevantes)
from sentra_brain_api.core.conversation_engine.mcp.sentra_mcp_client import SentraMCPClient

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("App startup: initializing resources...")

    mcp_client = None
    try:
        if os.getenv("TESTING") != "true":
            # DB
            postgres_service.init_db()

            # MCP persistent client (connect on startup)
            mcp_client = await SentraMCPClient().__aenter__()
            # Optional: quick sanity checks
            healthy = await mcp_client.healthcheck()
            if not healthy:
                logger.warning("⚠️ MCP healthcheck failed at startup")
            else:
                try:
                    tools = await mcp_client.list_tools()
                    logger.info(f"✅ MCP tools registered: {[t['name'] for t in tools]}")
                except Exception as e:
                    logger.warning(f"⚠️ Could not list MCP tools at startup: {e}")

            # ConversationEngine with injected MCP client
            app.state._sentra = AppState(
                conversation_engine=ConversationEngine(mcp_client=mcp_client)
            )

            # Background healthchecks (non-blocking)
            asyncio.create_task(keep_vllm_alive(app))
            asyncio.create_task(keep_mcp_alive(app))
        else:
            # Testing: avoid external deps
            app.state._sentra = AppState(conversation_engine=None)

        # Hand over control to FastAPI
        yield

    finally:
        # Graceful shutdown: close MCP client if open
        if mcp_client is not None:
            try:
                await mcp_client.__aexit__(None, None, None)
            except Exception as e:
                logger.warning(f"Error closing MCP client: {e}")



async def keep_vllm_alive(app: FastAPI):
    """ Periodically checks VLLM backend liveness.
        Keeps logs useful for diagnosing connectivity issues.
    """
    engine: ConversationEngine | None = getattr(app.state._sentra, "conversation_engine", None)
    if not engine:
        return
    llm_client = engine.llm_client
    while True:
        healthy = await llm_client.healthcheck()
        if not healthy:
            logger.warning("⚠️ LLM backend not responding to healthcheck")
        else:
            logger.debug("✅ LLM healthcheck passed")
        await asyncio.sleep(30)

async def keep_mcp_alive(app: FastAPI):
    """
    Periodically checks MCP liveness by listing tools.
    Keeps logs useful for diagnosing connectivity issues.
    """
    try:
        engine: ConversationEngine | None = getattr(app.state._sentra, "conversation_engine", None)
        if not engine or not getattr(engine, "mcp_client", None):
            return
        client: SentraMCPClient = engine.mcp_client
        while True:
            ok = await client.healthcheck()
            if not ok:
                logger.warning("⚠️ MCP backend not responding to healthcheck")
            else:
                logger.debug("✅ MCP healthcheck passed")
            await asyncio.sleep(30)
    except Exception as e:
        logger.warning(f"keep_mcp_alive terminated: {e}")


def create_app():
    app = FastAPI(
        title=TITLE,
        description=DESCRIPTION,
        version=VERSION,
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
    admin_settings_controller = AdminSettingsController()
    settings_controller = SettingsController()
    public_settings_controller = PublicSettingsController()
    conversation_controller = ConversationController()
    llm_proxy_controller = LLMProxyController()
    chat_controller = ChatController()

    app.include_router(auth_controller.router, prefix="/auth", tags=["auth"])
    app.include_router(user_controller.router, prefix="/users", tags=["users"])
    app.include_router(admin_controller.router, prefix="/admin", tags=["admin"])
    app.include_router(admin_settings_controller.router, prefix="/admin", tags=["admin"])
    app.include_router(settings_controller.router, prefix="", tags=["settings"])
    app.include_router(public_settings_controller.router, prefix="/public", tags=["public"])
    app.include_router(conversation_controller.router, prefix="/conversations", tags=["conversations"])
    app.include_router(sources.router, prefix="/knowledge/sources", tags=["knowledge"])
    app.include_router(documents.router, prefix="/knowledge", tags=["knowledge"])
    app.include_router(llm_proxy_controller.router, prefix="/v1", tags=["llm-proxy"])
    app.include_router(chat_controller.router, prefix="/chat", tags=["chat"])
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

    uvicorn.run(app, host="0.0.0.0", port=8100, log_level="debug" if debug_mode else "info")
