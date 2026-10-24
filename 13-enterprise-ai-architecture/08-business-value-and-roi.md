# Business Value and ROI

> **Level:** Advanced · **Time:** ~45 min · **Exam relevance:** CCAR-P 1.6, 6.3, 4.5, CCAO-F 4.5

## In plain English

Every Claude project is an investment. Someone spends money and people's time now, expecting a return later. Return on investment (ROI) is
the discipline of saying, in advance and in numbers, what that return should be, and then checking whether it arrived.

Value from AI comes in a few forms: doing the same work faster or cheaper (efficiency), letting people do more or better work
(productivity), doing things that were not possible before (transformation), and keeping service fast and dependable (performance against
service levels). Cost comes from model usage, the surrounding platform, the people who build and run it, and the risk you take on.

A business case is simply these numbers written down honestly, with ranges, assumptions and a plan to measure.

## Why it matters

- Funding decisions are made on business cases. A vague "AI will make us more efficient" loses to a specific, measurable proposal.
- The cost structure of Claude solutions is unusual: model cost is variable per request and often small next to labour value, while
  engineering, evaluation and operations costs are fixed and easy to underestimate.
- Architecture choices change the economics. Prompt caching, batching, model tiering and effort settings can move model cost by large
  factors; the wrong pattern (an agent where a single call would do) can multiply it.
- CCAR-P 1.6 asks you to align solutions to business value, including efficiency, transformation, productivity, cost and SLAs.

## How it works

### Value levers

| Lever | What changes | Typical metrics | Measurement approach |
|---|---|---|---|
| Efficiency | Less time or cost per unit of existing work | Handling time, cost per case, backlog age | Before/after timing on matched samples |
| Productivity | More or better output per person | Cases per person-day, first-contact resolution, quality scores | Cohort comparison during pilot |
| Transformation | New capability or service model | New revenue, new channel, decisions made earlier | Business KPIs agreed with the sponsor |
| Quality and risk | Fewer errors, better compliance | Error rate, rework, audit findings | Sampled review against a rubric |
| Performance (SLAs) | Faster, more consistent service | Response time, SLA attainment, availability | Service metrics and SLO dashboards |
| Experience | Customer or employee satisfaction | Satisfaction scores, attrition, adoption | Surveys, usage analytics |

Pick two or three primary levers per solution and measure them properly. A business case that claims every lever is usually not believed.

### Cost model

**Total cost of ownership (TCO)** for a Claude solution has five parts:

1. **Model usage**: input, cached input, output tokens and any tool or platform fees, per request, times volume.
2. **Platform**: gateway, vector store, queues, observability, hosting for your services.
3. **Build**: discovery, design, engineering, evaluation datasets, security review.
4. **Run**: on-call, prompt and evaluation maintenance, model upgrades, user support.
5. **Human review**: the time reviewers still spend, which is part of the solution's cost, not a free safety net.

**Model cost per request** is:

```text
cost_per_call = (uncached_input_tokens * input_price
               + cached_input_tokens   * cache_read_price
               + cache_write_tokens    * cache_write_price
               + output_tokens         * output_price) / 1,000,000

monthly_model_cost = cost_per_call * calls_per_request * requests_per_month
```

Agent loops resend the conversation on each turn, so `calls_per_request` and input tokens grow with the number of steps; measure them from
logs rather than guessing. Multi-agent systems multiply this again.

