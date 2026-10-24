# CCAR-F Common Misconceptions

> Twenty-six misconceptions with corrections. Each maps to objectives in [`registry.yaml`](../registry.yaml).
> Product facts are as of 2026-10-24.

| # | Misconception | Correction | Objective |
|---|---|---|---|
| 1 | "If the response contains text, the agent has finished." | Claude often writes text and requests a tool in the same turn. Control the loop with `stop_reason`: continue on `tool_use`, finish on `end_turn`, handle the rest explicitly. | 1.1 |
| 2 | "An iteration cap is a good way to end the loop." | A cap is a safety net. The normal end is `end_turn`; a cap as the main mechanism truncates complex tasks and wastes calls on simple ones. | 1.1 |
| 3 | "Subagents can see what the coordinator has already learned." | A subagent starts with a fresh context (unless it is a fork). Everything it needs must be in its brief. | 1.2, 1.3 |
| 4 | "A coordinator should run every subagent so nothing is missed." | Select subagents by request complexity; fan-out multiplies tokens and latency. | 1.2 |
| 5 | "Subagents run in parallel whenever there are several of them." | The coordinator must emit several Agent tool calls in one response; calls made across separate turns run one after another. | 1.3 |
| 6 | "The subagent tool is called Task." | The v1.0 exam guide uses "Task". Current SDKs use the `Agent` tool in `tool_use` blocks; the init tool list still shows `Task`. Same mechanism. | 1.3 |
| 7 | "`allowedTools` limits an agent to the listed tools." | It auto-approves those tools. Restrict with a subagent's `tools` list, `disallowedTools`, `--tools`, or deny rules. | 1.3, 2.3 |
| 8 | "A clear system-prompt rule is enough for compliance steps." | Prompt guidance has a non-zero failure rate. Use hooks or server-side checks when the rule must always hold. | 1.4, 1.5 |
| 9 | "Resuming a session is always better than starting over." | Resume when earlier context is still valid. If many tool results are stale, start fresh with a structured summary; if a few files changed, resume and name them. | 1.7 |
| 10 | "Forking a session also branches my files." | Sessions hold conversation, not filesystem state. A fork that edits files changes the real files. | 1.7 |
| 11 | "Tool names matter more than descriptions." | Descriptions are the main selection signal: purpose, when to use versus neighbours, inputs, outputs and limits. | 2.1 |
| 12 | "Any tool failure should be a protocol error." | In MCP, failures the model can act on (bad input, timeouts, business rules) are tool results with `isError: true`; protocol errors are for malformed requests and unknown tools. | 2.2 |
| 13 | "`errorCategory` and `isRetryable` are MCP fields." | Only `isError` is in the specification. Category and retryability are a payload convention you design so the agent can choose a recovery path. | 2.2 |
| 14 | "No matches is an error." | A query that ran and found nothing is a successful empty result. Reporting it as an error triggers pointless retries; reporting a timeout as empty causes false negatives. | 2.2, 5.3 |
| 15 | "`tool_choice: any` guarantees a tool call on every model." | It returns a 400 on Claude Opus 5.5, Sonnet 5.5, Fable 5.1 and Mythos 5.1 (Haiku 5.5 accepts it). Use `auto` plus an instruction and `strict: true`, or structured outputs. | 2.3, 4.3 |
| 16 | "Secrets for a shared MCP server must be committed so everyone has them." | Use `${VAR}` expansion in `.mcp.json`; each person or CI job supplies the variable. | 2.4 |
| 17 | "Personal `~/.claude/CLAUDE.md` instructions apply to the whole team." | User-level files are local to one person. Team conventions go in the project CLAUDE.md or `.claude/rules/`. | 3.1 |
| 18 | "Nearer CLAUDE.md files override broader ones." | Files are concatenated, not overridden. Conflicting instructions confuse Claude; remove contradictions. | 3.1 |
| 19 | "`allowed-tools` in a skill restricts it to those tools." | It pre-approves them for the invoking turn. Use `disallowed-tools` to remove tools while the skill is active. | 3.2 |
| 20 | "A subdirectory CLAUDE.md is the best place for file-type conventions." | For conventions that follow a file type across directories, a `.claude/rules/` file with `paths` globs is better. | 3.3 |
| 21 | "Plan mode is always the safer choice." | It costs time. Use it for multi-file, multi-option or architectural work; act directly on small, well-understood fixes. | 3.4 |
| 22 | "The session that wrote the code is the best reviewer because it knows the intent." | It carries its own reasoning and tends to confirm it. Use an independent instance. | 3.6, 4.6 |
| 23 | "Telling the model to be conservative reduces false positives." | Explicit report/skip criteria, severity definitions and contrasting examples do; adjectives do not. | 4.1 |
| 24 | "A strict schema means the data is correct." | It guarantees shape, not truth. Validate sums, dates and cross-field rules in code and retry with specific errors. | 4.3, 4.4 |
| 25 | "Batches are the cheap default for any workload." | Batches are half price but can take up to 24 hours and cannot continue a tool loop inside a request. Use them for latency-tolerant work only. | 4.5 |
| 26 | "96% overall accuracy means we can drop human review." | Aggregates hide weak document types and fields. Measure per segment, calibrate confidence on labelled data and keep stratified sampling. | 5.5 |

See the [decision scenarios](decision-scenarios.md) for worked examples of several of these, and the
[readiness assessment](readiness-assessment.md) to find which ones you still hold.
