# Domain 3 · Product and Model Selection (12%)

> Part of the [CCAO-F track](../README.md). Objective IDs and weights come from [`registry.yaml`](../../registry.yaml).
> Product and model facts were checked against [support.claude.com](https://support.claude.com/) and Anthropic's model
> documentation **as of 2026-10-24**. Features, plan availability and model names change often; recheck before relying
> on a detail.

## Objectives

| ID | What you must be able to do (paraphrased) |
|---|---|
| CCAO-F-3.1 | Pick the right Claude feature for the job: Projects, research, plain chat or artifacts |
| CCAO-F-3.2 | Tell the Claude model families apart (Haiku, Sonnet, Opus) |
| CCAO-F-3.3 | Match the model to the task's cost, speed and quality needs |
| CCAO-F-3.4 | Work within context limits and memory: know when to restart, summarise or persist information |

## Concepts to master

- What each Claude app feature is for, and the signal in a scenario that points to it.
- Model tiers as a trade-off: more capable models are slower and use more of your budget or usage allowance.
- The context window as Claude's working memory for one conversation, measured in tokens.
- The difference between a conversation's context, Project knowledge, memory across chats and chat search.
- Why long conversations degrade and cost more, and the three remedies: restart, summarise, persist.

## Detailed notes

### 3.1 Choosing the right product feature

| Feature | What it is (as of 2026-10-24) | Choose it when the scenario says... |
|---|---|---|
| **Chat** | A single conversation | "Quick question", "one-off", "draft this reply" |
| **Projects** | A workspace with its own chats, a knowledge base of uploaded files and Project instructions that apply to every chat in it. Available on all plans; Free accounts can create up to five Projects. On paid plans, Claude switches to a retrieval (RAG) mode when knowledge nears the context limit, expanding capacity by up to about ten times. Team and Enterprise can share Projects with "Can view" or "Can edit" permissions | "Recurring work", "the same documents every week", "the whole team should get consistent answers", "a standing set of rules" |
| **Research** | Claude runs many searches that build on each other across the web and your enabled connectors, then reports with citations. Paid plans only, needs web search switched on, and can use usage limits faster than normal chat | "Investigate", "survey the market", "multi-source", "compare what is out there", "with sources" |
| **Web search** | Claude looks up current information during a normal chat | "Latest", "current", "this week" but a quick answer is enough |
| **Artifacts** | Substantial, shareable work beside the chat: documents, decks, dashboards, small interactive tools. Requires the "Create and edit files" (code execution and file creation) capability | "Something I will edit and share", "a reusable tool", "a dashboard", "a document to hand over" |
| **Connectors** | Links to tools such as Google Drive, Gmail, Google Calendar, Microsoft 365 or Slack, so Claude can read (and sometimes act in) those systems with your permissions | "The files live in Drive", "check my calendar", "find the email thread" |
| **Skills** | Packaged instructions (and optional scripts) that teach Claude a repeatable way to do a task; Claude loads only the Skills a task needs | "We do this the same way every time", "apply our brand template", "standard report procedure" |
| **Memory and chat search** | Claude can search and reference past chats and keep memory across conversations, where enabled | "Build on what we discussed last week", "remember my preferences" |
| **Incognito chat** | A chat not saved to history or memory, available on all plans | "Don't keep this conversation", "one-off sensitive brainstorming" (still subject to policy, see Domain 6) |

Two exam-style distinctions worth remembering:

- **Project knowledge versus a chat attachment.** An attachment helps one chat. Project knowledge is available to every
  chat in the Project. If the same reference material is needed repeatedly, it belongs in the Project.
- **Research versus web search.** Web search answers a current-facts question quickly. Research is a deliberate,
  multi-step investigation that takes longer and returns a cited report. As of 2026-10-24, research runs on Claude Opus
  5.5 (falling back to Claude Opus 4.8) whatever model the chat has selected, per the
  [research help article](https://support.claude.com/en/articles/11088861-use-research-on-claude).

### 3.2 Model families

Claude models come in tiers. The names stay stable while version numbers advance.

| Family | Position | Typical fit |
|---|---|---|
| **Haiku** | Fastest and lowest cost | High-volume, simple, well-defined tasks: classification, short extraction, quick rewrites, triage |
| **Sonnet** | Balance of capability, speed and cost | Most everyday professional work: drafting, analysis, summarisation, coding help |
| **Opus** | Most capable of the three for complex reasoning; slower and costlier | Hard analysis, long multi-step tasks, nuanced judgement, complex documents |

As of 2026-10-24 the current models are Claude Haiku 5.5, Claude Sonnet 5.5 and Claude Opus 5.5. Anthropic also offers
**Claude Fable 5.1**, described as its most capable widely released model, priced above the Opus tier and aimed at the
most demanding reasoning and long-running work. The exam objective names Haiku, Sonnet and Opus; know that the tier
logic (capability against speed and cost) applies to whatever names are current. To give a sense of scale, Anthropic's
API list prices per million input tokens were roughly $0.10 (Haiku 5.5), $2 (Sonnet 5.5), $4 (Opus 5.5) and $10 (Fable
5.1) as of early October 2026; the Claude apps use plan usage limits rather than per-token billing, but more capable
models consume those limits faster. Check the live [models overview](https://platform.claude.com/docs/en/about-claude/models/overview)
and [pricing](https://platform.claude.com/docs/en/about-claude/pricing) pages.

On Team and Enterprise plans, administrators control which models are enabled for the organisation (the research
help article, for example, notes that an admin must keep at least one of the models research uses enabled).

### 3.3 Matching model to cost, speed and quality

Ask three questions:

1. **How hard is the reasoning?** Multi-step judgement, ambiguity or subtle trade-offs point to a more capable model.
2. **How much volume and how fast?** Many repetitive items, or someone waiting in real time, point to a faster model.
3. **What does an error cost?** If mistakes are cheap and easily caught, a lighter model is fine; if they are expensive,
   spend more on capability *and* on review.

A practical approach: start with the balanced model (Sonnet) for everyday work; move down to Haiku when the task proves
simple and repetitive and quality holds; move up to Opus (or Fable) when Sonnet's output misses nuance on a genuinely
hard task. Test on a few real examples before switching a whole workflow. The best model is the cheapest one that meets
the quality bar, not the most powerful one available.

Remember that a more capable model does not remove the need to verify. Hallucination risk falls with capability but
does not disappear.

### 3.4 Context limits and memory

**The context window** is everything Claude can consider at once in a conversation: your messages, its replies,
attached files and Project content in use. It is measured in tokens (pieces of words; a page of English is very roughly
500–800 tokens). As of 2026-10-24, the Help Center says the newest models on paid plans support up to 1 million tokens,
with others at 500,000 or 200,000, and part of the window is always reserved for Claude's reply
([context window article](https://support.claude.com/en/articles/8606394-how-large-is-the-context-window-on-paid-claude-plans)).

**What happens as a chat grows.** Each new message is processed together with the history, so long chats use more of
your usage allowance. On paid plans with code execution enabled, Claude automatically summarises earlier messages when
the conversation nears the limit (compaction) so the chat can continue; the full history remains available to
reference. Even so, very long chats that wander across topics accumulate stale or contradictory instructions, and
quality can drift.

**The three remedies:**

| Remedy | Use it when | How |
|---|---|---|
| **Restart** | The chat has drifted, earlier wrong turns are anchoring answers, or you are starting a new topic | Open a new chat (in the same Project if the reference material is there) |
| **Summarise** | You need continuity but the history is long | Ask Claude for a handover summary of decisions, open questions and key facts; paste it into a fresh chat |
| **Persist** | Information is needed across many chats | Put reference documents in Project knowledge, standing rules in Project instructions, repeatable procedures in a Skill; use memory for personal preferences where enabled |

**Memory and chat search, as of 2026-10-24** ([Help Center](https://support.claude.com/en/articles/11817273-use-claude-s-chat-search-and-memory-to-build-on-previous-context)):
Claude can search and reference past chats (a setting called "Search and reference chats") and can keep memory as
individual topics. By default it does not store topics on sensitive subjects such as health, religion or politics, and
some categories, like government ID numbers and financial account numbers, are never saved. Release notes indicate memory
is on by default for Free, Pro and Max users and off by default for Team and Enterprise organisations, where admins
decide. Incognito chats are not saved to history or memory. Memory is a convenience, not a records system: anything the
whole team relies on belongs in Project knowledge or instructions, where it is visible and maintained.

## Decision rules and heuristics

- **Recurring work plus shared reference material → Project.**
- **Multi-source investigation with citations → research. Quick current fact → web search.**
- **Substantial deliverable to edit or share → artifact. Short answer → inline.**
- **Simple, repetitive and high volume → Haiku. Everyday → Sonnet. Hard reasoning → Opus (or Fable for the hardest).**
- **Pick the cheapest model that passes your quality check on real examples.**
- **Drifted chat → restart. Long but healthy chat → summarise and continue. Needed everywhere → persist in the Project.**

## Worked mini-scenarios

**Scenario 1 – Weekly board pack.** A finance business partner at *Acme Logistics* prepares the same monthly commentary
using the same chart of accounts, house style guide and prior packs. Starting a fresh chat each month and re-uploading
everything wastes time and gives inconsistent tone. *Better:* a Project with the style guide and glossary as knowledge
and instructions that set structure and tone.

**Scenario 2 – Tagging ten thousand survey comments.** A product team needs each comment tagged with one of eight
themes. The categories are clear and a sample check shows Haiku tags them as well as Sonnet. *Better:* the faster,
cheaper model, with a spot-check sample reviewed each run. (In practice, very high volume may also call for a developer
to automate it through the API; recognising that hand-off is part of the role.)

**Scenario 3 – The three-week chat.** A programme manager has used one chat for three weeks covering four workstreams.
Claude starts mixing up deadlines between workstreams. *Better:* ask for a summary per workstream, verify it, and start
separate chats (or a Project per programme with the summaries as knowledge).

**Scenario 4 – Competitive landscape.** A strategy analyst needs an overview of how six competitors price a service,
with sources. *Better:* research mode, then verify a sample of citations and date-check the pricing pages.

## Common traps

- Defaulting to the most powerful model for everything, which wastes time and usage.
- Assuming a better model removes the need to check facts.
- Expecting a new chat to "remember" a previous chat's content without memory, chat search or Project knowledge.
- Treating memory as the place for team-wide rules (it is personal and less visible; use Project instructions).
- Uploading the same reference files to every chat instead of using Project knowledge.
- Using research for a simple lookup, or plain chat for a question that needs current, cited information.
- Believing a bigger context window means you never need to restart or summarise.

## Modules and labs

| Objective | Module pages | Labs |
|---|---|---|
| 3.1 | [Product ecosystem](../../../05-claude-products-and-models/01-product-ecosystem.md), [Projects and knowledge](../../../05-claude-products-and-models/04-projects-and-knowledge.md), [Artifacts and output formats](../../../05-claude-products-and-models/05-artifacts-and-output-formats.md) | [Lab 01](../../../19-hands-on-labs/lab-01-first-claude-interaction/README.md), [Lab 04](../../../19-hands-on-labs/lab-04-document-grounded-qa/README.md) |
| 3.2 | [Model families](../../../05-claude-products-and-models/02-model-families.md) | [Lab 06](../../../19-hands-on-labs/lab-06-model-comparison/README.md) |
| 3.3 | [Model selection](../../../05-claude-products-and-models/03-model-selection.md), [Cost optimisation](../../../15-production-operations/03-cost-optimisation.md) | [Lab 06](../../../19-hands-on-labs/lab-06-model-comparison/README.md), [Lab 17](../../../19-hands-on-labs/lab-17-cost-optimisation/README.md) |
| 3.4 | [Context windows](../../../01-ai-and-llm-fundamentals/05-context-windows.md), [Managing long context](../../../04-context-engineering/02-managing-long-context.md), [Memory and persistence](../../../04-context-engineering/04-memory-and-persistence.md), [Compaction](../../../04-context-engineering/05-compaction-and-context-editing.md) | [Lab 05](../../../19-hands-on-labs/lab-05-context-management/README.md) |

Hands-on: [practical exercises for Domain 3](../practical-exercises.md#domain-3--product-and-model-selection).

## Self-check

1. What signal in a request points to a Project rather than a single chat?
2. How does research differ from web search?
3. Put Haiku, Sonnet and Opus in order of speed and of capability.
4. Name the three remedies for context problems and when to use each.
5. Why is memory not the right home for a team's standard operating rules?

<details>
<summary>Answers</summary>

1. Recurring work, shared reference material, or the need for consistent behaviour across many chats or people.
2. Web search quickly retrieves current facts inside a normal chat; research runs a multi-step, multi-source
   investigation (web plus enabled connectors) and returns a cited report, taking longer and using more of your limits.
3. Speed: Haiku fastest, then Sonnet, then Opus. Capability: Opus highest, then Sonnet, then Haiku.
4. Restart when the chat has drifted or changed topic; summarise when you need continuity but the history is long;
   persist (Project knowledge, instructions, Skills, memory) when information is needed across chats.
5. Memory is personal, built automatically and less visible or controllable; team rules belong in Project
   instructions or knowledge, where they are shared, reviewed and maintained.

</details>
