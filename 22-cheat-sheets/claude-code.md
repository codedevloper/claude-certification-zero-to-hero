# Claude Code Cheat Sheet

> **As of 2026-10-24**, checked against [code.claude.com/docs](https://code.claude.com/docs/en/overview)
> (CLI reference, commands, settings, permissions, memory, hooks, skills, subagents and MCP pages). Claude Code ships
> frequently; run `/help` or `claude --help` for the version you have. Full lessons:
> [09 · Claude Code](../09-claude-code/README.md).

## 1. Starting and resuming

| Command | What it does |
|---|---|
| `claude` | Start an interactive session in the current directory |
| `claude "explain this project"` | Start interactively with a first prompt |
| `claude -p "query"` | Print mode: answer once and exit (scripts, CI) |
| `cat log.txt \| claude -p "explain"` | Pipe content into print mode |
| `claude -c` | Continue the most recent conversation in this directory |
| `claude -r "<id-or-name>"` | Resume a specific session (or open the picker) |
| `claude update` | Update to the latest version |
| `claude doctor` | Read-only install and settings diagnostics |
| `claude auth login` / `status` / `logout` | Manage sign-in (`--console` for API billing) |
| `claude mcp ...` | Add, list, remove and log in to MCP servers |

## 2. Useful flags

| Flag | Purpose |
|---|---|
| `--model <alias-or-id>` | Model for this session (`opus`, `sonnet`, `haiku`, `fable`, or a full ID) |
| `--effort <level>` | `low`, `medium`, `high`, `xhigh`, `max` (availability depends on model) |
| `--permission-mode <mode>` | Start in `default`, `acceptEdits`, `plan`, `auto`, `dontAsk` or `bypassPermissions` |
| `--allowedTools "Bash(npm test *)" "Read"` | Pre-approve tools for this run |
| `--disallowedTools "Bash(rm *)"` | Deny rules; a bare name removes the tool entirely |
| `--output-format text\|json\|stream-json` | Print-mode output format |
| `--max-turns N` | Cap agentic turns in print mode |
| `--append-system-prompt "..."` | Add text to the default system prompt |
| `--mcp-config <file-or-json>` | Load MCP servers for this run |
| `--add-dir <path>` | Give file access to another directory |
| `--settings <file-or-json>` | One-session settings override (below managed) |
| `--dangerously-skip-permissions` | Same as `bypassPermissions`. Only in isolated, disposable environments |

## 3. In-session slash commands (selection)

| Command | Use |
|---|---|
| `/init` | Generate a starter `CLAUDE.md` for the project |
| `/memory` | Edit `CLAUDE.md` files and manage auto memory |
| `/clear` | Start a fresh conversation (empty context) |
| `/compact [focus]` | Summarise the conversation to free context |
| `/context` | Visualise what is using the context window |
| `/model`, `/effort` | Switch model or effort level |
| `/permissions` | View and edit allow / ask / deny rules |
| `/hooks` | View hook configuration |
| `/mcp` | Manage MCP servers, including OAuth sign-in |
| `/agents` | Create or manage subagents |
| `/skills` | List available skills |
| `/plugin` | Manage plugins and marketplaces |
| `/config`, `/status` | Settings dialog; status shows loaded setting sources |
| `/usage` (`/cost`) | Session cost and plan usage |
| `/rewind` | Roll back conversation and/or code to a checkpoint |
| `/resume` | Pick up an earlier session |
| `/review`, `/security-review` | Review changes; security-focused review of the branch diff |
| `/doctor` | Setup checkup |
| `/help` | All commands |

Type `/` to see everything, including your own skills and plugin commands.

## 4. Files Claude Code reads

| File | Scope | Purpose |
|---|---|---|
| `CLAUDE.md` or `.claude/CLAUDE.md` | Project, committed | Build/test commands, conventions, architecture notes |
| `CLAUDE.local.md` | Project, personal (gitignore it) | Your sandbox URLs, personal preferences |
| `~/.claude/CLAUDE.md` | User, all projects | Personal defaults |
| Managed `CLAUDE.md` (system path) | Organisation | Policies from IT/security |
| `.claude/rules/*.md` | Project | Topic rules; `paths` frontmatter scopes them to files |
| `.claude/settings.json` | Project, committed | Team permissions, hooks, env, plugins |
| `.claude/settings.local.json` | Project, personal | Your overrides; standing approvals land here |
| `~/.claude/settings.json` | User | Personal settings |
| `managed-settings.json` / MDM / server-managed | Organisation | Enforced policy (highest precedence) |
| `.mcp.json` | Project, committed | Shared MCP servers |
| `~/.claude.json` | User | Local and user-scope MCP servers, account state |
| `.claude/skills/<name>/SKILL.md` | Project | Skills (also `~/.claude/skills/`) |
| `.claude/commands/<name>.md` | Project | Legacy custom commands (now merged into skills) |
| `.claude/agents/<name>.md` | Project | Subagents (also `~/.claude/agents/`) |

`CLAUDE.md` imports other files with `@path/to/file` (up to four hops). Keep each file short (the docs suggest under
200 lines); CLAUDE.md is guidance, not enforcement. To **block** something, use a deny rule or a hook.

## 5. Settings precedence (highest first)

1. Managed settings (cannot be overridden)
2. Command line (`--settings`)
3. Project local (`.claude/settings.local.json`)
4. Shared project (`.claude/settings.json`)
5. User (`~/.claude/settings.json`)

List settings such as `permissions.allow` **merge** across levels instead of replacing each other.

## 6. Permissions

```json
{
  "permissions": {
    "allow": ["Bash(npm run test *)", "Bash(git diff *)", "WebFetch(domain:docs.python.org)"],
    "ask":   ["Bash(git push *)"],
    "deny":  ["Read(./.env)", "Read(./.env.*)", "Bash(curl *)", "mcp__payments__*"]
  }
}
```

- Evaluation order: **deny → ask → allow**. A broad deny beats a narrower allow.
- `mcp__<server>__<tool>` names one MCP tool; `mcp__<server>__*` names all tools on a server.
- Modes: `default` (Manual; prompts on first use), `acceptEdits` (auto-accept edits in the working directory),
  `plan` (explore read-only, propose a plan), `auto` (a classifier reviews actions instead of prompts), `dontAsk`
  (auto-deny anything that would prompt), `bypassPermissions` (skip prompts; isolated environments only).

## 7. Hooks

Hooks run your code at lifecycle events. Configure them in any settings file:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [{"type": "command", "command": "${CLAUDE_PROJECT_DIR}/.claude/hooks/check-bash.sh", "timeout": 30}]
      }
    ],
    "PostToolUse": [
      {"matcher": "Edit|Write", "hooks": [{"type": "command", "command": "${CLAUDE_PROJECT_DIR}/.claude/hooks/format.sh"}]}
    ]
  }
}
```

| Common event | Fires | Typical use |
|---|---|---|
| `SessionStart` | Session begins or resumes | Load context, check environment |
| `UserPromptSubmit` | Before a prompt is processed | Add context, block secrets in prompts |
| `PreToolUse` | Before a tool runs | Block dangerous commands, enforce policy |
| `PermissionRequest` | A permission dialog would show | Auto-approve or deny programmatically |
| `PostToolUse` | After a tool succeeds | Format, lint, log |
| `Notification` | Claude needs attention | Desktop or chat alerts |
| `Stop` / `SubagentStop` | Claude or a subagent finishes | Run tests, enforce "done" criteria |
| `PreCompact` / `PostCompact` | Around compaction | Preserve key context |
| `SessionEnd` | Session ends | Clean-up, audit log |

A hook receives the event as JSON on stdin (for tool events this includes `tool_name` and `tool_input`), so a script
such as `format.sh` reads the edited file path from there. Exit codes for `command` hooks: **0** success (stdout may be JSON), **2** blocking error on events that can block
(stderr becomes the reason), **other** non-blocking error. Handler types: `command`, `http`, `mcp_tool`, `prompt`,
`agent`. Matchers: exact names, `Edit|Write` lists, or a regular expression such as `mcp__github__.*`.

## 8. Skills and subagents

```markdown
---
name: release-notes
description: Draft release notes from merged PRs. Use when the user asks for a changelog or release notes.
disable-model-invocation: true
allowed-tools: Bash(git log *)
---
1. Collect merged PR titles since the last tag.
2. Group them as Features, Fixes, Security.
```

- **Skill**: `SKILL.md` in its own folder; only `name` and `description` sit in context until it is invoked
  (progressive disclosure). Invoke with `/name` or let Claude load it when relevant.
- **Subagent**: Markdown file with `name`, `description`, optional `tools`, `model`, `permissionMode`; runs in its
  **own context window** and returns a summary. Use it to keep noisy searches out of the main context.

## 9. MCP in Claude Code

```bash
claude mcp add --transport http docs https://mcp.example.com/mcp                 # remote (recommended)
claude mcp add --env API_KEY="$API_KEY" --transport stdio local-db -- python server.py   # name must not follow --env
claude mcp add --transport http shared --scope project https://mcp.example.com/mcp
claude mcp list
```

Scopes: `local` (default, you only, this project), `project` (`.mcp.json`, shared), `user` (all your projects).
Authenticate remote servers with `/mcp` or `claude mcp login <name>`. SSE transport is deprecated.
Environment knobs: `MCP_TIMEOUT` (startup), `MCP_TOOL_TIMEOUT`, `MAX_MCP_OUTPUT_TOKENS` (default 25,000).

## 10. Headless and CI

```bash
claude -p "Review the diff for security issues and output JSON" \
  --output-format json --permission-mode plan --max-turns 5 \
  --allowedTools "Read" "Grep" "Bash(git diff *)"
```

Use least-privilege tools, a turn cap and a non-interactive permission mode; never pass secrets in the prompt. For
programmatic agents built on the same harness, see the Claude Agent SDK
([09 · Headless, CI and the Agent SDK](../09-claude-code/09-headless-ci-and-agent-sdk.md)).

## Further reading

- [CLI reference](https://code.claude.com/docs/en/cli-reference) · [Commands](https://code.claude.com/docs/en/commands)
- [Settings](https://code.claude.com/docs/en/settings) · [Permissions](https://code.claude.com/docs/en/permissions)
- [Memory (CLAUDE.md)](https://code.claude.com/docs/en/memory) · [Hooks](https://code.claude.com/docs/en/hooks)
- [Skills](https://code.claude.com/docs/en/skills) · [Subagents](https://code.claude.com/docs/en/sub-agents) · [MCP](https://code.claude.com/docs/en/mcp)
