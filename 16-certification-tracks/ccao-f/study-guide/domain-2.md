# Domain 2 · Output Evaluation and Validation (21%)

> Part of the [CCAO-F track](../README.md). Objective IDs and weights come from [`registry.yaml`](../../registry.yaml).
> This is the heaviest domain on the exam. Objectives are paraphrased; the official exam guide is the source of truth.

## Objectives

| ID | What you must be able to do (paraphrased) |
|---|---|
| CCAO-F-2.1 | Judge whether an output is accurate and complete |
| CCAO-F-2.2 | Recognise hallucinations, internal inconsistencies and bias |
| CCAO-F-2.3 | Use fact-checking and validation techniques |
| CCAO-F-2.4 | Decide when human review or extra verification is required |
| CCAO-F-2.5 | Edit, adapt and compare outputs so they suit the intended audience |
| CCAO-F-2.6 | Organise information and pick the right output format: an artifact, an inline answer or structured data |

## Concepts to master

- Accuracy versus completeness: a summary can be correct and still miss the one point that matters.
- Hallucination: fluent, confident, specific-looking content that is not supported by any source.
- Grounding: tying claims to a specific source the reader can check.
- Confidence is not evidence. How sure Claude sounds says nothing about whether it is right.
- Risk-based review: the higher the stakes and the wider the audience, the more verification.
- Bias: skewed framing, stereotypes, one-sided sourcing or uneven treatment of groups.
- Format choice: inline text for quick answers, artifacts for substantial reusable work, structured data for anything
  that goes into another system.

## Detailed notes

### 2.1 Accuracy and completeness

Evaluate an output against the **task**, not against your impression of it. Before you read the answer, write down (or
at least think through) what a correct and complete answer must contain. Then check:

| Check | Question |
|---|---|
| Correctness | Is each factual statement true and supported by the source? |
| Completeness | Did it cover every item you asked for, every document you gave it and every requirement in the brief? |
| Faithfulness | Does the summary say what the source says, without adding, softening or exaggerating? |
| Currency | Is the information current? Claude's built-in knowledge has a training cut-off, and documents can be out of date. |
| Fitness | Does it answer the actual question for the actual audience? |

Completeness failures are common with long inputs. If you gave Claude five supplier contracts, check that the
comparison actually draws on all five. Ask directly: "Which documents did you use for each row?"

### 2.2 Hallucinations, inconsistencies and bias

Language models generate likely-sounding text. Most of the time that text is right, but they can produce specific
details that look authoritative and are invented. Warning signs:

- Precise numbers, dates, clause numbers, case names, quotations or URLs that you did not supply.
- Names of people, products or reports you cannot find anywhere.
- Statements that go beyond the source ("the contract guarantees...") where the source is silent.
- Answers to questions about recent events without any search or source.

**Internal inconsistency** is easier to catch: totals that do not add up, a date in the summary that differs from the
date in the table, a recommendation that contradicts the analysis above it. Read the output once just for consistency.

**Bias** shows up as one-sided framing, assumptions about gender, age, culture or role, uneven tone when describing
different groups, or recommendations that disadvantage a group without justification. In hiring, lending, performance,
health and education contexts, bias checks are not optional. Useful tests: swap the group or name and see whether the
output changes; ask for the strongest counter-argument; check whose perspective is missing.

### 2.3 Fact-checking and validation techniques

| Technique | How it works | Good for |
|---|---|---|
| Check against the primary source | Open the original document, regulation or dataset and confirm the claim | Any claim that will be relied on |
| Ask for citations or quotes | "Quote the sentence that supports each point" | Document-grounded summaries |
| Verify the citation itself | Confirm the quoted text exists and says what is claimed | Catching invented or misattributed quotes |
| Recalculate | Redo key numbers in a spreadsheet or calculator, or ask Claude to show its working and check it | Financial or statistical output |
| Cross-check with an independent source | Look up the fact somewhere Claude did not use | Research findings, external facts |
| Ask Claude to critique its own draft | "List any claims above that are not supported by the attached material" | A first filter, never the last |
| Spot-check samples | For long or repeated outputs, verify a sample of items thoroughly | High-volume work where full review is impractical |
| Subject-matter review | A qualified person reviews the content | Legal, medical, financial, safety, regulatory |

Self-critique is useful because it often surfaces gaps, but it is not independent verification. Asking Claude "Are you
sure?" or "Rate your confidence" does not prove anything. The validation step must touch a source outside the model's
own answer.

