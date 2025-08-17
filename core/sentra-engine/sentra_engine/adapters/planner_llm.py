# sentra_engine/adapters/planner_llm.py
import json, httpx
from typing import Any
from sentra_engine.ports.planner import PlannerPort
from sentra_engine.core.models import PlanStep, Transcript

_PROMPT = """You are the Planner for a chat engine.
For THIS VERSION you may ONLY choose the action "Respond".
Return STRICT JSON with two fields, no prose:
{"action":"Respond","guidance":"One or two sentences guiding the writer."}
"""

class LLMPlannerAdapter(PlannerPort):
    def __init__(self, base_url: str, *, model: str, request_timeout: float | None = None):
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.request_timeout = request_timeout

    async def plan(self, transcript: Transcript, context: str) -> PlanStep:
        url = f"{self.base_url}/v1/chat/completions"
        messages = [
            {"role": "system", "content": _PROMPT},
            {"role": "user", "content": _summarize_for_planner(transcript)},
        ]
        payload: dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "temperature": 0,
            "stream": False,
            "response_format": {"type": "json_object"},
        }
        async with httpx.AsyncClient(timeout=self.request_timeout) as client:
            resp = await client.post(url, json=payload)
            resp.raise_for_status()
            data = resp.json()
        text = data.get("choices", [{}])[0].get("message", {}).get("content", "{}")
        try:
            obj = json.loads(text)
        except Exception:
            obj = {"action": "Respond", "guidance": ""}
        action = str(obj.get("action") or "Respond")
        guidance = str(obj.get("guidance") or "")
        return PlanStep(action=action, params={"guidance": guidance})

def _summarize_for_planner(t: Transcript) -> str:
    # Keep it simple for M2: last user message only (fallback to empty)
    for m in reversed(t.messages):
        if (m.role or "").lower() == "user":
            return m.content or ""
    return ""
