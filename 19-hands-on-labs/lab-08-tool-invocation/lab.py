"""Lab 08: a manual tool-use loop with safe, validated tools.

Claude gets three read-only tools for a fictional parcel carrier. The loop:
  1. sends the conversation and tool definitions (tool_choice auto, strict schemas);
  2. on stop_reason == "tool_use", validates and runs every tool_use block;
  3. returns ALL tool_result blocks in ONE user message (parallel tool use), marking
     failures with is_error so Claude can recover;
  4. repeats until end_turn, with an iteration cap.

Run offline (default):   CLAUDE_LAB_MODE=mock python lab.py
Run against the API:      CLAUDE_LAB_MODE=live python lab.py   (uses API credits)
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "common"))
from claude_lab import get_client, MODEL, register_mock, text_of, banner  # noqa: E402
from claude_lab import MODE, TextBlock, ToolUseBlock  # noqa: E402

DATA = Path(__file__).resolve().parent / "data"
SHIPMENTS = json.loads((DATA / "shipments.json").read_text(encoding="utf-8"))
DEPOTS = json.loads((DATA / "depots.json").read_text(encoding="utf-8"))
MAX_ITERATIONS = 6
MAX_RESULT_CHARS = 2000
TRACKING_ID = re.compile(r"^AL-\d{5}$")


# --------------------------------------------------------------------------- tools
class ToolInputError(ValueError):
    """Bad input from the model. The message is safe to show to Claude."""


def get_shipment_status(tracking_id: str) -> dict:
    if not TRACKING_ID.match(tracking_id):
        raise ToolInputError("tracking_id must look like AL- followed by 5 digits, e.g. AL-12345. Ask the customer to check it.")
    if tracking_id not in SHIPMENTS:
        raise ToolInputError(f"No shipment found with tracking_id {tracking_id}.")
    return {"tracking_id": tracking_id, **SHIPMENTS[tracking_id]}


def convert_weight(value: float, from_unit: str, to_unit: str) -> dict:
    if not 0 < value <= 10_000:
        raise ToolInputError("value must be greater than 0 and at most 10000.")
    kg = value * 0.45359237 if from_unit == "lb" else value
    result = kg / 0.45359237 if to_unit == "lb" else kg
    return {"value": round(result, 2), "unit": to_unit}


def get_depot_hours(depot_code: str) -> dict:
    if depot_code not in DEPOTS:
        raise ToolInputError(f"Unknown depot_code {depot_code!r}. Valid codes: {', '.join(sorted(DEPOTS))}.")
    return {"depot_code": depot_code, **DEPOTS[depot_code]}


def _schema(properties: dict, required: list[str]) -> dict:
    return {"type": "object", "properties": properties, "required": required, "additionalProperties": False}


TOOLS = [
    {
        "name": "get_shipment_status",
        "description": "Look up the delivery status, estimated arrival window, weight in pounds and destination depot "
                       "of one Acme Logistics shipment. Read-only. Call once per tracking ID; independent lookups can "
                       "be made in parallel.",
        "strict": True,
        "input_schema": _schema({"tracking_id": {"type": "string", "description": "Format AL-12345"}}, ["tracking_id"]),
    },
    {
        "name": "convert_weight",
        "description": "Convert a weight between kilograms and pounds. Pure calculation, no side effects.",
        "strict": True,
        "input_schema": _schema({
            "value": {"type": "number", "description": "Weight to convert, greater than 0"},
            "from_unit": {"type": "string", "enum": ["kg", "lb"]},
            "to_unit": {"type": "string", "enum": ["kg", "lb"]},
        }, ["value", "from_unit", "to_unit"]),
    },
    {
        "name": "get_depot_hours",
        "description": "Get the opening hours of an Acme Logistics depot by its three-letter code (BRS Bristol, "
                       "MAN Manchester, LDS Leeds). Read-only.",
        "strict": True,
        "input_schema": _schema({"depot_code": {"type": "string", "enum": sorted(DEPOTS)}}, ["depot_code"]),
    },
]
IMPLEMENTATIONS = {"get_shipment_status": get_shipment_status, "convert_weight": convert_weight,
                   "get_depot_hours": get_depot_hours}


def validate_input(schema: dict, data) -> list[str]:
    """Defence in depth: check the model's arguments against the tool schema before running anything."""
    if not isinstance(data, dict):
        return ["input must be an object"]
    errors = [f"missing '{k}'" for k in schema["required"] if k not in data]
    errors += [f"unexpected '{k}'" for k in data if k not in schema["properties"]]
    for key, rule in schema["properties"].items():
        if key not in data:
            continue
        value = data[key]
        if rule["type"] == "string" and not isinstance(value, str):
            errors.append(f"'{key}' must be a string")
        if rule["type"] == "number" and (isinstance(value, bool) or not isinstance(value, (int, float))):
            errors.append(f"'{key}' must be a number")
        if "enum" in rule and value not in rule["enum"]:
            errors.append(f"'{key}' must be one of {rule['enum']}")
    return errors


