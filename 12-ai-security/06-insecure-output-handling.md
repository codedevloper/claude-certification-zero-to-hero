# Insecure Output Handling

> **Level:** Advanced · **Time:** ~35 min · **Exam relevance:** CCAR-P D5 (5.1, 5.2), CCAR-P D3 (3.2)

## In plain English

Insecure output handling is what happens when you take text produced by a model and pass it straight into something
that interprets it: a web page, a database query, a shell, a template engine, a configuration file or another agent.
The model's output is shaped by everything in its context, including attacker-controlled content, so it must be
treated exactly like user input from the internet.

OWASP's 2025 list calls this **LLM05:2025 Improper Output Handling**. Older material uses the name "insecure output
handling". The idea is the same: validate, encode and sandbox model output before any downstream system acts on it.

## Why it matters

- It turns classic web vulnerabilities (cross-site scripting, SQL injection, command injection, server-side request
  forgery, path traversal) into LLM vulnerabilities. An attacker who cannot reach your database directly may be able
  to get a model to write the query for them.
- It is often the last line between a successful prompt injection and real impact.
- It is the most "traditional" risk on the list, so standard AppSec tooling and reviews can catch it, if reviewers know
  to look at model output as a source.

## How it works

### Sinks and their controls

| Sink | What goes wrong | Control |
|---|---|---|
| HTML / browser | Model emits `<script>` or event handlers; markdown converted to unsafe HTML | Render as text or through a sanitiser with an allow-list; Content Security Policy; never `innerHTML` raw output |
| SQL | Model-generated query or fragment executes with app privileges | Do not execute free-form model SQL; have the model choose from parameterised queries or produce structured filters that code turns into parameterised SQL; read-only database role |
| Shell / OS | Model output passed to `os.system` or `subprocess(shell=True)` | No shell interpolation; allow-listed commands with argument arrays; sandbox |
| Code execution | Running model-written code | Isolated sandbox with no credentials, CPU/memory/time limits, restricted network |
| File paths | Model chooses a path that escapes the intended directory | Resolve and verify paths stay under an allowed root |
| URLs / HTTP | Model chooses a URL your server fetches (server-side request forgery) | Allow-list hosts; block private IP ranges; route through an egress proxy |
| Templates | Model output inserted into a server-side template | Escape, or pass as data to the template, never as template source |
| Email / messaging | Header injection, phishing content sent under your brand | Structured fields, length limits, review for external sends |
| Another agent or model | Output carries instructions to the next agent | Treat as untrusted content (tool result with provenance) |
| `eval` / deserialisation | Arbitrary code execution | Never `eval`, `exec` or unpickle model output |

### Prefer structure over free text

The most effective control is to stop asking for free text when a downstream system needs data. Use structured
outputs (`output_config.format` with a JSON schema) or strict tool schemas so that the model returns typed fields,
then validate those fields with ordinary code. A model that returns
`{"action": "archive", "ticket_id": 4812}` from an enum-constrained schema cannot return a shell command.

Structured outputs guarantee *shape*, not *safety*. A schema-valid `ticket_id` might belong to another tenant; a
schema-valid `comment` string can still contain HTML. Validate semantics and encode for the sink.

### Check stop reasons first

Before you use any output, check `stop_reason`. `max_tokens` means the output may be truncated (a half-written JSON
object or a partial command). `refusal` means the model declined and `content` may be empty or partial.
`tool_use` means the model wants a tool, not that it has answered. Treat anything other than the expected value as
a failure path.

## Example

The function below turns a model-proposed database filter into a parameterised query. The model never writes SQL.

```python
"""safe_query.py - convert a structured, model-proposed filter into parameterised SQL."""
import json
import sqlite3

ALLOWED_FIELDS = {"status": str, "region": str, "min_days_overdue": int}
ALLOWED_STATUS = {"current", "late", "default", "closed"}
ALLOWED_REGION = {"north", "south", "east", "west"}

FILTER_SCHEMA = {  # pass this as output_config.format in the Claude request
    "type": "object",
    "properties": {
        "status": {"type": "string", "enum": sorted(ALLOWED_STATUS)},
        "region": {"type": "string", "enum": sorted(ALLOWED_REGION)},
        "min_days_overdue": {"type": "integer", "minimum": 0, "maximum": 365},
    },
    "required": ["status", "region", "min_days_overdue"],
    "additionalProperties": False,
}


def build_query(model_json: str, tenant_id: str) -> tuple[str, list]:
    data = json.loads(model_json)
    if set(data) != set(ALLOWED_FIELDS):
        raise ValueError("unexpected fields in filter")
    if data["status"] not in ALLOWED_STATUS or data["region"] not in ALLOWED_REGION:
        raise ValueError("value outside allowed set")
    days = int(data["min_days_overdue"])
    if not 0 <= days <= 365:
        raise ValueError("days out of range")
    sql = ("SELECT account_id, status, days_overdue FROM accounts "
           "WHERE tenant_id = ? AND status = ? AND region = ? AND days_overdue >= ? LIMIT 100")
    return sql, [tenant_id, data["status"], data["region"], days]


if __name__ == "__main__":
    db = sqlite3.connect(":memory:")
    db.execute("CREATE TABLE accounts (account_id, tenant_id, status, region, days_overdue)")
    db.execute("INSERT INTO accounts VALUES ('A-1', 't1', 'late', 'north', 45)")
    proposed = '{"status": "late", "region": "north", "min_days_overdue": 30}'  # from Claude
    sql, params = build_query(proposed, tenant_id="t1")
    print(db.execute(sql, params).fetchall())
```

