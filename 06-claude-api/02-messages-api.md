# The Messages API

> **Level:** Beginner → Intermediate · **Time:** ~60 min · **Exam relevance:** CCAR-P D1, D2, D3, D5

## In plain English

Almost everything you do with Claude through the API goes through one endpoint: `POST /v1/messages`. You send a
list of messages (the conversation so far) plus settings, and you get back one assistant message.

Three ideas carry most of the weight:

- **Messages have roles.** `user` messages come from your application or end user; `assistant` messages are Claude's
  earlier replies. A separate `system` parameter holds the standing instructions.
- **Content is made of blocks.** A message is not just a string; it is a list of typed blocks: text, images,
  documents, tool calls, tool results, thinking.
- **Every response says why it stopped.** The `stop_reason` tells you whether Claude finished, ran out of room, wants
  to use a tool, paused, or declined. Your code must check it before using the content.

The API is **stateless**: Claude does not remember earlier requests. To continue a conversation, you send the whole
history again.

## Why it matters

- It is the foundation for every other API feature: tools, structured outputs, caching, batches and agents are all
  options on this one endpoint.
- Mishandled stop reasons are a top cause of production bugs: truncated JSON treated as complete, refusals shown as
  blank answers, tool requests ignored.
- Architects need to reason about request design (what goes in `system` versus messages, which effort level, which
  model) for cost, latency and safety (CCAR-P-1.2, 2.1, 3.3, 5.1).

## How it works

### Request anatomy

```python
response = client.messages.create(
    model="claude-opus-5-5",                 # required: exact model ID
    max_tokens=4000,                          # required: ceiling on output, including thinking
    system="You are ...",                     # optional: standing instructions (string or text blocks)
    messages=[...],                           # required: the conversation, starting with a user turn
    output_config={"effort": "medium"},       # optional: low | medium | high | xhigh | max; also "format"
    thinking={"type": "adaptive"},            # optional on current models; adaptive is the default on Opus 5.5
    tools=[...],                              # optional: tool definitions (Module 07)
    tool_choice={"type": "auto"},             # optional: auto or none on Opus 5.5, Sonnet 5.5, Fable 5.1 and Mythos 5.1
    stop_sequences=["</answer>"],             # optional: custom stop strings
    metadata={"user_id": "hashed-user-123"},  # optional: an opaque end-user identifier for abuse monitoring
)
```

| Parameter | Key rules (as of 2026-10-24) |
|---|---|
| `model` | Use published IDs exactly (`claude-opus-5-5`, `claude-sonnet-5-5`, `claude-haiku-5-5`, `claude-fable-5-1`); no date suffixes |
| `max_tokens` | Hard limit; if reached, `stop_reason` is `max_tokens`. Around 16,000 is a reasonable non-streaming default; use [streaming](03-streaming.md) for very large values |
| `messages` | Must start with a `user` turn. The final turn must not be a prefilled `assistant` turn: current models reject prefill with a 400 error |
| `temperature`, `top_p`, `top_k` | Do not send them. Current models reject them |
| `thinking` | `{"type": "adaptive"}` or omitted. `budget_tokens` is legacy and rejected on current models; Claude Opus 5.5 cannot disable thinking |
| `output_config.effort` | Main depth and cost control; Claude Opus 5.5 defaults to `medium`, Claude Sonnet 5.5 to `high`. Set it explicitly |
| `output_config.format` | JSON Schema [structured outputs](../03-prompt-engineering/06-structured-output.md) |
| `tool_choice` | `any` and `tool` (forcing a call) are rejected on several current models; use `auto` plus instructions, or `none` |

### Roles and turns

```python
messages = [
    {"role": "user", "content": "Our warehouse in Leeds has 3 loading bays. How many trucks per hour can it handle?"},
    {"role": "assistant", "content": "It depends on turnaround time per truck. What is the average?"},
    {"role": "user", "content": "About 40 minutes."},
]
```

- The first message is a `user` message.
- Consecutive messages with the same role are combined into one turn.
- `system` is a separate top-level field, not a message. On models that support it (as of 2026-10-24: Claude Opus 5.5,
  Claude Sonnet 5.5 and several others), you can also append `{"role": "system", "content": ...}` later in `messages`
  for operator instructions that arrive mid-conversation. This avoids rewriting the cached top-level system prompt.

### Content blocks

`content` can be a plain string (shorthand for one text block) or a list of blocks.

| Block type | Appears in | Purpose |
|---|---|---|
| `text` | user, assistant | Ordinary text |
| `image` | user | Images by base64, URL or Files API reference ([vision](04-vision-documents-and-citations.md)) |
| `document` | user | PDFs and text documents, optionally with citations |
| `search_result` | user, tool results | Your own retrieved passages, citable like documents |
| `tool_use` | assistant | Claude asks your application to run a tool |
| `tool_result` | user | Your application returns the tool's output |
| `thinking` | assistant | Claude's reasoning (summarised or omitted); pass back unchanged |
| Server-tool blocks | assistant | Results of Anthropic-hosted tools such as web search or code execution |

