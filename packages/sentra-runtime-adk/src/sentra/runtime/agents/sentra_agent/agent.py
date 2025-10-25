"""Sentra Agent – customized general-purpose conversational agent.

This is the root agent discovered by AgentLoader. It uses the configured
vLLM backend, has a clear identity, and can leverage context and tools.
"""
from __future__ import annotations

from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from sentra.shared.settings import settings

llm_model = LiteLlm(
    model=settings.vllm_model,
    api_base=f"{settings.vllm_server_url}/v1",
)

root_agent = Agent(
    name="sentra_agent",
    model=llm_model,
    description="Sentra, your private AI copilot",
    instruction=(
        "You are Sentra, a private and secure AI assistant designed to help "
        "users with their work. "
        "You always use available context (conversation history, memories, and "
        "knowledge from documents) to give precise, concise, and useful answers. "
        "When asked 'who are you?', you reply: 'I am Sentra, your customized AI copilot, "
        "here to support you in your daily tasks.'"
    ),
)

