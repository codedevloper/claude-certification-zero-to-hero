# Troubleshooting: Claude API Errors

> **As of 2026-10-24**, based on the current Claude API reference and the official
> [errors page](https://platform.claude.com/docs/en/api/errors). Concepts:
> [06 · Errors, rate limits and retries](../06-claude-api/06-errors-rate-limits-retries.md).

## Read the error before you fix it

Every error response has the same shape:

```json
{
  "type": "error",
  "error": {"type": "invalid_request_error", "message": "messages: roles must alternate between \"user\" and \"assistant\""},
  "request_id": "req_..."
}
```

- `error.type` tells you the category; `error.message` usually tells you the exact field.
- Log the `request_id` (also in the `request-id` response header). Support needs it.
- In the Python SDK, catch typed exceptions from most to least specific:

```python
import logging

import anthropic

log = logging.getLogger(__name__)
client = anthropic.Anthropic()


def queue_for_later() -> None:
    """Placeholder for your own retry queue (for example a job queue with delayed retry)."""


try:
    resp = client.messages.create(model="claude-opus-5-5", max_tokens=1024,
                                  messages=[{"role": "user", "content": "ping"}])
except anthropic.BadRequestError as e:        # 400: fix the request, do not retry
    log.error("bad request %s: %s", e.request_id, e.message)
except anthropic.AuthenticationError:          # 401
    raise
except anthropic.NotFoundError as e:           # 404: usually the model ID
    log.error("not found: %s", e.message)
except anthropic.RateLimitError:               # 429: SDK already retried; back off further or queue
    queue_for_later()
except anthropic.APIStatusError as e:          # other HTTP errors, including 5xx and 529
    log.error("status %s", e.status_code)
except anthropic.APIConnectionError:           # network, DNS, TLS, timeout
    log.error("connection problem")
```

## Quick table

| HTTP | `error.type` | Retry? | Most common cause |
|---|---|---|---|
| 400 | `invalid_request_error` | No | Malformed body or a parameter the model rejects |
| 401 | `authentication_error` | No | Missing, wrong or revoked key |
| 402 | `billing_error` | No | Billing or payment problem |
| 403 | `permission_error` | No | Credential, workspace or region not allowed |
| 404 | `not_found_error` | No | Model ID typo or model not available to your organisation |
| 413 | `request_too_large` | No | Body over the size limit |
| 429 | `rate_limit_error` | Yes, after `retry-after` | Requests or tokens per minute exceeded |
| 500 | `api_error` | Yes, with backoff | Transient server problem |
| 529 | `overloaded_error` | Yes, with backoff | Temporary capacity pressure |

## 400 `invalid_request_error`

**Symptom:** the call fails immediately with a 400 and a message naming a field.

**Likely causes (current models):**

| Message mentions | Cause | Fix |
|---|---|---|
| `temperature`, `top_p`, `top_k` | Sampling parameters are rejected on current models | Remove them; control output with instructions, examples and `effort` |
| `budget_tokens`, `thinking.type.enabled` / `disabled` | Legacy thinking configuration | Use `thinking={"type": "adaptive"}` or omit it; set `output_config={"effort": ...}` |
| Final message is `assistant` / prefill | Assistant prefill is not supported | End with a `user` message; use structured outputs for format |
| `tool_choice` `any` / `tool` not supported | Forced tool use is rejected on current models | `tool_choice: auto` plus an explicit instruction; `strict: true` on the tool; or structured outputs |
| `roles must alternate` / first message | Message order | First message `user`; alternate roles; merge consecutive same-role messages |
| `max_tokens` | Above the model's output limit | Lower it, or stream for large values |
| `tool_use ids were found without tool_result` | Tool loop bug | Return a `tool_result` for **every** `tool_use` id in the next user message |
| `anthropic-beta` unexpected value | Unknown or not-enabled beta | Fix the header spelling; check your organisation has access |
| `Invalid signature in thinking block` | Earlier turns or thinking blocks were edited | Keep history append-only; pass thinking blocks back unchanged |
| Schema / `input_schema` | Invalid JSON Schema in a tool or output format | Validate the schema; with `strict: true` include `required` and `additionalProperties: false` |
| `citations` with `output_config.format` | The two features cannot be combined | Choose one per request |

**Diagnosis:** read `error.message`; diff the failing body against a known-good minimal request; check whether code
copied from an older tutorial still sends retired parameters.

**Fix:** correct the body. Never retry a 400 unchanged. Add a request-validation step (this repository's mock client
does this offline; see [labs troubleshooting](labs-and-repository.md)).

## 401 `authentication_error`

**Symptom:** every call fails with 401.

**Likely causes:** `ANTHROPIC_API_KEY` unset in the process that runs the code; a typo or stray whitespace; a revoked
key; both `ANTHROPIC_API_KEY` and `ANTHROPIC_AUTH_TOKEN` set; an OAuth token sent as `x-api-key` instead of
`Authorization: Bearer`.

**Diagnosis:**

```bash
python -c "import os; k=os.environ.get('ANTHROPIC_API_KEY',''); print('set' if k else 'missing', len(k))"
```

(Print presence and length only, never the key.) Check which shell, container or CI job actually runs the code.

**Fix:** set the variable in the right environment (a secrets manager in CI, `.env` loaded locally, never committed);
unset the conflicting variable; rotate the key if it may have leaked.

## 402 `billing_error` and 403 `permission_error`

**Symptom:** valid key, but calls are refused.

**Likely causes:** billing not set up or credits exhausted (402); the key's workspace is not allowed the operation, a
region or access requirement applies, or an organisation policy blocks the model (403).

**Diagnosis:** check the Console's billing and workspace pages; read the message, which often says what to do.

**Fix:** resolve billing; use a key from the correct workspace; ask your administrator for access.

## 404 `not_found_error`

**Symptom:** `not_found_error` with a message starting `model: ...`.

**Likely causes:** typo (`claude-opus-5.5` instead of `claude-opus-5-5`); an invented date suffix; a retired model; a
model your organisation cannot use (the API returns 404 rather than revealing it exists); wrong endpoint path.

**Diagnosis:** `client.models.list()` shows exactly which IDs you can use.

**Fix:** use the exact ID from the [models overview](https://platform.claude.com/docs/en/about-claude/models/overview);
keep model IDs in configuration, not scattered through code.

## 413 `request_too_large`

**Symptom:** large requests fail before processing.

**Likely causes:** big base64 PDFs or images, very long conversation history, many documents in one call.

**Diagnosis:** measure the serialised body size; count tokens with `count_tokens`.

**Fix:** upload once with the Files API and reference `file_id`; resize images; split documents; retrieve only relevant
chunks (RAG); compact or trim history.

## 429 `rate_limit_error`

**Symptom:** intermittent 429s under load, often in bursts.

**Likely causes:** requests per minute, input tokens per minute or output tokens per minute exceeded for your tier;
many workers starting at once; retry storms; a separate limit for a premium mode.

**Diagnosis:** read the `retry-after` and `anthropic-ratelimit-*` / `x-ratelimit-*` headers; plot request and token
rates; check whether retries multiply traffic.

**Fix:**

- Honour `retry-after`; exponential backoff **with jitter**; cap concurrency with a queue or semaphore.
- Cut tokens: prompt caching (cached reads count differently towards limits; see the
  [rate limits page](https://platform.claude.com/docs/en/api/rate-limits)), shorter outputs, retrieval instead of
  whole documents.
- Move non-urgent work to Message Batches.
- Request a higher tier if sustained demand justifies it. See [15 · Rate limits and capacity](../15-production-operations/06-rate-limits-and-capacity.md).

## 500 `api_error` and 529 `overloaded_error`

**Symptom:** occasional server errors, more frequent during peaks.

**Likely causes:** transient service issues or capacity pressure.

**Diagnosis:** check [status.anthropic.com](https://status.anthropic.com); confirm the error rate across many requests,
not one.

**Fix:** the SDK retries twice by default (`max_retries`); add your own backoff with jitter and an overall deadline;
degrade gracefully (queue, cached answer, smaller model for non-critical paths); alert when error rates cross a
threshold. Make retried operations idempotent so a retry never duplicates a side effect.

## Timeouts and streaming errors

| Symptom | Likely cause | Diagnosis | Fix |
|---|---|---|---|
| Client times out on long answers | Non-streaming request with a large `max_tokens` | Compare elapsed time to SDK timeout | Stream (`messages.stream`) and use `get_final_message()` |
| Stream stops with an `error` event | Server-side error mid-stream (for example overload) | Inspect the event payload | Retry the request; design the UI to handle partial output |
| Wall-clock far longer than the timeout | Timeouts are retried | Count attempts in logs | Set `timeout` and `max_retries` deliberately per route |
| `pause_turn` stop reason | Long server-tool turn paused | Check `stop_reason` | Send the response back unchanged to continue |

## Errors that are not HTTP errors

| Symptom | Cause | Fix |
|---|---|---|
| HTTP 200 but `stop_reason: "refusal"` | A safety classifier declined | Read `stop_details`; see [prompts and outputs](prompts-and-outputs.md#refusals) |
| HTTP 200 but JSON fails to parse | `stop_reason: "max_tokens"` truncated output | Check `stop_reason` first; raise `max_tokens` or use structured outputs |
| Web search returns an error object | Server tool errors arrive inside the result block | Branch on the result `content` type before indexing |

## Prevention checklist

- [ ] Model IDs and limits in config; startup check with `models.retrieve`.
- [ ] Typed exception handling with retry only for 429, 5xx and connection errors.
- [ ] `request_id`, model, `stop_reason` and `usage` logged for every call.
- [ ] Concurrency limits and backoff with jitter.
- [ ] Contract tests that send your real request shapes to a mock validator in CI.
