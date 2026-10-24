# Claude Certified Architect – Professional (CCAR-P) Preparation Track

> **Unofficial study track.** This repository is not affiliated with or endorsed by Anthropic. The official
> CCAR-P Exam Guide v1.0 is the source of truth. Every exam fact on this page comes from
> [`registry.yaml`](../registry.yaml) (verified 2026-10-24) and the
> [official certifications page](https://anthropic-partners.skilljar.com/page/partner-certifications).

## What the credential is for

CCAR-P is the professional-level architecture credential in Anthropic's Claude Certification Program. It
signals that you can take an ambiguous business problem and turn it into a production Claude solution:
choose the right pattern (single call, workflow, agent or multi-agent system), integrate it with enterprise
systems safely, prove that it works with evaluations, run it economically, govern it, and keep stakeholders
aligned for the whole lifecycle.

Where the foundations-level exams test whether you know *what* a feature does, CCAR-P tests whether you
can *choose between* reasonable options under constraints and defend the choice. Expect scenario items in
which two or three answers are technically possible and only one is the best fit for the stated latency,
cost, risk, compliance or organisational constraint.

## Who it is for

The exam is pitched at experienced technical people (architects, AI and ML engineers, tech leads, senior
developers) who are responsible for getting Claude solutions into production. In practice this
track also suits:

- Cloud, enterprise and security architects who review or approve AI designs.
- DevSecOps and platform engineers who own the paved road for AI workloads (gateways, secrets, logging).
- Technical leaders who must explain AI trade-offs to executives, risk and compliance teams.

### The minimally qualified candidate

A useful mental model of the person the exam is calibrated for (our interpretation, not official wording):

| Area | The minimally qualified candidate can... |
|---|---|
| Design | Decompose a business problem, choose workflow versus agent with a reason, and draw an end-to-end architecture with feedback loops. |
| Models and context | Pick a model tier and effort level per route, write a system prompt with guardrails, and budget a context window. |
| Integration | Choose MCP, a direct API/CLI tool or agent-to-agent delegation; spot over-privileged tools and identity gaps; design a RAG pipeline. |
| Evaluation | Define metrics, build a mixed-method eval set, run an A/B comparison and diagnose a regression. |
| Governance | Place guardrails and human review, map controls to GDPR, HIPAA or FedRAMP obligations, and address bias and transparency. |
| Stakeholders | Run discovery, write an ADR, set SLAs and manage expectations through handoff, monitoring and iteration. |
| Enablement | Configure Claude Code for a team (settings, permissions, hooks, MCP, CLAUDE.md) and use it for debugging and operations. |

### Recommended experience

From the registry: no mandatory prerequisites, but **3+ years in systems architecture or platform
engineering** and **6+ months hands-on with Claude or comparable LLM systems in production** are
recommended. If you lack production LLM experience, budget extra time for the labs in
[`19-hands-on-labs`](../../19-hands-on-labs/README.md), especially labs 11–20.

## Format and logistics

| Fact | Value (from [`registry.yaml`](../registry.yaml)) |
|---|---|
| Exam code | CCAR-P |
| Guide version | 1.0 (effective July 2026) |
| Items | 63 |
| Item types | Multiple-choice and multiple-response |
| Time | 120 minutes |
| Passing standard | Scaled score 720 on a 100–1,000 scale |
| Fee | USD 175 |
| Validity | 12 months |
| Result | Pass/fail, scaled score and percent-correct by domain |
| Delivery | Pearson VUE, online proctored (OnVUE) or test centre |

See also [`exam-facts.md`](../../25-official-resources/exam-facts.md) for all tracks side by side, and
[`exam-day.md`](exam-day.md) for check-in and pacing.

## Registration and eligibility

- **Eligibility:** certification exams are open to organisations in the **Claude Partner Network**. The free
  Anthropic Academy courses are open to everyone but award completion certificates, not certifications.
- **Registration path:** enrol through the Anthropic Partner Academy (Skilljar) certification page, then
  schedule with Pearson VUE. Your Pearson profile name must exactly match your government-issued ID
  (Latin characters only), according to the
  [Pearson VUE Claude Certification page](https://www.pearsonvue.com/us/en/anthropic.html) as of 2026-10-24.
- **Rescheduling:** Pearson VUE states that you must cancel or reschedule at least 48 hours before the
  appointment; late changes and no-shows forfeit the fee (as of 2026-10-24).

## Retake and renewal policy

- **Retakes** (registry): wait 14 days after the first failed attempt, 30 days after the second and
  90 days after the third, with at most four attempts per exam in a rolling 12 months. The limits apply per
  exam.
- **Validity:** the registry records a 12-month validity period.

**Renewal** (exam guide v1.0, section 14, checked 2026-10-24): renewal is free if you do it before expiry: catch up on
what has changed and pass an unproctored check on the Anthropic Partner Academy. Once it has expired, the only route
back is sitting and paying for the whole exam again. If exam content changes significantly, Anthropic may require the full exam instead of the
renewal assessment. See [exam facts](../../25-official-resources/exam-facts.md).

## Upcoming change: 2026-11-17 guide update

Pearson VUE states that **updated exam guides will be published on 2026-11-17** and that CCAR-P (together
with CCAO-F and CCDV-F) **will include updated content from 2026-12-07**. If you test on or after
2026-12-07, study from the updated guide and compare its objectives with [`registry.yaml`](../registry.yaml).
This track will be re-verified after 2026-11-17; until then it follows guide v1.0.

## Domains

| # | Domain | Weight | Study guide | Key modules |
|---|---|---|---|---|
| 1 | Solution Design & Architecture | 17% | [domain-1.md](study-guide/domain-1.md) | [13 Enterprise architecture](../../13-enterprise-ai-architecture/README.md), [10 Agentic AI](../../10-agentic-ai/README.md) |
| 2 | Claude Models, Prompting & Context Engineering | 13% | [domain-2.md](study-guide/domain-2.md) | [03 Prompt engineering](../../03-prompt-engineering/README.md), [04 Context engineering](../../04-context-engineering/README.md), [05 Products and models](../../05-claude-products-and-models/README.md) |
| 3 | Integration | 19% | [domain-3.md](study-guide/domain-3.md) | [07 Tool use](../../07-tool-use-and-function-calling/README.md), [08 MCP](../../08-model-context-protocol/README.md), [11 RAG](../../11-rag-and-knowledge-systems/README.md) |
| 4 | Evaluation, Testing & Optimization | 16% | [domain-4.md](study-guide/domain-4.md) | [14 Evaluation](../../14-evaluation-and-testing/README.md), [15 Production operations](../../15-production-operations/README.md) |
| 5 | Governance, Safety & Risk Management | 14% | [domain-5.md](study-guide/domain-5.md) | [12 AI security](../../12-ai-security/README.md), [13 Data governance](../../13-enterprise-ai-architecture/05-data-governance-and-compliance.md) |
| 6 | Stakeholder Communication & Lifecycle Management | 14% | [domain-6.md](study-guide/domain-6.md) | [13 Stakeholders](../../13-enterprise-ai-architecture/06-stakeholder-communication.md), [13 ADRs](../../13-enterprise-ai-architecture/07-architecture-decision-records.md), [13 Lifecycle](../../13-enterprise-ai-architecture/09-lifecycle-management.md) |
| 7 | Developer Productivity & Operational Enablement | 7% | [domain-7.md](study-guide/domain-7.md) | [09 Claude Code](../../09-claude-code/README.md) |

Integration (19%), Solution Design (17%) and Evaluation (16%) together make up just over half the exam.
Domain 7 is small (7%), but its objectives overlap heavily with Domains 3 and 5 (permissions, MCP, hooks).

## Recommended study sequence

The order below follows dependencies, not domain numbers.

1. **Baseline (week 1).** Take the [readiness assessment](readiness-assessment.md) cold. Skim
   [`revision-notes.md`](revision-notes.md) to see the whole surface.
2. **Models and context (Domain 2).** Everything else assumes you can choose a model, write a guarded
   system prompt and budget context. Do labs 02, 05 and 06.
3. **Design (Domain 1).** Workflow versus agent, multi-agent orchestration, decomposition, business value.
   Do lab 12 and draft your first ADR.
4. **Integration (Domain 3).** Tools, MCP, identity, RAG, progressive disclosure. Do labs 08, 09 and 11.
5. **Evaluation and optimisation (Domain 4).** Metrics, datasets, A/B testing, diagnosis, cost and latency.
   Do labs 16, 17 and 19.
6. **Governance (Domain 5).** Guardrails, failure modes, human-in-the-loop, compliance, fairness. Do labs
   13, 14 and 15.
7. **Stakeholders and lifecycle (Domain 6).** Discovery, ADRs, SLAs, handoff. Do lab 20 end to end.
8. **Enablement (Domain 7).** Team Claude Code configuration and operational debugging. Do labs 10 and 18.
9. **Consolidate.** Work through [`decision-scenarios.md`](decision-scenarios.md),
   [`practical-exercises.md`](practical-exercises.md), [`common-misconceptions.md`](common-misconceptions.md),
   the [CCAR-P flashcards](../../23-flashcards/decks/ccar-p.yaml), the
   [practice questions](../../17-practice-questions/README.md) and the
   [mock examinations](../../18-mock-examinations/README.md).
10. **Final week.** Re-take the readiness assessment, remediate weak objectives, read
    [`exam-day.md`](exam-day.md).

For calendar-based plans, see the [roadmaps](../../00-getting-started/roadmaps/README.md) (the 60-day and
90-day plans suit CCAR-P).

## Track contents

| File | Purpose |
|---|---|
| [`objective-map.yaml`](objective-map.yaml) | Every CCAR-P objective mapped to modules and labs |
| [`coverage-matrix.md`](coverage-matrix.md) | Generated matrix of objectives, modules, labs and practice questions |
| [`study-guide/`](study-guide/domain-1.md) | Seven architect-level domain guides |
| [`practical-exercises.md`](practical-exercises.md) | Hands-on architect deliverables (ADR, eval plan, threat model, RAG design, team config) |
| [`decision-scenarios.md`](decision-scenarios.md) | Original architecture case studies with options analysis |
| [`revision-notes.md`](revision-notes.md) | Condensed notes by domain |
| [`common-misconceptions.md`](common-misconceptions.md) | Architect-level misconceptions and corrections |
| [`exam-day.md`](exam-day.md) | Logistics, rules and pacing |
| [`readiness-assessment.md`](readiness-assessment.md) | Per-objective self-assessment and remediation |
| [CCAR-P one-pager](../../22-cheat-sheets/ccar-p-one-pager.md) | Single-page cheat sheet |

## Official resources

- [Anthropic Partner Academy: certifications page and exam guides](https://anthropic-partners.skilljar.com/page/partner-certifications)
- [Pearson VUE: Claude Certification Program](https://www.pearsonvue.com/us/en/anthropic.html)
- [Claude Platform documentation](https://platform.claude.com/docs)
- [Claude Code documentation](https://code.claude.com/docs)
- [Model Context Protocol](https://modelcontextprotocol.io)
- [Official resources in this repository](../../25-official-resources/README.md)
