# sentra_brain_api/core/exceptions.py
from typing import Optional, Any, Dict
from fastapi import HTTPException
from starlette.status import HTTP_400_BAD_REQUEST
from uuid import uuid4
from datetime import datetime, timezone

class SentraHTTPException(HTTPException):
    def __init__(
        self,
        *,
        status_code: int = HTTP_400_BAD_REQUEST,
        code: str = "UNKNOWN_ERROR",
        message: str = "An unexpected error occurred.",
        details: Optional[str] = None,
        path: Optional[str] = None,
        suggestion: Optional[str] = None,
        extra: Optional[Dict[str, Any]] = None
    ):
        request_id = str(uuid4())
        timestamp = datetime.now(timezone.utc).isoformat()

        error: Dict[str, Any] = {
            "code": code,
            "message": message,
            "timestamp": timestamp,
            "requestId": request_id,
        }
        if details is not None:
            error["details"] = details
        if path is not None:
            error["path"] = path
        if suggestion is not None:
            error["suggestion"] = suggestion
        if extra:
            error.update(extra)

        detail = {
            "status": "error",
            "statusCode": status_code,
            "error": error,
            "requestId": request_id,
            "documentation_url": "https://api.sentrabrain.com/docs/errors",
        }

        super().__init__(status_code=status_code, detail=detail)
