# Rate Limits and Capacity

> **Level:** Intermediate · **Time:** ~40 min · **Exam relevance:** CCAR-P D4 (4.5), CCAR-P D3 (3.3), CCAR-P D6 (6.3)

## In plain English

The Claude API limits how much each organisation can use: how many requests per minute, how many input and output
tokens per minute, and how much money per month. These limits protect the service and prevent accidental overspend.
Capacity planning means estimating your peak demand in those units, comparing it with your limits, and designing the
application to stay within them gracefully when traffic spikes.

## Why it matters

- Rate-limit errors (HTTP 429) at peak are one of the most common production incidents for LLM features, and they
  often appear for the first time on the busiest day.
- Token-based limits behave differently from request-based limits you may know from other APIs: one large request can
  consume as much capacity as hundreds of small ones.
- SLAs you agree with stakeholders (CCAR-P-6.3) are only credible if capacity supports them.

## How it works

### Types of limit (verified 2026-10-24)

Per Anthropic's [rate limits documentation](https://platform.claude.com/docs/en/api/rate-limits):

| Limit | What it caps | Notes |
|---|---|---|
| Spend limit | Monthly cost for the organisation | Each usage tier has a monthly cap; you can set a lower limit yourself. Reaching the tier cap returns 429 with `error_code` `enforced_spend_limit_reached` and no `retry-after`; reaching your own limit returns 400 |
| Requests per minute (RPM) | Number of Messages API requests | Per model class |
| Input tokens per minute (ITPM) | Uncached input tokens | For most current models, only `input_tokens` and `cache_creation_input_tokens` count; `cache_read_input_tokens` do not |
| Output tokens per minute (OTPM) | Output tokens actually generated | `max_tokens` does not count against OTPM |
| Message Batches limits | Batch API requests per minute and requests in the processing queue | Separate from Messages API limits |
| Other endpoint limits | Files API, Managed Agents endpoints, fast mode | Each has its own limits |
| Acceleration limits | Sharp increases in usage | Ramp traffic gradually |

Further details:

- Limits are set per **usage tier**, and organisations move up tiers based on usage history; higher limits can be
  requested in the Console.
- The API uses a **token bucket** algorithm: capacity refills continuously up to the maximum, rather than resetting at
  fixed intervals. A per-minute limit may be enforced over shorter intervals, so bursts can trigger 429s even if the
  minute's total is within the limit.
- **Workspaces** can have their own lower spend and rate limits, protecting other workspaces from one noisy
  application; organisation-wide limits always apply.
- Limits are maximums, not guaranteed minimums.

### Response headers

Every response carries headers you can use to steer traffic before you hit the limit:

| Header | Meaning |
|---|---|
| `retry-after` | Seconds to wait before retrying (on 429s that include it) |
| `anthropic-ratelimit-requests-limit` / `-remaining` / `-reset` | Request limit status |
| `anthropic-ratelimit-input-tokens-limit` / `-remaining` / `-reset` | Input-token limit status |
| `anthropic-ratelimit-output-tokens-limit` / `-remaining` / `-reset` | Output-token limit status |
| `anthropic-ratelimit-tokens-*` | The most restrictive token limit currently in effect |

Reset values are RFC 3339 timestamps; token remaining values are rounded to the nearest thousand.

### Why caching is a capacity lever

Because cached reads do not count towards ITPM on most current models, a high cache hit rate multiplies effective
input throughput. A worked example: if your limit is 500,000 ITPM and three-quarters of each prompt is served from the
cache, only a quarter of each request counts, so you can send roughly 2,000,000 input tokens per minute in total
(500,000 ÷ 0.25). Caching is therefore both a cost and
a capacity strategy (see [cost optimisation](03-cost-optimisation.md)).

### Capacity planning

1. **Measure per-request shape** for each route: uncached input tokens, cache-write tokens, cached-read tokens, output
   tokens, and calls per user action (agents make several).
2. **Forecast peak demand**: peak user actions per minute (not daily averages), including seasonal peaks and launch
   events.
3. **Convert to limit units**: RPM, ITPM (uncached input plus cache writes), OTPM, per model.
4. **Add headroom**: plan to run at no more than about 60 to 70 percent of each limit at forecast peak, to absorb
   bursts, retries and growth.
5. **Close the gap**: caching, input trimming, batching non-urgent work, spreading load across time, moving routes to
   other models (each model class has its own limits), requesting a tier increase, or using additional platforms.
6. **Re-check after changes**: a prompt that grows by 2,000 tokens changes ITPM for every request.

### Handling limits gracefully

- Client-side rate limiting (a token bucket in your service) to smooth bursts before they reach the API.
- Priority queues: interactive traffic first, background work later.
- Honour `retry-after`; use backoff with jitter.
- Shed or defer low-priority work when headroom is low.
- Separate workspaces (and keys) per application so one cannot starve another.
- Move bulk work to the Message Batches API, which has separate limits.

## Example

A capacity calculator and a client-side token bucket that respects input- and output-token budgets.

