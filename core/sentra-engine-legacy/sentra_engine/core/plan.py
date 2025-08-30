from dataclasses import dataclass, field
from typing import Any, Dict, List, Literal, Optional, Union

# Core step kinds (extensible; unknown kinds fallback to Tool.Call with name=kind)
StepKind = Literal[
    "LLM.Respond",     # stream LLM text; may emit tool-calls
    "Tool.Call",       # generic MCP call (incl. RAG as a tool)
    "Context.Inject",  # append a system message (e.g., RAG context summary)
    "Control.If",      # simple branching on vars
    "Control.Wait",    # await for N seconds (rare; useful for polling)
]


@dataclass
class Step:
    id: str
    kind: Union[StepKind, str]                   # unknown kinds -> treat as Tool.Call(name=kind)
    name: Optional[str] = None                   # tool name for Tool.Call; label for others
    params: Dict[str, Any] = field(default_factory=dict)  # step-specific inputs
    assign: Optional[str] = None                 # store step result into plan.vars[assign]
    next: Optional[str] = None                   # default next step id
    on: Optional[Dict[str, str]] = None          # branching map for Control.If: {"true": "...", "false": "..."}


@dataclass
class Plan:
    schema_version: int = 1
    steps: List[Step] = field(default_factory=list)
    entry: Optional[str] = None                  # first step id (defaults to steps[0].id)
    guidance: Optional[str] = None               # global hint for the LLM
    vars: Dict[str, Any] = field(default_factory=dict)  # scratch vars shared across steps
