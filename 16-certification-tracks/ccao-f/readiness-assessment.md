# CCAO-F Readiness Assessment

> Part of the [CCAO-F track](README.md). Objective IDs and domain weights come from [`registry.yaml`](../registry.yaml).
> This is a self-assessment tool. It cannot predict your official result.

Use this page three times: at the start (baseline), halfway through your preparation, and about a week before your
exam. Copy the tables into your own notes and fill them in.

## Confidence scale

| Score | Meaning |
|---|---|
| 1 | I do not know what this objective means |
| 2 | I understand it when I read about it, but could not apply it |
| 3 | I can apply it in a familiar situation with some effort |
| 4 | I apply it routinely at work and can explain the reasoning |
| 5 | I could teach it, including edge cases and common traps |

Be honest: an inflated score only hides a gap until exam day. For each objective, the "evidence" column describes what
you should be able to show if you rate yourself 4 or higher.

## Domain 1 · Prompting and Task Execution (14%)

| ID | Objective (paraphrased) | Evidence for a 4+ | Start | Mid | Final |
|---|---|---|---|---|---|
| CCAO-F-1.1 | Write effective prompts for business and technical tasks | You routinely include goal, context, audience, constraints, format and success criteria | | | |
| CCAO-F-1.2 | Decompose complex requests into sub-tasks | You chained a multi-step task and caught an error between steps (Exercise 1.2) | | | |
| CCAO-F-1.3 | Iterate on prompts to improve quality | You can show a prompt history where each change addressed a named problem | | | |
| CCAO-F-1.4 | Adapt strategy to task type | You can state the key prompt moves for analysis, research, drafting and brainstorming | | | |

## Domain 2 · Output Evaluation and Validation (21%)

| ID | Objective (paraphrased) | Evidence for a 4+ | Start | Mid | Final |
|---|---|---|---|---|---|
| CCAO-F-2.1 | Evaluate accuracy and completeness | You check outputs against the brief and all sources, item by item | | | |
| CCAO-F-2.2 | Spot hallucinations, inconsistencies and bias | You found unsupported claims in Exercise 2.1 and can list the warning signs | | | |
| CCAO-F-2.3 | Apply fact-checking and validation | You verify against primary sources and open citations, never relying on self-rated confidence | | | |
| CCAO-F-2.4 | Decide when human review is needed | You built a risk-based review plan (Exercise 2.2) using the six factors | | | |
| CCAO-F-2.5 | Edit, adapt and compare outputs for an audience | You produce audience versions without factual drift and compare against set criteria | | | |
| CCAO-F-2.6 | Curate information and choose formats | You choose between inline, artifact and structured data based on the next step | | | |

## Domain 3 · Product and Model Selection (12%)

| ID | Objective (paraphrased) | Evidence for a 4+ | Start | Mid | Final |
|---|---|---|---|---|---|
| CCAO-F-3.1 | Choose the right product feature | You match scenario signals to Projects, research, web search, artifacts, connectors, Skills, memory | | | |
| CCAO-F-3.2 | Differentiate Haiku, Sonnet and Opus | You can describe each tier's position and typical tasks | | | |
| CCAO-F-3.3 | Match model to cost, speed and quality | You compared models on real tasks (Exercise 3.2) and picked the cheapest adequate one | | | |
| CCAO-F-3.4 | Manage context limits and memory | You know when to restart, summarise or persist, and where each kind of information belongs | | | |

## Domain 4 · Workflow Integration and Solution Design (16%)

| ID | Objective (paraphrased) | Evidence for a 4+ | Start | Mid | Final |
|---|---|---|---|---|---|
| CCAO-F-4.1 | Analyse requirements and use cases | You screened use cases on frequency, checkability, risk and data | | | |
| CCAO-F-4.2 | Use Claude for research, planning and process optimisation | You produced a process map with bottlenecks and options (Exercise 4.2) | | | |
| CCAO-F-4.3 | Support solution design and iteration | You prototyped and iterated a small tool against test inputs (Exercise 4.3) | | | |
| CCAO-F-4.4 | Integrate Claude into workflows | You can distinguish augment, automate and redesign, and place the human checkpoint | | | |
| CCAO-F-4.5 | Communicate value and limitations | You wrote a balanced one-page brief with evidence, failures and controls | | | |

## Domain 5 · Configuration and Knowledge Management (12%)

| ID | Objective (paraphrased) | Evidence for a 4+ | Start | Mid | Final |
|---|---|---|---|---|---|
| CCAO-F-5.1 | Configure Projects with instructions and knowledge | You built and tested a Project (Exercise 5.1) | | | |
| CCAO-F-5.2 | Manage knowledge and connectors | You can explain upload versus connector, per-user access and admin controls | | | |
| CCAO-F-5.3 | Write effective system-level instructions | You can write the six-part instruction template from memory | | | |
| CCAO-F-5.4 | Maintain configurations over time | Your Project has an owner, review date, change log and test set | | | |

