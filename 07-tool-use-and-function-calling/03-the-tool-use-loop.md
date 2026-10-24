# The Tool-Use Loop

> **Level:** Intermediate · **Time:** ~45 min · **Exam relevance:** CCAR-P 3.3, 5.3

## In plain English

One tool call is rarely enough. To answer "Which of my overdue invoices are over £5,000, and email the account owners?", Claude might list invoices, filter them, look up owners and draft emails. Each step needs a tool result before the next step makes sense.

The **tool-use loop** is the small piece of code that keeps the conversation going:

1. Send the conversation to Claude.
2. If Claude asks for tools, run them and send the results back.
3. Repeat until Claude says it is done.

You can write this loop yourself (a *manual loop*) or let the Anthropic SDK's **Tool Runner** do it. Either way, you need to understand the rules underneath: how to send results for several tools at once, how to report a failed tool, and what each `stop_reason` means.

## Why it matters

- **Correctness.** Most tool-use bugs are loop bugs: a missing `tool_result`, results split across messages, or a paused server turn treated as finished.
- **Latency.** Running parallel tool calls concurrently, and keeping round trips low, is often the biggest latency win in an agent (CCAR-P-3.3).
- **Control points.** The loop is where you put human approval, logging, budgets and kill switches (CCAR-P-5.3).
- **Cost.** Every loop iteration resends the whole conversation. Unbounded loops are unbounded spend.

## How it works

### The stop reasons you must handle

Always check `stop_reason` before you use `content`.

| `stop_reason` | Meaning | What your loop does |
|---|---|---|
| `end_turn` | Claude finished its answer | Exit the loop and return the text |
| `tool_use` | Claude wants one or more client tools | Run them, append results, call again |
| `pause_turn` | A server-side tool loop (for example web search) paused a long turn | Append the assistant content unchanged and call again with the same `tools`; do **not** add a "Continue" message |
| `max_tokens` | Output hit your `max_tokens` cap | Do not run a truncated `tool_use`; retry with a higher cap or stop |
| `refusal` | A safety classifier declined the request | Do not execute any tools from this turn; read `stop_details`, then fall back or report |
| `stop_sequence` | A custom stop sequence matched | Handle as your design requires |

