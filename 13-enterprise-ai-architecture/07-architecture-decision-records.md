# Architecture Decision Records

> **Level:** Intermediate · **Time:** ~35 min · **Exam relevance:** CCAR-P 6.2, 6.4, 1.3

## In plain English

An architecture decision record (ADR) is a short document that captures one important decision: what you decided, why, what else you
considered and what follows from it. A collection of ADRs is the memory of a system. Six months later, when someone asks "why didn't we
just use an agent here?", the answer is a link, not a meeting.

ADRs are deliberately small. One decision per record, usually one or two pages, written when the decision is made and never rewritten
afterwards. If the decision changes, you write a new ADR that supersedes the old one.

## Why it matters

- AI systems change often: new models, new features, new prices, new regulations. Without recorded reasons, teams cannot tell which
  decisions are still valid when the context shifts.
- Reviewers (security, privacy, audit) need evidence of considered choices, especially for data flows and vendor coverage.
- ADRs make trade-offs explicit, which is the core of CCAR-P 6.2 (communicating decisions and trade-offs) and 6.4 (documenting architectures).
- They help handoff: the operating team inherits the reasoning, not just the code.

## How it works

### When to write an ADR

Write one when a decision is **significant** (affects cost, risk, quality or many components) and **hard to reverse**. For Claude
solutions, typical ADR topics are:

- Pattern choice (workflow versus agent versus multi-agent)
- Model tier and routing strategy
- Delivery platform and region
- Retrieval design (chunking, embedding model, hybrid search, reranking)
- Human-in-the-loop points and automation thresholds
- Data retention, logging of content, and compliance scope
- Integration mechanism (direct tools, MCP, CLI)
- Build versus buy (own loop, Agent SDK, Managed Agents)

Do not write ADRs for easily reversible details (a prompt wording change, a log field name). Those belong in commit history or a changelog.

### Lifecycle and storage

- Store ADRs as Markdown in the repository next to the code (for example `docs/adr/0007-use-hybrid-retrieval.md`), so changes are reviewed
  like code.
- Number them sequentially. Never renumber.
- Status values: **Proposed**, **Accepted**, **Superseded by ADR-NNNN**, **Deprecated**, **Rejected**.
- Add a **review trigger** for AI-specific decisions: a date or an event (new model release, price change, coverage change) that should prompt a re-check.

### Template

```markdown
# ADR-NNNN: <short decision title in the imperative, e.g. "Use a routing workflow for ticket triage">

- **Status:** Proposed | Accepted | Superseded by ADR-NNNN | Deprecated | Rejected
- **Date:** YYYY-MM-DD
- **Deciders:** <names or roles>
- **Consulted:** <security, privacy, operations, business owner ...>
- **Review trigger:** <date or event that should prompt re-evaluation>

## Context
What problem are we solving? What constraints apply (data classification, latency, budget, regulation, platform)?
What evidence do we have (evaluation results, cost model, pilot data)? Facts about vendors carry a date and a link.

## Decision
The choice, stated in one or two sentences.

## Options considered
| Option | Quality | Latency | Cost | Risk | Notes |
|---|---|---|---|---|---|
| A | | | | | |
| B | | | | | |

## Rationale
Why the chosen option wins on the criteria that matter most here.

## Consequences
- Positive:
- Negative / accepted trade-offs:
- Follow-up work:

## Compliance and security notes
Data flows affected, controls required, coverage evidence (link + date checked).

## Validation
How we will know the decision was right (metric, threshold, review date).
```

### Writing tips

- Lead with context and constraints. Most disagreements about decisions are really disagreements about context.
- Include at least one rejected option with honest pros. An ADR with a straw-man alternative persuades nobody.
- Quantify where you can, using evaluation results and the cost model; say where evidence is thin.
- Keep vendor facts dated. "Batch API not available on platform X (checked 2026-10-24, link)" can be re-verified; "not available" cannot.

