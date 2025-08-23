from typing import Dict, Any

from jsonschema import Draft202012Validator


class ArgsCoercer:
    """Coerce argument types based on JSON schema and validate."""

    def __init__(self, schema: dict):
        self.validator = Draft202012Validator(schema)

    def coerce(self, args: Dict[str, Any]) -> Dict[str, Any]:
        props = self.validator.schema.get("properties", {})
        out = dict(args)
        for key, ps in props.items():
            if key in out and ps.get("type") == "integer" and isinstance(out[key], str):
                try:
                    out[key] = int(out[key])
                except ValueError:
                    pass
        self.validator.validate(out)
        return out


__all__ = ["ArgsCoercer"]

