import asyncio
from typing import AsyncGenerator, List, Optional, Sequence, Dict, Any

from sentra_engine.core.plan import Plan, Step
from sentra_engine.core.models import DeltaEvent, Message, ToolSchema, PromptContext
from sentra_engine.core.time import utc_now_iso
from sentra_engine.core.id_utils import normalize_message_id
from sentra_engine.tools.internal.parser import ToolStreamParser
from sentra_engine.tools.internal.formatters import normalize_tool_output


class StepRunner:
    """
    Executes a Plan over a transcript. Streams message deltas during LLM.Respond,
    executes Tool.Call via orchestrator, and supports simple branching/waits.
    """

    def __init__(
        self,
        *,
        conversation_id: str,
        llm,
        persistence,
        tool_orchestrator=None,
        rag=None,
        tools_schema: Optional[Sequence[ToolSchema]] = None,
        max_rounds: int = 3,
        allow_plaintext_fallback: bool = False,
    ) -> None:
        self.conversation_id = conversation_id
        self.llm = llm
        self.persistence = persistence
        self.tool_orchestrator = tool_orchestrator
        self.rag = rag
        self.tools_schema = tools_schema
        self.max_rounds = max_rounds
        self.allow_plaintext_fallback = allow_plaintext_fallback
        self.final_text: str = ""

    async def run(self, plan: Plan, transcript: List[Message]) -> AsyncGenerator[DeltaEvent, None]:
        text_acc: List[str] = []
        steps_by_id: Dict[str, Step] = {s.id: s for s in plan.steps}
        current_id: Optional[str] = plan.entry or (plan.steps[0].id if plan.steps else None)
        rounds_on_respond = 0

        def as_openai_msg(m: Message) -> Dict[str, Any]:
            return {"role": (m.role or "system"), "content": (m.content or "")}

        while current_id:
            step = steps_by_id.get(current_id)
            if not step:
                break
            kind = str(step.kind)

            # ---- LLM.Respond -------------------------------------------------
            if kind == "LLM.Respond":
                guidance = step.params.get("guidance") if isinstance(step.params, dict) else None
                parser = ToolStreamParser(allow_plaintext_fallback=self.allow_plaintext_fallback)
                agen = self.llm.chat_stream(
                    prompt_context=PromptContext(messages=[as_openai_msg(m) for m in transcript]),
                    tools_schema=self.tools_schema,
                    guidance=guidance or plan.guidance,

                )
                try:
                    async for ev in agen:
                        parser.ingest(ev)
                        if ev.type == "message_delta" and ev.content:
                            text_acc.append(ev.content)
                            yield DeltaEvent(type="message_delta", content=ev.content)
                finally:
                    if hasattr(agen, "aclose"):
                        await agen.aclose()

                # Execute any tool intents immediately before proceeding
                intents = parser.finalize_intents()
                if intents and self.tool_orchestrator:
                    rounds_on_respond += 1
                    for call in intents:
                        res = await self.tool_orchestrator.execute_one(
                            conversation_id=self.conversation_id,
                            plan_step_id=normalize_message_id(None),
                            tool_name=call.name,
                            args=call.arguments,
                            tool_call_id=call.id,
                        )
                        sys_msg = Message(
                            id=normalize_message_id(None, prefer_hex=True),
                            role="system",
                            content=normalize_tool_output(call.name, res.content if res.ok else res.error),
                            timestamp=utc_now_iso(),
                        )
                        await self.persistence.append_message(self.conversation_id, sys_msg)
                        transcript.append(sys_msg)

                    # Repeat this LLM.Respond step to allow the model to use tool results
                    if rounds_on_respond < self.max_rounds:
                        continue
                rounds_on_respond = 0
                current_id = step.next
                continue

            # ---- Tool.Call (or unknown kind fallback) ------------------------
            if kind == "Tool.Call" or self._is_unknown_kind(kind):
                name = step.name or (None if kind == "Tool.Call" else kind)
                args = step.params or {}
                if name and self.tool_orchestrator:
                    res = await self.tool_orchestrator.execute_one(
                        conversation_id=self.conversation_id,
                        plan_step_id=normalize_message_id(None),
                        tool_name=name,
                        args=args,
                        tool_call_id=None,
                    )
                    # persist normalized tool output as system message
                    sys_msg = Message(
                        id=normalize_message_id(None, prefer_hex=True),
                        role="system",
                        content=normalize_tool_output(name, res.content if res.ok else res.error),
                        timestamp=utc_now_iso(),
                    )
                    await self.persistence.append_message(self.conversation_id, sys_msg)
                    transcript.append(sys_msg)
                    if step.assign:
                        # Store content or error into plan vars
                        plan.vars[step.assign] = res.content if res.ok else {"error": res.error}
                current_id = step.next
                continue

            # ---- Context.Inject ----------------------------------------------
            if kind == "Context.Inject":
                text = (step.params or {}).get("text", "")
                sys_msg = Message(
                    id=normalize_message_id(None, prefer_hex=True),
                    role="system",
                    content=str(text),
                    timestamp=utc_now_iso(),
                )
                await self.persistence.append_message(self.conversation_id, sys_msg)
                transcript.append(sys_msg)
                current_id = step.next
                continue

            # ---- Control.If ---------------------------------------------------
            if kind == "Control.If":
                cond = step.params or {}
                truth = self._eval_condition(plan.vars, cond)
                next_map = step.on or {}
                current_id = next_map.get("true") if truth else next_map.get("false")
                continue

            # ---- Control.Wait -------------------------------------------------
            if kind == "Control.Wait":
                try:
                    seconds = float((step.params or {}).get("seconds", 0))
                except Exception:
                    seconds = 0.0
                if seconds > 0:
                    await asyncio.sleep(seconds)
                current_id = step.next
                continue

            # Unknown step kind, skip
            current_id = step.next

        self.final_text = ("".join(text_acc)).strip() or "(no content)"

    @staticmethod
    def _is_unknown_kind(kind: str) -> bool:
        return kind not in {"LLM.Respond", "Tool.Call", "Context.Inject", "Control.If", "Control.Wait"}

    @staticmethod
    def _eval_condition(vars_dict: Dict[str, Any], cond: Dict[str, Any]) -> bool:
        """
        Supported:
          {"var": "results.total", "equals": 0}
          {"var": "results.items", "exists": true}
        """
        var_path = str(cond.get("var") or "")
        val = _get_dotted(vars_dict, var_path)
        if "exists" in cond:
            want = bool(cond.get("exists"))
            return (val is not None) == want
        if "equals" in cond:
            return val == cond.get("equals")
        return bool(val)


def _get_dotted(root: Dict[str, Any], path: str) -> Any:
    cur: Any = root
    for part in [p for p in path.split(".") if p]:
        if isinstance(cur, dict) and part in cur:
            cur = cur[part]
        else:
            return None
    return cur
