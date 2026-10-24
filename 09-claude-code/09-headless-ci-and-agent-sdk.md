# Headless, CI and the Agent SDK

> **Level:** Advanced · **Time:** ~50 min · **Exam relevance:** CCAR-P 7.2, 7.3, 1.3, 3.7, 5.1

## In plain English

Everything you can do interactively in Claude Code you can also do **without a person at the keyboard**:

- **Headless mode** (`claude -p "…"`) runs one task and prints the result, so scripts and pipelines can use it. Pipe in a log file, ask for a summary, get JSON back.
- **CI integrations** such as the Claude Code GitHub Action run Claude Code inside your workflows: respond to `@claude` mentions on pull requests, review code, triage issues, or run a scheduled report.
- **The Claude Agent SDK** turns Claude Code into a Python or TypeScript library, so you can build your own agents on the same loop, tools, permissions, hooks and context management.

Without a human in the loop, the configuration and guardrails you set up on earlier pages matter even more: nobody is there to click "No".

## Why it matters

- **Workflow automation (CCAR-P-7.2):** reviews on every pull request, nightly dependency checks, release notes, log triage.
- **Operations (CCAR-P-7.3):** headless runs in incident tooling and CI need predictable output, budgets and error handling.
- **Architecture patterns (CCAR-P-1.3):** a headless run is a workflow step; the Agent SDK is an agent harness you embed.
- **Integration choice (CCAR-P-3.7):** CLI subprocess, Agent SDK, Claude API with the Tool Runner, or Managed Agents each fit different needs.
- **Guardrails (CCAR-P-5.1):** headless runs skip interactive trust and approval prompts, so you must restrict them explicitly.

## How it works

### `claude -p` basics

```bash
claude -p "What does the auth module do?"                                   # plain text answer
tail -200 app.log | claude -p "Summarise errors and likely causes"           # pipe data in
claude -p "Summarise this project" --output-format json | jq -r '.result'   # JSON with metadata
```

- Exit code `0` on success, non-zero on failure. Invalid flags go to stderr; failures inside the run (for example missing authentication) appear as the result on stdout.
- `--output-format`: `text` (default), `json` (result, session ID, usage and estimated `total_cost_usd`), or `stream-json` (newline-delimited events; add `--verbose` and optionally `--include-partial-messages`).
- `--json-schema '<schema>'` with `--output-format json` returns validated output in `structured_output`. If a run ends without valid output (for example a refusal), the field is absent, so check for it.
- `--continue` / `--resume <id>` continue earlier conversations; `--append-system-prompt` adds instructions; `--model` and `--effort` choose model and depth.

### Controlling what a headless run may do

