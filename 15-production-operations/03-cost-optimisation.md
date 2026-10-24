# Cost Optimisation

> **Level:** Intermediate · **Time:** ~45 min · **Exam relevance:** CCAR-P D4 (4.5), CCAR-P D2 (2.4, 2.5), CCAR-P D1 (1.6), CCAO-F D3 (3.3)

## In plain English

You pay for Claude by the token: input tokens you send, output tokens it generates, and discounted or premium rates
for cached input. Cost optimisation means getting the same quality for fewer, cheaper tokens. The biggest savings
usually come from not paying full price for the same text over and over (prompt caching), from doing non-urgent work
in bulk at a discount (batch processing), and from choosing the right model and effort level for each task.

Optimise against a quality bar. A cheaper configuration that fails more often, or needs more retries, is not cheaper.

## Why it matters

- CCAR-P-4.5 asks you to optimise token usage, latency and cost-performance; CCAR-P-2.5 covers reuse through caching,
  modular prompts and Skills; CCAR-P-1.6 ties solutions to cost and business value.
- LLM costs scale with traffic and context size. A design choice that costs pennies in a pilot can cost a great deal
  at production volume.
- Several levers (caching especially) also raise effective throughput under rate limits and cut latency.

## How it works

### Know your token profile first

Before changing anything, measure. From each response's `usage` block, record input, output, cache-write and
cache-read tokens by route and model. Identify where spend concentrates. Then work through the levers, free wins
first, trade-offs second.

### Lever order

| Order | Lever | Quality trade-off? | Typical impact |
|---|---|---|---|
| 1 | Prompt caching | None | Large on repeated prefixes (system prompts, tool definitions, documents, conversation history) |
| 2 | Input-token hygiene | None if done carefully | Moderate: trim redundant instructions, unused tools, oversized retrieval |
| 3 | Output-token hygiene | Usually none | Moderate: concise formats, structured outputs, no unnecessary preamble |
| 4 | Agent loop hygiene | None | Moderate to large: fewer wasted turns, smaller tool results, iteration caps |
| 5 | Message Batches API | Latency (asynchronous) | 50 percent discount on eligible non-urgent work |
| 6 | Effort tuning | Possible | Lower effort reduces thinking and output tokens on routine tasks |
| 7 | Model routing | Possible | Cheaper models for simple, high-volume tasks |

### 1. Prompt caching

