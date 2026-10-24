"""Run-wide budget: model calls, tool calls and tokens. Exhaustion stops the run cleanly."""
from __future__ import annotations

from dataclasses import dataclass


class BudgetExceeded(RuntimeError):
    pass


@dataclass
class Budget:
    max_model_calls: int = 30
    max_tool_calls: int = 60
    max_tokens: int = 250_000
    model_calls: int = 0
    tool_calls: int = 0
    tokens: int = 0

    def before_model_call(self) -> None:
        if self.model_calls >= self.max_model_calls:
            raise BudgetExceeded(f"model-call budget of {self.max_model_calls} reached")
        if self.tokens >= self.max_tokens:
            raise BudgetExceeded(f"token budget of {self.max_tokens} reached")
        self.model_calls += 1

    def charge_tokens(self, usage) -> None:
        self.tokens += int(getattr(usage, "input_tokens", 0) or 0) + int(getattr(usage, "output_tokens", 0) or 0)

    def before_tool_call(self) -> None:
        if self.tool_calls >= self.max_tool_calls:
            raise BudgetExceeded(f"tool-call budget of {self.max_tool_calls} reached")
        self.tool_calls += 1

    def snapshot(self) -> dict:
        return {"model_calls": f"{self.model_calls}/{self.max_model_calls}",
                "tool_calls": f"{self.tool_calls}/{self.max_tool_calls}",
                "tokens": f"{self.tokens}/{self.max_tokens}"}
