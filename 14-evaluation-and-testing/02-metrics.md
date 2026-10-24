# Metrics

> **Level:** Intermediate · **Time:** ~40 min · **Exam relevance:** CCAR-P D4 (4.1, 4.5, 4.6), CCAR-P D3 (3.3)

## In plain English

A metric is a number that tells you how well something is going. For an LLM application you need several: is the
answer right (quality), how long did it take (latency), what did it cost (cost), did it avoid harm (safety), and did
it resist misuse (security). Optimising only one of them usually damages another.

Choose metrics that a stakeholder would recognise as meaningful ("percentage of tickets routed to the right team"),
then add the technical metrics that explain them ("retrieval recall at 5").

## Why it matters

- CCAR-P-4.1 asks you to define evaluation metrics across accuracy, latency, cost, safety and security. CCAR-P-3.3
  asks you to evaluate accuracy and latency trade-offs and justify a configuration.
- The right metric changes the decision. Accuracy on an imbalanced dataset can look excellent while the rare, important
  class fails. Cost per request can look low while cost per *completed task* is high because of retries.
- Metrics are the shared language between engineers, product owners and risk teams.

## How it works

### Quality metrics

| Metric | Use for | How to compute | Watch out for |
|---|---|---|---|
| Accuracy | Classification with balanced classes | correct / total | Misleading on imbalanced data |
| Precision, recall, F1 | Detection, extraction, imbalanced classification | precision = TP / (TP + FP); recall = TP / (TP + FN); F1 = harmonic mean | Report per class, plus macro average |
| Exact match / normalised match | Short structured answers | Compare after normalising case, whitespace, number formats | Too rigid for free text |
| Field-level accuracy | Structured extraction | Correct fields / total fields, per field | One wrong field can matter more than many right ones |
| Rubric score | Open-ended text (summaries, emails) | Graded 1 to 5 against a written rubric by a calibrated judge or humans | Grader bias; see [grading methods](04-grading-methods.md) |
| Faithfulness / groundedness | RAG and summarisation | Share of claims supported by the provided sources | Needs claim-level checking |
| Citation accuracy | Grounded answers | Share of citations that actually support the cited claim | Citations can look right but point to the wrong passage |
| Task success rate | Agents | Share of tasks where the end state is correct (tests pass, record updated correctly) | Grade the end state, not the transcript |
| Pairwise win rate | Comparing two versions | Share of cases where judges prefer version B over A | Randomise order to avoid position bias |
| Consistency | Repeated runs | Agreement across N runs of the same input | Requires multiple trials |

Retrieval systems have their own metrics (recall at k, precision at k, mean reciprocal rank); see
[RAG evaluation](../11-rag-and-knowledge-systems/06-rag-evaluation.md).

### Latency metrics

| Metric | Meaning | Why it matters |
|---|---|---|
| Time to first token (TTFT) | Time until the first streamed output arrives | Perceived responsiveness in chat UIs |
| Output tokens per second | Generation speed after the first token | Long answers, code generation |
| End-to-end latency | Request start to final usable result, including tools and retries | What the user or calling system actually waits |
| Percentiles (p50, p95, p99) | Distribution, not just average | Tail latency drives user frustration and timeouts |
| Agent task duration and turns | Wall-clock and number of model calls per task | Agents can be slow because of many turns, not slow calls |

Measure latency on the final successful request separately from retries and backoff, so a variant that hit more rate
limits is not unfairly judged slower. Module 15 covers [latency optimisation](../15-production-operations/04-latency-optimisation.md).

### Cost metrics

Compute cost from the `usage` block of each response, not from estimates. The Messages API reports
`input_tokens`, `output_tokens`, `cache_creation_input_tokens` and `cache_read_input_tokens`. Total input tokens are
`input_tokens + cache_creation_input_tokens + cache_read_input_tokens`; each part is priced differently.

```text
cost = input_tokens        x input_price
     + cache_write_tokens  x input_price x write_multiplier   (1.25x for 5-minute TTL, 2x for 1-hour TTL)
     + cache_read_tokens   x cache_read_price
     + output_tokens       x output_price
```

