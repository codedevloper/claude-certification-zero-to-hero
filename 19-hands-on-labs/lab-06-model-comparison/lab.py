"""Lab 06: compare Opus, Sonnet and Haiku on the same tasks.

Runs three graded tasks (classification, extraction, multi-constraint reasoning) on
several model/effort configurations, then builds a table of accuracy, latency, tokens
and cost computed from each response's `usage`. Finally it picks the cheapest
configuration that meets a quality bar.

Pricing comes from the claude-api skill's model table (cached 2026-10-06), checked on
2026-10-24. Prices change: confirm them on the pricing page before you rely on them.

Run offline (default):   CLAUDE_LAB_MODE=mock python lab.py
Run against the API:      CLAUDE_LAB_MODE=live python lab.py   (uses API credits)
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "common"))
from claude_lab import get_client, MODEL, register_mock, text_of, banner  # noqa: E402
from claude_lab import MODE, Message, TextBlock, Usage  # noqa: E402

DATA = Path(__file__).resolve().parent / "data"
TASKS = json.loads((DATA / "tasks.json").read_text(encoding="utf-8"))

PRICING_AS_OF = "2026-10-24"
# US$ per million tokens: (input, output). Haiku 5.5's rate applies to prompts up to 100K tokens.
PRICES = {
    "claude-opus-5-5": (4.00, 20.00),
    "claude-sonnet-5-5": (2.00, 10.00),
    "claude-haiku-5-5": (0.10, 0.50),
}
# Each configuration is a model plus an effort level. Effort is a second cost lever inside one model.
CONFIGS = [
    ("claude-opus-5-5", "medium"),
    ("claude-opus-5-5", "low"),
    ("claude-sonnet-5-5", "medium"),
    ("claude-haiku-5-5", "medium"),
]
QUALITY_BAR = 1.0  # fraction of tasks that must be correct


# --------------------------------------------------------------------------- mock responses
# Illustrative only. These canned numbers let the pipeline run offline; they are not benchmarks.
MOCK_OUTPUT_TOKENS = {  # thinking + answer tokens per task, by configuration
    ("claude-opus-5-5", "medium"): {"classify": 60, "extract": 110, "reason": 420},
    ("claude-opus-5-5", "low"): {"classify": 25, "extract": 60, "reason": 210},
    ("claude-sonnet-5-5", "medium"): {"classify": 70, "extract": 120, "reason": 480},
    ("claude-haiku-5-5", "medium"): {"classify": 50, "extract": 90, "reason": 260},
}
MOCK_TOKENS_PER_SECOND = {"claude-opus-5-5": 70, "claude-sonnet-5-5": 95, "claude-haiku-5-5": 190}
MOCK_ANSWERS = {
    "classify": {"category": "billing"},
    "extract": {"invoice_number": "INV-2026-0419", "total_eur": 1562.5, "due_date": "2026-11-20"},
    "reason": {"option": "A", "reason": "B departs at 09:00 but loading only finishes at 10:00, so A is the cheapest feasible option."},
}
MOCK_WRONG = {  # a plausible slip: the smallest model misses the loading constraint
    ("claude-haiku-5-5", "reason"): {"option": "B", "reason": "B is the cheapest option and arrives before Thursday 17:00."},
}


@register_mock
def fake_comparison(**request):
    fmt = (request.get("output_config") or {}).get("format")
    if not fmt:
        return None
    task = next((t for t in TASKS if t["prompt"] == request["messages"][-1]["content"]), None)
    if task is None:
        return None
    model, effort = request["model"], request["output_config"].get("effort", "medium")
    answer = MOCK_WRONG.get((model, task["id"]), MOCK_ANSWERS[task["id"]])
    usage = Usage(input_tokens=max(1, len(task["prompt"]) // 4) + 40,
                  output_tokens=MOCK_OUTPUT_TOKENS[(model, effort)][task["id"]])
    return Message(content=[TextBlock(json.dumps(answer))], model=model, usage=usage)


# --------------------------------------------------------------------------- lab code
def grade(answer: dict, expected: dict) -> bool:
    for key, value in expected.items():
        got = answer.get(key)
        if isinstance(value, float):
            if not isinstance(got, (int, float)) or abs(got - value) > 0.005:
                return False
        elif got != value:
            return False
    return True


def cost_usd(model: str, usage) -> float:
    in_price, out_price = PRICES[model]
    return (usage.input_tokens * in_price + usage.output_tokens * out_price) / 1_000_000


def run_task(client, model: str, effort: str, task: dict) -> dict:
    start = time.perf_counter()
    response = client.messages.create(
        model=model,
        max_tokens=4096,
        output_config={"effort": effort, "format": {"type": "json_schema", "schema": task["schema"]}},
        messages=[{"role": "user", "content": task["prompt"]}],
    )
    elapsed = time.perf_counter() - start
    if MODE != "live":  # the mock answers instantly, so estimate generation time from tokens
        elapsed = 0.35 + response.usage.output_tokens / MOCK_TOKENS_PER_SECOND[model]
    if response.stop_reason != "end_turn":
        return {"correct": False, "latency": elapsed, "usage": response.usage, "note": response.stop_reason}
    answer = json.loads(text_of(response))
    return {"correct": grade(answer, task["expected"]), "latency": elapsed, "usage": response.usage, "answer": answer}


def main() -> int:
    banner("Lab 06 - Model comparison")
    client = get_client()
    rows = []
    for model, effort in CONFIGS:
        results = {task["id"]: run_task(client, model, effort, task) for task in TASKS}
        accuracy = sum(r["correct"] for r in results.values()) / len(TASKS)
        in_tok = sum(r["usage"].input_tokens for r in results.values())
        out_tok = sum(r["usage"].output_tokens for r in results.values())
        cost = sum(cost_usd(model, r["usage"]) for r in results.values())
        latency = sum(r["latency"] for r in results.values()) / len(TASKS)
        misses = [tid for tid, r in results.items() if not r["correct"]]
        rows.append({"model": model, "effort": effort, "accuracy": accuracy, "latency": latency,
                     "in": in_tok, "out": out_tok, "cost": cost, "misses": misses})

    latency_label = "avg latency (s)" if MODE == "live" else "avg latency (s, simulated)"
    print(f"{'model':<19} {'effort':<7} {'accuracy':>8}  {latency_label:>26}  {'in tok':>6}  {'out tok':>7}  "
          f"{'cost/run $':>10}  {'per 1k runs $':>13}  misses")
    for r in rows:
        print(f"{r['model']:<19} {r['effort']:<7} {r['accuracy']:>8.0%}  {r['latency']:>26.2f}  {r['in']:>6}  "
              f"{r['out']:>7}  {r['cost']:>10.5f}  {r['cost'] * 1000:>13.2f}  {', '.join(r['misses']) or '-'}")
    print(f"\nPrices: US$/MTok input/output as of {PRICING_AS_OF}: "
          + "; ".join(f"{m} {p[0]:.2f}/{p[1]:.2f}" for m, p in PRICES.items()))

    qualifying = [r for r in rows if r["accuracy"] >= QUALITY_BAR]
    pick = min(qualifying, key=lambda r: r["cost"]) if qualifying else None
    if pick:
        print(f"Cheapest configuration meeting the {QUALITY_BAR:.0%} quality bar: {pick['model']} at effort={pick['effort']}")
    else:
        print("No configuration met the quality bar; improve the prompt or raise effort before choosing on cost.")

    print("\nSelf-checks")
    by_key = {(r["model"], r["effort"]): r for r in rows}
    checks = {
        "every configuration ran every task": len(rows) == len(CONFIGS),
        "cost is computed from usage and is positive": all(r["cost"] > 0 for r in rows),
        "grader accepts a correct answer and rejects a wrong one": grade({"option": "A"}, {"option": "A"})
        and not grade({"option": "B"}, {"option": "A"}),
        "grader compares numbers with a tolerance": grade({"total_eur": 1562.50}, {"total_eur": 1562.5})
        and not grade({"total_eur": "1562.5"}, {"total_eur": 1562.5}),
        "lower effort used fewer output tokens on the same model": by_key[("claude-opus-5-5", "low")]["out"]
        < by_key[("claude-opus-5-5", "medium")]["out"],
        "a recommendation was made only from configurations that met the bar": pick is None or pick["accuracy"] >= QUALITY_BAR,
    }
    live_advisory = {"lower effort used fewer output tokens on the same model"}
    failed = False
    for name, ok in checks.items():
        if ok:
            print(f"  [PASS] {name}")
        elif MODE == "live" and name in live_advisory:
            print(f"  [WARN] {name} (small samples are noisy)")
        else:
            print(f"  [FAIL] {name}")
            failed = True
    if failed:
        return 1
    print("\nAll checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