The research feature in the Claude apps returns findings with citations, which makes checking easier, but citations
still need spot-checking: open a few and confirm they support the claim.

### 2.4 When human review is needed

Use a simple risk lens. Each "yes" increases the level of review.

1. **Stakes.** Could an error cause financial, legal, safety, health or reputational harm?
2. **Audience.** Will it leave your team, go to customers, regulators, the public or senior leaders?
3. **Irreversibility.** Once sent or published, can it be corrected easily?
4. **Domain expertise.** Does judging correctness need specialist knowledge you do not have?
5. **Novelty.** Is this a new kind of task or a new data source where you have no track record?
6. **Decisions about people.** Does it affect someone's job, access, money or rights?

| Risk | Example | Review |
|---|---|---|
| Low | Internal meeting notes, brainstorm list | Quick read by the author |
| Medium | Team-wide process doc, customer FAQ draft | Author verifies facts; peer review |
| High | Contract language, regulatory filing, medical or financial advice, decisions about individuals | Qualified expert review and sign-off; Claude output is a draft only |

Escalation is part of the skill being certified: the Associate recognises when the work exceeds their remit and hands it
to a subject-matter expert, or to Claude Architects or Developers when the task needs technical design.

### 2.5 Editing, adapting and comparing for the audience

The same facts need different treatment for different readers. Ask Claude for audience-specific versions, then check
each one for drift: shortening and simplifying are where meaning is most often lost.

- **Executives:** decision first, three supporting points, risks, ask.
- **Frontline staff:** what changes for them, what to do, by when, where to get help.
- **Customers:** plain language, no internal jargon, accurate commitments only.
- **Technical teams:** precise detail, assumptions, edge cases.

When comparing outputs (two drafts, two models, two prompts), compare against **explicit criteria** written in advance
(accuracy, coverage of required points, tone, length, actionability), not against gut feel. A simple scoring table
avoids the "the longer one looks better" trap.

Always do the final edit yourself. You are accountable for what you send, and your name, not Claude's, is on it.

### 2.6 Curating information and choosing an output format

| Format | Choose it when | Examples |
|---|---|---|
| **Inline response** | Short, conversational, one-off answer you will read and act on | Quick explanation, a few options, a short reply draft |
| **Artifact** | Substantial, self-contained content you will edit, reuse or share; documents, decks, dashboards or small interactive tools | Policy draft, project plan, interactive checklist, data dashboard |
| **Structured data** (table, CSV, JSON) | Output feeds another tool or needs sorting, filtering or comparison | Extracted contract terms, tracker rows, a comparison matrix |
| **File output** (for example a spreadsheet or document) | The deliverable must live in another application | A formatted Excel sheet, a Word document |

