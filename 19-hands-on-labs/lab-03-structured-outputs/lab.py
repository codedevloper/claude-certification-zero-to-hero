"""Lab 03: structured outputs with a JSON Schema.

Turns free-text facilities requests into JSON tickets. The schema is sent in
`output_config.format`, so the API constrains Claude's answer to that shape. The lab
then validates every ticket twice: against the schema (defence in depth) and against
business rules the schema cannot express. In live mode it also shows the SDK's
`client.messages.parse()` helper with a Pydantic model.

Run offline (default):   CLAUDE_LAB_MODE=mock python lab.py
Run against the API:      CLAUDE_LAB_MODE=live python lab.py   (uses API credits)
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "common"))
from claude_lab import get_client, MODEL, register_mock, text_of, banner  # noqa: E402
from claude_lab import MODE  # noqa: E402

DATA = Path(__file__).resolve().parent / "data"
SCHEMA = json.loads((DATA / "ticket_schema.json").read_text(encoding="utf-8"))
REQUESTS = json.loads((DATA / "maintenance_requests.json").read_text(encoding="utf-8"))

SYSTEM = (
    "You triage facilities maintenance requests for Contoso Health's office buildings. "
    "Classify each request and extract where the problem is. Use 'unknown' for any location "
    "field the request does not state. Write the summary as one sentence of at most 25 words. "
    "Set safety_risk to true for anything that could injure people (fire, smoke, electrical "
    "hazards, water on floors, structural damage); safety risks are always high or critical priority."
)


# --------------------------------------------------------------------------- validation
def validate(instance, schema: dict, path: str = "$") -> list[str]:
    """Validate the JSON Schema subset this lab uses. Standard library only.

    Supports: type (object, array, string, boolean, integer, number), properties, required,
    additionalProperties: false, enum and items. Returns a list of error strings (empty = valid).
    """
    errors: list[str] = []
    expected = schema.get("type")
    type_map = {"object": dict, "array": list, "string": str, "boolean": bool}
    if expected in type_map and not isinstance(instance, type_map[expected]):
        return [f"{path}: expected {expected}, got {type(instance).__name__}"]
    if expected in {"integer", "number"} and (isinstance(instance, bool) or not isinstance(instance, (int, float))):
        return [f"{path}: expected {expected}"]
    if "enum" in schema and instance not in schema["enum"]:
        errors.append(f"{path}: {instance!r} is not one of {schema['enum']}")
    if expected == "object":
        props = schema.get("properties", {})
        for key in schema.get("required", []):
            if key not in instance:
                errors.append(f"{path}: missing required property '{key}'")
        if schema.get("additionalProperties") is False:
            for key in instance:
                if key not in props:
                    errors.append(f"{path}: unexpected property '{key}'")
        for key, sub in props.items():
            if key in instance:
                errors.extend(validate(instance[key], sub, f"{path}.{key}"))
    if expected == "array" and "items" in schema:
        for i, item in enumerate(instance):
            errors.extend(validate(item, schema["items"], f"{path}[{i}]"))
    return errors


def business_rules(ticket: dict) -> list[str]:
    """Rules a JSON Schema cannot express. Schema-valid is not the same as correct."""
    problems = []
    if ticket["safety_risk"] and ticket["priority"] not in {"high", "critical"}:
        problems.append("safety risk flagged but priority is below high")
    if len(ticket["summary"].split()) > 25:
        problems.append("summary is longer than 25 words")
    if not ticket["affected_items"]:
        problems.append("no affected items listed")
    return problems


# --------------------------------------------------------------------------- mock responses
MOCK_TICKETS = {
    "MR-301": {
        "category": "plumbing", "priority": "high",
        "location": {"building": "Riverside", "floor": "2", "area": "staff kitchen"},
        "summary": "Hot water tap in the floor 2 staff kitchen is leaking onto the floor and getting worse.",
        "safety_risk": True, "affected_items": ["hot water tap", "kitchen floor"],
    },
    "MR-302": {
        "category": "lighting", "priority": "low",
        "location": {"building": "Harbour", "floor": "ground", "area": "meeting room B"},
        "summary": "Two ceiling lights in meeting room B flicker constantly.",
        "safety_risk": False, "affected_items": ["ceiling light", "ceiling light"],
    },
    # Deliberately schema-valid but wrong on a business rule, to show why the second check exists.
    "MR-303": {
        "category": "electrical", "priority": "medium",
        "location": {"building": "Riverside", "floor": "4", "area": "electrical cupboard by the lifts"},
        "summary": "Burning smell near the floor 4 electrical cupboard; area cleared, alarm not triggered.",
        "safety_risk": True, "affected_items": ["electrical cupboard"],
    },
}


@register_mock
def fake_structured_output(**request):
    fmt = (request.get("output_config") or {}).get("format")
    if not fmt:
        return None
    assert fmt["type"] == "json_schema" and "schema" in fmt, "output_config.format needs type and schema"
    content = request["messages"][-1]["content"]
    for request_id, ticket in MOCK_TICKETS.items():
        if request_id in content:
            return json.dumps(ticket)  # structured outputs return the JSON as one text block
    return None


# --------------------------------------------------------------------------- lab code
def extract_ticket(client, item: dict) -> dict:
    response = client.messages.create(
        model=MODEL,
        max_tokens=4096,
        system=SYSTEM,
        output_config={
            "effort": "low",
            "format": {"type": "json_schema", "schema": SCHEMA},
        },
        messages=[{
            "role": "user",
            "content": f"<request id=\"{item['request_id']}\">\n{item['text']}\n</request>",
        }],
    )
    # A refusal or a max_tokens cut-off can leave the JSON incomplete, so check first.
    if response.stop_reason != "end_turn":
        raise RuntimeError(f"{item['request_id']}: stop_reason={response.stop_reason}; output may be incomplete")
    return json.loads(text_of(response))


def parse_with_pydantic(client, item: dict) -> None:
    """Live mode only: the SDK helper that builds the schema from a Pydantic model and parses the reply."""
    from typing import List, Literal

    from pydantic import BaseModel  # installed with the anthropic SDK

    class Location(BaseModel):
        building: str
        floor: str
        area: str

    class MaintenanceTicket(BaseModel):
        category: Literal["plumbing", "electrical", "lighting", "heating_cooling", "furniture", "cleaning", "other"]
        priority: Literal["low", "medium", "high", "critical"]
        location: Location
        summary: str
        safety_risk: bool
        affected_items: List[str]

    response = client.messages.parse(
        model=MODEL,
        max_tokens=4096,
        system=SYSTEM,
        output_config={"effort": "low"},
        output_format=MaintenanceTicket,
        messages=[{"role": "user", "content": f"<request id=\"{item['request_id']}\">\n{item['text']}\n</request>"}],
    )
    if response.stop_reason != "end_turn":
        raise RuntimeError(f"parse(): stop_reason={response.stop_reason}")
    ticket = response.parsed_output  # a validated MaintenanceTicket instance
    print(f"  messages.parse() -> {type(ticket).__name__}(category={ticket.category!r}, "
          f"priority={ticket.priority!r}, safety_risk={ticket.safety_risk})")


def main() -> int:
    banner("Lab 03 - Structured outputs")
    client = get_client()
    results = []
    for item in REQUESTS:
        ticket = extract_ticket(client, item)
        schema_errors = validate(ticket, SCHEMA)
        rule_problems = [] if schema_errors else business_rules(ticket)
        route = "auto-queue" if not schema_errors and not rule_problems else "human review"
        results.append((item["request_id"], ticket, schema_errors, rule_problems, route))
        print(f"{item['request_id']}: {json.dumps(ticket)}")
        print(f"  schema: {'valid' if not schema_errors else schema_errors}")
        print(f"  business rules: {'ok' if not rule_problems else rule_problems}")
        print(f"  route: {route}\n")

    if MODE == "live":
        print("Live extra: the same extraction with client.messages.parse() and Pydantic")
        parse_with_pydantic(client, REQUESTS[0])
    else:
        print("Live extra skipped in mock mode: client.messages.parse() needs the real SDK and pydantic.")

    print("\nSelf-checks")
    bad_examples = {
        "missing field": {k: v for k, v in MOCK_TICKETS["MR-302"].items() if k != "priority"},
        "wrong enum": {**MOCK_TICKETS["MR-302"], "priority": "whenever"},
        "extra property": {**MOCK_TICKETS["MR-302"], "assignee": "Sam"},
        "wrong nested type": {**MOCK_TICKETS["MR-302"], "location": {"building": "Harbour", "floor": 0, "area": "x"}},
    }
    checks = {
        "every response parsed as JSON": len(results) == len(REQUESTS),
        "every response matches the schema": all(not r[2] for r in results),
        "validator rejects a missing required field": bool(validate(bad_examples["missing field"], SCHEMA)),
        "validator rejects an out-of-enum value": bool(validate(bad_examples["wrong enum"], SCHEMA)),
        "validator rejects an unexpected property": bool(validate(bad_examples["extra property"], SCHEMA)),
        "validator rejects a wrong nested type": bool(validate(bad_examples["wrong nested type"], SCHEMA)),
        "safety rule routes the burning-smell ticket correctly": any(
            r[0] == "MR-303" and (r[4] == "human review" or r[1]["priority"] in {"high", "critical"}) for r in results
        ),
    }
    if MODE == "mock":
        checks["mock MR-303 is caught by the business rule"] = next(r for r in results if r[0] == "MR-303")[4] == "human review"
    failed = [name for name, ok in checks.items() if not ok]
    for name, ok in checks.items():
        print(f"  [{'PASS' if ok else 'FAIL'}] {name}")
    if failed:
        return 1
    print("\nAll checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
