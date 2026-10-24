# CCAR-F Domain 3 — Claude Code Configuration & Workflows (20%)

> **Track:** [CCAR-F](../README.md) · **Weight:** 20% (see [`registry.yaml`](../../registry.yaml)) ·
> **Objectives:** CCAR-F-3.1 to 3.6 · **Time:** ~7 hours including labs

This domain is about making Claude Code behave consistently for a whole team: instructions in the right files,
conventions that load only when relevant, reusable commands and skills, the judgement to plan before editing,
iterative techniques that converge quickly, and non-interactive runs in CI. It is a primary domain in the
code-generation, CI and developer-productivity [scenarios](../scenarios.md).

Claude Code facts were checked against [code.claude.com/docs](https://code.claude.com/docs) (memory, skills,
permission modes, CLI reference, headless) on **2026-10-24**. Claude Code ships frequently; confirm details
before relying on them.

## Objectives

| ID | Objective | Where to study |
|---|---|---|
| CCAR-F-3.1 | Organise CLAUDE.md files by hierarchy, scope and module | [CLAUDE.md and memory](../../../09-claude-code/03-claude-md-and-memory.md), [Team rollout](../../../09-claude-code/08-team-rollout.md) |
| CCAR-F-3.2 | Create and configure custom slash commands and skills | [Commands, skills and subagents](../../../09-claude-code/05-commands-skills-subagents.md), [Progressive disclosure and Skills](../../../04-context-engineering/06-progressive-disclosure-and-skills.md) |
| CCAR-F-3.3 | Use path-specific rules to load conventions conditionally | [CLAUDE.md and memory](../../../09-claude-code/03-claude-md-and-memory.md) |
| CCAR-F-3.4 | Decide between plan mode and direct execution | [Setup and first session](../../../09-claude-code/02-setup-and-first-session.md), [Commands, skills and subagents](../../../09-claude-code/05-commands-skills-subagents.md) |
| CCAR-F-3.5 | Refine work iteratively for progressive improvement | [Iterating on prompts](../../../03-prompt-engineering/08-iterating-on-prompts.md), [Few-shot examples](../../../03-prompt-engineering/03-examples-few-shot.md) |
| CCAR-F-3.6 | Integrate Claude Code into CI/CD pipelines | [Headless, CI and the Agent SDK](../../../09-claude-code/09-headless-ci-and-agent-sdk.md) |

## Key concepts

- **CLAUDE.md.** Markdown instructions Claude Code loads into context. It is guidance, not enforcement: to block an
  action whatever Claude decides, use permission rules or a `PreToolUse` hook.
- **Rules.** Topic files in `.claude/rules/`. Without `paths` frontmatter they load at launch; with it they load
  only when Claude works on matching files.
- **Skill.** A folder with a `SKILL.md` (frontmatter plus instructions) that Claude loads on demand or you invoke as
  `/name`. Custom commands (`.claude/commands/*.md`) are now part of the same system.
- **Plan mode.** A permission mode in which Claude researches and proposes a plan but cannot edit source files until
  you approve.
- **Headless mode.** `claude -p` (print mode) runs one non-interactive task and exits; the basis for CI.

## Detailed technical notes

### 3.1 CLAUDE.md hierarchy, scope and modular organisation

| Scope | Location | Shared with | Use for |
|---|---|---|---|
| Managed policy | OS-specific path set by IT (for example `/etc/claude-code/CLAUDE.md` on Linux) | Everyone in the organisation | Mandatory company standards |
| User | `~/.claude/CLAUDE.md` | Only you, all projects | Personal preferences |
| Project | `./CLAUDE.md` or `./.claude/CLAUDE.md` | The team, through git | Architecture, commands, conventions |
| Local | `./CLAUDE.local.md` (add to `.gitignore`) | Only you, this project | Your sandbox URLs, test accounts |
| Subdirectory | `<dir>/CLAUDE.md` | The team | Conventions for one package |

How they load:

