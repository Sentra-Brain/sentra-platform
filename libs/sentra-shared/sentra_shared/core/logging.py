import logging
import sys
import uuid
from typing import Optional
from contextvars import ContextVar
from sentra_shared.core import constants

# Context variable to store request_id across async calls
request_id_context: ContextVar[Optional[str]] = ContextVar('request_id', default=None)

class RequestContextFilter(logging.Filter):
    """Filter to inject request_id into log records for tracing."""
    
    def filter(self, record):
        request_id = request_id_context.get()
        if request_id:
            record.request_id = request_id
        else:
            record.request_id = "no-request-id"
        return True


def configure_logging(debug: bool = False):
    """
    Configure the root logger to control all application logging,
    including FastAPI and Uvicorn. Should be called before any logging.
    """
    level = logging.DEBUG if debug else logging.INFO

    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    # Remove existing handlers (e.g., Uvicorn’s default handlers)
    root_logger.handlers.clear()

    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(request_id)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    handler.setFormatter(formatter)
    
    # Add request context filter for tracing
    handler.addFilter(RequestContextFilter())
    root_logger.addHandler(handler)

    # Silence Uvicorn’s internal loggers to avoid duplication
    logging.getLogger("uvicorn.error").propagate = False
    logging.getLogger("uvicorn.access").propagate = False

    # Silence noisy pymongo heartbeat logs
    logging.getLogger("pymongo.topology").setLevel(logging.WARNING)


def get_logger(name: str | None = None) -> logging.Logger:
    """
    Returns a module-specific logger.
    """
    if name is None:
        name = constants.APP_NAME
    return logging.getLogger(name)


def set_request_id(request_id: str = None) -> str:
    """Set the request_id for the current context. Returns the request_id."""
    if request_id is None:
        request_id = str(uuid.uuid4())
    request_id_context.set(request_id)
    return request_id


def get_request_id() -> Optional[str]:
    """Get the current request_id from context."""
    return request_id_context.get()
