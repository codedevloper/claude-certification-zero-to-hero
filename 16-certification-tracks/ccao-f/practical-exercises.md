# CCAO-F Practical Exercises

> Part of the [CCAO-F track](README.md). Objective IDs come from [`registry.yaml`](../registry.yaml).

These exercises are done in the Claude apps (web, desktop or mobile), with no coding. Each one maps to objectives, takes
15–60 minutes, and has success criteria you can check yourself. Feature availability differs by plan (as of
2026-10-24: Projects on all plans; research, RAG mode for large Project knowledge and chat search on paid plans;
connectors may need an admin to enable them on Team and Enterprise). If a feature is unavailable to you, read the
matching Help Center article and complete the planning parts of the exercise.

**Ground rules for every exercise**

- Use fictional or public material, or work material your organisation's AI policy allows in your approved workspace.
- Use the synthetic examples provided here when in doubt. Never paste real personal data to complete an exercise.
- Keep a short exercise log (what you tried, what happened, what you changed). You will reuse it in
  [readiness-assessment.md](readiness-assessment.md).

---

## Domain 1 — Prompting and Task Execution

### Exercise 1.1 · From vague to specific (CCAO-F-1.1, 1.3)

1. Send this prompt in a new chat: `Write an announcement about the new expenses process.`
2. Note what is weak about the result.
3. Rewrite the prompt with goal, context, audience, constraints, format and success criteria. Invent the details: for
   example, *Tailspin Toys* moves from paper receipts to a mobile app on 1 March, with a one-month overlap, for 400
   field sales staff who mostly read email on their phones.
4. Compare the two outputs against three criteria you write before reading the second output.

**Success criteria:** your rewritten prompt contains all six elements; the second output meets all three criteria
without follow-up; you can say which added element made the biggest difference.

### Exercise 1.2 · Decompose a report (CCAO-F-1.2)

Task: produce a two-page "lessons learned" report from a fictional project retrospective. Ask Claude to generate
realistic synthetic retrospective notes from eight team members first.

1. Ask Claude to propose a step-by-step plan for producing the report, and edit the plan.
2. Run the steps in sequence (extract issues → group into themes → prioritise → draft → edit for executives), checking
   each intermediate output before continuing.
3. Run the whole task again as a single prompt and compare.

**Success criteria:** you caught and corrected at least one issue at an intermediate step; you can explain one
difference in quality between the chained and single-prompt versions.

### Exercise 1.3 · Four task types, one topic (CCAO-F-1.4)

Topic: reducing meeting overload in a 50-person department. Write four prompts: an **analysis** prompt (attach a
synthetic calendar summary), a **research** prompt (what approaches organisations commonly use, with sources), a
**drafting** prompt (an email to the department proposing a trial) and a **brainstorming** prompt (20 ideas across
categories, then a ranked top five).

**Success criteria:** each prompt uses the moves from the Domain 1 table for its type; the brainstorm returns varied
categories before ranking; the research output includes sources that you open and check.

---

## Domain 2 — Output Evaluation and Validation

### Exercise 2.1 · Hallucination hunt (CCAO-F-2.1, 2.2, 2.3)

1. Ask Claude to write a 500-word synthetic "industry briefing" about a fictional company, *Proseware Ltd*, using a fact
   sheet you write yourself with ten facts (founding year, headcount, products, revenue, and so on).
2. In a **new chat**, give Claude only the briefing and ask for a summary "including key statistics about Proseware's
   market position".
3. Compare every specific claim in the summary against your fact sheet.
4. Repeat step 2 with the instruction: "Use only the briefing. If a figure is not in it, write 'not stated'. Quote the
   sentence that supports each statistic."

**Success criteria:** you list every unsupported claim from step 2 (there may be none, or several); you explain why the
step 4 instruction changed the result; you verified the quotes in step 4 actually appear in the briefing.

### Exercise 2.2 · Risk-based review plan (CCAO-F-2.4)

List eight outputs you (or a fictional colleague) might produce with Claude in a month, such as meeting notes, a
customer FAQ, a board paper, a policy summary for staff, a performance-review draft and a supplier email. For each,
rate stakes, audience, reversibility, expertise needed and whether it affects individuals, then assign low, medium or
high review.

**Success criteria:** every output has a review level and a named reviewer role; anything affecting individuals or
leaving the organisation is at least medium; you can justify each high rating in one sentence.

### Exercise 2.3 · One message, three audiences (CCAO-F-2.5)

Take a synthetic incident summary (for example, a two-hour outage of a booking system at *Fabrikam Events*). Ask for
versions for executives, front-desk staff and customers. Then write criteria (accuracy, required points, tone, length,
action) and score each version.

**Success criteria:** all three versions keep the facts consistent (same duration, same cause, same next steps); you
caught and fixed any drift; the customer version contains no internal jargon or unapproved commitments.

### Exercise 2.4 · Choose the format (CCAO-F-2.6)

Ask Claude for the same content (a comparison of three fictional software vendors) in three formats: an inline answer,
an artifact (an editable document or interactive comparison) and a table you could paste into a spreadsheet.

