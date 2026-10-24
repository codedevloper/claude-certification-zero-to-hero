# Stakeholder and Behavioural Interview Questions

Twenty-six questions about working with stakeholders, leading AI initiatives and handling difficult situations, with
model answers. Solution architect and senior AI engineer interviews weight these heavily, and CCAR-P domain 6
(Stakeholder Communication & Lifecycle Management) covers the same skills. All scenarios are fictional and original.

> **Answer with STAR:** **S**ituation (one or two sentences), **T**ask (your responsibility), **A**ction (what *you*
> did, specifically), **R**esult (measurable where possible) and, ideally, what you learned. Two minutes is a good
> length. The model answers below use fictional examples; replace them with your own real experience. Never invent
> experience in an interview.

---

## Discovery and requirements

### 1. How do you run discovery for a proposed generative AI project?

**Model answer:** I start with the business outcome, not the technology: what decision or task improves, for whom, and
how we would measure it. Then I map the current process with the people who do it, collect real examples of inputs and
desired outputs, identify data sources and their sensitivity, and agree constraints (latency, cost, regulation,
languages). I ask what happens when the system is wrong and who is accountable. The output is a short brief with
success metrics, a risk list and a proposed smallest useful pilot. See
[13 · Solution design process](../13-enterprise-ai-architecture/01-solution-design-process.md).

### 2. A stakeholder says "we need an AI agent". How do you respond?

**Model answer:** I ask what job they want done and walk back from that. Often a single well-designed call or a fixed
workflow meets the need with less cost and risk, and I explain the difference in plain terms: a workflow follows our
steps; an agent decides its own. If the task genuinely needs open-ended exploration, an agent is right, and we then
talk about permissions, approvals and evaluation. The goal is to agree on the outcome, then choose the simplest design.

### 3. Tell me about a time requirements were unclear or kept changing

**Model answer (example):** At a fictional logistics firm, the operations director wanted "smarter exception handling"
for delayed shipments. I ran two workshops with dispatchers, collected fifty real exceptions, and we sorted them into
categories. That showed 70% were three predictable types. I proposed automating triage for those first, with the rest
routed to people. We agreed acceptance criteria per category. When new requests arrived later, we evaluated them
against the same criteria and backlog, which kept scope stable. The pilot shipped in six weeks.

### 4. How do you set success metrics for an AI feature with non-technical stakeholders?

**Model answer:** I translate quality into business terms: time saved per case, percentage of drafts accepted without
major edits, error rate on a defined sample, escalation rate, user satisfaction. I pair each with a technical measure
we can automate (eval accuracy, latency, cost per task) and agree a baseline from the current process so we can show
improvement. I also agree a "stop" condition: the level of errors at which we pause.

## Communicating trade-offs and decisions

### 5. How do you explain hallucination risk to an executive?

**Model answer:** Without jargon: the system writes fluent, confident text, and occasionally it is confidently wrong,
especially when it lacks the right source. Then I explain how we reduce it (giving it our documents, asking for
sources, checking key facts automatically), what we measured on real samples, and where a person stays in the loop.
I give a concrete error rate and the business impact of an error, so they can make an informed decision rather than
hearing "it's 100% accurate" or "AI is unreliable".

### 6. How do you present an architecture choice between two options?

**Model answer:** One page: the decision needed, the options, a comparison against the criteria the stakeholders care
about (cost, time to value, risk, flexibility, operational load), my recommendation with the reason, and what would
change my mind. I record it as an architecture decision record so the reasoning survives staff changes. Diagrams show
data flows and trust boundaries. See [13 · Architecture decision records](../13-enterprise-ai-architecture/07-architecture-decision-records.md).

### 7. A sponsor expects the AI to fully automate a process you believe needs human review. What do you do?

