# sentra-api/sentra_brain_api/core/lifecycle_config.py
from dataclasses import dataclass

@dataclass(frozen=True)
class AppLifecycleConfig:
    init_mcp: bool = True
    init_db: bool = True
