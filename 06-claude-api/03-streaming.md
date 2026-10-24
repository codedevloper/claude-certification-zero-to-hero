# Streaming

> **Level:** Intermediate · **Time:** ~40 min · **Exam relevance:** CCAR-P D3, D4

## In plain English

Without streaming, your application sends a request and waits, sometimes for a minute or more, until Claude has
written the entire answer. With **streaming**, the API sends the answer in small pieces as it is generated, so you can
show text to the user immediately, the way the Claude apps do.

Streaming does not make Claude finish sooner. It makes the wait *feel* shorter (time to first token instead of time to
last token), and it keeps long-running requests healthy: an open stream with steady traffic is less likely to be cut
off by timeouts than a silent connection waiting many minutes for one big reply.

## Why it matters

- **User experience.** Interactive applications should show progress within a second or two.
- **Long outputs need it.** Current models can produce up to 128,000 output tokens (as of 2026-10-24). The Python SDK
  refuses non-streaming requests it estimates would exceed about ten minutes, and recommends streaming instead.
- **Agents and tools.** Streaming lets you show intermediate progress during tool use and react to tool calls as they
  form.
- **Exam relevance.** Accuracy–latency trade-offs (CCAR-P-3.3) and latency optimisation (CCAR-P-4.5) include knowing
  that streaming improves perceived latency but not total generation time or cost.

## How it works

### Server-sent events

Set `"stream": true` and the API responds with a stream of server-sent events (SSE):

| Event | When | Contains |
|---|---|---|
| `message_start` | Once, first | Message metadata and initial usage |
| `content_block_start` | Each new block | Block type (text, thinking, tool_use, ...) |
| `content_block_delta` | Many times | A fragment: `text_delta`, `thinking_delta`, `input_json_delta` (tool input), `signature_delta` |
| `content_block_stop` | End of each block | |
| `message_delta` | Near the end | `stop_reason`, final output token usage |
| `message_stop` | Once, last | |
| `ping` | Any time | Keep-alive; ignore |
| `error` | Any time | An error that occurred after the HTTP 200 started, for example `overloaded_error` |

Two consequences:

1. **The HTTP status is 200 before generation is finished.** Errors can still arrive mid-stream as `error` events,
   and the SDK raises them as exceptions while you iterate.
2. **`stop_reason` arrives at the end** in `message_delta`. You only know whether the answer was complete, truncated
   or refused once the stream finishes.

### The SDK helpers

| Approach | Use when |
|---|---|
| `client.messages.stream(...)` with `text_stream` | You want to display text as it arrives (most applications) |
| `client.messages.stream(...)` then `get_final_message()` | You want streaming's timeout protection but only need the full message |
| `client.messages.create(..., stream=True)` | You want raw events with minimal memory use and will assemble the message yourself |
| `AsyncAnthropic().messages.stream(...)` | Async web frameworks and high concurrency |

`messages.stream()` accumulates the full message for you, so you can stream to the user *and* get a complete,
correctly typed `Message` (with `stop_reason`, `usage` and all content blocks) at the end.

### Thinking and streaming

On current models the default thinking display is `"omitted"`: thinking blocks stream with empty text. For users, that
looks like a pause before the first visible word. Either show a progress indicator, or request
`thinking={"type": "adaptive", "display": "summarized"}` to stream a readable reasoning summary. Thinking is billed the
same either way.

### Refusals and errors mid-stream

- If a request is declined after some text has streamed, the stream ends with `stop_reason == "refusal"`. Discard or
  clearly retract the partial text; do not leave it on screen as if it were an answer.
- If the stream fails with an error event (for example overload), the SDK raises an exception. Decide whether to retry
  the whole request; you cannot resume a broken stream from the middle.

### Tool use while streaming

When streaming with your own tools, tool inputs arrive as `input_json_delta` fragments. By default the API buffers and
validates a tool's input before streaming it. Setting `eager_input_streaming: true` on a tool definition streams large
inputs as they are generated, but then your code must validate the parsed input against the schema before running the
tool, and must check for `max_tokens` or `refusal` before executing anything. Tool use is covered in
[Module 07](../07-tool-use-and-function-calling/03-the-tool-use-loop.md).

## Example

A streaming helper for an internal *Contoso Health* (fictional) policy assistant. It prints text as it arrives,
retrieves the complete message at the end, and handles truncation, refusal and mid-stream errors.

```python
import sys

import anthropic

client = anthropic.Anthropic()  # API key from ANTHROPIC_API_KEY


def stream_answer(question: str) -> str | None:
    try:
        with client.messages.stream(
            model="claude-opus-5-5",
            max_tokens=32000,
            output_config={"effort": "medium"},
            system="You explain Contoso Health's internal IT policies to staff in plain English.",
            messages=[{"role": "user", "content": question}],
        ) as stream:
            for text in stream.text_stream:
                sys.stdout.write(text)
                sys.stdout.flush()
            final = stream.get_final_message()
    except anthropic.APIStatusError as exc:      # includes errors raised mid-stream
        print(f"\n[stream failed: {exc.status_code} {exc.type}; request {exc.request_id}]")
        return None
    except anthropic.APIConnectionError:
        print("\n[connection lost; please try again]")
        return None

    print()
    if final.stop_reason == "refusal":
        print("[The answer above was withdrawn. Please contact the IT service desk.]")
        return None
    if final.stop_reason == "max_tokens":
        print("[Answer truncated.]")
    print(f"[tokens: {final.usage.input_tokens} in, {final.usage.output_tokens} out]")
    return "".join(b.text for b in final.content if b.type == "text")


stream_answer("Can I use my personal laptop to access email from home?")
```

