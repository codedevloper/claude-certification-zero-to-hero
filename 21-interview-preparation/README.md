# 21 · Interview Preparation

Question sets with model answers for roles that build, design or secure systems on Claude and other large language
models: **AI engineer**, **solution architect** and **AI security engineer**. Everything here is original; none of it
comes from, or reconstructs, any certification exam.

## Question sets

| File | Questions | Best for |
|---|---|---|
| [Conceptual questions](conceptual-questions.md) | 30 | LLM fundamentals, prompting, context engineering, the API, tools, MCP, RAG, agents, evaluation |
| [System design questions](system-design-questions.md) | 26 | Whiteboard prompts with clarifying questions, architecture, trade-offs and what interviewers look for |
| [Security questions](security-questions.md) | 28 | Threat modelling, prompt injection, agent permissions, MCP, data protection, governance, incidents |
| [Stakeholder and behavioural](stakeholder-and-behavioural.md) | 26 | Discovery, communicating trade-offs, delivery, leadership, ethics (STAR format) |

## Which sets for which role

| Role | Focus | Also review |
|---|---|---|
| AI engineer | Conceptual (all), system design 1–3, 9–10, 13–14, 20 | [Claude API cheat sheet](../22-cheat-sheets/claude-api.md), [labs](../19-hands-on-labs/README.md) |
| Solution architect | System design (all), stakeholder (all), conceptual 11–13, 20–30 | [13 · Enterprise AI architecture](../13-enterprise-ai-architecture/README.md), [CCAR-P one-pager](../22-cheat-sheets/ccar-p-one-pager.md) |
| AI security engineer | Security (all), system design 4, 11, 12, 15, 19, 25, conceptual 17–19 | [AI security cheat sheet](../22-cheat-sheets/ai-security.md), [12 · AI security](../12-ai-security/README.md) |
| Technical leader | Stakeholder (all), system design 6, 11, 12, 20, 26 | [13 · Business value and ROI](../13-enterprise-ai-architecture/08-business-value-and-roi.md) |

## How to practise

1. **Answer out loud before reading the model answer.** Interviews test spoken reasoning; reading answers silently
   builds false confidence.
2. **Time yourself.** Conceptual answers in about two minutes; system design in 35–45 minutes; behavioural answers in
   about two minutes using STAR.
3. **Use your own experience.** The behavioural model answers use fictional examples to show structure. Replace them
   with real situations you can discuss in depth. Never invent experience.
4. **Build something.** Interviewers probe beyond the first answer. Having run the [hands-on labs](../19-hands-on-labs/README.md)
   or a [real-world project](../20-real-world-projects/README.md) gives you concrete follow-up details.
5. **Keep facts current.** Model names, prices and API features change. Answers here are dated 2026-10-24; check the
   [cheat sheets](../22-cheat-sheets/README.md) and official docs before an interview.

## What strong candidates do

| Signal | Example |
|---|---|
| Clarify before solving | "How many documents, how often do they change, and do permissions vary per user?" |
| Prefer the simplest design | "A routing workflow handles this; an agent adds cost without benefit here." |
| Measure | "I'd build a 100-case eval set and compare cost per completed task." |
| Design for failure | "Assume the model can be manipulated; enforce permissions in the tool." |
| Quantify | "About 8,000 alerts a day, so Haiku for first-pass triage keeps cost manageable." |
| Communicate trade-offs | "Option A is faster to ship; Option B is cheaper at scale. I recommend A for the pilot." |

## Common pitfalls

- Jumping to multi-agent architectures for problems a single call can solve.
- Describing prompt instructions as security controls.
- Ignoring evaluation ("we'll test it manually").
- Quoting outdated API patterns, such as `temperature` tuning or assistant prefill, which current Claude models reject.
- Overclaiming accuracy or hiding limitations from stakeholders.

## Related

- [16 · Certification tracks](../16-certification-tracks/README.md): the CCAR-P track overlaps strongly with
  architect interviews.
- [23 · Flashcards](../23-flashcards/README.md) for quick recall of terms.
- [Glossary](../GLOSSARY.md).