**Success criteria:** you can state which format suits (a) a quick decision in a chat, (b) a document to share with a
committee, (c) feeding a procurement tracker, and why.

---

## Domain 3 — Product and Model Selection

### Exercise 3.1 · Feature picker (CCAO-F-3.1)

For each request, pick the feature (chat, Project, research, web search, artifact, connector, Skill, incognito chat)
and write one sentence of justification. Then try at least three of them.

1. "Answer customers' questions about our returns policy consistently across a team of six."
2. "What did the central bank announce this morning?"
3. "Build a simple interactive checklist new starters can use in week one."
4. "Map the regulatory landscape for drone deliveries across five countries, with sources."
5. "Find last week's email thread with the venue and draft a reply."
6. "Apply our standard 8-section post-incident review format every time, in any Project."

**Success criteria:** your choices match the decision rules in [Domain 3](study-guide/domain-3.md); for each one tried,
you note one limitation you observed.

### Exercise 3.2 · Model comparison (CCAO-F-3.2, 3.3)

Pick three tasks of different difficulty: rewriting ten product names into title case; summarising a two-page synthetic
memo; analysing a messy, contradictory set of meeting notes to recommend a decision. Run each on two or three of the
models available to you.

**Success criteria:** a small table of task × model with quality (1–5), response time (rough) and your pick; for at
least one task, the lighter model was good enough, and for at least one, the more capable model was clearly better
(or you can explain why not).

### Exercise 3.3 · Restart, summarise, persist (CCAO-F-3.4)

Run a deliberately long, multi-topic chat (planning a fictional team offsite: venue, agenda, budget, travel). After
about 30 exchanges, ask Claude for a handover summary of decisions, open questions and key facts. Verify it against the
chat. Start a fresh chat with only the summary and continue. Then decide which items should be persisted in a Project
(knowledge or instructions) and which should not.

**Success criteria:** the summary is verified and corrected before reuse; the new chat continues without needing old
details; you can explain one thing you put in Project knowledge and one you deliberately left out.

---

## Domain 4 — Workflow Integration and Solution Design

### Exercise 4.1 · Use-case screening (CCAO-F-4.1, 4.5)

Ask Claude to interview you (one question at a time) about a real or fictional team's weekly work, then produce a list
of candidate use cases scored on frequency, effort, checkability, risk and data sensitivity.

**Success criteria:** at least one candidate is rejected or deferred for risk or data reasons; you pick one pilot and
can explain why in three sentences.

### Exercise 4.2 · Before-and-after process map (CCAO-F-4.2, 4.4)