And for HTML, escape by default and only allow a small markup set if you need it:

```python
import html

def render_answer_as_text(answer: str) -> str:
    """Safest default: show model output as text, preserving line breaks."""
    return "<p>" + html.escape(answer).replace("\n", "<br>") + "</p>"
```

For file paths:

```python
from pathlib import Path

WORKSPACE = Path("/srv/agent-workspace").resolve()

def safe_path(model_path: str) -> Path:
    p = (WORKSPACE / model_path).resolve()
    if not p.is_relative_to(WORKSPACE):
        raise PermissionError("path escapes workspace")
    return p
```

## Enterprise use case

*Acme Logistics* has a reporting assistant that originally let Claude write SQL against a read replica. A test
showed that a planted note in a shipment record could steer the model into writing a query that joined in a table
of driver home addresses, which the reporting user should not see.

The team moved to the pattern above: Claude selects one of eleven named report templates and fills a strict filter
schema; code builds parameterised SQL under a database role with row-level security per tenant. Output is rendered
as text in the dashboard, and CSV exports are escaped against formula injection (cells starting with `=`, `+`, `-`
or `@` are prefixed). Report accuracy on their eval set stayed the same and the attack path disappeared.

## Common mistakes

- `subprocess.run(model_output, shell=True)` in an internal tool "because only staff use it".
- Converting markdown to HTML with raw HTML enabled.
- Trusting structured output to be safe because it is valid JSON.
- Parsing tool inputs with string matching instead of `json.loads`; escaping can differ between model versions.
- Ignoring `stop_reason` and parsing truncated output.
- Exporting model text to spreadsheets without guarding against formula injection.

## Security considerations

- Apply your normal secure-coding standards and static analysis to every path from model output to a sink; label
  model output as a taint source in your SAST rules where the tool supports it.
- Sandboxes need resource limits and no ambient credentials (no cloud metadata access, no mounted secrets).
- Logging raw model output is itself a sink: escape it in log viewers and dashboards to avoid stored XSS in internal
  tools.
- Downstream agents should receive model output as untrusted content, as described in
  [indirect prompt injection](03-indirect-prompt-injection.md).

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| JSON parse errors in production | Output truncated at `max_tokens`, or no structured outputs | Check `stop_reason`; raise `max_tokens`; use `output_config.format` |
| Rendered answers lose formatting after sanitising | Sanitiser too strict | Allow a small, safe tag set (paragraphs, lists, code) with no attributes |
| Valid filters return other tenants' rows | Tenant scope not enforced in SQL | Add tenant predicate in code and row-level security in the database |

## Check your understanding

1. Why do structured outputs reduce but not eliminate insecure output handling risk?
2. What should happen before your code reads `response.content`?
3. Give the safe pattern for letting a model help query a database.
4. Why is a downstream agent a "sink"?

<details>
<summary>Answers</summary>

1. They guarantee the output matches a schema, but schema-valid values can still be malicious or unauthorised (other
   tenants' IDs, HTML in strings). Semantic validation and sink-specific encoding are still required.
2. Check `stop_reason` and handle `max_tokens`, `refusal`, `tool_use` and `pause_turn` appropriately.
3. The model selects from predefined queries or fills a constrained filter schema; code validates the values and
   builds a parameterised query under a least-privilege database role with tenant scoping.
4. It interprets the text it receives and may act on instructions within it, so the output can carry injected
   instructions to another component with different privileges.

</details>

## Further reading

- OWASP: [Top 10 for LLM Applications 2025](https://genai.owasp.org/llm-top-10/) (LLM05 Improper Output Handling)
- OWASP: [Cross Site Scripting Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html)
- Anthropic: [Structured outputs](https://platform.claude.com/docs/en/build-with-claude/structured-outputs)
- In this repository: [structured output](../03-prompt-engineering/06-structured-output.md),
  [Project 04: DevSecOps code review assistant](../20-real-world-projects/04-devsecops-code-review-assistant/README.md)
