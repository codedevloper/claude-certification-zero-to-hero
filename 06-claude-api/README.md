# Module 06 — The Claude API

> **Level:** Beginner → Advanced · **Time:** ~7 hours (pages) + ~3 hours (labs) · **Exam relevance:** CCAR-P D1, D2, D3, D4 · CCAO-F D3

This module takes you from your first authenticated request to production-grade API usage: the Messages API and its
content blocks, streaming, images and PDFs, the Files API and citations, batch processing, error handling and retries,
the cloud platforms that also serve Claude, and how to count tokens and estimate cost.

Every example follows the current API rules in [`docs/STYLE.md`](../docs/STYLE.md) section 1.5 and the official
[Claude API documentation](https://platform.claude.com/docs) as of 2026-10-24: model IDs without date suffixes
(`claude-opus-5-5` by default), no `temperature` / `top_p` / `top_k`, no assistant prefill, adaptive thinking tuned
with `effort`, and a `stop_reason` check before using any output. Python comes first; cURL appears where it helps you
see the raw HTTP shape.

## Learning objectives

By the end of this module you can:

1. Set up a Console account, create and protect an API key, and install the Python SDK.
2. Build Messages API requests with roles, system prompts and content blocks, and handle every stop reason, including
   refusals.
3. Stream responses and choose between the streaming helpers.
4. Send images and PDFs, reuse files with the Files API, and get verifiable citations.
5. Process large workloads asynchronously with the Message Batches API.
6. Handle errors with a typed exception chain, respect rate limits and design retries.
7. Explain the cloud platform options (Claude Platform on AWS, Amazon Bedrock, Google Vertex AI, Microsoft Foundry)
   and their client classes.
8. Count tokens, read the usage object and estimate cost.

## Page order

| # | Page | What you learn |
|---|---|---|
| 1 | [Getting started with the API](01-getting-started-with-the-api.md) | Console, workspaces, API keys in environment variables, SDK install, first request |
| 2 | [The Messages API](02-messages-api.md) | Request anatomy, roles, content blocks, stop reasons, refusals, effort, multi-turn |
| 3 | [Streaming](03-streaming.md) | Server-sent events, SDK helpers, long outputs, handling stream errors |
| 4 | [Vision, documents and citations](04-vision-documents-and-citations.md) | Images, PDFs, the Files API, the citations feature |
| 5 | [Batch processing](05-batch-processing.md) | The Message Batches API, limits, result handling, cost |
| 6 | [Errors, rate limits and retries](06-errors-rate-limits-retries.md) | HTTP errors, typed exceptions, rate-limit headers, backoff |
| 7 | [Cloud platforms](07-cloud-platforms.md) | Claude Platform on AWS, Bedrock, Vertex AI, Foundry; client classes and feature differences |
| 8 | [Token counting and cost](08-token-counting-and-cost.md) | `count_tokens`, usage fields, pricing levers, cost estimation |

## Prerequisites

- [Module 01 — Tokens](../01-ai-and-llm-fundamentals/04-tokens-and-tokenisation.md) and
  [context windows](../01-ai-and-llm-fundamentals/05-context-windows.md).
- [Module 03 — Prompt Engineering](../03-prompt-engineering/README.md); the API pages assume you can write a good
  prompt.
- Python 3.10+ and basic command-line skills. [Environment setup](../00-getting-started/environment-setup.md) walks
  through creating a virtual environment.
- An Anthropic Console account for live calls. Every lab also runs offline in mock mode.

## Exam relevance

Objective IDs come from [`16-certification-tracks/registry.yaml`](../16-certification-tracks/registry.yaml). The
Professional exam is architecture-focused: it tests whether you can choose and justify API features, not whether you
remember method names. Foundations candidates mainly need page 1 (what the API is) and the cost concepts on page 8.

| Certification | Objectives covered | Where |
|---|---|---|
| CCAR-P | CCAR-P-1.2 Design end-to-end architectures | Pages 2, 5, 7 |
| CCAR-P | CCAR-P-2.1 Select models based on trade-offs | Pages 2, 8 |
| CCAR-P | CCAR-P-2.4 Optimise context windows and token usage | Pages 4, 8 |
| CCAR-P | CCAR-P-3.2 Analyse authentication and authorisation | Pages 1, 7 |
| CCAR-P | CCAR-P-3.3 Accuracy–latency trade-offs | Pages 2, 3, 5 |
| CCAR-P | CCAR-P-3.4 Observability at scale | Pages 6, 8 |
| CCAR-P | CCAR-P-3.7 Choose the integration mechanism | Pages 1, 7 |
| CCAR-P | CCAR-P-4.5 Optimise token usage, latency and cost | Pages 5, 8 |
| CCAR-P | CCAR-P-5.4 Regulatory compliance (data residency, platform choice) | Page 7 |
| CCAR-P | CCAR-P-7.3 Debugging and operational issue resolution | Page 6 |
| CCAO-F | CCAO-F-3.3 Match model choice to cost, speed and quality | Page 8 |

## Hands-on labs

- [Lab 01 — First Claude interaction](../19-hands-on-labs/lab-01-first-claude-interaction/README.md)
- [Lab 03 — Structured outputs](../19-hands-on-labs/lab-03-structured-outputs/README.md)
- [Lab 04 — Document-grounded Q&A](../19-hands-on-labs/lab-04-document-grounded-qa/README.md)
- [Lab 07 — API integration](../19-hands-on-labs/lab-07-api-integration/README.md): streaming, error handling and
  retries in one small service.
- [Lab 17 — Cost optimisation](../19-hands-on-labs/lab-17-cost-optimisation/README.md): token counting, caching and
  batch pricing.
- [Lab 18 — Reliability engineering](../19-hands-on-labs/lab-18-reliability-engineering/README.md)

> **Cost:** requires API credits (live mode). All labs run offline in mock mode by default.

## Quick reference

- [Claude API cheat sheet](../22-cheat-sheets/claude-api.md)
- [Troubleshooting API errors](../24-troubleshooting/api-errors.md)

## Next module

Continue to [Module 07 — Tool Use and Function Calling](../07-tool-use-and-function-calling/README.md), where Claude
starts calling your code.
