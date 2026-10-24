# Commands, Skills and Subagents

> **Level:** Intermediate · **Time:** ~50 min · **Exam relevance:** CCAR-P 7.2, 2.5, 3.1, 3.8, 1.4

## In plain English

Claude Code has three ways to package "how we do things here" so you do not have to type it every time:

- **Commands** start with `/`. Some are built in (`/clear`, `/model`, `/permissions`). Others are **Skills** you or your team write, such as `/release-notes` or `/review-migration`.
- **Skills** are folders with a `SKILL.md` file: instructions, and optionally scripts and reference files, that Claude loads only when they are relevant or when you invoke them. They are reusable know-how.
- **Subagents** are specialised helpers with their own context window, their own instructions and a restricted tool set. Claude hands them a task ("review this diff", "search the codebase for every use of the old API"), they work separately, and only their summary comes back.

Think of a skill as a laminated procedure card Claude pulls out when needed, and a subagent as a colleague Claude delegates a job to so that its own desk stays clear.

## Why it matters

- **Workflow improvement (CCAR-P-7.2).** Repeatable procedures become one command for the whole team.
- **Prompt reuse (CCAR-P-2.5).** Skills are modular, versioned prompts with progressive disclosure: only a short description sits in context until the skill is used.
- **Progressive discovery (CCAR-P-3.8).** Skills and subagents keep the main context lean, compared with stuffing everything into `CLAUDE.md`.
- **Capability control (CCAR-P-3.1).** Subagents can be given fewer tools than the main session; skills can pre-approve or remove tools for a turn.
- **Multi-agent design (CCAR-P-1.4).** Subagents are a concrete orchestrator-worker pattern.

## How it works

### Built-in commands and bundled skills