Always iterate over `response.content` and check each block's `type`. Do not assume `content[0]` is text: with
thinking on, the first block is often a `thinking` block.

### The response object

```json
{
  "id": "msg_...",
  "type": "message",
  "role": "assistant",
  "model": "claude-opus-5-5",
  "content": [{"type": "text", "text": "..."}],
  "stop_reason": "end_turn",
  "stop_details": null,
  "usage": {"input_tokens": 512, "output_tokens": 230,
            "cache_creation_input_tokens": 0, "cache_read_input_tokens": 0}
}
```

### Stop reasons

| `stop_reason` | Meaning | What your code should do |
|---|---|---|
| `end_turn` | Claude finished naturally | Use the content |
| `max_tokens` | Hit your `max_tokens` limit | Treat output as incomplete: raise the limit, stream, or ask Claude to continue in a new user turn |
| `stop_sequence` | Hit one of your `stop_sequences` | Use the content; `stop_sequence` says which one |
| `tool_use` | Claude wants to call a tool | Run the tool(s), return `tool_result` blocks, call again ([the tool-use loop](../07-tool-use-and-function-calling/03-the-tool-use-loop.md)) |
| `pause_turn` | A long-running server-side turn paused | Send the response back as-is to let Claude continue |
| `refusal` | Claude, or a safety classifier, declined the request | Do not treat partial content as an answer; read `stop_details`; show a safe message or fall back |
| `model_context_window_exceeded` | The model ran out of context window | Reduce input; see [Module 04](../04-context-engineering/README.md) |

### Handling refusals

A refusal arrives as a normal HTTP 200 response with `stop_reason == "refusal"`. On current models, `stop_details`
gives a `category` (an open set, for example `"cyber"`, `"bio"` or `"reasoning_extraction"`, or `null`) and an
`explanation`. Good practice:

1. Check `stop_reason` before reading `content`; discard any partial text from a mid-stream refusal.
2. Show the user a clear, non-technical message, and log the category for review.
3. Consider whether a legitimate request was phrased in a way that looks risky, and rephrase the prompt.
4. On the Claude API and Claude Platform on AWS, you can opt in to **server-side fallbacks**, which re-run a declined
   request on a model Anthropic recommends for that refusal category, within the same call. As of 2026-10-24 this is a
   beta (`fallbacks="default"` with the `server-side-fallback-2026-07-01` header); on Amazon Bedrock, Vertex AI and
   Microsoft Foundry, the SDKs provide client-side middleware instead. Check the
   [refusals and fallback docs](https://platform.claude.com/docs/en/build-with-claude/refusals-and-fallback) for
   billing and current behaviour.

### Effort

`output_config={"effort": ...}` trades thoroughness against tokens and latency on a single model. Lower effort means
less thinking, fewer and more consolidated tool calls and terser output. Pick the level per route and measure (see
[reasoning and thinking](../03-prompt-engineering/04-reasoning-and-thinking.md)).

### Multi-turn conversations

Because the API is stateless, your application stores the history and resends it. When responses contain thinking or
tool blocks, append the **full** `response.content` as the assistant turn, not just the text, and keep history
append-only (do not edit earlier turns).

## Example

A reusable helper for *Acme Logistics* (fictional) that handles every stop reason explicitly and opts in to
server-side fallback for refusals on the first-party API.

```python
import logging

import anthropic

log = logging.getLogger("claude")
client = anthropic.Anthropic()  # API key from ANTHROPIC_API_KEY

SYSTEM = ("You answer Acme Logistics staff questions about shipping operations. "
          "Be concise and say when you are unsure.")


class IncompleteResponse(Exception):
    pass


def ask(history: list[dict], question: str, effort: str = "medium") -> str:
    history.append({"role": "user", "content": question})
    response = client.beta.messages.create(
        model="claude-opus-5-5",
        max_tokens=4000,
        system=SYSTEM,
        output_config={"effort": effort},
        betas=["server-side-fallback-2026-07-01"],   # opt in to category-based refusal fallback
        fallbacks="default",
        messages=history,
    )
    log.info("request_id=%s stop=%s in=%s out=%s", response._request_id, response.stop_reason,
             response.usage.input_tokens, response.usage.output_tokens)

    match response.stop_reason:
        case "end_turn" | "stop_sequence":
            history.append({"role": "assistant", "content": response.content})  # full content
            return "".join(b.text for b in response.content if b.type == "text")
        case "max_tokens":
            raise IncompleteResponse("Answer cut off; raise max_tokens or stream.")
        case "refusal":
            category = response.stop_details.category if response.stop_details else None
            log.warning("refusal category=%s", category)
            history.pop()  # do not keep the declined turn in the conversation
            return "Sorry, I can't help with that request. Please contact the operations desk."
        case other:
            raise IncompleteResponse(f"Unhandled stop_reason: {other}")


conversation: list[dict] = []
print(ask(conversation, "What documents does a pallet shipment to Norway need?"))
print(ask(conversation, "And for Switzerland?"))
```

The equivalent minimal cURL request, showing system, effort and the response fields to inspect:

```bash
curl https://api.anthropic.com/v1/messages \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -H "content-type: application/json" \
  -d '{
    "model": "claude-opus-5-5",
    "max_tokens": 2000,
    "system": "You answer shipping-operations questions concisely.",
    "output_config": {"effort": "low"},
    "messages": [{"role": "user", "content": "What is a bill of lading?"}]
  }' | python -c "import json,sys; r=json.load(sys.stdin); print(r['stop_reason']); print(r['usage'])"
```

> **Cost:** requires API credits (live mode).

## Enterprise use case

*Fabrikam Insurance* (fictional) audited its first three Claude integrations before scaling up. Findings:

- One service read `response.content[0].text` directly. When thinking was enabled, `content[0]` became a thinking
  block and the service returned empty strings. Fixed by iterating over blocks by type.
- A document-extraction job did not check `max_tokens`; about one long document in fifty produced truncated JSON that
  failed silently downstream. Fixed with an explicit check, a larger `max_tokens` and streaming.
- Refusals were displayed as blank answers. The team now shows a clear message, logs the category, and enables
  fallback where its platform supports it.

The audit produced an internal "response handling" library used by every team, with tests for each stop reason.

## Common mistakes

- **Using `content[0].text` blindly.** Iterate over blocks and check `type`.
- **Ignoring `stop_reason`.** Truncation, refusals and tool requests all look like "a response" otherwise.
- **Sending `temperature` or prefill** carried over from older code.
- **Appending only text to history** when the response contained thinking or tool-use blocks.
- **Forcing tool calls with `tool_choice` `any` or `tool`** on models that reject it.
- **Rewriting earlier turns** in a stored conversation.
- **Not setting effort explicitly**, so behaviour shifts when the model or its default changes.

## Security considerations

- **User input goes in `user` turns, operator instructions in `system`.** Do not concatenate untrusted text into the
  system prompt.
- **`metadata.user_id`** should be an opaque identifier (for example a hash), never an email address or name.
- **Treat output as untrusted.** Escape before rendering; validate before acting. See
  [insecure output handling](../12-ai-security/06-insecure-output-handling.md).
- **Log safely.** Request IDs, token counts and stop reasons are safe to log widely; prompts and outputs may contain
  personal data and need controlled storage.
- **Refusal handling is part of your safety design**, not an error to retry blindly.

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| 400: roles must alternate / first message must be user | Malformed `messages` | Start with a user turn; check history construction |
| 400 mentioning prefill or assistant last turn | Prefilled final assistant message | Remove it; use structured outputs or instructions |
| 400 mentioning `temperature` or `budget_tokens` | Legacy parameters | Remove sampling parameters; use adaptive thinking and effort |
| 400 on `tool_choice` | Forced tool use on a model that rejects it | Use `auto` with an instruction, or structured outputs |
| Empty text in output | First block is `thinking` | Iterate over blocks |
| Answers end mid-sentence | `stop_reason == "max_tokens"` | Raise `max_tokens`, stream, or lower effort |

## Check your understanding

1. Why must your application resend the full conversation on every request?
2. List the stop reasons and the correct action for `max_tokens`, `tool_use` and `refusal`.
3. Why is `response.content[0].text` fragile?
4. What replaces assistant prefill for forcing a JSON response?
5. Where should a new operator instruction that arrives mid-conversation go on a model that supports it, and why?

<details>
<summary>Answers</summary>

1. The API is stateless; Claude only sees what is in the current request.
2. `end_turn`, `max_tokens`, `stop_sequence`, `tool_use`, `pause_turn`, `refusal` (and
   `model_context_window_exceeded`). For `max_tokens`, treat the output as incomplete and raise the limit, stream, or
   continue; for `tool_use`, run the tools and return `tool_result` blocks; for `refusal`, do not use partial content,
   show a safe message, log `stop_details`, and optionally use fallbacks.
3. The first block may be a `thinking`, `tool_use` or server-tool block rather than text.
4. Structured outputs: `output_config.format` with a JSON Schema, or `client.messages.parse()` with a Pydantic model.
5. As a `{"role": "system", ...}` message appended to `messages`, because editing the top-level system prompt changes
   the prefix and invalidates the cached conversation.

</details>

## Further reading

- [Messages API reference](https://platform.claude.com/docs/en/api/messages) (Anthropic docs)
- [Handling stop reasons](https://platform.claude.com/docs/en/build-with-claude/handling-stop-reasons) (Anthropic docs)
- [Refusals and fallback](https://platform.claude.com/docs/en/build-with-claude/refusals-and-fallback) (Anthropic docs)
- [Effort](https://platform.claude.com/docs/en/build-with-claude/effort) (Anthropic docs)
- [Lab 07 — API integration](../19-hands-on-labs/lab-07-api-integration/README.md)

<!-- page-nav:start -->
---

[← Previous: Getting Started with the API](01-getting-started-with-the-api.md) · [Module overview](README.md) · [Next: Streaming →](03-streaming.md)
<!-- page-nav:end -->
