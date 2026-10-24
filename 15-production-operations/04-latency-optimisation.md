# Latency Optimisation

> **Level:** Intermediate · **Time:** ~40 min · **Exam relevance:** CCAR-P D4 (4.5), CCAR-P D3 (3.3), CCAO-F D3 (3.3)

## In plain English

Latency is how long users or calling systems wait. For an LLM application, total latency is roughly: time to send the
request and process the input, time to the first output token, and time to generate the rest of the output, plus any
retrieval, tool calls and extra model turns. Users perceive two things: how soon something appears, and how long until
the answer is complete.

You can make the system *feel* faster (streaming shows the answer as it is written) and *be* faster (fewer tokens,
cached input, a faster model or lower effort, parallel work, fewer turns).

## Why it matters

- CCAR-P-3.3 asks you to evaluate accuracy and latency trade-offs and justify a configuration; CCAR-P-4.5 covers
  latency optimisation.
- Latency drives adoption. Users abandon assistants that pause for long periods with no feedback.
- Long single requests can hit HTTP timeouts; streaming and sensible `max_tokens` prevent that.

## How it works

### Where the time goes

| Component | Main drivers | Levers |
|---|---|---|
| Network and queueing | Region, connection reuse, retries | Keep connections alive, avoid needless retries, choose deployment region |
| Input processing (prefill) | Number of uncached input tokens | Prompt caching, trimming context |
| Thinking | Effort level, task difficulty | Lower effort for routine tasks |
| Output generation | Number of output tokens, model speed | Shorter outputs, structured formats, faster model, fast mode where available |
| Orchestration | Sequential retrieval, tool calls, agent turns | Parallelism, fewer turns, caching tool results |

Output tokens usually dominate: generating 1,000 tokens takes far longer than reading 1,000. Cutting unnecessary
output is often the single biggest latency win.

### Levers in detail

**Streaming.** Stream responses so users see text as it is generated. Time to first token (TTFT) becomes the
perceived wait. Streaming also avoids HTTP timeouts on long outputs; the SDKs require streaming for very large
`max_tokens` values. When you do not need incremental events, the SDK's stream helper can still return the final
message (`get_final_message()` in Python). Note that on current models thinking is omitted from the stream by default
(`display: "omitted"`), which looks like a pause before text appears; if you show reasoning progress to users, set the
thinking display option explicitly, as described in Anthropic's docs.

**Prompt caching.** Cached prefixes do not need to be processed again, which reduces TTFT for long system prompts,
documents and conversation history. See [cost optimisation](03-cost-optimisation.md).

