"""One place that talks to Claude: build the request, check stop_reason, parse and validate JSON.

Rules followed here (current models, as of 2026-10-24):
- structured output through `output_config.format` (no prefill, no forced tool_choice);
- no `temperature`, `top_p` or `top_k`;
- `stop_reason` is checked before `content` is used;
- the parsed JSON is validated again locally, because model output is untrusted input.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any

from claude_lab import MODEL, text_of

from .schemas import validate

# USD per million tokens, from the claude-api skill pricing table (as of 2026-10-24).
# Check https://platform.claude.com/docs/en/about-claude/pricing before relying on them.
PRICES_PER_MTOK = {
    "claude-opus-5-5": (4.00, 20.00),
    "claude-sonnet-5-5": (2.00, 10.00),
    "claude-haiku-5-5": (0.10, 0.50),
}


class ModelOutputError(RuntimeError):
    """Raised when a response cannot be used: refusal, truncation, bad JSON or schema mismatch."""


@dataclass
class UsageTally:
    calls: int = 0
    input_tokens: int = 0
    output_tokens: int = 0
    by_model: dict[str, list[int]] = field(default_factory=dict)

    def add(self, model: str, usage: Any) -> None:
        self.calls += 1
        inp = int(getattr(usage, "input_tokens", 0) or 0)
        out = int(getattr(usage, "output_tokens", 0) or 0)
        self.input_tokens += inp
        self.output_tokens += out
        totals = self.by_model.setdefault(model, [0, 0])
        totals[0] += inp
        totals[1] += out

    def estimated_cost_usd(self) -> float:
        cost = 0.0
        for model, (inp, out) in self.by_model.items():
            price_in, price_out = PRICES_PER_MTOK.get(model, PRICES_PER_MTOK["claude-opus-5-5"])
            cost += inp / 1e6 * price_in + out / 1e6 * price_out
        return cost


def call_structured(
    client: Any,
    *,
    system: str,
    user: str,
    schema: dict[str, Any],
    max_tokens: int = 4000,
    model: str = MODEL,
    effort: str = "low",
    tally: UsageTally | None = None,
) -> dict[str, Any]:
    """Send one request with a JSON schema and return the validated object."""
    response = client.messages.create(
        model=model,
        max_tokens=max_tokens,
        system=system,
        messages=[{"role": "user", "content": user}],
        output_config={"effort": effort, "format": {"type": "json_schema", "schema": schema}},
    )
    if tally is not None:
        tally.add(model, response.usage)
    if response.stop_reason == "refusal":
        raise ModelOutputError("the model declined this request (stop_reason=refusal)")
    if response.stop_reason == "max_tokens":
        raise ModelOutputError("response was cut off at max_tokens; raise the limit or shrink the chunk")
    if response.stop_reason != "end_turn":
        raise ModelOutputError(f"unexpected stop_reason: {response.stop_reason}")
    try:
        data = json.loads(text_of(response))
    except json.JSONDecodeError as exc:
        raise ModelOutputError(f"response was not valid JSON: {exc}") from exc
    errors = validate(data, schema)
    if errors:
        raise ModelOutputError("response failed schema validation: " + "; ".join(errors[:5]))
    return data
