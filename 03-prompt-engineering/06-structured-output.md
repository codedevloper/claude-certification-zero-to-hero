# Structured Output

> **Level:** Intermediate · **Time:** ~50 min · **Exam relevance:** CCAO-F D1, D2 · CCAR-P D2, D3

## In plain English

People read prose; programs read data. When Claude's answer will be stored in a database, sent to another system or
checked automatically, you need it in a predictable shape, usually JSON with specific fields.

You can ask nicely ("reply in JSON with these fields"), and current models usually comply. But "usually" is not good
enough for software. **Structured outputs** let you hand the API a JSON Schema, and the response is constrained to
match it. In Python you can go one step further and describe the shape as a Pydantic model, then receive a validated
object back.

In the Claude apps, the equivalent skill is choosing the right output format for the reader: a table, a list, an
artifact or a downloadable file (CCAO-F-2.6). The principles on this page (define the shape, name the fields, say what
to do when data is missing) apply there too.

## Why it matters

- **Reliability.** A schema-constrained response parses every time it completes normally, so downstream code does not
  need fragile clean-up.
- **Clear contracts between steps.** In a [prompt chain](05-task-decomposition-and-chaining.md) or an agent, schemas
  are the interface between components.
- **Safer automation.** Validated fields with `enum` values are easier to check against business rules before acting.
- **The API changed.** Assistant-message prefill, which people used to force JSON (by starting the reply with `{`), is
  no longer accepted on current models (the Claude 4.6 family and later, including Haiku 5.5). Forcing a specific tool with `tool_choice` is also rejected on several current
  models. Structured outputs and strict tools are the supported replacements.

## How it works

There are three supported ways to get structured data, plus one retired technique.

### 1. JSON outputs with `output_config.format`

You pass a JSON Schema in `output_config.format`. The response's text block contains JSON that matches it.

```python
import json

import anthropic

client = anthropic.Anthropic()  # API key from ANTHROPIC_API_KEY

schema = {
    "type": "object",
    "properties": {
        "vendor_name": {"type": "string"},
        "contract_value": {"type": "number"},
        "currency": {"type": "string", "enum": ["USD", "EUR", "GBP"]},
        "renewal_date": {"type": "string", "format": "date"},
        "auto_renews": {"type": "boolean"},
    },
    "required": ["vendor_name", "contract_value", "currency", "renewal_date", "auto_renews"],
    "additionalProperties": False,
}

response = client.messages.create(
    model="claude-opus-5-5",
    max_tokens=2000,
    output_config={"format": {"type": "json_schema", "schema": schema}},
    messages=[{"role": "user", "content": "Extract the contract terms:\n<contract>...</contract>"}],
)

if response.stop_reason != "end_turn":
    raise RuntimeError(f"No complete structured output: {response.stop_reason}")

data = json.loads(next(b.text for b in response.content if b.type == "text"))
```

The equivalent cURL request:

```bash
curl https://api.anthropic.com/v1/messages \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -H "content-type: application/json" \
  -d '{
    "model": "claude-opus-5-5",
    "max_tokens": 1000,
    "output_config": {"format": {"type": "json_schema", "schema": {
      "type": "object",
      "properties": {"sentiment": {"type": "string", "enum": ["positive", "neutral", "negative"]}},
      "required": ["sentiment"],
      "additionalProperties": false
    }}},
    "messages": [{"role": "user", "content": "Sentiment of: The delivery was late again."}]
  }'
```

The older top-level `output_format` parameter on `messages.create()` is deprecated; use `output_config.format`.

### 2. `client.messages.parse()` with Pydantic

The Python SDK can build the schema from a Pydantic model and validate the result for you. This is the recommended
approach in Python.

```python
from typing import Literal

import anthropic
from pydantic import BaseModel

client = anthropic.Anthropic()


class ContractTerms(BaseModel):
    vendor_name: str
    contract_value: float
    currency: Literal["USD", "EUR", "GBP"]
    renewal_date: str          # ISO date
    auto_renews: bool
    termination_notice_days: int | None


response = client.messages.parse(
    model="claude-opus-5-5",
    max_tokens=2000,
    messages=[{"role": "user", "content": "Extract the contract terms:\n<contract>...</contract>"}],
    output_format=ContractTerms,
)

if response.stop_reason == "end_turn" and response.parsed_output is not None:
    terms: ContractTerms = response.parsed_output
    print(terms.vendor_name, terms.renewal_date)
else:
    print("Route to manual review:", response.stop_reason)
```

### 3. Strict tool use

When Claude calls one of your tools, `strict: true` on the tool definition guarantees the `input` matches the tool's
`input_schema`. Use this when the structured data is an *action request* (create a ticket, look up an order) rather
than a final answer.

