from fastapi import FastAPI
from fastapi.concurrency import asynccontextmanager
from fastapi.responses import RedirectResponse
import logging
import os
import uvicorn

from sentra_brain_api.features.auth.controller import router as auth_router
from sentra_brain_api.features.admin.controller import router as admin_router
from sentra_brain_api.features.conversations.controller import router as conversations_router

TITLE = "Sentra Brain API"
DESCRIPTION = "API for Sentra Brain platform."
CONTACT = {"name": "Sentra Brain Team", "email": "support@sentra.com"}
LICENSE_INFO = {"name": "MIT"}
SWAGGER_UI_PARAMETERS = {"defaultModelsExpandDepth": -1}
SWAGGER_FAVICON_URL = "https://fastapi.tiangolo.com/img/favicon.png"

logger = logging.getLogger("sentra_brain_api")
logging.basicConfig(level=logging.INFO)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Place for DB init, etc.
    logger.info("App startup: initializing resources...")
    yield

def create_app():
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

    app.include_router(auth_router, prefix="/api/v1/auth", tags=["auth"])
    app.include_router(admin_router, prefix="/api/v1/admin", tags=["admin"])
    app.include_router(conversations_router, prefix="/api/v1/conversations", tags=["conversations"])

    return app

app = create_app()

@app.get("/", include_in_schema=False, response_class=RedirectResponse)
async def redirect_to_swagger():
    logger.info("Redirect to swagger...")
    return RedirectResponse(url="/docs")

if __name__ == "__main__":
    if os.getenv("DEBUG_MODE") == "true":
        import debugpy
        debugpy.listen(("0.0.0.0", 5678))
        debugpy.wait_for_client()
    uvicorn.run(app, host="0.0.0.0", port=8000)
