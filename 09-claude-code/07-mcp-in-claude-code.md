# MCP in Claude Code

> **Level:** Intermediate · **Time:** ~40 min · **Exam relevance:** CCAR-P 7.1, 3.1, 3.7, 3.8

## In plain English

Out of the box, Claude Code can work with your files, your shell and the web. **MCP servers** let it reach everything else: your issue tracker, design documents, databases, monitoring dashboards and internal services. Adding one is a single command, and once added its tools appear alongside Claude Code's built-in tools.

This page is the practical, Claude Code-specific companion to [Module 08](../08-model-context-protocol/README.md): how to add servers, where the configuration is stored, how teams share it, how it affects context and permissions, and how administrators control it.

## Why it matters

- **Team configuration (CCAR-P-7.1).** A committed `.mcp.json` gives everyone the same integrations; managed MCP policy keeps them to an approved set.
- **Capability bloat (CCAR-P-3.1).** Every server adds tools and trust. Scopes, allow-lists and permission rules are how you keep that in check.
- **Integration choice (CCAR-P-3.7).** In Claude Code you can often choose between an MCP server and a CLI the agent runs through Bash; see [MCP versus alternatives](../08-model-context-protocol/06-mcp-vs-alternatives.md).
- **Context (CCAR-P-3.8).** Claude Code defers MCP tool definitions and discovers them with tool search, so many servers cost little context.

## How it works

### Adding servers

```bash
# Remote server over Streamable HTTP (Claude Code falls back to SSE if needed on recent versions)
claude mcp add --transport http notion https://mcp.notion.com/mcp

# With a static header (prefer OAuth where the server supports it)
claude mcp add --transport http internal-api https://mcp.internal.example.com/mcp \
  --header "Authorization: Bearer ${INTERNAL_MCP_TOKEN}"

# Local stdio server. Options come before the name; everything after -- is the launch command.
claude mcp add --transport stdio --env ASSETS_LOG_LEVEL=WARNING assets -- uvx contoso-assets-mcp==1.4.2

# From a JSON definition (also the way to add WebSocket servers: "type": "ws")
claude mcp add-json reports '{"type":"http","url":"https://mcp.reports.example.com/mcp"}'

# Import servers you already configured in Claude Desktop
claude mcp add-from-claude-desktop
```

Manage them:

```bash
claude mcp list            # health status of each server (Connected, Needs authentication, Failed to connect, Pending approval)
claude mcp get notion      # details, including the reason for a failure
claude mcp remove notion
claude mcp reset-project-choices   # reset your approvals of .mcp.json servers
```

Inside a session, `/mcp` shows servers and tools, signs in to OAuth-protected servers, reconnects, and enables or disables servers for the current project.

### Scopes and where configuration lives

| Scope | Flag | Loads in | Shared with team | Stored in |
|---|---|---|---|---|
| Local (default) | `--scope local` | Current project only | No | `~/.claude.json`, under the project's path |
| Project | `--scope project` | Current project | **Yes**, via version control | `.mcp.json` at the project root |
| User | `--scope user` | All your projects | No | `~/.claude.json` |

When the same server name is defined in several places, Claude Code uses one definition with this precedence: local, then project, then user, then plugin-provided servers, then claude.ai connectors. Entries are not merged field by field.

> **Note:** MCP "local scope" lives in `~/.claude.json`, which is different from the general `.claude/settings.local.json` file.

### A shared `.mcp.json`

```json
{
  "mcpServers": {
    "tickets": {
      "type": "http",
      "url": "${TICKETS_MCP_URL:-https://mcp.tickets.example.com/mcp}"
    },
    "assets": {
      "type": "stdio",
      "command": "uvx",
      "args": ["contoso-assets-mcp==1.4.2"],
      "env": { "ASSETS_API_TOKEN": "${ASSETS_API_TOKEN}" }
    }
  }
}
```

Claude Code expands `${VAR}` and `${VAR:-default}` in `command`, `args`, `env`, `url` and `headers`, so the committed file carries **no secrets**: each developer supplies tokens through environment variables or OAuth.

