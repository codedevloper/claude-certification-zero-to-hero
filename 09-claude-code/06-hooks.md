# Hooks

> **Level:** Advanced · **Time:** ~50 min · **Exam relevance:** CCAR-P 7.1, 7.2, 7.3, 5.1, 5.3

## In plain English

Everything Claude does in a session passes through predictable moments: a session starts, you submit a prompt, Claude is about to use a tool, a tool has finished, Claude is about to stop. A **hook** is your own code that Claude Code runs at one of those moments.

Hooks turn "please remember to…" into "this always happens":

- Format every file after Claude edits it.
- Block any shell command that touches production.
- Run the test suite before Claude is allowed to say it is finished.
- Add today's on-call rota to the context at session start.
- Send a notification when Claude is waiting for input.

The difference from `CLAUDE.md` is the difference between a sign on the wall and a lock on the door. The model can overlook a sign; it cannot walk through a lock.

## Why it matters

- **Deterministic guardrails (CCAR-P-5.1).** A `PreToolUse` hook can deny a tool call regardless of what the model decided.
- **Human-in-the-loop (CCAR-P-5.3).** Hooks can force a permission prompt (`ask`) for sensitive actions, even in auto mode.
- **Team workflow automation (CCAR-P-7.1, 7.2).** Formatting, linting, test gates and notifications become shared, committed configuration.
- **Operations (CCAR-P-7.3).** Hooks provide audit trails and integrate Claude Code with existing logging, ticketing and chat tools.

## How it works

### Lifecycle events

Claude Code exposes many events (as of 2026-10-24). The ones you will use most:

| Event | When it fires | Can block? | Typical use |
|---|---|---|---|
| `SessionStart` | Session begins or resumes (matcher: `startup`, `resume`, `clear`, `compact`) | No | Inject context (stdout becomes context), set up environment |
| `UserPromptSubmit` | You submit a prompt, before Claude sees it | Yes | Reject prompts containing secrets; add context |
| `PreToolUse` | After Claude chooses tool inputs, before the tool runs | **Yes** | Allow, deny, ask, or modify the call |
| `PermissionRequest` | A tool call needs a permission decision | Yes | Auto-answer prompts by policy |
| `PostToolUse` | After a tool succeeds | Feedback only (the tool already ran) | Format, lint, scan output, give Claude feedback |
| `PostToolUseFailure` | After a tool fails | Feedback | Diagnostics |
| `Notification` | Claude Code sends a notification (for example waiting for permission) | No | Desktop or chat alerts |
| `Stop` / `SubagentStop` | Claude (or a subagent) is about to finish its response | **Yes** (force it to continue) | Test gates, completeness checks |
| `PreCompact` / `PostCompact` | Around context compaction | Varies | Preserve notes |
| `SessionEnd` | Session terminates | No | Clean-up, logging |

