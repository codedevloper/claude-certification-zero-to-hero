# Errors, Rate Limits and Retries

> **Level:** Intermediate → Advanced · **Time:** ~55 min · **Exam relevance:** CCAR-P D3, D4, D7

## In plain English

Every networked service fails sometimes. Requests can be malformed, keys can be wrong, you can send more traffic than
your account allows, or the service can be briefly overloaded. A production integration is not one that never sees
errors; it is one that **tells the difference** between errors you should fix and errors you should wait out, and
behaves sensibly in both cases.

The basic sorting rule:

- **Your request is wrong** (400, 401, 403, 404, 413): retrying the same request will fail again. Fix it.
- **The service is busy or briefly unhealthy** (429, 500, 529, network failures): wait and retry, with growing delays.

## Why it matters

- A retry loop that retries everything wastes money and hides bugs; a client that retries nothing turns brief blips
  into outages.
- Rate limits shape architecture: how many concurrent workers, whether to batch, how to prioritise traffic.
- Observability and operational debugging are exam objectives (CCAR-P-3.4, CCAR-P-7.3), and reliability engineering is
  covered in [Module 15](../15-production-operations/05-reliability-engineering.md).

## How it works

### HTTP errors

Errors come back as JSON with a `type` and `message`, plus a `request_id` you should log:

```json
{"type": "error",
 "error": {"type": "rate_limit_error", "message": "..."},
 "request_id": "req_..."}
```

| Status | `error.type` | Retry? | Typical cause | Fix |
|---|---|---|---|---|
| 400 | `invalid_request_error` | No | Malformed request; unsupported parameter (for example `temperature`, `budget_tokens`, prefill, forced `tool_choice` on Opus 5.5, Sonnet 5.5, Fable 5.1 or Mythos 5.1) | Read the message; fix the request |
| 401 | `authentication_error` | No | Missing, invalid or revoked credential | Check the key or token in the running environment |
| 402 | `billing_error` | No | Billing or payment problem | Resolve in the Console |
| 403 | `permission_error` | No | Credential not allowed for this action or resource | Check workspace and organisation permissions |
| 404 | `not_found_error` | No | Unknown endpoint, or model ID wrong or unavailable to you | Use exact model IDs; list models |
| 413 | `request_too_large` | No | Request body exceeds the size limit | Use the Files API, shrink inputs, split work |
| 429 | `rate_limit_error` | Yes, after `retry-after` | Too many requests or tokens per minute | Back off; smooth traffic; request higher limits |
| 500 | `api_error` | Yes, with backoff | Unexpected internal error | Retry; check the status page if persistent |
| 529 | `overloaded_error` | Yes, with backoff | Temporary capacity pressure | Retry with backoff; spread load |

Two "errors" are not HTTP errors at all and must be handled in normal response handling:

- `stop_reason == "refusal"`: the request was declined, with HTTP 200 (see
  [the Messages API](02-messages-api.md)).
- Server-tool problems, such as a web search failing, arrive as error objects inside tool-result blocks with HTTP 200.

When streaming, an error can arrive **after** the 200 status as an `error` event; the SDK raises it while you iterate
(see [streaming](03-streaming.md)).

### The typed exception chain (Python SDK)

The SDK maps each status to an exception class, so you never need to parse error strings:

| Exception | Status |
|---|---|
| `anthropic.BadRequestError` | 400 |
| `anthropic.AuthenticationError` | 401 |
| `anthropic.PermissionDeniedError` | 403 |
| `anthropic.NotFoundError` | 404 |
| `anthropic.UnprocessableEntityError` | 422 |
| `anthropic.RateLimitError` | 429 |
| `anthropic.InternalServerError` | 500 and above |
| `anthropic.APIStatusError` | Base class for any non-2xx response (`.status_code`, `.type`, `.message`, `.request_id`) |
| `anthropic.APIConnectionError` | Network failure before any response; `APITimeoutError` is a subclass |
| `anthropic.APIError` | Base of all of the above |

Catch **most specific first**, with separate handling for retryable and non-retryable cases. A single broad
`except Exception` throws away the information you need.

### Built-in retries

The Python SDK automatically retries connection errors, 408, 409, 429 and 5xx responses with exponential backoff:
`max_retries` defaults to 2 and the default timeout is 10 minutes (as of 2026-10-24). Configure per client or per call:

```python
client = anthropic.Anthropic(max_retries=4, timeout=120.0)
client.with_options(max_retries=0).messages.create(...)   # disable for this call
```

Note that timeouts are retried too, so the worst-case wall-clock time is roughly `timeout x (max_retries + 1)`.

