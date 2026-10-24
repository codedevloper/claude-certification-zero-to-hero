# OWASP LLM and Agentic Risk Mapping

> **Level:** Advanced · **Time:** ~25 min · **Exam relevance:** CCAR-P D5 (5.1, 5.2), CCAR-P D3 (3.1, 3.2)

This page maps two OWASP GenAI Security Project lists to the pages, labs and projects in this repository. Use it as a
review checklist: for a given design, walk each row, decide whether the risk applies, and follow the links for
controls and tests.

> **Attribution.** The risk identifiers and names below (LLM01–LLM10, ASI01–ASI10) come from the
> [OWASP GenAI Security Project](https://genai.owasp.org), whose Top 10 for LLM Applications is published under
> [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/). Only the identifiers and names are reused; the
> descriptions, controls and mappings on this page are original to this repository. OWASP does not endorse this project.

Both lists were checked on 2026-10-24:

- **OWASP Top 10 for LLM Applications 2025**, from [genai.owasp.org/llm-top-10](https://genai.owasp.org/llm-top-10/).
- **OWASP Top 10 for Agentic Applications for 2026**, published 9 December 2025, from the
  [OWASP GenAI Security Project announcement](https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/).

The descriptions below are short summaries in our own words. Read the OWASP documents for full definitions,
examples and their own mitigation guidance.

## OWASP Top 10 for LLM Applications 2025

| ID | Risk | One-line summary | Primary pages | Labs and projects | Key controls |
|---|---|---|---|---|---|
| LLM01:2025 | Prompt Injection | Input or content alters the model's behaviour against the developer's intent, directly or via third-party content | [Prompt injection](02-prompt-injection.md), [Indirect prompt injection](03-indirect-prompt-injection.md) | [Lab 14](../19-hands-on-labs/lab-14-prompt-injection-testing/README.md), [Project 03](../20-real-world-projects/03-security-alert-triage-assistant/README.md) | Untrusted content in tool results, screening, privilege separation, least-privilege tools |
| LLM02:2025 | Sensitive Information Disclosure | Model exposes personal, confidential or proprietary data | [Data exfiltration and disclosure](04-data-exfiltration-and-disclosure.md), [Secrets management](10-secrets-management.md) | [Lab 15](../19-hands-on-labs/lab-15-sensitive-data-protection/README.md) | Retrieval-time access control, output channel controls, data minimisation, log redaction |
| LLM03:2025 | Supply Chain | Compromised or vulnerable models, packages, plugins, servers or data sources | [Supply-chain risks](07-supply-chain-risks.md), [MCP server security](08-mcp-server-security.md) | [Project 04](../20-real-world-projects/04-devsecops-code-review-assistant/README.md) | Intake review, pinning, SBOM, managed MCP allow-lists, Skill audits |
| LLM04:2025 | Data and Model Poisoning | Manipulated training, fine-tuning, retrieval or eval data changes behaviour | [Supply-chain risks](07-supply-chain-risks.md), [Indirect prompt injection](03-indirect-prompt-injection.md) | [Lab 16](../19-hands-on-labs/lab-16-evaluation-framework/README.md) | Index write controls, ingestion provenance, protected eval sets |
| LLM05:2025 | Improper Output Handling | Model output passed to downstream components without validation or encoding | [Insecure output handling](06-insecure-output-handling.md) | [Project 04](../20-real-world-projects/04-devsecops-code-review-assistant/README.md) | Structured outputs, parameterised queries, encoding, sandboxing, `stop_reason` checks |
| LLM06:2025 | Excessive Agency | Too much functionality, permission or autonomy | [Tool misuse and excessive agency](05-tool-misuse-and-excessive-agency.md), [Agent identity and permissions](09-agent-identity-and-permissions.md), [Human oversight](13-human-oversight.md) | [Lab 13](../19-hands-on-labs/lab-13-human-in-the-loop/README.md), [Lab 20](../19-hands-on-labs/lab-20-secure-enterprise-architecture/README.md), [Project 05](../20-real-world-projects/05-agentic-investigation-assistant/README.md) | Narrow tools, policy enforcement point, delegated tokens, risk-tiered approval |
| LLM07:2025 | System Prompt Leakage | System prompts reveal secrets or control logic | [Prompt injection](02-prompt-injection.md), [Data exfiltration and disclosure](04-data-exfiltration-and-disclosure.md), [Secrets management](10-secrets-management.md) | [Lab 14](../19-hands-on-labs/lab-14-prompt-injection-testing/README.md) | No secrets in prompts; enforcement outside the prompt |
| LLM08:2025 | Vector and Embedding Weaknesses | Weaknesses in how embeddings and vector stores are built, accessed and used, including leakage and poisoning | [Data exfiltration and disclosure](04-data-exfiltration-and-disclosure.md), [Indirect prompt injection](03-indirect-prompt-injection.md) | [Lab 11](../19-hands-on-labs/lab-11-rag-pipeline/README.md), [Project 02](../20-real-world-projects/02-knowledge-base-qa-assistant/README.md) | Per-tenant indexes, ACL filters at query time, ingestion review |
| LLM09:2025 | Misinformation | Confident but false or misleading output that people rely on | [Human oversight](13-human-oversight.md); [hallucinations](../01-ai-and-llm-fundamentals/06-hallucinations.md); [grounding and citations](../11-rag-and-knowledge-systems/05-grounding-and-citations.md) | [Lab 04](../19-hands-on-labs/lab-04-document-grounded-qa/README.md), [Lab 16](../19-hands-on-labs/lab-16-evaluation-framework/README.md) | Grounding with citations, evals for faithfulness, review for high-stakes outputs |
| LLM10:2025 | Unbounded Consumption | Uncontrolled resource use leading to denial of service, cost blow-out or model extraction | [Tool misuse and excessive agency](05-tool-misuse-and-excessive-agency.md); [rate limits and capacity](../15-production-operations/06-rate-limits-and-capacity.md); [cost optimisation](../15-production-operations/03-cost-optimisation.md) | [Lab 17](../19-hands-on-labs/lab-17-cost-optimisation/README.md), [Lab 18](../19-hands-on-labs/lab-18-reliability-engineering/README.md) | Input size limits, iteration caps, task budgets, per-user quotas, spend limits |

## OWASP Top 10 for Agentic Applications for 2026

The entry names below are as listed on the OWASP GenAI Security Project's announcement of the list.

| ID | Risk | One-line summary | Primary pages | Labs and projects |
|---|---|---|---|---|
| ASI01 | Agent Goal Hijack | Content the agent reads redirects its objective or decision path | [Indirect prompt injection](03-indirect-prompt-injection.md), [Prompt injection](02-prompt-injection.md) | [Lab 14](../19-hands-on-labs/lab-14-prompt-injection-testing/README.md) |
| ASI02 | Tool Misuse | Legitimate tools used in unintended or unsafe ways | [Tool misuse and excessive agency](05-tool-misuse-and-excessive-agency.md) | [Lab 20](../19-hands-on-labs/lab-20-secure-enterprise-architecture/README.md), [Project 05](../20-real-world-projects/05-agentic-investigation-assistant/README.md) |
| ASI03 | Identity and Privilege Abuse | Agents act with shared, inherited or excessive identities and privileges | [Agent identity and permissions](09-agent-identity-and-permissions.md), [Secrets management](10-secrets-management.md) | [Lab 20](../19-hands-on-labs/lab-20-secure-enterprise-architecture/README.md) |
| ASI04 | Agentic Supply Chain Vulnerabilities | Compromised tools, MCP servers, Skills, plugins or agent components | [Supply-chain risks](07-supply-chain-risks.md), [MCP server security](08-mcp-server-security.md) | [Lab 09](../19-hands-on-labs/lab-09-mcp-fundamentals/README.md) |
| ASI05 | Unexpected Code Execution | Agents generate or run code that leads to unintended execution | [Insecure output handling](06-insecure-output-handling.md), [Tool misuse and excessive agency](05-tool-misuse-and-excessive-agency.md) | [Lab 10](../19-hands-on-labs/lab-10-claude-code-workflows/README.md) |
| ASI06 | Memory and Context Poisoning | Persistent memory or context is seeded with malicious or false content | [Indirect prompt injection](03-indirect-prompt-injection.md); [memory and persistence](../04-context-engineering/04-memory-and-persistence.md) | [Lab 05](../19-hands-on-labs/lab-05-context-management/README.md) |
| ASI07 | Insecure Inter-Agent Communication | Messages between agents are spoofed, tampered with or trusted blindly | [LLM threat modelling](01-llm-threat-modelling.md), [Agent identity and permissions](09-agent-identity-and-permissions.md); [multi-agent architecture](../10-agentic-ai/04-multi-agent-architecture.md) | [Lab 12](../19-hands-on-labs/lab-12-agentic-task-execution/README.md) |
| ASI08 | Cascading Failures | An error or compromise in one agent or step propagates through a system | [Logging and auditability](11-logging-and-auditability.md); [reliability engineering](../15-production-operations/05-reliability-engineering.md); [agent reliability](../10-agentic-ai/07-agent-reliability.md) | [Lab 18](../19-hands-on-labs/lab-18-reliability-engineering/README.md) |
| ASI09 | Human-Agent Trust Exploitation | Humans over-trust agents, or agents (or attackers via agents) exploit that trust | [Human oversight](13-human-oversight.md) | [Lab 13](../19-hands-on-labs/lab-13-human-in-the-loop/README.md) |
| ASI10 | Rogue Agents | Agents that deviate from intended behaviour or operate outside authorised scope | [Tool misuse and excessive agency](05-tool-misuse-and-excessive-agency.md), [Logging and auditability](11-logging-and-auditability.md), [Enterprise deployment controls](14-enterprise-deployment-controls.md) | [Project 05](../20-real-world-projects/05-agentic-investigation-assistant/README.md) |

> **Unverified:** The one-line summaries for ASI05 to ASI10 are our interpretation of the entry names. We confirmed
> the IDs and names on the OWASP announcement but did not review the full downloadable document for each entry's
> definition. Read the OWASP document before citing these summaries.

## Cross-reference: STRIDE to OWASP

If you threat-model with STRIDE ([page 1](01-llm-threat-modelling.md)), this table helps you tag findings with OWASP
IDs for reporting.

| STRIDE | Most relevant OWASP entries |
|---|---|
| Spoofing | LLM01, ASI01, ASI03, ASI07 |
| Tampering | LLM03, LLM04, LLM08, ASI04, ASI06 |
| Repudiation | ASI08, ASI10 (both depend on audit trails) |
| Information disclosure | LLM02, LLM07, LLM08 |
| Denial of service | LLM10, ASI08 |
| Elevation of privilege | LLM05, LLM06, ASI02, ASI03, ASI05 |

## How to use this mapping in a review

1. Draw the data-flow diagram and mark untrusted content flows (page 1).
2. For each row above, answer: does this risk apply? If not, record why.
3. For applicable risks, list the controls present and missing, using the linked pages.
4. For each control, name the test that proves it: a lab-style harness test, an eval case
   ([safety and red-team evals](../14-evaluation-and-testing/07-safety-and-red-team-evals.md)) or a log-based
   detection.
5. Record residual risk and the owner who accepts it ([AI governance](12-ai-governance.md)).

## Further reading

- OWASP GenAI Security Project: [LLM Top 10](https://genai.owasp.org/llm-top-10/)
- OWASP GenAI Security Project: [Top 10 for Agentic Applications for 2026](https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/)
- Anthropic: [Mitigate jailbreaks and prompt injections](https://platform.claude.com/docs/en/test-and-evaluate/strengthen-guardrails/mitigate-jailbreaks)
- In this repository: [AI security cheat sheet](../22-cheat-sheets/ai-security.md),
  [interview security questions](../21-interview-preparation/security-questions.md)
