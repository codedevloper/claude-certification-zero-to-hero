# Module 10 — Agentic AI

> **Level:** Intermediate to Advanced · **Time:** ~6 hours including labs · **Exam relevance:** CCAR-P D1 (primary), D5

An "agent" is one of the most overused words in AI. This module gives you a precise vocabulary for it, shows you
the simpler designs that solve most problems, and then teaches you how to build, supervise and harden real agents
with Claude. The thread running through every page is the same piece of advice Anthropic's engineers give: start
with the simplest design that works, and add autonomy only when it earns its cost.

## Learning objectives

By the end of this module you can:

1. Distinguish a single augmented LLM call, a workflow (code decides the path) and an agent (the model decides the path),
   and argue when **not** to build an agent.
2. Recognise and implement the five common workflow patterns: prompt chaining, routing, parallelisation,
   orchestrator–workers and evaluator–optimiser.
3. Write a correct agent loop against the Messages API, including every `stop_reason` and parallel tool results.
4. Design a multi-agent system with an orchestrator and subagents, and explain its context isolation benefit, its
   token-cost multiplication and how failures propagate.
5. Place human-in-the-loop controls: approval gates, confidence thresholds and escalation paths.
6. Choose between a manual loop, the SDK Tool Runner, the Claude Agent SDK and Claude Managed Agents.
7. Make an agent reliable with budgets, stopping conditions, idempotent tools, checkpoints and observability.

## Page order

| # | Page | What you learn |
|---|---|---|
| 1 | [Workflows vs agents](01-workflows-vs-agents.md) | The complexity ladder and the "should this be an agent?" test |
| 2 | [Workflow patterns](02-workflow-patterns.md) | Augmented LLM plus five composable patterns, with diagrams and code |
| 3 | [The agent loop](03-the-agent-loop.md) | The observe–decide–act cycle in code, and every way it ends |
| 4 | [Multi-agent architecture](04-multi-agent-architecture.md) | Orchestrator and subagents, isolation, cost and failure propagation |
| 5 | [Human in the loop](05-human-in-the-loop.md) | Approval gates, confidence thresholds and escalation |
| 6 | [Managed Agents, Agent SDK, Tool Runner or manual loop](06-managed-agents-and-agent-sdk.md) | The four ways to build an agent on Claude |
| 7 | [Agent reliability](07-agent-reliability.md) | Budgets, stopping conditions, idempotency, checkpoints, observability |

## Prerequisites

- [Module 03 — Prompt engineering](../03-prompt-engineering/README.md), especially
  [task decomposition and chaining](../03-prompt-engineering/05-task-decomposition-and-chaining.md).
- [Module 04 — Context engineering](../04-context-engineering/README.md): agents live or die by what is in their context.
- [Module 07 — Tool use and function calling](../07-tool-use-and-function-calling/README.md), especially
  [the tool-use loop](../07-tool-use-and-function-calling/03-the-tool-use-loop.md). This module assumes you can define a tool
  and return a `tool_result`.
- Helpful: [Module 08 — Model Context Protocol](../08-model-context-protocol/README.md) and
  [Module 09 — Claude Code](../09-claude-code/README.md), because Claude Code is itself an agent built on the same ideas.

## Exam relevance

This module underpins the following Claude Certified Architect – Professional (CCAR-P) objectives. Objective IDs
and wording come from [`registry.yaml`](../16-certification-tracks/registry.yaml).

| Objective | Summary | Pages |
|---|---|---|
| **CCAR-P-1.3** | Select architectural patterns (workflow, agentic, augmented LLM) | 01, 02, 06 |
| **CCAR-P-1.4** | Design multi-agent systems and orchestration strategies | 03, 04 |
| **CCAR-P-1.5** | Apply decomposition techniques to complex problems | 02, 04 |
| **CCAR-P-5.3** | Apply human-in-the-loop validation | 05 |
| CCAR-P-5.2 (secondary) | Identify risks, limitations and failure modes of LLM systems | 04, 07 |
| CCAR-P-3.1 (secondary) | Evaluate tool and agent configuration for capability bloat | 03, 06 |
| CCAR-P-4.6 (secondary) | Monitor performance with logging and observability tooling | 07 |

The CCAR-P study guides for [Domain 1](../16-certification-tracks/ccar-p/study-guide/domain-1.md) and
[Domain 5](../16-certification-tracks/ccar-p/study-guide/domain-5.md) link back here.

## Practise it

- Lab: [lab-12 — Agentic task execution](../19-hands-on-labs/lab-12-agentic-task-execution/README.md) builds a
  bounded agent loop with budgets and a stopping condition, offline in mock mode.
- Lab: [lab-13 — Human in the loop](../19-hands-on-labs/lab-13-human-in-the-loop/README.md) adds approval gates and
  confidence-based escalation.
- Lab: [lab-18 — Reliability engineering](../19-hands-on-labs/lab-18-reliability-engineering/README.md) practises
  retries, idempotency and checkpoints.
- Lab: [lab-20 — Secure enterprise architecture](../19-hands-on-labs/lab-20-secure-enterprise-architecture/README.md)
  puts an agent behind enterprise controls.
- Projects: [Agentic investigation assistant](../20-real-world-projects/05-agentic-investigation-assistant/README.md)
  (orchestrator, tools, approvals) and [Security alert triage assistant](../20-real-world-projects/03-security-alert-triage-assistant/README.md)
  (routing and escalation).
- When something goes wrong: [tools and agents troubleshooting](../24-troubleshooting/tools-and-agents.md).

## Next module

Continue to [Module 11 — RAG and knowledge systems](../11-rag-and-knowledge-systems/README.md), where retrieval
becomes one of the tools an agent can call. Agent security (excessive agency, tool misuse, agent identity) is covered
in depth in [Module 12 — AI security](../12-ai-security/README.md).
