import logging
import sys
from sentra_brain_api.core import constants


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
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    handler.setFormatter(formatter)
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
