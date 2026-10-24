# CCAO-F Revision Notes

> Part of the [CCAO-F track](README.md). Domains, weights and objective IDs come from [`registry.yaml`](../registry.yaml);
> the human-readable summary is [exam-facts.md](../../25-official-resources/exam-facts.md). Product facts are as of
> 2026-10-24. Use these notes in the final week, after working through the
> [study guides](study-guide/domain-1.md).

## The exam in five lines

- 60 items, multiple-choice and multiple-response, 120 minutes, Pearson VUE (online or test centre).
- Seven domains; Domain 2 (Output Evaluation and Validation) is the largest at 21%.
- Questions test judgement in realistic business situations: the best next action, the right feature, the right level
  of review.
- No coding or API knowledge is needed.
- Updated guide due 2026-11-17; updated exam content from 2026-12-07.

## Domain 1 · Prompting and Task Execution (14%)

- **Strong prompt = goal + context + audience + constraints + format + success criteria.**
- Say what to do (not only what to avoid) and why the rule exists.
- Examples show style and format faster than adjectives; vary them.
- Long material first, question last; label the parts.
- "If it is not in the material, say 'not stated'" reduces invented facts.
- **Decompose** multi-phase or high-stakes work; check between steps; ask Claude to plan first.
- **Iterate diagnostically:** name the problem, find the cause in the prompt, change one thing, compare. Edit and
  regenerate when the first attempt went off track.
- **Task types:** analysis → evidence and reasoning; research → scope and sources; drafting → audience and voice;
  brainstorming → volume and variety, then rank.

## Domain 2 · Output Evaluation and Validation (21%)

- **Accurate ≠ complete.** Check both, against the brief.
- **Hallucination warning signs:** figures, dates, clause numbers, quotes, URLs or names you did not supply; claims
  beyond the source; recent events with no source.
- **Validation means an outside source:** primary document, recalculation, independent cross-check, expert review.
  Self-rated confidence and "are you sure?" are not validation.
- **Citations must be opened** and confirmed.
- **Review level rises with:** stakes, external audience, irreversibility, specialist expertise, novelty, decisions
  about people.
- **Bias checks:** swap names or groups; look for coded language; ask whose perspective is missing.
- **Audience adaptation:** executives (decision first), staff (what changes, what to do), customers (plain, accurate
  commitments), technical (detail, assumptions). Check for drift when shortening.
- **Compare outputs against criteria set in advance.**
- **Formats:** inline (quick), artifact (substantial, reusable, shareable), structured data (feeds another tool).
- **You own what you send.**

## Domain 3 · Product and Model Selection (12%)

| Signal | Feature |
|---|---|
| Recurring work, shared files, consistent team behaviour | Project (instructions + knowledge) |
| Multi-source investigation with citations | Research (paid plans, web search on) |
| Quick current fact | Web search |
| Substantial deliverable or small tool to edit and share | Artifact |
| Content lives in Drive, Gmail, Calendar and so on | Connector |
| Same procedure every time, across workspaces | Skill |
| Continuity of personal preferences | Memory or chat search (where enabled) |
| Do not save this chat | Incognito chat (still follow policy) |

- **Haiku:** fastest, cheapest, simple high-volume tasks. **Sonnet:** balanced default for everyday work. **Opus:** most
  capable of the three, for complex reasoning. **Fable 5.1:** Anthropic's most capable widely released model, premium
  tier (as of 2026-10-24).
- **Choose the cheapest model that meets the quality bar,** tested on real examples.
- **Context window:** everything Claude can consider in one conversation. Up to 1M tokens for the newest models on paid
  plans; part is reserved for the reply. Long chats use more of your limits and can drift.
- **Restart** (drifted or new topic) · **Summarise** (long but healthy) · **Persist** (needed across chats).
- Research runs on Claude Opus 5.5 whatever model the chat uses (as of 2026-10-24).

## Domain 4 · Workflow Integration and Solution Design (16%)

