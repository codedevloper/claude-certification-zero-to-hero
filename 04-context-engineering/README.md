# Module 04 — Context Engineering

> **Level:** Intermediate → Advanced · **Time:** ~6 hours (pages) + ~2 hours (labs) · **Exam relevance:** CCAO-F D3, D5 · CCAR-P D2, D3, D4

Prompt engineering asks "what should I write?". Context engineering asks a larger question: "of everything that
*could* be in Claude's context window (instructions, documents, tool definitions, tool results, conversation history,
memories), what is the smallest, most useful set for this step, and how do I keep it that way as the work goes on?"

This module covers the techniques Anthropic documents for that job, as of 2026-10-24: careful placement of long
documents, prompt caching, memory, compaction, context editing and progressive disclosure with Agent Skills. It is the
conceptual foundation for Professional objectives **CCAR-P-2.4** (optimise context windows and token usage),
**CCAR-P-2.5** (reuse prompts via caching, modular prompts and Skills) and **CCAR-P-3.8** (progressive discovery versus
monolithic context).

## Learning objectives

By the end of this module you can:

1. Explain context engineering, the idea of a finite "attention budget", and how it differs from prompt engineering.
2. Structure prompts with long documents for accuracy: placement, document tags and quote-first grounding.
3. Design prompts for caching: stable prefixes, breakpoints, TTL choice, verification and cost estimation.
4. Choose between memory options: Projects memory in the Claude apps and the memory tool in the API.
5. Keep long conversations and agent loops healthy with compaction and context editing.
6. Compare progressive disclosure (Skills, just-in-time retrieval) with monolithic context and justify a choice.

## Page order

| # | Page | What you learn |
|---|---|---|
| 1 | [What is context engineering?](01-what-is-context-engineering.md) | The context window as a budget; the components of context; the core strategies |
| 2 | [Managing long context](02-managing-long-context.md) | Document placement, multi-document structure, quotes-first grounding, when to restart |
| 3 | [Prompt caching](03-prompt-caching.md) | Prefix matching, breakpoints, TTLs, usage fields, silent invalidators, cost maths |
| 4 | [Memory and persistence](04-memory-and-persistence.md) | Apps memory and Projects; the API memory tool; designing what to remember |
| 5 | [Compaction and context editing](05-compaction-and-context-editing.md) | Server-side summarisation, clearing tool results and thinking, when to use which |
| 6 | [Progressive disclosure and Skills](06-progressive-disclosure-and-skills.md) | Agent Skills, just-in-time loading, tool search, monolithic versus progressive context |

## Prerequisites

- [Module 01 — Context windows](../01-ai-and-llm-fundamentals/05-context-windows.md) and
  [tokens](../01-ai-and-llm-fundamentals/04-tokens-and-tokenisation.md).
- [Module 03 — Prompt Engineering](../03-prompt-engineering/README.md), especially
  [XML tags](../03-prompt-engineering/02-structure-with-xml-tags.md) and
  [system prompts](../03-prompt-engineering/07-system-prompts-and-roles.md).
- For pages 3 to 6, it helps to have made a basic API call ([Module 06](../06-claude-api/01-getting-started-with-the-api.md)).

## Exam relevance

Objective IDs come from [`16-certification-tracks/registry.yaml`](../16-certification-tracks/registry.yaml).

| Certification | Objectives covered | Where |
|---|---|---|
| CCAR-P | CCAR-P-2.4 Optimise context windows and token usage | Pages 1, 2, 5 |
| CCAR-P | CCAR-P-2.5 Reuse prompts via caching, modular prompts and Skills | Pages 3, 6 |
| CCAR-P | CCAR-P-3.8 Progressive discovery versus monolithic context | Pages 1, 6 |
| CCAR-P | CCAR-P-4.5 Optimise token usage, latency and cost-performance | Pages 3, 5 |
| CCAR-P | CCAR-P-1.4 Multi-agent systems (context isolation) | Page 1 |
| CCAO-F | CCAO-F-3.4 Manage context limits and memory | Pages 2, 4, 5 |
| CCAO-F | CCAO-F-5.1, 5.4 Configure and maintain Projects | Page 4 |

Foundations candidates should focus on pages 1, 2 and 4 (the apps view: when to restart, summarise or persist).
Professional candidates need all six, including the API mechanics and cost reasoning.

## Hands-on labs

- [Lab 05 — Context management](../19-hands-on-labs/lab-05-context-management/README.md): long-document placement,
  quote-first grounding and compaction in a mock agent loop.
- [Lab 17 — Cost optimisation](../19-hands-on-labs/lab-17-cost-optimisation/README.md): measure the effect of prompt
  caching with the usage fields.
- [Lab 04 — Document-grounded Q&A](../19-hands-on-labs/lab-04-document-grounded-qa/README.md): grounding answers in
  supplied documents.

> **Cost:** requires API credits (live mode). All labs run offline in mock mode by default.

## Related material

- [RAG versus long context](../11-rag-and-knowledge-systems/07-rag-vs-long-context.md)
- [Cost optimisation](../15-production-operations/03-cost-optimisation.md)
- [Claude Code memory and CLAUDE.md](../09-claude-code/03-claude-md-and-memory.md)

## Next module

Continue to [Module 05 — Claude Products and Models](../05-claude-products-and-models/README.md), which covers the
product surfaces (apps, Projects, artifacts, connectors) and how to choose a model.
