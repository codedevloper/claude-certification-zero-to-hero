# Token Counting and Cost

> **Level:** Intermediate · **Time:** ~45 min · **Exam relevance:** CCAO-F D3 · CCAR-P D2, D4

## In plain English

Claude's usage is measured and billed in **tokens**, small chunks of text (see
[tokens and tokenisation](../01-ai-and-llm-fundamentals/04-tokens-and-tokenisation.md)). Every request has:

- **Input tokens**: everything you send (system prompt, tools, conversation, documents, images).
- **Output tokens**: everything Claude generates, including thinking.

Output tokens cost several times more than input tokens. Some input can be cheaper (cache reads), some more expensive
(cache writes), and asynchronous batch work is half price.

To manage cost you need to **measure before and after**: count tokens before you send, read the `usage` object after,
and multiply by current prices.

## Why it matters

- Cost per task decides whether a use case is viable at scale. A design that costs a few cents per request can cost
  thousands per month at volume.
- Most savings come from a handful of levers: caching, batching, effort, model choice and context hygiene. You need
  numbers to know which lever matters for your workload.
- Matching model choice to cost, speed and quality is a Foundations objective (CCAO-F-3.3); optimising token usage and
  cost-performance is a Professional objective (CCAR-P-2.4, CCAR-P-4.5).

## How it works

### Counting tokens before you send

The token-counting endpoint, `POST /v1/messages/count_tokens`, accepts the same `model`, `system`, `messages`, `tools`
and document or image blocks as a real request and returns `input_tokens`. Counts are **model-specific**, because
different model generations use different tokenizers, so always pass the model you will use.

```python
import anthropic

client = anthropic.Anthropic()  # API key from ANTHROPIC_API_KEY

count = client.messages.count_tokens(
    model="claude-opus-5-5",
    system="You are a contracts analyst.",
    messages=[{"role": "user", "content": open("data/msa.txt", encoding="utf-8").read()}],
)
print(count.input_tokens)
```

```bash
curl https://api.anthropic.com/v1/messages/count_tokens \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -H "content-type: application/json" \
  -d '{"model": "claude-opus-5-5",
       "messages": [{"role": "user", "content": "How many tokens is this sentence?"}]}'
```