Others include `InstructionsLoaded`, `ConfigChange`, `FileChanged`, `CwdChanged`, `SubagentStart`, `WorktreeCreate`, `PreModelSwitch`, `Elicitation` and more; see the [hooks reference](https://code.claude.com/docs/en/hooks).

### Configuration structure

Hooks live in settings files (or plugin, skill and subagent definitions). There are three levels: **event** → **matcher group** → **handlers**.

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          { "type": "command", "command": "python3", "args": ["${CLAUDE_PROJECT_DIR}/.claude/hooks/guard_bash.py"], "timeout": 10 }
        ]
      }
    ]
  }
}
```

- **Locations**: `~/.claude/settings.json` (you, all projects), `.claude/settings.json` (team, committed), `.claude/settings.local.json` (you, this project), managed policy, plugin `hooks/hooks.json`, skill and subagent frontmatter. Hooks **merge** across levels rather than replacing each other.
- **Matchers**: `"*"` or empty matches everything; plain names match exactly (`"Edit|Write"`); anything else is an unanchored JavaScript regular expression (`"mcp__github__.*"`). For tool events the matcher is the tool name.
- **`if`**: an optional permission-rule filter on tool events, such as `"if": "Bash(git push *)"`, so the handler only spawns for matching calls.
- **Handler types**: `command` (shell or exec form), `http` (POST the event JSON to a URL), `mcp_tool` (call a tool on an MCP server), `prompt` (single-turn model evaluation), and `agent` (a verifying subagent; experimental).
- **Timeouts** default to 600 seconds for command, HTTP and MCP-tool hooks (shorter on some events), 30 for prompt and 60 for agent hooks. Matching hooks for an event run in parallel.
- **`${CLAUDE_PROJECT_DIR}`** gives a stable path to project scripts.

### Input and output

A command hook receives the event as JSON on **stdin**. Common fields include `session_id`, `transcript_path`, `cwd`, `permission_mode` and `hook_event_name`; tool events add `tool_name`, `tool_input` and `tool_use_id` (and `agent_id`/`agent_type` inside subagents). File-tool paths arrive absolute.

The hook communicates back through its **exit code** and **stdout**:

| Exit code | Meaning |
|---|---|
| `0` | Success. If stdout is a single JSON object, its fields apply (decisions, context) |
| `2` | **Blocking error** on events that can block: the action stops and your **stderr** is the reason given to Claude |
| Anything else | Non-blocking error; the action proceeds and a hook-error notice appears |

For `PreToolUse`, return a decision in `hookSpecificOutput`:

```json
{
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "deny",
    "permissionDecisionReason": "Production database commands are blocked by policy. Use the staging DSN."
  }
}
```

`permissionDecision` can be `allow` (skip the prompt), `deny`, `ask` (force a prompt, even in auto mode) or `defer` (headless only). With several hooks, precedence is `deny` > `defer` > `ask` > `allow`. **Deny and ask permission rules are still evaluated regardless of what a hook returns**, so a hook cannot loosen a managed deny. `updatedInput` can rewrite the tool input; `additionalContext` adds text Claude sees.

`PostToolUse` and `Stop` use top-level `decision: "block"` with a `reason`. For `Stop`, blocking means "do not stop yet; here is why", and the input's `stop_hook_active` field tells you whether Claude is already continuing because of a stop hook, so you can avoid infinite loops.

### Managing and debugging hooks

- `/hooks` shows configured hooks.
- `"disableAllHooks": true` turns hooks off (it cannot disable managed hooks from outside managed settings).
- Administrators can set `allowManagedHooksOnly` to block user, project and plugin hooks, and `allowedHttpHookUrls` to restrict HTTP hook destinations.
- Run `claude --debug` (log at `~/.claude/debug/<session-id>.txt`) or `claude --debug-file <path>` to see hook execution, output parsing and timing.

## Example

A guard for shell commands, a formatter after edits, and a test gate before Claude stops.

### `.claude/settings.json`

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          { "type": "command", "command": "python3",
            "args": ["${CLAUDE_PROJECT_DIR}/.claude/hooks/guard_bash.py"], "timeout": 10 }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          { "type": "command", "command": "python3",
            "args": ["${CLAUDE_PROJECT_DIR}/.claude/hooks/format_python.py"], "timeout": 60 }
        ]
      }
    ],
    "Stop": [
      {
        "hooks": [
          { "type": "command", "command": "python3",
            "args": ["${CLAUDE_PROJECT_DIR}/.claude/hooks/require_tests.py"], "timeout": 300 }
        ]
      }
    ]
  }
}
```

### `.claude/hooks/guard_bash.py`

```python
#!/usr/bin/env python3
"""PreToolUse guard: deny shell commands that target production or read secrets."""
import json
import re
import sys

event = json.load(sys.stdin)
command = event.get("tool_input", {}).get("command", "")

RULES = [
    (r"\bprod(uction)?[-_.]?(db|database)\b|DATABASE_URL_PROD", "Production database access is blocked; use staging."),
    (r"(^|\s)(cat|less|head|tail|cp|scp)\s+[^|;&]*\.env\b", "Reading .env files is blocked; ask a human for the value you need."),
    (r"\bkubectl\b.*--context[= ]\S*prod", "kubectl against production contexts is blocked."),
]

for pattern, reason in RULES:
    if re.search(pattern, command, re.IGNORECASE):
        print(json.dumps({"hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": reason,
        }}))
        sys.exit(0)

if re.search(r"\bgit\s+push\b", command):
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": "ask",
        "permissionDecisionReason": "Pushing changes: please confirm the branch and remote.",
    }}))
sys.exit(0)  # no output: normal permission flow applies
```

### `.claude/hooks/format_python.py`

```python
#!/usr/bin/env python3
"""PostToolUse: format edited Python files with ruff if it is installed. Never blocks."""
import json
import shutil
import subprocess
import sys

event = json.load(sys.stdin)
path = event.get("tool_input", {}).get("file_path", "")
if path.endswith(".py") and shutil.which("ruff"):
    subprocess.run(["ruff", "format", "--quiet", path], check=False)  # argument list, no shell
sys.exit(0)
```

### `.claude/hooks/require_tests.py`

```python
#!/usr/bin/env python3
"""Stop hook: do not let Claude finish while the test suite fails."""
import json
import subprocess
import sys

event = json.load(sys.stdin)
if event.get("stop_hook_active"):
    sys.exit(0)  # already continuing because of this hook; avoid an infinite loop

result = subprocess.run(["python3", "-m", "pytest", "-q", "-x"], capture_output=True, text=True, check=False)
if result.returncode not in (0, 5):  # 5 = no tests collected
    tail = "\n".join(result.stdout.splitlines()[-15:])
    print(json.dumps({"decision": "block",
                      "reason": f"Tests are failing. Fix them before finishing.\n{tail}"}))
sys.exit(0)
```

Test a hook without Claude by piping sample JSON into it:

```bash
echo '{"tool_name":"Bash","tool_input":{"command":"psql $DATABASE_URL_PROD -c \"select 1\""}}' \
  | python3 .claude/hooks/guard_bash.py
```

