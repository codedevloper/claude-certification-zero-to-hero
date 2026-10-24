# CCAR-F Readiness Assessment

> A self-assessment against every CCAR-F objective in [`registry.yaml`](../registry.yaml), with a scenario check,
> readiness criteria and remediation paths. Take it at the start of your preparation and again in the final week.

> **Important:** nothing in this repository produces an official score. Practice-question percentages, mock-exam
> results and the self-ratings below are **unofficial indicators only and do not equal the scaled score**
> (100–1,000, pass at 720) reported by the real exam. Scaled scores come from the official exam's own psychometric
> process and cannot be derived from a raw percentage on our materials.

## How to rate yourself

| Score | Meaning |
|---|---|
| 0 | I could not explain this to a colleague |
| 1 | I recognise the terms but could not choose a configuration |
| 2 | I can choose and justify the right configuration for a typical case |
| 3 | I have built it (in the labs or at work) and can handle edge cases |

CCAR-F is hands-on; be strict about the difference between 2 and 3.

## Self-assessment by objective

### Domain 1 — Agentic Architecture & Orchestration (27%)

| ID | Can I... | Score |
|---|---|---|
| CCAR-F-1.1 | Write a loop that branches on `stop_reason`, appends all tool results correctly, and name three loop anti-patterns? | |
| CCAR-F-1.2 | Design a coordinator that selects subagents per request, partitions scope and iterates on coverage gaps? | |
| CCAR-F-1.3 | Define `AgentDefinition`s, brief subagents completely, spawn them in parallel and explain `Agent` vs `Task` and approval vs restriction? | |
| CCAR-F-1.4 | Turn a compliance rule into a programmatic gate and write a structured hand-off for a human? | |
| CCAR-F-1.5 | Write `PreToolUse` and `PostToolUse` hooks that block, rewrite or normalise, and explain when a hook is required? | |
| CCAR-F-1.6 | Choose between prompt chaining, dynamic decomposition and per-file plus integration passes? | |
| CCAR-F-1.7 | Resume, name and fork sessions in the CLI and SDK, and decide between resuming and starting fresh? | |

### Domain 2 — Tool Design & MCP Integration (18%)

| ID | Can I... | Score |
|---|---|---|
| CCAR-F-2.1 | Rewrite ambiguous tool descriptions and split or rename overlapping tools? | |
| CCAR-F-2.2 | Return MCP tool errors with `isError` and a structured payload, and tell an access failure from an empty result? | |
| CCAR-F-2.3 | Scope tools per agent and explain `tool_choice` options, including the 400 on current Opus, Sonnet, Fable and Mythos models? | |
| CCAR-F-2.4 | Configure project, user and local MCP servers with `${VAR}` expansion and use resources? | |
| CCAR-F-2.5 | Pick Glob, Grep, Read, Edit, Write or Bash correctly and recover from a failed Edit? | |

### Domain 3 — Claude Code Configuration & Workflows (20%)

| ID | Can I... | Score |
|---|---|---|
| CCAR-F-3.1 | Place instructions at the right CLAUDE.md level, use `@imports` and diagnose with `/memory`? | |
| CCAR-F-3.2 | Write skills and commands with the right frontmatter, including `context: fork` and the `allowed-tools` / `disallowed-tools` difference? | |
| CCAR-F-3.3 | Write path-scoped rules and say when they beat subdirectory CLAUDE.md files? | |
| CCAR-F-3.4 | Decide plan mode versus direct execution and use the Explore subagent? | |
| CCAR-F-3.5 | Use examples, tests, the interview pattern and combined versus sequential fixes? | |
| CCAR-F-3.6 | Build a CI job with `-p`, JSON output, a schema, scoped tools and an independent reviewer? | |

### Domain 4 — Prompt Engineering & Structured Output (20%)

