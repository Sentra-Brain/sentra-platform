"""Default general-purpose conversational agent.

This agent is a thin ADK Agent instance that can answer general user
queries using the configured LLM backend. It is discovered by the
``AgentLoader`` via the ``root_agent`` attribute.
"""
from __future__ import annotations

from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from sentra.shared.settings import settings

# Instantiate model (delegates to configured vLLM / OpenAI compatible server)
llm_model = LiteLlm(model=settings.vllm_model, api_base=f"{settings.vllm_server_url}/v1")

root_agent = Agent(
    name="default_agent",
    model=llm_model,
    description="General-purpose assistant agent",
    instruction="You are a helpful assistant who answers user queries.",
)