Facts (as of 2026-10-24; see the [token counting docs](https://platform.claude.com/docs/en/build-with-claude/token-counting)):

- Token counting is free to call but has its own rate limits.
- The count is an estimate that can differ slightly from the billed amount.
- **Do not use other vendors' tokenizers** (for example `tiktoken`) to estimate Claude tokens; they can be wrong by a
  large margin, especially for code and non-English text.
- Newer Claude models use a newer tokenizer that can produce more tokens for the same text than older models. Re-count
  when you change model.

Uses: checking that a document fits the context window before sending, budgeting a batch job, and context reviews
(see [what is context engineering](../04-context-engineering/01-what-is-context-engineering.md)).

### Reading usage after a request

Every response has a `usage` object:

| Field | Meaning |
|---|---|
| `input_tokens` | Input after the last cache breakpoint, billed at the base input price |
| `cache_creation_input_tokens` | Input written to the cache (billed at the cache-write rate) |
| `cache_read_input_tokens` | Input served from the cache (billed at the cache-read rate) |
| `output_tokens` | Generated tokens, including thinking |
| `server_tool_use` | Counts of server-side tool calls such as web searches, which may be billed per use |
| `iterations` | Present with some features (for example compaction): per-step usage that you sum for the true total |

Total input = `input_tokens + cache_creation_input_tokens + cache_read_input_tokens`. A common mistake is to look only
at `input_tokens` and conclude a long prompt was tiny.

### Prices and multipliers (as of 2026-10-24)

Always confirm on the [pricing page](https://platform.claude.com/docs/en/about-claude/pricing); prices change and
partner platforms price separately.

| Model | Input (USD per million tokens) | Output (USD per million tokens) | Context window |
|---|---:|---:|---|
| `claude-fable-5-1` | 10.00 | 50.00 | 1M |
| `claude-opus-5-5` | 4.00 | 20.00 | 1M |
| `claude-sonnet-5-5` | 2.00 | 10.00 | 1M |
| `claude-haiku-5-5` | 0.10 (prompts up to 100K tokens) | 0.50 (prompts up to 100K tokens) | 1M |

Haiku 5.5's rates rise for prompts above 100K tokens (to 0.50 input and 2.50 output per million, as of 2026-10-24).

| Modifier | Multiplier on the base price |
|---|---|
| Cache write, 5-minute TTL | 1.25x input |
| Cache write, 1-hour TTL | 2x input |
| Cache read | 0.1x input on most models; 0.05x on Claude Opus 5.5; 0.025x on Claude Fable 5.1 |
| Message Batches API | 0.5x input and output |
| Fast mode (research preview, selected Opus models, Claude API only) | Premium pricing, about 2x |

Images and PDF pages are billed as input tokens; server tools such as web search can add per-use charges; and code
execution can carry container-time charges.

### The main cost levers, in a sensible order

1. **Free wins first.** Cache stable prefixes; remove unused tools, duplicated instructions and boilerplate; keep tool
   outputs concise; set `max_tokens` sensibly; avoid unnecessary retries.
2. **Batch** anything that can wait (50% off).
3. **Tune effort per route.** Lower effort means less thinking and fewer tool calls.
4. **Choose the model per route.** Test whether a smaller model, or the same model at lower effort, meets the quality
   bar. Measure cost per *completed task*, not per request: a cheaper request that needs more retries or turns may cost
   more overall.
5. **Re-architect** only if needed: retrieval instead of whole documents, sub-agents on cheaper models, output-length
   limits.

Caches are per model, so a design that routes one conversation across several models gives up cache reuse; factor that
into multi-model cascades.

### Estimating cost

```text
cost = (input_tokens x input_price
        + cache_creation_tokens x input_price x write_multiplier
        + cache_read_tokens x input_price x read_multiplier
        + output_tokens x output_price)          [ x 0.5 if batched ]
```

Worked example (illustrative): an assistant on Claude Sonnet 5.5 handles 20,000 requests a day. Each has a
6,000-token cached prefix, 1,500 uncached input tokens and 700 output tokens, with continuous traffic so almost every
request reads the cache.

| Component | Daily tokens | Rate (USD per million) | Daily cost (USD) |
|---|---:|---:|---:|
| Cache reads | 20,000 x 6,000 = 120M | 2.00 x 0.1 = 0.20 | 24.00 |
| Uncached input | 20,000 x 1,500 = 30M | 2.00 | 60.00 |
| Output | 20,000 x 700 = 14M | 10.00 | 140.00 |
| **Total** | | | **about 224** |

Without caching, the prefix would cost 120M x 2.00 / 1M = USD 240 a day instead of 24. Notice that output dominates the
remaining cost, so shorter answers or lower effort are the next levers to test.

## Example

A small cost tracker for *Acme Logistics* (fictional) that records usage per route and computes cost from a price
table kept in configuration, not hardcoded throughout the code.

```python
from collections import defaultdict
from dataclasses import dataclass

import anthropic

client = anthropic.Anthropic()  # API key from ANTHROPIC_API_KEY

# Prices in USD per million tokens, as of 2026-10-24. Load from config in real code and review regularly.
PRICES = {
    "claude-opus-5-5":   {"in": 4.00, "out": 20.00, "read": 0.05},
    "claude-sonnet-5-5": {"in": 2.00, "out": 10.00, "read": 0.10},
}
WRITE_5M = 1.25


@dataclass
class RouteTotals:
    requests: int = 0
    cost_usd: float = 0.0


totals: dict[str, RouteTotals] = defaultdict(RouteTotals)


def record(route: str, msg: anthropic.types.Message, batched: bool = False) -> float:
    p = PRICES[msg.model]
    u = msg.usage
    cost = (
        u.input_tokens * p["in"]
        + (u.cache_creation_input_tokens or 0) * p["in"] * WRITE_5M
        + (u.cache_read_input_tokens or 0) * p["in"] * p["read"]
        + u.output_tokens * p["out"]
    ) / 1_000_000
    if batched:
        cost *= 0.5
    totals[route].requests += 1
    totals[route].cost_usd += cost
    return cost


question = "Which depots exceeded their exception threshold last week?"
estimate = client.messages.count_tokens(model="claude-sonnet-5-5",
                                        messages=[{"role": "user", "content": question}])
print("estimated input tokens:", estimate.input_tokens)

msg = client.messages.create(
    model="claude-sonnet-5-5",
    max_tokens=1000,
    output_config={"effort": "low"},
    messages=[{"role": "user", "content": question}],
)
print(f"this call: USD {record('depot-qa', msg):.5f}")
for route, t in totals.items():
    print(route, t.requests, f"USD {t.cost_usd:.4f}")
```

> **Cost:** requires API credits (live mode). Token counting itself is free but rate-limited.

For organisation-wide reporting, the Console shows usage and cost, and an Admin API offers usage and cost reports
(Admin API keys are separate from normal API keys).

## Enterprise use case

*Northwind Lending* (fictional) launched a broker-support assistant on its most capable model at high effort. Usage
grew faster than planned and the monthly bill tripled. The FinOps and engineering teams used per-route usage logs to
build a cost profile:

| Finding | Action | Effect |
|---|---|---|
| 70% of input was a static product guide re-sent uncached | Cached it as a stable prefix | Input cost fell sharply |
| Simple FAQ questions ran at high effort | Routed them at low effort after an eval showed no quality loss | Output and thinking tokens fell |
| Nightly broker-email summaries ran in real time | Moved to the Batches API | Half price for that workload |
| Long answers were often truncated by users anyway | Asked for answers under 150 words | Fewer output tokens |

They kept the most capable model for complex eligibility questions, where evals showed it mattered. Cost per resolved
broker question became the KPI reported to the steering group (see
[business value and ROI](../13-enterprise-ai-architecture/08-business-value-and-roi.md)).

## Common mistakes

- **Estimating tokens with the wrong tokenizer.** Use `count_tokens` with the target model.
- **Reading only `input_tokens`.** Add cache writes and reads to see the true prompt size.
- **Ignoring thinking in output costs.** Thinking is billed as output, even when not displayed.
- **Hardcoding prices across the codebase.** Keep a dated price table in configuration.
- **Optimising per request instead of per task.** Cheaper calls that need more retries or turns can cost more.
- **Switching models mid-conversation to save money**, losing all cached context.
- **Forgetting partner-platform pricing differences.**

## Security considerations

- **Denial of wallet.** Attackers can drive up costs with long inputs, many requests or prompts that trigger long
  outputs. Apply per-user quotas, input size limits, `max_tokens` caps and workspace spend limits.
- **Cost anomalies as security signals.** A sudden spike can indicate a leaked key or abuse; alert on it.
- **Usage logs** are generally safe to share widely; prompt and output logs are not. Keep them separate.
- **Admin API keys** that read cost data are highly privileged; store and rotate them carefully.

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| Bill higher than estimates | Thinking tokens, cache writes or images not counted | Recalculate from `usage`; include all fields |
| `count_tokens` differs from billed input | Counting is an estimate; system additions for tools | Treat as approximate; reconcile from `usage` |
| Cost jumped after a model upgrade | Different tokenizer or default effort | Re-count tokens; set effort explicitly |
| Cache savings smaller than expected | Prefix changing, or traffic gaps longer than the TTL | See [prompt caching](../04-context-engineering/03-prompt-caching.md) |
| Rate-limited on token counting | High-volume counting calls | Count once per template, or sample |

## Check your understanding

1. Why must you pass the same model to `count_tokens` that you will use for the request?
2. How do you compute the total input tokens of a request that used prompt caching?
3. Rank these levers by how you would usually try them: model change, caching, batching, effort tuning.
4. In the worked example, which component dominates cost after caching, and what would you test next?

<details>
<summary>Answers</summary>

1. Token counts depend on the model's tokenizer, which differs between model generations.
2. `input_tokens + cache_creation_input_tokens + cache_read_input_tokens`.
3. Typically caching and other free wins first, then batching for work that can wait, then effort tuning, then model
   changes, each validated against your quality bar.
4. Output tokens. Test shorter answer instructions, lower effort, or a smaller model for simple questions, measuring
   quality on an eval set.

</details>

## Further reading

- [Token counting](https://platform.claude.com/docs/en/build-with-claude/token-counting) (Anthropic docs)
- [Pricing](https://platform.claude.com/docs/en/about-claude/pricing) (Anthropic docs)
- [Models overview](https://platform.claude.com/docs/en/about-claude/models/overview) (Anthropic docs)
- [Cost optimisation](../15-production-operations/03-cost-optimisation.md) and [model selection](../05-claude-products-and-models/03-model-selection.md) in this repository
- [Lab 17 — Cost optimisation](../19-hands-on-labs/lab-17-cost-optimisation/README.md)
- Next module: [Module 07 — Tool Use and Function Calling](../07-tool-use-and-function-calling/README.md)