## Domain 6 · Governance, Risk, and Responsible Use (15%)

| ID | Objective (paraphrased) | Evidence for a 4+ | Start | Mid | Final |
|---|---|---|---|---|---|
| CCAO-F-6.1 | Distinguish appropriate from inappropriate use | You triaged ten uses with controls or alternatives (Exercise 6.2) | | | |
| CCAO-F-6.2 | Apply data-sensitivity, regulatory and privacy considerations | You de-identified a dataset before analysis (Exercise 6.1) | | | |
| CCAO-F-6.3 | Follow AI policy and governance | You have a one-page summary of your organisation's AI policy and know who to ask | | | |
| CCAO-F-6.4 | Understand ethical implications | You can discuss fairness, transparency, accountability and over-reliance with examples | | | |

## Domain 7 · Troubleshooting and Optimization (10%)

| ID | Objective (paraphrased) | Evidence for a 4+ | Start | Mid | Final |
|---|---|---|---|---|---|
| CCAO-F-7.1 | Diagnose and fix poor outputs | You fixed three injected faults by symptom → cause → fix (Exercise 7.1) | | | |
| CCAO-F-7.2 | Adjust based on feedback and results | You ran a feedback loop with before-and-after comparison (Exercise 7.2) | | | |
| CCAO-F-7.3 | Optimise workflows | You completed an efficiency audit with quality safeguards (Exercise 7.3) | | | |

## Weighted readiness score (optional)

To see where effort pays off most, compute a weighted average:

1. For each domain, average your objective scores.
2. Multiply each domain average by its weight (14, 21, 12, 16, 12, 15, 10), add them and divide by 100.

A low score in Domain 2 (21%) costs more than the same score in Domain 7 (10%). Prioritise accordingly, but do not
ignore any domain: every domain contributes items.

## Readiness criteria

You are likely ready to book (or to keep your booking) when **all** of the following hold:

- [ ] **Every objective is rated 3 or higher**, and at least three quarters are 4 or higher.
- [ ] **No domain average is below 3.5.**
- [ ] **Consistent mock-exam results by domain:** across at least two full, timed [mock exams](../../18-mock-examinations/README.md)
      taken on different days, you scored comfortably above your target in every domain, not just overall, and your
      weakest domain is stable or improving.
- [ ] **Practice questions explained, not just answered:** for the
      [CCAO-F practice questions](../../17-practice-questions/README.md) you got wrong, you can explain why the right
      answer is right and why your choice was wrong.
- [ ] **Hands-on evidence:** you have completed at least one exercise per domain in
      [practical-exercises.md](practical-exercises.md), including building and testing a Project.
- [ ] **Pacing:** you finished a 60-item mock within 120 minutes with time to review flagged items.
- [ ] **Logistics done:** ID name matches registration, system test passed (online) and [exam-day.md](exam-day.md) read.

> **Important:** unofficial scores, including this repository's mock exams, practice questions and any third-party
> tests, **do not equal the official scaled score**. The official exam uses a scaled score on a 100–1,000 scale set by
> a standard-setting study (see [`registry.yaml`](../registry.yaml)); how raw performance converts to that scale is not
> published. This repository's mock engine reports raw percent-correct and scores multiple-response items
> all-or-nothing as an explicit assumption. Use unofficial results to find weak areas and track trends, never to
> predict a pass.

## Next steps by result

| Your situation | What to do next |
|---|---|
| Several objectives at 1–2 | Work through the matching study guide sections and module pages before attempting more questions |
| Objectives at 3 but mock scores uneven by domain | Do the practical exercises for weak domains; read [decision-scenarios.md](decision-scenarios.md) and [common-misconceptions.md](common-misconceptions.md) |
| Domain 2 or 6 weak | These are judgement-heavy: practise verification and data-minimisation on real (approved) work every day for a week |
| Good knowledge but running out of time | Practise timed sets of 15 items in 30 minutes; apply the pacing checkpoints in [exam-day.md](exam-day.md) |
| All criteria met | Book the exam; in the final week use [revision-notes.md](revision-notes.md) and the [flashcards](../../23-flashcards/README.md) |
| Exam on or after 2026-12-07 | Check the updated official guide (due 2026-11-17) for changed objectives and re-rate yourself against it |

## Reassess

After each study block, rerun the relevant domain table. Record the date and your scores so you can see trends. If an
objective will not move past 3 after two attempts, try a different resource: a hands-on exercise, a decision scenario, a
module page or explaining the topic to a colleague.