As of 2026-10-24, list prices per million tokens on the Claude API were (check the
[pricing page](https://platform.claude.com/docs/en/about-claude/pricing) before using them):

| Model | Input | Output | Notes |
|---|---|---|---|
| `claude-opus-5-5` | $4.00 | $20.00 | Default high-capability model |
| `claude-sonnet-5-5` | $2.00 | $10.00 | Balanced speed and capability |
| `claude-haiku-5-5` | $0.10 | $0.50 | For prompts up to 100K tokens; higher beyond |

Cache reads are billed at a small fraction of the input price, and the Message Batches API is billed at 50% of standard prices. Cloud
platforms may price differently; Amazon Bedrock and Vertex AI are partner-operated with separate pricing.

### Cost optimisation levers (in the order to try them)

1. **Prompt caching**: put stable content first; verify with `usage.cache_read_input_tokens`.
2. **Batch** non-interactive work.
3. **Trim inputs**: send only relevant retrieved chunks; avoid resending large tool results.
4. **Right-size output**: ask for concise formats; cap `max_tokens` sensibly.
5. **Effort setting**: lower `output_config.effort` where quality holds on your evaluation set.
6. **Model tiering**: a smaller model for easy routes, measured against the simpler alternative of one model at lower effort.
7. **Pattern**: replace an unnecessary agent with a workflow.

Judge cost per **completed task**, not per request: a cheaper call that needs more retries or more human rework is not cheaper.
[Cost optimisation](../15-production-operations/03-cost-optimisation.md) covers these levers in depth.

### ROI, payback and sensitivity

```text
net_monthly_benefit = monthly_value - monthly_model_cost - monthly_run_cost
payback_months      = one_off_build_cost / net_monthly_benefit
ROI_12_months       = (12 * net_monthly_benefit - one_off_build_cost) / one_off_build_cost
```

Two adjustments keep the case honest:

- **Realisation factor**: saved minutes do not automatically become money. Apply a factor (for example 50–70%) for how much saved time is
  actually redeployed, and say what it will be redeployed to.
- **Adoption ramp**: usage grows over months; model the first quarter at partial adoption.

Always show a **sensitivity table**: what happens to payback if time saved is half the pilot result, or volume doubles, or the model cost
doubles. Decision-makers trust ranges more than single numbers.

### SLAs as part of value

Service levels are value too. If the business promise is "broker queries answered within 4 business hours", the architecture must support
it: latency budgets per step, capacity for peak volume within rate limits, a fallback when the model endpoint is degraded, and quality SLOs.
State the SLOs in the business case and cost the redundancy they require.

## Example

A small calculator you can adapt. It uses only the standard library, synthetic inputs, and the list prices above.

```python
"""Business-case calculator for a Claude assistant (synthetic inputs, standard library only)."""
from dataclasses import dataclass

# Prices in USD per million tokens, as of 2026-10-24. Re-check the official pricing page before use.
PRICES = {
    "claude-opus-5-5":   {"input": 4.00, "output": 20.00, "cache_read": 0.20},
    "claude-sonnet-5-5": {"input": 2.00, "output": 10.00, "cache_read": 0.10},
}

@dataclass
class Workload:
    requests_per_month: int
    calls_per_request: float      # follow-ups, retries, multi-step chains
    uncached_input_tokens: int
    cached_input_tokens: int      # stable prefix read from cache
    output_tokens: int
    model: str

def model_cost_per_month(w: Workload) -> float:
    p = PRICES[w.model]
    per_call = (
        w.uncached_input_tokens * p["input"]
        + w.cached_input_tokens * p["cache_read"]
        + w.output_tokens * p["output"]
    ) / 1_000_000
    return per_call * w.calls_per_request * w.requests_per_month

def labour_value_per_month(requests: int, minutes_before: float, minutes_after: float,
                           loaded_rate_per_hour: float, realisation: float) -> float:
    hours_saved = requests * (minutes_before - minutes_after) / 60
    return hours_saved * loaded_rate_per_hour * realisation

if __name__ == "__main__":
    w = Workload(requests_per_month=12_000, calls_per_request=1.5,
                 uncached_input_tokens=2_000, cached_input_tokens=4_000,
                 output_tokens=800, model="claude-sonnet-5-5")
    model = model_cost_per_month(w)
    value = labour_value_per_month(12_000, minutes_before=14, minutes_after=8,
                                   loaded_rate_per_hour=48, realisation=0.6)
    run_cost = 6_000          # platform, vector store, monitoring, support time
    build_cost = 90_000       # one-off delivery cost
    net = value - model - run_cost
    print(f"model cost / month:    ${model:,.2f}")
    print(f"labour value / month:  ${value:,.2f}")
    print(f"net benefit / month:   ${net:,.2f}")
    print(f"payback (months):      {build_cost / net:.1f}")
    print(f"12-month ROI:          {(12 * net - build_cost) / build_cost:.0%}")
    w_opus = Workload(**{**w.__dict__, "model": "claude-opus-5-5"})
    print(f"same workload on Opus: ${model_cost_per_month(w_opus):,.2f} / month")
```

Output with these synthetic inputs (cache-write cost ignored for simplicity):

```text
model cost / month:    $223.20
labour value / month:  $34,560.00
net benefit / month:   $28,336.80
payback (months):      3.2
12-month ROI:          278%
same workload on Opus: $446.40 / month
```

The lesson in the numbers is common in practice: model cost is small next to labour value and run cost. That makes the **quality** of the
saved time, the realisation factor and the fixed run cost the numbers worth arguing about, and it means choosing a cheaper model to save a
few hundred dollars is only worthwhile if quality holds on your evaluation set.

## Enterprise use case

*Northwind Lending* built the business case for its broker-query assistant using the calculator above, with inputs from a four-week pilot.

| Scenario | Minutes saved per query | Realisation | Payback |
|---|---|---|---|
| Pilot result | 6 | 60% | about 3 months |
| Conservative (half the time saving) | 3 | 60% | about 8 months, because the fixed run cost now eats a third of the value |
| Volume doubles in year 2 | 6 | 60% | under 2 months |

The conservative row changed the conversation. It showed that the fixed run cost, not the model, was the risk to the case, so the team
reduced run cost by reusing the shared AI gateway and vector store from another project instead of building their own. The sponsor approved
the project with a commitment to report time saved monthly against the pilot figure, and an agreed stop condition if the six-month average fell
below four minutes.

## Common mistakes

- **Counting all saved time as money.** Without a realisation factor and a plan for the freed capacity, the benefit is theoretical.
- **Ignoring fixed costs.** Evaluation maintenance, model upgrades and on-call are real, recurring costs.
- **Estimating tokens instead of measuring them.** Agents in particular use far more tokens than intuition suggests; measure from pilot logs.
- **Optimising model cost first.** It is often the smallest line; quality and adoption usually matter more.
- **No stop condition.** A business case should say what result would cause you to stop or redesign.
- **Fabricated benchmarks.** Never cite industry statistics you cannot source; use your own baseline and pilot data.

## Security considerations

- Include the cost of security controls and reviews (red-teaming, threat modelling, logging storage) in TCO. Leaving them out makes secure
  designs look expensive later.
- Spend is a security signal. Budget caps and anomaly alerts per application detect abuse (for example, a leaked key or a runaway agent).
- Value claims that depend on removing human review must be weighed against the cost of errors; consult the risk owner, and see
  [human oversight](../12-ai-security/13-human-oversight.md).

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| Actual model cost far above estimate | Agent loops, retries, low cache hit rate | Measure calls per task and `cache_read_input_tokens`; fix cache prefix; add step budgets |
| Time savings do not show up in team metrics | Freed time not redeployed, or measurement mismatch | Agree the redeployment plan and measure the same KPI as the baseline |
| Sponsor doubts the numbers | Single-point estimate, no sources | Show ranges, sensitivity, pilot data and assumptions |
| Costs grow faster than usage | Prompt growth over time, larger retrieved context | Review prompt length monthly; trim retrieval; re-run the cost model |

## Check your understanding

1. Name the five parts of TCO for a Claude solution.
2. Why does an agent's `calls_per_request` matter more than for a single-call design?
3. What is a realisation factor and why apply it?
4. In the example, which input most affects payback, and why?
5. Give three cost optimisation levers to try before switching to a smaller model.

<details>
<summary>Answers</summary>

1. Model usage, platform, build, run, and human review.
2. Agent loops call the model once per step and resend the growing conversation each time, so input tokens and calls multiply with the
   number of steps; a single call has a fixed, predictable cost.
3. The share of saved time that is actually converted into value (redeployed work, avoided hiring). It prevents overstating benefit,
   because saved minutes do not automatically become money.
4. The minutes saved per query (with the realisation factor), because labour value is far larger than model cost; halving the time saving
   more than doubles the payback period, because the fixed run cost stays the same while the value halves.
5. Any three of: prompt caching, batch processing, trimming inputs, right-sizing outputs, lowering effort, simplifying the pattern.

</details>

## Further reading

- Claude docs: [Pricing](https://platform.claude.com/docs/en/about-claude/pricing),
  [Prompt caching](https://platform.claude.com/docs/en/build-with-claude/prompt-caching),
  [Batch processing](https://platform.claude.com/docs/en/build-with-claude/batch-processing)
- In this repository: [token counting and cost](../06-claude-api/08-token-counting-and-cost.md),
  [cost optimisation](../15-production-operations/03-cost-optimisation.md), [model selection](../05-claude-products-and-models/03-model-selection.md),
  [stakeholder communication](06-stakeholder-communication.md)
- Practice: [Lab 17: Cost optimisation](../19-hands-on-labs/lab-17-cost-optimisation/README.md)

<!-- page-nav:start -->
---

[← Previous: Architecture Decision Records](07-architecture-decision-records.md) · [Module overview](README.md) · [Next: Lifecycle Management →](09-lifecycle-management.md)
<!-- page-nav:end -->
