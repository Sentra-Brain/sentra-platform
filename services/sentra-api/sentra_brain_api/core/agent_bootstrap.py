"""
Agent Registry bootstrapper for Sentra Runtime.

Loads all built-in, file-based, YAML-defined, and SQL-stored agent templates
into the global AgentRegistry at application startup.
"""

import importlib
import pkgutil
from pathlib import Path
from sentra.shared import logging
from sentra.runtime.agents import __path__ as AGENTS_PATH
from sentra.runtime.agents.registry import agent_registry, AgentTemplate
from sentra.shared.settings import settings

logger = logging.get_logger("agent_bootstrap")

# --------------------------------------------------------------------
# 1. Core agents that must always be loaded in a known order
# --------------------------------------------------------------------
CORE_AGENTS = [
    "sentra.runtime.agents.sentra_agent",  # cornerstone agent
]

# --------------------------------------------------------------------
# 2. YAML agents — placeholder for declarative agent definitions
# --------------------------------------------------------------------
YAML_AGENTS_DIR = Path("/mnt/sentra_agents")  # configurable path in the future


# --------------------------------------------------------------------
# Main bootstrap function
# --------------------------------------------------------------------
def initialize_agents() -> None:
    """Load core, dynamic, YAML, and database agents."""

    # ----------------------------------------------------------------
    # Load core agents explicitly
    # ----------------------------------------------------------------
    for mod in CORE_AGENTS:
        try:
            importlib.import_module(mod)
            logger.debug(f"Loaded core agent: {mod}")
        except Exception as e:
            logger.warning(f"⚠️ Failed to load core agent {mod}: {e}")

    # ----------------------------------------------------------------
    # Auto-discover dynamic agent modules in sentra.runtime.agents/
    # ----------------------------------------------------------------
    for _, module_name, _ in pkgutil.iter_modules(AGENTS_PATH):
        if module_name.endswith("_agent"):
            full_name = f"sentra.runtime.agents.{module_name}"
            if full_name not in CORE_AGENTS:
                try:
                    importlib.import_module(full_name)
                    logger.debug(f"Discovered extra agent: {full_name}")
                except Exception as e:
                    logger.warning(f"⚠️ Failed to import agent {full_name}: {e}")

    # ----------------------------------------------------------------
    # Load declarative YAML-based agents (future feature)
    # ----------------------------------------------------------------
    # Example: Each YAML file defines { key, name, description, instructions, model_id }
    try:
        if YAML_AGENTS_DIR.exists():
            for yaml_file in YAML_AGENTS_DIR.glob("*.yaml"):
                logger.debug(f"Found YAML agent definition: {yaml_file.name}")
                # Placeholder — future implementation:
                #   from sentra.runtime.agents.yaml_loader import load_agent_template_from_yaml
                #   template = load_agent_template_from_yaml(yaml_file)
                #   agent_registry.register(template)
                pass
        else:
            logger.debug(f"No YAML agents folder found at {YAML_AGENTS_DIR}")
    except Exception as e:
        logger.warning(f"⚠️ YAML agent loading failed: {e}")

    # ----------------------------------------------------------------
    # Load SQL-registered agent templates (future feature)
    # ----------------------------------------------------------------
    # Example: agents defined in organization configuration tables
    try:
        # Placeholder — future implementation:
        #   from sentra.domain.repository.agent_repository import AgentTemplateRepository
        #   repo = AgentTemplateRepository()
        #   db_templates = repo.list_enabled()
        #   for tmpl in db_templates:
        #       agent_registry.register(
        #           AgentTemplate(
        #               key=tmpl.key,
        #               name=tmpl.name,
        #               description=tmpl.description,
        #               instructions=tmpl.instructions,
        #               default_model_id=tmpl.model_id or settings.model_id,
        #               agent_cls=SentraAgent,
        #           )
        #       )
        pass
    except Exception as e:
        logger.warning(f"⚠️ SQL agent loading failed: {e}")

    # ----------------------------------------------------------------
    # Log final registry summary
    # ----------------------------------------------------------------
    templates = agent_registry.list_templates()
    logger.info("✅ %d agent templates available:", len(templates))
    for t in templates:
        logger.info("   • %(name)s [model=%(model_id)s]", t)
