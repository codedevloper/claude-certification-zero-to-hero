# Managing Long Context

> **Level:** Intermediate · **Time:** ~45 min · **Exam relevance:** CCAO-F D2, D3 · CCAR-P D2, D3

## In plain English

Claude can read a lot at once: current models accept up to 1M tokens of context (as of 2026-10-24), which is
thousands of pages. But being *able* to read a whole binder is not the same as finding the right paragraph in it. How
you lay out long material, and what you ask Claude to do with it, makes a large difference to accuracy.

Three habits do most of the work:

1. **Documents first, question last.** Put the long material at the top and your instructions and question at the end.
2. **Label every document.** Wrap each one in tags with its source and other metadata.
3. **Quotes before conclusions.** Ask Claude to pull out the relevant passages first, then answer from those quotes.

And one habit for conversations: **know when to start fresh** rather than letting a chat grow forever.

## Why it matters

- Anthropic reports that putting queries at the end of long prompts can improve response quality by up to 30% in its
  tests, especially with complex multi-document inputs (Prompting best practices, checked 2026-10-24).
- Quote-first grounding focuses Claude on the relevant text, makes answers checkable, and reduces unsupported claims
  (see [hallucinations](../01-ai-and-llm-fundamentals/06-hallucinations.md)).
- Long conversations accumulate stale or contradictory material that drags quality down. Deciding when to restart,
  summarise or persist is a named Foundations objective (CCAO-F-3.4); optimising context and tokens is a Professional
  objective (CCAR-P-2.4).

## How it works

### 1. Placement: long data at the top

For prompts with roughly 20,000 or more tokens of documents or data, Anthropic recommends:

```text
[long documents, inside tags]       <- top
[examples, if any]
[instructions]
[the specific question]             <- bottom
```

The question is then the last thing Claude reads before answering, with the material it refers to already in view.

### 2. Structure: one tag per document, with metadata

```xml
<documents>
  <document index="1">
    <source>architecture_review_2026Q3.md</source>
    <date>2026-08-14</date>
    <document_content>
    {{REVIEW}}
    </document_content>
  </document>
  <document index="2">
    <source>incident_postmortem_INC-2231.md</source>
    <date>2026-09-02</date>
    <document_content>
    {{POSTMORTEM}}
    </document_content>
  </document>
</documents>
```

Metadata such as source, date, author or version lets Claude cite precisely and reason about which document is more
recent or more authoritative. Tell it how to resolve conflicts: "If documents disagree, prefer the most recent and
mention the disagreement."

### 3. Grounding: quotes first

Ask Claude to extract relevant quotes into a tagged section, then answer using only those quotes:

```text
First, find the passages in the documents that are relevant to the question and copy them
word for word into <quotes> tags, each with its document index. If nothing is relevant,
write "No relevant passages found."
Then answer the question inside <answer> tags, using only the quoted passages. Refer to
quotes by document index. If the quotes do not answer the question, say so.
```

Benefits:

- Claude focuses on the relevant text and ignores the rest.
- A reviewer, or code, can check every quote against the source.
- "No relevant passages found" gives the model a sanctioned way to say "I don't know".

In the API, the [citations feature](../06-claude-api/04-vision-documents-and-citations.md) provides machine-verifiable
citations for documents you supply, which is stronger than prompted quoting when you need exact provenance.

### 4. Send only what is relevant

A 1M-token window is a ceiling, not a target. Before loading everything:

- **Pre-filter** with search or retrieval so only candidate sections are included (see
  [RAG versus long context](../11-rag-and-knowledge-systems/07-rag-vs-long-context.md)).
- **Split large jobs**: analyse sections separately, then synthesise (see
  [task decomposition](../03-prompt-engineering/05-task-decomposition-and-chaining.md)).
- **Remove boilerplate** such as repeated headers, legal footers and navigation text.
- **Cache** large documents that you query repeatedly (see [prompt caching](03-prompt-caching.md)).

Do not silently truncate a document to make it fit. If something genuinely cannot fit, split it and say so in the
output, or tell the user.

### 5. Long conversations: restart, summarise or persist

| Situation | Best move |
|---|---|
| Chat has drifted across several topics | Start a new chat for the new topic |
| Long working session on one task, but early detail is no longer needed | Ask Claude for a summary of decisions and open questions, then start a new chat with that summary |
| Information needed across many future sessions | Persist it: Project knowledge or instructions, memory, or a notes file |
| An agent loop that runs for hours | Automatic [compaction and context editing](05-compaction-and-context-editing.md) plus a [memory](04-memory-and-persistence.md) or notes file |

A useful hand-off summary includes: the goal, decisions made and why, current state, open questions, and constraints
that still apply.

## Example

*Contoso Health* (fictional) asks Claude which open risks from an architecture review were addressed by a later
incident post-mortem. The documents go first, each tagged; the instructions ask for quotes first; and the code checks
that each quote really appears in the source before showing the answer.

