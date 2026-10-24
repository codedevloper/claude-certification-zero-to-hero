# CCAR-P Readiness Assessment

> A self-assessment against every CCAR-P objective in [`registry.yaml`](../registry.yaml), with readiness
> criteria and remediation paths. Take it at the start of your preparation and again in the final week.

> **Important:** nothing in this repository produces an official score. Practice-question percentages,
> mock-exam results and the self-ratings below are **unofficial indicators only and do not equal the scaled
> score** (100–1,000, pass at 720) reported by the real exam. Scaled scores are produced by the official exam's
> own psychometric process and cannot be derived from a raw percentage on our materials.

## How to rate yourself

For each objective, give yourself a score from 0 to 3:

| Score | Meaning |
|---|---|
| 0 | I could not explain this to a colleague |
| 1 | I recognise the terms but could not make a design decision |
| 2 | I can choose between options and justify the choice for a typical scenario |
| 3 | I have done this in practice or in the labs, and can handle edge cases and explain trade-offs to stakeholders |

Be honest: a 2 means you could defend the decision in a design review.

## Self-assessment by objective

### Domain 1 — Solution Design & Architecture (17%)

| ID | Can I... | Score |
|---|---|---|
| CCAR-P-1.1 | Turn a vague business request into a value hypothesis, decide whether an LLM is the right tool, and apply the four agent criteria? | |
| CCAR-P-1.2 | Draw an end-to-end architecture with input controls, processing, output gates and a feedback loop? | |
| CCAR-P-1.3 | Choose between a single call, each workflow pattern and an agent, and justify it? | |
| CCAR-P-1.4 | Design an orchestrator–workers system with scoped tools, budgets, condensed hand-offs and tracing? | |
| CCAR-P-1.5 | Decompose a complex problem by function, data, time, risk and verification? | |
| CCAR-P-1.6 | Build a cost-per-completed-task business case with SLAs and sensitivity ranges? | |

### Domain 2 — Claude Models, Prompting & Context Engineering (13%)

| ID | Can I... | Score |
|---|---|---|
| CCAR-P-2.1 | Pick model tier and effort per route from eval evidence, and state current model IDs and request rules? | |
| CCAR-P-2.2 | Write a structured system prompt and a layered guardrail design, without relying on prefill or sampling parameters? | |
| CCAR-P-2.3 | Decide when to use zero-shot, few-shot or reasoning, and how adaptive thinking and effort change that? | |
| CCAR-P-2.4 | Produce a context budget and choose among compaction, context editing, sub-agents and retrieval? | |
| CCAR-P-2.5 | Lay out a cache-friendly prompt, list silent invalidators, and decide when to use Skills or modular prompts? | |

### Domain 3 — Integration (19%)

| ID | Can I... | Score |
|---|---|---|
| CCAR-P-3.1 | Audit an agent's tools for bloat and redesign them as narrow, strict, read/write-separated tools? | |
| CCAR-P-3.2 | Find identity and authorisation gaps (shared credentials, token passthrough, missing ACL filters)? | |
| CCAR-P-3.3 | Justify a configuration with eval accuracy, latency percentiles and cost against an SLO? | |
| CCAR-P-3.4 | Specify tracing, metrics, redaction and sampling for an agent at high volume? | |
| CCAR-P-3.5 | Choose chunking and indexing for different document types with metadata and ACLs? | |
| CCAR-P-3.6 | Match retrieval strategy (dense, hybrid, query tools, agentic, long context, live API) to data and queries? | |
| CCAR-P-3.7 | Choose between direct tools, CLI, MCP and agent-to-agent for a given consumer and trust boundary? | |
| CCAR-P-3.8 | Decide between monolithic context and progressive discovery, and configure tool search correctly? | |

### Domain 4 — Evaluation, Testing & Optimization (16%)

| ID | Can I... | Score |
|---|---|---|
| CCAR-P-4.1 | Define primary, secondary and guardrail metrics across accuracy, latency, cost, safety and security? | |
| CCAR-P-4.2 | Design a stratified, versioned dataset with splits and a calibrated mixed-method grading approach? | |
| CCAR-P-4.3 | Plan shadow, canary and A/B rollouts with pre-registered metrics and rollback triggers? | |
| CCAR-P-4.4 | Distinguish prompt failure, retrieval failure, hallucination type and model mismatch with specific diagnostics? | |
| CCAR-P-4.5 | Apply cost and latency levers in the right order and prove the result? | |
| CCAR-P-4.6 | Specify what to log per call and which dashboards and alerts to build? | |

### Domain 5 — Governance, Safety & Risk Management (14%)