Caching is a prefix match over `tools`, then `system`, then `messages`. Put stable content first, mark breakpoints
with `cache_control`, and keep anything that varies (timestamps, user IDs, the latest question) after the last
breakpoint. As of 2026-10-24 (check the [pricing page](https://platform.claude.com/docs/en/about-claude/pricing)):

- Cache writes cost 1.25x the base input price for the default 5-minute TTL and 2x for the 1-hour TTL.
- Cache reads cost a fraction of the base input price (around 0.1x on most models; some current models are lower).
- A cache read refreshes the entry's lifetime.
- On most current models, cached reads do not count towards input-tokens-per-minute rate limits, so caching also
  raises throughput.
- There is a minimum cacheable prefix length that varies by model; shorter prefixes silently do not cache.

Verify with `usage.cache_read_input_tokens`. If it stays zero on repeated requests, something in the prefix changes
each time: a date in the system prompt, non-deterministic JSON key order, a varying tool list. Choose TTL by traffic
gaps: 5 minutes for continuous traffic; 1 hour when requests on the same prefix are minutes apart (and for batches,
which can take longer than 5 minutes). See [prompt caching](../04-context-engineering/03-prompt-caching.md).

### 2 and 3. Token hygiene

- Remove instructions the current model no longer needs; prompts written for older models are often longer than
  necessary.
- Send only the tools a route needs; consider tool search with deferred loading for large catalogues.
- Retrieve fewer, better chunks rather than many marginal ones.
- Ask for the output you need: structured outputs instead of prose plus JSON; a length guide; no restating the
  question.
- Do not lowball `max_tokens` to save money: it does not reduce cost on successful answers (you pay for tokens
  generated, and `max_tokens` does not count against output rate limits) and truncation forces costly retries.

### 4. Agent loop hygiene

Agent costs grow with turns because each turn re-sends the conversation. Cache the conversation prefix, return
compact tool results (IDs and needed fields, not whole records), cap iterations, use task budgets where supported, and
consider context editing or compaction for long sessions (they manage context size; context editing rewrites the
cached prefix, so use it to make room, not as a savings lever).

### 5. Message Batches API

For work nobody is waiting on (nightly classification, evals, back-filling summaries), the
[Message Batches API](https://platform.claude.com/docs/en/build-with-claude/batch-processing) processes requests
asynchronously at a 50 percent discount (as of 2026-10-24). Most batches finish within an hour; batches expire if not
complete within 24 hours, and results are available for 29 days. Results can return in any order, so key by
`custom_id`. Batches can be combined with prompt caching.

### 6. Effort

`output_config.effort` (`low`, `medium`, `high`, `xhigh`, `max`) trades thoroughness for tokens within one model.
Defaults differ by model (for example `medium` on Claude Opus 5.5 and `high` on Claude Sonnet 5.5, as of
2026-10-24), so set it explicitly. Routine classification, extraction and chat often hold quality at `low` or
`medium`; complex coding and agentic work repay higher effort. Measure per route with your eval suite.

### 7. Model routing

Use a smaller, cheaper model (for example Claude Haiku 5.5) for simple, high-volume tasks such as classification,
screening and extraction, and a larger model where quality demands it. Before building a multi-model cascade, test the
stronger model at lower effort: it is often competitive, and one model keeps one cache (caches are model-specific, so
routing between models forfeits cache reuse). Judge every option by **cost per completed task** on your eval suite.

## Example

Caching a long, stable system prompt and tool list, and reading cache metrics back. The same request shape works in
mock mode.

```python
"""cached_call.py - cache a stable prefix and verify cache reads."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "19-hands-on-labs" / "common"))
from claude_lab import MODEL, get_client  # noqa: E402

POLICY_HANDBOOK = "...(several thousand tokens of stable policy text)..."

SYSTEM = [
    {"type": "text", "text": "You answer staff questions about Acme Logistics shipping policy. "
                             "Answer only from the handbook; say when it does not cover a question."},
    {"type": "text", "text": POLICY_HANDBOOK, "cache_control": {"type": "ephemeral"}},  # breakpoint after stable prefix
]


def ask(client, question: str):
    response = client.messages.create(
        model=MODEL,
        max_tokens=1024,
        output_config={"effort": "low"},     # routine Q&A; confirm with evals
        system=SYSTEM,
        messages=[{"role": "user", "content": question}],   # varying content after the breakpoint
    )
    u = response.usage
    total_in = u.input_tokens + (u.cache_creation_input_tokens or 0) + (u.cache_read_input_tokens or 0)
    hit = (u.cache_read_input_tokens or 0) / total_in if total_in else 0.0
    print(f"stop={response.stop_reason} cache_read={u.cache_read_input_tokens} "
          f"cache_write={u.cache_creation_input_tokens} hit_rate={hit:.0%}")
    return response


if __name__ == "__main__":
    client = get_client()
    ask(client, "Can we ship lithium batteries by air?")
    ask(client, "What is the claims window for damaged goods?")   # second call should read from cache (live)
```

And submitting non-urgent work as a batch (live mode only):

```python
import anthropic

client = anthropic.Anthropic()
batch = client.messages.batches.create(requests=[
    {"custom_id": f"ticket-{i}",
     "params": {"model": "claude-haiku-5-5", "max_tokens": 64,
                "system": "Classify the ticket as billing, delivery, damage or other. Reply with one word.",
                "messages": [{"role": "user", "content": text}]}}
    for i, text in enumerate(["Parcel arrived crushed.", "Charged twice this month."])
])
print(batch.id, batch.processing_status)  # poll retrieve(batch.id) until "ended", then read results by custom_id
```

> **Cost:** requires API credits (live mode). [Lab 17](../19-hands-on-labs/lab-17-cost-optimisation/README.md)
> measures each lever offline and then live.

## Enterprise use case

*Northwind Lending* spends most of its Claude budget on a servicing assistant and a nightly document-classification
job. The cost review:

| Finding | Lever | Effect (illustrative) |
|---|---|---|
| 12,000-token system prompt and tool list re-sent on every turn; cache hit rate 3 percent | Moved the per-request timestamp out of the system prompt; added a breakpoint after tools and system | Cache hit rate above 80 percent; input cost for the assistant fell sharply |
| Retrieval sent 20 chunks; evals showed 6 was enough | Input hygiene | Fewer input tokens, slightly better faithfulness |
| Nightly classification ran synchronously on the largest model | Batch API plus a smaller model validated on the eval set | Large reduction on that job with equal accuracy |
| Effort left at default for simple "what is my balance" intents | Routed simple intents to low effort | Fewer output tokens, same quality |

Each change went through the eval suite; one candidate (a smaller model for hardship questions) was rejected because
cost per completed task rose once escalations were counted.

## Common mistakes

- Dynamic content (dates, IDs, shuffled tools) at the top of the prompt, silently breaking caching.
- Comparing cost per request instead of cost per completed task.
- Cutting `max_tokens` to save money and causing truncation and retries.
- Switching models for cost without running the eval suite.
- Running evals and back-fills synchronously at full price.

## Security considerations

- Keep cached prefixes free of per-user secrets and avoid mixing tenants in shared prefixes.
- Spend limits per workspace contain the impact of a leaked key or a runaway agent loop (OWASP LLM10 Unbounded
  Consumption).
- Batch inputs and results are stored for the batch's lifetime; check retention eligibility for sensitive data.

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| `cache_read_input_tokens` always zero | Prefix changes per request, prefix below minimum length, or requests more than the TTL apart | Diff consecutive request prefixes; lengthen stable prefix; use 1-hour TTL |
| Cache hit rate drops after a deploy | Prompt or tool order changed | Keep prefix deterministic; sort tool lists and JSON keys |
| Batch results missing for some requests | Requests errored or expired | Check each result's type; resubmit errored or expired ones |
| Costs rose after switching to a "cheaper" model | More retries, longer outputs or escalations | Measure cost per completed task |

## Check your understanding

1. Why is prompt caching usually the first cost lever to apply?
2. Name three things that silently break prompt caching.
3. When is the Message Batches API appropriate, and what are its timing limits?
4. Why should you test a stronger model at lower effort before building a multi-model cascade?

<details>
<summary>Answers</summary>

1. It reduces cost (and often latency and rate-limit pressure) without any change in output quality.
2. Any three: timestamps or IDs early in the prompt, non-deterministic JSON or tool ordering, changing the tool set,
   prefix shorter than the minimum, gaps longer than the TTL, switching models.
3. For work no one is waiting on; most batches finish within an hour, they expire if not complete in 24 hours, and
   results are available for 29 days.
4. Lower effort on a capable model often keeps quality while cutting tokens, and a single model keeps a single cache;
   a cascade forfeits cache reuse across models and adds complexity.

</details>

## Further reading

- Anthropic: [Prompt caching](https://platform.claude.com/docs/en/build-with-claude/prompt-caching)
- Anthropic: [Batch processing](https://platform.claude.com/docs/en/build-with-claude/batch-processing)
- Anthropic: [Effort](https://platform.claude.com/docs/en/build-with-claude/effort)
- Anthropic: [Pricing](https://platform.claude.com/docs/en/about-claude/pricing)
- In this repository: [token counting and cost](../06-claude-api/08-token-counting-and-cost.md),
  [model selection](../05-claude-products-and-models/03-model-selection.md),
  [Lab 17](../19-hands-on-labs/lab-17-cost-optimisation/README.md),
  [Project 01](../20-real-world-projects/01-document-summarisation-assistant/README.md)

<!-- page-nav:start -->
---

[← Previous: Observability](02-observability.md) · [Module overview](README.md) · [Next: Latency Optimisation →](04-latency-optimisation.md)
<!-- page-nav:end -->
