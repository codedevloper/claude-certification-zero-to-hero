"""Lab 17: Cost optimisation.

Estimate what Claude traffic costs from `usage` objects, then compare caching, batch and
model-routing scenarios for a synthetic workload and work out where prompt caching breaks even.

Usage (from the repository root):

    CLAUDE_LAB_MODE=mock python 19-hands-on-labs/lab-17-cost-optimisation/lab.py   # offline, free
    CLAUDE_LAB_MODE=live python 19-hands-on-labs/lab-17-cost-optimisation/lab.py   # real API, uses credits

Pricing comes from data/pricing.json (dated). Confirm it against the live pricing page before
using any number in this lab for a real budget.
"""
from __future__ import annotations

import json
import os
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "common"))

from claude_lab import (  # noqa: E402
    MODE,
    MODEL,
    Message,
    TextBlock,
    Usage,
    banner,
    get_client,
    register_mock,
    text_of,
)

DATA = HERE / "data"
OUT_DIR = Path(os.environ.get("LAB_OUTPUT_DIR") or tempfile.gettempdir()) / "claude-labs" / "lab-17"
TIER_RANK = {"simple": 0, "medium": 1, "complex": 2}

_results: list[tuple[str, bool]] = []


def check(label: str, condition: bool) -> None:
    _results.append((label, bool(condition)))
    print(f"  [{'PASS' if condition else 'FAIL'}] {label}")


def load_json(name: str) -> dict:
    return json.loads((DATA / name).read_text(encoding="utf-8"))


# --------------------------------------------------------------------------- cost model
def _field(usage, name: str) -> int:
    """Read a usage field from an SDK object or a plain dict; missing or None counts as 0."""
    value = usage.get(name) if isinstance(usage, dict) else getattr(usage, name, 0)
    return int(value or 0)


def rates_for(pricing: dict, model: str, prompt_tokens: int) -> dict:
    """Per-MTok rates for a model, switching to long-prompt rates where the model has them."""
    entry = pricing["models"][model]
    threshold = entry.get("long_prompt_threshold_tokens")
    if threshold and prompt_tokens > threshold:
        return {**entry, **entry["long_prompt"]}
    return entry


def cost_from_usage(pricing: dict, model: str, usage, *, batch: bool = False, ttl: str = "5m") -> dict:
    """Turn one response's usage into dollars, split by the four token meters."""
    inp = _field(usage, "input_tokens")
    out = _field(usage, "output_tokens")
    cw = _field(usage, "cache_creation_input_tokens")
    cr = _field(usage, "cache_read_input_tokens")
    rates = rates_for(pricing, model, inp + cw + cr)
    write_mult = pricing["multipliers"]["cache_write_1h" if ttl == "1h" else "cache_write_5m"]
    parts = {
        "input": inp * rates["input"] / 1e6,
        "cache_write": cw * rates["input"] * write_mult / 1e6,
        "cache_read": cr * rates["cache_read"] / 1e6,
        "output": out * rates["output"] / 1e6,
    }
    factor = pricing["multipliers"]["batch_discount"] if batch else 1.0
    parts = {k: v * factor for k, v in parts.items()}
    parts["total"] = sum(parts.values())
    return parts


def expected_usage(prefix: int, suffix: int, output: int, *, cached: bool, hit_rate: float, min_prefix: int) -> dict:
    """Average usage for one request whose first `prefix` tokens are shared with other requests."""
    if not cached or prefix < min_prefix:
        return {"input_tokens": prefix + suffix, "output_tokens": output}
    return {
        "input_tokens": suffix,
        "cache_creation_input_tokens": prefix * (1 - hit_rate),
        "cache_read_input_tokens": prefix * hit_rate,
        "output_tokens": output,
    }


# --------------------------------------------------------------------------- routing
COMPLEX_WORDS = ("analyse", "analyze", "compare", "assess", "evaluate", "recommend", "trade-off",
                 "design", "review", "risk")
MEDIUM_WORDS = ("draft", "summarise", "summarize", "rewrite", "explain", "write", "turn these", "reply")


