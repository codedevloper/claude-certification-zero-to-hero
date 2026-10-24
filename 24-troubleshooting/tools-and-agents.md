# Troubleshooting: Tools and Agents

Agents fail in ways single calls do not: they loop, call the wrong tool, pass bad arguments, lose track of the goal
or stop too early. Most fixes live in **tool design, loop code and guardrails**, not only in the prompt. Concepts:
[07 · Tool use](../07-tool-use-and-function-calling/README.md), [10 · Agentic AI](../10-agentic-ai/README.md),
[10 · Agent reliability](../10-agentic-ai/07-agent-reliability.md).

> **As of 2026-10-24.** On current Claude models `tool_choice` accepts `auto` or `none` only; `any` and `tool`
> return a 400. Steer tool use with descriptions and instructions, and use `strict: true` for schema-valid arguments.

## Instrument the loop first

Log one line per turn: turn number, `stop_reason`, tool names and argument hashes, tool latency, `is_error`, and
cumulative `usage`. Without this, agent bugs are guesswork.

```python
for turn in range(MAX_TURNS):
    resp = client.messages.create(model=MODEL, max_tokens=4096, tools=TOOLS, messages=messages)
    calls = [b for b in resp.content if b.type == "tool_use"]
    log.info("turn=%d stop=%s tools=%s in=%d out=%d", turn, resp.stop_reason,
             [c.name for c in calls], resp.usage.input_tokens, resp.usage.output_tokens)
    ...
else:
    raise RuntimeError("agent exceeded MAX_TURNS")   # never loop forever
```

## Infinite or very long loops

**Symptom:** the agent keeps calling tools, repeats the same call, or runs until a budget or timeout stops it.

**Likely causes:**

- No stopping criterion: the task never says what "done" looks like.
- Tool results are ambiguous (empty list vs error), so Claude retries.
- Errors are swallowed or returned as success, so Claude cannot adapt.
- Results are huge and truncated, so the answer is never visible.
- The loop code forgets to append the assistant turn or the tool results, so Claude repeats itself.

**Diagnosis:** look for identical `(tool, arguments)` pairs in the turn log; read the tool results Claude actually saw;
confirm the message history grows correctly each turn.

**Fix:**

- State completion criteria: "Stop when you have the order status and the delivery date, then answer."
- Return explicit, informative results: `{"matches": [], "note": "No orders for that email. Ask the user to confirm it."}`.
- Return failures as `tool_result` with `is_error: true` and a helpful message.
- Paginate or summarise large results; include counts.
- Add a hard turn cap, a repeated-call detector and, on supported models, a **task budget** (beta) so Claude paces
  itself.
- Append `resp.content` (the full content, not just text) as the assistant turn every time.

## Tool errors

**Symptom:** tools raise exceptions, time out, or Claude passes invalid arguments.

**Likely causes:** the input schema is loose (free-text where an enum is needed); descriptions do not explain
formats; the tool assumes values Claude cannot know; external API failures.

**Diagnosis:** validate every `tool_use.input` against the schema and log rejections; group failures by tool and field.

**Fix:**

| Problem | Fix |
|---|---|
| Wrong types or missing fields | `strict: true` with `required` and `additionalProperties: false` |
| Wrong formats (dates, IDs) | Describe the format and give an example in the description; use `enum` or `pattern` |
| Arguments parsed by string matching | Always `json.loads` / use the SDK object; escaping differs between models |
| External API flakiness | Retries with backoff inside the tool; return a clear `is_error` result if it still fails |
| Unsafe values | Validate business rules in code (amount limits, allowed tenants) before executing |
| Missing `tool_result` for a call | Return exactly one result per `tool_use` id, all in **one** user message |

## Bad tool selection

**Symptom:** Claude uses the wrong tool, uses none when it should, or calls a tool for something it could answer.

**Likely causes:** overlapping tools with similar names; vague descriptions; too many tools (capability bloat); the
prompt never says when to use a tool.

**Diagnosis:** build a small routing test set (input → expected tool) and measure accuracy; list tool pairs that are
confused with each other.

**Fix:**

- Write descriptions like documentation for a new colleague: what it does, when to use it, when **not** to, what it
  returns.
- Merge overlapping tools, or namespace them (`crm_search_contacts`, `billing_search_invoices`).
- Remove tools the task does not need; for large tool sets, load tools on demand (tool search, Skills or sub-agents
  with focused toolsets).
- Add an instruction: "Use `lookup_shipment` for any question about a shipment's location or ETA."
- Keep `tool_choice: auto`; forced selection is not available on Opus 5.5, Sonnet 5.5, Fable 5.1 and Mythos 5.1.

See [07 · Tool design best practices](../07-tool-use-and-function-calling/05-tool-design-best-practices.md).

## No parallel calls, or everything in sequence

**Symptom:** independent lookups run one per turn, so the agent is slow.

**Likely cause:** results for parallel calls were split across several user messages in earlier turns, which teaches
Claude to stop calling in parallel; or `disable_parallel_tool_use` is set.

**Fix:** execute all `tool_use` blocks from one response (concurrently if safe) and return all results in a single
user message; tell Claude independent lookups can be done together.

## Agent stops too early or asks permission constantly

**Symptom:** the agent gives a partial answer or asks the user to confirm trivial steps.

**Likely causes:** low effort on a complex task; prompt says "ask if unsure" without saying what is safe to do alone;
`max_tokens` reached.

**Fix:** raise effort for long-horizon work; state what the agent may do autonomously and what needs approval;
check `stop_reason`; for long tasks give the full specification up front.

## Agent does something it should not

**Symptom:** a write, send or delete happened without the expected approval, or data crossed a boundary.

**Likely causes:** excessive agency (write tools available when only reads were needed); approval enforced by the
prompt rather than code; injected instructions in a tool result.

**Diagnosis:** trace the turn that issued the call and the content Claude read just before it.

**Fix:** enforce approvals in code (the tool refuses without a signed approval token); split read and write tools;
least-privilege credentials per tool; treat tool results as untrusted; add a regression eval. See
[12 · Tool misuse and excessive agency](../12-ai-security/05-tool-misuse-and-excessive-agency.md) and
[10 · Human in the loop](../10-agentic-ai/05-human-in-the-loop.md).

## Context overflow in long runs

**Symptom:** later turns get slower and costlier, quality drops, or requests fail for size.

**Likely causes:** every tool result kept verbatim; large file reads; no compaction.

**Fix:** trim or summarise old tool results (context editing), enable server-side compaction (beta) on supported
models, delegate reading-heavy subtasks to sub-agents that return summaries, and cache the stable prefix. See
[04 · Compaction and context editing](../04-context-engineering/05-compaction-and-context-editing.md).

## Multi-agent coordination problems

| Symptom | Likely cause | Fix |
|---|---|---|
| Sub-agents duplicate work | Vague task split | Give each sub-agent a distinct objective, output format and boundary |
| Orchestrator loses results | Sub-agents return huge transcripts | Require concise structured summaries |
| Costs explode | Too many agents for a simple task | Use a workflow or single agent; measure before adding agents |
| Conflicting edits | Shared resources without locking | Assign ownership; isolate work (separate branches or worktrees) |

See [10 · Multi-agent architecture](../10-agentic-ai/04-multi-agent-architecture.md).

## `pause_turn` and server tools

**Symptom:** a response with server tools (web search, code execution) ends with `stop_reason: "pause_turn"`.

**Fix:** append the assistant content and call again unchanged so Claude can continue. Server-tool errors arrive as
result blocks containing an error object, not as exceptions; branch on the content type.
