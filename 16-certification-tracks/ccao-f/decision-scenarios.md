# CCAO-F Decision Scenarios

> Part of the [CCAO-F track](README.md). Objective IDs come from [`registry.yaml`](../registry.yaml).
> These are original workplace case studies with fictional organisations. They are **not** exam questions and are not
> based on live exam content. Their purpose is to practise the reasoning the exam measures: picking the *best next
> action* given the stakes, the data and the tools available.

How to use them: read the situation, decide what you would do and why, then compare with the recommended reasoning.
Pay attention to *why* the weaker options are weaker; that is where most marks are won or lost.

---

## 1. The onboarding pack nobody reads

**Situation.** *Tailspin Toys* hires 30 warehouse staff a month. The onboarding pack is 45 pages. The training lead
wants Claude to "make it better".

**Decision.** How to approach the request.

**Recommended reasoning.** "Make it better" has no success criterion. Start by defining one with the training lead: for
example, "new starters can find the five things they need in week one in under two minutes". Use Claude to analyse the
pack against that goal (what is essential in week one, what can move to later, what is duplicated), then draft a
one-page week-one guide as an artifact and a restructured pack. Test with two recent starters. Rewriting all 45 pages in
one prompt would produce something shallow and unchecked.

**Objectives:** CCAO-F-1.1, 1.2, 4.1

---

## 2. The confident market statistic

**Situation.** A marketing manager at *Proseware Ltd* asks Claude, with no sources attached and no web search, for the
size of the European pet-insurance market. Claude gives a precise figure and a growth rate. The figure is going into a
board slide.

**Decision.** Whether the figure can go on the slide.

**Recommended reasoning.** Not as it stands. A precise figure produced without a source is exactly the kind of detail
that may be invented or out of date. Use research mode (or find an industry report) to get sourced figures, open the
sources to confirm them, note the date and source on the slide, and present a range if sources disagree. Asking Claude
"are you sure?" does not count as verification.

**Objectives:** CCAO-F-2.2, 2.3, 3.1

---

## 3. One Project or many?

**Situation.** *Contoso Health*'s facilities team handles maintenance requests for four hospitals. Each site has its own
contractor list and procedures, but a shared health-and-safety policy.

**Decision.** How to structure Projects.