As of 2026-10-24, the Claude Help Center describes an artifact as a piece of work you could show to someone (a
document, deck, dashboard, design or small tool) that opens beside the conversation, can be edited and shared, and is
saved to the Artifacts tab. Artifacts need the code execution and file creation capability ("Create and edit files")
switched on in settings. On Free, Pro and Max, a published artifact can be viewed by anyone with the link; on Team and
Enterprise, sharing stays within the organisation. See
[What are artifacts?](https://support.claude.com/en/articles/17153992-what-are-artifacts-and-how-do-i-use-them).

Curation means more than formatting: decide what to leave out, group related points, put the most important item
first and label uncertainty. A well-curated one-page table is often worth more than a complete ten-page narrative.

## Decision rules and heuristics

- **Specific details you did not supply are the first things to verify.**
- **Confidence is not a validation method.** Neither is asking Claude whether it is sure.
- **Verify in proportion to stakes and audience.** External, irreversible or people-affecting output gets expert review.
- **Check completeness against the brief, item by item**, especially with several source documents.
- **Compare against criteria written in advance**, not against impressions.
- **Pick the format for the next step**: will a human read it, edit it, share it or load it into another tool?
- **The human who sends it owns it.**

## Worked mini-scenarios

**Scenario 1 – The tidy benefits summary.** An HR generalist at *Northwind Lending* asks Claude to summarise a new
parental-leave policy for staff. The summary is clear and lists "18 weeks of paid leave". The policy says 16 weeks paid
plus 2 weeks unpaid. *Lesson:* figures that matter to readers must be checked against the source; a small numeric drift
here would create real employee-relations problems. Ask Claude to quote the sentence supporting each figure, check the
quotes, then send.

**Scenario 2 – The missing region.** An operations analyst attaches four regional reports and asks for a combined risk
summary. The output is good, but the APAC report never appears. *Lesson:* completeness check. Ask "list which report
each risk came from"; the gap becomes obvious.

**Scenario 3 – Format for the next step.** A procurement team wants to extract renewal dates and notice periods from 30
supplier contracts into their tracker. An inline narrative would need re-typing. *Better:* ask for a table with fixed
columns (supplier, renewal date, notice period, source clause) and spot-check a sample against the contracts.

**Scenario 4 – Bias in a job advert.** A recruiter asks for a job advert for a warehouse supervisor. The draft uses
heavily gendered language and an unnecessary "young, energetic team" phrase. *Lesson:* review people-related outputs for
bias and legal risk; remove age-coded and gendered wording; follow your organisation's inclusive-language guidance.

## Common traps

- Trusting polished formatting as a sign of accuracy.
- Verifying only the parts that look suspicious instead of the parts that matter most.
- Treating a citation as proof without opening it.
- Asking Claude to grade itself and stopping there.
- Assuming a summary is complete because it reads well.
- Sending a customer-facing draft without a human edit.
- Choosing an artifact for a one-line answer, or a chat reply for data that must go into a spreadsheet.

## Modules and labs

| Objective | Module pages | Labs |
|---|---|---|
| 2.1 | [Why evaluate](../../../14-evaluation-and-testing/01-why-evaluate.md), [Metrics](../../../14-evaluation-and-testing/02-metrics.md), [Capabilities and limitations](../../../01-ai-and-llm-fundamentals/07-capabilities-and-limitations.md) | [Lab 04](../../../19-hands-on-labs/lab-04-document-grounded-qa/README.md), [Lab 16](../../../19-hands-on-labs/lab-16-evaluation-framework/README.md) |
| 2.2 | [Hallucinations](../../../01-ai-and-llm-fundamentals/06-hallucinations.md), [Grounding and citations](../../../11-rag-and-knowledge-systems/05-grounding-and-citations.md), [Responsible use](../../../02-claude-fundamentals/05-responsible-use.md) | [Lab 04](../../../19-hands-on-labs/lab-04-document-grounded-qa/README.md), [Lab 16](../../../19-hands-on-labs/lab-16-evaluation-framework/README.md) |
| 2.3 | [Grounding and citations](../../../11-rag-and-knowledge-systems/05-grounding-and-citations.md), [Grading methods](../../../14-evaluation-and-testing/04-grading-methods.md) | [Lab 04](../../../19-hands-on-labs/lab-04-document-grounded-qa/README.md) |
| 2.4 | [Human oversight](../../../12-ai-security/13-human-oversight.md), [Human in the loop](../../../10-agentic-ai/05-human-in-the-loop.md) | [Lab 13](../../../19-hands-on-labs/lab-13-human-in-the-loop/README.md) |
| 2.5 | [Iterating on prompts](../../../03-prompt-engineering/08-iterating-on-prompts.md), [Clear instructions](../../../03-prompt-engineering/01-clear-direct-instructions.md) | [Lab 02](../../../19-hands-on-labs/lab-02-prompt-improvement/README.md), [Lab 06](../../../19-hands-on-labs/lab-06-model-comparison/README.md) |
| 2.6 | [Artifacts and output formats](../../../05-claude-products-and-models/05-artifacts-and-output-formats.md), [Structured output](../../../03-prompt-engineering/06-structured-output.md) | [Lab 03](../../../19-hands-on-labs/lab-03-structured-outputs/README.md) |

Hands-on: [practical exercises for Domain 2](../practical-exercises.md#domain-2--output-evaluation-and-validation).

## Self-check

1. Why is "ask Claude how confident it is" not a validation technique?
2. Name three warning signs of a possible hallucination.
3. List three factors that raise the level of human review needed.
4. You need extracted invoice data loaded into a finance tool. Which output format, and why?
5. How do you test a draft for bias towards one group?

<details>
<summary>Answers</summary>

1. Self-reported confidence comes from the same model that produced the answer; it is not independent evidence.
   Validation has to check against a source outside the answer.
2. Any three of: precise figures, dates, clause numbers, quotes or URLs you did not provide; names you cannot find;
   claims that go beyond what the source says; answers about recent events with no source.
3. Any three of: high stakes, external or senior audience, irreversibility, need for specialist expertise, novel task or
   data, decisions affecting individuals.
4. Structured data (a table or CSV with fixed columns), because it goes into another system and needs to be
   machine-readable and checkable row by row.
5. Swap names or group descriptors and compare the outputs; ask for the strongest counter-view; check whose perspective
   is missing; review for stereotyped or coded language.

</details>
