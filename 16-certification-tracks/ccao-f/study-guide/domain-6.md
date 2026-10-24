# Domain 6 · Governance, Risk, and Responsible Use (15%)

> Part of the [CCAO-F track](../README.md). Objective IDs and weights come from [`registry.yaml`](../../registry.yaml).
> Data-handling facts were checked against Anthropic's privacy and support centres **as of 2026-10-24**. This page is
> general education, not legal advice: your organisation's policy and your legal, privacy and security teams decide
> what is allowed.

## Objectives

| ID | What you must be able to do (paraphrased) |
|---|---|
| CCAO-F-6.1 | Tell appropriate use cases from inappropriate ones |
| CCAO-F-6.2 | Apply data-sensitivity, regulatory and privacy considerations |
| CCAO-F-6.3 | Follow your organisation's AI policy and governance standards |
| CCAO-F-6.4 | Understand the ethical implications of using AI |

## Concepts to master

- Appropriateness depends on the task, the data, the stakes and who is affected, not on whether Claude *can* do it.
- Data classification (for example public, internal, confidential, restricted) and what each allows.
- Data minimisation: share only what the task needs; redact, anonymise or use synthetic data where you can.
- Instructions to the model ("don't remember this") are not data controls.
- Approved tools and accounts: commercial workspace versus personal consumer account.
- Accountability, transparency, fairness and human oversight as everyday practices.

## Detailed notes

### 6.1 Appropriate and inappropriate use

A quick appropriateness test, applied before you start:

1. **Is the use permitted** by your organisation's AI policy and by Anthropic's usage policy?
2. **Is the data allowed** in this tool, under this account, for this purpose?
3. **Who is affected** if the output is wrong, and how badly?
4. **Will a qualified human make the final decision** where the stakes are high?
5. **Would you be comfortable** explaining this use to the person affected, a regulator or a journalist?

| Generally appropriate (with normal review) | Needs extra controls or expert sign-off | Generally inappropriate |
|---|---|---|
| Drafting internal communications, summarising meetings, brainstorming, editing for clarity, explaining concepts, structuring plans | Customer-facing content, analysis that informs financial, legal, HR or medical decisions, content for regulators | Making final decisions about individuals' employment, credit, health or legal status without human judgement; uploading data your policy prohibits; generating deceptive content (fake reviews, impersonation); bypassing security or policy controls |

Claude is designed to decline some requests outright under Anthropic's usage policy. More often the question for an
Associate is not whether Claude will help but whether the organisation *should* use AI for this task in this way.

### 6.2 Data sensitivity, regulation and privacy

**Classify before you paste.** Most organisations use a scheme such as:

| Class | Examples | Typical rule for AI tools |
|---|---|---|
| Public | Published marketing copy, public reports | Allowed |
| Internal | Process documents, meeting notes | Allowed in approved tools |
| Confidential | Unreleased financials, contracts, strategy | Approved commercial workspace only, minimum necessary |
| Restricted | Personal data, health data, payment card data, credentials, legally privileged material | Often prohibited, or only with specific approval and safeguards |

**Data minimisation techniques** (the preferred route over "skip the task" or "upload it anyway"):

- **Redact** identifiers: names, emails, phone numbers, ID numbers, addresses.
- **Pseudonymise**: replace identifiers with consistent tokens (Employee A, Employee B) so analysis still works, and
  keep the key outside the AI tool.
- **Aggregate**: share counts and averages instead of row-level records.
- **Use synthetic or sample data** to design the prompt, then apply the approach to real data only where approved.
- **Share excerpts**: the relevant clause, not the whole file.

**Regulation.** Regulations such as GDPR (EU and UK data protection), HIPAA (US health information), sector rules in
finance and education, and emerging AI-specific laws such as the EU AI Act may apply depending on where you work and
what data you handle. An Associate is not expected to interpret them, but must recognise when regulated data or a
regulated decision is involved and follow the organisation's process (often: privacy team approval, approved tool,
documented purpose).

