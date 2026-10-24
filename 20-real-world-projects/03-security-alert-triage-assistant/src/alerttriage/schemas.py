"""Triage output schema (sent as `output_config.format`) and a small standard-library validator.

The structured-output schema subset has no pattern, length or range constraints, so technique ID
formats, targets and severity rules are enforced in `triage.py` after validation.
"""
from __future__ import annotations

from typing import Any

SEVERITIES = ("informational", "low", "medium", "high", "critical")
ADVISORY_ACTIONS = ("investigate", "enrich", "notify")
CONTAINMENT_ACTIONS = ("isolate_host", "disable_account", "block_ip", "reset_credentials")

TRIAGE_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "alert_id": {"type": "string"},
        "severity": {"type": "string", "enum": list(SEVERITIES)},
        "confidence": {"type": "string", "enum": ["low", "medium", "high"]},
        "summary": {"type": "string", "description": "Two or three sentences for the analyst."},
        "attack_techniques": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "technique_id": {"type": "string", "description": "MITRE ATT&CK ID such as T1110 or T1110.003"},
                    "name": {"type": "string"},
                    "rationale": {"type": "string"},
                },
                "required": ["technique_id", "name", "rationale"],
                "additionalProperties": False,
            },
        },
        "next_actions": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "action_type": {"type": "string", "enum": list(ADVISORY_ACTIONS + CONTAINMENT_ACTIONS)},
                    "target": {"type": "string", "description": "A host, user, IP or domain copied from the alert entities."},
                    "rationale": {"type": "string"},
                },
                "required": ["action_type", "target", "rationale"],
                "additionalProperties": False,
            },
        },
        "injection_suspected": {"type": "boolean"},
        "false_positive_likelihood": {"type": "string", "enum": ["low", "medium", "high"]},
    },
    "required": [
        "alert_id", "severity", "confidence", "summary", "attack_techniques",
        "next_actions", "injection_suspected", "false_positive_likelihood",
    ],
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
