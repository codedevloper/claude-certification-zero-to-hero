# Module 07: Tool Use and Function Calling

> **Level:** Intermediate · **Time:** ~4 hours including the lab · **Exam relevance:** CCAR-P 3.1, 3.3, 3.8, 5.1, 5.3

Tool use is how Claude stops being a text generator and starts taking actions: looking up a record, running a calculation, searching the web, or calling your internal API. Almost every production Claude system beyond a simple chat or summarisation call uses tools. This module teaches the mechanics first (how a tool call travels between your code, the API and the model), then the design and security judgement that separates a demo from a system you can put in front of customers.

## Learning objectives

By the end of this module you can:

1. Explain the difference between **client tools** (your code runs them) and **server tools** (Anthropic runs them), and choose between them.
2. Write a tool definition with a precise name, description and JSON Schema, and decide when to add `strict: true` and `input_examples`.
3. Implement the tool-use loop by hand and with the SDK Tool Runner, including parallel tool calls, `is_error` results and the `pause_turn` stop reason.
4. Explain why forced `tool_choice` (`any` or `tool`) is rejected on Opus 5.5, Sonnet 5.5, Fable 5.1 and Mythos 5.1 and what to use instead.
5. Configure the web search, web fetch, code execution and tool search server tools, including deferred loading.
6. Apply tool design practices: consolidation, namespacing, high-signal responses and evaluation-driven iteration.
7. Secure a tool surface with least privilege, input validation, confirmation gates and a review for capability bloat.

## Pages in this module

| # | Page | What you learn |
|---|---|---|
| 1 | [Tool use fundamentals](01-tool-use-fundamentals.md) | What a tool is, client versus server tools, the request and response shapes |
| 2 | [Defining tools](02-defining-tools.md) | Names, descriptions, JSON Schema, `strict: true`, `input_examples`, `tool_choice` |
| 3 | [The tool-use loop](03-the-tool-use-loop.md) | Manual loop, Tool Runner, parallel calls, `is_error`, stop reasons |
| 4 | [Server tools](04-server-tools.md) | Web search, web fetch, code execution, tool search and deferred loading |
| 5 | [Tool design best practices](05-tool-design-best-practices.md) | Designing tools for a non-deterministic caller, evaluation-driven iteration |
| 6 | [Tool security](06-tool-security.md) | Least privilege, validation, confirmation gates, capability bloat |

Work through the pages in order, then complete the lab.

## Hands-on lab

- [Lab 08: Tool invocation](../19-hands-on-labs/lab-08-tool-invocation/README.md) builds a small tool-using assistant. It runs offline in mock mode by default (`CLAUDE_LAB_MODE=mock`) and against the real API with `CLAUDE_LAB_MODE=live`.

> **Cost:** requires API credits (live mode).

## Prerequisites

- [Module 03: Prompt engineering](../03-prompt-engineering/README.md), especially [structured output](../03-prompt-engineering/06-structured-output.md) and [system prompts](../03-prompt-engineering/07-system-prompts-and-roles.md).
- [Module 06: Claude API](../06-claude-api/README.md), especially the [Messages API](../06-claude-api/02-messages-api.md) and [streaming](../06-claude-api/03-streaming.md).
- Comfortable reading Python 3.10+ and JSON.

## Exam relevance

Objective IDs come from [`registry.yaml`](../16-certification-tracks/registry.yaml).

| Objective | Where this module helps |
|---|---|
| CCAR-P-3.1 Evaluate tool and agent configuration for capability bloat | Pages 5 and 6: tool count, consolidation, least privilege |
| CCAR-P-3.3 Evaluate accuracy–latency trade-offs | Pages 3 and 4: parallel calls, server-side loops, dynamic filtering, tool search |
| CCAR-P-3.8 Evaluate progressive discovery versus monolithic context | Page 4: tool search and `defer_loading` |
| CCAR-P-5.1 Implement guardrails and safety controls | Page 6: validation, allow-lists, sandboxing |
| CCAR-P-5.3 Apply human-in-the-loop validation | Pages 3 and 6: confirmation gates inside the loop |

For a domain-level view, see the [CCAR-P domain 3 study guide](../16-certification-tracks/ccar-p/study-guide/domain-3.md).

## Key facts to remember (as of 2026-10-24)

- Tool use is a feature of `POST /v1/messages`, not a separate API.
- `tool_choice` of `any` or `tool` returns a 400 on Claude Opus 5.5, Claude Sonnet 5.5 and Claude Fable 5.1. Use `auto` with a clear instruction, `strict: true`, or structured outputs.
- Return every `tool_result` for one assistant turn in a **single** user message, with the `tool_result` blocks first.
- Server tools can end a turn with `stop_reason: "pause_turn"`; resend the assistant content unchanged to continue.

## Next module

Continue to [Module 08: Model Context Protocol](../08-model-context-protocol/README.md), which standardises how tools and data are packaged and shared across applications.