**Recommended reasoning.** Two reasonable designs: one Project per site (site documents plus the shared policy in each),
or one Project with clearly labelled site documents and an instruction to always confirm which site a request is for.
Per-site Projects reduce the risk of mixing up contractors and simplify permissions if staff only serve one site; a
single Project is easier to maintain if the same team covers all sites. Whichever is chosen, the shared policy must
have one owner who updates every copy, and test questions should include cross-site traps ("who do I call for a lift
fault?" without naming the site).

**Objectives:** CCAO-F-5.1, 5.4, 3.1

---

## 4. The supplier-risk deep dive

**Situation.** A procurement analyst at *Acme Logistics* needs a view of a potential supplier's financial health, recent
news and any regulatory actions, with sources, for a sourcing committee next week.

**Decision.** Which Claude capability to use, and what to check.

**Recommended reasoning.** This is a multi-source investigation that needs citations: research mode fits. Scope the
request (time frame, source types, what "regulatory action" means here). Verify the material findings against the
cited sources, confirm dates, and note gaps the research could not fill. Financial-health conclusions should be framed
as indicators for the committee, with the procurement or finance specialist making the risk judgement.

**Objectives:** CCAO-F-3.1, 4.2, 2.3, 2.4

---

## 5. The 3,000 ticket categories

**Situation.** An IT service manager wants to tag 3,000 historical helpdesk tickets into 12 categories to find patterns.
The tickets contain employee names and occasionally device serial numbers.

**Decision.** How to run the task.

**Recommended reasoning.** First, data: remove names (and serial numbers if not needed) or confirm the approved
workspace and policy allow them. Second, design: test the category definitions on 50 tickets, compare a lighter and a
balanced model on that sample, and pick the cheapest model that meets the accuracy bar. Third, scale: 3,000 items in the
chat interface is laborious; process in structured batches with spot-checks, or recognise that a repeatable,
high-volume job like this may be better automated by a developer through the API, and hand over the tested category
definitions and examples.

**Objectives:** CCAO-F-3.3, 6.2, 4.4, 7.3

---

## 6. "Just make the Project remember it"

**Situation.** A sales team keeps telling Claude in chats that the discount ceiling is now 12%. Each new chat forgets.
Someone suggests turning memory on for everyone.

**Decision.** Where the rule should live.

**Recommended reasoning.** A team-wide business rule belongs in the Project instructions (and the pricing policy in
Project knowledge), not in each person's memory. Instructions are visible, shared, reviewable and maintained by an
owner; memory is personal and less controllable. Update the instructions, replace the pricing document, and retest with
common quote questions.

**Objectives:** CCAO-F-3.4, 5.3, 5.4

---

## 7. The personal account shortcut

**Situation.** A consultant at *Woodgrove Consulting* is waiting for IT to approve a Drive connector in the company
workspace. To meet a deadline, they plan to paste client interview transcripts into their personal Claude account,
with model training switched off.

**Decision.** Whether this is acceptable.

**Recommended reasoning.** No. Client data must stay in the organisation's approved tools; a personal consumer account
is outside the firm's contracts, controls and audit, whatever the training setting. Options: upload the transcripts
directly to an approved Project in the company workspace if that is permitted without the connector; work from
de-identified excerpts; or escalate the deadline risk to the engagement lead. The approval delay is a governance
issue to raise, not to work around.

**Objectives:** CCAO-F-6.2, 6.3

---

## 8. The redesign that removes a reviewer

**Situation.** A legal-operations lead at *Northwind Lending* proposes that Claude review incoming non-disclosure
agreements against a playbook and, if no issues are flagged, send them straight for signature, removing the paralegal
review.

**Decision.** Whether to approve the redesign.

**Recommended reasoning.** The idea has value, but it removes a human control from a legal process. A safer redesign:
Claude pre-checks each agreement against the playbook and produces a structured issues list; the paralegal reviews the
list and the flagged clauses rather than reading from scratch, which saves time while keeping a qualified person in the
loop. Pilot on past agreements where the right answer is known, measure misses, and get legal sign-off before changing
the process. Full automation would need much stronger evidence and a decision by legal leadership, and likely
Architect involvement.

**Objectives:** CCAO-F-4.4, 2.4, 6.1

---

## 9. Two drafts, one decision

**Situation.** A communications officer has two Claude drafts of a staff announcement about an office move, one from
each of two prompts. Colleagues prefer the longer one "because it feels more thorough".

**Decision.** How to choose.

**Recommended reasoning.** Write criteria first: correct dates and addresses, the three actions staff must take, tone,
length suitable for mobile reading, and a clear contact point. Score both drafts. The longer one may bury the actions.
Pick the better draft on the criteria, or merge the strongest parts, then verify every fact against the move plan.

**Objectives:** CCAO-F-2.5, 2.1

---

## 10. The Project that went stale

**Situation.** A Project used by 40 customer-support agents was set up nine months ago. Agents report that answers about
the returns window are sometimes wrong. Nobody knows who owns the Project.

**Decision.** What to do first and what to change.

**Recommended reasoning.** Immediate: confirm the correct returns policy, check the knowledge for outdated or duplicate
versions, fix it, and tell agents what changed. Then fix the root cause: assign an owner, add a review date and a change
log, create a set of test questions covering high-risk topics (returns, refunds, warranties), and rerun them after
each change or model update. Restrict "Can edit" to maintainers.

**Objectives:** CCAO-F-5.4, 7.1, 7.2

---

## 11. Brainstorm or analysis?

**Situation.** A school's head of year at *Fourth Coffee Academy* (a fictional school) asks Claude, "What should we do
about falling attendance in Year 10?", attaching an anonymised attendance summary.

**Decision.** How to structure the work.

**Recommended reasoning.** This combines two task types. First analysis: what does the data show (which groups, which
days, trends), with reasoning grounded in the attachment and gaps stated. Then brainstorming: a wide range of
interventions across categories (engagement, family contact, timetable, support), followed by ranking against
criteria (cost, evidence, staff time). Mixing both in one vague prompt tends to jump to generic advice without using the
data. Any intervention affecting individual students needs the school's safeguarding and pastoral process, not an AI
recommendation.

**Objectives:** CCAO-F-1.4, 1.2, 6.4

---

## 12. The connector that reads too much

**Situation.** A team assistant connects Gmail so Claude can find meeting logistics. During research on a venue,
Claude's report quotes from an unrelated confidential HR email in the assistant's inbox.

**Decision.** What went wrong and how to prevent it.

**Recommended reasoning.** Connectors act with the user's full access, and research can use enabled connectors without
asking each time. The fix is least access: enable only the connectors a chat needs, switch connectors off for research
that does not need them, and keep sensitive mail in accounts not connected to AI tools if policy requires it. Report
the incident if the confidential content was shared further. Ask IT whether organisation-level connector settings
should restrict what can be done.

**Objectives:** CCAO-F-5.2, 6.2, 3.1

---

## 13. Instructions that contradict themselves

**Situation.** A Project's instructions include "Always respond in a formal tone", "Be friendly and casual with
customers" and "Keep answers short but complete and include all relevant background." Output quality is erratic.

**Decision.** How to fix it.

**Recommended reasoning.** The rules conflict, so Claude has to guess which to follow. Rewrite with clear scope: who the
audience is, one tone definition with an example, a specific length ("under 150 words; link to the policy for detail"),
and what to do when unsure. Test before and after on the same five requests.

**Objectives:** CCAO-F-5.3, 7.1

---

## 14. Explaining a pilot to a sceptical director

**Situation.** An operations analyst ran a four-week pilot using Claude to draft weekly supplier performance summaries.
Drafting time fell from about four hours to about 75 minutes including review. Reviewers corrected two factual errors
across 16 summaries. The operations director thinks AI is "unreliable".

**Decision.** How to present the results.

**Recommended reasoning.** Lead with the measured baseline and result, then show the errors openly and explain the
review step that caught them. Explain what Claude does and what people still own, the cost, and the decision requested
(for example, extending the pilot to two more categories with the same review step). Acknowledge that the director's
concern is valid and show how the control addresses it. Do not round the saving up or hide the errors.

**Objectives:** CCAO-F-4.5, 2.4

---

## 15. The long planning chat

**Situation.** An event manager has used one chat for six weeks to plan a conference. Claude now confuses the speaker
list with an earlier draft and suggests a session that was cancelled.

**Decision.** How to continue.

**Recommended reasoning.** The chat has accumulated stale and superseded information. Ask Claude for a summary of the
current state (confirmed speakers, agenda, venue details, open actions), check it against the source of truth (the
event plan), correct it, and start fresh, ideally in a Project with the confirmed agenda and speaker list as knowledge.
Keep the source of truth outside the chat and update the Project when it changes.

**Objectives:** CCAO-F-3.4, 7.1, 5.1

---

## 16. A job advert and a fairness check

**Situation.** An HR coordinator asks Claude to draft job adverts for 12 roles quickly. Reviewing them, a colleague
notices that technical roles use assertive, competitive language and care roles use nurturing language.

**Decision.** What to do with the drafts.

**Recommended reasoning.** This is a bias pattern that can discourage some groups from applying. Revise using the
organisation's inclusive-language guidance, add an instruction to the Project (neutral, skills-based language; no
age-coded or gendered wording; essential versus desirable requirements), and check the revised drafts with a simple
test: would the wording change if the role were stereotypically associated with a different group? Record the check as
part of the standard review for people-related content.

