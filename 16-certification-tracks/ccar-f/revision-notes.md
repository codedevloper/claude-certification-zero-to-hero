# CCAR-F Revision Notes

> Condensed notes for the final two weeks. Exam facts come from [`registry.yaml`](../registry.yaml); SDK, Claude
> Code, MCP and API facts are as of 2026-10-24. Each section links to the full study guide.

**Exam at a glance:** 60 items (multiple-choice and multiple-response), 120 minutes, 4 scenarios drawn at random
from a published bank of 6, scaled score 720 on 100–1,000 to pass, USD 125, valid 12 months. Details:
[README](README.md), [exam day](exam-day.md), [scenarios](scenarios.md).

| Domain | Weight | Rough items (of 60) |
|---|---|---|
| 1 Agentic Architecture & Orchestration | 27% | ~16 |
| 2 Tool Design & MCP Integration | 18% | ~11 |
| 3 Claude Code Configuration & Workflows | 20% | ~12 |
| 4 Prompt Engineering & Structured Output | 20% | ~12 |
| 5 Context Management & Reliability | 15% | ~9 |

Item counts per domain are our estimates from the weights, not official figures.

---

## Domain 1 — Agentic architecture ([guide](study-guide/domain-1.md))

- Loop: `tool_use` → run tools, append the full assistant turn and **all** `tool_result` blocks in one user
  message, call again; `end_turn` → done; `max_tokens`, `pause_turn`, `refusal` → handle explicitly.
- Never end on "text present" or parsed phrases; caps (`max_turns`, `max_budget_usd`) are safety nets.
- Hub and spoke: subagents report to the coordinator. Coordinator selects subagents per request, partitions scope,
  checks coverage, re-delegates for gaps.
- Subagents start fresh (forks excepted): pass goal, scope, prior findings and output format in the brief.
- `AgentDefinition`: `description` + `prompt` required; `tools` allow-list restricts; `model`, `skills`,
  `mcpServers`, `maxTurns` optional. Spawned through the **`Agent` tool** (called `Task` in the v1.0 guide).
- `allowed_tools` / `allowedTools` **auto-approves**; it does not restrict.
- Parallel subagents: several Agent calls in one coordinator response.
- Enforcement: hooks or server checks for must-hold rules; prompts for guidance. Prerequisite gates keep state
  outside the model.
- Hooks: `PreToolUse` (`permissionDecision: deny|ask|allow|defer`, `updatedInput`), `PostToolUse`
  (`updatedToolOutput`, `additionalContext`); most restrictive decision wins; matchers match tool names.
- Hand-offs to humans: structured summary (customer, issues, evidence, actions, recommendation, expectation).
- Decomposition: chaining for predictable steps; dynamic for open-ended work; per-file passes + integration pass.
- Sessions: `--continue`, `--resume <id|name>`, `-n` to name, `--fork-session`; SDK `resume`, `fork_session` /
  `forkSession`, `continue_conversation` / `continue`. Sessions hold conversation, not files. Stale context →
  fresh session with a summary; a few changed files → resume and name them.

## Domain 2 — Tools and MCP ([guide](study-guide/domain-2.md))

- Descriptions: what, when (versus neighbours), input format with example, output, limits. Rename or split
  overlapping tools; check the system prompt for keyword triggers.
- MCP errors: tool execution errors → result with `isError: true`; protocol errors → JSON-RPC error. Clients
  should give tool errors to the model.
- Your payload convention: category (`transient`, `validation`, `business_rule`, `permission`), retryable flag,
  human-readable and customer-safe messages. Empty result ≠ error.
- Subagents recover locally; escalate with attempted actions and partial results.
- Few role-specific tools per agent; constrained tools over general ones; narrow cross-role tools only for
  frequent needs.
- `tool_choice`: `auto`, `none`, `any`, `{"type": "tool"}`. **`any` and forced return a 400 on Opus 5.5,
  Sonnet 5.5, Fable 5.1, Mythos 5.1**; Haiku 5.5 accepts. Replacement: `auto` + instruction + `strict: true` +
  check, or `output_config.format`.
