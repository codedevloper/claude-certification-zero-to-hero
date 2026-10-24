# CLAUDE.md and Memory

> **Level:** Intermediate · **Time:** ~40 min · **Exam relevance:** CCAR-P 7.1, 2.2, 2.5

## In plain English

Every Claude Code session starts with an empty context window. Without help, Claude would rediscover your build commands, conventions and quirks every time. **CLAUDE.md** files fix that: they are plain Markdown files that Claude Code loads at the start of each session, like a project handbook placed on a new colleague's desk every morning.

There are two kinds of memory:

- **CLAUDE.md files** (and rule files) that **you** write: instructions and facts for every session.
- **Auto memory** that **Claude** writes for itself: notes on your preferences, corrections and project context that it judges useful later.

Both are *context*, not enforcement. They shape what Claude does; they do not stop it doing something. Enforcement belongs in settings and hooks ([pages 4](04-permissions-and-settings.md) and [6](06-hooks.md)).

## Why it matters

- **Consistency across a team (CCAR-P-7.1).** A committed `CLAUDE.md` gives every developer's sessions the same conventions.
- **Prompt reuse (CCAR-P-2.5).** Memory files and rules are modular, reusable prompt components; Skills extend the idea with on-demand loading.
- **Guardrail design (CCAR-P-2.2).** Knowing the difference between guidance (CLAUDE.md) and enforcement (permission rules, hooks) is a frequent exam theme.
- **Context budget.** Everything in memory consumes context in every session. Bloated files reduce adherence.

## How it works

### Where CLAUDE.md files live

Listed from broadest to most specific; content loads in this order, so more specific instructions appear later in context (as of 2026-10-24):

| Scope | Location | Purpose | Shared with |
|---|---|---|---|
| Managed policy | macOS `/Library/Application Support/ClaudeCode/CLAUDE.md`; Linux and WSL `/etc/claude-code/CLAUDE.md`; Windows `C:\Program Files\ClaudeCode\CLAUDE.md` | Organisation-wide guidance deployed by IT | Everyone on the machine |
| User | `~/.claude/CLAUDE.md` | Your personal preferences in every project | Only you |
| Project | `./CLAUDE.md` or `./.claude/CLAUDE.md` | Team conventions, build and test commands, architecture | The team, through version control |
| Local | `./CLAUDE.local.md` (add to `.gitignore`) | Your personal notes for this project | Only you |

Organisations can also put managed CLAUDE.md content directly in managed settings with the `claudeMd` key.

### How files load

- Claude Code loads `CLAUDE.md` and `CLAUDE.local.md` from the working directory **and every directory above it** at launch. They are **concatenated**, not overridden, ordered from the filesystem root down; within a directory, `CLAUDE.local.md` comes after `CLAUDE.md`.
- `CLAUDE.md` files in **subdirectories** load on demand, when Claude reads or edits files there.
- Run `/context` (Memory files section) to see what loaded.
- Block-level HTML comments (`<!-- note for maintainers -->`) are stripped before injection, so you can leave notes for humans at no token cost.
- In monorepos, `claudeMdExcludes` (for example in `.claude/settings.local.json`) skips other teams' files; it cannot exclude a managed CLAUDE.md.
- If a repository has `AGENTS.md` for other coding agents, Claude Code can read it; see the memory documentation for exactly when.

### Imports

A CLAUDE.md file can pull in other files with `@path` syntax:

```markdown
See @README.md for an overview and @package.json for npm scripts.

# Workflow
- Git conventions: @docs/git-instructions.md
- My personal preferences: @~/.claude/my-project-instructions.md
```

Relative paths resolve relative to the importing file; imports can nest up to four hops. Imports organise content but **do not** reduce context cost: imported files load with the file that imports them. The first time a project file imports something **outside** the working directory, Claude Code asks you to approve it, protecting you from files other people commit. Wrap a path in backticks to mention it without importing it.