## Example

Two worked ADRs for a fictional organisation, *Acme Logistics*, which is building a shipment-exception assistant. All numbers are synthetic.

### Worked ADR 1: pattern choice

```markdown
# ADR-0003: Use a prompt-chaining workflow, not an autonomous agent, for customs document checks

- **Status:** Accepted
- **Date:** 2026-10-10
- **Deciders:** Lead architect, Head of Customs Operations
- **Consulted:** Security architecture, Customs compliance lead, Platform operations
- **Review trigger:** Exception cases exceed 25% of volume, or quarterly review

## Context
Specialists spend most of their time extracting fields from commercial invoices, comparing them with the booking
record and drafting query emails. A two-week sample of 300 files showed a median of 18 minutes per file. A broker
signs every declaration, so model errors cause delays rather than regulatory penalties, provided a human signs.
Around 12% of files are genuine exceptions needing open-ended investigation.

## Decision
Implement a three-step workflow: (1) Claude extracts fields to a strict schema, (2) code compares fields with the
booking record, (3) Claude drafts a query email from a template when fields disagree. Exceptions go to specialists.

## Options considered
| Option | Quality (golden set, 120 files) | Median latency | Relative cost | Risk |
|---|---|---|---|---|
| A. Prompt-chaining workflow | 96% fields correct; drafts accepted 89% | 40 s | 1.0x | Low: fixed steps, each tested |
| B. Single agent with document and booking tools | 95% fields correct; drafts accepted 90% | 3 min | about 4x | Medium: variable paths, harder to test |
| C. Single large prompt doing all steps | 91% fields correct | 30 s | 0.8x | Medium: failures hard to localise |

## Rationale
Option A matches B on quality at a quarter of the cost and a fraction of the latency, and each step can be
evaluated independently. Option B's flexibility is valuable only for the exception cases, which remain with humans.

## Consequences
- Positive: predictable cost; step-level metrics; simple rollback per step.
- Negative: exceptions still need specialists; adding new document types requires new extraction schemas.
- Follow-up: evaluate an investigation agent for exceptions in a later phase (separate ADR).

## Compliance and security notes
No tools with write access. Documents contain business contact details; logging is metadata-only. Extraction
output validated against the schema before use.

## Validation
Pilot target: median handling time under 9 minutes with no increase in broker rejections over four weeks.
```

### Worked ADR 2: delivery platform

```markdown
# ADR-0005: Run the workload on Claude Platform on AWS rather than Amazon Bedrock

- **Status:** Accepted
- **Date:** 2026-10-17
- **Deciders:** Lead architect, Cloud platform owner
- **Consulted:** Procurement, Security architecture, FinOps
- **Review trigger:** Platform feature-availability change, contract renewal, or 2027-04-01

## Context
Shipping documents live in Amazon S3 in the same region. Procurement prefers AWS billing. The nightly
exception-summary job (about 9,000 requests) is not latency-sensitive and suits the Message Batches API.
A later phase plans to evaluate Managed Agents for exception investigation.

Feature availability checked 2026-10-24 against Anthropic's platform documentation:
the Message Batches API and Managed Agents (beta) were listed for the Claude API and Claude Platform on AWS,
and not for Amazon Bedrock.

## Decision
Use Claude Platform on AWS for both the interactive workflow and the nightly batch job.

## Options considered
| Option | Feature fit | Billing | Operations | Notes |
|---|---|---|---|---|
| A. Claude Platform on AWS | Batches and Managed Agents available | AWS | AWS identity | Anthropic-operated, API parity |
| B. Amazon Bedrock | No Message Batches API or Managed Agents | AWS | Native Bedrock tooling | Would need a different batch approach |
| C. Claude API (first party) | Full feature set | Anthropic invoice | Separate credentials and egress | Procurement objection |

## Rationale
Option A meets the billing preference and supports both the batch job and the planned agent phase without
re-platforming. Option B would forgo batch pricing for the nightly job (estimated at roughly double the model cost
for that job) and block the agent phase.

## Consequences
- Positive: one platform for all phases; batch discount retained.
- Negative: team must learn a second AWS-based Claude surface alongside existing Bedrock usage elsewhere.
- Follow-up: add the platform to the AI gateway routing table; update runbooks.

## Compliance and security notes
Data stays in the same AWS region as the source documents (verify region support at deployment).
Service identities scoped to the S3 prefix and the model endpoint only.

## Validation
Batch job completes before 06:00 on 95% of nights; monthly cost within 10% of the model.
```

