# Exam Facts (verified)

> **Last verified:** 2026-10-24, against the official exam guides v1.0 (effective July 2026) published on the
> [Anthropic Partner Academy certifications page](https://anthropic-partners.skilljar.com/page/partner-certifications)
> and the [Pearson VUE Claude Certification Program page](https://www.pearsonvue.com/us/en/anthropic.html).
> The machine-readable version is [`registry.yaml`](../16-certification-tracks/registry.yaml).
>
> **Change ahead:** Pearson VUE says updated exam guides arrive on **2026-11-17** and that CCAO-F, CCDV-F and CCAR-P
> carry updated content from **2026-12-07**. If you sit an exam on or after 2026-12-07, use the updated guide.
> This page will be re-verified then; check the [verification log](verification-log.md) for the latest review.

## The program at a glance

| | |
|---|---|
| Program | Claude Certification Program (Anthropic) |
| Exams | Four, across three roles: Associate, Developer, Architect |
| Delivery | Pearson VUE, online proctored or at a test centre |
| Registration | Anthropic Partner Academy (Skilljar), then scheduling with Pearson VUE |
| Eligibility | Open to organisations in the **Claude Partner Network** |
| Item types | Multiple-choice and multiple-response; each item says how many responses to select |
| Scoring | Criterion-referenced; scaled score 100–1,000; **cut score 720**; score report shows percent-correct per domain |
| Validity | 12 months; on-time renewal is a free, non-proctored assessment; a lapsed credential means retaking the exam |
| Retakes | Wait 14 days after the 1st failed attempt, 30 after the 2nd, 90 after the 3rd; at most 4 attempts per exam in a rolling 12 months |
| Rescheduling | **Plan on 48 hours.** The v1.0 exam guides say 24 hours, but the Partner Academy FAQ and the Pearson VUE page (both checked 2026-10-24) say cancellations and reschedules must be made at least 48 hours ahead, or the fee is forfeited |
| Conduct | NDA covering all exam content; no AI tools, notes or second monitor during the exam |

> The free [Anthropic Academy](https://anthropic.skilljar.com/) courses are open to anyone, but they award
> certificates of completion, not certifications.

## Exam-by-exam

| Exam | Code | Items | Time | Fee (USD) | Status in this repo |
|---|---|---|---|---|---|
| Claude Certified Associate – Foundations | CCAO-F | 60 | 120 min | $99 | Full track: [ccao-f](../16-certification-tracks/ccao-f/README.md) |
| Claude Certified Architect – Professional | CCAR-P | 63 | 120 min | $175 | Full track: [ccar-p](../16-certification-tracks/ccar-p/README.md) |
| Claude Certified Architect – Foundations | CCAR-F | 60 | 120 min | $125 | Facts recorded; track planned |
| Claude Certified Developer – Foundations | CCDV-F | 53 | 120 min | $125 | Facts recorded; track planned |

Fees are list prices from the exam guides; the checkout price can reflect a partner-tier discount.

## Domain blueprints

### CCAO-F — Claude Certified Associate – Foundations

For professionals who use Claude as a productivity tool (operations, marketing, project management, education,
communications). No coding or API experience required.

| # | Domain | Weight |
|---|---|---|
| 1 | Prompting and Task Execution | 14% |
| 2 | Output Evaluation and Validation | 21% |
| 3 | Product and Model Selection | 12% |
| 4 | Workflow Integration and Solution Design | 16% |
| 5 | Configuration and Knowledge Management | 12% |
| 6 | Governance, Risk, and Responsible Use | 15% |
| 7 | Troubleshooting and Optimization | 10% |

### CCAR-P — Claude Certified Architect – Professional

For mid- to senior-level architects and engineers delivering production Claude systems. Recommended (not required):
3+ years in systems architecture or platform engineering and 6+ months hands-on with LLM systems in production.

| # | Domain | Weight |
|---|---|---|
| 1 | Solution Design & Architecture | 17% |
| 2 | Claude Models, Prompting & Context Engineering | 13% |
| 3 | Integration | 19% |
| 4 | Evaluation, Testing & Optimization | 16% |
| 5 | Governance, Safety & Risk Management | 14% |
| 6 | Stakeholder Communication & Lifecycle Management | 14% |
| 7 | Developer Productivity & Operational Enablement | 7% |

### CCAR-F — Claude Certified Architect – Foundations (track planned)

| # | Domain | Weight |
|---|---|---|
| 1 | Agentic Architecture & Orchestration | 27% |
| 2 | Tool Design & MCP Integration | 18% |
| 3 | Claude Code Configuration & Workflows | 20% |
| 4 | Prompt Engineering & Structured Output | 20% |
| 5 | Context Management & Reliability | 15% |

### CCDV-F — Claude Certified Developer – Foundations (track planned)

| # | Domain | Weight |
|---|---|---|
| 1 | Agents and Workflows | 14.7% |
| 2 | Applications and Integration | 33.1% |
| 3 | Claude Code | 3.1% |
| 4 | Eval, Testing, and Debugging | 2.6% |
| 5 | Model Selection and Optimization | 16.8% |
| 6 | Prompt and Context Engineering | 11.0% |
| 7 | Security and Safety | 8.1% |
| 8 | Tools and MCPs | 10.6% |

The detailed objectives for the supported tracks, with the IDs used throughout this repository, are in
[`registry.yaml`](../16-certification-tracks/registry.yaml).

## What this repository does not know

- How the 100–1,000 scale is computed, or whether multiple-response items earn partial credit. The guides do not say.
  The [mock-exam engine](../18-mock-examinations/README.md) therefore reports raw percent-correct and scores
  multiple-response items all-or-nothing, as an explicit assumption.
- The content of any live exam item. Exam content is confidential under the exam policy, and nothing here is
  derived from it.

> **About third-party figures:** several prep sites published different fees or domain lists before the v1.0 guides
> appeared. Where they conflict with the table above, the official guide wins.