### Rules: `.claude/rules/`

For larger projects, split instructions into topic files under `.claude/rules/` (discovered recursively). A rule without frontmatter loads at launch like `.claude/CLAUDE.md`. A rule with a `paths` field loads only when Claude works with matching files:

```markdown
---
paths:
  - "src/api/**/*.ts"
---
# API rules
- Every handler validates input with the shared zod schemas in src/api/schemas.
- Errors use the ProblemDetails format in src/api/errors.ts.
```

User-level rules live in `~/.claude/rules/`.

### What to put in CLAUDE.md, and what not to

| Put in CLAUDE.md | Put elsewhere |
|---|---|
| Build, test and lint commands | Multi-step procedures used occasionally → a **Skill** ([page 5](05-commands-skills-subagents.md)) |
| Conventions Claude cannot infer ("use pnpm, not npm") | Instructions for one part of the codebase → a **path-scoped rule** |
| Architecture facts and where things live | Hard prohibitions ("never read `.env`") → **permission deny rules** |
| "Always do X" rules that apply everywhere | Actions that must happen every time ("format after edit") → **hooks** |
| Pointers to key docs (with imports, sparingly) | Secrets and credentials → never in memory files |

Anthropic's guidance (as of 2026-10-24): keep each CLAUDE.md under about **200 lines**; write concrete, verifiable instructions ("use 2-space indentation", not "format code properly"); use headings and bullets; and remove contradictions, because Claude may pick one of two conflicting instructions arbitrarily. Add to CLAUDE.md when Claude makes the same mistake twice, a review catches something it should have known, or you repeat the same correction. `/doctor prompt-audit` can review your instruction files for outdated or conflicting content.

### Auto memory

Auto memory lets Claude save notes for itself as it works (on by default in local sessions):

- Stored per project at `~/.claude/projects/<project>/memory/`, shared across worktrees of the same git repository, and **machine-local**.
- `MEMORY.md` is an index; the first **200 lines or 25 KB** (whichever comes first) load at the start of every session. Topic files (for example `feedback_testing.md`) are read on demand.
- Notes are typed as `user`, `feedback`, `project` or `reference`. Claude skips what it can derive from the code or what CLAUDE.md already says.
- Toggle it in `/memory` (saves `autoMemoryEnabled`), set `"autoMemoryEnabled": false` in project settings, or set `CLAUDE_CODE_DISABLE_AUTO_MEMORY=1`. Change the location with `autoMemoryDirectory`.
- "Remember to use pnpm" goes to auto memory; "add this to CLAUDE.md" goes to CLAUDE.md.

### Viewing and editing

`/memory` lists every memory file location, opens files in your editor (creating them if needed), and toggles auto memory. `/context` shows what actually loaded.

## Example

A compact, effective project `CLAUDE.md` for a fictional service:

```markdown
# Acme Checkout Service

## Commands
- Install: `pnpm install` (never npm or yarn)
- Test all: `pnpm test`; one file: `pnpm test -- src/payments/card.test.ts`
- Lint and types: `pnpm lint && pnpm typecheck` (run before every commit)

## Architecture
- HTTP handlers: `src/api/handlers/`; business logic: `src/domain/`; no DB calls in handlers.
- Payment providers live in `src/payments/providers/`, one file per provider, all implementing `PaymentProvider`.
- Money is integer pence (`amountPence`); never use floats for money.

## Conventions
- New code is TypeScript strict; no `any` without a `// reason:` comment.
- Tests sit next to the code as `*.test.ts`; use the factories in `test/factories/`.
- Commit messages follow Conventional Commits.

## Gotchas
- Integration tests need Redis: `docker compose up redis` first.
- `src/legacy/` is frozen; do not refactor it, add adapters instead.