- Files in the working directory and every directory **above** it load at launch and are **concatenated**, from
  the filesystem root down. Nothing overrides anything; if two instructions conflict, Claude may follow either.
- `CLAUDE.md` files in **subdirectories** load on demand, when Claude reads or edits a file there.
- `@path/to/file` imports another file into a CLAUDE.md. Relative paths resolve from the importing file;
  imports can nest up to four hops. External imports ask for approval once per project.
- After `/compact`, the project-root CLAUDE.md is re-read from disk; nested files and path-scoped rules reload
  when they next match.
- `/memory` lists the memory files in use and opens them for editing; `/context` shows what loaded at launch.

**Classic diagnosis.** "A new teammate's Claude Code ignores our conventions." The conventions are in someone's
`~/.claude/CLAUDE.md`, which is personal and never committed. Move them to the project CLAUDE.md or
`.claude/rules/`.

**Modular organisation.** A 900-line CLAUDE.md is hard to maintain and costs context in every session. Split it:

```text
CLAUDE.md                     # short: project purpose, build/test commands, pointers
.claude/rules/
  testing.md                  # paths: tests and spec files
  api-conventions.md          # paths: src/api/**
  migrations.md               # paths: db/migrations/**
packages/payments/CLAUDE.md   # @imports ../../docs/standards/pci-handling.md
```

Use `@import` in a package's CLAUDE.md to pull in only the standards that package's maintainers know it needs.

### 3.2 Custom slash commands and skills

| Location | Scope |
|---|---|
| `.claude/skills/<name>/SKILL.md` | Project: shared through git |
| `~/.claude/skills/<name>/SKILL.md` | Personal: all your projects |
| `.claude/commands/<name>.md` / `~/.claude/commands/<name>.md` | Older command format; still works and accepts the same frontmatter (except `name` and `paths`) |

Commands have been merged into skills: `.claude/commands/review.md` and `.claude/skills/review/SKILL.md` both
create `/review`, and if both exist the skill wins. For the same name, an enterprise skill overrides a personal
one, and a personal one overrides a project one. To customise a team skill for yourself without affecting
teammates, create a personal skill with a **different name**.

Frontmatter fields the exam names, with their current meaning (as of 2026-10-24):

| Field | Effect |
|---|---|
| `description` | What it does and when to use it; Claude uses it to decide when to load the skill |
| `argument-hint` | Autocomplete hint shown when invoking, for example `[ticket-id] [environment]` |
| `context: fork` | Run the skill as a subagent with a clean context; only its result returns to the conversation |
| `agent` | Which subagent type runs a forked skill (`Explore`, `Plan`, `general-purpose` or a custom agent) |
| `allowed-tools` | Tools **pre-approved** (no prompt) during the invoking turn. It does **not** remove other tools |
| `disallowed-tools` | Tools **removed** while the skill is active: the way to restrict |
| `disable-model-invocation: true` | Only a person can invoke it with `/name` |
| `paths` | Glob patterns limiting when Claude auto-loads the skill |

> **Exam-guide nuance.** The v1.0 guide describes `allowed-tools` as restricting tool access during a skill. The
> current documentation says it pre-approves listed tools and leaves the rest available under normal
> permissions; restriction comes from `disallowed-tools` (or permission deny rules). Understand both readings.

Forked skills now run in the background by default; set `background: false` when the conversation must wait for
the result. Use `context: fork` for skills that produce a lot of output (a codebase survey) or exploratory
material (brainstorming alternatives) you do not want filling the main conversation.

```markdown
---
name: dependency-survey
description: Survey third-party dependencies in a service and report outdated or risky ones. Use when asked to audit dependencies.
argument-hint: "[service-directory]"
context: fork
agent: Explore
disallowed-tools: Write, Edit
---
Survey the dependencies declared under $ARGUMENTS. For each, report name, pinned version, latest known
version if visible in the lockfile metadata, and any licence or maintenance concern. Return a table only.
```

**Skill or CLAUDE.md?** CLAUDE.md is for standards that apply to almost every session; it is always loaded. A
skill is for a task-specific procedure that should load only when needed.