- **Good first use case:** frequent, time-consuming, text-heavy, checkable, low risk, permitted data.
- Claude can analyse interview notes into steps, pain points and contradictions; people resolve the contradictions.
- **Augment → automate a step → redesign.** Each step needs stronger evidence and controls.
- **A named human checkpoint** before anything external, irreversible or affecting individuals.
- **Measure a baseline before the pilot.** Track a quality measure as well as time.
- **Prototype** with Projects and artifacts; test on easy, typical and awkward examples.
- **Communicate:** problem and baseline, what Claude does and what people do, evidence including failures, limitations
  and controls, cost, decision needed. No overselling.
- **Escalate** integrations, automation at scale, public-facing products and systems of record to Architects,
  Developers and IT.

## Domain 5 · Configuration and Knowledge Management (12%)

- **Project = instructions (how to behave) + knowledge (what to know) + chats (the work).**
- Projects on all plans (Free: up to five); RAG mode extends knowledge capacity on paid plans; Team and Enterprise
  sharing with "Can view" or "Can edit".
- Chats in a Project do not share their conversations with each other; put shared facts in knowledge.
- **Knowledge hygiene:** current, authoritative, one version per document, clear names with dates, nothing
  unnecessary or restricted.
- **Upload** stable reference material; **connect** live, changing content.
- **Connectors:** Team and Enterprise owners enable them and can set actions to allow, needs approval or blocked; each
  user authenticates individually; custom (remote MCP) connectors are not verified by Anthropic.
- **Instruction template:** purpose, audience, knowledge use, format, rules (with reasons), when unsure.
- **Instructions are not a security control.**
- **Maintain:** owner, review date, change log, test set; retest after any change or model update.

## Domain 6 · Governance, Risk, and Responsible Use (15%)

- **Appropriateness test:** permitted by policy? data allowed? who is harmed if wrong? human decides? comfortable
  explaining it?
- **Classify before you paste:** public, internal, confidential, restricted.
- **Minimise:** redact, pseudonymise (key kept outside the tool), aggregate, synthetic data, excerpts. Usually better
  than either skipping the task or uploading everything.
- **"Don't remember this" is not a control.** Neither is a personal account with training switched off.
- **Commercial plans (Team, Enterprise, API):** no training on customer data by default. **Consumer plans (Free, Pro,
  Max):** training only if the user opts in. **Incognito:** not in history or memory; not used for training (as of
  2026-10-24).
- **Policy unclear → ask and pause.** Mistake with data → report promptly.
- **Ethics:** accuracy, fairness, transparency, accountability, privacy, intellectual property, impact on people,
  over-reliance.
- **Decisions about people stay with qualified humans.**

## Domain 7 · Troubleshooting and Optimization (10%)

| Symptom | First thing to check |
|---|---|
| Generic | Missing context or audience |
| Wrong format | Format unstated or conflicting |
| Invented facts | No source, no fallback rule |
| Missed input | Too much material, poor labelling |
| Ignores a rule | Vague, buried or contradicted instruction |
| Out of date | Old knowledge file, no web search |
| Inconsistent | Duplicate files, conflicting instructions, different access |
| Worse over time in one chat | Context drift: summarise and restart |
| Shallow on hard task | Model too light, no room to reason |

- Reproduce → change one thing → retest on saved examples → log the change.
- Fix recurring issues in configuration, not chat by chat.
- **Efficiency levers:** Projects (cached reuse), Skills and templates, right-sized models, shorter chats, batching,
  structured outputs, review matched to risk.
- If repeated fixes fail, reconsider task fit or escalate.

## Last-day checklist

- [ ] I can name the feature for each scenario signal in the Domain 3 table without looking.
- [ ] I can list the six review-level factors.
- [ ] I can explain why self-rated confidence is not validation.
- [ ] I can list five data-minimisation techniques.
- [ ] I can write a Project instruction set from memory using the six-part template.
- [ ] I have read [exam-day.md](exam-day.md) and checked my ID name against my registration.
