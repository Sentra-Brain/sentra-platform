from fastapi import HTTPException
from starlette.status import HTTP_400_BAD_REQUEST
from uuid import uuid4
from datetime import datetime, timezone


class SentraHTTPException(HTTPException):
    def __init__(
        self,
        status_code: int = HTTP_400_BAD_REQUEST,
        code: str = "UNKNOWN_ERROR",
        message: str = "An unexpected error occurred.",
        details: str = None,
        path: str = None,
        suggestion: str = None
    ):
        request_id = str(uuid4())
        timestamp = datetime.now(timezone.utc).isoformat()

        error_body = {
            "status": "error",
            "statusCode": status_code,
            "error": {
                "code": code,
                "message": message,
                "details": details,
                "timestamp": timestamp,
                "path": path,
                "suggestion": suggestion,
                "requestId": request_id
            },
            "requestId": request_id,
            "documentation_url": "https://api.sentrabrain.com/docs/errors"
        }

        super().__init__(status_code=status_code, detail=error_body)