**Objectives:** CCAO-F-2.2, 6.4, 5.3

---

## 17. Model choice for a hard synthesis

**Situation.** A policy analyst must synthesise 14 consultation responses with conflicting arguments into a balanced
options paper. A first attempt using a lighter model is fluent but misses tensions between positions.

**Decision.** What to change.

**Recommended reasoning.** The task needs careful reasoning across many documents, so a more capable model is
justified. Also change the approach: extract each response's position and evidence first (decomposition), check that
all 14 are covered, then ask for the synthesis with explicit instructions to represent each position fairly and show
where they conflict. The analyst then reviews for balance before circulation.

**Objectives:** CCAO-F-3.3, 1.2, 2.1

---

## 18. When the answer is "escalate"

**Situation.** A marketing team wants a public website chatbot that answers product questions using their Claude
Project's knowledge.

**Decision.** Whether the team can build this themselves in the Claude apps.

**Recommended reasoning.** A Project is a workspace for the team's own use; a public-facing chatbot is a product
integration with security, privacy, availability and brand-risk requirements. The Associate's job here is to capture
the requirements (audience, questions, tone, sources, escalation to humans, success measures) and test content quality
in a Project, then hand the build to Claude Architects or Developers and the relevant IT, security and legal teams.

**Objectives:** CCAO-F-4.3, 4.5, 6.1

---

## Patterns across the scenarios

- Clarify the goal and success criterion before generating anything.
- Verify specific facts in proportion to their stakes.
- Persist shared rules and knowledge in the Project, with an owner.
- Minimise data before using it, and use only approved tools.
- Keep a qualified human at every high-stakes or external decision point.
- Pick the lightest model and feature that meet the bar.
- Escalate when the work becomes system integration, public-facing or high-risk automation.

Continue with [common-misconceptions.md](common-misconceptions.md).