| ID | Can I... | Score |
|---|---|---|
| CCAR-P-5.1 | Design layered guardrails where enforcement does not depend on the model complying? | |
| CCAR-P-5.2 | Threat-model an LLM system and list its failure modes with controls? | |
| CCAR-P-5.3 | Choose the oversight level by impact, reversibility and confidence, and design effective review? | |
| CCAR-P-5.4 | Map GDPR, HIPAA and FedRAMP obligations to architecture controls and evidence? | |
| CCAR-P-5.5 | Plan bias testing (slices, counterfactuals) and transparency measures? | |

### Domain 6 — Stakeholder Communication & Lifecycle Management (14%)

| ID | Can I... | Score |
|---|---|---|
| CCAR-P-6.1 | Run discovery across value, users, data, risk, quality and non-functionals? | |
| CCAR-P-6.2 | Present options with consequences to executives, risk teams and engineers, and write an ADR? | |
| CCAR-P-6.3 | Agree SLOs for availability, latency, quality and cost, and run feedback loops? | |
| CCAR-P-6.4 | Assemble a complete handover pack and implementation guide? | |
| CCAR-P-6.5 | Lead a solution through handoff, monitoring, iteration, model migration and retirement? | |

### Domain 7 — Developer Productivity & Operational Enablement (7%)

| ID | Can I... | Score |
|---|---|---|
| CCAR-P-7.1 | Configure Claude Code for a team with correct settings precedence, permissions, hooks, CLAUDE.md and MCP? | |
| CCAR-P-7.2 | Choose among CLAUDE.md, Skills, subagents, hooks, plugins, headless mode and the Agent SDK for a workflow? | |
| CCAR-P-7.3 | Use Claude for incident investigation and debug common Claude API and Claude Code problems? | |

## Readiness criteria

You are likely ready to book (or keep) your exam date when **all** of the following hold:

1. **Self-assessment:** no objective scored 0; no more than three objectives scored 1; every objective in
   Domains 1, 3 and 4 (52% of the exam) scored 2 or higher.
2. **Practice questions:** consistently at or above 80% on the CCAR-P
   [practice question banks](../../17-practice-questions/README.md) across all seven domains, on questions you
   have not seen before, and you can explain why each wrong option is wrong.
3. **Mock exams:** at least two timed [mock examinations](../../18-mock-examinations/README.md) at 63 items
   in 120 minutes, each finished with time to review and scoring 80% or higher.
4. **Deliverables:** at least five of the ten [practical exercises](practical-exercises.md) completed and
   self-reviewed at 8/10 or higher, including the ADR, eval plan and threat model.
5. **Scenarios:** you reach the recommended decision on at least 13 of the 16
   [decision scenarios](decision-scenarios.md) before reading the analysis.

These thresholds are our suggestion for building a safety margin. They are **not** a conversion to the
official scaled score, and meeting them does not guarantee a pass.

## Remediation paths

Find your weakest objectives and follow the matching path. Each path ends by re-scoring the objective.