**Model answer:** I bring evidence: error rates from our evaluation, the cost of each type of error, and regulatory or
reputational constraints. I propose a staged path: assisted mode first (AI drafts, humans approve), measure agreement
rates, then automate the categories where errors are rare and cheap while keeping review for the rest. That respects
their goal of efficiency while managing risk, and turns the disagreement into a data question.

### 8. How do you communicate cost to stakeholders?

**Model answer:** As cost per unit of business value (per document processed, per resolved request), with a monthly
projection at expected volume and at peak, and the levers that change it (model choice, caching, batching, effort).
I show the comparison with the current manual cost. I flag uncertainty and agree a budget alert threshold so nobody
is surprised.

### 9. Describe a time you had to say no to a stakeholder

**Model answer (example):** A fictional marketing lead wanted customer purchase histories pasted into a public chatbot
tool to generate campaigns. I explained the data-policy and privacy issues, and offered an alternative: an approved
workspace with aggregated, de-identified segments. We delivered the first campaign drafts from aggregated data within a
week. The lead got the outcome without the risk, and we wrote the pattern into our AI usage guidance.

## Delivery and lifecycle

### 10. How do you plan a pilot for a Claude-based solution?

**Model answer:** Pick a narrow, valuable slice with available data and a clear owner. Define success metrics and a
baseline, build the smallest working version with logging and an evaluation set from day one, run it with a small
group in assisted mode, review results weekly, and decide go, iterate or stop at a fixed date. I plan for production
from the start (security review, data handling, monitoring) so a successful pilot does not need a rewrite.

### 11. How do you hand over an AI system to an operations team?

**Model answer:** A runbook covering architecture, dependencies, model and prompt versions, known failure modes and
fixes, dashboards and alerts, escalation paths and how to roll back. The eval suite and how to run it. Cost and rate
limit expectations. A model-upgrade procedure. I run a joint on-call period and a game day where we simulate failures
(API errors, bad outputs, an injection attempt) before I step back. See
[13 · Lifecycle management](../13-enterprise-ai-architecture/09-lifecycle-management.md).

### 12. How do you manage expectations and SLAs for an LLM-powered service?

**Model answer:** I separate what we can guarantee (availability of our service with fallbacks, latency targets based
on measured percentiles, response time to incidents) from what is probabilistic (answer quality, measured as a rate on
evaluations). I agree SLOs with error budgets, design fallbacks for provider slowdowns, and report quality metrics
regularly so stakeholders see trends rather than anecdotes.

### 13. A model upgrade changed outputs and users complained. How would you handle it?

**Model answer:** Acknowledge quickly, roll back or pin the previous model if the impact is significant, and gather
examples. Compare old and new outputs on our eval set to understand the change. Adjust prompts or configuration for the
new model, re-run evals, and roll out gradually. Then fix the process gap: upgrades go through the eval gate and a
staged rollout, with communication to users about expected changes.

### 14. How do you gather and act on user feedback?

**Model answer:** Lightweight in-product signals (thumbs up/down with an optional reason, edits made to drafts,
escalations), periodic interviews, and sampling of conversations with consent and redaction. Each week we categorise
failures, turn representative ones into eval cases, and prioritise fixes by impact. I close the loop with users by
telling them what changed because of their feedback.

## Collaboration and leadership

### 15. How do you work with security and legal teams on AI projects?

**Model answer:** Early, not at the end. I bring them a clear data-flow diagram, the data classes involved, the
provider's terms and retention settings, and the controls we plan. I ask what evidence they need and build it into
the project (threat model, DPIA, test results). Treating them as design partners shortens approval time and usually
improves the design.

### 16. Tell me about a time you influenced without authority

**Model answer (example):** At a fictional insurer, several teams built separate prompt wrappers with inconsistent
logging. I could not mandate a standard, so I built a small shared library with logging, retries and redaction, showed
how it cut one team's integration time from two weeks to two days, and offered to pair with others. Within a quarter
most teams adopted it, which made our later security review far simpler.