### 3.3 Path-specific rules

```markdown
---
paths:
  - "infra/terraform/**/*.tf"
  - "infra/modules/**/*.tf"
---
# Terraform conventions
- Every resource carries the `owner` and `cost_centre` tags.
- No inline IAM policies; use the shared policy modules.
```

- A rule with `paths` loads when Claude reads, writes or edits a matching file (including a single-file read
  through Bash, such as `cat`). Rules without `paths` load at launch like project CLAUDE.md.
- Patterns are globs relative to the folder that contains `.claude`; brace expansion works
  (`src/**/*.{ts,tsx}`).
- **Rules versus subdirectory CLAUDE.md:** a subdirectory CLAUDE.md covers one directory tree. A glob rule covers
  files by type wherever they live, for example `**/*.test.ts` across forty packages. Choose rules when the
  convention follows the file type, not the folder.
- Personal rules can live in `~/.claude/rules/`.

### 3.4 Plan mode versus direct execution

| Choose plan mode when | Choose direct execution when |
|---|---|
| The change spans many files or services | The change is small, local and well understood |
| There are several valid approaches with different trade-offs | There is one obvious fix (clear stack trace, single function) |
| The decision has architectural or infrastructure consequences | Rework would be cheap if the first attempt is wrong |
| You are new to the codebase and need exploration first | You already know exactly what to change |

Enter plan mode with Shift+Tab, `claude --permission-mode plan`, or a `/plan` prefix on one prompt. In plan mode
Claude can read and explore but cannot edit source files; when the plan is ready you approve it (and choose how
edits are approved), edit it, or keep planning. A common pattern is **plan, then execute**: plan a migration in
plan mode, review and adjust the plan, then let Claude implement it directly.

The built-in **Explore** subagent is read-only and is designed for search-heavy discovery. Delegating discovery
to it keeps the verbose output (dozens of file reads) out of the main conversation, which receives only a
summary. The **Plan** subagent does research during plan mode.

### 3.5 Iterative refinement

| Technique | Use when | How |
|---|---|---|
| Concrete input/output examples | Prose descriptions of a transformation keep being misread | Give two or three before/after pairs, including an edge case |
| Test-driven iteration | Behaviour can be specified as tests | Write tests (normal, edge, performance) first; ask Claude to make them pass; feed failures back |
| Interview pattern | The domain is unfamiliar or requirements are fuzzy | Ask Claude to question you about constraints (failure modes, caching, data volumes) before it writes code |
| One combined message | Several problems interact (fixing one changes another) | Describe all of them together so the fix is coherent |
| Sequential fixes | Problems are independent | Fix and verify one at a time; smaller diffs are easier to review |

Specific beats general: "the migration fails when `middle_name` is null; expected output for row 3 is ..." fixes
the bug faster than "handle edge cases better".

### 3.6 Claude Code in CI/CD

```bash
claude --bare -p "Review the diff in pr.diff against the standards in CLAUDE.md. Report only new issues." \
  --append-system-prompt-file .claude/ci/review-instructions.md \
  --allowedTools "Read,Grep,Glob" \
  --output-format json \
  --json-schema "$(cat .claude/ci/findings.schema.json)" \
  --max-turns 15 \
  > review.json
jq '.structured_output' review.json
```

| Flag | Why it matters in CI |
|---|---|
| `-p` / `--print` | Non-interactive: runs and exits instead of waiting for input |
| `--output-format json` | Machine-readable result with `result`, `session_id`, cost and usage |
| `--json-schema` | Validated output in the `structured_output` field; check the field exists before use |
| `--allowedTools`, `--permission-mode dontAsk` | `--allowedTools` **auto-approves** the listed tools; it does not remove others. With `dontAsk`, any call that would need a prompt is denied instead of hanging. To limit which tools exist at all, use `--tools` (or deny rules) |
| `--max-turns`, `--max-budget-usd` | Bound runaway jobs |
| `--bare` | Skip auto-discovery of local hooks, skills, plugins, MCP servers and CLAUDE.md for reproducible runs; pass what you need with flags. Recommended for scripted calls |

