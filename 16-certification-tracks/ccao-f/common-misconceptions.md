# CCAO-F Common Misconceptions

> Part of the [CCAO-F track](README.md). Objective IDs come from [`registry.yaml`](../registry.yaml). Product facts are
> as of 2026-10-24 and were checked against [support.claude.com](https://support.claude.com/).

Each entry gives the misconception, the correction and why it matters. Many wrong answer options in judgement-style
exams are built from beliefs like these, so learn to recognise them.

## Prompting (Domain 1)

**1. "Longer prompts always produce better results."**
Relevant detail helps; padding, repetition and contradictory rules hurt. Aim for complete, not long: goal, context,
audience, constraints, format and success criteria. *(CCAO-F-1.1)*

**2. "Assigning a role ('You are an expert…') is the key to a good prompt."**
A role can set tone and focus, but it does not supply the missing context, audience or format. A role with no task
details still gives generic output. *(CCAO-F-1.1, 1.4)*

**3. "If the first answer is poor, keep adding follow-ups until it is right."**
Small adjustments work well as follow-ups. When the first attempt went off track, editing the original prompt and
regenerating is usually faster and avoids anchoring on the bad draft. *(CCAO-F-1.3)*

**4. "Breaking a task into steps is slower, so it is always worse."**
For multi-phase or high-stakes work, decomposition improves quality and lets you catch errors between steps. It is only
overhead for simple tasks. *(CCAO-F-1.2)*

**5. "The same prompting style works for every task."**
Analysis, research, drafting and brainstorming need different moves: evidence and reasoning, scope and sources,
audience and voice, volume and variety. *(CCAO-F-1.4)*

## Evaluation (Domain 2)

**6. "If Claude sounds confident, it is probably right."**
Tone and fluency are not evidence. Specific details you did not provide (figures, dates, clause numbers, quotes) are the
first things to verify. *(CCAO-F-2.2)*

**7. "Asking Claude whether it is sure is a good way to check its answer."**
Self-assessment is not independent verification. Self-critique can surface gaps, but validation must check a source
outside the answer. *(CCAO-F-2.3)*

**8. "A citation means the claim is correct."**
Citations make checking easier, but you still need to open them and confirm they exist and say what is claimed.
*(CCAO-F-2.3)*

**9. "A well-written summary is a complete summary."**
Summaries can be accurate yet omit the most important point, or skip one of several documents. Check completeness
against the brief, item by item. *(CCAO-F-2.1)*

**10. "Human review is a sign the AI is not good enough."**
Review in proportion to risk is part of responsible use at every quality level. External, irreversible, regulated or
people-affecting outputs need qualified human review regardless of the model. *(CCAO-F-2.4)*

**11. "Artifacts are just for code."**
As of 2026-10-24, artifacts cover documents, decks, dashboards, designs and small interactive tools. Choose them for
substantial, shareable or reusable work; choose inline answers for quick replies and structured data for anything going
into another tool. *(CCAO-F-2.6)*

## Products and models (Domain 3)

**12. "Always use the most powerful model to be safe."**
The best model is the cheapest one that meets the quality bar. More capable models are slower and use more of your
allowance; light models are often fine for simple, repetitive tasks. *(CCAO-F-3.3)*

**13. "A better model means I no longer need to fact-check."**
More capable models make fewer mistakes, but none is free of hallucination. Verification still depends on stakes.
*(CCAO-F-3.2, 2.3)*

**14. "Research and web search are the same thing."**
Web search fetches current information in a normal chat. Research runs a multi-step, multi-source investigation across
the web and your enabled connectors and returns a cited report; it takes longer and uses limits faster. *(CCAO-F-3.1)*

**15. "With a huge context window, I never need to restart a chat."**
Large windows help, and paid plans automatically summarise older messages in long chats, but long chats still drift,
carry superseded information and consume more usage. Restart, summarise or persist. *(CCAO-F-3.4)*

**16. "A new chat automatically knows what I discussed yesterday."**
Only if memory or chat search is enabled and relevant, or if the information is in Project knowledge or instructions.
Do not rely on memory for team-critical information. *(CCAO-F-3.4)*

## Configuration (Domain 5)

**17. "Uploaded Project files update when the original changes."**
Uploaded knowledge is a snapshot. Replace files when sources change, or use a connector for content that changes
frequently. *(CCAO-F-5.2, 5.4)*

**18. "A connector shows Claude the same thing for everyone."**
Each user authenticates individually, so Claude sees what that user can access. Results can differ between users.
*(CCAO-F-5.2)*

**19. "Project instructions are a security control."**
Instructions guide behaviour; they do not stop someone uploading restricted data or guarantee the model never errs.
Permissions, admin settings, data policy and human review provide the boundaries. *(CCAO-F-5.3, 6.3)*

**20. "More knowledge files make a Project smarter."**
Irrelevant, outdated or conflicting files dilute and confuse answers. Curate a small set of current, authoritative
documents. *(CCAO-F-5.1, 7.1)*

**21. "Any custom connector listed online is safe because it works with Claude."**
As of 2026-10-24, the Help Center states custom connectors are not verified by Anthropic. Connect only to trusted
services, review requested permissions, and follow organisational approval. *(CCAO-F-5.2, 6.3)*

## Governance (Domain 6)

**22. "Telling Claude not to remember sensitive data makes it fine to upload."**
An instruction to the model does not change how the platform processes or retains data, and does not satisfy a policy
that prohibits that data in the tool. Minimise first: redact, pseudonymise, aggregate. *(CCAO-F-6.2)*

**23. "If training is switched off in my personal account, I can use it for work data."**
Approved tools are about contracts, controls and audit, not one setting. Use the organisation's approved workspace.
*(CCAO-F-6.2, 6.3)*

**24. "When data is sensitive, the only safe option is not to use AI at all."**
Often the better answer is to make the data safe: anonymise or aggregate it, or use synthetic data, within policy. Skip
the task only if no compliant route exists. *(CCAO-F-6.2)*

**25. "Internal use means data rules do not apply."**
Data classification and privacy obligations apply regardless of whether the output stays internal. *(CCAO-F-6.2, 6.3)*

**26. "If the policy does not mention it, it is allowed."**
Silence is not permission. Ask the policy owner and pause the risky part. *(CCAO-F-6.3)*

**27. "AI can make objective decisions about people because it has no feelings."**
Models can reflect biases in their training data and prompts. Decisions about employment, credit, health or rights need
qualified human judgement, with AI as support at most. *(CCAO-F-6.1, 6.4)*

## Workflow and troubleshooting (Domains 4 and 7)

**28. "The best first use case is the one with the biggest potential impact."**
The best first pilot is frequent, checkable, low risk and uses permitted data. High-impact, high-risk ideas come later,
with evidence and controls. *(CCAO-F-4.1)*

**29. "Automating a step means removing the human."**
Automation usually moves the human from doing to reviewing. Removing review from high-stakes steps requires an equal
or better control and approval. *(CCAO-F-4.4, 2.4)*

**30. "Poor output means the model is the problem."**
Check the inputs first: outdated or conflicting files, contradictory instructions, missing context, the wrong feature,
or a drifting chat. *(CCAO-F-7.1)*

**31. "Optimisation means making it faster."**
Optimise quality per unit of effort. A faster workflow that sends more errors out is worse. Track a quality measure
alongside time. *(CCAO-F-7.3)*

**32. "An Associate should build whatever integration the team asks for."**
The credential explicitly includes recognising limits and escalating complex or technical work, such as system
integrations or public-facing products, to Claude Architects and Developers. *(CCAO-F-4.3, 4.5)*

## About the exam itself

**33. "A good score on unofficial practice tests means I will pass."**
Unofficial scores (including this repository's mock exams) are not the official scaled score. Use them to find weak
domains, not to predict a result. The official passing standard is in [`registry.yaml`](../registry.yaml).

**34. "Multiple-response items are just multiple-choice with extra options."**
Each multiple-response item tells you how many answers to select. Treat each option as a true/false judgement against
the scenario. See [exam-day.md](exam-day.md).

Continue with [revision-notes.md](revision-notes.md).
