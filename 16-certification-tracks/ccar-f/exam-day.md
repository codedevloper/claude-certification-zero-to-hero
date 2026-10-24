# CCAR-F Exam Day

> Logistics, rules and pacing. Exam facts come from [`registry.yaml`](../registry.yaml) (verified 2026-10-24).
> Delivery rules come from the [Pearson VUE Claude Certification page](https://www.pearsonvue.com/us/en/anthropic.html)
> and the [Partner Academy certifications page](https://anthropic-partners.skilljar.com/page/partner-certifications);
> the official exam guide and your confirmation email take precedence over this page.

## The exam in one table

| Fact | Value |
|---|---|
| Items | 60 (multiple-choice and multiple-response; each item states how many to select) |
| Structure | 4 scenarios drawn at random from a published bank of 6 |
| Time | 120 minutes |
| Passing standard | Scaled score 720 on a 100–1,000 scale |
| Result | Pass/fail, scaled score, percent-correct by domain |
| Delivery | Pearson VUE: online proctored (OnVUE) or test centre |

## Before the day

- **Name and ID.** Your registration name must exactly match your valid, government-issued photo ID. To correct
  it, contact Anthropic certification support before scheduling, as the exam guide directs.
- **Rescheduling.** Treat 48 hours before the appointment as the deadline (the registry records that the Partner
  Academy and Pearson VUE pages require 48 hours, although the v1.0 guide says 24). Later changes and no-shows
  forfeit the fee.
- **Accommodations.** Request and get approval through Pearson VUE *before* you schedule.
- **Online proctoring.** Run the OnVUE system test on the exact machine and network you will use. Corporate VPNs and
  locked-down laptops often fail it.
- **Room.** Quiet, private, clear desk, no second monitor, phone out of reach.
- **Revise the six scenarios.** Skim [`scenarios.md`](scenarios.md) the day before: the architecture and traps for
  each. You will see four of them.

## Rules during the exam

> **Source:** the CCAR-F exam guide v1.0 (sections 12–14), checked 2026-10-24. Pearson VUE sets the detailed
> check-in procedure; read the agreement presented when you register and at check-in.

- **No materials, devices or people.** No notes, books, phones, smart watches, headphones or recording devices.
  Any permitted scratch material is specified by Pearson VUE.
- **No AI tools.** Do not use Claude or any other assistant during the exam.
- **Stay in view** of the webcam for the whole session if testing online.
- **Confidentiality.** You must accept a non-disclosure agreement covering questions, answer options **and
  scenarios**. Do not share, post or reconstruct any of it afterwards, including the wording of the scenarios as
  they appear on the exam. This repository's practice material is original for that reason.

## Pacing for 60 items in 120 minutes

- **Average:** 2 minutes per item. Scenario items add reading time up front: each scenario's context is read once
  and then supports several questions.
- **Plan:** for each scenario, spend about two minutes reading the context and noting its constraints, then about
  1 minute 30 seconds per item, flagging anything slow. That finishes a first pass in roughly 100 minutes and leaves
  about 20 minutes for flagged items.

| Checkpoint | Target |
|---|---|
| 30 minutes | First scenario finished (about item 15) |
| 60 minutes | About item 30 |
| 90 minutes | About item 45 |
| 100 minutes | First pass complete |
| 120 minutes | Every item answered (assume no penalty for guessing unless the guide says otherwise) |

The number of items per scenario is not published; assume they are roughly even and adjust at each checkpoint.

## Working a scenario

1. **Read the scenario context once, carefully.** Note the product (Agent SDK, Claude Code, API), the goal (a
   resolution rate, actionable feedback, high accuracy) and any constraint.
2. **For each item, read the stem first.** Look for "most effective", "first", "most reliable", "least effort".
3. **Return to the scenario only for the detail the item needs.** Do not re-read the whole context every time.
4. **Answer the item in front of you.** Each question is independent even when the scenario is shared.

## Multiple-response strategy

- Select exactly the number of options the item asks for.
- Judge each option true or false against the scenario before comparing them.
- Watch for options that are true statements but do not solve the problem asked about.
- Treat each multiple-response item as all-or-nothing unless the official guide says otherwise.

## Reading CCAR-F items

| Clue in the stem | What it usually rewards |
|---|---|
| "Must always", "guarantee", "compliance" | Programmatic enforcement: hooks, server-side checks, permission rules |
| "The agent ignores", "picks the wrong tool" | Better tool descriptions, fewer and narrower tools, removing keyword triggers |
| "Subagent did not use", "lost the source" | Pass complete context and structured metadata in the brief |
| "New team member", "inconsistent across developers" | Move configuration from user scope to project scope |
| "Only for certain files" | `.claude/rules/` with `paths` globs |
| "Floods the context", "answers get vague" | Subagents, forked skills, trimming, scratchpads, `/compact` |
| "In the pipeline" | `-p`, JSON output with a schema, independent review |
| "False positives", "developers ignore" | Explicit criteria, examples, disabling noisy categories |
| "Invented values" | Nullable fields and examples with missing data |
| "Overnight", "weekly", "cost" | Message Batches API, sized to the deadline |

Eliminate answers that rely solely on prompt wording for a guarantee, that give an agent more tools or context than
it needs, or that add complexity the scenario does not call for.

> **Version drift.** The exam was written against v1.0 of the guide. If an option describes behaviour that has
> since changed in the product (for example the `Task` tool name, now `Agent`), answer according to the concept the
> question is testing. See the "Product facts move faster than the exam guide" table in the [README](README.md).

## After the exam

You receive pass/fail, a scaled score and percent-correct by domain (the domain percentages do not decide the
result; the total scaled score does). If you need a retake, the registry's policy is 14 days after the first
failed attempt, 30 days after the second and 90 after the third, with at most four attempts per exam in a rolling
12 months. Appeals go to Pearson VUE within 14 days. Use the domain breakdown with the
[readiness assessment](readiness-assessment.md) to plan remediation.
