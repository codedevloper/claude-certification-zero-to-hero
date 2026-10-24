# Module 12: AI Security

> **Level:** Advanced · **Time:** ~10 hours (pages) + ~6 hours (labs) · **Exam relevance:** CCAR-P D5 (5.1, 5.2, 5.3, 5.4), CCAR-P D3 (3.1, 3.2, 3.4), CCAO-F D6 (6.2, 6.3)

This is the dedicated AI security track and the deepest module in the repository. It is written for security
engineers, DevSecOps practitioners and architects who have to answer one question before a Claude-based system
goes live: *what can go wrong, and which controls make it acceptable?*

The module is defensive throughout. It shows how attacks work at the level of detail you need to design and test
controls, and it gives you concrete architecture patterns, policy settings and Python code. It does not contain
working attack payloads against real systems. Every injection string in this module is illustrative and aimed at
your own test harness.

## Learning objectives

By the end of this module you can:

1. Build a threat model for an LLM application: draw its data-flow diagram, mark trust boundaries and apply STRIDE
   to each element, including the model, tools, retrieval stores and agents.
2. Explain direct and indirect prompt injection, why neither can be fully "patched" in the model, and which
   architectural controls contain the impact.
3. Design controls against sensitive information disclosure and data exfiltration, including markdown-image, link
   and tool-based exfiltration channels.
4. Limit excessive agency through least-privilege tools, scoped credentials, confirmation gates and sandboxing.
5. Treat model output as untrusted input in every downstream sink (HTML, SQL, shell, templates, other agents).
6. Assess supply-chain risk across models, MCP servers, packages, prompts and Skills, and run an intake process.
7. Secure MCP servers and clients against confused-deputy, token-passthrough, SSRF and session-hijack attacks.
8. Give agents their own non-human identities with scoped, short-lived, delegated credentials.
9. Keep secrets out of prompts, context, logs and model reach.
10. Design logging that supports audit and incident response without creating a new data-leak channel.
11. Map your programme to NIST AI RMF 1.0, NIST AI 600-1, ISO/IEC 42001 and the EU AI Act at a level an architect
    needs.
12. Choose human-oversight patterns proportionate to risk, and configure enterprise deployment controls
    (SSO/SCIM, retention, network controls, admin settings) that Anthropic actually offers.

## Page order

| # | Page | What you get |
|---|---|---|
| 1 | [LLM threat modelling](01-llm-threat-modelling.md) | STRIDE for LLM apps, trust boundaries, Mermaid data-flow diagrams |
| 2 | [Prompt injection](02-prompt-injection.md) | Direct injection and jailbreaks, layered defences, screening code |
| 3 | [Indirect prompt injection](03-indirect-prompt-injection.md) | Injection through documents, web pages, email and tool results |
| 4 | [Data exfiltration and disclosure](04-data-exfiltration-and-disclosure.md) | Markdown-image, link and tool exfiltration; system prompt leakage |
| 5 | [Tool misuse and excessive agency](05-tool-misuse-and-excessive-agency.md) | Least agency, policy enforcement points, confirmation gates |
| 6 | [Insecure output handling](06-insecure-output-handling.md) | Encoding, validation and sandboxing for every output sink |
| 7 | [Supply-chain risks](07-supply-chain-risks.md) | Models, MCP servers, packages, prompts and Skills |
| 8 | [MCP server security](08-mcp-server-security.md) | Authorization, confused deputy, token passthrough, SSRF, local servers |
| 9 | [Agent identity and permissions](09-agent-identity-and-permissions.md) | Non-human identities, scoped tokens, delegation |
| 10 | [Secrets management](10-secrets-management.md) | Keeping credentials out of model reach |
| 11 | [Logging and auditability](11-logging-and-auditability.md) | What to log, how to protect logs, audit trails for agents |
| 12 | [AI governance](12-ai-governance.md) | NIST AI RMF, NIST AI 600-1, ISO/IEC 42001, EU AI Act |
| 13 | [Human oversight](13-human-oversight.md) | Risk-tiered review, approval UX, automation bias |
| 14 | [Enterprise deployment controls](14-enterprise-deployment-controls.md) | SSO/SCIM, retention and ZDR, network controls, admin settings |
| - | [OWASP LLM mapping](owasp-llm-mapping.md) | OWASP Top 10 for LLM Applications 2025 and Agentic Top 10 mapped to pages and labs |