STATS = {"executed": 0, "rejected_by_validation": 0}


def run_tool(block) -> dict:
    """Execute one tool_use block and return its tool_result block. Never raises."""
    def result(content: str, is_error: bool = False) -> dict:
        out = {"type": "tool_result", "tool_use_id": block.id, "content": content[:MAX_RESULT_CHARS]}
        if is_error:
            out["is_error"] = True
        return out

    tool = next((t for t in TOOLS if t["name"] == block.name), None)
    if tool is None:
        return result(f"Unknown tool {block.name!r}.", is_error=True)
    problems = validate_input(tool["input_schema"], block.input)
    if problems:
        STATS["rejected_by_validation"] += 1
        return result("Invalid input: " + "; ".join(problems), is_error=True)
    try:
        STATS["executed"] += 1
        return result(json.dumps(IMPLEMENTATIONS[block.name](**block.input)))
    except ToolInputError as exc:
        return result(str(exc), is_error=True)
    except Exception:  # never leak stack traces or internals to the model
        return result("The tool failed unexpectedly. Try again later or continue without it.", is_error=True)


# --------------------------------------------------------------------------- mock responses
def _results(message: dict) -> list[dict]:
    return [b for b in message["content"] if isinstance(b, dict) and b.get("type") == "tool_result"]


@register_mock
def fake_tool_user(**request):
    if not request.get("tools"):
        return None
    msgs = request["messages"]
    turn = sum(1 for m in msgs if m["role"] == "assistant")
    if turn == 0:  # three independent lookups at once
        return [
            TextBlock("I'll look up both parcels and the Bristol depot hours."),
            ToolUseBlock("get_shipment_status", {"tracking_id": "AL-58213"}),
            ToolUseBlock("get_shipment_status", {"tracking_id": "AL-9999"}),
            ToolUseBlock("get_depot_hours", {"depot_code": "BRS"}),
        ]
    if turn == 1:  # depends on the first result: convert the weight it returned
        results = _results(msgs[-1])
        assert len(results) == 3, "all three results must arrive in one user message"
        shipment = json.loads(next(r["content"] for r in results if "out_for_delivery" in r["content"]))
        return [ToolUseBlock("convert_weight", {"value": shipment["weight_lb"], "from_unit": "lb", "to_unit": "kg"})]
    kg = json.loads(_results(msgs[-1])[0]["content"])["value"]
    return (
        f"Here's what I found:\n- AL-58213 is out for delivery, arriving 2026-11-05 between 14:00 and 16:00. "
        f"It weighs 18.5 lb, which is about {kg} kg.\n- AL-9999 isn't a valid tracking number (they look like "
        "AL- followed by five digits). Could you check it on your receipt?\n- The Bristol depot is open on "
        "Saturday from 08:00 to 13:00."
    )


