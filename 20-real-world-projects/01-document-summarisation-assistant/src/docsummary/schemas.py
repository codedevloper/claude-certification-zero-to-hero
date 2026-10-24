"""JSON schemas sent as `output_config.format`, plus a small standard-library validator.

Structured outputs guarantee the response parses and matches the schema in live mode, but the
schema subset the API accepts has no length or range constraints, and mock mode has no
guarantee at all. So every response is validated again here before the pipeline uses it.
"""
from __future__ import annotations

from typing import Any

AUDIENCES = ("executive", "engineering", "compliance")
CATEGORIES = ("finding", "metric", "risk", "decision", "action")

_KEY_POINT = {
    "type": "object",
    "properties": {
        "point": {"type": "string", "description": "One sentence in your own words."},
        "evidence_quote": {
            "type": "string",
            "description": "A short verbatim quote copied exactly from the source that supports the point.",
        },
        "category": {"type": "string", "enum": list(CATEGORIES)},
    },
    "required": ["point", "evidence_quote", "category"],
    "additionalProperties": False,
}

MAP_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {"key_points": {"type": "array", "items": _KEY_POINT}},
    "required": ["key_points"],
    "additionalProperties": False,
}

SUMMARY_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "audience": {"type": "string", "enum": list(AUDIENCES)},
        "headline": {"type": "string"},
        "summary": {"type": "string"},
        "key_points": {"type": "array", "items": _KEY_POINT},
        "action_items": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "action": {"type": "string"},
                    "owner": {"type": "string", "description": "Owner named in the source, or 'Not stated'."},
                    "evidence_quote": {"type": "string"},
                },
                "required": ["action", "owner", "evidence_quote"],
                "additionalProperties": False,
            },
        },
        "open_questions": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["audience", "headline", "summary", "key_points", "action_items", "open_questions"],
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
