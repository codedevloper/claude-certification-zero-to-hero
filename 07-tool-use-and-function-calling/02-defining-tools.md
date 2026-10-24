# Defining Tools

> **Level:** Intermediate · **Time:** ~35 min · **Exam relevance:** CCAR-P 3.1, 3.3, 5.1

## In plain English

A tool definition is a short contract between you and Claude. It answers three questions:

1. **What is this tool called?** (`name`)
2. **What does it do, and when should it be used?** (`description`)
3. **What inputs does it need?** (`input_schema`, written in JSON Schema)

Claude never sees your function's code. Everything it knows about the tool comes from this contract. A vague contract produces vague behaviour: the wrong tool, missing arguments, or no call at all. A precise contract is the cheapest reliability improvement you can make.

Think of writing a tool definition like writing a job card for a contractor who is brilliant but has never visited your building. "Fix the light" will not do. "Replace the failed LED panel in meeting room 3B; the spare is in cupboard C; do not touch the emergency lighting circuit" will.

## Why it matters

- **Tool selection accuracy** depends mostly on descriptions. Anthropic's documentation calls detailed descriptions "by far the most important factor in tool performance".
- **Argument quality** depends on the schema: types, enums and per-field descriptions.
- **Safety** depends on what the schema allows. A free-text `query` field that becomes SQL is a different risk profile from an enum of three report names.
- **Cost and latency** depend on size: every tool definition is sent with every request and counts as input tokens. Large catalogues are where tool search ([page 4](04-server-tools.md#tool-search-and-deferred-loading)) and prompt caching earn their keep.

## How it works

### The fields of a user-defined tool

| Field | Required | Notes (as of 2026-10-24) |
|---|---|---|
| `name` | Yes | Must match `^[a-zA-Z0-9_-]{1,128}$`. Use verbs and namespaces: `crm_search_contacts`, not `search` |
| `description` | Yes in practice | Plain text: what it does, when to use it and when not, what it returns, caveats. Aim for at least three or four sentences |
| `input_schema` | Yes | A JSON Schema object (`"type": "object"`) with `properties` and `required` |
| `input_examples` | No | Array of example input objects, each valid against `input_schema` |
| `strict` | No | `true` guarantees `tool_use.input` validates against the schema |
| `cache_control` | No | Prompt-caching breakpoint (see [prompt caching](../04-context-engineering/03-prompt-caching.md)) |
| `defer_loading` | No | Keep the definition out of context until tool search finds it |
| `eager_input_streaming` | No | Stream large tool inputs as they are generated; you then validate them yourself |

The full list of optional properties is in the [tool reference](https://platform.claude.com/docs/en/agents-and-tools/tool-use/tool-reference).

### Writing the description

A strong description covers:

- **What** the tool does, in one sentence.
- **When** to call it, written as trigger conditions ("Call this when the user asks…"). Being prescriptive about *when* helps recent models, which reach for tools more conservatively.
- **When not** to call it, and what it does **not** return.
- **What each parameter means** and how it changes the behaviour.
- **What comes back**: fields, units, limits, pagination.

Two smaller rules from Anthropic's documentation are worth remembering:

- **Consolidate related operations.** Prefer one `pull_request` tool with an `action` parameter over separate `create_pr`, `review_pr` and `merge_pr` tools when they share most of their inputs.
- **Ask for an explanation, not reasoning.** If you add a parameter asking why Claude is making the call, request a short justification or supporting evidence. A parameter that asks for the model's step-by-step reasoning can trigger a `reasoning_extraction` refusal on current models.

### Designing the schema

- Use `enum` for closed sets (`"status": {"enum": ["open", "closed", "on_hold"]}`).
- Describe every property, including units and formats ("ISO 8601 date", "amount in pence").
- Put only genuinely required fields in `required`; give others sensible defaults in your code.
- Prefer flat objects. Deep nesting raises error rates; if you need it, add `input_examples`.
- Name parameters unambiguously: `customer_id` rather than `customer`.

### Strict tool use

Setting `"strict": true` on a tool definition makes the API constrain Claude's output so that `tool_use.input` always matches your schema: no missing required fields, no wrong types, no extra properties. It is a top-level field on the tool, not part of `tool_choice`.

Rules to remember (as of 2026-10-24):

- Every object in the schema needs `"additionalProperties": false`, and the schema should list `required` fields.
- Strict mode supports a subset of JSON Schema. Basic types, `enum`, `const`, `anyOf`, `allOf`, `$ref`/`$defs` and common string formats (`date`, `date-time`, `email`, `uuid` and others) work. Recursive schemas, numeric bounds (`minimum`, `maximum`) and string length limits (`minLength`, `maxLength`) are not enforced by the API; the Python and TypeScript SDKs strip unsupported constraints and check them client-side.
- A new schema has a one-time compilation cost on first use; Anthropic caches compiled schemas for 24 hours.
- Strict mode guarantees **shape**, not **meaning**. `"order_id": "A-9999"` can be perfectly valid JSON and still be an order the user does not own. You still validate business rules.

### Tool use examples (`input_examples`)

For tools with nested objects, optional parameters or format-sensitive inputs, `input_examples` shows Claude concrete, valid calls:

- Each example must validate against `input_schema`; an invalid example returns a 400.
- They work on user-defined tools and Anthropic-schema client tools, but **not** on server tools or the computer use and browser use toolsets.
- They cost prompt tokens: roughly 20 to 50 tokens for a simple example and 100 to 200 for a complex nested one.
- Descriptions still matter most. Add examples when descriptions alone leave errors.

### Controlling when Claude calls a tool

`tool_choice` takes four values:

| Value | Meaning | Status on current models (as of 2026-10-24) |
|---|---|---|
| `{"type": "auto"}` | Claude decides (default when tools are present) | Supported |
| `{"type": "none"}` | Claude may not call tools | Supported |
| `{"type": "any"}` | Claude must call some tool | **400 error** on Claude Opus 5.5, Claude Sonnet 5.5, Claude Fable 5.1 and Claude Mythos 5.1 |
| `{"type": "tool", "name": "…"}` | Claude must call this tool | **400 error** on the same models |

Older models (for example Claude Opus 5) still accept forced tool use, but the current default models do not. If you are migrating code that forced a call, replace it with one of these:

1. **`auto` plus a clear instruction** in the user or system prompt ("Use the `get_order_status` tool to answer"). Because `auto` does not guarantee a call, check for a `tool_use` block and re-prompt if none came back.
2. **`strict: true`** on the tool, so that when Claude does call it the arguments are schema-valid.
3. **Structured outputs** (`output_config.format` or `client.messages.parse()`) when the forced call only existed to get JSON back. That is the cleaner design for extraction; see [structured output](../03-prompt-engineering/06-structured-output.md).

`disable_parallel_tool_use: true` still works with `auto` and limits Claude to at most one tool call per turn.

## Example

A well-specified tool for a fictional logistics company, with strict mode and examples.

> **Cost:** requires API credits (live mode).

```python
import os
import anthropic

client = anthropic.Anthropic()

create_shipment_quote = {
    "name": "shipping_create_quote",
    "description": (
        "Create a non-binding shipping price quote in the Acme Logistics rating engine. "
        "Call this when a customer asks how much it will cost to send a parcel or pallet "
        "between two UK postcodes. Returns quote_id, price in pence, service level and "
        "estimated transit days. Quotes expire after 24 hours. This tool does not book a "
        "shipment or take payment; never tell the customer their shipment is booked."
    ),
    "strict": True,
    "input_schema": {
        "type": "object",
        "properties": {
            "origin_postcode": {"type": "string", "description": "UK postcode of collection, e.g. LS1 4AP."},
            "destination_postcode": {"type": "string", "description": "UK postcode of delivery."},
            "package_type": {"type": "string", "enum": ["parcel", "pallet"]},
            "weight_kg": {"type": "number", "description": "Total weight in kilograms."},
            "service_level": {
                "type": "string",
                "enum": ["economy", "standard", "next_day"],
                "description": "Use standard if the customer has not said.",
            },
        },
        "required": ["origin_postcode", "destination_postcode", "package_type", "weight_kg", "service_level"],
        "additionalProperties": False,
    },
    "input_examples": [
        {"origin_postcode": "LS1 4AP", "destination_postcode": "M1 1AE",
         "package_type": "parcel", "weight_kg": 2.5, "service_level": "standard"},
        {"origin_postcode": "B1 1BB", "destination_postcode": "G1 1XQ",
         "package_type": "pallet", "weight_kg": 410, "service_level": "economy"},
    ],
}

response = client.messages.create(
    model=os.environ.get("CLAUDE_MODEL", "claude-opus-5-5"),
    max_tokens=16000,
    tools=[create_shipment_quote],
    # tool_choice defaults to auto; we steer with the prompt instead of forcing.
    system="You are Acme Logistics' quoting assistant. Use shipping_create_quote for any price question.",
    messages=[{"role": "user", "content": "How much to send a 3 kg parcel from Leeds LS1 4AP to Manchester M1 1AE?"}],
)

if response.stop_reason == "tool_use":
    call = next(b for b in response.content if b.type == "tool_use")
    print(call.name, call.input)
else:
    print("No tool call; stop_reason =", response.stop_reason)
```

The same definition without `strict`, `enum` values and the "does not book" sentence is a common source of production incidents: assistants that confirm bookings that never happened.

## Enterprise use case

*Contoso Health* (fictional) runs a clinic-scheduling assistant. Its first tool, `query_schedule(sql: string)`, passed model-written SQL to a read replica. It worked in demos and failed review: the security team could not bound what data the model might read, and the SQL sometimes joined patient tables.

The redesign replaced it with three narrow tools: `schedule_find_slots` (clinic ID from an enum of the user's clinics, date range, appointment type from an enum), `schedule_hold_slot` (slot ID, 10-minute hold), and `schedule_confirm_booking` (hold ID, patient ID taken from the authenticated session, never from the model). All three use `strict: true`. Selection accuracy in the team's evaluation set rose, the data-protection officer signed off because no tool could return clinical notes, and audit logs became readable because every call had a named purpose.

## Common mistakes

- **Descriptions that only restate the name.** "Gets the weather" tells Claude nothing about when to call it or what it returns.
- **Forcing calls with `tool_choice: any` on Opus 5.5, Sonnet 5.5, Fable 5.1 and Mythos 5.1.** It returns a 400. Use `auto` plus instructions, `strict: true` or structured outputs.
- **Assuming strict mode validates business rules.** It guarantees the schema, not authorisation or plausibility.
- **Forgetting `additionalProperties: false`** on nested objects when using `strict`.
- **Over-long parameter lists.** Ten optional flags confuse the model; split or consolidate thoughtfully.
- **Asking for "your reasoning" in a parameter.** Ask for a short justification instead.
- **Changing tool definitions mid-conversation casually.** Tools render first in the prompt, so edits invalidate the prompt cache. Keep the tool list stable and deterministic in order.

## Security considerations

- **The schema is your first guardrail.** Enums and narrow types reduce the space of possible inputs; free-text fields that reach interpreters (SQL, shell, templates) are high risk.
- **Never put identity in the model's hands.** User IDs, tenant IDs and roles should come from the authenticated session in your code, not from a tool parameter Claude fills.
- **Descriptions are prompt content.** If tool definitions come from a third party (for example an MCP server), a malicious description can steer the model. See [MCP security](../08-model-context-protocol/05-mcp-security.md).
- **Strict mode reduces malformed input but not malicious input.** Keep server-side validation.

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| 400 mentioning `tool_choice` `any`/`tool` not supported | Forced tool use on Opus 5.5, Sonnet 5.5 or Fable 5.1 | Switch to `auto` and instruct; add `strict: true` |
| 400 on an `input_examples` entry | Example does not validate against the schema | Fix the example or the schema |
| Strict tool rejected | Missing `additionalProperties: false`, or unsupported keyword | Add it to every object; move numeric bounds into your validation |
| First request with a new strict schema is slow | Schema compilation | Expected once; compiled schemas are cached for 24 hours |
| Claude passes a name where an ID is expected | Ambiguous parameter name | Rename to `customer_id`, describe the format, add an example |

## Check your understanding

1. What are the three essential fields of a user-defined tool, and which one most influences tool selection?
2. You migrate code that used `tool_choice: {"type": "tool", "name": "extract_invoice"}` only to get JSON back. What is the cleanest replacement on Claude Opus 5.5?
3. Does `strict: true` guarantee that a refund amount is within policy limits? Explain.
4. When are `input_examples` worth their token cost?

<details>
<summary>Answers</summary>

1. `name`, `description` and `input_schema`. The description has the most influence on whether and when Claude calls the tool.
2. Structured outputs (`output_config.format` or `client.messages.parse()`), which constrain the response to a JSON schema without needing a tool call.
3. No. Strict mode guarantees the input matches the schema's types and required fields, and the API does not enforce numeric bounds such as `maximum`. Policy limits must be checked in your tool code.
4. For tools with nested objects, optional parameters or format-sensitive inputs where evaluation shows parameter errors that a clearer description has not fixed.

</details>

## Further reading

- [Define tools](https://platform.claude.com/docs/en/agents-and-tools/tool-use/define-tools) (Claude Docs)
- [Strict tool use](https://platform.claude.com/docs/en/agents-and-tools/tool-use/strict-tool-use) (Claude Docs)
- [Structured outputs](https://platform.claude.com/docs/en/build-with-claude/structured-outputs) (Claude Docs)
- [Writing effective tools for agents](https://www.anthropic.com/engineering/writing-tools-for-agents) (Anthropic Engineering, 2025-09-11)

<!-- page-nav:start -->
---

[← Previous: Tool Use Fundamentals](01-tool-use-fundamentals.md) · [Module overview](README.md) · [Next: The Tool-Use Loop →](03-the-tool-use-loop.md)
<!-- page-nav:end -->