## Enterprise use case

*Fabrikam Insurance* introduced ADRs after an audit finding: nobody could explain why claim summaries were stored for seven years when policy
required three. The root cause was an undocumented early decision to log full prompts and responses "for debugging".

The remediation plan included an ADR log for every AI solution, with a mandatory ADR for content logging and retention. Each ADR template
included a "Compliance and security notes" section and a review trigger. Within two quarters, the governance board could answer most
review questions by linking ADRs, and the time to approve new AI use cases fell because reviewers trusted the documented reasoning.

## Common mistakes

- **Writing ADRs after the fact** to justify what was built. They lose credibility and miss the real alternatives.
- **Editing accepted ADRs.** Supersede instead, so the history remains.
- **Essay-length ADRs.** If it takes 20 minutes to read, nobody will.
- **No evidence.** "We chose X because it is better" without evaluation data or a cost model.
- **No review trigger** for decisions that depend on fast-changing vendor facts.

## Security considerations

- Use ADRs to record security-relevant choices explicitly: agent permissions, approval gates, logging of content, secrets handling, data
  residency. These are what auditors and incident responders need.
- Do not include secrets, internal hostnames that should not be widely known, or real personal data in ADRs; they are widely read.
- Reference threat-model findings and accepted residual risks by ID so they are traceable ([LLM threat modelling](../12-ai-security/01-llm-threat-modelling.md)).

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| ADRs pile up unread | Too long or too many trivial ones | Enforce a size limit and a significance test |
| Same debate recurs every quarter | Decision not recorded, or context not captured | Write the ADR with context and rejected options; link it in reviews |
| ADR facts are wrong after a vendor update | No review trigger | Add triggers; schedule a quarterly sweep of vendor-dependent ADRs |

## Check your understanding

1. What two properties make a decision worth an ADR?
2. Why do you supersede an ADR instead of editing it?
3. Why do AI-related ADRs need a review trigger more than many traditional ones?
4. In worked ADR 2, which dated facts drove the platform choice?

<details>
<summary>Answers</summary>

1. It is significant (affects cost, risk, quality or many components) and hard to reverse.
2. To preserve the history of reasoning, so later readers can see what was decided, when and why, and what changed.
3. Because model capabilities, prices, feature availability and compliance coverage change frequently, so the context behind the decision can expire.
4. As checked on 2026-10-24, the Message Batches API and Managed Agents were available on the Claude API and Claude Platform on AWS but not on Amazon Bedrock.

</details>

## Further reading

- Michael Nygard's original post: [Documenting architecture decisions](https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions)
- The ADR community site: [adr.github.io](https://adr.github.io/)
- In this repository: [stakeholder communication](06-stakeholder-communication.md), [integration patterns](04-integration-patterns.md),
  [lifecycle management](09-lifecycle-management.md)
- Practice: write ADRs for the [Lab 20](../19-hands-on-labs/lab-20-secure-enterprise-architecture/README.md) design and for one of the
  [real-world projects](../20-real-world-projects/README.md)

<!-- page-nav:start -->
---

[← Previous: Stakeholder Communication](06-stakeholder-communication.md) · [Module overview](README.md) · [Next: Business Value and ROI →](08-business-value-and-roi.md)
<!-- page-nav:end -->