def route(prompt: str) -> str:
    """A deliberately simple keyword router. Real routers are measured, not trusted."""
    p = prompt.lower()
    if any(w in p for w in COMPLEX_WORDS):
        return "complex"
    if any(w in p for w in MEDIUM_WORDS) or len(p) > 400:
        return "medium"
    return "simple"


def routing_matrix(samples: list[dict]) -> tuple[float, dict]:
    """Return accuracy and, for each true tier, the share of prompts routed to each tier."""
    matrix = {t: {r: 0 for r in TIER_RANK} for t in TIER_RANK}
    correct = 0
    for s in samples:
        got = route(s["prompt"])
        matrix[s["tier"]][got] += 1
        correct += got == s["tier"]
    shares = {t: {r: n / max(1, sum(row.values())) for r, n in row.items()} for t, row in matrix.items()}
    return correct / len(samples), {"counts": matrix, "shares": shares}


# --------------------------------------------------------------------------- scenarios
def per_request_cost(pricing, workload, rt, model, *, cached, batch) -> float:
    a = workload["assumptions"]
    hit = a["batch_cache_hit_rate"] if batch else a["interactive_cache_hit_rate"]
    usage = expected_usage(workload["shared_prefix_tokens"], rt["suffix_input_tokens"], rt["output_tokens"],
                           cached=cached, hit_rate=hit, min_prefix=pricing["min_cacheable_prefix_tokens"])
    return cost_from_usage(pricing, model, usage, batch=batch, ttl=a["cache_ttl"])["total"]


def monthly_cost(pricing, workload, *, cached=False, use_batch=False, routing=None) -> float:
    """routing: None (everything on the default model) or a shares dict {true_tier: {routed_tier: share}}."""
    days = workload["days_per_month"]
    tier_models = workload["tier_models"]
    total = 0.0
    for rt in workload["request_types"]:
        batch = use_batch and not rt["latency_sensitive"]
        volume = rt["daily_requests"] * days
        if routing is None:
            total += volume * per_request_cost(pricing, workload, rt, MODEL_FOR_BASELINE, cached=cached, batch=batch)
            continue
        true_tier = rt["true_tier"]
        for routed, share in routing[true_tier].items():
            if share == 0:
                continue
            cost = per_request_cost(pricing, workload, rt, tier_models[routed], cached=cached, batch=batch)
            if TIER_RANK[routed] < TIER_RANK[true_tier]:
                # Under-powered model misses the quality bar: pay for the failed try, then escalate.
                cost += per_request_cost(pricing, workload, rt, tier_models[true_tier], cached=cached, batch=batch)
            total += volume * share * cost
    return total


MODEL_FOR_BASELINE = "claude-opus-5-5"


def break_even(pricing: dict, model: str, prefix: int, ttl: str, n_max: int = 6) -> tuple[int | None, list]:
    """Smallest number of requests sharing `prefix` tokens at which caching beats no caching."""
    rows, first = [], None
    min_prefix = pricing["min_cacheable_prefix_tokens"]
    for n in range(1, n_max + 1):
        plain = n * cost_from_usage(pricing, model, {"input_tokens": prefix})["total"]
        if prefix < min_prefix:
            cached = plain  # below the minimum, the marker is silently ignored
        else:
            cached = cost_from_usage(pricing, model, {"cache_creation_input_tokens": prefix}, ttl=ttl)["total"]
            cached += (n - 1) * cost_from_usage(pricing, model, {"cache_read_input_tokens": prefix})["total"]
        rows.append((n, plain, cached))
        if first is None and cached < plain:
            first = n
    return first, rows


# --------------------------------------------------------------------------- live/mock demo
KB_MARKER = "Northwind Lending support handbook"
_seen_prefixes: set[int] = set()
_CANNED = [
    ("friday", "The support desk closes at 18:00 on Fridays (handbook section 1)."),
    ("public holiday", "Yes. The hardship hotline opens 10:00 to 14:00 on public holidays (handbook section 1)."),
    ("recording", "Call recordings are kept for 18 months and then deleted automatically (handbook section 6)."),
]


