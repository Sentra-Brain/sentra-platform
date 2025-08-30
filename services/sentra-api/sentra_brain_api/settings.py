from typing import Literal
import os

ENGINE_MODE: Literal["legacy", "adk"] = os.getenv("ENGINE_MODE", "legacy")