### 17. How do you upskill a team new to LLM development?

**Model answer:** Short hands-on sessions over lectures: build a first call, then a structured-output extraction, then a
tool loop, then an evaluation. Pair programming on real tickets. Shared guidelines (prompt patterns, security rules,
code templates) and a review checklist. Office hours. I measure progress by what people ship and by fewer repeated
mistakes in reviews.

### 18. Describe a disagreement with a technical peer about an AI design

**Model answer (example):** A colleague wanted a multi-agent design for a document review task; I thought a fixed
workflow would do. Rather than argue, we agreed to build both on a 100-document sample and compare accuracy, latency
and cost. The workflow matched accuracy at a third of the cost, but the agent handled two unusual document types
better. We shipped the workflow with an agent fallback for those types. The experiment, not opinions, settled it.

## Ethics, risk and judgment

### 19. What would you do if you discovered an AI feature was producing biased outcomes?

**Model answer:** Pause or limit the affected decisions if harm is ongoing, inform the owner and risk or compliance
teams, and analyse the scope with data (which groups, which decisions, how often). Find the cause (data, prompt,
retrieval, evaluation gaps), fix it, add fairness measures to the eval suite and monitor. Be transparent with affected
stakeholders as policy requires. Bias work needs to be continuous, not a one-off check.

### 20. A colleague wants to paste confidential client data into an unapproved AI tool to meet a deadline. What do you do?

**Model answer:** Stop it politely and help them meet the deadline another way: an approved tool, a de-identified
version of the data, or more time negotiated with the client. Explain the risk in concrete terms (contractual breach,
data protection, client trust). If it already happened, follow the incident process. Then look at whether our approved
tools are hard to use, because shadow AI usually signals a gap we should fix.

### 21. How do you decide whether a use case is appropriate for AI at all?

**Model answer:** I look at the stakes of errors, whether outputs can be checked, whether the task needs accountability
that should stay with a person, legal and ethical constraints, and whether a simpler non-AI solution exists. High-stakes
decisions about individuals need human decision-makers with AI as support at most. If errors are cheap and verifiable,
AI can do more. I write the reasoning down so the decision is reviewable.

### 22. Tell me about a project that failed or that you stopped

**Model answer (example):** We piloted an assistant that drafted responses to complex supplier disputes. After four
weeks, reviewers accepted only 30% of drafts and editing took longer than writing. The cause was that key information
lived in phone calls, not in any system we could access. I recommended stopping, documented the lesson (check data
availability during discovery), and we redirected effort to a document-summary feature that later succeeded.

## Communication under pressure

### 23. How do you explain an AI incident to non-technical leadership?

**Model answer:** What happened, who was affected, what we did immediately, what we know and do not know yet, and when
the next update comes. Plain language, no blame, no speculation. Then the root cause and the fixes once confirmed,
including the process change that prevents recurrence.

### 24. How do you handle a stakeholder who overestimates what AI can do?

**Model answer:** Show, do not argue: run their real examples through a prototype, including hard cases, and review the
results together. Point out where it excels and where it fails. Reframe goals around realistic outcomes (for example,
first drafts in minutes rather than finished documents) and agree measurable targets.

### 25. And one who is sceptical of AI altogether?

**Model answer:** Take the concerns seriously; they are often valid (accuracy, jobs, data). Start with a low-risk,
high-friction task they care about, keep humans in control, measure the result against today's process, and share the
evidence. Invite them to help define the review process. Trust grows from demonstrated, measured results and from
being honest about limitations.

### 26. Why do you want to work on AI systems, and how do you stay current?

**Model answer:** Give a genuine, specific reason (for example, enjoying the mix of software engineering, product
thinking and risk management). For staying current: official documentation and changelogs, engineering blogs from
model providers, security guidance from OWASP and NIST, hands-on experiments with new features on a small eval set, and
sharing findings with the team. Mention one recent change you evaluated and what you concluded.