| ID | Can I... | Score |
|---|---|---|
| CCAR-F-4.1 | Write explicit report/skip and severity criteria that measurably cut false positives? | |
| CCAR-F-4.2 | Choose few-shot examples for format, ambiguous cases and varied documents? | |
| CCAR-F-4.3 | Enforce output with `output_config.format` or strict tools and design nullable, extensible schemas? | |
| CCAR-F-4.4 | Build semantic validation with targeted retries and know when retries cannot help? | |
| CCAR-F-4.5 | Decide synchronous versus batch, size submission intervals to a deadline and handle failures by `custom_id`? | |
| CCAR-F-4.6 | Design independent and multi-pass review with confidence per finding? | |

### Domain 5 — Context Management & Reliability (15%)

| ID | Can I... | Score |
|---|---|---|
| CCAR-F-5.1 | Keep case facts outside summaries, trim tool output and order long inputs for position effects? | |
| CCAR-F-5.2 | Write escalation criteria that honour explicit requests and policy gaps without escalating on sentiment? | |
| CCAR-F-5.3 | Design error reports that let a coordinator recover, and annotate coverage gaps? | |
| CCAR-F-5.4 | Keep a long codebase exploration coherent with subagents, scratchpads, summaries and `/compact`? | |
| CCAR-F-5.5 | Calibrate confidence, measure accuracy by segment and design stratified sampling? | |
| CCAR-F-5.6 | Preserve claim-source mappings, annotate conflicts and handle dates in synthesis? | |

## Scenario check

Because the exam draws four of six scenarios, rate yourself on each one as well. For each, can you sketch the
architecture, name three key decisions with the right choice, and list three traps, without notes?

| Scenario | Ready (yes/no) |
|---|---|
| Customer Support Resolution Agent | |
| Code Generation with Claude Code | |
| Multi-Agent Research System | |
| Developer Productivity with Claude | |
| Claude Code for Continuous Integration | |
| Structured Data Extraction | |

## Readiness criteria

You are likely ready to book (or keep) your exam date when **all** of the following hold:

1. **Self-assessment:** no objective scored 0, no more than three scored 1, and every Domain 1 objective (27% of the
   exam) scored 2 or higher.
2. **Scenarios:** "yes" for **all six** scenarios. A gap in any one has about a two-in-three chance of appearing.
3. **Practice questions:** consistently at or above 80% on the CCAR-F
   [practice question banks](../../17-practice-questions/README.md), on questions you have not seen before, and you
   can explain why each wrong option is wrong.
4. **Mock exams:** at least two timed [mock examinations](../../18-mock-examinations/README.md) at 60 items in
   120 minutes, finished with time to review and scoring 80% or higher.
5. **Hands-on:** at least five of the eight [practical exercises](practical-exercises.md) completed, including
   exercises 1, 3 and 6.
6. **Decisions:** the recommended choice on at least 12 of the 14 [decision scenarios](decision-scenarios.md) before
   reading the analysis.

These thresholds are our suggestion for building a safety margin. They are **not** a conversion to the official
scaled score, and meeting them does not guarantee a pass.

## Remediation paths