**Platform data handling, as of 2026-10-24** ([privacy centre](https://privacy.claude.com/en/articles/7996868-is-my-data-used-for-model-training)):

- On **commercial** products (Team, Enterprise, API), Anthropic does not use customer data to train models by default.
  The customer organisation is the data controller and Anthropic acts as processor.
- On **consumer** plans (Free, Pro, Max), chats may be used to improve models only if the user turns on the
  model-improvement setting.
- **Incognito chats** are not saved to history or memory and are not used for training; on Team and Enterprise they are
  still retained for 30 days for safety purposes.

The practical lesson: use the account and workspace your organisation has approved. A personal consumer account is not
an approved place for company data just because a setting is switched off. Telling Claude "don't keep this" does not
change how data is processed or retained; only the right tool, settings and data minimisation do.

### 6.3 Following organisational AI policy and governance

Typical elements of an AI policy and what they mean for you:

| Policy element | Your obligation |
|---|---|
| Approved tools and accounts | Use the sanctioned Claude workspace, not personal accounts or unapproved apps |
| Data rules | Follow the classification table; get approval for exceptions before, not after |
| Approved connectors and integrations | Enable only what IT has approved; do not add unverified custom connectors on your own authority |
| Human review requirements | Apply the required review for customer-facing, regulated or people-affecting outputs |
| Disclosure | Disclose AI assistance where policy or context requires it (for example in client deliverables or academic work) |
| Record keeping | Keep prompts, sources and decisions for important work where policy requires |
| Incident reporting | Report mistakes such as uploading restricted data, or harmful outputs, through the official channel promptly |

When policy is unclear, **ask the policy owner** (often a privacy, security or AI governance team) and pause the risky
part of the task. Do not interpret silence as permission, and do not work around a control because it is inconvenient.
If you think a rule blocks a valuable use, propose a change through governance rather than ignoring it.

Admin controls in the Claude apps (which connectors are enabled, which actions they may take, memory defaults, sharing)
are part of governance. They complement, but do not replace, individual judgement.

### 6.4 Ethical implications

| Theme | What it looks like in daily work |
|---|---|
| **Accuracy and honesty** | Do not present unverified AI output as fact; correct errors you discover |
| **Fairness and bias** | Review people-related outputs for bias; do not let AI rank, screen or judge people without human oversight |
| **Transparency** | Be open about AI assistance where it matters to the reader or where policy requires |
| **Accountability** | The person who uses the output is responsible for it; "the AI said so" is not a defence |
| **Privacy and dignity** | Treat other people's information as you would want yours treated |
| **Intellectual property** | Do not ask Claude to reproduce copyrighted material wholesale; check that outputs you publish do not copy others' work |
| **Impact on people** | Consider how changes to workflows affect colleagues' roles, skills and workload; involve them |
| **Over-reliance** | Keep your own expertise sharp; use Claude to support judgement, not replace it |

Anthropic publishes its approach to safety (including its constitution for Claude and its usage policy). Those shape
what Claude will and will not do, but organisational ethics are your responsibility as the user.

## Decision rules and heuristics

- **Classify the data before you share it.** If you do not know the class, find out first.
- **Minimise before you upload**: redact, pseudonymise, aggregate or use synthetic data. This is usually better than
  either abandoning the task or uploading everything.
- **Model instructions are not data controls.**
- **Approved commercial workspace for company data; never a personal account.**
- **High-stakes decisions about people stay with qualified humans.**
- **Unclear policy → ask and pause, not guess and proceed.**
- **Made a mistake with data → report it promptly through the official channel.**

## Worked mini-scenarios

**Scenario 1 – Grievance notes.** An HR adviser at *Northwind Lending* wants Claude to find themes across 40 grievance
case notes that include names, managers and medical details. Policy classifies these as restricted. *Approach:* ask the
privacy team whether this use is approved; if it is, pseudonymise names, remove medical details not needed for theme
analysis, use the organisation's commercial workspace, and keep the key offline. If it is not approved, aggregate the
themes manually and use Claude only on the de-identified summary.

**Scenario 2 – The helpful personal account.** A consultant's company workspace is slow to approve a new connector, so
they consider pasting client documents into their personal Pro account "with training switched off". *Answer:* no. The
personal account is not an approved tool for client data, regardless of settings. Escalate the approval delay instead.

**Scenario 3 – Screening candidates.** A hiring manager asks Claude to rank 200 applicants and reject the bottom half
automatically. *Answer:* inappropriate as described. Claude can help draft structured, job-related criteria and
summarise applications for a human reviewer, with bias checks, but rejection decisions stay with trained people under
the organisation's hiring policy and applicable employment law.

**Scenario 4 – Discovered mistake.** After uploading a file, an analyst notices it contained a column of customer home
addresses. *Approach:* stop, delete the chat or file as your tools allow, and report through the incident process. Do
not quietly delete and move on; the privacy team may have obligations to assess it.

## Common traps

- Believing that asking Claude not to remember data makes uploading it acceptable.
- Assuming a consumer account with training switched off is equivalent to an approved enterprise workspace.
- Choosing to skip a valuable task entirely when anonymisation would make it safe.
- Treating "internal use only" as a reason to ignore data rules.
- Letting AI make final decisions about individuals.
- Waiting until after a pilot to ask governance for approval.
- Hiding AI involvement where disclosure is expected.

## Modules and labs

| Objective | Module pages | Labs |
|---|---|---|
| 6.1 | [Responsible use](../../../02-claude-fundamentals/05-responsible-use.md), [Capabilities and limitations](../../../01-ai-and-llm-fundamentals/07-capabilities-and-limitations.md), [Anthropic's safety approach](../../../02-claude-fundamentals/04-anthropic-safety-approach.md) | [Lab 13](../../../19-hands-on-labs/lab-13-human-in-the-loop/README.md) |
| 6.2 | [Data exfiltration and disclosure](../../../12-ai-security/04-data-exfiltration-and-disclosure.md), [Data governance and compliance](../../../13-enterprise-ai-architecture/05-data-governance-and-compliance.md) | [Lab 15](../../../19-hands-on-labs/lab-15-sensitive-data-protection/README.md) |
| 6.3 | [AI governance](../../../12-ai-security/12-ai-governance.md), [Enterprise deployment controls](../../../12-ai-security/14-enterprise-deployment-controls.md) | [Lab 15](../../../19-hands-on-labs/lab-15-sensitive-data-protection/README.md), [Lab 20](../../../19-hands-on-labs/lab-20-secure-enterprise-architecture/README.md) |
| 6.4 | [Anthropic's safety approach](../../../02-claude-fundamentals/04-anthropic-safety-approach.md), [Responsible use](../../../02-claude-fundamentals/05-responsible-use.md), [Human oversight](../../../12-ai-security/13-human-oversight.md) | [Lab 13](../../../19-hands-on-labs/lab-13-human-in-the-loop/README.md) |

Hands-on: [practical exercises for Domain 6](../practical-exercises.md#domain-6--governance-risk-and-responsible-use).

## Self-check

1. List four data-minimisation techniques.
2. Why is "tell Claude not to retain the file" not an adequate control?
3. What should you do when your AI policy does not clearly cover a task?
4. Give an example of an inappropriate use involving decisions about people, and an appropriate alternative.
5. Name four ethical themes relevant to everyday Claude use.

<details>
<summary>Answers</summary>

1. Any four of: redaction, pseudonymisation, aggregation, synthetic or sample data, sharing only relevant excerpts.
2. An instruction to the model does not change how the platform processes or retains data, and it does not satisfy a
   policy rule about which data may enter which tool. Controls are the approved tool, settings and minimisation.
3. Pause the risky part, ask the policy owner (privacy, security or governance), and proceed only with approval.
4. Auto-rejecting job applicants or credit applications based on AI ranking. Alternative: use Claude to draft
   structured criteria or summaries for a trained human decision-maker, with bias review.
5. Any four of: accuracy and honesty, fairness and bias, transparency, accountability, privacy, intellectual property,
   impact on people, over-reliance.

</details>