Describe a current process (for example, producing a monthly project status report from three teams' updates). Ask
Claude to map it, identify bottlenecks, and propose augment, automate-a-step and redesign options with trade-offs.
Produce the future-state map as an artifact.

**Success criteria:** the future state has a named human checkpoint before anything leaves the team; you can name the
baseline measure (for example, hours per report) you would track.

### Exercise 4.3 · Prototype a small tool (CCAO-F-4.3)

Use an artifact to build a small interactive tool for your pilot, such as an intake form that turns a request into a
structured brief, or a checklist with scoring. Test it with three realistic inputs, including an awkward one, and
iterate twice.

**Success criteria:** the tool handles all three inputs; you logged what changed in each iteration and why.

### Exercise 4.4 · One-page value brief (CCAO-F-4.5)

Write a one-page brief for a sponsor about your pilot: problem and baseline, what Claude does and what people do,
evidence (including at least one failure), limitations and controls, cost, decision needed. Ask Claude to critique it
as a sceptical finance director, then revise.

**Success criteria:** the brief contains no unqualified claims ("always accurate", "fully automated"); limitations and
controls are as visible as benefits.

---

## Domain 5 — Configuration and Knowledge Management

### Exercise 5.1 · Build a Project (CCAO-F-5.1, 5.3)

Create a Project called "Policy Helper – Synthetic". Ask Claude (in a separate chat) to generate three short synthetic
policy documents for a fictional company: travel, expenses and remote working. Upload them as Project knowledge. Write
instructions using the structure in [Domain 5](study-guide/domain-5.md) (purpose, audience, knowledge use, format,
rules, when unsure).

Test with eight questions: five answerable from the documents, two not covered by them, and one that should be referred
to a human (for example, a request for an exception).

**Success criteria:** the five answers are correct and cite the right document; the two uncovered questions get "not in
the documents" rather than invented answers; the exception request is referred, not granted.

### Exercise 5.2 · Knowledge hygiene (CCAO-F-5.2, 5.4)

Add a second, conflicting version of the travel policy (different per-diem rate) to the Project. Ask the same travel
questions again and note the behaviour. Then remove the old version, rename the current file with a version and date,
add a "cite the document and date" rule, and retest.

**Success criteria:** you observed the effect of conflicting knowledge; after the fix, answers are consistent and cite
the dated file; you recorded the change in a short change log.

### Exercise 5.3 · Connector review (CCAO-F-5.2)

If you have a connector available (for example Google Drive or Gmail in an approved workspace), connect it and ask
Claude to find a specific non-sensitive document. If not, read the
[connectors](https://support.claude.com/en/articles/11176164-use-connectors-to-extend-claude-s-capabilities) article.
Either way, write a one-paragraph "connector decision note": what the connector can reach, whose permissions it uses,
which admin settings apply, and when you would use upload instead.

**Success criteria:** the note correctly states that the connector uses your own access, that Team and Enterprise
owners enable connectors and can restrict actions, and that custom connectors are not verified by Anthropic.

### Exercise 5.4 · Write a Skill outline (CCAO-F-5.3)

Write (on paper or in a document) the `SKILL.md` content for a repeatable procedure, such as your team's meeting-minutes
format: name, when to use it, steps, output format and one example. If Skills are enabled for you, upload it following
the [Help Center steps](https://support.claude.com/en/articles/12512180-use-skills-in-claude) and test it.

**Success criteria:** the description says clearly when the Skill applies; the steps are specific enough that two
people would get the same structure.

---

## Domain 6 — Governance, Risk, and Responsible Use

### Exercise 6.1 · Redact before you analyse (CCAO-F-6.2)

Ask Claude to generate a synthetic table of 20 employee exit-interview comments that include fake names, team names,
manager names and occasional personal details. Treat it as if it were real and restricted.

1. Redact or pseudonymise the table yourself (for example, Employee 01, Manager A), keeping the key in a separate
   document that never goes into Claude.
2. Remove details not needed for theme analysis.
3. In a new chat, analyse themes using only the de-identified version.

**Success criteria:** no direct identifiers remain in the analysed version; the analysis still produces useful themes;
you can explain why "telling Claude not to remember the names" would not have been an acceptable alternative.

### Exercise 6.2 · Appropriateness triage (CCAO-F-6.1, 6.4)

Classify ten proposed uses as appropriate, appropriate with extra controls, or inappropriate, and give the control or
alternative for each. Suggested list: drafting a team newsletter; summarising public research; ranking job applicants
for automatic rejection; drafting customer apology letters; writing fake product reviews; translating an internal FAQ;
summarising a patient's medical record for a doctor; generating a first draft of a contract clause; analysing
anonymised sales data; producing a speech that imitates a real executive without their consent.

**Success criteria:** every "inappropriate" item has a stated reason and an alternative where one exists; every "extra
controls" item names the control (expert review, approval, anonymisation, disclosure).

### Exercise 6.3 · Map your policy (CCAO-F-6.3)

Find your organisation's AI policy (or, if none, use a public example policy from a government or university). Build a
one-page cheat sheet: approved tools, data rules, review requirements, disclosure rules, incident reporting route.

**Success criteria:** you can answer "can I use Claude for X with data Y?" for five scenarios from your cheat sheet
alone, and you know who to ask when it does not say.

---

## Domain 7 — Troubleshooting and Optimization

### Exercise 7.1 · Break and fix (CCAO-F-7.1)

In your Policy Helper Project from Exercise 5.1, introduce three faults one at a time: a contradictory instruction
("be brief" and "be comprehensive"), an outdated knowledge file, and a vague format rule. For each, observe the symptom,
diagnose using the table in [Domain 7](study-guide/domain-7.md), fix it and retest with your eight test questions.

**Success criteria:** for each fault you recorded symptom → cause → fix → retest result; all eight test questions pass
after the final fix.

### Exercise 7.2 · Feedback loop (CCAO-F-7.2)

Ask a colleague (or Claude acting as a strict reviewer with a rubric you supply) to review five outputs from your
Project. Group the feedback into recurring issues, change one thing, and re-run the same five requests.

**Success criteria:** at least one recurring issue is fixed in configuration, not chat by chat; you compared before and
after on the same inputs.

### Exercise 7.3 · Efficiency audit (CCAO-F-7.3)

Review one week of your own Claude use. Identify: repeated uploads that could be Project knowledge; prompts you retype
that could be instructions or a Skill; long chats that should have been restarted; tasks that could use a lighter
model; review effort that is too high or too low for the risk.

**Success criteria:** at least three concrete changes, each with an expected benefit and a quality measure you will
watch so that efficiency does not come at the cost of accuracy.

---

## Mapping summary

| Exercise | Objectives |
|---|---|
| 1.1–1.3 | CCAO-F-1.1, 1.2, 1.3, 1.4 |
| 2.1–2.4 | CCAO-F-2.1 to 2.6 |
| 3.1–3.3 | CCAO-F-3.1 to 3.4 |
| 4.1–4.4 | CCAO-F-4.1 to 4.5 |
| 5.1–5.4 | CCAO-F-5.1 to 5.4 |
| 6.1–6.3 | CCAO-F-6.1 to 6.4 |
| 7.1–7.3 | CCAO-F-7.1 to 7.3 |

If you code, the [hands-on labs](../../19-hands-on-labs/README.md) cover the same ideas through the API; the
[objective map](objective-map.yaml) lists the lab for each objective.