Async version for a web service (for example FastAPI with server-sent events to the browser):

```python
import anthropic

async_client = anthropic.AsyncAnthropic()


async def answer_events(question: str):
    async with async_client.messages.stream(
        model="claude-opus-5-5",
        max_tokens=8000,
        messages=[{"role": "user", "content": question}],
    ) as stream:
        async for text in stream.text_stream:
            yield {"event": "token", "data": text}
        final = await stream.get_final_message()
        yield {"event": "done", "data": final.stop_reason}
```

Raw HTTP with cURL (`-N` disables buffering so you see events as they arrive):

```bash
curl -N https://api.anthropic.com/v1/messages \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -H "content-type: application/json" \
  -d '{
    "model": "claude-opus-5-5",
    "max_tokens": 1000,
    "stream": true,
    "messages": [{"role": "user", "content": "Explain streaming in one paragraph."}]
  }'
```

> **Cost:** requires API credits (live mode). Streaming costs the same as non-streaming for the same tokens.

## Enterprise use case

*Tailspin Travel* (fictional) generates personalised multi-day itineraries that can run to several thousand words.
The first implementation used non-streaming requests with a 60-second gateway timeout; long itineraries regularly
failed, and users stared at a spinner.

The redesign streams from Claude through the backend to the browser using server-sent events, shows the first day
within a couple of seconds, and keeps the full message for storage. The gateway's idle timeout was adjusted for
streaming connections. Two edge cases were handled explicitly: if the stream ends with a refusal, the partial
itinerary is removed from the screen and replaced with a message; if the connection drops, the client offers a retry
that re-requests the whole itinerary rather than trying to stitch fragments.

## Common mistakes

- **Treating HTTP 200 as success.** Errors and refusals can occur after streaming starts.
- **Reading `stop_reason` from the first events.** It only arrives at the end.
- **Building your own accumulator** when `messages.stream()` and `get_final_message()` already do it correctly.
- **Leaving refused partial text on screen.**
- **Assuming streaming reduces cost or total latency.** It improves perceived latency and robustness only.
- **Proxies that buffer.** Some reverse proxies buffer SSE responses and destroy the streaming effect; disable
  buffering for these routes.

## Security considerations

- **Output filtering is harder when streaming.** If you must block certain content (for example personal data), you
  either filter incrementally with a small buffer or hold back display until a check passes. Design this explicitly for
  high-risk applications.
- **Partial output can be harmful.** A refusal or later correction does not erase what the user already saw; for
  sensitive domains consider buffering per paragraph.
- **Escape streamed text** before inserting it into HTML, exactly as you would a complete response.
- **Resource exhaustion.** Long-lived streams hold connections; set per-user concurrency limits on your backend.

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| `ValueError` about long requests without streaming | Large `max_tokens` on a non-streaming call | Use `messages.stream()` (with `get_final_message()` if you only need the result) |
| Long silence before first text | Thinking display `"omitted"`, or high effort | Show progress, request `display: "summarized"`, or lower effort |
| Text arrives all at once at the end | A proxy or framework buffers the response | Disable buffering (for example `X-Accel-Buffering: no` on nginx); flush after each chunk |
| Exception after some text appeared | Mid-stream error event (for example overload) | Catch `APIStatusError`; retry the whole request with backoff |
| Final message missing tool input fields | Eager input streaming with truncated JSON | Check `stop_reason`; validate tool input before executing |

## Check your understanding

1. What does streaming improve, and what does it not improve?
2. Why can a streaming request fail after returning HTTP 200?
3. When would you use `get_final_message()` without displaying the stream?
4. A stream ends with `stop_reason == "refusal"` after two paragraphs were shown. What should the UI do?

<details>
<summary>Answers</summary>

1. It improves time to first token (perceived latency) and robustness for long requests. It does not reduce total
   generation time or token cost.
2. The status is sent when streaming begins; errors that occur during generation (such as overload) arrive later as
   `error` events, which the SDK raises as exceptions.
3. For long or high-`max_tokens` requests where you need only the complete result: streaming avoids HTTP timeouts and
   the SDK's long-request guard, and `get_final_message()` returns the assembled message.
4. Remove or clearly withdraw the partial text, show a clear message explaining the request could not be completed,
   and log the refusal category.

</details>

## Further reading

- [Streaming messages](https://platform.claude.com/docs/en/build-with-claude/streaming) (Anthropic docs)
- [Fine-grained tool streaming](https://platform.claude.com/docs/en/agents-and-tools/tool-use/fine-grained-tool-streaming) (Anthropic docs)
- [Latency optimisation](../15-production-operations/04-latency-optimisation.md) in this repository
- [Lab 07 — API integration](../19-hands-on-labs/lab-07-api-integration/README.md)

<!-- page-nav:start -->
---

[← Previous: The Messages API](02-messages-api.md) · [Module overview](README.md) · [Next: Vision, Documents, the Files API and Citations →](04-vision-documents-and-citations.md)
<!-- page-nav:end -->
