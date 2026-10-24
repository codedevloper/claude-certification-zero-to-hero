# Module 03 — Prompt Engineering

> **Level:** Beginner → Intermediate · **Time:** ~6 hours (pages) + ~2 hours (labs) · **Exam relevance:** CCAO-F D1, D7 · CCAR-P D2, D4

Prompt engineering is the craft of writing the instructions, context and examples that steer Claude toward a
useful, reliable answer. This module turns the basics from
[Module 02 — Prompt fundamentals](../02-claude-fundamentals/03-prompt-fundamentals.md) into a repeatable
method you can use in the Claude apps and in production code.

All guidance here follows Anthropic's living reference,
[Prompting best practices](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices)
(checked 2026-10-24). Where an API detail matters (thinking, effort, structured outputs), the examples follow the
current rules in [`docs/STYLE.md`](../docs/STYLE.md) section 1.5.

## Learning objectives

By the end of this module you can:

1. Write clear, direct instructions that a capable newcomer could follow without guessing.
2. Separate instructions, context, examples and inputs with XML tags.
3. Choose between zero-shot and few-shot prompting, and build a small, diverse example set.
4. Decide when Claude should reason before answering, and tune that with adaptive thinking and `effort`.
5. Break a complex request into sub-tasks and chain them, with checks between steps.
6. Get machine-readable output with JSON Schema structured outputs, `messages.parse()` and strict tools, and explain why
   assistant prefill is no longer used.
7. Design system prompts, roles, reusable templates and guardrails.
8. Improve a prompt systematically with test cases and small, measured changes.
9. Adapt your strategy to the task type: analysis, research, drafting or brainstorming.

## Page order

| # | Page | What you learn |
|---|---|---|
| 1 | [Clear and direct instructions](01-clear-direct-instructions.md) | The "new colleague" test, context and motivation, task-type strategies |
| 2 | [Structure with XML tags](02-structure-with-xml-tags.md) | Separating instructions from data, nesting documents, tagged output |
| 3 | [Examples and few-shot prompting](03-examples-few-shot.md) | Zero-shot vs few-shot, choosing and formatting examples |
| 4 | [Reasoning and thinking](04-reasoning-and-thinking.md) | Prompted chain of thought, adaptive thinking, the `effort` parameter |
| 5 | [Task decomposition and chaining](05-task-decomposition-and-chaining.md) | Splitting work, sequential and parallel chains, self-correction |
| 6 | [Structured output](06-structured-output.md) | JSON Schema outputs, Pydantic parsing, strict tools, life after prefill |
| 7 | [System prompts and roles](07-system-prompts-and-roles.md) | Roles, templates, variables, guardrails, prompt injection basics |
| 8 | [Iterating on prompts](08-iterating-on-prompts.md) | Test sets, failure analysis, versioning, knowing when to stop |

## Prerequisites

- [Module 01 — AI and LLM fundamentals](../01-ai-and-llm-fundamentals/README.md), especially
  [tokens](../01-ai-and-llm-fundamentals/04-tokens-and-tokenisation.md) and
  [hallucinations](../01-ai-and-llm-fundamentals/06-hallucinations.md).
- [Module 02 — Claude fundamentals](../02-claude-fundamentals/README.md).
- For the code examples: Python 3.10+, the `anthropic` SDK and an API key in an environment variable
  (see [environment setup](../00-getting-started/environment-setup.md)). Every concept can also be practised in the Claude
  apps without code.

## Exam relevance

Objective IDs come from [`16-certification-tracks/registry.yaml`](../16-certification-tracks/registry.yaml).

| Certification | Objectives covered | Where |
|---|---|---|
| CCAO-F | CCAO-F-1.1 Write effective prompts | Pages 1, 2, 3, 7 |
| CCAO-F | CCAO-F-1.2 Decompose complex requests | Page 5 |
| CCAO-F | CCAO-F-1.3 Iterate on prompts | Page 8 |
| CCAO-F | CCAO-F-1.4 Adapt strategy to task type | Pages 1, 4, 5 |
| CCAO-F | CCAO-F-2.6 Choose output formats | Page 6 |
| CCAO-F | CCAO-F-5.3 Write system-level instructions | Page 7 |
| CCAO-F | CCAO-F-7.1, 7.2 Diagnose and fix poor outputs | Page 8 |
| CCAR-P | CCAR-P-2.2 System prompts, templates, guardrails | Page 7 |
| CCAR-P | CCAR-P-2.3 Zero-shot, few-shot, chain of thought | Pages 3, 4 |
| CCAR-P | CCAR-P-1.5 Decomposition techniques | Page 5 |
| CCAR-P | CCAR-P-4.4 Diagnose prompt failure | Page 8 |
| CCAR-P | CCAR-P-5.1 Guardrails and safety controls | Page 7 |

Foundations candidates should be able to apply every technique in the Claude apps. Professional candidates should
also be able to justify the technique in an architecture review and know the API mechanics (structured outputs,
effort, strict tools).

## Hands-on labs

- [Lab 02 — Prompt improvement](../19-hands-on-labs/lab-02-prompt-improvement/README.md): take a weak prompt through
  several measured revisions.
- [Lab 03 — Structured outputs](../19-hands-on-labs/lab-03-structured-outputs/README.md): extract validated JSON with
  `output_config.format` and Pydantic.
- [Lab 16 — Evaluation framework](../19-hands-on-labs/lab-16-evaluation-framework/README.md): build the test harness
  that page 8 describes.

> **Cost:** requires API credits (live mode). All labs run offline in mock mode by default.

## Quick reference

- [Prompt engineering cheat sheet](../22-cheat-sheets/prompt-engineering.md)
- [Troubleshooting prompts and outputs](../24-troubleshooting/prompts-and-outputs.md)

## Next module

Continue to [Module 04 — Context Engineering](../04-context-engineering/README.md), which widens the lens from the
words in one prompt to everything that fills Claude's context window: documents, memory, caching and Skills.
