import logging
import pkgutil
import importlib
import sentra.domain.entities as _entities_pkg

logger = logging.getLogger("entity-import")

for _, module_name, _ in pkgutil.iter_modules(_entities_pkg.__path__):
    logger.debug(f"Importing entity module: {_entities_pkg.__name__}.{module_name}")
    importlib.import_module(f"{_entities_pkg.__name__}.{module_name}")