| Weak area | Read | Do | Then |
|---|---|---|---|
| 1.1 | [Domain 1 guide](study-guide/domain-1.md), [The agent loop](../../10-agentic-ai/03-the-agent-loop.md) | [Lab 08](../../19-hands-on-labs/lab-08-tool-invocation/README.md), exercise 1 | Decision scenario 1 |
| 1.2, 1.3, 1.6 | [Multi-agent architecture](../../10-agentic-ai/04-multi-agent-architecture.md), [Agent SDK](../../10-agentic-ai/06-managed-agents-and-agent-sdk.md) | [Lab 12](../../19-hands-on-labs/lab-12-agentic-task-execution/README.md), exercise 2 | Decision scenarios 2, 3 |
| 1.4, 1.5 | [Hooks](../../09-claude-code/06-hooks.md), [Human in the loop](../../10-agentic-ai/05-human-in-the-loop.md) | [Lab 13](../../19-hands-on-labs/lab-13-human-in-the-loop/README.md), exercise 3 | Decision scenarios 4, 5 |
| 1.7, 5.4 | [Headless, CI and the Agent SDK](../../09-claude-code/09-headless-ci-and-agent-sdk.md), [Compaction and context editing](../../04-context-engineering/05-compaction-and-context-editing.md) | [Lab 05](../../19-hands-on-labs/lab-05-context-management/README.md), exercise 8 | Decision scenarios 6, 11 |
| 2.1, 2.3 | [Tool design best practices](../../07-tool-use-and-function-calling/05-tool-design-best-practices.md), [Defining tools](../../07-tool-use-and-function-calling/02-defining-tools.md) | [Lab 08](../../19-hands-on-labs/lab-08-tool-invocation/README.md) | Decision scenarios 7, 8 |
| 2.2, 2.4 | [Building an MCP server](../../08-model-context-protocol/03-building-an-mcp-server.md), [MCP in Claude Code](../../09-claude-code/07-mcp-in-claude-code.md) | [Lab 09](../../19-hands-on-labs/lab-09-mcp-fundamentals/README.md), exercise 4 | Decision scenario 9 |
| 2.5, 3.4 | [What is Claude Code](../../09-claude-code/01-what-is-claude-code.md), [Commands, skills and subagents](../../09-claude-code/05-commands-skills-subagents.md) | [Lab 10](../../19-hands-on-labs/lab-10-claude-code-workflows/README.md) | Scenario 4 in [scenarios.md](scenarios.md) |
| 3.1, 3.2, 3.3 | [CLAUDE.md and memory](../../09-claude-code/03-claude-md-and-memory.md), [Team rollout](../../09-claude-code/08-team-rollout.md) | Exercise 5 | Decision scenarios 10, 11 |
| 3.5 | [Iterating on prompts](../../03-prompt-engineering/08-iterating-on-prompts.md) | [Lab 02](../../19-hands-on-labs/lab-02-prompt-improvement/README.md) | Scenario 2 in [scenarios.md](scenarios.md) |
| 3.6, 4.1, 4.2, 4.6 | [Domain 4 guide](study-guide/domain-4.md), [Few-shot examples](../../03-prompt-engineering/03-examples-few-shot.md), [Grading methods](../../14-evaluation-and-testing/04-grading-methods.md) | [Lab 16](../../19-hands-on-labs/lab-16-evaluation-framework/README.md), exercise 6 | Decision scenario 12 |
| 4.3, 4.4 | [Structured output](../../03-prompt-engineering/06-structured-output.md), [Diagnosing failures](../../14-evaluation-and-testing/06-diagnosing-failures.md) | [Lab 03](../../19-hands-on-labs/lab-03-structured-outputs/README.md), exercise 7 | Decision scenario 13 |
| 4.5 | [Batch processing](../../06-claude-api/05-batch-processing.md), [Cost optimisation](../../15-production-operations/03-cost-optimisation.md) | [Lab 17](../../19-hands-on-labs/lab-17-cost-optimisation/README.md) | Decision scenario 14 |
| 5.1, 5.2 | [Managing long context](../../04-context-engineering/02-managing-long-context.md), [Human oversight](../../12-ai-security/13-human-oversight.md) | [Lab 05](../../19-hands-on-labs/lab-05-context-management/README.md), [Lab 13](../../19-hands-on-labs/lab-13-human-in-the-loop/README.md) | Scenario 1 in [scenarios.md](scenarios.md) |
| 5.3, 5.6 | [Agent reliability](../../10-agentic-ai/07-agent-reliability.md), [Grounding and citations](../../11-rag-and-knowledge-systems/05-grounding-and-citations.md) | [Lab 18](../../19-hands-on-labs/lab-18-reliability-engineering/README.md), exercise 2 | Scenario 3 in [scenarios.md](scenarios.md) |
| 5.5 | [Grading methods](../../14-evaluation-and-testing/04-grading-methods.md), [Human oversight](../../12-ai-security/13-human-oversight.md) | Exercise 7 | Scenario 6 in [scenarios.md](scenarios.md) |

Use the [CCAR-F flashcards](../../23-flashcards/decks/ccar-f.yaml) daily for recall, filtered by the objectives you
scored 0 or 1. The [coverage matrix](coverage-matrix.md) shows which practice questions map to each objective.
