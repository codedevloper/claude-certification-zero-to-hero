# Domain 5 · Configuration and Knowledge Management (12%)

> Part of the [CCAO-F track](../README.md). Objective IDs and weights come from [`registry.yaml`](../../registry.yaml).
> Product facts were checked against [support.claude.com](https://support.claude.com/) **as of 2026-10-24**; settings
> labels and plan availability change, so recheck before relying on them.

## Objectives

| ID | What you must be able to do (paraphrased) |
|---|---|
| CCAO-F-5.1 | Set up Projects with instructions and knowledge sources |
| CCAO-F-5.2 | Manage uploaded knowledge and connectors such as Google Drive and Gmail |
| CCAO-F-5.3 | Write effective system-level (Project-level) instructions |
| CCAO-F-5.4 | Keep configurations, knowledge and instructions current over time |

## Concepts to master

- The three configuration layers in a Project: instructions (how to behave), knowledge (what to know) and chats (the
  work itself).
- Knowledge quality beats knowledge quantity: current, authoritative, de-duplicated, clearly named files.
- Connectors give Claude live access to tools using *your* permissions, so they inherit your access, and your risks.
- Instructions are a standing brief: role, audience, scope, rules, format, and what to do when unsure.
- Configuration is a living asset: it needs an owner, a review cycle and a change log.

## Detailed notes

### 5.1 Configuring Projects

As of 2026-10-24, the Help Center describes Projects as self-contained workspaces with their own chat histories and
knowledge bases ([What are projects?](https://support.claude.com/en/articles/9517075-what-are-projects)). Key facts:

- **Availability:** all plans, including Free (Free accounts can create up to five Projects).
- **Knowledge:** you upload documents, text, code and other files; Claude uses them as background for every chat in the
  Project.
- **Instructions:** set once per Project; they apply to all chats in that Project and do not carry over to other
  Projects.
- **Capacity:** on paid plans, when knowledge approaches the context limit Claude switches to retrieval-augmented
  generation (RAG) mode, which searches the knowledge for relevant parts instead of reading everything, expanding
  capacity by up to roughly ten times.
- **Sharing (Team and Enterprise):** share with individuals, groups or the whole organisation. "Can view" members can
  see contents and chat; "Can edit" members can change instructions and knowledge and manage members.
- **Separate chats:** each chat in a Project has its own conversation. Information discussed in one chat is not
  automatically shared with the others; if everyone needs it, add it to Project knowledge.
- **Usage:** Project content is cached, so reusing it counts less against usage limits than re-uploading files to each
  chat (the cache expires after inactivity).

A setup sequence that works:

1. Write the Project's **purpose** in one sentence ("Draft and review supplier communications for the procurement team").
2. Gather **knowledge**: only current, approved, relevant documents. Remove drafts and superseded versions.
3. Write **instructions** (see 5.3).
4. **Test** with five to ten realistic requests, including tricky ones and one that should be refused or escalated.
5. **Share** with the right permission level; most users need "Can view", only maintainers need "Can edit".
6. Record an **owner** and a review date.

### 5.2 Managing knowledge and connectors

**Uploaded knowledge** is a snapshot. If the policy changes in your document system, the copy in the Project does not
update itself. Good practice:

- Name files clearly with version and date (`Travel-Policy_v4_2026-09.pdf`).
- Keep one authoritative version per document; conflicting versions cause conflicting answers.
- Prefer text-based files; scanned images and complex layouts may not be read as you expect.
- Do not upload data the Project does not need, especially personal or restricted data (Domain 6).

**Connectors** link Claude to external tools so it can search and read (and in some cases act in) those systems. As of
2026-10-24 ([connectors](https://support.claude.com/en/articles/11176164-use-connectors-to-extend-claude-s-capabilities),
[Google Workspace connectors](https://support.claude.com/en/articles/10166901-use-google-workspace-connectors)):

- On **Team and Enterprise**, an Owner must enable a connector for the organisation first; each person then
  authenticates individually, so Claude sees only what that person can access.
- Owners can set what categories of action a connector may take: always allow, needs approval, or blocked. Individual
  users cannot override these organisation settings.
- **Custom connectors** use remote MCP (Model Context Protocol) servers. They are available on all plans (Free users
  are limited to one), must be reachable from the public internet, and are **not verified by Anthropic**, so connect
  only to services from organisations you trust and review the permissions requested.
- The **Google Drive** connector extracts text from documents; images embedded in documents are not processed.
- **Research** can use your enabled connectors without asking each time, so be deliberate about which connectors are on
  for a chat.

Uploaded knowledge versus connectors:

| | Uploaded Project knowledge | Connector |
|---|---|---|
| Freshness | Snapshot; you must re-upload changes | Live: reads the current version |
| Control | You choose exactly what is included | Claude can reach anything your account can reach in that tool |
| Consistency | Same material for every Project user | Depends on each user's own access |
| Best for | Stable reference material (style guides, policies, templates) | Fast-changing content (email, calendars, active documents) |

Content that Claude reads through a connector, a web page or a document can contain text that tries to give Claude
instructions (indirect prompt injection). Treat unexpected behaviour after reading external content as a warning sign,
and keep a human checkpoint before any action.

**Skills** package a repeatable procedure (instructions plus optional files or scripts) that Claude loads only when a
task needs it. As of 2026-10-24, Skills are available on all plans with code execution enabled; a custom skill is a
folder with a `SKILL.md` file, uploaded as a ZIP under Customize > Skills; Team and Enterprise owners can provision
Skills for the whole organisation ([What are skills?](https://support.claude.com/en/articles/12512176-what-are-skills)).
Choose a Skill for "how we do this task" that should work across Projects; choose Project instructions for "how to
behave in this workspace".

### 5.3 Writing effective system-level instructions

Project instructions act like a standing brief that applies before every message. A reliable structure:

```text
Purpose: You help the Fabrikam Events marketing team draft and review attendee communications.

Audience: Event attendees (mostly HR and L&D professionals). Plain, warm, professional British English.

Use of knowledge: Base facts about events only on the files in this Project (event schedule, venue guide,
brand voice guide). If a fact is not in them, say so and ask; do not guess dates, prices or venues.

Format: Subject line, then body under 200 words, then a single call to action. Offer two subject-line options.

Rules:
- Never promise refunds, discounts or exceptions; refer those to events@fabrikam.example.
- Do not include attendee personal data in drafts; use placeholders such as [First name].

When unsure: Ask one clarifying question rather than making assumptions.
```

Principles:

- **Be specific and explain the reason** for important rules.
- **Separate stable rules from task details.** Instructions hold what is always true; individual chats hold this week's
  specifics.
- **Tell Claude what to do when information is missing.** This single line prevents many hallucinations.
- **Keep them short enough to maintain.** Long, contradictory instruction sets are a common cause of erratic output.
- **Test after every change** with your saved test requests.

Instructions guide behaviour, but they are not a security control. They do not stop someone with access from uploading
restricted data, and they cannot guarantee Claude never makes a mistake. Real controls are permissions, data policy and
human review.

### 5.4 Maintaining configurations over time

Configuration drifts out of date quietly. Build a maintenance routine:

| Trigger | Action |
|---|---|
| A source document changes | Replace the file in knowledge; remove the old version |
| Users report a recurring error | Reproduce it with a test request, fix instructions or knowledge, retest |
| A model update or new feature | Rerun your test set; adjust instructions if behaviour changed |
| Team or process change | Review sharing permissions and instructions |
| Scheduled review (for example quarterly) | Check every file is current, remove unused files, confirm the owner |

Keep a short change log (date, what changed, why, who) in a document inside or alongside the Project. When something
breaks, the log tells you what changed.

## Decision rules and heuristics

- **Stable, shared reference → upload as Project knowledge. Live, changing content → connector.**
- **Behaviour for this workspace → Project instructions. Repeatable procedure across workspaces → Skill.**
- **One authoritative version of each document.** Conflicting files produce conflicting answers.
- **Least access:** enable only the connectors and sharing levels a task needs.
- **Every Project needs an owner, a test set and a review date.**
- **Instructions shape behaviour; permissions and policy enforce boundaries.**

## Worked mini-scenarios

**Scenario 1 – The contradictory answers.** A Project for the IT service desk at *Contoso Health* gives different
password-reset steps on different days. The knowledge contains both the 2024 and the 2026 versions of the guide.
*Fix:* remove the superseded file, rename the current one with its date, add an instruction to cite the document used,
retest.

**Scenario 2 – Drive or upload?** A bid team's proposal drafts change daily in Google Drive, while its boilerplate
library changes twice a year. *Design:* upload the boilerplate as Project knowledge; use the Drive connector for the
live drafts.

**Scenario 3 – Instruction bloat.** A Project's instructions have grown to three pages after six people each added
rules. Output became inconsistent. *Fix:* the owner consolidates into purpose, audience, knowledge use, format, rules
and when-unsure sections, removes contradictions and reruns the test set.

**Scenario 4 – Over-sharing.** A team lead shares a Project containing salary-band documents with the whole organisation
by mistake. *Fix:* restrict sharing immediately, remove the file if it should not be there at all, report under the
organisation's incident process, and add a permissions check to the review routine.

## Common traps

- Uploading everything "just in case", which dilutes relevant material and may expose sensitive data.
- Assuming uploaded files update when the original changes.
- Assuming a connector shows Claude the same thing for every user (it uses each person's own access).
- Writing instructions as vague adjectives ("be professional and helpful") with no format, scope or fallback.
- Using instructions as if they were a security boundary.
- Giving "Can edit" to everyone.
- Connecting an unverified custom connector without checking who runs it and what it can access.

## Modules and labs

| Objective | Module pages | Labs |
|---|---|---|
| 5.1 | [Projects and knowledge](../../../05-claude-products-and-models/04-projects-and-knowledge.md), [System prompts and roles](../../../03-prompt-engineering/07-system-prompts-and-roles.md) | [Lab 04](../../../19-hands-on-labs/lab-04-document-grounded-qa/README.md) |
| 5.2 | [Connectors and integrations](../../../05-claude-products-and-models/06-connectors-and-integrations.md), [What is MCP](../../../08-model-context-protocol/01-what-is-mcp.md), [Indirect prompt injection](../../../12-ai-security/03-indirect-prompt-injection.md) | [Lab 09](../../../19-hands-on-labs/lab-09-mcp-fundamentals/README.md), [Lab 04](../../../19-hands-on-labs/lab-04-document-grounded-qa/README.md) |
| 5.3 | [System prompts and roles](../../../03-prompt-engineering/07-system-prompts-and-roles.md), [Structure with XML tags](../../../03-prompt-engineering/02-structure-with-xml-tags.md), [Progressive disclosure and Skills](../../../04-context-engineering/06-progressive-disclosure-and-skills.md) | [Lab 02](../../../19-hands-on-labs/lab-02-prompt-improvement/README.md), [Lab 03](../../../19-hands-on-labs/lab-03-structured-outputs/README.md) |
| 5.4 | [Lifecycle management](../../../13-enterprise-ai-architecture/09-lifecycle-management.md), [Model upgrades and change management](../../../15-production-operations/08-model-upgrades-and-change-management.md) | [Lab 04](../../../19-hands-on-labs/lab-04-document-grounded-qa/README.md), [Lab 16](../../../19-hands-on-labs/lab-16-evaluation-framework/README.md) |

Hands-on: [practical exercises for Domain 5](../practical-exercises.md#domain-5--configuration-and-knowledge-management).

## Self-check

1. What are the three layers of a Project, and what does each hold?
2. When is a connector better than uploading a file, and when is it worse?
3. What single line in Project instructions most reduces invented facts?
4. Why are Project instructions not a security control?
5. Name three triggers for reviewing a Project's configuration.

<details>
<summary>Answers</summary>

1. Instructions (how to behave), knowledge (what to know) and chats (the work). Instructions and knowledge apply to
   every chat in the Project.
2. Better for live, frequently changing content; worse when you need tight control over exactly what Claude sees, the
   same view for every user, or when the tool contains data the task should not touch.
3. A fallback rule such as "If the information is not in the Project files, say so and ask rather than guessing."
4. They guide the model's behaviour but do not stop people uploading or accessing data, and the model can still make
   mistakes. Boundaries come from permissions, data policy, admin settings and human review.
5. Any three of: source document changes, recurring user-reported errors, model or feature updates, team or process
   changes, scheduled periodic review.

</details>