> **Note:** Pattern-matching on command strings is a useful extra layer, not a complete defence: commands can be written in many ways. Pair hooks with permission deny rules and the sandbox ([page 4](04-permissions-and-settings.md)).

## Enterprise use case

*Northwind Lending* (fictional) needed evidence for auditors that AI-assisted changes to its loan-servicing code were reviewed and that no production credentials were ever used from developer machines. The platform team deployed hooks through **managed settings** with `allowManagedHooksOnly: true`:

- A `PreToolUse` HTTP hook posts every Bash, Edit, Write and MCP tool call to an internal policy service, which denies production endpoints and asks for confirmation on `git push` to release branches.
- A `PostToolUse` command hook appends tool name, file paths, session ID and user to a local audit log shipped to the SIEM.
- A `Stop` hook requires `make verify` (tests, lint, secret scan) to pass before Claude can declare a task complete.
- A `Notification` hook posts to the developer's chat when Claude is waiting for a permission decision.

Because the hooks are managed, developers cannot disable them with `disableAllHooks` from their own settings, and the auditors received a single configuration file plus SIEM evidence instead of per-team assurances.

## Common mistakes

- **Expecting exit code 1 to block.** Only exit code 2 (or a JSON deny) blocks; other non-zero codes are non-blocking errors.
- **Printing extra text with JSON** on stdout, which turns the output into a parse failure.
- **Stop hooks without a `stop_hook_active` check**, causing endless continuation.
- **Slow hooks on hot paths** (every `PreToolUse`), which make sessions sluggish.
- **Unquoted shell variables and string-built commands** in hook scripts.
- **Assuming hooks fire for `@` file mentions.** Files referenced with `@` are inserted without a tool call, so `PreToolUse` on `Read` does not fire; use `Read` deny rules.
- **Treating command-string regexes as complete protection.**

## Security considerations

- **Hooks run with your full user permissions and outside the sandbox.** Review every hook as you would any script you run.
- **Repository hooks are code from the repository.** In interactive sessions Claude Code holds back hooks until you accept workspace trust; in `claude -p` and SDK sessions the folder counts as trusted and committed hooks **run**. For untrusted repositories use `--bare` or `--settings '{"disableAllHooks": true}'`.
- **Use managed hooks** (`allowManagedHooksOnly`) for controls that must not be bypassed, and `allowedHttpHookUrls` to stop hooks sending data to arbitrary endpoints.
- Follow the reference's practices: validate input, quote variables, block path traversal, use absolute paths, skip sensitive files.

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| Hook never runs | Wrong matcher (case-sensitive), folder not trusted, or `disableAllHooks` set | Check `/hooks`; accept trust; fix the matcher |
| "hook error" notice | Script crashed or printed invalid JSON | Run it manually with sample stdin; check `claude --debug` logs |
| Block not taking effect | Exited 1 instead of 2, or JSON malformed | Exit 2 with stderr, or print valid JSON and exit 0 |
| Claude never stops | Stop hook blocks unconditionally | Check `stop_hook_active`; make the condition achievable |
| Sessions feel slow | Expensive hook on every tool call | Narrow the matcher, add an `if` filter, or run asynchronously |

## Check your understanding

1. Which event and output let you prevent a tool call, and what are the four possible decisions?
2. A hook exits with code 1 and prints an error. Does the tool call proceed?
3. Why can a `PreToolUse` hook returning `allow` not override a managed `deny` rule?
4. What field prevents a `Stop` hook from looping forever?
5. Why are committed hooks a risk in `claude -p` pipelines on external pull requests?

<details>
<summary>Answers</summary>

1. `PreToolUse` with `hookSpecificOutput.permissionDecision`: `allow`, `deny`, `ask` or `defer` (headless only). Exit code 2 also blocks.
2. Yes. Non-zero codes other than 2 are non-blocking errors (unless the hook is configured so that failure blocks).
3. Deny and ask permission rules are still evaluated regardless of what a hook returns.
4. `stop_hook_active` in the hook input, which is `true` when Claude is already continuing because of a stop hook.
5. `claude -p` treats the folder as trusted and runs hooks from the repository's `.claude/settings.json`, so a malicious pull request could add a hook that runs arbitrary commands with the runner's permissions. Use `--bare`, disable hooks, or restrict setting sources.

</details>

## Further reading

- [Hooks reference](https://code.claude.com/docs/en/hooks) and [hooks guide](https://code.claude.com/docs/en/hooks-guide) (Claude Code Docs)
- [Configure permissions: extend permissions with hooks](https://code.claude.com/docs/en/permissions) (Claude Code Docs)
- [Human oversight](../12-ai-security/13-human-oversight.md) and [logging and auditability](../12-ai-security/11-logging-and-auditability.md) in Module 12
- Previous: [Commands, Skills and subagents](05-commands-skills-subagents.md) · Next: [MCP in Claude Code](07-mcp-in-claude-code.md)
