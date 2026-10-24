# Stakeholder Communication

> **Level:** Intermediate · **Time:** ~35 min · **Exam relevance:** CCAR-P 6.2, 6.3, 1.6, CCAO-F 4.5

## In plain English

An architecture nobody understands does not get funded, approved or adopted. Stakeholder communication is the work of explaining what the
solution does, what it costs, what can go wrong and what you need from each person, in words that make sense to them.

A good analogy is a doctor explaining a treatment plan. The same facts are framed differently for the patient (what will I feel, how long),
the family (what support is needed), the insurer (cost and evidence) and a colleague (dosage and contraindications). Nothing is hidden; the
emphasis changes.

## Why it matters

- Generative AI creates unusually wide expectation gaps. Executives may expect perfection or fear catastrophe; engineers may underestimate
  operational work; risk teams may not know what controls exist. Unmanaged, those gaps become cancelled projects or unsafe launches.
- Claude solutions are probabilistic. "It will be right 100% of the time" is never true. You need language for error rates, review steps and
  service levels that people can accept in advance.
- CCAR-P 6.2 and 6.3 test whether you communicate trade-offs and manage expectations, including service level agreements (SLAs), in
  realistic scenarios.

## How it works

### Map the stakeholders

| Stakeholder | Cares about | Bring them | Ask them for |
|---|---|---|---|
| Executive sponsor | Outcome, cost, risk to reputation, timeline | One-page brief, ROI range, top three risks | Decision, funding, priority |
| Business process owner | Workflow impact, staff adoption, quality | Process map before and after, pilot metrics | Golden set, pilot users, acceptance criteria |
| End users | Does it help me, can I trust it, can I override it | Demos on their own cases, how to report problems | Feedback, edge cases |
| Security | Attack surface, identity, data exposure, logging | Threat model, control set, data flow | Risk acceptance, control requirements |
| Privacy and legal | Lawful basis, contracts, retention, transparency | Data-flow map, DPIA draft, vendor coverage evidence | Approval, required notices |
| Compliance and audit | Evidence, repeatability | ADRs, evaluation reports, change logs | Evidence requirements |
| Platform and operations | Supportability, on-call, SLOs | Runbooks, dashboards, rollback plan | Acceptance of handoff |
| Finance | Spend predictability, chargeback | Cost model with sensitivity, budget alerts | Budget, cost centre |

### Communicate trade-offs explicitly

Most architecture decisions trade between quality, latency, cost, risk and time to deliver. State the trade-off, the option you recommend
and what you give up.

A reusable structure for any trade-off message:

1. **Decision needed**: one sentence.
2. **Options**: two or three, each with its effect on quality, latency, cost and risk.
3. **Recommendation** and the evidence for it (evaluation results, cost model, risk review).
4. **What we give up** and how we would know if that turns out to matter.
5. **Reversibility**: how hard it is to change later.
6. **By when** the decision is needed and what happens if it slips.

### Talk about accuracy honestly

- Report **rates on a defined evaluation set**, not adjectives. "On 400 real past cases, 91% of summaries were rated acceptable by two
  reviewers; 3% contained a factual error that a reviewer caught" is better than "very accurate".
- Explain **who catches errors** and how. A 3% error rate with mandatory review is a different proposition from 3% sent straight to customers.
- Separate **model quality** from **system quality**: retrieval coverage, data freshness and integration bugs cause many "AI errors".
- Present ranges with uncertainty when you only have pilot data.

### Set service-level expectations

Distinguish three terms that are often confused:

| Term | Meaning | Example |
|---|---|---|
| Service level indicator (SLI) | What you measure | p95 time to first token; share of answers with a valid citation |
| Service level objective (SLO) | Internal target for an SLI | p95 time to first token under 2 s over 28 days |
| Service level agreement (SLA) | A commitment to a customer, often with consequences | 99.5% monthly availability of the assistant API |

For Claude solutions, include **quality SLOs** (for example, citation validity rate, escalation rate, reviewer acceptance rate) alongside
availability and latency. Do not promise an SLA stronger than your dependencies support; check the provider's published terms for your
platform and plan for degradation (fallback models, queueing, graceful "please try later" messages). See
[reliability engineering](../15-production-operations/05-reliability-engineering.md).

### Run feedback loops

- **In-product feedback**: thumbs up or down with a reason, routed into a review queue that feeds the evaluation set.
- **Regular review**: a fortnightly or monthly session with the process owner to review metrics, failure examples and the backlog.
- **Change notices**: tell users before prompts, models or behaviours change, and what to expect.
- **Closing the loop**: show stakeholders which feedback led to which change. People keep giving feedback when they see it used.

### Choose the right artefact

| Audience | Artefact |
|---|---|
| Executives | One-page brief, decision memo, quarterly value report |
| Risk owners | Threat model, data-flow map, ADRs, evaluation and red-team results |
| Engineers | Architecture diagrams, ADRs, interface specs, runbooks |
| Users | Short guide: what it does, what it does not, how to check and report |

## Example

A one-page decision memo for an executive audience. It uses synthetic numbers.