Write your own retry layer only when you need behaviour the SDK does not provide: a global retry budget, falling back
to a different model, a circuit breaker, or moving work to a queue.

### Rate limits

Limits are set per organisation and usage tier, per model class, and are visible in the Console (as of 2026-10-24):

| Limit | Measures |
|---|---|
| Requests per minute (RPM) | Number of requests |
| Input tokens per minute (ITPM) | Uncached input tokens; on most models, cache reads do not count |
| Output tokens per minute (OTPM) | Generated tokens, including thinking |

Limits are enforced continuously rather than as a fixed reset each minute, so a short burst can trigger 429 even if
your per-minute average is below the limit. Separate limits can apply to particular features (for example the Batches
API, fast mode or long-context requests), and organisations can also set **spend limits** per workspace.

Response headers tell you where you stand:

| Header | Meaning |
|---|---|
| `retry-after` | Seconds to wait before retrying (on 429) |
| `anthropic-ratelimit-requests-limit` / `-remaining` / `-reset` | Request limit status |
| `anthropic-ratelimit-input-tokens-limit` / `-remaining` / `-reset` | Input token limit status |
| `anthropic-ratelimit-output-tokens-limit` / `-remaining` / `-reset` | Output token limit status |

### Designing for limits

1. **Smooth traffic.** Use a client-side token bucket or a work queue instead of bursting.
2. **Use caching.** Cached input does not count toward ITPM on most models, raising effective throughput.
3. **Batch what can wait.** The [Batches API](05-batch-processing.md) has its own capacity.
4. **Prioritise.** Reserve capacity for interactive users; let background jobs back off first.
5. **Right-size `max_tokens` and effort.** Output limits are consumed by thinking too.
6. **Monitor headers** and alert before you hit the ceiling; request higher limits ahead of launches.

## Example

A resilient call wrapper for *Acme Logistics* (fictional). It relies on the SDK for routine retries, adds one
application-level fallback for sustained overload, and logs request IDs for every failure.

```python
import logging
import random
import time

import anthropic

log = logging.getLogger("claude.client")
client = anthropic.Anthropic(max_retries=3)   # SDK handles short blips with backoff

PRIMARY, FALLBACK = "claude-opus-5-5", "claude-sonnet-5-5"


class NonRetryableError(Exception):
    """The request itself is wrong; do not retry."""


def create_with_resilience(**params) -> anthropic.types.Message:
    model = params.pop("model", PRIMARY)
    for attempt in range(3):
        try:
            return client.messages.create(model=model, **params)
        except anthropic.BadRequestError as e:          # 400: fix the request
            log.error("bad request %s: %s", e.request_id, e.message)
            raise NonRetryableError(e.message) from e
        except (anthropic.AuthenticationError, anthropic.PermissionDeniedError) as e:  # 401/403
            log.critical("credential problem %s (%s)", e.status_code, e.request_id)
            raise NonRetryableError("Check credentials and workspace permissions") from e
        except anthropic.NotFoundError as e:            # 404: wrong model ID or endpoint
            raise NonRetryableError(f"Not found: {e.message}") from e
        except anthropic.RateLimitError as e:           # 429 after SDK retries were exhausted
            wait = float(e.response.headers.get("retry-after", "30"))
            log.warning("rate limited (%s); waiting %.0fs", e.request_id, wait)
            time.sleep(wait)
        except anthropic.APIStatusError as e:           # 5xx including 529 overloaded
            if e.status_code >= 500:
                log.warning("server error %s %s (%s)", e.status_code, e.type, e.request_id)
                if e.type == "overloaded_error" and attempt == 1:
                    model = FALLBACK                    # documented, tested degradation path
                time.sleep(min(2 ** attempt + random.random(), 30))
            else:
                raise NonRetryableError(f"{e.status_code}: {e.message}") from e
        except anthropic.APIConnectionError as e:       # network: DNS, TLS, timeout
            log.warning("connection problem: %s", e)
            time.sleep(min(2 ** attempt + random.random(), 30))
    raise RuntimeError("Claude unavailable after retries; queue the work for later")


msg = create_with_resilience(
    max_tokens=2000,
    messages=[{"role": "user", "content": "Summarise today's depot exceptions."}],
)
print(msg.stop_reason, msg.model)
```

Reading rate-limit headers on a successful call:

```python
raw = client.messages.with_raw_response.create(
    model="claude-opus-5-5", max_tokens=100,
    messages=[{"role": "user", "content": "ping"}],
)
remaining = raw.headers.get("anthropic-ratelimit-output-tokens-remaining")
print("output tokens remaining this window:", remaining)
message = raw.parse()
```