In interactive sessions, Claude Code **asks each developer to approve** project-scoped servers from `.mcp.json` before using them; a cloned repository cannot approve its own servers through its committed settings until the folder is trusted. In `claude -p`, Agent SDK and some cloud sessions there is no prompt and project servers load without asking ([page 9](09-headless-ci-and-agent-sdk.md) explains how to prevent that).

### Authentication

For OAuth-protected remote servers, add the server and then run `/mcp` to sign in through the browser. Claude Code supports pre-configured OAuth client credentials, a fixed callback port, scope restriction, and a `headersHelper` command that generates headers at connect time for custom schemes. Tokens are stored by Claude Code, not in `.mcp.json`.

### Using MCP tools, resources and prompts

- **Tools** appear as `mcp__<server>__<tool>`. Claude calls them like built-in tools, subject to permissions.
- **Resources**: type `@` to see resources from connected servers and reference them as `@server:protocol://path`, for example `@tickets:ticket://PAY-1042`.
- **Prompts** become commands: `/mcp__<server>__<prompt>` (listed as `/server:prompt (MCP)`), with arguments separated by spaces.
- **claude.ai connectors** you have enabled can also reach Claude Code; their tools appear as `mcp__claude_ai_<server>__<tool>`.

### Context: tool search and output limits

- **Tool search is on by default** (as of 2026-10-24): only tool names and server instructions load at session start; full definitions load when Claude needs them. Control it with the `ENABLE_TOOL_SEARCH` environment variable. Server authors should write good server instructions so Claude knows when to search for their tools.
- Claude Code warns when an MCP tool result exceeds **10,000 tokens**, and by default caps results at **25,000 tokens** (`MAX_MCP_OUTPUT_TOKENS`). Larger successful results are saved to a file Claude can read instead of flooding context.

### Permissions for MCP tools

Use the normal permission rules ([page 4](04-permissions-and-settings.md)):

```json
{
  "permissions": {
    "allow": ["mcp__tickets__tickets_search", "mcp__tickets__tickets_get"],
    "ask":   ["mcp__tickets__tickets_comment"],
    "deny":  ["mcp__tickets__tickets_delete"]
  }
}
```

`mcp__tickets__*` matches every tool from a server. Server authors can mark a tool with `_meta["anthropic/requiresUserInteraction"]: true` so Claude Code prompts on every call, even in auto and bypass modes. Subagents can be given their own `mcpServers` list so that only the subagent that needs a server can use it.

### Organisation controls (managed MCP)

| Pattern | Configure |
|---|---|
| Disable MCP entirely | `managed-mcp.json` with an empty `mcpServers` map |
| Fixed deployment: everyone gets the same servers and cannot add others | `managed-mcp.json` at `/Library/Application Support/ClaudeCode/` (macOS), `/etc/claude-code/` (Linux, WSL) or `C:\Program Files\ClaudeCode\` (Windows) |
| Provide servers to everyone, who can still add their own | `managedMcpServers` in managed settings |
| Approved catalogue: only listed servers may be added | `allowedMcpServers` plus `allowManagedMcpServersOnly: true` |
| Block known-bad servers | `deniedMcpServers` |

Allow-list and deny-list entries match by `serverUrl` (wildcards allowed), `serverCommand` (exact argument array) or `serverName`. Without `allowManagedMcpServersOnly`, allow-lists from user and project settings merge with the managed list, so users can broaden it; the deny-list always merges from every scope.

### Claude Code as an MCP server

`claude mcp serve` runs Claude Code itself as a stdio MCP server that other MCP clients (such as Claude Desktop) can connect to and use its tools.

## Example

A platform team's onboarding instructions for a repository:

```bash
# 1. Export your personal token (from the internal token portal); never commit it
export ASSETS_API_TOKEN=...   # placeholder: get your own token

# 2. Start Claude Code in the repo and approve the project's MCP servers when prompted
claude

