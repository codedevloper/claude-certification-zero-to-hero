# Module 13: Enterprise AI Architecture

> **Level:** Advanced · **Time:** ~6 hours (pages) plus ~3 hours (lab and project) · **Exam relevance:** CCAR-P D1, CCAR-P D6, CCAR-P 5.4

This module is where the individual skills from the earlier modules (prompting, tools, MCP, agents, retrieval, security) come together into
systems that an organisation can approve, run, pay for and improve. It is written for solution architects, enterprise architects, technical
leads and security engineers who have to take a Claude idea from a whiteboard to a production service and keep it healthy afterwards.

## Learning objectives

By the end of this module you can:

1. Run a structured discovery, design and delivery process for a Claude solution and turn a business problem into a scoped design.
2. Choose between single-call, workflow, agentic and augmented-LLM patterns, and justify the choice in writing.
3. Draw and explain reference architectures for an AI gateway, a retrieval-augmented generation (RAG) service, an agent platform and a multi-tenant SaaS design.
4. Pick an integration style (synchronous, streaming, asynchronous, batch, event-driven) and a delivery platform (Claude API, Claude Platform on AWS, Amazon Bedrock, Google Cloud Vertex AI, Microsoft Foundry) for a given workload.
5. Explain what GDPR, HIPAA and FedRAMP ask of an architecture, and check which Claude offerings carry which attestations using Anthropic's own trust and privacy pages.
6. Communicate trade-offs to executives, risk owners and engineers, and record decisions as architecture decision records (ADRs).
7. Build a defensible business case: baseline, value levers, cost model, service level objectives and a measurement plan.
8. Manage the solution lifecycle from discovery through design, handoff, monitoring and iteration, including model upgrades.

## Page order

| # | Page | What you learn |
|---|---|---|
| 1 | [Solution design process](01-solution-design-process.md) | Discovery, design and delivery phases, with the artefacts each one produces |
| 2 | [Architecture patterns](02-architecture-patterns.md) | The pattern ladder from a single call to multi-agent systems, and the cross-cutting patterns around it |
| 3 | [Reference architectures](03-reference-architectures.md) | Mermaid diagrams for a gateway, RAG, an agent platform and multi-tenant designs |
| 4 | [Integration patterns](04-integration-patterns.md) | Sync, streaming, async, batch, event-driven and the cloud platforms |
| 5 | [Data governance and compliance](05-data-governance-and-compliance.md) | GDPR, HIPAA and FedRAMP obligations, and verified Claude attestations |
| 6 | [Stakeholder communication](06-stakeholder-communication.md) | Explaining trade-offs, setting expectations and managing feedback loops |
| 7 | [Architecture decision records](07-architecture-decision-records.md) | An ADR template and two worked ADRs |
| 8 | [Business value and ROI](08-business-value-and-roi.md) | Value levers, cost models, SLAs and a worked return-on-investment calculation |
| 9 | [Lifecycle management](09-lifecycle-management.md) | Discovery, design, handoff, monitoring and iteration in practice |

## Prerequisites

- [Module 10: Agentic AI](../10-agentic-ai/README.md), especially [workflows versus agents](../10-agentic-ai/01-workflows-vs-agents.md) and [multi-agent architecture](../10-agentic-ai/04-multi-agent-architecture.md).
- [Module 11: RAG and knowledge systems](../11-rag-and-knowledge-systems/README.md).
- [Module 12: AI security](../12-ai-security/README.md), in particular [enterprise deployment controls](../12-ai-security/14-enterprise-deployment-controls.md) and [AI governance](../12-ai-security/12-ai-governance.md).
- Helpful but optional: [cloud platforms](../06-claude-api/07-cloud-platforms.md) and [production readiness](../15-production-operations/01-production-readiness.md).

## Exam relevance

This module is the main study source for two Claude Certified Architect – Professional (CCAR-P) domains and one objective from a third.
Domain weights and objective wording come from [`registry.yaml`](../16-certification-tracks/registry.yaml); see also
[exam facts](../25-official-resources/exam-facts.md).

| Objective | Short description | Main pages |
|---|---|---|
| CCAR-P-1.1 | Translate business problems into Claude-based solutions | 01, 08 |
| CCAR-P-1.2 | Design end-to-end architectures (input, processing, output, feedback loops) | 02, 03, 04 |
| CCAR-P-1.3 | Select architectural patterns (workflow, agentic, augmented LLM) | 02 |
| CCAR-P-1.4 | Design multi-agent systems and orchestration strategies | 02, 03 |
| CCAR-P-1.5 | Apply decomposition techniques to complex problems | 01, 02 |
| CCAR-P-1.6 | Align solutions to business value (efficiency, transformation, productivity, cost, SLAs) | 08 |
| CCAR-P-5.4 | Ensure regulatory compliance (e.g. GDPR, HIPAA, FedRAMP) | 05 |
| CCAR-P-6.1 | Run structured discovery and requirements gathering | 01, 09 |
| CCAR-P-6.2 | Communicate architectural decisions and trade-offs | 06, 07 |
| CCAR-P-6.3 | Manage stakeholder feedback loops and expectations, including SLAs | 06, 08 |
| CCAR-P-6.4 | Document architectures and give implementation guidance | 03, 07, 09 |
| CCAR-P-6.5 | Support lifecycle phases (discovery, design, handoff, monitoring, iteration) | 09 |

The study guides at [`ccar-p/study-guide/domain-1.md`](../16-certification-tracks/ccar-p/study-guide/domain-1.md) and
[`ccar-p/study-guide/domain-6.md`](../16-certification-tracks/ccar-p/study-guide/domain-6.md) map these objectives back to this module.

## Hands-on practice

- [Lab 20: Secure enterprise architecture](../19-hands-on-labs/lab-20-secure-enterprise-architecture/README.md) is the capstone lab for this module.
- [Lab 13: Human in the loop](../19-hands-on-labs/lab-13-human-in-the-loop/README.md) practises the approval gates that most enterprise designs need.
- [Lab 11: RAG pipeline](../19-hands-on-labs/lab-11-rag-pipeline/README.md) and [Lab 12: Agentic task execution](../19-hands-on-labs/lab-12-agentic-task-execution/README.md) build the components that the reference architectures assume.
- [Real-world projects](../20-real-world-projects/README.md): treat any of them as an architecture exercise. Write the discovery brief, two ADRs and a business case before you read the code.
  - [Document summarisation assistant](../20-real-world-projects/01-document-summarisation-assistant/README.md)
  - [Knowledge base Q&A assistant](../20-real-world-projects/02-knowledge-base-qa-assistant/README.md)
  - [Security alert triage assistant](../20-real-world-projects/03-security-alert-triage-assistant/README.md)
  - [DevSecOps code review assistant](../20-real-world-projects/04-devsecops-code-review-assistant/README.md)
  - [Agentic investigation assistant](../20-real-world-projects/05-agentic-investigation-assistant/README.md)

## How to study this module

Read pages 1 and 2 first, because every later page assumes their vocabulary. Then read pages 3 and 4 together with a whiteboard: redraw
each diagram from memory for a different fictional organisation. Page 5 is dense; read it once for the concepts and again when you need a
compliance answer, and always re-check the linked official pages, because attestations change. Pages 6 to 9 are about people and time.
They are short on code and long on judgement, which is exactly what scenario questions test.

## Next module

Continue to [Module 14: Evaluation and testing](../14-evaluation-and-testing/README.md), which turns the success criteria you defined
here into measurable evaluations.
