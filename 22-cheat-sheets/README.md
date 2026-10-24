# 22 · Cheat Sheets

Condensed, printable references for the moments when you need the answer quickly: while building, before an
interview, or in the final week before an exam. Each sheet links back to the module that explains the "why".

> **Dated content.** Model IDs, prices, Claude Code commands and MCP details change often. Every sheet states the date
> it was checked (2026-10-24 for this release) and links to the live official page. If a sheet disagrees with the
> official docs, the docs win; please open an issue (see [CONTRIBUTING](../CONTRIBUTING.md)).

## The sheets

| Sheet | Covers | Best for |
|---|---|---|
| [Claude API](claude-api.md) | Request shape, stop reasons, content blocks, structured outputs, caching, streaming, batches, errors, tool loop | Developers and architects |
| [Prompt engineering](prompt-engineering.md) | Prompt anatomy, techniques, output control on current models, hallucination controls, prompt smells | Everyone |
| [Model selection](model-selection.md) | Current models table with prices and context, price modifiers, decision guide | Architects, budget owners |
| [Claude Code](claude-code.md) | CLI, flags, slash commands, files, settings precedence, permissions, hooks, skills, subagents, MCP | Developers, platform teams |
| [MCP](mcp.md) | Roles, primitives, transports, message shape, authorization, security checklist | Integrators, security reviewers |
| [AI security](ai-security.md) | OWASP LLM Top 10 (2025), injection defences, agent controls, data protection, threat modelling | Security engineers, architects |
| [CCAO-F one-pager](ccao-f-one-pager.md) | Associate exam format, domains, weights, key concepts per objective | CCAO-F candidates |
| [CCAR-F one-pager](ccar-f-one-pager.md) | Architect Foundations exam format, scenarios, domains, weights, key concepts per objective | CCAR-F candidates |
| [CCAR-P one-pager](ccar-p-one-pager.md) | Architect Professional exam format, domains, weights, key concepts per objective | CCAR-P candidates |

Exam facts on the one-pagers come from [`registry.yaml`](../16-certification-tracks/registry.yaml); see also
[exam-facts.md](../25-official-resources/exam-facts.md).

## How to use them

- **While learning:** read the module first, then use the sheet to consolidate. A sheet is a summary, not a
  substitute.
- **While building:** keep the API and Claude Code sheets open; they reflect the current API rules in
  [STYLE.md](../docs/STYLE.md) (no sampling parameters, no prefill, adaptive thinking, `effort`).
- **Before an exam:** read the one-pager for your track, then drill [flashcards](../23-flashcards/README.md) and a
  [mock exam](../18-mock-examinations/README.md).
- **Printing:** each sheet is plain Markdown. Most Markdown viewers print to PDF cleanly; Mermaid diagrams render on
  GitHub.

## Related reference sections

- [21 · Interview preparation](../21-interview-preparation/README.md)
- [23 · Flashcards](../23-flashcards/README.md)
- [24 · Troubleshooting](../24-troubleshooting/README.md)
- [Glossary](../GLOSSARY.md) and [FAQ](../FAQ.md)