**Model and effort choice.** Smaller models are faster. Lower `effort` means less thinking and often fewer, more
consolidated tool calls. Measure quality at each setting with your eval suite before switching. For some Claude Opus
models on the Claude API, a fast mode at premium pricing (as of 2026-10-24) increases output speed, with its own rate
limits; check model availability, status and pricing in the
[fast mode docs](https://platform.claude.com/docs/en/build-with-claude/fast-mode).

**Shorter outputs.** Ask for the format you need, set expectations about length, use structured outputs for
machine-consumed results, and avoid asking the model to restate inputs.

**Parallelism.**

- Run independent retrieval, tool calls and sub-tasks concurrently.
- Claude can request several tools in one turn (parallel tool use); execute them concurrently and return all results
  in a single user message.
- Split large jobs into independent chunks processed concurrently (within rate limits), then combine.

**Fewer turns.** Each agent turn adds a full round trip. Give the full task specification up front, design tools that
return what the next step needs, and avoid chatty multi-step flows where one call would do.

**Speculative and precomputed work.** Pre-warm caches before predictable traffic (for example, cache pre-warming with a
`max_tokens: 0` request where supported), precompute summaries of static documents, and cache final answers to
frequent identical questions in your own application cache when freshness allows.

**Route by need.** Interactive paths get streaming and fast settings; non-urgent work goes to batch.

### Trade-off table

| Change | Latency | Quality risk | Cost |
|---|---|---|---|
| Streaming | Perceived much better | None | None |
| Caching | Better TTFT | None | Lower |
| Shorter output | Better | Low if format still meets needs | Lower |
| Lower effort | Better | Task-dependent; measure | Lower |
| Smaller model | Better | Task-dependent; measure | Lower |
| Parallel tools and chunks | Better | None (if independent) | Neutral; watch rate limits |
| Fast mode | Better output speed | None | Higher |

## Example

Streaming with time-to-first-token measurement, and running independent calls concurrently. Uses the official SDK
(live mode).

```python
"""latency_demo.py - stream with TTFT measurement and run independent calls in parallel."""
import asyncio
import time

import anthropic

MODEL = "claude-sonnet-5-5"


def stream_answer(client: anthropic.Anthropic, question: str) -> None:
    start = time.monotonic()
    first = None
    with client.messages.stream(
        model=MODEL,
        max_tokens=2048,
        output_config={"effort": "low"},
        messages=[{"role": "user", "content": question}],
    ) as stream:
        for text in stream.text_stream:
            if first is None:
                first = time.monotonic() - start
            print(text, end="", flush=True)
        final = stream.get_final_message()
    total = time.monotonic() - start
    print(f"\n[ttft={first or 0:.2f}s total={total:.2f}s stop={final.stop_reason} "
          f"out_tokens={final.usage.output_tokens}]")


async def summarise_many(docs: list[str]) -> list[str]:
    client = anthropic.AsyncAnthropic()
    sem = asyncio.Semaphore(8)          # stay within rate limits

    async def one(doc: str) -> str:
        async with sem:
            r = await client.messages.create(
                model=MODEL, max_tokens=300, output_config={"effort": "low"},
                messages=[{"role": "user", "content": f"Summarise in two sentences:\n<doc>{doc}</doc>"}])
            return "".join(b.text for b in r.content if b.type == "text") if r.stop_reason == "end_turn" else ""

    return await asyncio.gather(*(one(d) for d in docs))


if __name__ == "__main__":
    stream_answer(anthropic.Anthropic(), "Give three tips for packing fragile items for shipping.")
    print(asyncio.run(summarise_many(["Report A ...", "Report B ...", "Report C ..."])))
```

> **Cost:** requires API credits (live mode).

## Enterprise use case

*Acme Logistics'* driver-support assistant had a p95 latency of 14 seconds. Profiling with traces showed: retrieval
and two tool calls ran sequentially (4 seconds), the 9,000-token system prompt was never cached (TTFT around
2 seconds), and answers averaged 600 output tokens of which drivers read about 150.

Changes: parallel retrieval and tool calls, prompt caching with a breakpoint after the system prompt, a format
instruction for three short bullet points, streaming in the mobile app, and `effort: "low"` for the "where is my next
stop" intent after evals confirmed no quality loss. The p95 dropped to about 5 seconds and perceived wait (TTFT) to
under 1.5 seconds. These figures are illustrative.

## Common mistakes

- Optimising the model call while sequential tool calls and retrieval dominate the trace.
- Not streaming in interactive UIs.
- Requesting long, verbose answers nobody reads.
- Parallelising without a concurrency limit, causing 429s that make latency worse.
- Lowering effort or switching models without measuring quality.

## Security considerations

- Streaming renders partial output; apply output sanitisation incrementally or render as plain text until complete
  (see [insecure output handling](../12-ai-security/06-insecure-output-handling.md)).
- Application-level answer caches must be keyed per user or tenant where answers depend on permissions.
- Aggressive timeouts can cause retries that duplicate side-effecting actions; combine with idempotency
  ([reliability engineering](05-reliability-engineering.md)).

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| Long pause before any text even with streaming | Thinking not displayed; long uncached prefix | Show progress or summarised thinking; cache the prefix; lower effort |
| Latency fine at p50, bad at p99 | Occasional long outputs, retries or agent loops | Cap output, investigate retries, cap iterations |
| Parallel calls slower than sequential | Rate limiting | Add a semaphore; check rate-limit headers |
| Requests time out | Large `max_tokens` without streaming | Stream long requests |

## Check your understanding

1. Why do output tokens usually dominate latency?
2. What does streaming improve, and what does it not change?
3. Name two ways to reduce the number of round trips in an agent.
4. Why must parallel requests be bounded?

<details>
<summary>Answers</summary>

1. Output is generated token by token, while input is processed in parallel; generating a token takes much longer than
   reading one.
2. It improves perceived latency (time to first visible output) and avoids timeouts; it does not reduce total
   generation time or cost.
3. Any two: give the full task specification up front; tools that return everything the next step needs; parallel tool
   calls in one turn; combining steps that do not need separate model calls.
4. Unbounded concurrency hits rate limits, causing 429 errors and retries that increase latency overall.

</details>

## Further reading

- Anthropic: [Streaming](https://platform.claude.com/docs/en/build-with-claude/streaming)
- Anthropic: [Reducing latency](https://platform.claude.com/docs/en/test-and-evaluate/strengthen-guardrails/reduce-latency)
- Anthropic: [Effort](https://platform.claude.com/docs/en/build-with-claude/effort) and
  [fast mode](https://platform.claude.com/docs/en/build-with-claude/fast-mode)
- In this repository: [streaming](../06-claude-api/03-streaming.md),
  [model selection](../05-claude-products-and-models/03-model-selection.md),
  [Project 01](../20-real-world-projects/01-document-summarisation-assistant/README.md)

<!-- page-nav:start -->
---

[← Previous: Cost Optimisation](03-cost-optimisation.md) · [Module overview](README.md) · [Next: Reliability Engineering →](05-reliability-engineering.md)
<!-- page-nav:end -->