A selection of commands you will use (full list in the [commands reference](https://code.claude.com/docs/en/commands), as of 2026-10-24):

| Area | Commands |
|---|---|
| Session and context | `/clear`, `/compact`, `/context`, `/resume`, `/rewind`, `/branch`, `/export` |
| Configuration | `/config`, `/permissions`, `/model`, `/effort`, `/memory`, `/hooks`, `/mcp`, `/sandbox`, `/status`, `/statusline` |
| Extensions | `/skills`, `/agents`, `/plugin`, `/reload-skills` |
| Review and quality | `/diff`, `/code-review`, `/security-review`, `/simplify` |
| Help and diagnostics | `/help`, `/doctor`, `/usage`, `/debug` |
| Setup | `/init`, `/install-github-app`, `/login`, `/logout` |

Some of these (for example `/code-review`, `/simplify`, `/debug`, `/loop`, `/doctor`) are **bundled skills**: skills Anthropic ships with Claude Code that use the same mechanism as yours.

### Skills

**Commands and skills are now one mechanism.** Whether you write `.claude/commands/deploy.md` (the older style) or `.claude/skills/deploy/SKILL.md`, you get the same `/deploy` command. Old command files keep working; the skill format is the richer option, because it gives you a folder for helper files, control over who can invoke it, and loading on demand. Claude Code skills follow the open [Agent Skills](https://agentskills.io) standard, with Claude Code-specific extensions.

**Where skills live:**

| Location | Path | Loads in |
|---|---|---|
| Enterprise | `.claude/skills/<name>/SKILL.md` in the managed settings directory | All users where deployed |
| Personal | `~/.claude/skills/<name>/SKILL.md` | All your projects on this machine |
| Project | `.claude/skills/<name>/SKILL.md` | This repository (commit it for the team) |
| Plugin | `<plugin>/skills/<name>/SKILL.md` | Wherever the plugin is enabled, as `/plugin-name:skill-name` |

**How a skill loads:** by default, the skill's `description` (plus optional `when_to_use`, truncated together at 1,536 characters) sits in context so Claude knows it exists. The full body loads only when you type `/name` or Claude decides it is relevant. That is progressive disclosure: long reference material costs almost nothing until needed. Once invoked, the rendered skill stays in the conversation; after compaction Claude Code re-attaches recent skills within a token budget.

**Key frontmatter fields:**

| Field | Purpose |
|---|---|
| `name` | Command name (defaults to the directory name) |
| `description` | A summary plus the situations it is for; this text is how Claude judges whether to load the skill |
| `when_to_use` | Extra trigger phrases, appended to the description |
| `argument-hint`, `arguments` | Autocomplete hint and named arguments (`$name`); `$ARGUMENTS`, `$0`, `$1` also work |
| `disable-model-invocation: true` | Only you can invoke it (use for side effects like deploys); its description stays out of context |
| `user-invocable: false` | Only Claude can invoke it (background knowledge) |
| `allowed-tools` | Tools pre-approved for the turn that invokes the skill |
| `disallowed-tools` | Tools removed while the skill is active |
| `model`, `effort` | Override model or effort for that turn |
| `context: fork`, `agent` | Run the skill in a forked subagent |
| `paths` | Only auto-load when working with matching files |
| `hooks` | Hooks registered when the skill is invoked |

**Dynamic context injection:** a line such as `` !`git diff HEAD` `` in a skill runs the command and inlines its output before Claude reads the skill, so the instructions arrive with live data.

### Subagents

A subagent runs in **its own context window** with its own system prompt, tool set and (optionally) model and permission mode. Its tool calls stay out of your main conversation; Claude gets back a summary.

**Built-in subagents** (as of 2026-10-24) include **Explore** (fast, read-only codebase search; starts without your CLAUDE.md to stay cheap), **Plan** (research for plan mode) and **general-purpose** (exploration plus changes), plus helper agents such as `claude-code-guide`.

**Custom subagents** are Markdown files with YAML frontmatter:

| Location | Scope | Priority |
|---|---|---|
| Managed settings | Organisation | 1 (highest) |
| `--agents` CLI flag (JSON) | Current session | 2 |
| `.claude/agents/` | Current project | 3 |
| `~/.claude/agents/` | All your projects | 4 |
| Plugin `agents/` | Where the plugin is enabled | 5 |

Frequently used fields: `name` and `description` (required), `tools` (allow-list; inherits all if omitted), `disallowedTools`, `model` (`sonnet`, `opus`, `haiku`, `fable`, a full ID, or `inherit`), `permissionMode`, `maxTurns`, `skills` (preload), `mcpServers`, `hooks`, `memory` (`user`, `project` or `local` persistent memory), `isolation: worktree`, and `effort`.

Claude delegates **automatically** when a task matches a subagent's description, or **explicitly** when you ask ("use the security-reviewer agent on this branch"). Subagents Claude spawns from the main conversation start in the background by default. Control which subagents may run with permission rules such as `Agent(Explore)` in `deny`.

### Choosing the right extension

| You want to… | Use |
|---|---|
| Give facts and conventions to every session | `CLAUDE.md` / rules ([page 3](03-claude-md-and-memory.md)) |
| Package a repeatable procedure or reference that loads on demand | **Skill** |
| Trigger a workflow only when a human asks (deploy, release) | Skill with `disable-model-invocation: true` |
| Delegate a self-contained task and keep the main context clean, possibly with fewer tools or a cheaper model | **Subagent** |
| Guarantee something happens (or is blocked) every time | **Hook** ([page 6](06-hooks.md)) |
| Reach an external system | **MCP server** ([page 7](07-mcp-in-claude-code.md)) |
| Distribute skills, agents, hooks and MCP servers together | **Plugin** (through a marketplace) |

## Example

### A project skill: `.claude/skills/db-migration-review/SKILL.md`

```markdown
---
description: Reviews a database migration for safety before merge. Use when the user asks to review, check or approve a migration, or when a diff touches db/migrations/.
argument-hint: "[migration file]"
allowed-tools: Bash(git diff *) Bash(git log *)
---
## Migration under review
!`git diff --stat origin/main -- db/migrations/`

## Checklist
Review $ARGUMENTS (or every changed migration above) against these rules and report PASS or FAIL for each:
1. Adds columns as nullable or with a default; never adds NOT NULL without a default on a large table.
2. Creates indexes CONCURRENTLY.
3. No data backfill inside the schema migration; backfills go in a separate job.
4. Has a reversible down migration.
5. Does not rename or drop columns still read by the current release (search src/ for usages).

Finish with a one-line verdict: SAFE TO MERGE or NEEDS CHANGES.
```

Invoke with `/db-migration-review db/migrations/2026_10_20_add_loyalty.sql`, or let Claude load it when a diff touches migrations.

### A project subagent: `.claude/agents/security-reviewer.md`

```markdown
---
name: security-reviewer
description: Reviews code changes for security issues (injection, authz, secrets, unsafe deserialisation). Use proactively after changes to authentication, payments or input handling.
tools: Read, Grep, Glob, Bash
model: opus
permissionMode: plan
maxTurns: 25
---
You are a senior application security reviewer for a payments service.
Review only the diff against origin/main. For each finding give: file and line,
the vulnerability class, a concrete exploit scenario, and a minimal fix.
Do not edit files. If you find nothing, say so explicitly and list what you checked.
```

The `tools` list is an allow-list of tool names (it has no `Edit` or `Write`), so the subagent can read, search and run shell commands but cannot use the file-editing tools; plan mode and your Bash permission rules still govern which commands run, and it is capped at 25 turns. Its long investigation stays out of the main session.

## Enterprise use case

*Fabrikam Software* (fictional) noticed that its root `CLAUDE.md` had become a 600-line mix of conventions, a release procedure, a migration checklist and an incident runbook. Engineers complained that Claude followed some sections and ignored others.

The platform team moved each procedure into a project skill (`/release`, `/db-migration-review`, `/incident-timeline`), marking `/release` with `disable-model-invocation: true` so it only runs when a release manager types it. They added two subagents: `security-reviewer` (read-only, Opus, plan mode) and `test-writer` (can edit only under `tests/`, enforced with a hook). They then packaged the skills, agents and hooks as an internal plugin distributed through a managed marketplace, so every repository could opt in with one setting. `CLAUDE.md` shrank to 120 lines, and `/skill-doctor` reports showed which skills were actually used, which guided pruning.

## Common mistakes

- **Vague skill descriptions** ("helps with databases") so Claude never loads them, or loads them too often.
- **Long procedures in `CLAUDE.md`** instead of skills, costing context in every session.
- **Side-effecting skills Claude can invoke on its own.** Use `disable-model-invocation: true` for deploys and releases.
- **Over-broad `allowed-tools`** in skills; the grant applies to that turn without prompts.
- **Subagents with every tool** when they only need to read.
- **Expecting subagents to share the main conversation's context.** They start fresh (unless forked) and return only a summary; give them a complete task description.
- **Too many overlapping subagents**, so Claude cannot tell which to use.

## Security considerations

- Skills and subagents in a repository are **prompt content and configuration from that repository**. Review changes to `.claude/skills/` and `.claude/agents/` like code.
- A skill's `allowed-tools` grant applies regardless of workspace trust (as of 2026-10-24), so treat skills from untrusted repositories with care.
- Give subagents least privilege: restricted `tools`, `permissionMode: plan` for reviewers, `maxTurns` caps.
- Plugins bundle hooks and MCP servers that run code; restrict marketplaces with managed settings ([page 8](08-team-rollout.md)).

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| Skill never triggers automatically | Description lacks trigger conditions, or `disable-model-invocation` is set | Rewrite the description with when-to-use phrases; check frontmatter |
| Skill triggers too often | Description too broad | Narrow it; add `paths` |
| New skill not listed | Directory created mid-session | `/reload-skills` or restart |
| Subagent not found | `agents` directory created after the session started | Restart Claude Code |
| Subagent lacks information | It started with a fresh context | Put full context in the delegation prompt, or preload skills |

## Check your understanding

1. What is the practical difference between a skill and a `CLAUDE.md` section?
2. How do you make sure only a human can trigger `/deploy`?
3. Why might you give a subagent a cheaper model and fewer tools than the main session?
4. Where would you put a subagent that every engineer in the company should have, and what has the highest priority if two definitions share a name?

<details>
<summary>Answers</summary>

1. A `CLAUDE.md` section loads in every session; a skill's body loads only when invoked or judged relevant (only its description is in context), so skills suit procedures and long reference material.
2. Set `disable-model-invocation: true` in the skill's frontmatter.
3. Cost and safety: exploration or review tasks rarely need the most capable model or write access, and fewer tools reduce the blast radius if the subagent is misled.
4. Deploy it through managed settings (or a plugin from a managed marketplace). Managed definitions have the highest priority, followed by `--agents`, project `.claude/agents/`, user `~/.claude/agents/`, then plugins.

</details>

## Further reading

- [Extend Claude with skills](https://code.claude.com/docs/en/skills) (Claude Code Docs)
- [Subagents](https://code.claude.com/docs/en/sub-agents) (Claude Code Docs)
- [Commands reference](https://code.claude.com/docs/en/commands) (Claude Code Docs)
- [Plugins overview](https://code.claude.com/docs/en/plugins/overview) (Claude Code Docs)
- [Progressive disclosure and Skills](../04-context-engineering/06-progressive-disclosure-and-skills.md) in Module 04

<!-- page-nav:start -->
---

[← Previous: Permissions and Settings](04-permissions-and-settings.md) · [Module overview](README.md) · [Next: Hooks →](06-hooks.md)
<!-- page-nav:end -->
