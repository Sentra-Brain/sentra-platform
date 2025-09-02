from sentra_engine.config import settings


class PolicyError(Exception):
    """Raised when an agent violates policy restrictions."""


def check_tool_allowed(agent_name: str, tool_name: str) -> None:
    """Ensure ``agent_name`` is allowed to invoke ``tool_name``."""
    allowlist = settings.tool_allowlist.get(agent_name, [])
    if tool_name not in allowlist:
        raise PolicyError(f"{agent_name} is not allowed to use {tool_name}")


def get_allowed_sources(agent_name: str) -> list[str]:
    """Return source identifiers ``agent_name`` may access."""
    return settings.rag_source_allowlist.get(agent_name, [])


def redact_pii(text: str) -> str:
    """Placeholder PII redaction stub."""
    return text.replace("John", "[REDACTED]")