# 3. In the session
/mcp                                   # sign in to "tickets" via OAuth
> Summarise @tickets:ticket://PAY-1042 and find the code paths it mentions
> /mcp__tickets__triage PAY-1042       # run the server's triage prompt
```

## Enterprise use case

*Adventure Works* (fictional) let engineers add MCP servers freely during a pilot and then audited usage: 41 distinct servers, several unpinned `npx -y` commands, and two community servers with broad OAuth scopes to the corporate document store.

For general availability, the team deployed **managed settings** with an approved catalogue (`allowedMcpServers` plus `allowManagedMcpServersOnly: true`), using URL patterns for vendor-hosted servers and exact, version-pinned commands for local ones. Common servers (tickets, documentation search) were delivered to everyone with `managedMcpServers`. Each repository's `.mcp.json` lists only what that codebase needs, with `${VAR}` placeholders for tokens. Permission rules deny destructive tools by default, and the security team's MCP review checklist from [Module 08](../08-model-context-protocol/05-mcp-security.md) gates catalogue additions.

## Common mistakes

- **Committing tokens in `.mcp.json`.** Use `${VAR}` expansion or OAuth.
- **Placing options after `--` in stdio adds.** Everything after `--` goes to the server command.
- **Putting `--env KEY=value` directly before the server name**, which the CLI reads as another pair; put another option between them.
- **Assuming `.mcp.json` is reviewed automatically.** Approval is per developer in interactive sessions, and absent in headless runs.
- **Loading many large servers without tool search** (or disabling it) and wondering why context fills quickly.
- **Unpinned package commands** (`npx -y some-server`).
- **Relying on a soft allow-list** (without `allowManagedMcpServersOnly`) as an enforcement control.

## Security considerations

- Every MCP server is third-party code or a third-party service with access to your session's data. Apply the provenance checks in [MCP security](../08-model-context-protocol/05-mcp-security.md).
- Local stdio servers and their environment variables run **outside the Bash sandbox** with your user permissions.
- Use permission rules to deny destructive MCP tools and require confirmation for external effects.
- In CI, use `--strict-mcp-config` with an explicit `--mcp-config`, or `--bare`, so repositories cannot add servers to automated runs.

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| `claude mcp list` shows `Needs authentication` | OAuth sign-in not done | `/mcp` → authenticate |
| `Pending approval` for a `.mcp.json` server | Not approved yet, or folder not trusted | Run `claude` interactively, accept trust, approve |
| `Failed to connect` (stdio) | Wrong command path, missing runtime, or server printing to stdout | `claude mcp get <name>` for details; run the command manually |
| Server blocked | Not on the managed allow-list | `/status` to see managed sources; request catalogue approval |
| Tool results truncated or saved to a file | Over the output limit | Paginate on the server, or raise `MAX_MCP_OUTPUT_TOKENS` deliberately |

More in [MCP troubleshooting](../24-troubleshooting/mcp.md).

## Check your understanding

1. Which scope shares a server with your team, and where is it stored?
2. How do you keep a team-shared server's token out of version control?
3. What permission rule allows every tool from a server named `tickets`?
4. Which managed settings create an authoritative approved catalogue of MCP servers?
5. How does Claude Code keep context small when many MCP servers are connected?

<details>
<summary>Answers</summary>

1. Project scope, stored in `.mcp.json` at the project root (committed to version control).
2. Use `${VAR}` (or `${VAR:-default}`) expansion in `.mcp.json` and have each developer provide the value in their environment, or use OAuth through `/mcp`.
3. `mcp__tickets__*` (or `mcp__tickets`) in `permissions.allow`.
4. `allowedMcpServers` together with `allowManagedMcpServersOnly: true` in a managed settings source.
5. Tool search is on by default: only tool names and server instructions load at start, and full definitions load on demand.

</details>

## Further reading

- [Connect Claude Code to tools via MCP](https://code.claude.com/docs/en/mcp) and [MCP quickstart](https://code.claude.com/docs/en/mcp-quickstart) (Claude Code Docs)
- [Managed MCP configuration](https://code.claude.com/docs/en/managed-mcp) (Claude Code Docs)
- [Module 08: Model Context Protocol](../08-model-context-protocol/README.md)
- Previous: [Hooks](06-hooks.md) · Next: [Team rollout](08-team-rollout.md)