- Claude Code MCP scopes: `local` (default, `~/.claude.json` per project), `project` (`.mcp.json`, shared),
  `user` (`~/.claude.json`, all projects). Precedence local > project > user. `${VAR}` / `${VAR:-default}`.
- Resources: `@server:protocol://path`; catalogues reduce exploratory calls. Tool search on by default.
- Built-ins: Glob = paths, Grep = content, Read → Edit (unique anchor) or Write (whole file), Bash = commands.
  Edit fails on non-unique match → more context, replace-all, or Read + Write.

## Domain 3 — Claude Code ([guide](study-guide/domain-3.md))

- CLAUDE.md: managed → user (`~/.claude/CLAUDE.md`) → project (`./CLAUDE.md` or `./.claude/CLAUDE.md`) → local
  (`CLAUDE.local.md`); ancestors load at launch and concatenate; subdirectories load on demand.
- `@path` imports (relative to the importing file, up to four hops). `/memory` to see and edit; `/context` to see
  what loaded.
- `.claude/rules/*.md`: no `paths` → always; `paths:` globs → only when a matching file is read or edited.
  Rules beat subdirectory CLAUDE.md for conventions that follow file type.
- Skills: `.claude/skills/<name>/SKILL.md` (project), `~/.claude/skills/` (personal); commands merged in; skill
  wins over same-name command. Frontmatter: `description`, `argument-hint`, `context: fork`, `agent`,
  `allowed-tools` (**pre-approves**), `disallowed-tools` (**restricts**), `disable-model-invocation`, `paths`.
- CLAUDE.md = always-on standards; skills = on-demand procedures.
- Plan mode (Shift+Tab, `--permission-mode plan`, `/plan`): explore and plan, no source edits until approved.
  Use for multi-file, multi-option, architectural work. Explore subagent = read-only discovery.
- Iteration: concrete I/O examples, tests first, interview pattern, combined message for interacting issues.
- CI: `-p`, `--output-format json`, `--json-schema` → `structured_output`; `--allowedTools`; `dontAsk`;
  `--max-turns`; `--bare` for reproducibility (then pass context explicitly). Independent reviewer; feed prior
  findings on re-runs; give existing tests to test generation.

## Domain 4 — Prompts and structured output ([guide](study-guide/domain-4.md))

- Precision from explicit report/skip criteria and severity definitions with examples, not "be conservative".
  Temporarily disable noisy categories.
- Few-shot: 2–4 diverse examples, include borderline cases with reasons, show format, show null for absent data.
- Structured outputs: `output_config.format` (`json_schema`) or `messages.parse()`; `strict: true` tools. Shape,
  not truth. Incompatible with citations and prefill. Check `stop_reason`.
- Schema: nullable for optional data; `enum` + `"other"` + detail; `"unclear"`; `additionalProperties: false`;
  normalisation rules in the prompt.
- Validation: semantic checks in code; retry with document + failed output + specific errors; do not retry when
  data is absent; record which rule produced each finding.
- Batches: 50% price, ≤24 h, no latency SLA, `custom_id`, results in any order, 29-day retention, ≤100,000
  requests; no tool loop inside a request; submission interval = deadline − 24 h (minus margin); re-submit
  failures only; tune on a sample first.
- Review: independent instance over self-review; per-file + integration passes; confidence per finding, calibrated
  before use.

## Domain 5 — Context and reliability ([guide](study-guide/domain-5.md))

- Case-facts block outside summaries; trim tool results; key findings first, headed sections; per-issue state;
  resend full history.
- Escalate: explicit request (immediately), policy gap, no progress, beyond authority. Not sentiment alone, not
  self-reported confidence. Multiple matches → ask for another identifier.
- Errors: failure type, what was attempted, partial results, alternatives; distinguish access failure from empty;
  no silent suppression; no abort-all; coverage annotations.
- Large codebases: subagents for discovery, scratchpad files, phase summaries, `/compact`, manifests for crash
  recovery.
- Review: accuracy by type and field; stratified sampling of high-confidence output; calibrated field confidence;
  route low-confidence and conflicting items first.
- Provenance: claim-source records preserved through synthesis; conflicts annotated with sources; dates required;
  established vs contested; render by content type.