@register_mock
def fake_handbook_answer(**request):
    system = request.get("system")
    if not isinstance(system, list) or not any(KB_MARKER in b.get("text", "") for b in system):
        return None
    prefix_text = "".join(b["text"] for b in system)
    prefix_tokens = len(prefix_text) // 4
    first = hash(prefix_text) not in _seen_prefixes
    _seen_prefixes.add(hash(prefix_text))
    question = request["messages"][-1]["content"]
    answer = next((a for k, a in _CANNED if k in question.lower()), "I could not find that in the handbook.")
    usage = Usage(
        input_tokens=len(question) // 4 + 8,
        output_tokens=len(answer) // 4,
        cache_creation_input_tokens=prefix_tokens if first else 0,
        cache_read_input_tokens=0 if first else prefix_tokens,
    )
    return Message(content=[TextBlock(answer)], model=request["model"], usage=usage)


def run_demo(pricing: dict) -> list[dict]:
    print("Part 1: measure real usage with a cached handbook prefix\n")
    if MODEL not in pricing["models"]:
        raise SystemExit(f"No price for {MODEL} in data/pricing.json; add it or unset CLAUDE_LAB_MODEL.")
    client = get_client()
    kb = (DATA / "northwind_kb.md").read_text(encoding="utf-8")
    system = [
        {"type": "text", "text": "You answer questions from Northwind Lending staff using only the handbook below. "
                                  "Cite the section number. If the handbook does not say, reply that you cannot find it."},
        {"type": "text", "text": kb, "cache_control": {"type": "ephemeral"}},
    ]
    questions = [
        "What time does the support desk close on Friday?",
        "Is the hardship hotline open on a public holiday?",
        "How long do we keep call recordings?",
    ]
    estimate = client.messages.count_tokens(model=MODEL, system=system,
                                            messages=[{"role": "user", "content": questions[0]}])
    print(f"  count_tokens estimate for request 1: {estimate.input_tokens} input tokens"
          f" (about ${estimate.input_tokens * pricing['models'][MODEL]['input'] / 1e6:.5f} uncached)\n")
    rows = []
    for i, q in enumerate(questions, 1):
        resp = client.messages.create(
            model=MODEL, max_tokens=1024, system=system,
            messages=[{"role": "user", "content": q}],
            output_config={"effort": "low"},
        )
        if resp.stop_reason != "end_turn":
            print(f"  request {i}: stop_reason={resp.stop_reason}; skipping answer")
            rows.append({"stop_reason": resp.stop_reason})
            continue
        u = resp.usage
        actual = cost_from_usage(pricing, MODEL, u)
        prompt_total = _field(u, "input_tokens") + _field(u, "cache_creation_input_tokens") + _field(u, "cache_read_input_tokens")
        uncached = cost_from_usage(pricing, MODEL, {"input_tokens": prompt_total, "output_tokens": _field(u, "output_tokens")})
        print(f"  Q{i}: {q}\n      A: {text_of(resp)[:110]}")
        print(f"      usage: input={_field(u, 'input_tokens')} cache_write={_field(u, 'cache_creation_input_tokens')} "
              f"cache_read={_field(u, 'cache_read_input_tokens')} output={_field(u, 'output_tokens')}")
        print(f"      cost ${actual['total']:.6f} vs ${uncached['total']:.6f} without caching\n")
        rows.append({"stop_reason": resp.stop_reason, "usage": {k: _field(u, k) for k in (
            "input_tokens", "cache_creation_input_tokens", "cache_read_input_tokens", "output_tokens")},
            "cost": actual["total"], "uncached_cost": uncached["total"]})
    return rows


