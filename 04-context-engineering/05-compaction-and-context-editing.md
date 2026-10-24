# Compaction and Context Editing

> **Level:** Advanced · **Time:** ~50 min · **Exam relevance:** CCAO-F D3 · CCAR-P D2, D3, D4

## In plain English

Long conversations and agent loops keep growing. Every turn adds messages, and every tool call adds its result. Left
alone, the context fills with material that was useful once but is now just weight: a 5,000-token search result
from an hour ago, or reasoning about a step that is long finished.

There are two server-side ways to shed that weight in the Claude API (both beta as of 2026-10-24):

- **Compaction** *summarises*: older turns are replaced by a summary that Claude writes, and the conversation
  continues from it. Think of a meeting secretary who condenses the first two hours into one page.
- **Context editing** *clears*: specific old items, such as tool results or thinking blocks, are removed by rule,
  while the rest of the conversation stays word for word. Think of clearing old printouts off the desk while keeping
  your notes.

In the Claude apps, the same idea appears as summarising a long chat and continuing in a new one; some products also
compact automatically.

## Why it matters

- **Agents can run longer.** Without context reduction, a long task hits the context limit or degrades in quality
  ("context rot", see [what is context engineering](01-what-is-context-engineering.md)).
- **Cost and latency.** Smaller requests are cheaper and faster.
- **Accuracy.** Stale tool results can mislead; removing them keeps the model focused on current information.
- **Exam relevance.** Optimising context windows and token usage (CCAR-P-2.4) and cost-performance (CCAR-P-4.5) include
  knowing when to summarise, clear or persist. Foundations covers the apps equivalent: restart, summarise or persist
  (CCAO-F-3.4).

## How it works

### Choosing a technique

| Technique | What it does | Keeps verbatim | Best for |
|---|---|---|---|
| **Context editing: tool-result clearing** | Removes the oldest tool results (optionally their inputs) once a trigger is reached, keeping the most recent few | Everything except cleared tool results | Agents whose history is dominated by large tool outputs |
| **Context editing: thinking clearing** | Removes thinking blocks from older assistant turns | Everything except cleared thinking | Long reasoning-heavy loops where old thinking is no longer needed |
| **Compaction** | Replaces earlier history with a model-written summary | Only what follows the summary | Long conversations where everything accumulates, not just tool results |
| **Client-side summarisation** | Your own code summarises and rewrites history | Whatever you choose | Platforms or models without server-side support; custom rules |
| **Fresh session plus notes or memory** | Start again, loading a progress file | Only the notes | Very long, multi-session work; agents that can rediscover state from files |

These combine well with [memory](04-memory-and-persistence.md): reduction keeps the window small, memory keeps what
must survive.

### Context editing (beta)

Enabled per request with the beta header `context-management-2025-06-27` and a `context_management` parameter. Editing
happens on the server before the model sees the prompt; **your client keeps its full history**.

Tool-result clearing, `clear_tool_uses_20250919` (fields and defaults as documented on 2026-10-24):

| Field | Default | Meaning |
|---|---|---|
| `trigger` | 100,000 input tokens | When clearing starts; input tokens or number of tool uses |
| `keep` | 3 tool uses | How many recent tool use/result pairs to keep |
| `clear_at_least` | none | Minimum tokens to clear each time, so a clear is worth the cache cost |
| `exclude_tools` | none | Tool names whose results are never cleared |
| `clear_tool_inputs` | `false` | Also clear the tool call parameters |

Thinking clearing, `clear_thinking_20251015`, has a `keep` setting (`{"type": "thinking_turns", "value": N}` or
`"all"`). When combining both strategies, list thinking clearing first. The response reports what was cleared in
`context_management.applied_edits`.

**Caching trade-off.** Clearing changes the prompt prefix from the clearing point onward, so it invalidates the cache
there. Use `clear_at_least` so each clear removes enough to be worth the new cache write.

### Compaction (beta)

Anthropic documents two forms (as of 2026-10-24):

| | Compaction at a token threshold | Compaction on demand |
|---|---|---|
| Who decides when | The API, when input tokens pass your trigger | Your code, by sending a compaction request |
| Beta header | `compact-2026-01-12` | `compact-2026-09-04` |
| Request shape | `context_management={"edits": [{"type": "compact_20260112", ...}]}` on normal requests | `compaction={"type": "summarize"}` on a separate request |
| Default trigger | 150,000 input tokens (minimum 50,000) | Whenever you choose |
| What you send back | Append the full `response.content`; the API ignores everything before the last compaction block | Replace the summarised messages with the returned block, placed first in `messages` |
| Anthropic's recommendation | Use when you want the API to manage context inside ordinary requests | Preferred where available; more control, can keep recent turns, can run in the background |