```python
"""capacity.py - estimate peak usage against limits, and smooth traffic with a token bucket."""
import threading
import time


def plan(peak_actions_per_min: float, calls_per_action: float, uncached_in: int,
         cache_write: int, out_tokens: int, limits: dict, target_utilisation: float = 0.65) -> dict:
    rpm = peak_actions_per_min * calls_per_action
    itpm = rpm * (uncached_in + cache_write)     # cache reads excluded for most current models
    otpm = rpm * out_tokens
    need = {"rpm": rpm, "itpm": itpm, "otpm": otpm}
    return {k: {"need": round(v), "limit": limits[k],
                "utilisation": round(v / limits[k], 2),
                "ok": v <= limits[k] * target_utilisation} for k, v in need.items()}


class TokenBucket:
    """Refills continuously; acquire() blocks until enough capacity is available."""

    def __init__(self, capacity_per_min: float):
        self.capacity = capacity_per_min
        self.tokens = capacity_per_min
        self.rate = capacity_per_min / 60.0
        self.last = time.monotonic()
        self.lock = threading.Lock()

    def acquire(self, amount: float) -> None:
        amount = min(amount, self.capacity)
        while True:
            with self.lock:
                now = time.monotonic()
                self.tokens = min(self.capacity, self.tokens + (now - self.last) * self.rate)
                self.last = now
                if self.tokens >= amount:
                    self.tokens -= amount
                    return
                wait = (amount - self.tokens) / self.rate
            time.sleep(min(wait, 1.0))


if __name__ == "__main__":
    # Illustrative limits; read yours from the Console or the Rate Limits API.
    limits = {"rpm": 5_000, "itpm": 5_000_000, "otpm": 1_000_000}
    print(plan(peak_actions_per_min=900, calls_per_action=3, uncached_in=1_500,
               cache_write=200, out_tokens=350, limits=limits))
    input_bucket = TokenBucket(limits["itpm"] * 0.65)
    input_bucket.acquire(1_700)   # call before each request with its estimated uncached input tokens
    print("acquired")
```

Use `messages.count_tokens` or recorded usage to estimate each request's input tokens. After each response, compare
the `anthropic-ratelimit-*-remaining` headers with your own estimate and adjust.

## Enterprise use case

*Acme Logistics* expects holiday traffic of 1,200 customer conversations per minute at peak, each averaging three model
calls. Its capacity plan:

| Measure | Before | After optimisation |
|---|---|---|
| Uncached input per call | 9,000 tokens (no caching) | 1,200 tokens (system prompt and tools cached) |
| Peak ITPM need | about 32 million | about 4.3 million (plus cache writes) |
| Peak OTPM need | about 1.4 million | about 0.9 million (shorter answer format) |
| Plan | Exceeds current tier | Within limits at about 60 percent utilisation after a tier increase request |

Figures are illustrative. The team also moved post-conversation summarisation to the Batch API overnight, split
customer and internal tools into separate workspaces with their own limits, and load-tested at 120 percent of
forecast peak two weeks before the season.

## Common mistakes

- Planning from daily averages instead of peak minutes.
- Ignoring that agents make several calls per user action.
- Forgetting that prompt growth increases ITPM on every request.
- Retrying 429s immediately without honouring `retry-after`.
- One shared key and workspace for all applications.

## Security considerations

- Spend limits are a security control against leaked keys and runaway agents (OWASP LLM10 Unbounded Consumption). Set
  workspace limits below organisation limits.
- Per-user quotas in your own application stop a single user (or attacker) from consuming the organisation's
  capacity.
- Alert on sudden usage increases from one key or workspace.

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| 429s while the minute's total is under the limit | Bursts; limit enforced over shorter intervals | Client-side smoothing; jittered scheduling |
| 429 with no `retry-after` and an `enforced_spend_limit_reached` code | Monthly spend cap reached | Do not retry; raise the limit or wait for reset; alert |
| 400 saying you reached your specified usage limits | Your own spend limit (organisation or workspace) | Raise or remove the limit |
| ITPM limit hit despite modest traffic | Low cache hit rate or large retrieval payloads | Fix caching; trim inputs |
| 429s after a sudden launch | Acceleration limits | Ramp traffic gradually |

## Check your understanding

1. Which token counts count towards ITPM on most current Claude models?
2. Why does `max_tokens` not affect OTPM?
3. How does prompt caching increase effective throughput?
4. How should your application react to a 429 that has no `retry-after` header and an
   `enforced_spend_limit_reached` code?

<details>
<summary>Answers</summary>

1. Uncached `input_tokens` and `cache_creation_input_tokens`; `cache_read_input_tokens` do not count on most current
   models.
2. OTPM is evaluated on the output tokens actually generated, in real time, not on the requested maximum.
3. Cached reads do not count towards ITPM, so a high hit rate lets far more total input flow within the same limit.
4. Treat it as a spend-cap condition: do not retry, degrade gracefully, alert, and raise the limit or wait for the
   monthly reset.

</details>

## Further reading

- Anthropic: [Rate limits](https://platform.claude.com/docs/en/api/rate-limits)
- Anthropic: [Rate Limits API](https://platform.claude.com/docs/en/manage-claude/rate-limits-api)
- Anthropic: [Workspaces](https://platform.claude.com/docs/en/manage-claude/workspaces)
- Anthropic: [Token counting](https://platform.claude.com/docs/en/build-with-claude/token-counting)
- In this repository: [errors, rate limits and retries](../06-claude-api/06-errors-rate-limits-retries.md),
  [Lab 17](../19-hands-on-labs/lab-17-cost-optimisation/README.md),
  [Lab 18](../19-hands-on-labs/lab-18-reliability-engineering/README.md)
