from datetime import datetime, timezone
from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from sentra_brain_api.core.exceptions import SentraHTTPException
import traceback


class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            return await call_next(request)

        except SentraHTTPException as exc:
            return JSONResponse(
                status_code=exc.status_code,
                content=exc.detail
            )

        except Exception as e:
            request_id = request.headers.get("X-Request-ID", "n/a")
            return JSONResponse(
                status_code=500,
                content={
                    "status": "error",
                    "statusCode": 500,
                    "error": {
                        "code": "INTERNAL_SERVER_ERROR",
                        "message": "An unexpected server error occurred.",
                        "details": str(e),
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "path": request.url.path,
                        "requestId": request_id,
                        "suggestion": "Please contact support with the request ID."
                    },
                    "requestId": request_id,
                    "documentation_url": "https://api.sentrabrain.com/docs/errors"
                }
            )
