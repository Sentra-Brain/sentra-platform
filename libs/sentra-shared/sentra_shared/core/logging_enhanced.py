import logging
import sys
import uuid
import time
from typing import Optional, Dict, Any
from contextvars import ContextVar
from sentra_shared.core import constants

# Context variable to store request_id across async calls
request_id_context: ContextVar[Optional[str]] = ContextVar('request_id', default=None)


class StructuredLogger:
    """Enhanced logger with structured logging capabilities."""
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
    
    def log_step(self, level: int, step: str, document_id: str = None, 
                 duration: float = None, error: str = None, **kwargs):
        """Log a processing step with structured data."""
        extra_data = {
            'request_id': request_id_context.get(),
            'step': step,
            'document_id': document_id,
            'duration': duration,
            'error': error,
            **kwargs
        }
        
        # Filter out None values
        extra_data = {k: v for k, v in extra_data.items() if v is not None}
        
        # Create message
        message_parts = [f"Step: {step}"]
        if document_id:
            message_parts.append(f"Document: {document_id}")
        if duration is not None:
            message_parts.append(f"Duration: {duration:.2f}s")
        if error:
            message_parts.append(f"Error: {error}")
        
        message = " | ".join(message_parts)
        
        # Add extra data to logger record
        self.logger.log(level, message, extra=extra_data)
    
    def info_step(self, step: str, **kwargs):
        """Log an info-level step."""
        self.log_step(logging.INFO, step, **kwargs)
    
    def warning_step(self, step: str, **kwargs):
        """Log a warning-level step."""
        self.log_step(logging.WARNING, step, **kwargs)
    
    def error_step(self, step: str, **kwargs):
        """Log an error-level step."""
        self.log_step(logging.ERROR, step, **kwargs)
    
    # Delegate standard logging methods to the underlying logger
    def info(self, message, *args, **kwargs):
        self.logger.info(message, *args, **kwargs)
    
    def warning(self, message, *args, **kwargs):
        self.logger.warning(message, *args, **kwargs)
    
    def error(self, message, *args, **kwargs):
        self.logger.error(message, *args, **kwargs)
    
    def debug(self, message, *args, **kwargs):
        self.logger.debug(message, *args, **kwargs)


class RequestContextFilter(logging.Filter):
    """Filter to inject request_id into log records."""
    
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

    # Remove existing handlers (e.g., Uvicorn's default handlers)
    root_logger.handlers.clear()

    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(request_id)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    handler.setFormatter(formatter)
    
    # Add request context filter
    handler.addFilter(RequestContextFilter())
    root_logger.addHandler(handler)

    # Silence Uvicorn's internal loggers to avoid duplication
    logging.getLogger("uvicorn.error").propagate = False
    logging.getLogger("uvicorn.access").propagate = False

    # Silence noisy pymongo heartbeat logs
    logging.getLogger("pymongo.topology").setLevel(logging.WARNING)


def get_logger(name: str | None = None) -> StructuredLogger:
    """
    Returns a module-specific structured logger.
    """
    if name is None:
        name = constants.APP_NAME
    logger = logging.getLogger(name)
    return StructuredLogger(logger)


def set_request_id(request_id: str = None) -> str:
    """Set the request_id for the current context. Returns the request_id."""
    if request_id is None:
        request_id = str(uuid.uuid4())
    request_id_context.set(request_id)
    return request_id


def get_request_id() -> Optional[str]:
    """Get the current request_id from context."""
    return request_id_context.get()


class StepTimer:
    """Context manager for timing processing steps."""
    
    def __init__(self, logger: StructuredLogger, step: str, document_id: str = None):
        self.logger = logger
        self.step = step
        self.document_id = document_id
        self.start_time = None
    
    def __enter__(self):
        self.start_time = time.time()
        self.logger.info_step(f"{self.step}_started", document_id=self.document_id)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = time.time() - self.start_time
        if exc_type is None:
            self.logger.info_step(f"{self.step}_completed", 
                                document_id=self.document_id, 
                                duration=duration)
        else:
            self.logger.error_step(f"{self.step}_failed", 
                                 document_id=self.document_id, 
                                 duration=duration, 
                                 error=str(exc_val))