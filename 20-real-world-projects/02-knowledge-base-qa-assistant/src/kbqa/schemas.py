"""JSON schema for grounded answers, plus a small standard-library validator.

The API's structured-output schema subset has no length or range constraints, and mock mode has
no guarantees at all, so the pipeline validates every response again before using it.
"""
from __future__ import annotations

from typing import Any

ANSWER_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "answerable": {
            "type": "boolean",
            "description": "true only if the provided documents contain the answer",
        },
        "answer": {"type": "string", "description": "The answer, or an empty string when not answerable."},
        "citations": {
            "type": "array",
            "items": {"type": "string"},
            "description": "IDs of the documents that support the answer, exactly as given in the id attribute.",
        },
        "confidence": {"type": "string", "enum": ["high", "medium", "low"]},
    },
    "required": ["answerable", "answer", "citations", "confidence"],
    "additionalProperties": False,
}

_TYPES = {"object": dict, "array": list, "string": str, "boolean": bool, "integer": int, "number": (int, float)}


def validate(instance: Any, schema: dict[str, Any], path: str = "$") -> list[str]:
    """Validate the subset of JSON Schema used in this project. Returns a list of error strings."""
    errors: list[str] = []
    expected = schema.get("type")
    if expected:
        py_type = _TYPES[expected]
        if not isinstance(instance, py_type) or (expected in ("integer", "number") and isinstance(instance, bool)):
            return [f"{path}: expected {expected}, got {type(instance).__name__}"]
    if "enum" in schema and instance not in schema["enum"]:
        errors.append(f"{path}: {instance!r} is not one of {schema['enum']}")
    if expected == "object":
        props = schema.get("properties", {})
        for key in schema.get("required", []):
            if key not in instance:
                errors.append(f"{path}: missing required field '{key}'")
        if schema.get("additionalProperties") is False:
            for key in instance:
                if key not in props:
                    errors.append(f"{path}: unexpected field '{key}'")
        for key, sub in props.items():
            if key in instance:
                errors.extend(validate(instance[key], sub, f"{path}.{key}"))
    if expected == "array" and "items" in schema:
        for i, item in enumerate(instance):
            errors.extend(validate(item, schema["items"], f"{path}[{i}]"))
    return errors