| Flag (as of 2026-10-24) | Effect |
|---|---|
| `--allowedTools "Read,Edit,Bash(pnpm test *)"` | Pre-approve specific tools or patterns |
| `--disallowedTools "WebFetch"` | Deny tools (a bare name removes the tool) |
| `--permission-mode dontAsk` | Deny anything that would prompt; only allowed tools run (good for locked-down CI) |
| `--permission-mode acceptEdits` | Allow file edits and common filesystem commands; other commands still need allow rules |
| `--permission-mode auto` | A classifier reviews actions instead of a person |
| `--permission-prompts none` | Nobody can answer prompts: deny them, tell Claude not to retry, and remove tools that need a person |
| `--max-turns N` | Cap agentic turns |
| `--max-budget-usd X` | Stop when estimated API spend reaches X |
| `--bare` | Skip auto-discovery of hooks, skills, commands, subagents, plugins, MCP servers, auto memory and CLAUDE.md; requires `ANTHROPIC_API_KEY` (or `apiKeyHelper` via `--settings`) |
| `--setting-sources user` | Load only user settings (not the repository's project or local settings) |
| `--mcp-config <file>` with `--strict-mcp-config` | Use only the MCP servers you pass |
| `--settings '{"disableAllHooks": true}'` | Turn hooks off for the run |

With Claude Code v2.1.302 or later, a `claude -p` run starts in Manual (`default`) mode when nothing sets a mode, and calls that need approval are denied unless a rule, hook or permission host approves them.

> **Warning:** `claude -p` and Agent SDK sessions **do not show the workspace trust dialog**. Without `--bare` or restricted setting sources, a run executes the repository's committed hooks, connects its `.mcp.json` servers without asking, and applies its `env` block. Before running headless Claude Code on code you did not write (for example pull requests from forks), use `--bare` or `--setting-sources user`, `--strict-mcp-config`, and disable hooks.

### GitHub Actions

The [Claude Code GitHub Action](https://github.com/anthropics/claude-code-action) (`anthropics/claude-code-action@v1`) runs Claude Code in your workflows.

- **Quick setup:** run `/install-github-app` in Claude Code (github.com repositories only). It installs the Claude GitHub App, stores a repository secret (`ANTHROPIC_API_KEY` for an API key, or `CLAUDE_CODE_OAUTH_TOKEN` for a subscription token), and opens a pull request with workflow files.
- **Interactive mode:** with no `prompt` input, Claude responds to `@claude` in issue and pull request comments.
- **Automation mode:** with a `prompt` input (plain text or a `/skill` invocation), it runs on any event, including a schedule. Pass CLI flags through `claude_args` (for example `--allowedTools`, `--max-turns`, `--model`).
- On public repositories, GitHub withholds secrets from workflows triggered by fork pull requests, so reviews run only for branches in the same repository.

GitLab CI/CD has a separate integration; see the Claude Code docs.

### The Claude Agent SDK

The Agent SDK (`claude-agent-sdk` for Python, `@anthropic-ai/claude-agent-sdk` for TypeScript) runs the Claude Code harness as a library: built-in tools (Read, Write, Edit, Bash, Glob, Grep, WebSearch, WebFetch), the agent loop, context management, permissions, hooks, subagents, MCP, sessions, and the same `.claude/` configuration if you choose to load it.

| You want to | Use |
|---|---|
| Interactive development or one-off tasks | Claude Code CLI |
| A script or pipeline step in any language | `claude -p` as a subprocess with `--output-format json` |
| Embed a Claude Code-style agent in your Python or TypeScript service, on your infrastructure | **Agent SDK** |
| Call the Claude API with **your own** tools and loop | Client SDK (Messages API) with the Tool Runner or a manual loop ([Module 07](../07-tool-use-and-function-calling/03-the-tool-use-loop.md)) |
| Have Anthropic host the agent loop and sandbox | Managed Agents ([Module 10](../10-agentic-ai/06-managed-agents-and-agent-sdk.md)) |

Key Python options (`ClaudeAgentOptions`): `allowed_tools`, `permission_mode`, `can_use_tool` (a callback for approval decisions), `system_prompt`, `mcp_servers`, `max_turns`, `max_budget_usd`, `cwd`, and `setting_sources` (pass `[]` to load no user, project or local settings). The final `ResultMessage` carries `subtype`, `is_error`, `result`, `structured_output`, `total_cost_usd`, `num_turns` and `permission_denials`.

Authentication: use API keys (or cloud-provider credentials). As of 2026-10-24, if you build a product on the Agent SDK, your users authenticate with API credentials; Anthropic's terms do not let you sign them in with their claude.ai accounts or borrow claude.ai plan limits without prior approval.

## Example

### A CI review step with structured output

> **Cost:** requires API credits (live mode).

```python
"""ci_review.py: ask Claude Code for a structured review of the current branch and fail on blockers.

Run in CI after checkout. Needs ANTHROPIC_API_KEY in the environment (from the CI secret store).
"""
import json
import subprocess
import sys

SCHEMA = {
    "type": "object",
    "properties": {
        "verdict": {"type": "string", "enum": ["approve", "changes_requested"]},
        "blockers": {"type": "array", "items": {"type": "object", "properties": {
            "file": {"type": "string"}, "line": {"type": "integer"}, "issue": {"type": "string"}},
            "required": ["file", "issue"]}},
        "summary": {"type": "string"},
    },
    "required": ["verdict", "blockers", "summary"],
}

cmd = [
    "claude", "-p",
    "Review the diff between origin/main and HEAD for correctness and security bugs. "
    "Only report blockers you are confident about.",
    "--bare",                                   # ignore repository hooks, MCP servers, skills
    "--output-format", "json",
    "--json-schema", json.dumps(SCHEMA),
    "--allowedTools", "Read,Grep,Glob,Bash(git diff *),Bash(git log *)",
    "--permission-mode", "dontAsk",             # anything else is denied, never prompted
    "--max-turns", "30",
    "--max-budget-usd", "2",
]
proc = subprocess.run(cmd, capture_output=True, text=True, timeout=1200, check=False)
if proc.returncode != 0:
    print("claude failed:", proc.stderr or proc.stdout, file=sys.stderr)
    sys.exit(2)

payload = json.loads(proc.stdout)
review = payload.get("structured_output")
if review is None:                              # e.g. refusal or budget reached
    print("No structured review produced:", payload.get("result"), file=sys.stderr)
    sys.exit(2)

print(review["summary"])
for b in review["blockers"]:
    print(f"BLOCKER {b['file']}:{b.get('line', '?')} {b['issue']}")
print(f"(estimated cost ${payload.get('total_cost_usd', 0):.2f})")
sys.exit(1 if review["verdict"] == "changes_requested" else 0)
```

### A GitHub Actions workflow responding to `@claude`

This is a security-hardened variant of the example in the official
[Claude Code GitHub Actions documentation](https://code.claude.com/docs/en/github-actions). Compared with a
minimal setup, it only answers mentions on pull requests, only from people with a role in the repository, runs with
read-only repository contents, and has a time limit. Check the official page for the inputs the action currently
supports.

```yaml
name: Claude PR assistant (members only)

on:
  issue_comment:
    types: [created]

permissions: {}                      # nothing by default; the job grants what it needs

jobs:
  assist:
    # Pull-request comments only, mentioning @claude, from owners, members or collaborators.
    if: >-
      github.event.issue.pull_request &&
      contains(github.event.comment.body, '@claude') &&
      contains(fromJSON('["OWNER", "MEMBER", "COLLABORATOR"]'), github.event.comment.author_association)
    runs-on: ubuntu-latest
    timeout-minutes: 15
    permissions:
      contents: read                 # Claude can read the code but not push to it
      pull-requests: write           # post review comments
      issues: write                  # reply to the triggering comment
      id-token: write                # used by the action to authenticate
    steps:
      - uses: actions/checkout@v6
        with:
          fetch-depth: 1
      - uses: anthropics/claude-code-action@v1
        with:
          anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}
          claude_args: "--max-turns 10"
```

### A minimal Agent SDK agent (Python)

> **Cost:** requires API credits (live mode).

```python
import asyncio

from claude_agent_sdk import AssistantMessage, ClaudeAgentOptions, ResultMessage, query


async def main() -> None:
    options = ClaudeAgentOptions(
        allowed_tools=["Read", "Grep", "Glob"],   # read-only investigation
        permission_mode="dontAsk",                # anything not allowed is denied
        setting_sources=[],                       # do not load user/project/local settings
        max_turns=20,
        system_prompt="You are an incident analyst. Cite file paths for every claim.",
    )
    async for message in query(prompt="Find where request timeouts are configured and summarise them.",
                               options=options):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if hasattr(block, "text"):
                    print(block.text)
        elif isinstance(message, ResultMessage):
            print("done:", message.subtype, "cost:", message.total_cost_usd)


asyncio.run(main())
```

Install with `pip install claude-agent-sdk` (or `uv add claude-agent-sdk`).

## Enterprise use case

*Tailwind Traders* (fictional) automated three workflows:

1. **Pull request review.** A GitHub Actions job runs a team `/review` skill through the Claude Code Action on internal pull requests. Fork pull requests are excluded (secrets are withheld anyway), and the job uses `--max-turns` and a dedicated, budget-limited API workspace.
2. **Nightly dependency report.** A scheduled pipeline runs `claude -p --bare` with `--output-format json` and a JSON schema, read-only tools and `--permission-mode dontAsk`, and files a ticket when `structured_output` lists critical upgrades.
3. **Incident assistant.** The SRE team built a small service on the **Agent SDK** that, when paged, investigates logs and runbooks read-only, with `can_use_tool` routing any write action to the on-call engineer in chat. They chose the Agent SDK over the Messages API Tool Runner because they wanted Claude Code's built-in file and search tools and hooks without rebuilding them.

All three share a policy: no headless run loads repository-supplied hooks or MCP servers unless the repository is internal and the job explicitly opts in.

## Common mistakes

- **Running `claude -p` on untrusted code** without `--bare` or restricted setting sources.
- **Not checking for `structured_output`** before using it.
- **No turn or budget caps** in scheduled jobs.
- **Using `bypassPermissions` in CI on shared runners** instead of `dontAsk` with explicit allow rules (or an isolated container).
- **Expecting interactive tools** (questions, approvals) to work in unattended runs; use `--permission-prompts none` so Claude stops waiting.
- **Confusing the Agent SDK with the Tool Runner.** The Agent SDK is the Claude Code harness with built-in tools; the Tool Runner is a client-SDK helper for your own tools.
- **Storing API keys in workflow files** instead of CI secrets.

## Security considerations

- Least privilege for automation: read-only tools by default, explicit allow rules for anything else, `dontAsk` or auto mode, and no bypass on shared infrastructure.
- Isolate runners: ephemeral containers, no long-lived credentials, network egress controls.
- Treat pull request content and issue comments as untrusted input (prompt injection), especially in workflows that can push commits.
- Keep GitHub workflow `permissions` minimal for each job.
- Log runs (`stream-json` events or OpenTelemetry) for audit.

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| Run hangs waiting | A permission host is waiting for an answer | `--permission-prompts none`, or allow the needed tools |
| `this workspace has not been trusted` warning; allow rules ignored | Project allow rules need trust, which `-p` never grants | Pass rules with `--allowedTools` or `--settings` |
| `--bare` run fails to authenticate | Bare mode does not read OAuth or keychain credentials | Set `ANTHROPIC_API_KEY` or pass `apiKeyHelper` in `--settings` |
| No `structured_output` | Refusal, budget or turn limit reached, or schema problem | Check `result` and `subtype`; validate the schema |
| `@claude` does nothing | Workflow `if:` filter, missing secret, or app not installed | Re-run `/install-github-app`; check workflow logs |

## Check your understanding

1. Which flags would you combine for a locked-down, read-only CI run on code you do not fully trust?
2. Where does validated JSON appear when you use `--json-schema`, and what must your script check?
3. What is the difference between interactive mode and automation mode in the Claude Code GitHub Action?
4. When would you choose the Agent SDK over `claude -p` in a subprocess, and over the Messages API Tool Runner?
5. Why does `claude -p` deserve more caution than an interactive session in an unfamiliar repository?

<details>
<summary>Answers</summary>

1. For example: `--bare` (or `--setting-sources user` with `--strict-mcp-config`), `--allowedTools` with read-only tools, `--permission-mode dontAsk`, `--max-turns`, `--max-budget-usd`, and `--settings '{"disableAllHooks": true}'` if not using `--bare`.
2. In the `structured_output` field of the JSON result; check that it is present before using it, because runs that end without valid output omit it.
3. Interactive mode (no `prompt` input) waits for `@claude` mentions in comments; automation mode (a `prompt` input) runs a task on any configured event, including schedules.
4. Choose the Agent SDK when you want to embed a Claude Code-style agent with built-in tools, hooks and permissions inside a Python or TypeScript service; choose `claude -p` for simple script steps or other languages. Choose the Tool Runner when you only need your own tools and a lighter dependency on the Messages API.
5. It never shows the workspace trust dialog, so repository hooks run, `.mcp.json` servers connect without asking and the project `env` applies.

</details>

## Further reading

- [Run Claude Code programmatically (headless)](https://code.claude.com/docs/en/headless) and [CLI reference](https://code.claude.com/docs/en/cli-reference) (Claude Code Docs)
- [Claude Code GitHub Actions](https://code.claude.com/docs/en/github-actions) and [GitLab CI/CD](https://code.claude.com/docs/en/gitlab-ci-cd) (Claude Code Docs)
- [Agent SDK overview](https://code.claude.com/docs/en/agent-sdk/overview) and [Python reference](https://code.claude.com/docs/en/agent-sdk/python) (Claude Code Docs)
- [Managed agents and the Agent SDK](../10-agentic-ai/06-managed-agents-and-agent-sdk.md) in Module 10

<!-- page-nav:start -->
---

[← Previous: Team Rollout](08-team-rollout.md) · [Module overview](README.md) · [Next module: Module 10 — Agentic AI →](../10-agentic-ai/README.md)
<!-- page-nav:end -->