Multipliers and prices are as of 2026-10-24; always check the [pricing page](https://platform.claude.com/docs/en/about-claude/pricing).

| Metric | Meaning |
|---|---|
| Cost per request | Easy to compute, often misleading for agents |
| Cost per completed task | Total cost of all calls (including retries, judge calls and tool loops) divided by successful tasks. The right unit for comparison |
| Cache hit rate | `cache_read_input_tokens` / total input tokens. A key efficiency signal |
| Tokens per task | Input and output separately; output usually costs more per token |
| Eval cost | What it costs to run the suite, including the judge model |

### Safety metrics

| Metric | Meaning |
|---|---|
| Harmful output rate | Share of outputs flagged by policy classifiers or reviewers on a safety test set |
| Correct refusal rate | Share of requests that *should* be refused that are refused |
| Over-refusal (false refusal) rate | Share of legitimate requests that are wrongly refused |
| Policy adherence | Share of outputs following domain rules (no medical diagnosis, required disclaimers) |
| Refusal stop-reason rate | Share of responses with `stop_reason: "refusal"` from model safety classifiers; track separately from capability failures |

Always pair correct-refusal rate with over-refusal rate. Either alone can be gamed by refusing everything or nothing.

### Security metrics

| Metric | Meaning |
|---|---|
| Attack success rate (ASR) | Share of adversarial test cases where the attack achieved its goal (wrong tool call, data leaked, policy bypassed) |
| Guardrail detection rate | Share of attacks caught by screens or filters |
| Guardrail false-positive rate | Share of benign inputs blocked |
| Unauthorised action rate | Tool calls denied by the policy enforcement point per 1,000 tasks (a production signal) |
| Data leakage rate | Outputs containing planted canary secrets or other-tenant data in tests |

[Safety and red-team evals](07-safety-and-red-team-evals.md) shows how to build these test sets.

### Choosing a metric set

Pick one or two **primary** metrics that define success, a small set of **guardrail** metrics that must not get worse,
and **diagnostic** metrics that explain changes.

| Use case | Primary | Guardrails | Diagnostic |
|---|---|---|---|
| Support ticket routing | Macro F1 across queues | p95 latency, cost per ticket, misroute rate for urgent class | Per-class confusion matrix |
| Policy Q&A (RAG) | Faithfulness and answer correctness | Citation accuracy, over-refusal rate | Retrieval recall at 5 |
| Coding agent | Task success (tests pass) | Cost per task, unauthorised action rate | Turns per task, tool error rate |
| Customer-facing chat | Resolution rate, rubric score | Harmful output rate, ASR, TTFT | Escalation rate |

## Example

A metrics module you can reuse in any harness. It computes per-class precision and recall, latency percentiles and
cost per completed task from recorded usage.

```python
"""metrics.py - quality, latency and cost metrics from recorded eval rows (standard library only)."""
from collections import Counter
from statistics import quantiles

# Example prices per million tokens as of 2026-10-24 for claude-sonnet-5-5; check the pricing page before use.
PRICES = {"claude-sonnet-5-5": {"input": 2.00, "output": 10.00, "cache_read": 0.10}}


def per_class_prf(rows: list[dict]) -> dict:
    labels = {r["expected"] for r in rows} | {r["predicted"] for r in rows}
    out = {}
    for label in sorted(labels):
        tp = sum(r["expected"] == label and r["predicted"] == label for r in rows)
        fp = sum(r["expected"] != label and r["predicted"] == label for r in rows)
        fn = sum(r["expected"] == label and r["predicted"] != label for r in rows)
        p = tp / (tp + fp) if tp + fp else 0.0
        r = tp / (tp + fn) if tp + fn else 0.0
        f1 = 2 * p * r / (p + r) if p + r else 0.0
        out[label] = {"precision": round(p, 3), "recall": round(r, 3), "f1": round(f1, 3), "support": tp + fn}
    out["macro_f1"] = round(sum(v["f1"] for v in out.values()) / len(labels), 3)
    return out


def latency_percentiles(latencies_s: list[float]) -> dict:
    q = quantiles(latencies_s, n=100, method="inclusive")
    return {"p50": round(q[49], 3), "p95": round(q[94], 3), "p99": round(q[98], 3)}


def row_cost(row: dict) -> float:
    p, u = PRICES[row["model"]], row["usage"]
    write_mult = 1.25  # 5-minute cache TTL
    return (u["input_tokens"] * p["input"]
            + u.get("cache_creation_input_tokens", 0) * p["input"] * write_mult
            + u.get("cache_read_input_tokens", 0) * p["cache_read"]
            + u["output_tokens"] * p["output"]) / 1_000_000


def cost_per_completed_task(rows: list[dict]) -> float:
    total = sum(row_cost(r) for r in rows)          # includes failed attempts and retries
    completed = sum(1 for r in rows if r["task_success"])
    return total / completed if completed else float("inf")


if __name__ == "__main__":
    rows = [
        {"expected": "billing", "predicted": "billing", "latency_s": 1.2, "task_success": True,
         "model": "claude-sonnet-5-5", "usage": {"input_tokens": 900, "output_tokens": 20,
                                                 "cache_read_input_tokens": 4000}},
        {"expected": "network", "predicted": "billing", "latency_s": 1.9, "task_success": False,
         "model": "claude-sonnet-5-5", "usage": {"input_tokens": 950, "output_tokens": 22,
                                                 "cache_read_input_tokens": 4000}},
        {"expected": "network", "predicted": "network", "latency_s": 1.4, "task_success": True,
         "model": "claude-sonnet-5-5", "usage": {"input_tokens": 880, "output_tokens": 18,
                                                 "cache_read_input_tokens": 4000}},
    ]
    print(per_class_prf(rows))
    print(latency_percentiles([r["latency_s"] for r in rows]))
    print(f"cost per completed task: ${cost_per_completed_task(rows):.6f}")
    print(Counter((r["expected"], r["predicted"]) for r in rows))  # confusion pairs
```

## Enterprise use case

*Contoso Health* compares two configurations of its benefits Q&A assistant: Claude Opus 5.5 at medium effort and
Claude Sonnet 5.5 at high effort, both with the same retrieval. On a 400-question eval:

| Metric | Opus 5.5, medium | Sonnet 5.5, high |
|---|---|---|
| Answer correctness (rubric 4 or 5) | 93% | 91% |
| Faithfulness | 98% | 97% |
| Over-refusal rate | 1.0% | 1.5% |
| p95 end-to-end latency | 6.1 s | 5.4 s |
| Cost per answered question | higher | lower |

These numbers are illustrative, not benchmarks. The point is the shape of the decision: the difference in correctness
is within the run-to-run variation the team measured (see [A/B testing](05-ab-testing-and-iteration.md)), so the
team chooses the cheaper, faster configuration and keeps the other as a fallback for complex questions.

## Common mistakes

- Reporting accuracy on imbalanced data without per-class numbers.
- Comparing cost per request instead of cost per completed task.
- Measuring average latency only.
- Counting refusals, truncations (`max_tokens`) and API errors as ordinary wrong answers. Track them separately.
- Choosing metrics nobody outside engineering understands.

## Security considerations

- Security and safety metrics belong in the same dashboard as quality metrics so trade-offs are visible.
- Track over-refusal alongside attack success rate; tightening a guardrail usually moves both.
- Metrics computed from production logs inherit the privacy constraints of those logs.

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| Accuracy high, users unhappy | Wrong metric or unrepresentative data | Add per-class and rubric metrics; sample real traffic |
| Cost metric jumps without traffic change | Cache hit rate fell (a prefix changed) | Check `cache_read_input_tokens`; see [cost optimisation](../15-production-operations/03-cost-optimisation.md) |
| Latency p95 much worse than p50 | Long outputs, agent loops or retries | Break down by turns and output length; stream |

## Check your understanding

1. Why is cost per completed task a better comparison unit than cost per request?
2. Which two safety metrics should always be reported together, and why?
3. How do you compute total input tokens from a Messages API `usage` block?
4. What is the difference between a primary metric and a guardrail metric?

<details>
<summary>Answers</summary>

1. It includes retries, failed attempts, judge calls and multi-turn loops, and reflects the cost of actually achieving
   the outcome; a cheap request that often fails is not cheap.
2. Correct refusal rate and over-refusal rate; optimising one alone can be achieved trivially by refusing everything
   or nothing.
3. `input_tokens + cache_creation_input_tokens + cache_read_input_tokens`.
4. A primary metric defines success and is what you try to improve; a guardrail metric must not get worse beyond a set
   tolerance when you make changes.

</details>

## Further reading

- Anthropic: [Define your success criteria](https://platform.claude.com/docs/en/test-and-evaluate/define-success)
- Anthropic: [Pricing](https://platform.claude.com/docs/en/about-claude/pricing) and
  [prompt caching](https://platform.claude.com/docs/en/build-with-claude/prompt-caching)
- In this repository: [token counting and cost](../06-claude-api/08-token-counting-and-cost.md),
  [RAG evaluation](../11-rag-and-knowledge-systems/06-rag-evaluation.md),
  [Lab 16](../19-hands-on-labs/lab-16-evaluation-framework/README.md)

<!-- page-nav:start -->
---

[← Previous: Why Evaluate](01-why-evaluate.md) · [Module overview](README.md) · [Next: Building Eval Datasets →](03-building-eval-datasets.md)
<!-- page-nav:end -->
