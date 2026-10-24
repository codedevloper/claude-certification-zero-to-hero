# CCAR-P One-Pager: Claude Certified Architect – Professional

> **Unofficial summary.** Every exam fact on this page comes from
> [`16-certification-tracks/registry.yaml`](../16-certification-tracks/registry.yaml) (verified 2026-10-24 against the
> official exam guide v1.0, effective July 2026) and is summarised in
> [exam-facts.md](../25-official-resources/exam-facts.md). The official guide on the
> [Anthropic Partner Academy](https://anthropic-partners.skilljar.com/page/partner-certifications) is the source of
> truth. Pearson VUE has announced updated guides for 2026-11-17 and updated exam content from 2026-12-07, so
> re-check before you book. Full track: [16 · CCAR-P](../16-certification-tracks/ccar-p/README.md).

## Exam format

| Item | Value (from the registry) |
|---|---|
| Audience | Mid- to senior-level solution architects, AI/ML engineers, technical leads, senior software engineers |
| Recommended experience | 3+ years in systems architecture or platform engineering; 6+ months hands-on with LLM systems in production (not mandatory) |
| Items | 63, multiple-choice and multiple-response |
| Time | 120 minutes |
| Passing | Scaled score 720 on a 100–1,000 scale |
| Fee | USD 175 (list price) |
| Validity | 12 months |
| Delivery | Pearson VUE, online proctored or test centre |
| Eligibility | Organisations in the Claude Partner Network |

## Domains, weights and what to know

### D1 · Solution Design & Architecture — 17%

- Translate a business problem into a Claude solution with measurable outcomes (CCAR-P-1.1).
- End-to-end design: input, processing, output, feedback loops (CCAR-P-1.2).
- Pattern choice: single call → workflow (prompt chaining, routing, parallelisation, orchestrator–workers,
  evaluator–optimiser) → agent; pick the simplest that works (CCAR-P-1.3).
- Multi-agent orchestration: when sub-agents help (parallel, context isolation) and what they cost (CCAR-P-1.4).
- Decomposition and value alignment: efficiency, cost, SLAs (CCAR-P-1.5, 1.6).
- Study: [10 · Workflows vs agents](../10-agentic-ai/01-workflows-vs-agents.md),
  [13 · Architecture patterns](../13-enterprise-ai-architecture/02-architecture-patterns.md).

### D2 · Claude Models, Prompting & Context Engineering — 13%

- Model trade-offs: capability, latency, cost, context; tune effort before switching (CCAR-P-2.1).
- System prompts, templates and guardrails (CCAR-P-2.2).
- Zero-shot, few-shot and reasoning (adaptive thinking, effort) (CCAR-P-2.3).
- Context window and token optimisation: retrieval, compaction, context editing (CCAR-P-2.4).
- Reuse: prompt caching (prefix stability), modular prompts, Agent Skills (CCAR-P-2.5).
- Study: [04 · Context engineering](../04-context-engineering/README.md), [cheat sheet: model selection](model-selection.md).

### D3 · Integration — 19% (largest domain)

- Capability bloat: too many or over-powered tools; trim, scope and split (CCAR-P-3.1).
- AuthN/AuthZ gaps: user-bound permissions, audience-bound tokens, no shared admin keys (CCAR-P-3.2).
- Accuracy–latency trade-offs: model, effort, retrieval depth, streaming, caching (CCAR-P-3.3).
- Observability at scale: tracing tool calls, token usage, request IDs (CCAR-P-3.4).
- RAG design: chunking, embeddings, hybrid search, reranking, metadata filters (CCAR-P-3.5, 3.6).
- Study: [07 · Tool design](../07-tool-use-and-function-calling/05-tool-design-best-practices.md),
  [08 · MCP](../08-model-context-protocol/README.md), [11 · RAG](../11-rag-and-knowledge-systems/README.md).

### D4 · Evaluation, Testing & Optimization — 16%

- Metrics: accuracy, latency, cost, safety, security (CCAR-P-4.1).
- Datasets and mixed methods: code-graded, model-graded, human-graded (CCAR-P-4.2).
- A/B testing and iterative improvement (CCAR-P-4.3).
- Diagnose prompt failures, hallucination and model mismatch (CCAR-P-4.4).
- Token, latency and cost optimisation: caching, batches, effort, routing (CCAR-P-4.5).
- Monitoring with logging and observability tooling (CCAR-P-4.6).
- Study: [14 · Evaluation and testing](../14-evaluation-and-testing/README.md).

### D5 · Governance, Safety & Risk Management — 14%

- Guardrails and safety controls in and around the model (CCAR-P-5.1).
- Failure modes: injection, hallucination, excessive agency, drift (CCAR-P-5.2).
- Human-in-the-loop design: where, who, with what information (CCAR-P-5.3).
- Regulatory compliance: data residency, retention, sector rules (CCAR-P-5.4).
- Bias, fairness and transparency (CCAR-P-5.5).
- Study: [12 · AI security](../12-ai-security/README.md), [cheat sheet: AI security](ai-security.md).

### D6 · Stakeholder Communication & Lifecycle Management — 14%

- Discovery and requirements (CCAR-P-6.1).
- Communicate decisions and trade-offs; architecture decision records (CCAR-P-6.2, 6.4).
- Expectations and SLAs; feedback loops (CCAR-P-6.3).
- Lifecycle: discovery, design, handoff, monitoring, iteration (CCAR-P-6.5).
- Study: [13 · Stakeholder communication](../13-enterprise-ai-architecture/06-stakeholder-communication.md),
  [13 · Lifecycle management](../13-enterprise-ai-architecture/09-lifecycle-management.md).

### D7 · Developer Productivity & Operational Enablement — 7%

- Configure Claude Code for teams: shared settings, permissions, `CLAUDE.md`, hooks, MCP (CCAR-P-7.1).
- AI-assisted developer workflows: review, tests, CI (CCAR-P-7.2).
- Debugging and operational issue resolution (CCAR-P-7.3).
- Study: [09 · Team rollout](../09-claude-code/08-team-rollout.md), [cheat sheet: Claude Code](claude-code.md).

## Architect's decision reflexes

| Situation | Reflex |
|---|---|
| Unclear if an agent is needed | Start with a workflow; add autonomy only where the path cannot be pre-defined |
| Repeated large prefix | Prompt caching with stable content first |
| Work that can wait | Message Batches |
| Machine-consumed output | Structured outputs or strict tools |
| Consequential action | Human approval plus deterministic checks |
| Many tools | Trim, namespace, or use tool search / Skills to load on demand |
| Quality question | Answer with an eval, not an opinion |

Practice: [17 · CCAR-P questions](../17-practice-questions/README.md),
[18 · Mock exams](../18-mock-examinations/README.md), [23 · Flashcards](../23-flashcards/README.md).
