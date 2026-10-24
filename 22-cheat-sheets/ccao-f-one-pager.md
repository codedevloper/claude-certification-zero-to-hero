# CCAO-F One-Pager: Claude Certified Associate – Foundations

> **Unofficial summary.** Every exam fact on this page comes from
> [`16-certification-tracks/registry.yaml`](../16-certification-tracks/registry.yaml) (verified 2026-10-24 against the
> official exam guide v1.0, effective July 2026) and is summarised in
> [exam-facts.md](../25-official-resources/exam-facts.md). The official guide on the
> [Anthropic Partner Academy](https://anthropic-partners.skilljar.com/page/partner-certifications) is the source of
> truth. Pearson VUE has announced updated guides for 2026-11-17 and updated exam content from 2026-12-07, so
> re-check before you book. Full track: [16 · CCAO-F](../16-certification-tracks/ccao-f/README.md).

## Exam format

| Item | Value (from the registry) |
|---|---|
| Audience | Business and knowledge workers using Claude as a productivity tool; not aimed at API developers |
| Items | 60, multiple-choice and multiple-response |
| Time | 120 minutes |
| Passing | Scaled score 720 on a 100–1,000 scale |
| Fee | USD 99 (list price) |
| Validity | 12 months |
| Delivery | Pearson VUE, online proctored or test centre |
| Eligibility | Organisations in the Claude Partner Network |

## Domains, weights and what to know

### D1 · Prompting and Task Execution — 14%

- Clear goal, context, constraints and format; say who the output is for (CCAO-F-1.1).
- Break big requests into steps; chain outputs (CCAO-F-1.2).
- Iterate: change one thing, compare results (CCAO-F-1.3).
- Match the approach to the task: analysis, research, drafting, brainstorming (CCAO-F-1.4).
- Study: [03 · Clear, direct instructions](../03-prompt-engineering/01-clear-direct-instructions.md),
  [03 · Task decomposition](../03-prompt-engineering/05-task-decomposition-and-chaining.md).

### D2 · Output Evaluation and Validation — 21% (largest domain)

- Check accuracy and completeness against sources; never accept figures unverified (CCAO-F-2.1).
- Recognise hallucinations: confident specifics with no source, invented citations, internal contradictions (CCAO-F-2.2).
- Fact-check: ask for quotes, cross-check against the original, use research mode with cited sources (CCAO-F-2.3).
- Escalate to human review for high-stakes, regulated or external-facing content (CCAO-F-2.4).
- Edit for audience and compare alternative drafts (CCAO-F-2.5).
- Choose the format: inline text, artifacts, tables or structured data (CCAO-F-2.6).
- Study: [01 · Hallucinations](../01-ai-and-llm-fundamentals/06-hallucinations.md),
  [05 · Artifacts and output formats](../05-claude-products-and-models/05-artifacts-and-output-formats.md).

### D3 · Product and Model Selection — 12%

- Pick the feature: chat for quick tasks, Projects for repeated work with shared knowledge, research for sourced
  investigation, artifacts for standalone deliverables (CCAO-F-3.1).
- Model families: Haiku (fast, low cost), Sonnet (balanced), Opus (most capable in everyday use) (CCAO-F-3.2, 3.3).
- Context limits: when a chat gets long, summarise and restart, or persist key facts in a Project (CCAO-F-3.4).
- Study: [05 · Product ecosystem](../05-claude-products-and-models/01-product-ecosystem.md),
  [cheat sheet: model selection](model-selection.md).

### D4 · Workflow Integration and Solution Design — 16%

- Use Claude to analyse requirements and use cases (CCAO-F-4.1) and for research and planning (CCAO-F-4.2).
- Support solution design with options and trade-offs (CCAO-F-4.3).
- Augment or redesign a workflow; keep humans at decision points (CCAO-F-4.4).
- Explain value **and** limitations honestly to stakeholders (CCAO-F-4.5).
- Study: [13 · Business value and ROI](../13-enterprise-ai-architecture/08-business-value-and-roi.md).

### D5 · Configuration and Knowledge Management — 12%

- Projects: custom instructions plus curated knowledge files (CCAO-F-5.1).
- Connectors (for example Google Drive, Gmail): connect only what the work needs, respect permissions (CCAO-F-5.2).
- Write system-level instructions that are specific, stable and testable (CCAO-F-5.3).
- Maintain: remove stale files, version instructions, review periodically (CCAO-F-5.4).
- Study: [05 · Projects and knowledge](../05-claude-products-and-models/04-projects-and-knowledge.md),
  [05 · Connectors](../05-claude-products-and-models/06-connectors-and-integrations.md).

### D6 · Governance, Risk, and Responsible Use — 15%

- Appropriate vs inappropriate uses; no fully automated high-impact decisions about people without oversight (CCAO-F-6.1).
- Data sensitivity: personal, confidential and regulated data; minimise and follow policy (CCAO-F-6.2).
- Follow your organisation's AI policy and approved tools (CCAO-F-6.3).
- Ethics: bias, transparency, disclosure of AI assistance (CCAO-F-6.4).
- Study: [02 · Responsible use](../02-claude-fundamentals/05-responsible-use.md),
  [12 · AI governance](../12-ai-security/12-ai-governance.md).

### D7 · Troubleshooting and Optimization — 10%

- Diagnose weak outputs: missing context, vague task, wrong format, too-long conversation (CCAO-F-7.1).
- Adjust from feedback: add examples, constraints, a rubric (CCAO-F-7.2).
- Optimise workflows: reusable Projects, templates, smaller models for simple steps (CCAO-F-7.3).
- Study: [24 · Prompts and outputs](../24-troubleshooting/prompts-and-outputs.md).

## Last-week checklist

- [ ] Can you explain when to use a Project instead of a single chat?
- [ ] Can you list three signs of a hallucination and how to check each?
- [ ] Can you choose between Haiku, Sonnet and Opus for a described task and justify it?
- [ ] Can you name data you should not paste into an AI tool without approval?
- [ ] Can you rewrite a vague prompt into goal, context, constraints and format?

Practice: [17 · CCAO-F questions](../17-practice-questions/README.md),
[18 · Mock exams](../18-mock-examinations/README.md), [23 · Flashcards](../23-flashcards/README.md).
