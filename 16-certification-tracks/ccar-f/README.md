# Claude Certified Architect – Foundations (CCAR-F) Preparation Track

> **Unofficial study track.** This repository is not affiliated with or endorsed by Anthropic. The official
> CCAR-F Exam Guide v1.0 is the source of truth. Every exam fact on this page comes from
> [`registry.yaml`](../registry.yaml) (verified 2026-10-24), [`exam-facts.md`](../../25-official-resources/exam-facts.md)
> and the [official certifications page](https://anthropic-partners.skilljar.com/page/partner-certifications).

## What the credential is for

CCAR-F is the foundations-level architecture credential in Anthropic's Claude Certification Program. It
signals that you can build and configure production systems with the four technologies architects reach
for most: the **Claude Agent SDK** (agent loops, subagents, hooks, sessions), **Claude Code** (CLAUDE.md,
rules, skills, plan mode, CI), the **Model Context Protocol** (tool and resource design, structured errors)
and the **Claude API** (tool use, structured output, the Message Batches API).

"Foundations" does not mean "easy". The exam is practical: it asks what you would *configure*, *build* or
*change* in a specific production situation, and the wrong answers are usually things that work in a demo
but fail at scale, such as relying on a prompt instruction where a hook is needed, or giving every agent
every tool.

## Who it is for

The registry describes the target candidate as a solution architect who designs and implements production
applications with Claude, with hands-on experience of the Agent SDK, Claude Code, MCP tool design and
structured-output prompting. In practice this track also suits:

- Senior developers and tech leads who own a team's Claude Code setup or an internal agent.
- Platform and DevSecOps engineers who wire Claude Code into CI/CD and govern MCP servers.
- Security engineers who review agent designs and want to know where enforcement really lives.

### How CCAR-F differs from CCAR-P

| | CCAR-F (this track) | [CCAR-P](../ccar-p/README.md) |
|---|---|---|
| Focus | Building and configuring: SDK, Claude Code, MCP, structured output | Designing and governing whole solutions across an enterprise |
| Typical question | "Which configuration, hook, schema or flag fixes this?" | "Which architecture best fits these constraints and stakeholders?" |
| Format | Scenario-based: 4 scenarios drawn from a published bank of 6 | Independent items across seven domains |

Many candidates take CCAR-F first; the hands-on knowledge transfers directly to CCAR-P's Domain 3
(Integration) and Domain 7 (Developer Productivity).

### Recommended experience

From the registry: no mandatory prerequisites, but **6+ months of practical experience building with the
Claude API, Agent SDK, Claude Code and MCP** is recommended. If you have used Claude Code but never written
an agent loop or an MCP server, budget extra time for labs 03, 08, 09, 10 and 12 in
[`19-hands-on-labs`](../../19-hands-on-labs/README.md).

## Format and logistics

| Fact | Value (from [`registry.yaml`](../registry.yaml)) |
|---|---|
| Exam code | CCAR-F |
| Guide version | 1.0 (effective July 2026) |
| Items | 60 |
| Item types | Multiple-choice and multiple-response (each item says how many to select) |
| Structure | 4 scenarios drawn at random from a published bank of 6 |
| Time | 120 minutes |
| Passing standard | Scaled score 720 on a 100–1,000 scale |
| Fee | USD 125 |
| Validity | 12 months |
| Result | Pass/fail, scaled score and percent-correct by domain |
| Delivery | Pearson VUE, online proctored (OnVUE) or test centre |

See [`exam-facts.md`](../../25-official-resources/exam-facts.md) for all tracks side by side and
[`exam-day.md`](exam-day.md) for check-in and pacing.

## The scenario-based format: 4 of 6

This is the feature that most changes how you prepare.

- The exam guide publishes **six scenarios**, each a short description of a production context. The registry
  lists them with their primary domains:

  | Scenario | Primary domains |
  |---|---|
  | Customer Support Resolution Agent | 1, 2, 5 |
  | Code Generation with Claude Code | 3, 5 |
  | Multi-Agent Research System | 1, 2, 5 |
  | Developer Productivity with Claude | 2, 3, 1 |
  | Claude Code for Continuous Integration | 3, 4 |
  | Structured Data Extraction | 4, 5 |

- On exam day, **four of the six are chosen at random**. Each scenario frames a group of questions, so you
  read the context once and then answer several items about it.
- You **cannot predict which four** you will get. Every scenario has a roughly one-in-three chance of being
  left out, so skipping one in your preparation is a gamble you will lose about two times in three.
- Domain weights still apply across the whole exam. A scenario's "primary domains" tell you where most of
  its questions come from, not that other domains are excluded.

**What this means for study.** Prepare every scenario as a mini case study: know the reference architecture,
the decisions an architect makes in it and the traps. [`scenarios.md`](scenarios.md) does this for all six,
with original content (no exam items). Then practise reading a scenario *once* and holding its constraints in
mind across several questions, which is what the [practice questions](../../17-practice-questions/README.md)
and [mock examinations](../../18-mock-examinations/README.md) for this track train.

## Registration and eligibility

- **Eligibility:** certification exams are open to organisations in the **Claude Partner Network**. The free
  Claude Academy courses are open to everyone but award completion certificates, not certifications.
- **Registration path:** enrol through the Anthropic Partner Academy (Skilljar) certification page, then
  schedule with Pearson VUE. Your Pearson profile name must exactly match your government-issued ID.
- **Rescheduling:** the v1.0 guide says changes are allowed up to 24 hours before the appointment, but the
  Partner Academy FAQ and Pearson VUE page (checked 2026-10-24) require at least 48 hours. The registry treats
  **48 hours** as the effective deadline; later changes forfeit the fee.

## Retake and renewal policy

- **Retakes** (registry): wait 14 days after the first failed attempt, 30 days after the second and 90 days
  after the third, with at most four attempts per exam in a rolling 12 months. Each attempt is charged.
- **Validity:** 12 months from the award date.
- **Renewal** (exam guide v1.0, section 15, checked 2026-10-24): renewing before expiry is free. You review
  what has changed and pass a non-proctored check on the Anthropic Partner Academy. A lapsed credential means
  sitting and paying for the full exam again, and Anthropic may require the full exam if content changes
  significantly.

## Upcoming change: 2026-11-17 guide update

Pearson VUE states that updated exam guides will be published on **2026-11-17** and names CCAO-F, CCDV-F and
CCAR-P as receiving updated content from 2026-12-07. CCAR-F is not named in that notice.

> **Unverified:** whether the CCAR-F guide will also change on 2026-11-17. Check the
> [certifications page](https://anthropic-partners.skilljar.com/page/partner-certifications) before you book,
> and compare any new guide's objectives with [`registry.yaml`](../registry.yaml).

## Product facts move faster than the exam guide

The v1.0 guide was written against the products as they stood in mid-2026. A few details have since changed
in the official docs, and this track teaches both the concept the exam tests and the current behaviour
(as of 2026-10-24):

| Exam-guide concept | Current behaviour to know |
|---|---|
| Subagents are spawned with the "Task" tool | Use the **`Agent` tool**, called `Task` in the v1.0 exam guide (the `system:init` tool list still shows `Task`). List `Agent` in `allowedTools` so delegation runs without a prompt |
| `allowedTools` for a coordinator | `allowedTools` **auto-approves** the listed tools; it does not restrict the tool set. Restrict with `AgentDefinition.tools`, `disallowedTools` or deny rules |
| Forcing a tool with `tool_choice` `any` or `{"type": "tool"}` | Returns a **400 on Claude Opus 5.5, Sonnet 5.5, Fable 5.1 and Mythos 5.1**; Haiku 5.5 still accepts it. Use `auto` plus an explicit instruction, `strict: true` tools, or structured outputs |
| Skills' `allowed-tools` frontmatter | **Pre-approves** listed tools; it does not remove others. Use `disallowed-tools` to restrict |
| Slash commands in `.claude/commands/` | Still work, but are now merged into skills; a skill with the same name wins |

The [domain study guides](study-guide/domain-1.md) explain each one where it arises.

## Domains

| # | Domain | Weight | Study guide | Key modules |
|---|---|---|---|---|
| 1 | Agentic Architecture & Orchestration | 27% | [domain-1.md](study-guide/domain-1.md) | [10 Agentic AI](../../10-agentic-ai/README.md), [09 Hooks](../../09-claude-code/06-hooks.md) |
| 2 | Tool Design & MCP Integration | 18% | [domain-2.md](study-guide/domain-2.md) | [07 Tool use](../../07-tool-use-and-function-calling/README.md), [08 MCP](../../08-model-context-protocol/README.md) |
| 3 | Claude Code Configuration & Workflows | 20% | [domain-3.md](study-guide/domain-3.md) | [09 Claude Code](../../09-claude-code/README.md) |
| 4 | Prompt Engineering & Structured Output | 20% | [domain-4.md](study-guide/domain-4.md) | [03 Prompt engineering](../../03-prompt-engineering/README.md), [06 Batches](../../06-claude-api/05-batch-processing.md) |
| 5 | Context Management & Reliability | 15% | [domain-5.md](study-guide/domain-5.md) | [04 Context engineering](../../04-context-engineering/README.md), [10 Agent reliability](../../10-agentic-ai/07-agent-reliability.md) |

Domain 1 alone is more than a quarter of the exam, and it appears as a primary domain in four of the six
scenarios. Domains 3 and 4 together are another 40%.

## Recommended study sequence

The order below follows dependencies, not domain numbers.

1. **Baseline (week 1).** Take the [readiness assessment](readiness-assessment.md) cold and skim
   [`revision-notes.md`](revision-notes.md). Read [`scenarios.md`](scenarios.md) once to see the six contexts.
2. **Tool use and structured output (Domain 4, objectives 4.3–4.4; Domain 2, 2.1–2.3).** Everything agentic
   rests on a correct tool loop and well-designed tools. Do labs 03 and 08.
3. **Agent loop and orchestration (Domain 1).** Loop control on `stop_reason`, coordinator and subagents,
   hooks, decomposition, sessions. Do lab 12 and lab 13.
4. **MCP (Domain 2, 2.2 and 2.4).** Build a small server with structured errors and connect it to Claude Code.
   Do lab 09.
5. **Claude Code (Domain 3).** CLAUDE.md hierarchy, `.claude/rules/`, skills, plan mode, headless CI.
   Do lab 10 end to end on a real repository.
6. **Prompting for precision (rest of Domain 4).** Explicit criteria, few-shot examples, batches, multi-pass
   review. Do labs 02, 16 and 17.
7. **Context and reliability (Domain 5).** Case-facts blocks, escalation, error propagation, large-codebase
   exploration, confidence calibration, provenance. Do labs 05 and 18.
8. **Consolidate by scenario.** Work through [`scenarios.md`](scenarios.md),
   [`decision-scenarios.md`](decision-scenarios.md), [`practical-exercises.md`](practical-exercises.md),
   [`common-misconceptions.md`](common-misconceptions.md), the
   [CCAR-F flashcards](../../23-flashcards/decks/ccar-f.yaml), the
   [practice questions](../../17-practice-questions/README.md) and the
   [mock examinations](../../18-mock-examinations/README.md).
9. **Final week.** Re-take the readiness assessment, remediate weak objectives, read [`exam-day.md`](exam-day.md).

For a calendar-based plan, follow Weeks 1 to 4 of the [60-day plan](../../00-getting-started/roadmaps/60-day-comprehensive.md)
and add Module 09 (Claude Code); the [roadmaps guide](../../00-getting-started/roadmaps/README.md) explains why.

## Track contents

| File | Purpose |
|---|---|
| [`objective-map.yaml`](objective-map.yaml) | Every CCAR-F objective mapped to modules and labs |
| [`coverage-matrix.md`](coverage-matrix.md) | Generated matrix of objectives, modules, labs and practice questions |
| [`scenarios.md`](scenarios.md) | Study guide for each of the six published exam scenarios |
| [`study-guide/`](study-guide/domain-1.md) | Five domain guides |
| [`practical-exercises.md`](practical-exercises.md) | Hands-on build exercises (agent loop, hooks, MCP server, Claude Code setup, CI review, extraction pipeline) |
| [`decision-scenarios.md`](decision-scenarios.md) | Original configuration case studies with options analysis |
| [`revision-notes.md`](revision-notes.md) | Condensed notes by domain |
| [`common-misconceptions.md`](common-misconceptions.md) | Misconceptions and corrections |
| [CCAR-F one-pager](../../22-cheat-sheets/ccar-f-one-pager.md) | Single-page cheat sheet |
| [`exam-day.md`](exam-day.md) | Logistics, rules and pacing for a scenario-based exam |
| [`readiness-assessment.md`](readiness-assessment.md) | Per-objective self-assessment and remediation |

## Official resources

- [Anthropic Partner Academy: certifications page and exam guides](https://anthropic-partners.skilljar.com/page/partner-certifications)
- [Pearson VUE: Claude Certification Program](https://www.pearsonvue.com/us/en/anthropic.html)
- [Claude Agent SDK documentation](https://code.claude.com/docs/en/agent-sdk/overview)
- [Claude Code documentation](https://code.claude.com/docs)
- [Model Context Protocol specification](https://modelcontextprotocol.io/specification/latest)
- [Claude Platform documentation](https://platform.claude.com/docs)
- [Official resources in this repository](../../25-official-resources/README.md)