# --------------------------------------------------------------------------- main
def main() -> int:
    banner("Lab 17: Cost optimisation")
    pricing = load_json("pricing.json")
    workload = load_json("workload.json")
    samples = load_json("routing_samples.json")["samples"]
    print(f"Pricing as of {pricing['as_of']} ({pricing['pricing_page']})\n")

    demo = run_demo(pricing)

    print("Part 2: monthly scenarios for the synthetic Northwind workload\n")
    accuracy, matrix = routing_matrix(samples)
    oracle = {t: {r: 1.0 if r == t else 0.0 for r in TIER_RANK} for t in TIER_RANK}
    scenarios = {
        "A baseline (Opus, no cache, no batch)": monthly_cost(pricing, workload),
        "B + prompt caching": monthly_cost(pricing, workload, cached=True),
        "C + batch for non-urgent work": monthly_cost(pricing, workload, use_batch=True),
        "D caching + batch": monthly_cost(pricing, workload, cached=True, use_batch=True),
        "E D + keyword router (with escalations)": monthly_cost(pricing, workload, cached=True, use_batch=True,
                                                                routing=matrix["shares"]),
        "F D + perfect router (upper bound)": monthly_cost(pricing, workload, cached=True, use_batch=True,
                                                           routing=oracle),
    }
    base = scenarios["A baseline (Opus, no cache, no batch)"]
    print(f"  {'scenario':<42}{'monthly USD':>14}{'vs A':>9}")
    for name, cost in scenarios.items():
        print(f"  {name:<42}{cost:>14,.2f}{(cost - base) / base:>+9.1%}")
    print(f"\n  router accuracy on {len(samples)} labelled prompts: {accuracy:.1%}")
    for t, row in matrix["counts"].items():
        print(f"    true {t:<8} -> routed {row}")

    print("\nPart 3: prompt-caching break-even (Opus 5.5, shared prefix)\n")
    be = {}
    for prefix, ttl in ((6000, "5m"), (6000, "1h"), (400, "5m")):
        n, rows = break_even(pricing, "claude-opus-5-5", prefix, ttl)
        be[f"{prefix}-{ttl}"] = n
        label = f"{prefix}-token prefix, {ttl} TTL"
        print(f"  {label}: " + ", ".join(f"N={r[0]} ${r[2]:.4f} vs ${r[1]:.4f}" for r in rows[:3])
              + (f"  -> break-even at N={n}" if n else "  -> no break-even: prefix is below the cacheable minimum"))

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    report = {"pricing_as_of": pricing["as_of"], "mode": MODE, "demo": demo,
              "scenarios_monthly_usd": scenarios, "router_accuracy": accuracy, "break_even": be}
    (OUT_DIR / "cost_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"\n  report written to {OUT_DIR / 'cost_report.json'}")

    print("\nSelf-checks")
    one_m = cost_from_usage(pricing, "claude-opus-5-5", {"input_tokens": 1_000_000})["total"]
    check("1M Opus input tokens cost 4.00 USD", abs(one_m - 4.0) < 1e-9)
    check("batch halves the same request",
          abs(cost_from_usage(pricing, "claude-opus-5-5", {"input_tokens": 1_000_000}, batch=True)["total"] - 2.0) < 1e-9)
    check("5-minute cache write is 1.25x input",
          abs(cost_from_usage(pricing, "claude-opus-5-5", {"cache_creation_input_tokens": 1_000_000})["total"] - 5.0) < 1e-9)
    long_rate = rates_for(pricing, "claude-haiku-5-5", 150_000)["input"]
    check("Haiku switches to long-prompt rates above 100K prompt tokens", long_rate == 0.50)
    check("5m TTL breaks even at 2 requests, 1h TTL at 3", be["6000-5m"] == 2 and be["6000-1h"] == 3)
    check("a prefix below the minimum never benefits from caching", be["400-5m"] is None)
    check("router accuracy is at least 85%", accuracy >= 0.85)
    s = list(scenarios.values())
    check("caching and batch each cut cost; together they cut more", s[1] < s[0] and s[2] < s[0] and s[3] < min(s[1], s[2]))
    check("misrouting costs money: perfect router beats keyword router", s[5] <= s[4])
    ok_demo = [r for r in demo if r.get("stop_reason") == "end_turn"]
    check("every demo request ended with stop_reason end_turn", len(ok_demo) == len(demo))
    if MODE == "mock":
        check("requests 2 and 3 read the handbook from cache",
              all(r["usage"]["cache_read_input_tokens"] > 0 for r in ok_demo[1:]))
        check("cached requests cost less than uncached ones", all(r["cost"] < r["uncached_cost"] for r in ok_demo[1:]))
    else:
        reads = [r["usage"]["cache_read_input_tokens"] for r in ok_demo[1:]]
        print(f"  [INFO] live cache reads on requests 2-3: {reads} (0 means the prefix did not cache; see Troubleshooting)")

    failed = [label for label, ok in _results if not ok]
    print(f"\n{len(_results) - len(failed)}/{len(_results)} checks passed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