> **Cost:** requires API credits (live mode). Be careful with client-side timeouts: if the server finished a request
> your client gave up on, retrying it can mean paying for the same work twice. Prefer streaming for long requests.

## Enterprise use case

*Woodgrove Bank* (fictional) ran a month-end reporting job that fired several hundred Claude requests at once. Each
month it hit 429 errors, the original code retried immediately in a tight loop, and the job made the problem worse,
eventually failing and paging the on-call engineer.

The fix combined several measures: a client-side limiter sized from the rate-limit headers; the SDK's built-in
backoff; moving the narrative-generation requests, which had a next-morning deadline, to the Batches API; caching
the shared report template so cached reads no longer counted against input-token limits; and dashboards on
429 rates, `retry-after` values and request IDs. The interactive analyst assistant now has its own workspace with its
own limits, so batch jobs can no longer starve it. Month-end runs complete without pages.

## Common mistakes

- **Retrying 400-class errors.** They fail again and cost time; fix the request.
- **Retrying without backoff or jitter.** Synchronised retries create a thundering herd.
- **Ignoring `retry-after`.** It tells you exactly how long to wait.
- **Stacking retry layers.** SDK retries plus your retries plus a gateway's retries can multiply load. Know which
  layer retries.
- **String-matching error messages.** Use the typed exceptions and `.type`.
- **Not logging `request_id`.** Support cannot investigate without it.
- **Treating `refusal` as an error to retry.** It is a deliberate outcome; handle it in response logic.
- **Silent model fallback.** Falling back to another model changes behaviour and quality; make it explicit, tested
  and logged.

## Security considerations

- **Do not log credentials**; log request IDs, status codes and error types.
- **Error messages can echo input.** A 400 message may quote part of your request; scrub logs that may contain
  personal data.
- **Abuse and cost controls.** Per-user quotas in your application stop one user (or attacker) from consuming your
  organisation's rate limit or budget. Use workspace spend limits as a backstop.
- **Fail safely.** When Claude is unavailable, degrade to a safe state (queue, human handling, clear message), not to
  skipping a check that the model normally performs.
- **401 spikes** can indicate a leaked or revoked key; alert on them.

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| Frequent 429 at modest average volume | Bursty traffic | Smooth with a limiter or queue; check per-model limits |
| 429 on input tokens only | Large uncached prompts | Cache stable prefixes; trim context |
| 529 during peaks | Temporary overload | Backoff; spread load; consider a documented fallback model |
| Requests take far longer than the timeout | Timeouts are retried | Lower `timeout` or `max_retries` for interactive paths |
| 400 after a model upgrade | Parameters the new model rejects | Remove sampling parameters, prefill, `budget_tokens`, forced `tool_choice` |
| 413 | Request body too large | Files API; smaller images; split documents |

More in [troubleshooting API errors](../24-troubleshooting/api-errors.md).

## Check your understanding

1. Which status codes should normally be retried, and which should not?
2. Why should you catch `RateLimitError` before `APIStatusError`?
3. How does prompt caching help with rate limits as well as cost?
4. What is the risk of adding your own retry loop on top of the SDK's retries and an API gateway's retries?

<details>
<summary>Answers</summary>

1. Retry 429, 500, 529 and connection errors (with backoff, honouring `retry-after`). Do not retry 400, 401, 402, 403,
   404 or 413; fix the cause.
2. `RateLimitError` is a subclass of `APIStatusError`; if the broad class comes first, the specific handler never
   runs and you lose the distinct rate-limit handling.
3. On most models, cache reads do not count toward input-tokens-per-minute limits, so caching raises effective
   throughput.
4. Retries multiply: each layer's attempts multiply the others', amplifying load during an incident and lengthening
   worst-case latency. Decide which layer owns retries.

</details>

## Further reading

- [Errors](https://platform.claude.com/docs/en/api/errors) (Anthropic docs)
- [Rate limits](https://platform.claude.com/docs/en/api/rate-limits) (Anthropic docs)
- [Anthropic status page](https://status.anthropic.com)
- [Reliability engineering](../15-production-operations/05-reliability-engineering.md) and [rate limits and capacity](../15-production-operations/06-rate-limits-and-capacity.md) in this repository
- [Lab 18 — Reliability engineering](../19-hands-on-labs/lab-18-reliability-engineering/README.md)

<!-- page-nav:start -->
---

[← Previous: Batch Processing](05-batch-processing.md) · [Module overview](README.md) · [Next: Cloud Platforms: AWS, Google Cloud and Microsoft Foundry →](07-cloud-platforms.md)
<!-- page-nav:end -->
