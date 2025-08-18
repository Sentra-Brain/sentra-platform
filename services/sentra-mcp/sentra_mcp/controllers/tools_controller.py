from fastapi import APIRouter, Body, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Any, Awaitable, Callable, Dict, List, Optional, get_args, get_origin, Union
import asyncio
import inspect

router = APIRouter(prefix="/tools", tags=["tools"])

# --------- Models ---------

class RunRequest(BaseModel):
    name: str = Field(..., description="Tool name")
    args: Dict[str, Any] = Field(default_factory=dict)

# --------- Helpers ---------

def _callable_from_tool(obj: Any) -> Optional[Callable[..., Awaitable[Any]]]:
    # FastMCP registered callable (keep fallbacks)
    for attr in ("func", "handler", "callable", "fn"):
        cb = getattr(obj, attr, None)
        if cb:
            return cb
    return None

def _json_type_from_py(t: Any) -> Dict[str, Any]:
    origin = get_origin(t)
    args = get_args(t)

    if t in (str,):
        return {"type": "string"}
    if t in (int,):
        return {"type": "integer"}
    if t in (float,):
        return {"type": "number"}
    if t in (bool,):
        return {"type": "boolean"}
    if t in (dict, Dict):
        return {"type": "object"}
    if t in (list, List):
        return {"type": "array"}

    if origin in (list, List) and args:
        return {"type": "array", "items": _json_type_from_py(args[0])}
    if origin in (dict, Dict) and len(args) == 2:
        # Dict[K, V] -> object with additionalProperties: schema(V)
        return {"type": "object", "additionalProperties": _json_type_from_py(args[1])}

    # Optional[T] == Union[T, NoneType]
    if origin is Union and args and any(a is type(None) for a in args):
        non_none = [a for a in args if a is not type(None)]
        if len(non_none) == 1:
            subschema = _json_type_from_py(non_none[0])
            return {"anyOf": [subschema, {"type": "null"}]}

    # Fallback – unknown/Any
    return {}

async def _registry_payload(request: Request) -> List[Dict[str, Any]]:
    tools = await request.app.state.mcp.get_tools()
    out: List[Dict[str, Any]] = []

    for t in tools.values():
        cb = _callable_from_tool(t)
        sig = inspect.signature(cb) if cb else None
        # Try to resolve type hints, tolerate failures
        try:
            from typing import get_type_hints as _gth
            hints = _gth(cb) if cb else {}
        except Exception:
            hints = {}

        properties: Dict[str, Any] = {}
        required: List[str] = []

        if sig:
            for name, param in sig.parameters.items():
                if name == "self":
                    continue
                ann = hints.get(name, param.annotation)
                sch = _json_type_from_py(ann)
                if param.default is inspect.Parameter.empty:
                    required.append(name)
                else:
                    if param.default is not None:
                        sch["default"] = param.default
                properties[name] = sch

        parameters_schema = {
            "type": "object",
            "properties": properties,
            "required": required,
            "additionalProperties": False,
        }

        out.append({
            "name": getattr(t, "name", None) or getattr(t, "tool", None),
            "title": getattr(t, "title", None) or getattr(t, "name", None),
            "description": getattr(t, "description", None) or "",
            "parameters": parameters_schema,
        })
    return out

# --------- Routes ---------

@router.get("/registry")
async def tools_registry(request: Request):
    try:
        return await _registry_payload(request)
    except Exception as e:
        return JSONResponse({"error": "registry_error"}, status_code=500)

@router.post("/run")
async def tools_run(request: Request, req: RunRequest = Body(...)):
    try:
        tools = await request.app.state.mcp.get_tools()
        tool = tools.get(req.name)
        if not tool:
            return JSONResponse({"ok": False, "error": "tool_not_found"}, status_code=404)

        cb = _callable_from_tool(tool)
        if not cb:
            return JSONResponse({"ok": False, "error": "tool_handler_missing"}, status_code=500)

        if asyncio.iscoroutinefunction(cb):
            result = await cb(**(req.args or {}))
        else:
            res = cb(**(req.args or {}))
            if asyncio.iscoroutine(res):  # in case the callable returns a coroutine
                result = await res
            else:
                result = res

        return {"ok": True, "content": result}
    except TypeError as te:
        # likely argument mismatch
        return JSONResponse({"ok": False, "error": f"bad_args: {te}"}, status_code=400)
    except Exception:
        return JSONResponse({"ok": False, "error": "tool_execution_failed"}, status_code=500)
