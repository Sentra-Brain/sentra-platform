"""Dynamic agent discovery and loading utilities.

This module provides :class:`AgentLoader` which discovers agent modules
under the ``sentra.runtime.agents`` package. An "agent" is any module or
package that exposes a ``root_agent`` variable referencing an instantiated
ADK ``BaseAgent`` (e.g. created via ``google.adk.agents.Agent``).

Discovery rules (initial implementation):
  - A top-level python module file ``<name>.py`` containing ``root_agent``.
  - A subpackage ``<name>/agent.py`` containing ``root_agent``.
  - A subpackage ``<name>/__init__.py`` exposing ``root_agent`` (optional for now).

Internal / non-user selectable helpers can be excluded by prefixing their
name with ``__`` or by simply not exposing ``root_agent``.

The loader caches imported agent instances to avoid redundant imports.
"""
from __future__ import annotations

from dataclasses import dataclass
from importlib import import_module
from importlib.util import find_spec
from pathlib import Path
from types import ModuleType
from typing import Dict, List

from google.adk.agents import BaseAgent  # type: ignore


@dataclass
class LoadedAgent:
    name: str
    instance: BaseAgent
    module: ModuleType
    

class AgentLoader:
    """Discover and load agents dynamically.

    Parameters
    ----------
    agents_path: Path
        Filesystem path to the directory containing agent modules.
    package_prefix: str
        Python import package prefix for modules in ``agents_path``.
    """

    def __init__(self, agents_path: Path | None = None, package_prefix: str = "sentra.runtime.agents"):
        if agents_path is None:
            # Resolve directory containing this file (.. is the agents package)
            agents_path = Path(__file__).parent
        self.agents_path = agents_path
        self.package_prefix = package_prefix
        self._cache: Dict[str, LoadedAgent] = {}

    # ---------------------------- Discovery ----------------------------
    def list_agents(self) -> List[str]:
        """List available agent names.

        Returns only names for which a ``root_agent`` can be resolved
        (without executing heavy imports multiple times). We attempt a
        lightweight inspection by checking file existence patterns first.
        Hidden directories, ``__pycache__`` and dunder-prefixed entries are skipped.
        """

        names: List[str] = []
        for entry in sorted(self.agents_path.iterdir()):
            if entry.name.startswith("__") or entry.name == "agent_loader.py":  # internal / skip loader file
                continue
            if entry.is_dir():
                # pattern: <name>/agent.py OR <name>/__init__.py
                agent_py = entry / "agent.py"
                init_py = entry / "__init__.py"
                if agent_py.exists() or init_py.exists():
                    # We will attempt load to ensure a root_agent exists
                    if self._has_root_agent(entry.name):
                        names.append(entry.name)
            elif entry.suffix == ".py":
                if entry.stem in {"__init__", "agent_loader"}:
                    continue
                if self._has_root_agent(entry.stem):
                    names.append(entry.stem)
        return names

    # ----------------------------- Loading -----------------------------
    def load_agent(self, name: str) -> BaseAgent:
        """Load (or return cached) agent instance by name.

        Resolution order mimics ADK expectations:
          1. Import as module or package: ``sentra.runtime.agents.<name>``
          2. Fallback to submodule: ``sentra.runtime.agents.<name>.agent``
        After importing, look for ``root_agent`` attribute referencing a
        ``BaseAgent`` instance.
        """

        if name in self._cache:
            return self._cache[name].instance

        errors: List[str] = []
        module: ModuleType | None = None
        # Attempt primary import
        full_module = f"{self.package_prefix}.{name}"
        try:
            module = import_module(full_module)
        except Exception as e:  # noqa: BLE001
            errors.append(f"{full_module}: {e}")

        # Fallback to <name>.agent
        if module is None:
            alt_module = f"{full_module}.agent"
            try:
                module = import_module(alt_module)
            except Exception as e:  # noqa: BLE001
                errors.append(f"{alt_module}: {e}")

        if module is None:
            raise ImportError(f"Could not import agent '{name}'. Attempts: {errors}")

        if not hasattr(module, "root_agent"):
            raise AttributeError(f"Module '{module.__name__}' does not define 'root_agent'")

        root_agent = getattr(module, "root_agent")
        if not isinstance(root_agent, BaseAgent):  # ensure instantiated object
            raise TypeError(
                f"Attribute 'root_agent' in '{module.__name__}' is not a BaseAgent instance (got {type(root_agent)!r})"
            )

        self._cache[name] = LoadedAgent(name=name, instance=root_agent, module=module)
        return root_agent

    # ---------------------------- Utilities ----------------------------
    def _has_root_agent(self, name: str) -> bool:
        """Check if an agent name resolves to a module with ``root_agent``.

        This performs import attempts but caches positive result to avoid
        re-import for list -> load flow. We intentionally ignore exceptions
        and treat them as absence during discovery.
        """
        try:
            if name in self._cache:
                return True
            full_module = f"{self.package_prefix}.{name}"
            spec = find_spec(full_module)
            alt_spec = find_spec(f"{full_module}.agent") if spec is None else None
            if spec is None and alt_spec is None:
                return False
            # Import fully (cost acceptable for current scale) and verify
            try:
                mod = import_module(full_module)
            except Exception:  # noqa: BLE001
                try:
                    mod = import_module(f"{full_module}.agent")
                except Exception:
                    return False
            if hasattr(mod, "root_agent") and isinstance(getattr(mod, "root_agent"), BaseAgent):
                self._cache[name] = LoadedAgent(name=name, instance=getattr(mod, "root_agent"), module=mod)
                return True
            return False
        except Exception:  # noqa: BLE001
            return False

__all__ = ["AgentLoader"]