Read pages 1 to 6 in order: they build one threat model and its core controls. Pages 7 to 14 can be read in any
order once you have that foundation. Use the OWASP mapping as a checklist when you review a real design.

## Prerequisites

- [Module 07: Tool use and function calling](../07-tool-use-and-function-calling/README.md), especially
  [tool security](../07-tool-use-and-function-calling/06-tool-security.md).
- [Module 08: Model Context Protocol](../08-model-context-protocol/README.md), especially
  [MCP security](../08-model-context-protocol/05-mcp-security.md).
- [Module 10: Agentic AI](../10-agentic-ai/README.md), especially
  [human in the loop](../10-agentic-ai/05-human-in-the-loop.md).
- Helpful: [Module 11: RAG](../11-rag-and-knowledge-systems/README.md) for the retrieval-specific threats, and basic
  application security knowledge (OWASP Top 10 for web, OAuth 2.0, least privilege).

## Hands-on labs and projects

| Lab / project | Pages it exercises |
|---|---|
| [Lab 14: prompt injection testing](../19-hands-on-labs/lab-14-prompt-injection-testing/README.md) | 2, 3, 5 |
| [Lab 15: sensitive data protection](../19-hands-on-labs/lab-15-sensitive-data-protection/README.md) | 4, 10, 11 |
| [Lab 20: secure enterprise architecture](../19-hands-on-labs/lab-20-secure-enterprise-architecture/README.md) | 1, 5, 8, 9, 14 |
| [Project 03: security alert triage assistant](../20-real-world-projects/03-security-alert-triage-assistant/README.md) | 3, 5, 6, 11, 13 |
| [Project 04: DevSecOps code review assistant](../20-real-world-projects/04-devsecops-code-review-assistant/README.md) | 6, 7, 10 |
| [Project 05: agentic investigation assistant](../20-real-world-projects/05-agentic-investigation-assistant/README.md) | 5, 9, 11, 13 |

## Exam relevance

| Objective | Where it is covered |
|---|---|
| CCAR-P-5.1 Implement guardrails and safety controls | Pages 2, 3, 5, 6, 13 |
| CCAR-P-5.2 Identify risks, limitations and failure modes | Pages 1, 4, 7, owasp-llm-mapping |
| CCAR-P-5.3 Apply human-in-the-loop validation | Page 13 |
| CCAR-P-5.4 Ensure regulatory compliance | Pages 12, 14 |
| CCAR-P-3.1 Evaluate tool and agent configuration for capability bloat | Pages 5, 8 |
| CCAR-P-3.2 Analyse authentication and authorisation to find security gaps | Pages 8, 9, 10 |
| CCAR-P-3.4 Observability at scale | Page 11 |
| CCAO-F-6.2 Data-sensitivity, regulatory and privacy considerations | Pages 4, 12, 14 |
| CCAO-F-6.3 Organisational AI policy and governance | Pages 12, 13, 14 |

Domain names, weights and objective wording come from
[`16-certification-tracks/registry.yaml`](../16-certification-tracks/registry.yaml). See the
[CCAR-P Domain 5 study guide](../16-certification-tracks/ccar-p/study-guide/domain-5.md) for exam-focused revision and the
[AI security cheat sheet](../22-cheat-sheets/ai-security.md) for a one-page summary.

## How to use this module as a security reviewer

1. Start every review with page 1. Draw the data-flow diagram before reading any code.
2. Walk the [OWASP mapping](owasp-llm-mapping.md) against the diagram and record which risks apply.
3. For each applicable risk, check the "Security considerations" and "Common mistakes" sections of the matching page.
4. Turn findings into tests using Lab 14 and Lab 15 as templates, and into evals using
   [Module 14: safety and red-team evals](../14-evaluation-and-testing/07-safety-and-red-team-evals.md).

## Next module

Continue to [Module 13: Enterprise AI architecture](../13-enterprise-ai-architecture/README.md), which places these
controls inside complete reference architectures.