<!-- Maintainers: keep this under 200 lines. Move procedures into .claude/skills/. -->
```

Paired with `.claude/rules/api.md` (path-scoped to `src/api/**`) and a deny rule for `.env` files in `.claude/settings.json`.

## Enterprise use case

*Tailspin Toys* (fictional) had three problems after rolling out Claude Code: root `CLAUDE.md` files had grown past 800 lines, teams in the monorepo were picking up each other's instructions, and a "never commit secrets" line in CLAUDE.md had not prevented a `.env` file being read into context.

The platform team restructured: a managed CLAUDE.md with ten lines of company-wide guidance (data handling reminders, where the engineering handbook lives); a root project file under 150 lines; per-team instructions moved into path-scoped rules; long procedures (release process, incident runbook) moved into Skills; and `claudeMdExcludes` documented for engineers who work in one corner of the monorepo. The `.env` problem was solved where it belongs, with a managed deny rule `Read(./.env*)` and a sandbox `denyRead` entry, not with more CLAUDE.md text.

## Common mistakes

- **Using CLAUDE.md as a security control.** It is guidance; use permission rules and hooks for enforcement.
- **Giant files.** Long files cost context every session and reduce adherence; aim for under 200 lines each.
- **Vague instructions** ("write good tests") that cannot be verified.
- **Contradictions** between root, nested and rule files.
- **Committing `CLAUDE.local.md`** or personal preferences in the project file.
- **Expecting imports to save tokens.** They organise, they do not compress.
- **Relying on early conversation instructions** after compaction; put persistent rules in CLAUDE.md.

## Security considerations

- Memory files are **prompt content from the repository**. A malicious contributor could add misleading instructions; review CLAUDE.md and rules changes in code review like any other code.
- External imports in project files require your approval the first time; decline imports you do not recognise.
- Never store secrets, tokens or personal data in memory files; auto memory files are plain text under `~/.claude/`.
- Managed CLAUDE.md is good for compliance reminders, but technical controls (deny rules, sandbox, managed MCP policy) must back it up.

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| Claude ignores a rule | File not loaded, too long, or contradicted | `/context` to confirm loading; shorten; remove conflicts; make it concrete |
| A nested CLAUDE.md seems ignored | Subdirectory files load only when Claude works in that directory | Ask Claude to work there, or move the rule to the root or a path-scoped rule |
| Other teams' instructions appear | Ancestor files in a monorepo | `claudeMdExcludes` |
| Instructions lost after `/compact` | They were only in the conversation | Put them in CLAUDE.md; add compact instructions |
| Unsure what auto memory saved | Notes are written silently | `/memory` → open the auto memory folder |

## Check your understanding

1. In what order do user, project and local CLAUDE.md files appear in context, and do later files override earlier ones?
2. A team wants Claude to "never run database migrations against production". Where should this live?
3. What is the difference between `CLAUDE.md` and auto memory?
4. When should a section of CLAUDE.md become a Skill or a path-scoped rule?

<details>
<summary>Answers</summary>

1. Managed, then user, then project (from the filesystem root down to the working directory), with `CLAUDE.local.md` after `CLAUDE.md` at each level. Files are concatenated, not overridden; later instructions are simply read later.
2. Enforce it with permission deny rules (and/or a PreToolUse hook) for the migration command and production credentials; a CLAUDE.md line can explain the policy but is not enforcement.
3. You write CLAUDE.md as instructions for every session; Claude writes auto memory notes for itself (preferences, corrections, project context), with only the `MEMORY.md` index loaded at start.
4. When it is a multi-step procedure needed only sometimes (Skill), or when it applies only to certain files or directories (path-scoped rule).

</details>

## Further reading

- [How Claude remembers your project](https://code.claude.com/docs/en/memory) (Claude Code Docs)
- [Best practices](https://code.claude.com/docs/en/best-practices) (Claude Code Docs)
- [Memory and persistence](../04-context-engineering/04-memory-and-persistence.md) in Module 04
- Previous: [Setup and first session](02-setup-and-first-session.md) · Next: [Permissions and settings](04-permissions-and-settings.md)
