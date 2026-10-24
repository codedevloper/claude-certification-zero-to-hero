# Module 15: Production Operations

> **Level:** Advanced · **Time:** ~7 hours (pages) + ~4 hours (labs) · **Exam relevance:** CCAR-P D4 (4.5, 4.6), CCAR-P D3 (3.3, 3.4), CCAR-P D6 (6.3, 6.5), CCAR-P D7 (7.3), CCAR-P D1 (1.6)

Getting a Claude application to work in a demo is the start. Running it for thousands of users, around the clock,
within a budget and a latency target, through model upgrades and incidents, is a different discipline. This module
covers that discipline: readiness, observability, cost, latency, reliability, capacity, incident response and change
management.

The emphasis is on what is specific to LLM systems: token-based cost and rate limits, variable output length,
`stop_reason` handling, refusals, prompt caching, model deprecations and quality regressions that do not show up as
errors.

## Learning objectives

By the end of this module you can:

1. Run a production-readiness review for a Claude-based application using a checklist.
2. Instrument an application with structured logs, request IDs, usage fields, traces (OpenTelemetry concepts) and
   dashboards that cover quality as well as uptime.
3. Reduce cost with prompt caching, the Message Batches API, model routing, effort tuning and token hygiene, and
   measure the effect.
4. Reduce latency with streaming, caching, model and effort choice, and parallelism.
5. Build reliable integrations: timeouts, retries with backoff, fallbacks, circuit breakers, idempotency and refusal
   handling.
6. Plan capacity against rate limits and spend limits, and handle 429 and 529 responses gracefully.
7. Respond to AI-specific incidents, from outages to prompt-injection campaigns and quality regressions.
8. Manage model upgrades safely with pinning, regression evals, staged rollout and deprecation tracking.

## Page order

| # | Page | What you get |
|---|---|---|
| 1 | [Production readiness](01-production-readiness.md) | A readiness checklist and review process |
| 2 | [Observability](02-observability.md) | Logs, traces, request IDs, usage fields, dashboards |
| 3 | [Cost optimisation](03-cost-optimisation.md) | Caching, batch, routing, effort, token hygiene |
| 4 | [Latency optimisation](04-latency-optimisation.md) | Streaming, caching, model choice, parallelism |
| 5 | [Reliability engineering](05-reliability-engineering.md) | Retries, timeouts, fallbacks, circuit breakers, idempotency |
| 6 | [Rate limits and capacity](06-rate-limits-and-capacity.md) | RPM, ITPM, OTPM, spend limits, capacity planning |
| 7 | [Incident response](07-incident-response.md) | AI-specific incident types and runbooks |
| 8 | [Model upgrades and change management](08-model-upgrades-and-change-management.md) | Pinning, regression evals, deprecations, rollout |

Read page 1 first; it links to everything else. Pages 2 to 6 can be read in any order. Pages 7 and 8 assume you have
read pages 2 and 5.

## Prerequisites

- [Module 06: Claude API](../06-claude-api/README.md), especially
  [streaming](../06-claude-api/03-streaming.md), [batch processing](../06-claude-api/05-batch-processing.md),
  [errors, rate limits and retries](../06-claude-api/06-errors-rate-limits-retries.md) and
  [token counting and cost](../06-claude-api/08-token-counting-and-cost.md).
- [Module 04: Prompt caching](../04-context-engineering/03-prompt-caching.md).
- [Module 14: Evaluation and testing](../14-evaluation-and-testing/README.md).
- Helpful: [Module 12: logging and auditability](../12-ai-security/11-logging-and-auditability.md) and general SRE
  concepts (SLOs, error budgets, on-call).

## Hands-on labs and projects

| Lab / project | Pages it exercises |
|---|---|
| [Lab 17: cost optimisation](../19-hands-on-labs/lab-17-cost-optimisation/README.md) | 3, 6 |
| [Lab 18: reliability engineering](../19-hands-on-labs/lab-18-reliability-engineering/README.md) | 5, 6 |
| [Lab 19: observability](../19-hands-on-labs/lab-19-observability/README.md) | 2, 7 |
| [Lab 16: evaluation framework](../19-hands-on-labs/lab-16-evaluation-framework/README.md) | 8 |
| [Lab 20: secure enterprise architecture](../19-hands-on-labs/lab-20-secure-enterprise-architecture/README.md) | 1 |
| [Project 01: document summarisation assistant](../20-real-world-projects/01-document-summarisation-assistant/README.md) | 3, 4, 5 |
| [Project 03: security alert triage assistant](../20-real-world-projects/03-security-alert-triage-assistant/README.md) | 2, 5, 7 |

## Exam relevance

| Objective | Where it is covered |
|---|---|
| CCAR-P-4.5 Optimise token usage, latency and cost-performance | Pages 3, 4 |
| CCAR-P-4.6 Monitor performance with logging and observability tooling | Page 2 |
| CCAR-P-3.3 Evaluate accuracy–latency trade-offs and justify configuration | Pages 3, 4, 8 |
| CCAR-P-3.4 Analyse observability challenges and choose monitoring at scale | Page 2 |
| CCAR-P-6.3 Manage stakeholder expectations, including SLAs | Pages 1, 6, 7 |
| CCAR-P-6.5 Support lifecycle phases (monitoring, iteration) | Pages 1, 8 |
| CCAR-P-7.3 Support debugging and operational issue resolution | Pages 2, 5, 7 |
| CCAR-P-1.6 Align solutions to business value (cost, SLAs) | Pages 1, 3 |

Objective wording and weights come from
[`16-certification-tracks/registry.yaml`](../16-certification-tracks/registry.yaml). See the
[CCAR-P Domain 4 study guide](../16-certification-tracks/ccar-p/study-guide/domain-4.md) and the
[API troubleshooting guide](../24-troubleshooting/api-errors.md).

## Next module

You have completed the learning modules. Continue to
[16: Certification tracks](../16-certification-tracks/README.md) to map what you have learned to the exam objectives
and start structured revision.