# --------------------------------------------------------------------------- the loop
def run_conversation(client, user_text: str) -> tuple[str, list[dict], list[str]]:
    messages = [{"role": "user", "content": user_text}]
    trace = []
    for iteration in range(1, MAX_ITERATIONS + 1):
        response = client.messages.create(
            model=MODEL,
            max_tokens=4096,
            output_config={"effort": "medium"},
            system="You are Acme Logistics' parcel assistant. Use the tools for facts; never guess tracking data.",
            tools=TOOLS,
            tool_choice={"type": "auto"},  # forced tool use is not supported on Opus 5.5, Sonnet 5.5, Fable 5.1 and Mythos 5.1
            messages=messages,
        )
        messages.append({"role": "assistant", "content": response.content})
        calls = [b for b in response.content if getattr(b, "type", "") == "tool_use"]
        trace.append(f"iteration {iteration}: stop_reason={response.stop_reason}, tool calls={[c.name for c in calls]}")
        print(f"  {trace[-1]}")

        if response.stop_reason == "end_turn":
            return text_of(response), messages, trace
        if response.stop_reason in {"max_tokens", "refusal"}:
            raise RuntimeError(f"stopped early: {response.stop_reason}; do not run partial tool calls")
        if response.stop_reason != "tool_use":
            raise RuntimeError(f"unexpected stop_reason {response.stop_reason}")

        results = [run_tool(call) for call in calls]
        for call, res in zip(calls, results):
            flag = " is_error" if res.get("is_error") else ""
            print(f"    {call.name}({json.dumps(call.input)}) ->{flag} {res['content'][:90]}")
        messages.append({"role": "user", "content": results})  # every result, one message
    raise RuntimeError(f"no final answer after {MAX_ITERATIONS} iterations")


def main() -> int:
    banner("Lab 08 - Tool invocation")
    client = get_client()
    question = ("Can you check parcels AL-58213 and AL-9999? Also, what does AL-58213 weigh in kg, "
                "and is the Bristol depot open on Saturday?")
    print(f"User: {question}\n")
    answer, messages, trace = run_conversation(client, question)
    print(f"\nClaude:\n{answer}\n")

    print("Self-checks")
    uses = [b.id for m in messages if m["role"] == "assistant" for b in m["content"] if getattr(b, "type", "") == "tool_use"]
    results = [r for m in messages if m["role"] == "user" and isinstance(m["content"], list) for r in m["content"]]
    result_msgs = [m for m in messages if m["role"] == "user" and isinstance(m["content"], list)]
    checks = {
        "loop ended with end_turn within the iteration cap": len(trace) <= MAX_ITERATIONS and "end_turn" in trace[-1],
        "every tool_use id got exactly one tool_result": sorted(uses) == sorted(r["tool_use_id"] for r in results),
        "each user turn after a tool call holds only tool_result blocks": all(
            all(r.get("type") == "tool_result" for r in m["content"]) for m in result_msgs),
        "validator rejects missing, extra, wrong-type and out-of-enum inputs": all([
            validate_input(TOOLS[1]["input_schema"], {"value": 1, "from_unit": "lb"}),
            validate_input(TOOLS[1]["input_schema"], {"value": 1, "from_unit": "lb", "to_unit": "kg", "x": 1}),
            validate_input(TOOLS[1]["input_schema"], {"value": "1", "from_unit": "lb", "to_unit": "kg"}),
            validate_input(TOOLS[1]["input_schema"], {"value": 1, "from_unit": "stone", "to_unit": "kg"}),
        ]),
        "unknown tools return is_error instead of crashing": run_tool(ToolUseBlock("delete_shipment", {}))["is_error"],
        "weight conversion is correct": convert_weight(18.5, "lb", "kg")["value"] == 8.39,
    }
    if MODE == "mock":
        checks["three independent calls ran in parallel in one turn"] = "tool calls=['get_shipment_status', 'get_shipment_status', 'get_depot_hours']" in trace[0]
        checks["malformed tracking ID came back as is_error"] = any(r.get("is_error") and "AL- followed by 5 digits" in r["content"] for r in results)
        checks["final answer uses the converted weight"] = "8.39 kg" in answer
    failed = [n for n, ok in checks.items() if not ok]
    for name, ok in checks.items():
        print(f"  [{'PASS' if ok else 'FAIL'}] {name}")
    if failed:
        return 1
    print("\nAll checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