```python
import re
from pathlib import Path

import anthropic

client = anthropic.Anthropic()  # API key from ANTHROPIC_API_KEY

docs = {
    1: ("architecture_review_2026Q3.md", Path("data/review.md").read_text(encoding="utf-8")),
    2: ("incident_postmortem_INC-2231.md", Path("data/postmortem.md").read_text(encoding="utf-8")),
}

doc_block = "<documents>\n" + "\n".join(
    f'<document index="{i}">\n<source>{name}</source>\n<document_content>\n{text}\n'
    f"</document_content>\n</document>"
    for i, (name, text) in docs.items()
) + "\n</documents>"

question = (
    "Which risks listed in document 1 are addressed by actions in document 2?\n\n"
    "First copy the relevant passages word for word into <quote doc=\"N\"> tags. "
    "Then answer inside <answer> tags using only those quotes. If a risk is not addressed, "
    "say so explicitly."
)

response = client.messages.create(
    model="claude-opus-5-5",
    max_tokens=8000,
    output_config={"effort": "medium"},
    messages=[{"role": "user", "content": f"{doc_block}\n\n{question}"}],  # documents first
)
if response.stop_reason != "end_turn":
    raise RuntimeError(f"Incomplete answer: {response.stop_reason}")

text = next(b.text for b in response.content if b.type == "text")

# Verify every quote against its source document before trusting the answer.
for doc_id, quote in re.findall(r'<quote doc="(\d+)">(.*?)</quote>', text, re.DOTALL):
    source_text = docs[int(doc_id)][1]
    status = "ok" if quote.strip() in source_text else "NOT FOUND - review"
    print(f"[doc {doc_id}] {status}: {quote.strip()[:80]}")
```

> **Cost:** requires API credits (live mode). Long documents mean many input tokens per call; cache them if you ask
> several questions.

## Enterprise use case

*Northwind Lending* (fictional) used Claude to compare 30 supplier contracts against a new data-processing standard.
The first approach pasted all contracts into one chat and asked "which contracts are non-compliant?". Answers were
plausible but missed clauses in the middle contracts, and reviewers could not verify them.

The redesign: one request per contract (documents first, standard included, question last); quote-first answers with
a fixed list of clauses to look for; automatic verification that each quote exists in the contract; and a final
synthesis step over the 30 structured results. The contracts and standard are cached between the per-clause
questions. Reviewers now spend their time on the flagged clauses rather than re-reading whole contracts.

## Common mistakes

- **Question first, documents after.** Works for short inputs; underperforms for long ones.
- **Untagged concatenation.** Claude cannot cite or distinguish sources it cannot tell apart.
- **Asking for conclusions without evidence.** Makes errors hard to spot.
- **Trusting quotes without checking.** Quotes can be paraphrased or slightly altered; verify them, or use the
  citations feature.
- **Filling the window because it is there.** Irrelevant material costs money and dilutes attention.
- **Never restarting.** Very long chats carry stale instructions and abandoned ideas.

## Security considerations

- **Long documents are a classic injection vector.** A contract, email or web page can contain instructions. Keep
  documents in tags, tell Claude they are data, and never let document content authorise actions. See
  [indirect prompt injection](../12-ai-security/03-indirect-prompt-injection.md).
- **Minimise sensitive content.** Redact personal data that the task does not need before sending documents.
- **Summaries can leak.** Hand-off summaries and notes may carry sensitive details into new sessions or other users'
  contexts; apply the same handling rules.
- **Check data residency and retention** rules for the documents you send (see
  [data governance and compliance](../13-enterprise-ai-architecture/05-data-governance-and-compliance.md)).

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| Misses information in the middle of a long input | Weak structure; question at the top | Tag documents, put the question last, ask for quotes first |
| Mixes up which document said what | No indexes or sources | Add `index` and `<source>`; ask for citations by index |
| Quote check fails | Model paraphrased | Re-instruct "word for word"; use API citations for exact spans |
| Request rejected as too large | Exceeds context or request size limits | Pre-filter, split, or use the Files API for large files |
| Chat answers reflect abandoned ideas | Long, drifting conversation | Summarise decisions and start a new chat |

## Check your understanding

1. Where should long documents go relative to your question, and what improvement does Anthropic report?
2. Describe the quote-first grounding pattern and two benefits.
3. A chat about one project has run for two days and answers are getting muddled. What would you do?
4. Why is it a mistake to silently truncate a document that does not fit?

<details>
<summary>Answers</summary>

1. At the top, with the instructions and question at the end. Anthropic reports up to 30% better response quality in
   its tests, especially for complex multi-document inputs.
2. Ask Claude to copy relevant passages word for word into tags, then answer using only those quotes. It focuses Claude
   on relevant text, makes answers verifiable, and gives a natural way to say no relevant information was found.
3. Ask Claude for a summary of the goal, decisions, current state and open questions; check it; start a new chat with
   that summary (or put durable facts in Project knowledge or memory).
4. The answer will be based on incomplete information without anyone knowing. Split the work or tell the user what
   could not be processed.

</details>

## Further reading

- [Prompting best practices: long context prompting](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices) (Anthropic docs)
- [Citations](https://platform.claude.com/docs/en/build-with-claude/citations) (Anthropic docs)
- [Context windows](https://platform.claude.com/docs/en/build-with-claude/context-windows) (Anthropic docs)
- [Grounding and citations](../11-rag-and-knowledge-systems/05-grounding-and-citations.md) in this repository
- [Lab 05 — Context management](../19-hands-on-labs/lab-05-context-management/README.md)
- Next page: [Prompt caching](03-prompt-caching.md)
