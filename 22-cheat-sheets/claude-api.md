# Claude API Cheat Sheet

> **As of 2026-10-24.** Model IDs, parameters and limits change. Facts here come from the current Claude API reference
> material and the live docs at [platform.claude.com/docs](https://platform.claude.com/docs/en/api/overview). When in
> doubt, check the [models overview](https://platform.claude.com/docs/en/about-claude/models/overview) and
> [errors page](https://platform.claude.com/docs/en/api/errors). Full explanations live in
> [06 · Claude API](../06-claude-api/README.md).

## 1. One endpoint

Everything goes through `POST /v1/messages`. Tools, structured outputs, thinking, caching and citations are features
of that one endpoint. Supporting endpoints:

| Endpoint | Purpose |
|---|---|
| `POST /v1/messages` | Generate a response (optionally streamed) |
| `POST /v1/messages/count_tokens` | Count input tokens before you send (free, rate-limited separately) |
| `POST /v1/messages/batches` | Submit asynchronous batch work at 50% of standard prices |
| `POST /v1/files` | Upload a file once, reference it by `file_id` later |
| `GET /v1/models`, `GET /v1/models/{id}` | Discover models available to your organisation, their context window (`max_input_tokens`) and output cap |

## 2. Request shape (Python SDK)

```python
import anthropic

client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY from the environment; never hardcode keys

response = client.messages.create(
    model="claude-opus-5-5",                 # exact ID, no date suffix
    max_tokens=16000,                        # hard cap on output tokens for this response
    system="You are a concise assistant for Acme Logistics dispatchers.",
    messages=[
        {"role": "user", "content": "Summarise today's three delayed shipments."},
    ],
    thinking={"type": "adaptive"},           # optional; adaptive is the only on-mode on current models
    output_config={"effort": "medium"},      # low | medium | high | xhigh | max
)

if response.stop_reason == "end_turn":
    print("".join(b.text for b in response.content if b.type == "text"))
```

| Field | Required | Notes |
|---|---|---|
| `model` | Yes | `claude-opus-5-5` (default), `claude-sonnet-5-5`, `claude-haiku-5-5`, `claude-fable-5-1` |
| `max_tokens` | Yes | Output ceiling. Around 16,000 for non-streaming; up to 128K with streaming |
| `messages` | Yes | Alternating `user` / `assistant`; first message is `user`; **last must not be `assistant`** (no prefill) |
| `system` | No | String or list of content blocks; the operator's instructions |
| `tools` | No | Client tools (`name`, `description`, `input_schema`, optional `strict: true`) or server tools (`type`) |
| `tool_choice` | No | `auto` (default) or `none`. `any` and `tool` return a 400 on Claude Opus 5.5, Sonnet 5.5, Fable 5.1 and Mythos 5.1; Haiku 5.5 accepts them |
| `thinking` | No | `{"type": "adaptive"}` or omit. `budget_tokens` is legacy and rejected on current models |
| `output_config` | No | `effort`, `format` (structured outputs), `task_budget` (beta) |
| `stream` | No | `true` for server-sent events; SDKs offer `.stream()` helpers |

**Do not send** `temperature`, `top_p` or `top_k`. Opus 5.5 rejects them, Sonnet 5.5 and Haiku 5.5 reject non-default
values, and on API version `2026-10-21` every model rejects them with a 400. Shape output with
instructions, examples, effort and structured outputs instead.

## 3. Response and stop reasons

```json
{
  "id": "msg_...",
  "type": "message",
  "role": "assistant",
  "model": "claude-opus-5-5",
  "content": [{"type": "text", "text": "..."}],
  "stop_reason": "end_turn",
  "stop_details": null,
  "usage": {"input_tokens": 812, "output_tokens": 240,
            "cache_creation_input_tokens": 0, "cache_read_input_tokens": 0}
}
```

Always branch on `stop_reason` before you use `content`:

| `stop_reason` | Meaning | What your code does |
|---|---|---|
| `end_turn` | Claude finished naturally | Use the content |
| `max_tokens` | Hit your `max_tokens` cap; output is truncated | Raise the cap, stream, or ask for shorter output. Never parse truncated JSON |
| `stop_sequence` | Hit one of your `stop_sequences` | Use content up to the sequence |
| `tool_use` | Claude wants one or more tools run | Execute every `tool_use` block, return all `tool_result` blocks in **one** user message, call again |
| `pause_turn` | A long server-tool turn paused | Send the response back as-is to let Claude continue |
| `refusal` | A safety classifier declined | Read `stop_details.category` / `explanation`; do not retry blindly; consider the server-side `fallbacks` option |
| `model_context_window_exceeded` | The conversation reached the model's context window | Compact, trim or summarise history, then retry |

## 4. Content blocks you will meet

| Block | Direction | Purpose |
|---|---|---|
| `text` | both | Plain text; may carry `citations` |
| `image` | user | Base64, URL or `file_id` source |
| `document` | user | PDF or text; base64, URL or `file_id`; set `citations: {"enabled": true}` for grounded answers |
| `tool_use` | assistant | `id`, `name`, `input` (parse with `json.loads`, never string-match) |
| `tool_result` | user | `tool_use_id`, `content`, optional `is_error: true` |
| `thinking` | assistant | Reasoning summary or empty text; pass back unchanged on later turns |
| `server_tool_use` / `*_tool_result` | assistant | Web search, web fetch, code execution results |

## 5. Structured outputs

Two ways to guarantee machine-readable output (no prefill needed):

```python
from pydantic import BaseModel

class Ticket(BaseModel):
    category: str
    priority: int
    summary: str

parsed = client.messages.parse(           # SDK helper: validates against the model class
    model="claude-opus-5-5",
    max_tokens=2048,
    messages=[{"role": "user", "content": "Triage: 'Scanner at dock 4 offline since 06:10'"}],
    output_format=Ticket,
)
ticket = parsed.parsed_output
```

```python
raw = client.messages.create(            # raw JSON Schema form
    model="claude-opus-5-5",
    max_tokens=2048,
    messages=[{"role": "user", "content": "..."}],
    output_config={"format": {"type": "json_schema", "schema": {
        "type": "object",
        "properties": {"category": {"type": "string"}, "priority": {"type": "integer"}},
        "required": ["category", "priority"],
        "additionalProperties": False,
    }}},
)
```

- `strict: true` on a **tool definition** guarantees the tool's `input` validates against its schema
  (needs `additionalProperties: false` and `required`).
- The old top-level `output_format` parameter on `messages.create()` is deprecated; use `output_config.format`.
- Structured outputs and document citations cannot be combined in one request (400).

## 6. Prompt caching

| Rule | Detail |
|---|---|
| Prefix match | Render order is `tools` → `system` → `messages`; any byte change invalidates everything after it |
| Breakpoints | Up to 4 `cache_control: {"type": "ephemeral"}` markers, or one top-level `cache_control` for automatic caching |
| TTL | 5 minutes by default; `"ttl": "1h"` for longer gaps. Reads refresh the timer |
| Price | Writes cost about 1.25x base input (5 min) or 2x (1 h); reads about 0.1x (0.05x on Claude Opus 5.5) |
| Minimum | Model-dependent minimum prefix (512 tokens on the current generation); shorter prefixes silently do not cache |
| Verify | `usage.cache_read_input_tokens > 0` on the second and later requests |
| Silent breakers | Timestamps or request IDs in the system prompt, unsorted JSON, a tool list that changes per request, switching models |

```python
system = [
    {"type": "text", "text": LONG_STABLE_POLICY_TEXT, "cache_control": {"type": "ephemeral"}},
]
```

Details: [04 · Prompt caching](../04-context-engineering/03-prompt-caching.md).

## 7. Streaming

```python
with client.messages.stream(model="claude-opus-5-5", max_tokens=64000, messages=msgs) as stream:
    for text in stream.text_stream:
        print(text, end="", flush=True)
    final = stream.get_final_message()   # full Message with stop_reason and usage
```

Raw event order: `message_start` → (`content_block_start` → `content_block_delta`\* → `content_block_stop`)\* →
`message_delta` (carries `stop_reason` and final usage) → `message_stop`. `ping` events can appear anywhere; an
`error` event can arrive mid-stream. Stream whenever `max_tokens` is large or output is long, to avoid HTTP timeouts.
Details: [06 · Streaming](../06-claude-api/03-streaming.md).

## 8. Message Batches

| Fact | Value |
|---|---|
| Discount | 50% of standard token prices |
| Size | Up to 100,000 requests or 256 MB per batch |
| Completion | Most within 1 hour; maximum 24 hours, then unfinished requests `expired` |
| Results | Available for 29 days; arrive in **any order**, so key by `custom_id` |
| Result types | `succeeded`, `errored`, `canceled`, `expired` |

```python
batch = client.messages.batches.create(requests=[
    {"custom_id": "doc-001", "params": {"model": "claude-haiku-5-5", "max_tokens": 1024,
                                         "messages": [{"role": "user", "content": "Classify: ..."}]}},
])
# poll client.messages.batches.retrieve(batch.id).processing_status until "ended"
for item in client.messages.batches.results(batch.id):
    print(item.custom_id, item.result.type)
```

Details: [06 · Batch processing](../06-claude-api/05-batch-processing.md).

## 9. Errors

| HTTP | `error.type` | Retry? | Typical fix |
|---|---|---|---|
| 400 | `invalid_request_error` | No | Fix the body: roles, banned params, prefill, forced `tool_choice`, schema |
| 401 | `authentication_error` | No | Set `ANTHROPIC_API_KEY`; do not send both an API key and an auth token |
| 402 | `billing_error` | No | Resolve billing in the Console |
| 403 | `permission_error` | No | Credential or workspace not allowed this operation |
| 404 | `not_found_error` | No | Model ID typo, or model not available to your organisation; list `GET /v1/models` |
| 413 | `request_too_large` | No | Shrink the request: split documents, resize images, use the Files API |
| 429 | `rate_limit_error` | Yes | Honour `retry-after`; smooth traffic; cache; batch |
| 500 | `api_error` | Yes | Retry with exponential backoff and jitter |
| 529 | `overloaded_error` | Yes | Back off; queue; consider another model for non-critical traffic |

The SDKs retry 408, 409, 429, 5xx and connection errors twice by default (`max_retries`). Catch typed exceptions from
most to least specific (`RateLimitError` → `APIStatusError` → `APIConnectionError`). Log the `request-id` header.
Full guide: [24 · API errors](../24-troubleshooting/api-errors.md).

## 10. Tool-use loop in a dozen lines

```python
messages = [{"role": "user", "content": question}]
while True:
    resp = client.messages.create(model="claude-opus-5-5", max_tokens=4096, tools=TOOLS, messages=messages)
    messages.append({"role": "assistant", "content": resp.content})
    if resp.stop_reason != "tool_use":
        if resp.stop_reason != "end_turn":   # max_tokens, refusal, pause_turn...: handle, don't ignore
            raise RuntimeError(f"stopped with {resp.stop_reason}; see the stop_reason table")
        break
    results = [{"type": "tool_result", "tool_use_id": b.id, "content": run_tool(b.name, b.input)}
               for b in resp.content if b.type == "tool_use"]
    messages.append({"role": "user", "content": results})
```

Add a maximum-iteration guard, validate `b.input` before running anything, and return failures as
`is_error: true` results rather than dropping them. Details: [07 · The tool-use loop](../07-tool-use-and-function-calling/03-the-tool-use-loop.md).

## Further reading

- [Messages API reference](https://platform.claude.com/docs/en/api/messages)
- [Models overview](https://platform.claude.com/docs/en/about-claude/models/overview) and [pricing](https://platform.claude.com/docs/en/about-claude/pricing)
- [Prompt caching](https://platform.claude.com/docs/en/build-with-claude/prompt-caching)
- [Batch processing](https://platform.claude.com/docs/en/build-with-claude/batch-processing)
- [Errors](https://platform.claude.com/docs/en/api/errors)