> **Choose deliberately between `--bare` and CLAUDE.md context.** The exam guide treats CLAUDE.md as the way to
> give CI runs project context (testing standards, fixtures, review criteria). That is true in a normal `-p` run.
> In `--bare` mode CLAUDE.md is not loaded, so supply the same content explicitly, for example with
> `--append-system-prompt-file`. Both are valid; the point is that the context must arrive somehow.

Design guidance for review and test-generation jobs:

- **Independent reviewer.** The session that wrote code is a poor reviewer of it: it carries its own reasoning
  and tends to agree with itself. Run review in a separate invocation with no generation history.
- **Re-runs after new commits.** Include the previous findings and ask Claude to report only issues that are new
  or still unaddressed, so the PR does not collect duplicate comments.
- **Test generation.** Provide the existing tests (or their names) so Claude does not regenerate covered cases;
  document test standards, valuable test criteria and available fixtures in CLAUDE.md or the appended prompt.
- **Inline comments.** Make the schema carry `file`, `line`, `severity`, `category`, `message` and
  `suggested_fix` so a script can post each finding at the right place.

## Worked design scenario

*Northwind Freight* has 60 engineers and a monorepo with 35 services. Claude Code output is inconsistent.

1. Conventions lived in two senior engineers' `~/.claude/CLAUDE.md`. They move to the project CLAUDE.md
   (short) and `.claude/rules/` files.
2. Test conventions apply to `**/*_test.go` in every service, so they become a path-scoped rule rather than 35
   subdirectory CLAUDE.md files.
3. A `/release-notes` skill with `argument-hint: "[from-tag] [to-tag]"` replaces a wiki page of copy-paste
   prompts; a `/survey-service` skill uses `context: fork` with the Explore agent.
4. Engineers use plan mode for cross-service changes and direct execution for single-file fixes.
5. CI runs `claude --bare -p ... --output-format json --json-schema ...` with read-only tools as a separate
   review job, feeding previous findings on re-runs.

## Anti-patterns

- Team standards in a personal CLAUDE.md, or secrets in any CLAUDE.md.
- One huge CLAUDE.md that loads hundreds of irrelevant lines into every session.
- Treating CLAUDE.md as a security control ("never read .env") instead of a deny rule or hook.
- Assuming `allowed-tools` blocks the tools it does not list.
- Plan mode for a typo fix; direct execution for a cross-cutting migration.
- CI jobs without `-p`, without a schema, or reviewing code in the same session that wrote it.

## Labs and further practice

- [Lab 10: Claude Code workflows](../../../19-hands-on-labs/lab-10-claude-code-workflows/README.md)
- [Lab 02: Prompt improvement](../../../19-hands-on-labs/lab-02-prompt-improvement/README.md)
- [Claude Code cheat sheet](../../../22-cheat-sheets/claude-code.md)
- Practical exercises 5 and 6 in [`practical-exercises.md`](../practical-exercises.md)

## Self-check

1. Where should a convention for all `*.test.tsx` files across a monorepo live, and why?
2. What does `context: fork` do in a skill?
3. Does `allowed-tools: Read, Grep` stop a skill from using Bash?
4. Name two signals that call for plan mode.
5. Which two CLI flags give you schema-validated JSON in CI, and where does the result appear?

<details>
<summary>Answers</summary>

1. In a `.claude/rules/` file with `paths: ["**/*.test.tsx"]`, because it applies by file type across many
   directories and loads only when such a file is touched.
2. It runs the skill as a subagent with a clean context, so its verbose output stays out of the main
   conversation; only the result returns.
3. No. It pre-approves Read and Grep; Bash remains available under normal permissions. Use `disallowed-tools`
   or a deny rule to remove it.
4. Any two of: many files or services affected, several valid approaches, architectural or infrastructure
   consequences, unfamiliar codebase.
5. `--output-format json` with `--json-schema`; the validated object is in `structured_output`.

</details>