| Weak area | Read | Do | Then |
|---|---|---|---|
| 1.1, 1.3, 1.5 | [Domain 1 guide](study-guide/domain-1.md), [Workflows vs agents](../../10-agentic-ai/01-workflows-vs-agents.md), [Workflow patterns](../../10-agentic-ai/02-workflow-patterns.md) | [Lab 12](../../19-hands-on-labs/lab-12-agentic-task-execution/README.md), exercise 1 | Scenarios 1–3 |
| 1.2, 1.4 | [Architecture patterns](../../13-enterprise-ai-architecture/02-architecture-patterns.md), [Multi-agent architecture](../../10-agentic-ai/04-multi-agent-architecture.md) | [Lab 20](../../19-hands-on-labs/lab-20-secure-enterprise-architecture/README.md) | Scenario 2 |
| 1.6, 4.5 | [Business value and ROI](../../13-enterprise-ai-architecture/08-business-value-and-roi.md), [Cost optimisation](../../15-production-operations/03-cost-optimisation.md) | [Lab 17](../../19-hands-on-labs/lab-17-cost-optimisation/README.md) | Scenario 4 |
| 2.1, 3.3 | [Model selection](../../05-claude-products-and-models/03-model-selection.md), [Latency optimisation](../../15-production-operations/04-latency-optimisation.md) | [Lab 06](../../19-hands-on-labs/lab-06-model-comparison/README.md), exercise 2 | Scenario 5 |
| 2.2, 2.3 | [System prompts](../../03-prompt-engineering/07-system-prompts-and-roles.md), [Few-shot](../../03-prompt-engineering/03-examples-few-shot.md), [Reasoning](../../03-prompt-engineering/04-reasoning-and-thinking.md) | [Lab 02](../../19-hands-on-labs/lab-02-prompt-improvement/README.md) | Scenario 6 |
| 2.4, 2.5, 3.8 | [Managing long context](../../04-context-engineering/02-managing-long-context.md), [Prompt caching](../../04-context-engineering/03-prompt-caching.md), [Progressive disclosure](../../04-context-engineering/06-progressive-disclosure-and-skills.md) | [Lab 05](../../19-hands-on-labs/lab-05-context-management/README.md) | Scenario 7 |
| 3.1, 3.2 | [Tool design](../../07-tool-use-and-function-calling/05-tool-design-best-practices.md), [Agent identity](../../12-ai-security/09-agent-identity-and-permissions.md), [MCP security](../../08-model-context-protocol/05-mcp-security.md) | [Lab 08](../../19-hands-on-labs/lab-08-tool-invocation/README.md), exercise 3 | Scenarios 7, 8 |
| 3.4, 4.6 | [Observability](../../15-production-operations/02-observability.md), [Logging and auditability](../../12-ai-security/11-logging-and-auditability.md) | [Lab 19](../../19-hands-on-labs/lab-19-observability/README.md), exercise 10 | Scenario 11 |
| 3.5, 3.6 | [Chunking](../../11-rag-and-knowledge-systems/02-chunking-strategies.md), [Retrieval strategies](../../11-rag-and-knowledge-systems/04-retrieval-strategies.md) | [Lab 11](../../19-hands-on-labs/lab-11-rag-pipeline/README.md), exercise 6 | Scenarios 9, 13 |
| 3.7 | [MCP vs alternatives](../../08-model-context-protocol/06-mcp-vs-alternatives.md), [Integration patterns](../../13-enterprise-ai-architecture/04-integration-patterns.md) | [Lab 09](../../19-hands-on-labs/lab-09-mcp-fundamentals/README.md), exercise 7 | Scenario 10 |
| 4.1–4.4 | [Domain 4 guide](study-guide/domain-4.md), [Grading methods](../../14-evaluation-and-testing/04-grading-methods.md), [Diagnosing failures](../../14-evaluation-and-testing/06-diagnosing-failures.md) | [Lab 16](../../19-hands-on-labs/lab-16-evaluation-framework/README.md), exercise 4 | Scenarios 12, 13 |
| 5.1, 5.2 | [LLM threat modelling](../../12-ai-security/01-llm-threat-modelling.md), [Enterprise deployment controls](../../12-ai-security/14-enterprise-deployment-controls.md) | [Lab 14](../../19-hands-on-labs/lab-14-prompt-injection-testing/README.md), exercise 3 | Scenarios 3, 6 |
| 5.3 | [Human in the loop](../../10-agentic-ai/05-human-in-the-loop.md), [Human oversight](../../12-ai-security/13-human-oversight.md) | [Lab 13](../../19-hands-on-labs/lab-13-human-in-the-loop/README.md) | Scenario 3 |
| 5.4, 5.5 | [Data governance and compliance](../../13-enterprise-ai-architecture/05-data-governance-and-compliance.md), [AI governance](../../12-ai-security/12-ai-governance.md) | [Lab 15](../../19-hands-on-labs/lab-15-sensitive-data-protection/README.md), exercise 8 | Scenarios 14, 15 |
| 6.1–6.4 | [Domain 6 guide](study-guide/domain-6.md), [Stakeholder communication](../../13-enterprise-ai-architecture/06-stakeholder-communication.md), [ADRs](../../13-enterprise-ai-architecture/07-architecture-decision-records.md) | Exercises 1 and 9 | Scenario 4 |
| 6.5 | [Lifecycle management](../../13-enterprise-ai-architecture/09-lifecycle-management.md), [Model upgrades](../../15-production-operations/08-model-upgrades-and-change-management.md) | [Lab 18](../../19-hands-on-labs/lab-18-reliability-engineering/README.md) | Scenario 12 |
| 7.1–7.3 | [Domain 7 guide](study-guide/domain-7.md), [Team rollout](../../09-claude-code/08-team-rollout.md), [Hooks](../../09-claude-code/06-hooks.md) | [Lab 10](../../19-hands-on-labs/lab-10-claude-code-workflows/README.md), exercise 5 | Scenario 16 |

Use the [CCAR-P flashcards](../../23-flashcards/decks/ccar-p.yaml) daily for recall, filtered by the
objectives you scored 0 or 1. The [coverage matrix](coverage-matrix.md) shows which practice questions map to
each objective.