```markdown
# Decision: model tier for the policy Q&A assistant (Fabrikam Insurance)

**Decision needed by:** 14 November. **Owner:** Head of Claims Operations.

**Options**
| Option | Reviewer-accepted answers (400-case set) | p95 latency | Est. monthly model cost |
|---|---|---|---|
| A. Larger model for all questions | 94% | 6.1 s | about 2.4x option B |
| B. Smaller model for all questions | 86% | 2.0 s | baseline |
| C. Route: smaller model first, larger model for complex questions | 93% | 2.9 s (p95) | about 1.3x option B |

**Recommendation:** Option C. It keeps quality within one point of option A at roughly half its cost, and meets the 3-second
latency objective agreed with the claims team.

**What we give up:** about 1 point of accuracy versus A, and some routing complexity. We will watch the reviewer-acceptance
rate weekly; if it drops below 92% for two weeks we revisit.

**Reversibility:** high. Routing is configuration in the gateway.

**Risks:** misrouting complex questions to the smaller model. Mitigation: the router fails safe to the larger model when unsure.
```

Notice what the memo avoids: model jargon, unqualified claims, and any promise of zero errors.

## Enterprise use case

*Northwind Lending* launched an assistant that drafts responses to broker queries. Two weeks into the pilot, a sales director escalated a
single bad draft to the chief operating officer as proof that "the AI is not ready".

The architect had prepared for this. The pilot charter, signed before launch, stated that drafts are reviewed by a person, that the target
was 85% of drafts accepted with minor or no edits, and that errors would be logged and categorised. The response to the COO was a short
note: the error was caught by the reviewer as designed; the pilot was at 88% acceptance; this error belonged to a category (out-of-date
rate tables in the knowledge base) already fixed by moving to an event-driven re-index; and here are the next two weeks of metrics to watch.

The escalation became evidence that the controls worked. Without the charter, the same incident could have ended the pilot.

## Common mistakes

- **Over-promising** ("it will eliminate manual review") to win funding, then losing trust at the first error.
- **Under-explaining risk** to security and privacy teams, who then block late.
- **Jargon** with executives (tokens, embeddings, temperature) instead of outcomes, cost and risk.
- **Metrics without baselines**, which make any number meaningless.
- **Silent changes** to prompts or models that users notice before you tell them.
- **One-way communication**: no channel for users to report problems, so you only hear about failures through escalations.

## Security considerations

- Be precise with security stakeholders about what the model can and cannot do: which tools it can call, with which identity, and which
  actions require approval. Vague answers erode trust.
- Do not share sensitive examples (customer data, internal incidents) in broad demos or slide decks; use synthetic data.
- Make residual risks explicit and get them accepted by named owners. "Accepted by the CISO on 3 October" is evidence; "discussed" is not.
- Include AI-specific incidents (prompt injection, data disclosure, harmful output) in incident communication plans ([incident response](../15-production-operations/07-incident-response.md)).

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| Executives lose confidence after one bad example | No agreed error expectations | Pilot charter with target rates and review design, signed before launch |
| Engineers and business disagree about "done" | Acceptance criteria not written | Define SLIs, SLOs and evaluation thresholds together |
| Users stop using the tool | Feedback ignored or tool unreliable | Show "you said, we did"; fix the top failure category first |
| Risk teams keep asking the same questions | Evidence scattered | Maintain an ADR log and an evidence index per solution |

## Check your understanding

1. What is the difference between an SLO and an SLA, and why should quality metrics appear among your SLOs?
2. List the six parts of the trade-off message structure.
3. Why should accuracy be reported on a defined evaluation set rather than with adjectives?
4. What did Northwind Lending's pilot charter contain that turned an escalation into evidence?

<details>
<summary>Answers</summary>

1. An SLO is an internal target for a measured indicator; an SLA is an external commitment, often with consequences. Claude solutions can
   be available and fast while giving poor answers, so quality indicators (citation validity, reviewer acceptance, escalation rate) need targets too.
2. Decision needed; options with their effects; recommendation and evidence; what we give up; reversibility; deadline and the consequence of slipping.
3. Adjectives cannot be compared, tested or tracked. A rate on a fixed set gives a baseline, enables regression testing and lets
   stakeholders judge acceptability with the review design in mind.
4. Human review of every draft, a target acceptance rate, and a commitment to log and categorise errors, all agreed before launch.

</details>

## Further reading

- Google SRE book: [Service level objectives](https://sre.google/sre-book/service-level-objectives/)
- Anthropic engineering: [Building effective agents](https://www.anthropic.com/engineering/building-effective-agents) (on transparency of planning steps)
- In this repository: [architecture decision records](07-architecture-decision-records.md), [business value and ROI](08-business-value-and-roi.md),
  [metrics](../14-evaluation-and-testing/02-metrics.md), [stakeholder and behavioural interview questions](../21-interview-preparation/stakeholder-and-behavioural.md)
- Practice: [Lab 13: Human in the loop](../19-hands-on-labs/lab-13-human-in-the-loop/README.md)

<!-- page-nav:start -->
---

[← Previous: Data Governance and Compliance](05-data-governance-and-compliance.md) · [Module overview](README.md) · [Next: Architecture Decision Records →](07-architecture-decision-records.md)
<!-- page-nav:end -->