Both return a `compaction` content block holding the summary. Key rules:

- **Pass blocks back exactly as returned**, including any signature. Do not extract just the text.
- **Optional `instructions`** replace the default summarisation prompt entirely; say what must be preserved (names,
  decisions, open tasks) and that the model should not call tools.
- **Usage is reported per iteration.** The summarisation step is billed; sum `usage.iterations` to see total tokens.
- **Some content does not survive.** Images, documents and fetched pages inside summarised turns are gone afterwards;
  re-supply anything later turns need.
- **Check `stop_reason`.** On-demand compaction returns `stop_reason == "compaction"` when a summary was produced;
  other values (for example `max_tokens`) mean no summary came back and you should continue without one or retry.
- Compaction on demand and `context_management` cannot be combined in one request.

### Keep history append-only

On current models with preserved thinking (for example Claude Opus 5.5, as of 2026-10-24), editing earlier turns
yourself, such as deleting messages or rewriting a reminder, can invalidate thinking blocks and break caching. Prefer
the server-side features above, mid-conversation system messages for new operator instructions, and documented
compaction flows over hand-editing history. The API's error messages name the turn that changed if you get this wrong.

### Prompting for context awareness

If your harness compacts or saves state, tell Claude, so it does not wrap up early as the context fills:
"Your context will be compacted automatically as it approaches its limit, so you can keep working. Before that
happens, save progress and open tasks to memory."

## Example

An *Acme Logistics* (fictional) research agent that calls a search tool many times. Context editing clears old search
results, keeping the latest three, but never clears results from the `get_policy` tool.

```python
import anthropic

client = anthropic.Anthropic()  # API key from ANTHROPIC_API_KEY

response = client.beta.messages.create(
    model="claude-opus-5-5",
    max_tokens=8000,
    betas=["context-management-2025-06-27"],
    context_management={
        "edits": [{
            "type": "clear_tool_uses_20250919",
            "trigger": {"type": "input_tokens", "value": 60000},
            "keep": {"type": "tool_uses", "value": 3},
            "clear_at_least": {"type": "input_tokens", "value": 10000},
            "exclude_tools": ["get_policy"],
        }]
    },
    tools=TOOLS,          # defined elsewhere: search_shipments, get_policy, ...
    messages=history,     # the full, unedited conversation
)

for edit in (response.context_management.applied_edits if response.context_management else []):
    print("cleared:", edit)
```

Compaction on demand in a chat loop, compacting when the conversation passes a budget you choose:

```python
import anthropic

client = anthropic.Anthropic()
SYSTEM = "You help Acme Logistics planners design next quarter's network changes."
COMPACT_AT = 120_000      # choose a limit comfortably below the model's context window
history = []


def turn(user_text: str) -> str:
    global history
    history.append({"role": "user", "content": user_text})
    response = client.beta.messages.create(
        model="claude-opus-5-5", max_tokens=8000, system=SYSTEM,
        betas=["compact-2026-09-04"], messages=history,
    )
    history.append({"role": "assistant", "content": response.content})  # full content, not just text

    u = response.usage
    size = u.input_tokens + u.output_tokens + (u.cache_read_input_tokens or 0) + (u.cache_creation_input_tokens or 0)
    if size > COMPACT_AT:
        summary = client.beta.messages.create(
            model="claude-opus-5-5", max_tokens=6000, system=SYSTEM,   # same system and tools as the chat
            betas=["compact-2026-09-04"], messages=history,
            compaction={"type": "summarize",
                        "instructions": "Preserve every depot name, agreed decision, owner and open "
                                        "question. Do not call tools; reply with the summary only."},
        )
        if summary.stop_reason == "compaction":
            history = [{"role": "assistant", "content": summary.content}]  # block goes first
    return next((b.text for b in response.content if b.type == "text"), "")
```

> **Cost:** requires API credits (live mode). The summarisation call is billed like any other request.