```python
tools = [{
    "name": "create_maintenance_ticket",
    "description": "Open a maintenance ticket for a faulty asset. Use when the report describes a fault.",
    "strict": True,
    "input_schema": {
        "type": "object",
        "properties": {
            "asset_id": {"type": "string"},
            "priority": {"type": "string", "enum": ["low", "medium", "high"]},
            "summary": {"type": "string"},
        },
        "required": ["asset_id", "priority", "summary"],
        "additionalProperties": False,
    },
}]

response = client.messages.create(
    model="claude-opus-5-5",
    max_tokens=2000,
    tools=tools,
    tool_choice={"type": "auto"},
    messages=[{"role": "user", "content": "Report: conveyor C-14 is jammed and smoking. "
                                          "If this is a fault, open a ticket with the tool."}],
)
```

On current models such as Claude Opus 5.5 and Claude Sonnet 5.5, `tool_choice` of `{"type": "any"}` or
`{"type": "tool", "name": ...}` returns a 400 error (as of 2026-10-24). Use `auto`, name the tool in your instruction,
and check whether a `tool_use` block came back. If you only wanted the "forced tool" to get JSON, use structured
outputs instead. Tool use is covered fully in
[Module 07](../07-tool-use-and-function-calling/README.md).

### Retired: assistant prefill

Older guides suggested ending your `messages` with a partial assistant turn such as `{"role": "assistant",
"content": "{"}` so Claude would continue in JSON, or `"Here is the summary:"` to skip a preamble. Starting with the
Claude 4.6 generation, a prefilled final assistant turn returns a 400 error. Replacements:

| Old prefill purpose | Current approach |
|---|---|
| Force JSON or YAML | Structured outputs (`output_config.format` or `messages.parse()`) |
| Force a classification label | Schema with an `enum` field |
| Skip a preamble | Instruction: "Respond directly without preamble"; or tagged output; strip leftovers in code |
| Continue an interrupted answer | Put the partial text in the user turn: "Your previous response ended with … Continue from there." |
| Keep a persona or reminder in long chats | System prompt, or a reminder in the user turn |

Earlier assistant turns in the history are still fine; only a prefilled *final* assistant turn is rejected.

### Schema design guidance

- Every object needs `"additionalProperties": false` and a `required` list.
- Supported: basic types, `enum`, `const`, `anyOf`, `allOf`, `$ref`, and common string formats such as `date`,
  `date-time`, `email` and `uri`. Not supported (as of 2026-10-24): recursive schemas and numeric or length constraints
  such as `minimum` or `maxLength`. The Python and TypeScript SDKs strip unsupported constraints from the schema they
  send and check them client-side.
- **Plan for missing data.** Use nullable fields (`int | None`) or an explicit `"not_found"` enum value, and tell
  Claude when to use them. Otherwise Claude may invent a plausible value to satisfy a required field.
- **Use enums for categories** your code branches on.
- **Keep schemas small and flat** where you can. Deeply nested schemas are harder to fill well.
- **Describe fields.** Short `description` values in the schema, or notes in the prompt, improve accuracy.

### What structured outputs do not guarantee

- **Truth.** A perfectly valid JSON object can contain a wrong value. Validate content against business rules.
- **Completion.** If `stop_reason` is `max_tokens` the JSON may be cut off; if it is `refusal` the output may not match
  the schema. Always check `stop_reason` first.
- **Compatibility with everything.** Structured outputs cannot be combined with
  [citations](../06-claude-api/04-vision-documents-and-citations.md) in the same request (400 error). New schemas also
  incur a one-time compilation delay on first use.

## Example

*Acme Logistics* (fictional) turns free-text carrier emails into shipment updates. The prompt explains how to treat
missing data; the schema makes that rule enforceable.

```python
from typing import Literal

import anthropic
from pydantic import BaseModel, Field

client = anthropic.Anthropic()


class ShipmentUpdate(BaseModel):
    tracking_number: str | None = Field(description="Null if no tracking number appears in the email")
    status: Literal["in_transit", "delayed", "delivered", "exception", "unknown"]
    new_eta: str | None = Field(description="ISO date, or null if not stated")
    reason: str | None


email = open("data/carrier_email_0042.txt", encoding="utf-8").read()

response = client.messages.parse(
    model="claude-sonnet-5-5",
    max_tokens=1000,
    output_config={"effort": "low"},
    messages=[{
        "role": "user",
        "content": (
            "Convert this carrier email into a shipment update. Use null for any field the "
            "email does not state; never guess a tracking number or date. Use status 'unknown' "
            "if the email does not make the status clear.\n"
            f"<email>\n{email}\n</email>"
        ),
    }],
    output_format=ShipmentUpdate,
)

update = response.parsed_output if response.stop_reason == "end_turn" else None
if update is None or update.tracking_number is None:
    print("Send to the exceptions queue for a human to review.")
else:
    print(update.model_dump())
```

