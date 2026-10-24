# CCAR-F Domain 2 — Tool Design & MCP Integration (18%)

> **Track:** [CCAR-F](../README.md) · **Weight:** 18% (see [`registry.yaml`](../../registry.yaml)) ·
> **Objectives:** CCAR-F-2.1 to 2.5 · **Time:** ~6 hours including labs

Tools are how an agent acts, and their names, descriptions and error messages are almost the only thing the
model knows about them. This domain covers designing tools the model picks correctly, reporting failures so the
model can recover, giving each agent the right tools, wiring MCP servers into Claude Code and agents, and using
Claude Code's built-in tools well. It is a primary domain in the support-agent, research-system and
developer-productivity [scenarios](../scenarios.md).

Facts below were checked on **2026-10-24** against the
[MCP specification (version 2026-07-28)](https://modelcontextprotocol.io/specification/latest/server/tools),
the [Claude Code MCP docs](https://code.claude.com/docs/en/mcp) and the `claude-api` reference.

## Objectives

| ID | Objective | Where to study |
|---|---|---|
| CCAR-F-2.1 | Design tool interfaces with clear descriptions and boundaries | [Tool design best practices](../../../07-tool-use-and-function-calling/05-tool-design-best-practices.md), [Defining tools](../../../07-tool-use-and-function-calling/02-defining-tools.md) |
| CCAR-F-2.2 | Return structured error responses from MCP tools | [Building an MCP server](../../../08-model-context-protocol/03-building-an-mcp-server.md), [MCP architecture](../../../08-model-context-protocol/02-architecture.md) |
| CCAR-F-2.3 | Distribute tools across agents and configure tool choice | [Defining tools](../../../07-tool-use-and-function-calling/02-defining-tools.md), [Excessive agency](../../../12-ai-security/05-tool-misuse-and-excessive-agency.md) |
| CCAR-F-2.4 | Integrate MCP servers into Claude Code and agent workflows | [MCP in Claude Code](../../../09-claude-code/07-mcp-in-claude-code.md), [Using MCP with Claude](../../../08-model-context-protocol/04-using-mcp-with-claude.md) |
| CCAR-F-2.5 | Choose and use the built-in tools (Read, Write, Edit, Bash, Grep, Glob) well | [What is Claude Code](../../../09-claude-code/01-what-is-claude-code.md), [Permissions and settings](../../../09-claude-code/04-permissions-and-settings.md) |

## Key concepts

- **Tool description.** The text that tells the model what a tool does, when to use it, what it needs and what it
  returns. It is the main signal for tool selection.
- **Tool execution error vs protocol error.** In MCP, a failure the model can act on (bad input, upstream
  timeout, business rule) is returned *as a tool result* with `isError: true`. A malformed request or unknown
  tool is a JSON-RPC protocol error.
- **Tool scoping.** Giving each agent only the tools its role needs.
- **`tool_choice`.** The API setting that controls whether Claude may, must or must not call tools.
- **MCP scopes in Claude Code.** `local` (default, private to you in one project), `project` (shared through
  `.mcp.json` in the repository) and `user` (private to you, every project).
- **MCP resources.** Read-only content a server exposes by URI (catalogues, schemas, documents) as opposed to
  tools, which perform actions.

## Detailed technical notes

### 2.1 Tool interfaces with clear descriptions and boundaries

A description should answer five questions:

1. **What does it do?** One sentence, in domain terms.
2. **When should Claude use it, and when should it use something else?** Name the neighbouring tool.
3. **What inputs does it need, in what format?** Identifier patterns, units, date formats, an example.
4. **What does it return?** Key fields and their meaning; what an empty result means.
5. **What are the limits?** Pagination, maximum range, side effects, permissions.

Weak versus strong:

```json
{"name": "search", "description": "Searches data."}
```

```json
{
  "name": "search_product_manuals",
  "description": "Full-text search over published product manuals (PDF text, one result per section). Use for 'how do I' and specification questions about a named product. Do NOT use for order or account questions; use get_order for those. Input: query (plain words, not SQL), optional product_code like 'AW-1042'. Returns up to 10 sections with manual_id, section_title, page and a 300-character excerpt. An empty list means no manual matched; say so rather than guessing.",
  "input_schema": {
    "type": "object",
    "properties": {
      "query": {"type": "string", "description": "Plain-language search terms"},
      "product_code": {"type": "string", "pattern": "^[A-Z]{2}-\\d{4}$"}
    },
    "required": ["query"],
    "additionalProperties": false
  }
}
```

Fixes for selection problems, in order of preference:

| Symptom | Fix |
|---|---|
| Two tools with near-identical descriptions; Claude picks the wrong one | Rename to reflect the real difference (`search_web_results` vs `search_internal_docs`) and state when to use each |
| One generic tool doing several jobs (`manage_order(action, ...)`) | Split into purpose-specific tools with their own input and output contracts (`get_order_status`, `cancel_order`, `change_delivery_address`) |
| Claude prefers a built-in tool (for example Grep) over a better MCP tool | Expand the MCP tool's description to say what it does that the built-in cannot |
| A system-prompt sentence such as "always search first" makes Claude call a search tool for everything | Review the system prompt for keyword-driven instructions that override good descriptions; make them conditional |

### 2.2 Structured error responses from MCP tools

The MCP specification separates two kinds of failure:

| Kind | Examples | How it is returned | Who can fix it |
|---|---|---|---|
| **Protocol error** | Unknown tool, malformed request, server crash | JSON-RPC `error` object | Usually the client or developer |
| **Tool execution error** | Upstream timeout, invalid date, policy violation, permission denied | Normal result with `isError: true` and explanatory content | Often the model: retry, change input, escalate, or tell the user |

The specification says clients **should** pass tool execution errors to the model so it can self-correct. What
it does not define is *how* to describe the error. The exam (and good practice) expects a structured payload
inside the result so the agent can choose a recovery path. A useful convention:

```json
{
  "isError": true,
  "content": [{"type": "text", "text": "{\"error_category\": \"business_rule\", \"retryable\": false, \"code\": \"RETURN_WINDOW_CLOSED\", \"message\": \"Order 7781 was delivered 64 days ago; returns close after 30 days.\", \"customer_message\": \"This order is outside our 30-day return window.\", \"suggested_next_step\": \"Offer store credit review via open_handoff\"}"}]
}
```

`error_category`, `retryable` and the other keys are **your convention**, not MCP fields; only `isError` (and the
content array) comes from the specification. Servers that declare an `outputSchema` can also return
`structuredContent`.

| Category | Retryable? | What the agent should do |
|---|---|---|
| `transient` (timeout, 503, rate limited) | Yes, with backoff | Retry a small number of times, then report the failure with what was attempted |
| `validation` (bad format, out of range) | Yes, after fixing input | Correct the argument and call again |
| `business_rule` (policy forbids it) | No | Explain to the user in plain words; offer the allowed alternative or escalate |
| `permission` (caller not entitled) | No | Do not retry; escalate or ask for the right identity |
| `not_found` vs **empty result** | Different | A query that ran and matched nothing is a *success* with an empty list, not an error |

The last row matters: if a search tool returns `isError: true` when nothing matched, the agent retries pointlessly;
if a timeout is returned as an empty list, the agent wrongly concludes there is no data. A generic "Operation
failed" message blocks every sensible recovery decision.

In a multi-agent system, subagents should handle transient errors locally (retry, alternative source) and pass
up only what they cannot resolve, with the partial results and what they tried. See
[Domain 5](domain-5.md), 5.3.

### 2.3 Distributing tools across agents and configuring tool choice

**Fewer, role-specific tools select better.** An agent with four or five well-described tools chooses more
reliably than one with twenty; tools outside an agent's role invite misuse (a synthesis agent that starts running
web searches instead of using the findings it was given).

| Practice | Example |
|---|---|
| Scope tools to the role | Reader subagent: `open_report`, `list_report_sections`. Synthesiser: no search tools |
| Replace a general tool with a constrained one | Swap an open `run_sql(query)` for `get_supplier(supplier_id)` and `list_supplier_orders(supplier_id, since)` |
| Allow a narrow cross-role tool for a frequent need | Give the report writer a read-only `get_source_metadata(source_id)` so it can format references itself, while any new research goes back through the coordinator |
| Restrict in configuration, not prose | `AgentDefinition(tools=[...])`, `disallowedTools`, Claude Code permission rules |

**`tool_choice` options** on the Messages API:

| Value | Meaning | Current model support (as of 2026-10-24) |
|---|---|---|
| `{"type": "auto"}` (default with tools) | Claude decides whether to call a tool | All models |
| `{"type": "none"}` | Claude must not call tools | All models |
| `{"type": "any"}` | Claude must call some tool | **400 on Claude Opus 5.5, Sonnet 5.5, Fable 5.1 and Mythos 5.1**; Haiku 5.5 and older models accept it |
| `{"type": "tool", "name": "..."}` | Claude must call that tool | Same restriction as `any` |

The exam guide teaches `any` and forced selection as ways to guarantee a tool call (for example, guaranteeing
structured output when several extraction schemas exist, or forcing a first step). Know the concept, and know
the current replacement on the newest models:

1. `tool_choice: {"type": "auto"}` plus an explicit instruction naming the tool ("Call `classify_document`
   first, then...").
2. `strict: true` on the tool so its arguments always match the schema.
3. Check that a tool call happened; if not, send a short follow-up asking for it.
4. If the call existed only to get JSON back, use structured outputs (`output_config.format`) instead (see
   [Domain 4](domain-4.md), 4.3).
5. For a fixed first step, run it as its own request (a workflow step), then continue.

`disable_parallel_tool_use: true` with `auto` still limits Claude to at most one call per turn.

### 2.4 Integrating MCP servers into Claude Code and agents

| Scope | Stored in | Shared? | Use for |
|---|---|---|---|
| `local` (default) | `~/.claude.json`, under this project's path | No | Trying a server in one project |
| `project` | `.mcp.json` at the repository root | Yes, through version control | Team tooling everyone needs |
| `user` | `~/.claude.json` | No | Personal servers you want in every project |

When the same server name appears in several places, local beats project beats user (then plugin servers and
claude.ai connectors); the winning entry is used whole, not merged. Organisation-managed servers rank above all
of these.

Secrets stay out of the repository through **environment variable expansion** in `.mcp.json`: `${VAR}` or
`${VAR:-default}` in `command`, `args`, `env`, `url` and `headers`.

```json
{
  "mcpServers": {
    "tickets": {
      "type": "http",
      "url": "${TICKETS_MCP_URL:-https://mcp.tickets.example.com}/mcp",
      "headers": {"Authorization": "Bearer ${TICKETS_TOKEN}"}
    }
  }
}
```

```bash
claude mcp add --scope project --transport http tickets https://mcp.tickets.example.com/mcp
claude mcp add --scope user --transport stdio scratch-notes -- npx -y example-notes-server
```

Behaviour to know:

- Interactive sessions ask each developer to approve project-scoped servers before first use. Non-interactive
  runs (`claude -p`, the Agent SDK) cannot show that prompt and load them, so CI should pin servers explicitly
  (`--mcp-config` with `--strict-mcp-config`, or `--bare`).
- All configured servers' tools are discovered at connection time and are available together. Claude Code's
  tool search is on by default and loads MCP tool definitions on demand, which keeps many servers from flooding
  context.
- MCP tool output above 10,000 tokens triggers a warning and is capped at 25,000 tokens by default
  (`MAX_MCP_OUTPUT_TOKENS` raises it).
- **Resources** are referenced with `@server:protocol://resource/path` and attached to the prompt. Exposing a
  catalogue (open tickets, schema list, docs index) as a resource lets the agent see what exists without
  exploratory tool calls.
- **Prompts** from servers appear as commands, for example `/mcp__tickets__triage`.
- Prefer an existing, maintained server for a standard system (issue tracker, source host) and write custom
  servers for team-specific workflows. Review third-party servers like any dependency (see
  [MCP security](../../../08-model-context-protocol/05-mcp-security.md)).

In the Agent SDK, pass servers with the `mcp_servers` (`mcpServers`) option and allow their tools by name
(`mcp__tickets__get_ticket`) or by server pattern.

### 2.5 Built-in tools

| Need | Tool | Example |
|---|---|---|
| Find files by name or path pattern | **Glob** | `**/*.spec.ts`, `services/*/Dockerfile` |
| Find content inside files | **Grep** | All call sites of `apply_discount(`, an error string, an import |
| Read a whole file | **Read** | Follow an import after Grep found the entry point |
| Make a targeted change | **Edit** | Replace one unique snippet with another |
| Create or fully rewrite a file | **Write** | New module, generated fixture |
| Run commands | **Bash** | Tests, builds, `git` |

**Edit needs a unique anchor.** Edit replaces an exact string; if that string occurs more than once, the edit
fails. Options: include more surrounding lines to make the match unique, use the replace-all option when every
occurrence should change, or (the exam guide's fallback) Read the whole file and Write it back with the change.

**Explore incrementally.** Start with Grep or Glob to find entry points, Read only the files that matter, and
follow imports outward. Reading every file up front wastes context and degrades later answers. To trace a
function that is re-exported through wrapper modules, first find every name it is exported under, then search
for each name.

## Worked design scenario

*Fabrikam Labs* is building an internal research agent with three subagents. Tool selection is unreliable and
failures stall the run.

1. **Descriptions:** `report_tool` and `report_helper` had near-identical descriptions. They become
   `summarise_report(report_id)` and `compare_reports(report_ids)`, each saying when to use the other.
2. **Errors:** the search server returned "Search failed" for timeouts and for zero hits. It now returns
   `isError: true` with `error_category: "transient", retryable: true` for timeouts, and a successful empty
   list for zero hits.
3. **Distribution:** the synthesiser lost its search tools; the report writer gained read-only
   `get_source_metadata`. The reader's free-form database query tool became two narrow lookups.
4. **Tool choice:** the pipeline used `tool_choice: {"type": "any"}` on Claude Opus 5.5 and received 400 errors
   after an upgrade. It now uses `auto`, an explicit instruction, `strict: true` tools and a check that the call
   happened.
5. **Claude Code:** the team's shared servers live in `.mcp.json` with `${...}` tokens; each developer's
   experimental servers are user-scoped.

## Anti-patterns

- One-line descriptions ("Gets data") and tools whose names differ by one word.
- "Operation failed" for every error, or empty results reported as errors.
- Every agent holding every tool "just in case".
- Hard-coded tokens in `.mcp.json` committed to the repository.
- Forcing tool calls with `any` on a model that rejects it, or relying on forcing instead of good design.
- Reading an entire repository before searching it.

## Labs and further practice

- [Lab 08: Tool invocation](../../../19-hands-on-labs/lab-08-tool-invocation/README.md)
- [Lab 09: MCP fundamentals](../../../19-hands-on-labs/lab-09-mcp-fundamentals/README.md)
- [Lab 10: Claude Code workflows](../../../19-hands-on-labs/lab-10-claude-code-workflows/README.md)
- [MCP cheat sheet](../../../22-cheat-sheets/mcp.md)
- Practical exercise 4 in [`practical-exercises.md`](../practical-exercises.md)

## Self-check

1. Name four things a good tool description states.
2. How should an MCP tool report that an upstream API timed out, and how should it report that a search matched
   nothing?
3. What does `tool_choice: {"type": "any"}` do on Claude Opus 5.5, and what do you use instead?
4. Where do you configure an MCP server the whole team should get, and how do you keep its token out of git?
5. An Edit fails because the target text appears three times. What are your options?

<details>
<summary>Answers</summary>

1. Any four of: what it does, when to use it versus similar tools, input formats with an example, what it
   returns, limits and side effects.
2. Timeout: a tool result with `isError: true` and a structured payload marking it transient and retryable.
   No matches: a successful result with an empty list (not an error).
3. It returns a 400. Use `auto` with an explicit instruction, `strict: true` tools and a check that the call
   happened, or structured outputs if you only need JSON.
4. In `.mcp.json` at the repository root (project scope), with `${TOKEN}` environment variable expansion.
5. Add more surrounding context to make the match unique, use replace-all if every occurrence should change, or
   Read the file and Write the full corrected version.

</details>