> **Note:** On Claude Opus 5.5 and other current models, a `refusal` can arrive with HTTP 200. Anthropic offers a server-side `fallbacks` option (beta) that retries refused requests on another model; check the [refusals and fallback guide](https://platform.claude.com/docs/en/build-with-claude/refusals-and-fallback) before relying on it.

### Message-ordering rules

These rules cause most 400 errors:

1. Append Claude's **entire** `response.content` as the `assistant` message. It carries the `tool_use` blocks your results refer to (and any thinking blocks, which must be passed back unchanged).
2. The very next message is a `user` message containing a `tool_result` for **every** `tool_use` id in that assistant turn.
3. Inside that user message, all `tool_result` blocks come **first**. Text, if any, goes after them.
4. If the assistant turn also contains a `server_tool_use` that has no result yet (Claude called a server tool and a client tool together), the user message must contain **only** `tool_result` blocks, and you must send the same `tools` array again.

### Parallel tool calls

By default Claude may request several tools in one turn, for example three independent lookups. Run them concurrently if they are independent, then return **all** results in **one** user message.

Splitting results across several user messages is not only an error risk: Anthropic's guidance notes it teaches Claude to stop making parallel calls, which costs you latency. If you need strictly one call at a time (for example, tools with side effects that must be sequenced), set `"disable_parallel_tool_use": true` inside `tool_choice` with `"type": "auto"`.

### Reporting failures with `is_error`

When a tool fails, still return a `tool_result`, with `"is_error": true` and a message Claude can act on:

```json
{
  "type": "tool_result",
  "tool_use_id": "toolu_01...",
  "is_error": true,
  "content": "Order A-9999 not found. Order IDs look like A-1234; ask the customer to check their confirmation email."
}
```

Instructive errors let Claude recover: retry with corrected input, try another tool, or ask the user. "Error 500" does not. Anthropic's documentation notes that for invalid or missing parameters Claude will typically retry two or three times with corrections before apologising to the user.

### Forced tool use is gone on current models

Older loops sometimes forced the first call with `tool_choice: {"type": "tool", ...}`. On Claude Opus 5.5, Claude Sonnet 5.5 and Claude Fable 5.1 that returns a 400. Use `auto`, instruct clearly, and check whether a `tool_use` came back. See [Defining tools](02-defining-tools.md#controlling-when-claude-calls-a-tool).

### Manual loop or Tool Runner?

| Approach | You write | Good for |
|---|---|---|
| **Manual loop** | The `while` loop, dispatch, result formatting | Full control, no beta dependency, unusual control flow, teaching |
| **Tool Runner** (`client.beta.messages.tool_runner`, beta) | Only the tool functions (`@beta_tool` in Python) | Most custom-tool agents. The SDK calls the API, runs your functions, feeds results back and stops when Claude is done |
| **Claude Agent SDK** | A prompt and options | A batteries-included coding agent with built-in file and shell tools; see [Module 09](../09-claude-code/09-headless-ci-and-agent-sdk.md) |
| **Managed Agents** | Agent configuration | Anthropic hosts both the loop and the sandbox; see [Module 10](../10-agentic-ai/06-managed-agents-and-agent-sdk.md) |

The Tool Runner is not a black box: you can inspect each yielded message, gate a call inside the tool function, or modify results. One caution as of 2026-10-24: the Python Tool Runner does **not** resume `pause_turn` automatically. If you mix server tools into a runner, handle `pause_turn` yourself or use a manual loop.

## Example

### A manual loop with parallel execution, validation and approval

This loop handles every stop reason in the table, runs parallel calls concurrently, returns errors with `is_error`, and asks a human before any tool marked as having side effects.

> **Cost:** requires API credits (live mode).

```python
"""Manual tool-use loop for a fictional Acme Logistics support assistant."""
from __future__ import annotations

import json
import os
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Callable

import anthropic

client = anthropic.Anthropic()  # ANTHROPIC_API_KEY from the environment
MODEL = os.environ.get("CLAUDE_MODEL", "claude-opus-5-5")
MAX_ITERATIONS = 10

# --- Tool implementations (synthetic data) -----------------------------------
ORDERS = {"A-1042": {"status": "shipped", "carrier": "Parcelwise"},
          "A-1043": {"status": "packing", "carrier": None}}

def get_order_status(order_id: str) -> dict[str, Any]:
    if order_id not in ORDERS:
        raise LookupError(f"Order {order_id} not found. IDs look like A-1234.")
    return {"order_id": order_id, **ORDERS[order_id]}

def cancel_order(order_id: str, reason: str) -> dict[str, Any]:
    if ORDERS.get(order_id, {}).get("status") == "shipped":
        raise ValueError("Shipped orders cannot be cancelled; offer a return instead.")
    return {"order_id": order_id, "cancelled": True}

REGISTRY: dict[str, tuple[Callable[..., Any], bool]] = {
    # name: (function, has_side_effects)
    "get_order_status": (get_order_status, False),
    "cancel_order": (cancel_order, True),
}

TOOLS = [
    {"name": "get_order_status", "strict": True,
     "description": "Look up one order's fulfilment status. Call for any 'where is my order' question.",
     "input_schema": {"type": "object", "additionalProperties": False, "required": ["order_id"],
                      "properties": {"order_id": {"type": "string", "description": "Format A-1234"}}}},
    {"name": "cancel_order", "strict": True,
     "description": "Cancel an order that has not shipped. Only call after the customer explicitly asks to cancel.",
     "input_schema": {"type": "object", "additionalProperties": False, "required": ["order_id", "reason"],
                      "properties": {"order_id": {"type": "string"},
                                     "reason": {"type": "string", "description": "Customer's stated reason"}}}},
]

def human_approves(name: str, args: dict[str, Any]) -> bool:
    """Confirmation gate. Replace with your UI or ticketing workflow."""
    answer = input(f"Approve {name}({json.dumps(args)})? [y/N] ")
    return answer.strip().lower() == "y"

def run_one(block) -> dict[str, Any]:
    """Execute one tool_use block and always return a tool_result."""
    entry = REGISTRY.get(block.name)
    if entry is None:
        return {"type": "tool_result", "tool_use_id": block.id, "is_error": True,
                "content": f"Unknown tool {block.name}."}
    func, side_effects = entry
    if side_effects and not human_approves(block.name, block.input):
        return {"type": "tool_result", "tool_use_id": block.id, "is_error": True,
                "content": "The user declined this action. Do not retry it; ask what they would like instead."}
    try:
        result = func(**block.input)  # strict: true guarantees the shape; func checks business rules
        return {"type": "tool_result", "tool_use_id": block.id, "content": json.dumps(result)}
    except Exception as exc:  # report, never crash the loop
        return {"type": "tool_result", "tool_use_id": block.id, "is_error": True, "content": str(exc)}

def answer(question: str) -> str:
    messages: list[dict[str, Any]] = [{"role": "user", "content": question}]
    for _ in range(MAX_ITERATIONS):
        response = client.messages.create(
            model=MODEL, max_tokens=16000, tools=TOOLS, messages=messages,
            system="You are Acme Logistics' order assistant. Use tools; never guess order status.",
        )
        if response.stop_reason == "end_turn":
            return "".join(b.text for b in response.content if b.type == "text")
        if response.stop_reason == "refusal":
            return "This request can't be completed. A human agent will follow up."
        if response.stop_reason == "max_tokens":
            raise RuntimeError("Output truncated; raise max_tokens rather than running partial tool calls.")

        messages.append({"role": "assistant", "content": response.content})  # full content, always

        if response.stop_reason == "pause_turn":
            continue  # resend unchanged so the server-side loop resumes

        if response.stop_reason == "tool_use":
            calls = [b for b in response.content if b.type == "tool_use"]
            approval_needed = any(REGISTRY.get(c.name, (None, False))[1] for c in calls)
            if approval_needed:
                results = [run_one(c) for c in calls]  # sequential so prompts don't interleave
            else:
                with ThreadPoolExecutor(max_workers=8) as pool:
                    results = list(pool.map(run_one, calls))  # order preserved
            messages.append({"role": "user", "content": results})  # ALL results, ONE message
            continue

        raise RuntimeError(f"Unhandled stop_reason: {response.stop_reason}")
    raise RuntimeError("Loop limit reached; escalate to a human.")

if __name__ == "__main__":
    print(answer("Where are orders A-1042 and A-1043? If A-1043 hasn't shipped, cancel it, I ordered twice."))
```

Points worth noticing: the loop is bounded; every `tool_use` gets exactly one `tool_result`; failures become `is_error` results rather than exceptions; and the cancellation tool cannot run without a person saying yes.

### The same assistant with the Tool Runner

The Tool Runner builds the schema from type hints and the docstring, and drives the loop for you. The approval gate moves inside the tool function.

```python
import json
import os

import anthropic
from anthropic import beta_tool

client = anthropic.Anthropic()

@beta_tool
def get_order_status(order_id: str) -> str:
    """Look up one order's fulfilment status. Call for any 'where is my order' question.

    Args:
        order_id: Order reference in the form A-1234.
    """
    orders = {"A-1042": "shipped", "A-1043": "packing"}
    if order_id not in orders:
        return json.dumps({"error": f"Order {order_id} not found. IDs look like A-1234."})
    return json.dumps({"order_id": order_id, "status": orders[order_id]})

runner = client.beta.messages.tool_runner(
    model=os.environ.get("CLAUDE_MODEL", "claude-opus-5-5"),
    max_tokens=16000,
    tools=[get_order_status],
    messages=[{"role": "user", "content": "Where are orders A-1042 and A-1043?"}],
)
final = runner.until_done()  # iterate `for message in runner:` instead to observe each turn
print(final.stop_reason)
print("".join(b.text for b in final.content if b.type == "text"))
```

> **Note:** The Tool Runner is a beta helper in the Anthropic SDKs (as of 2026-10-24). For streaming requests with client tools, Anthropic recommends `eager_input_streaming: true` on each tool, which means you must validate parsed inputs yourself. `@beta_tool` functions with typed parameters are validated by the SDK.

## Enterprise use case

*Fabrikam Insurance* (fictional) built a claims-intake assistant with six read tools and two write tools (`claim_create_draft`, `claim_submit`). Early latency was poor: Claude requested policy, customer and prior-claims lookups in parallel, but the team's loop executed them sequentially and, worse, returned them in three separate user messages. Over a week of logs, parallel calls became rarer.

The fix had three parts. The loop now runs read tools concurrently and returns one combined user message; median time to first draft fell noticeably in their load tests. `claim_submit` is gated: the loop pauses, the human adjuster sees the draft and approves in the claims UI, and only then does the tool run. Finally, a ten-iteration cap and a per-conversation token budget stop runaway loops, with an `is_error` result telling Claude to summarise progress for a human when the budget is near.

## Common mistakes

- **Only checking for `end_turn`.** A `pause_turn` or `max_tokens` treated as "done" silently truncates answers.
- **Splitting parallel results** across several user messages, or placing text before `tool_result` blocks.
- **Raising exceptions out of the loop** instead of returning `is_error` results. The conversation then cannot recover.
- **Adding "Continue" after `pause_turn`.** Resend the assistant content unchanged; the API resumes on its own.
- **No iteration or budget limit.** A confused model plus a failing tool can loop for a long time.
- **Approving side effects in parallel.** Interleaved approval prompts confuse reviewers; sequence calls that need approval.
- **Assuming the Python Tool Runner resumes `pause_turn`.** It does not (as of 2026-10-24); handle it explicitly.

## Security considerations

- **Gate side effects in code, not in the prompt.** "Ask before cancelling" in the system prompt is guidance; a confirmation check in the loop is enforcement. See [human oversight](../12-ai-security/13-human-oversight.md).
- **Bound the loop.** Iteration caps, token budgets and wall-clock timeouts limit damage from prompt injection or tool failures.
- **Log every call** with tool name, validated input, result size, approver and conversation ID for audit ([logging and auditability](../12-ai-security/11-logging-and-auditability.md)).
- **Never run tools from a `refusal` or truncated turn.**
- **Sanitise errors.** Error messages go back into the model's context; do not include stack traces, secrets or internal hostnames.

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| 400: `tool_use` ids were found without `tool_result` blocks immediately after | A result is missing, misplaced, or text came first | One user message, every id answered, results first |
| 400 naming an unresolved `web_fetch` or other server tool | You added text after `tool_result` blocks while a server tool was pending, or dropped it from `tools` | Send only `tool_result` blocks and the same `tools` array |
| Parallel calls stopped happening | Results returned in separate messages | Return all results together |
| Answer ends mid-research | `pause_turn` treated as final | Resend assistant content and continue |
| Loop never ends | Tool keeps failing with an unhelpful error | Make errors instructive; cap iterations |

More cases: [tools and agents troubleshooting](../24-troubleshooting/tools-and-agents.md).

## Check your understanding

1. Claude returns three `tool_use` blocks in one turn. How many user messages should you send back, and in what order are the blocks inside?
2. What is the correct response to `stop_reason: "pause_turn"`?
3. A tool throws a timeout. What should your loop send to Claude?
4. Name one reason to keep a manual loop instead of the Tool Runner.
5. Why should a side-effecting tool's approval be enforced in code rather than in the system prompt?

<details>
<summary>Answers</summary>

1. One user message containing three `tool_result` blocks (one per `tool_use` id), with the `tool_result` blocks first and any text after them.
2. Append the assistant's content unchanged and call the API again with the same `tools`; do not add a "Continue" user message.
3. A `tool_result` with `"is_error": true` and an instructive message, for example that the service timed out and when to retry.
4. Any one of: avoiding a beta dependency; unusual control flow; handling `pause_turn` explicitly in Python; a custom transport or request shape the SDK cannot build.
5. The model's behaviour can be influenced by injected content or mistakes; a code-level gate holds regardless of what the model decides.

</details>

## Further reading

- [Handle tool calls](https://platform.claude.com/docs/en/agents-and-tools/tool-use/handle-tool-calls) (Claude Docs)
- [Parallel tool use](https://platform.claude.com/docs/en/agents-and-tools/tool-use/parallel-tool-use) (Claude Docs)
- [Tool Runner](https://platform.claude.com/docs/en/agents-and-tools/tool-use/tool-runner) (Claude Docs)
- [Handling stop reasons](https://platform.claude.com/docs/en/build-with-claude/handling-stop-reasons) (Claude Docs)
- [The agent loop](../10-agentic-ai/03-the-agent-loop.md) in Module 10
- Previous: [Defining tools](02-defining-tools.md) · Next: [Server tools](04-server-tools.md)