> **Cost:** requires API credits (live mode).

## Enterprise use case

*Woodgrove Bank* (fictional) extracts covenant terms from commercial loan agreements into its credit-monitoring
system. Their first version asked for "JSON with these fields" in the prompt and parsed the reply; roughly one reply in
a few hundred broke the parser, and some covenants were silently dropped when Claude added commentary.

They moved to `messages.parse()` with a Pydantic model, added an explicit `"not_stated"` value for each optional term,
and added business-rule checks after parsing (for example, a leverage ratio must be positive and below a sane upper
bound). Parser failures disappeared, and the business-rule checks now catch the more important class of error:
well-formed but wrong values. Low-confidence extractions go to a credit analyst, which satisfies the bank's model-risk
policy.

## Common mistakes

- **Prefilling `{` to force JSON.** Rejected on current models. Use structured outputs.
- **Using forced `tool_choice` to get JSON.** Rejected on several current models. Use structured outputs or `auto`
  with a strict tool.
- **Required fields with no "missing" option.** Forces Claude to fabricate. Make fields nullable or add a sentinel.
- **Skipping `stop_reason` checks.** A truncated or refused response is not valid data.
- **Trusting valid JSON as correct data.** Schema validity is not factual accuracy.
- **Asking for citations and structured output together.** Split into two calls, or include quoted evidence as a
  schema field.

## Security considerations

- **Model output is untrusted input.** Validate values, escape strings before rendering them in HTML, and never pass
  fields to `eval`, a shell or a SQL string. See
  [insecure output handling](../12-ai-security/06-insecure-output-handling.md).
- **Constrain actions with enums and allow-lists.** A `priority` enum is safer than a free-text field your code
  interprets.
- **Strict tools validate shape, not authority.** A schema-valid `delete_record` call can still be the wrong action.
  Authorise every tool call in code.
- **Avoid sensitive fields you do not need.** Every extracted field ends up in logs and databases; extract only what
  the process requires.

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| 400 error: prefill not supported | Final assistant turn in `messages` | Remove it; use structured outputs or instructions |
| 400 error on `tool_choice` | `any` or `tool` on a model that rejects forced tool use | Use `auto` plus an instruction, a strict tool, or structured outputs |
| 400 error mentioning schema | Unsupported keyword or missing `additionalProperties: false` | Simplify the schema; let the SDK handle constraints client-side |
| 400 error when citations enabled | Citations and structured outputs combined | Use one per request |
| `json.loads` fails | Response truncated (`max_tokens`) or refused | Check `stop_reason`; raise `max_tokens` |
| Plausible but invented values | No way to express "missing" | Nullable fields or sentinel values, plus instructions |
| First request slow | Schema compiled on first use | Expected; later requests reuse the compiled schema |

## Check your understanding

1. What are the three supported ways to get structured data from Claude, and when would you use each?
2. Why does a prefilled `{` no longer work, and what replaces it?
3. A schema has a required `invoice_date` field, and some invoices have no date. What will likely happen, and how do
   you fix it?
4. Name two things structured outputs do *not* guarantee.

<details>
<summary>Answers</summary>

1. `output_config.format` with a JSON Schema (structured final answers in any language), `client.messages.parse()`
   with a Pydantic model (the same, with automatic validation in Python), and `strict: true` tools (when the structured
   data is a request to perform an action).
2. Current models reject a prefilled final assistant turn with a 400 error. Structured outputs replace prefill for
   format control; instructions or tags replace it for skipping preambles.
3. Claude may invent a plausible date to satisfy the required field. Make the field nullable (or add a sentinel value)
   and instruct Claude to use it when the date is absent.
4. Factual correctness of the values, and completion when the response stops for `max_tokens` or `refusal`.

</details>

## Further reading

- [Structured outputs](https://platform.claude.com/docs/en/build-with-claude/structured-outputs) (Anthropic docs)
- [Prompting best practices: migrating away from prefilled responses](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices) (Anthropic docs)
- [Defining tools](../07-tool-use-and-function-calling/02-defining-tools.md) in this repository
- [Lab 03 — Structured outputs](../19-hands-on-labs/lab-03-structured-outputs/README.md)

<!-- page-nav:start -->
---

[← Previous: Task Decomposition and Prompt Chaining](05-task-decomposition-and-chaining.md) · [Module overview](README.md) · [Next: System Prompts, Roles, Templates and Guardrails →](07-system-prompts-and-roles.md)
<!-- page-nav:end -->
