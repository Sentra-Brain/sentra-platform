from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class ErrorDetail(BaseModel):
    code: str
    message: str
    details: Optional[str] = None
    path: Optional[str] = None
    suggestion: Optional[str] = None
    timestamp: str
    requestId: Optional[str] = None


class ErrorResponse(BaseModel):
    status: str = "error"
    statusCode: int
    error: ErrorDetail
    documentation_url: Optional[str] = "https://api.sentrabrain.com/docs/errors"
