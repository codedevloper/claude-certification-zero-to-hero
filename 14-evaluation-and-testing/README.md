# Module 14: Evaluation and Testing

> **Level:** Intermediate to Advanced · **Time:** ~6 hours (pages) + ~3 hours (labs) · **Exam relevance:** CCAR-P D4 (4.1, 4.2, 4.3, 4.4, 4.5), CCAR-P D5 (5.1, 5.2), CCAO-F D2 (2.1, 2.2, 2.3), CCAO-F D7 (7.1, 7.2)

Evaluation is how you turn "it seems to work" into evidence. This module shows how to define success, measure it,
build datasets that represent real use, grade outputs reliably, compare versions fairly, find out why a system fails,
and test for safety and security failures before attackers or customers find them.

It underpins CCAR-P Domain 4, Evaluation, Testing and Optimization. The production side of Domain 4 (cost, latency
and monitoring) continues in [Module 15](../15-production-operations/README.md).

## Learning objectives

By the end of this module you can:

1. Explain why LLM applications need systematic evaluation and where evals sit in the development lifecycle.
2. Define success criteria and metrics across accuracy, latency, cost, safety and security, using Anthropic's
   guidance on specific, measurable, achievable and relevant criteria.
3. Build evaluation datasets from production samples, golden sets, synthetic generation and deliberate edge cases,
   and keep them healthy over time.
4. Choose and combine grading methods: code-based checks, LLM-as-judge with rubrics and calibration, and human review.
5. Run offline comparisons and online A/B tests with basic statistical discipline, and iterate safely.
6. Diagnose failures: prompt failure, hallucination, model mismatch, retrieval failure and harness bugs, using a
   decision tree.
7. Design safety and red-team evals that test guardrails, prompt-injection resistance and harmful-output behaviour.

## Page order

| # | Page | What you get |
|---|---|---|
| 1 | [Why evaluate](01-why-evaluate.md) | The case for evals, the eval-driven loop, types of evals |
| 2 | [Metrics](02-metrics.md) | Quality, latency, cost, safety and security metrics, with formulas |
| 3 | [Building eval datasets](03-building-eval-datasets.md) | Golden sets, synthetic generation, edge cases, dataset hygiene |
| 4 | [Grading methods](04-grading-methods.md) | Code-based, LLM-as-judge, human review, mixed methods, calibration |
| 5 | [A/B testing and iteration](05-ab-testing-and-iteration.md) | Offline vs online, significance basics, safe iteration |
| 6 | [Diagnosing failures](06-diagnosing-failures.md) | Failure taxonomy and decision tree |
| 7 | [Safety and red-team evals](07-safety-and-red-team-evals.md) | Guardrail, injection and harmful-output testing |

Read the pages in order. Pages 2 to 4 are the core toolkit; pages 5 to 7 apply it.

## Prerequisites

- [Module 03: Prompt engineering](../03-prompt-engineering/README.md), especially
  [iterating on prompts](../03-prompt-engineering/08-iterating-on-prompts.md).
- [Module 06: Claude API](../06-claude-api/README.md), including
  [batch processing](../06-claude-api/05-batch-processing.md) (useful for running large evals cheaply).
- Helpful: [Module 11: RAG evaluation](../11-rag-and-knowledge-systems/06-rag-evaluation.md) and
  [Module 12: AI security](../12-ai-security/README.md) for page 7.
- Basic Python and comfort with simple statistics (means, proportions).

## Hands-on labs and projects

| Lab / project | Pages it exercises |
|---|---|
| [Lab 16: evaluation framework](../19-hands-on-labs/lab-16-evaluation-framework/README.md) | 2, 3, 4, 5 |
| [Lab 14: prompt injection testing](../19-hands-on-labs/lab-14-prompt-injection-testing/README.md) | 7 |
| [Lab 06: model comparison](../19-hands-on-labs/lab-06-model-comparison/README.md) | 2, 5, 6 |
| [Lab 11: RAG pipeline](../19-hands-on-labs/lab-11-rag-pipeline/README.md) | 6 (retrieval failures) |
| [Project 02: knowledge base Q&A assistant](../20-real-world-projects/02-knowledge-base-qa-assistant/README.md) | 3, 4, 6 |
| [Project 04: DevSecOps code review assistant](../20-real-world-projects/04-devsecops-code-review-assistant/README.md) | 4, 7 |

## Exam relevance

| Objective | Where it is covered |
|---|---|
| CCAR-P-4.1 Define evaluation metrics (accuracy, latency, cost, safety, security) | Pages 1, 2 |
| CCAR-P-4.2 Design evaluation datasets and mixed-method test frameworks | Pages 3, 4 |
| CCAR-P-4.3 Run A/B tests and iterative improvement | Page 5 |
| CCAR-P-4.4 Diagnose prompt failure, hallucination and model mismatch | Page 6 |
| CCAR-P-4.5 Optimise token usage, latency and cost-performance | Page 2 (measurement); continued in Module 15 |
| CCAR-P-5.1 / 5.2 Guardrails; risks and failure modes | Page 7 |
| CCAO-F-2.1 / 2.2 / 2.3 Evaluate outputs; spot hallucinations; fact-checking | Pages 4, 6 |
| CCAO-F-7.1 / 7.2 Diagnose and fix poor outputs; adjust based on feedback | Pages 5, 6 |

Objective wording and domain weights come from
[`16-certification-tracks/registry.yaml`](../16-certification-tracks/registry.yaml). The
[CCAR-P Domain 4 study guide](../16-certification-tracks/ccar-p/study-guide/domain-4.md) gives exam-focused revision.

## Next module

Continue to [Module 15: Production operations](../15-production-operations/README.md), where these evals become
release gates, monitoring signals and upgrade checks.
