# CCAR-F One-Pager: Claude Certified Architect – Foundations

> **Unofficial summary.** Every exam fact on this page comes from
> [`16-certification-tracks/registry.yaml`](../16-certification-tracks/registry.yaml) (verified 2026-10-24 against the
> official exam guide v1.0, effective July 2026) and is summarised in
> [exam-facts.md](../25-official-resources/exam-facts.md). The official guide on the
> [Anthropic Partner Academy](https://anthropic-partners.skilljar.com/page/partner-certifications) is the source of
> truth. Pearson VUE has announced updated guides for 2026-11-17, so re-check before you book.
> Full track: [16 · CCAR-F](../16-certification-tracks/ccar-f/README.md).

## Exam format

| Item | Value (from the registry) |
|---|---|
| Audience | Solution architects building production applications with the Agent SDK, Claude Code, MCP and structured output |
| Recommended experience | 6+ months building with the Claude API, Agent SDK, Claude Code and MCP (not mandatory) |
| Items | 60, multiple-choice and multiple-response |
| Structure | 4 scenarios drawn at random from a published bank of 6 |
| Time | 120 minutes |
| Passing | Scaled score 720 on a 100–1,000 scale |
| Fee | USD 125 (list price) |
| Validity | 12 months |
| Delivery | Pearson VUE, online proctored or test centre |
| Eligibility | Organisations in the Claude Partner Network |

The six scenarios and how to study each are in [scenarios.md](../16-certification-tracks/ccar-f/scenarios.md).

## Domains, weights and what to know

### D1 · Agentic Architecture & Orchestration — 27% (largest domain)

- The agent loop: call, run tools, return results, stop on `end_turn`; cap turns and budget (CCAR-F-1.1).
- Coordinator and subagents: delegate for parallelism or context isolation, return summaries, not transcripts (CCAR-F-1.2, 1.3).
- Subagents are spawned with the `Agent` tool (called `Task` in the v1.0 guide); pass what they need in the prompt.
- Enforce order with code, not prose: prerequisite checks and hooks beat "always do X first" (CCAR-F-1.4).
- Hooks (`PreToolUse`, `PostToolUse`) intercept, block or normalise tool calls and results (CCAR-F-1.5).
- Decompose by independence and context size; keep sessions resumable or fork them (CCAR-F-1.6, 1.7).
- Study: [10 · The agent loop](../10-agentic-ai/03-the-agent-loop.md),
  [10 · Multi-agent architecture](../10-agentic-ai/04-multi-agent-architecture.md), [09 · Hooks](../09-claude-code/06-hooks.md).

### D2 · Tool Design & MCP Integration — 18%

- Tool descriptions are the interface: say what, when, inputs, outputs and limits (CCAR-F-2.1).
- Return errors as results with `isError` and enough context to recover; don't hide failures (CCAR-F-2.2).
- Give each agent only the tools it needs; `allowedTools` pre-approves, it does not restrict (CCAR-F-2.3).
- Forced `tool_choice` returns a 400 on Opus 5.5, Sonnet 5.5 and Fable 5.1; use `auto` plus a clear instruction or structured outputs.
- MCP scopes: project `.mcp.json` for the team, user scope for you (CCAR-F-2.4).
- Built-in tools: Grep and Glob to find, Read to inspect, Edit over Write for changes (CCAR-F-2.5).
- Study: [07 · Tool design](../07-tool-use-and-function-calling/05-tool-design-best-practices.md),
  [08 · MCP](../08-model-context-protocol/README.md), [cheat sheet: MCP](mcp.md).

### D3 · Claude Code Configuration & Workflows — 20%

- `CLAUDE.md` hierarchy: user, project, subdirectory; keep the root file short (CCAR-F-3.1).
- Skills (including what used to be custom slash commands) package repeatable team workflows (CCAR-F-3.2).
- `.claude/rules/` with `paths` frontmatter loads conventions only for matching files (CCAR-F-3.3).
- Plan mode for unfamiliar or wide changes; direct execution for small, clear ones (CCAR-F-3.4, 3.5).
- CI: headless `claude -p`, scoped tools and structured output for review and triage (CCAR-F-3.6).
- Study: [09 · Claude Code](../09-claude-code/README.md), [cheat sheet: Claude Code](claude-code.md).

### D4 · Prompt Engineering & Structured Output — 20%

- Explicit criteria cut false positives: say exactly what to flag and what to ignore (CCAR-F-4.1).
- Few-shot examples for format and edge cases; keep them varied (CCAR-F-4.2).
- Structured output with JSON schemas and strict tools; validate anyway (CCAR-F-4.3, 4.4).
- Retry with the validation error fed back; stop after a bounded number of attempts (CCAR-F-4.4).
- Message Batches for work that can wait; they cannot run your client-side tools mid-request (CCAR-F-4.5).
- Independent multi-pass review beats one model grading its own work (CCAR-F-4.6).
- Study: [03 · Prompt engineering](../03-prompt-engineering/README.md),
  [03 · Structured output](../03-prompt-engineering/06-structured-output.md),
  [06 · Batches](../06-claude-api/05-batch-processing.md).

### D5 · Context Management & Reliability — 15%

- Keep critical facts in a stable block outside summaries (CCAR-F-5.1).
- Escalate on ambiguity or policy limits; don't guess (CCAR-F-5.2).
- Propagate errors with enough context for the coordinator to decide (CCAR-F-5.3).
- Large codebases: delegate exploration to subagents, keep notes, compact (CCAR-F-5.4).
- Human review where confidence is low or impact is high (CCAR-F-5.5).
- Keep sources and dates attached to claims; report conflicts instead of picking one (CCAR-F-5.6).
- Study: [04 · Context engineering](../04-context-engineering/README.md),
  [10 · Agent reliability](../10-agentic-ai/07-agent-reliability.md).

## Builder's decision reflexes

| Situation | Reflex |
|---|---|
| A rule must always hold | Enforce it in code or a hook, not only in the prompt |
| Subagent needs information | Put it in the subagent's prompt; it does not see the parent conversation |
| Agent keeps calling the wrong tool | Fix the tool descriptions before adding instructions |
| Tool fails | Return a structured error result so the model can adapt |
| Output feeds code | Schema plus validation plus bounded retry |
| Long exploration fills context | Delegate to a subagent and keep a notes file |
| Team convention for some files | Path-scoped rule in `.claude/rules/` |

Practice: [17 · CCAR-F questions](../17-practice-questions/README.md),
[18 · Mock exams](../18-mock-examinations/README.md), [23 · Flashcards](../23-flashcards/README.md).
