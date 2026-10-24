# Module 09: Claude Code

> **Level:** Beginner to Advanced · **Time:** ~6 hours including the lab · **Exam relevance:** CCAR-P 7.1, 7.2, 7.3, 2.5, 3.1, 5.1

Claude Code is Anthropic's agentic coding tool. It reads your codebase, edits files, runs commands and works with your existing developer tools, from a terminal, IDE, desktop app, browser or CI pipeline. For individual developers it is a productivity tool. For architects and platform teams it is something to **configure, secure and roll out**: which files it may touch, which commands it may run, which MCP servers it may reach, how its costs are tracked, and how it behaves in automation.

This module goes from first install to a governed team rollout. Every command, file path and setting name was checked against [code.claude.com/docs](https://code.claude.com/docs) on 2026-10-24. Claude Code changes quickly (new versions ship frequently), so re-check the documentation for anything you plan to enforce.

## Learning objectives

By the end of this module you can:

1. Explain what Claude Code is, where it runs, and how its agent loop and built-in tools work.
2. Install Claude Code, authenticate, and run a productive first session.
3. Write effective `CLAUDE.md` files and rules, and explain the memory hierarchy, imports and auto memory.
4. Configure settings files and precedence, permission modes, allow/ask/deny rules, sandboxing and managed (enterprise) settings.
5. Extend Claude Code with Skills (including custom slash commands) and subagents, and choose between them.
6. Automate and enforce behaviour with hooks.
7. Connect MCP servers in Claude Code and control them centrally.
8. Plan a team rollout: shared configuration, cost and usage visibility, and security guardrails (CCAR-P-7.1 to 7.3).
9. Run Claude Code headlessly in scripts and CI, and know when to use the Claude Agent SDK instead.

## Pages in this module

| # | Page | What you learn |
|---|---|---|
| 1 | [What is Claude Code?](01-what-is-claude-code.md) | Surfaces, agent loop, tools, models and authentication options |
| 2 | [Setup and first session](02-setup-and-first-session.md) | Install, sign in, `/init`, plan mode, checkpoints, everyday commands |
| 3 | [CLAUDE.md and memory](03-claude-md-and-memory.md) | Memory locations and load order, imports, rules, auto memory |
| 4 | [Permissions and settings](04-permissions-and-settings.md) | Settings precedence, permission modes and rules, sandboxing, managed settings |
| 5 | [Commands, Skills and subagents](05-commands-skills-subagents.md) | Built-in commands, Skills and custom commands, subagents |
| 6 | [Hooks](06-hooks.md) | Lifecycle events, matchers, exit codes, JSON decisions, security |
| 7 | [MCP in Claude Code](07-mcp-in-claude-code.md) | `claude mcp` commands, scopes, `.mcp.json`, tool search, managed MCP |
| 8 | [Team rollout](08-team-rollout.md) | Shared settings, managed policy, costs, analytics, telemetry, guardrails |
| 9 | [Headless, CI and the Agent SDK](09-headless-ci-and-agent-sdk.md) | `claude -p`, structured output, GitHub Actions, Agent SDK |

## Hands-on lab

- [Lab 10: Claude Code workflows](../19-hands-on-labs/lab-10-claude-code-workflows/README.md) practises project configuration, permission rules, a hook and a skill. Its scripted parts run in mock mode by default (`CLAUDE_LAB_MODE=mock`).

> **Cost:** using Claude Code consumes your Claude plan usage or API credits (live mode).

## Prerequisites

- Comfortable with a terminal and git.
- [Module 07: Tool use](../07-tool-use-and-function-calling/README.md) (Claude Code is a tool-using agent) and [Module 08: MCP](../08-model-context-protocol/README.md).
- Helpful: [Module 04: Context engineering](../04-context-engineering/README.md), especially [memory](../04-context-engineering/04-memory-and-persistence.md) and [Skills](../04-context-engineering/06-progressive-disclosure-and-skills.md).

## Exam relevance

Objective IDs come from [`registry.yaml`](../16-certification-tracks/registry.yaml).

| Objective | Where this module helps |
|---|---|
| CCAR-P-7.1 Configure Claude tools and environments for teams | Pages 3, 4, 7 and 8 |
| CCAR-P-7.2 Improve developer workflows with AI-assisted tooling | Pages 2, 5, 6 and 9 |
| CCAR-P-7.3 Support debugging and operational issue resolution | Pages 2, 6, 8 and 9 (troubleshooting, `/doctor`, telemetry, CI) |
| CCAR-P-2.5 Reuse prompts via caching, modular prompts and Skills | Pages 3 and 5 |
| CCAR-P-3.1 Evaluate tool and agent configuration for capability bloat | Pages 4, 5 and 7 |
| CCAR-P-5.1 Implement guardrails and safety controls | Pages 4, 6 and 8 |

See the [CCAR-P domain 7 study guide](../16-certification-tracks/ccar-p/study-guide/domain-7.md) for the domain view.

## Key facts to remember (as of 2026-10-24)

- Project memory lives in `./CLAUDE.md` or `./.claude/CLAUDE.md`; personal project notes in `./CLAUDE.local.md`; user memory in `~/.claude/CLAUDE.md`.
- Settings precedence, highest first: **managed**, **command line**, **project local** (`.claude/settings.local.json`), **shared project** (`.claude/settings.json`), **user** (`~/.claude/settings.json`).
- Permission rules are evaluated **deny, then ask, then allow**; a deny anywhere cannot be overridden by an allow elsewhere.
- Custom commands have been merged into **Skills**: `.claude/commands/x.md` and `.claude/skills/x/SKILL.md` both create `/x`.
- `claude -p` runs non-interactively; it does not show the workspace trust dialog, so it uses project hooks and `.mcp.json` servers unless you pass `--bare` or restrict setting sources.

## Next module

Continue to [Module 10: Agentic AI](../10-agentic-ai/README.md), which generalises the agent patterns you have just used in Claude Code.