Beta features change; check the [compaction](https://platform.claude.com/docs/en/build-with-claude/compaction) and
[context editing](https://platform.claude.com/docs/en/build-with-claude/context-editing) pages before relying on the
exact field names.

## Enterprise use case

*Northwind Lending* (fictional) runs an overnight agent that reconciles payment-file exceptions. Each exception
involves several lookups returning large JSON documents. The agent used to fail around exception 40 with context
errors, and its later answers occasionally referred to the wrong account's data.

The team applied three measures: tool-result clearing with a trigger well below the context limit and `keep` of 3,
excluding the small `get_reconciliation_rules` tool; a memory file that records each resolved exception in one line;
and an instruction telling the agent that old results are cleared and it should re-query rather than rely on recall.
The agent now processes the full overnight batch. Clearing also fixed the cross-account confusion, because old account
data is no longer in context to be confused with the current one. Cache-hit rates dropped slightly after each clear,
which the team accepted after measuring the net cost.

## Common mistakes

- **Appending only the text of a response** when compaction is on. The compaction block is lost and the API cannot
  replace the history.
- **Leaving summarised messages in front of an on-demand compaction block.** They get re-sent, or the request fails.
- **Clearing tools whose results are still needed**, such as policy lookups. Use `exclude_tools`.
- **Triggering clears too often** with small `clear_at_least` values, which repeatedly invalidates the cache.
- **Default summaries for specialised work.** Write `instructions` that name what must survive.
- **Hand-editing history** on models with preserved thinking.

## Security considerations

- **Summaries can drop safety-relevant context**, such as a user's earlier statement that they are not authorised
  for an action. Tell the summariser to preserve permissions, constraints and refusals.
- **Summaries can preserve injected instructions.** If an earlier turn contained an injection, a summary may carry it
  forward in condensed form. Keep untrusted content tagged and treat summaries as untrusted input.
- **Audit trails.** Server-side editing means the model saw less than your log contains. Log what was cleared or
  compacted (the response reports applied edits and compaction blocks) so investigations know what the model actually
  saw.
- **Retention.** Compaction blocks contain condensed conversation data; handle them under the same retention rules.

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| 400 error: compaction block misplaced | Summarised messages left before the block | Replace them with the block; block first |
| 400 error: signature invalid or content mismatch | Block modified before being sent back | Send it exactly as returned |
| No compaction block returned | `stop_reason` was `max_tokens`, `tool_use` or `refusal` | Raise `max_tokens`; instruct not to call tools; continue without a summary |
| Agent forgets a key fact after compaction | Summary did not preserve it | Add it to `instructions`; store it in memory |
| Cache reads drop after enabling clearing | Clearing changes the prefix | Raise `clear_at_least`; accept or measure the trade-off |
| Agent stops early "to save context" | Unaware of compaction | Tell it in the system prompt that context is managed automatically |

## Check your understanding

1. What is the difference between compaction and context editing?
2. Why does tool-result clearing affect prompt caching, and which setting reduces the impact?
3. With compaction enabled, why must you append `response.content` rather than only the response text?
4. Which technique would you use for an agent whose context is 80% old search results? Why?

<details>
<summary>Answers</summary>

1. Compaction replaces earlier history with a model-written summary. Context editing removes specific items (old tool
   results or thinking blocks) by rule and leaves everything else word for word.
2. Clearing changes the prompt from the clearing point onward, invalidating the cached prefix there. `clear_at_least`
   ensures each clear removes enough tokens to justify the new cache write.
3. The compaction block is a content block in the response. If you keep only the text, the block is lost and the API
   cannot replace the old history with the summary.
4. Tool-result clearing (context editing): it targets exactly the bulky, stale material while keeping the
   conversation and recent results verbatim. Pair it with memory or notes for conclusions that must persist.

</details>

## Further reading

- [Compaction overview](https://platform.claude.com/docs/en/build-with-claude/compaction) (Anthropic docs)
- [Context editing](https://platform.claude.com/docs/en/build-with-claude/context-editing) (Anthropic docs)
- [Effective context engineering for AI agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) (Anthropic engineering, 2025-09-29)
- [The agent loop](../10-agentic-ai/03-the-agent-loop.md) and [agent reliability](../10-agentic-ai/07-agent-reliability.md) in this repository

<!-- page-nav:start -->
---

[← Previous: Memory and Persistence](04-memory-and-persistence.md) · [Module overview](README.md) · [Next: Progressive Disclosure and Agent Skills →](06-progressive-disclosure-and-skills.md)
<!-- page-nav:end -->
