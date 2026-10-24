# Chunking Strategies

> **Level:** Intermediate · **Time:** ~30 min · **Exam relevance:** CCAR-P D3 (3.5)

## In plain English

Chunking is cutting documents into pieces small enough to search precisely and large enough to make sense on their
own. Think of cutting a cookbook into index cards. Cut each card at one sentence and the card "Bake for 40 minutes"
is useless, because you no longer know what is being baked. Put the whole chapter on one card and every search returns
the whole chapter. Good chunking gives you one recipe per card, with the recipe's name written at the top.

## Why it matters

Retrieval can only return chunks you created. If the answer is split across two chunks, or a chunk loses the context
that makes it meaningful, no embedding model or reranker can recover it. Chunking is the cheapest place to win or
lose RAG quality, and it is the first thing to revisit when retrieval metrics are poor.

Chunk size also drives cost and latency: more, smaller chunks mean a bigger index and more candidates to rerank;
larger chunks mean more tokens sent to Claude per answer.

This page supports objective CCAR-P-3.5 ("design RAG pipelines with suitable chunking and indexing") in the
[registry](../16-certification-tracks/registry.yaml).

## How it works

### The four main strategies

| Strategy | How it splits | Strengths | Weaknesses | Good fit |
|---|---|---|---|---|
| **Fixed-size** | Every N tokens (or characters), regardless of content | Simple, predictable, fast | Cuts mid-sentence and mid-table; ignores meaning | Uniform prose, quick baselines, logs |
| **Recursive** | Tries the largest separator first (sections, then paragraphs, then sentences, then words) until each piece fits the size limit | Respects natural boundaries, still bounded in size | Needs a sensible separator list per format | Most mixed text corpora; the usual default |
| **Semantic** | Embeds sentences and starts a new chunk where meaning shifts (similarity between neighbours drops) | Chunks follow topics | Slower and costlier to build; uneven sizes; harder to debug | Long unstructured text with topic drift (transcripts, essays) |
| **Structure-aware** | Uses the document's own structure: headings, list items, table rows, code functions, FAQ pairs, clauses | Chunks match how people look things up; easy citations | Needs a parser per format; depends on clean source structure | Policies, manuals, contracts, API docs, code |

In practice you combine them: structure-aware splitting at headings, then recursive splitting inside any section
that is still too long, with a size cap.

### Size

There is no universal best size. A useful starting range for prose is roughly 200–800 tokens per chunk, then tune
against your evaluation set (see [RAG evaluation](06-rag-evaluation.md)). Factors:

- **Question granularity.** Fact lookups ("what is the hotel cap?") prefer smaller chunks. Explanatory questions
  ("how does the appeals process work?") prefer larger ones.
- **Embedding model input limit.** Chunks longer than the model's limit are truncated silently by some clients.
- **Generation budget.** K chunks multiplied by chunk size is the context you send on every request.

> **Unverified:** Any single "optimal" chunk size quoted in blogs. Results depend on corpus, embedding model and
> queries, so measure on your own data rather than adopting a number.

### Overlap

Overlap repeats the end of one chunk at the start of the next (for example 10–20% of the chunk size). It reduces the
chance that an answer spanning a boundary is lost. Costs: a larger index, near-duplicate results in the top K, and
duplicated text in the prompt. Structure-aware chunking at clean boundaries needs less overlap than fixed-size
chunking. If you use overlap, deduplicate adjacent chunks before sending them to Claude.

### Metadata and context

A chunk on its own often lacks context. "The limit increases by 10% after year two" is useless unless you know which
limit and which product. Three complementary fixes:

1. **Metadata fields** stored alongside the chunk: `doc_id`, `title`, `section_path` ("Card policy > Limits > Increases"),
   `effective_date`, `product`, `language`, `access_label`, `source_url`, `chunk_index`. Use them for filtering, citations
   and debugging.
2. **Header prepending.** Prefix the chunk text with its title and section path before embedding and indexing. Cheap and
   effective.
3. **Contextual chunk descriptions.** Ask a model to write a one- or two-sentence description that situates the chunk in
   its document, and prepend it before embedding and building the keyword index. This is Anthropic's
   [Contextual Retrieval](https://www.anthropic.com/news/contextual-retrieval) technique, covered on the
   [retrieval strategies](04-retrieval-strategies.md) page.

### Special content

| Content | Approach |
|---|---|
| Tables | Keep a table (or row group) intact; repeat the header row in each chunk; consider also storing it as structured data for SQL retrieval |
| Code | Split by function or class; include the file path and signature |
| FAQs | One question-answer pair per chunk |
| Transcripts | Split by speaker turn or topic, keep timestamps as metadata |
| Scanned PDFs | Run OCR first, otherwise there is no text to chunk |
| Very short documents | Do not split; one document, one chunk |

### Parent-child (small-to-big) retrieval

Index small chunks for precise matching, but store a pointer to a larger parent (the full section). Retrieve on the
small chunk, then send the parent to Claude. This gives precise search with enough surrounding context for a good
answer, at the cost of more tokens per answer.

## Example

A structure-aware chunker with recursive fallback and metadata, using only the standard library. Token counts are
approximated as words × 1.3; in production use the provider's tokenizer for the embedding model.

```python
"""Structure-aware Markdown chunker with recursive fallback, overlap and metadata."""
from __future__ import annotations
import re
from dataclasses import dataclass, field

MAX_TOKENS = 400
OVERLAP_TOKENS = 50

def approx_tokens(text: str) -> int:
    return int(len(text.split()) * 1.3)

@dataclass
class Chunk:
    text: str
    metadata: dict = field(default_factory=dict)

def split_recursive(text: str, separators=("\n\n", "\n", ". ", " ")) -> list[str]:
    """Split text using the largest separator that yields pieces under MAX_TOKENS."""
    if approx_tokens(text) <= MAX_TOKENS:
        return [text]
    sep, *rest = separators or (" ",)
    parts, current = [], ""
    for piece in text.split(sep):
        candidate = f"{current}{sep}{piece}" if current else piece
        if approx_tokens(candidate) <= MAX_TOKENS:
            current = candidate
        else:
            if current:
                parts.append(current)
            current = piece
    if current:
        parts.append(current)
    # Recurse on any part that is still too long
    out: list[str] = []
    for p in parts:
        out.extend(split_recursive(p, tuple(rest)) if approx_tokens(p) > MAX_TOKENS and rest else [p])
    return out

def add_overlap(pieces: list[str]) -> list[str]:
    overlapped = []
    for i, p in enumerate(pieces):
        if i == 0:
            overlapped.append(p)
            continue
        tail_words = pieces[i - 1].split()[-int(OVERLAP_TOKENS / 1.3):]
        overlapped.append(" ".join(tail_words) + " " + p)
    return overlapped

def chunk_markdown(doc_id: str, title: str, markdown: str, base_meta: dict) -> list[Chunk]:
    chunks: list[Chunk] = []
    path: list[str] = []
    sections = re.split(r"^(#{1,6} .+)$", markdown, flags=re.MULTILINE)
    body_for_heading: list[tuple[list[str], str]] = []
    for part in sections:
        m = re.match(r"^(#{1,6}) (.+)$", part)
        if m:
            level = len(m.group(1))
            path = path[: level - 1] + [m.group(2).strip()]
        elif part.strip():
            body_for_heading.append((list(path), part.strip()))
    for section_path, body in body_for_heading:
        header = f"{title} > " + " > ".join(section_path) if section_path else title
        for i, piece in enumerate(add_overlap(split_recursive(body))):
            chunks.append(Chunk(
                text=f"[{header}]\n{piece}",  # header prepending for context
                metadata={**base_meta, "doc_id": doc_id, "title": title,
                          "section_path": " > ".join(section_path), "chunk_index": i},
            ))
    return chunks

if __name__ == "__main__":
    doc = """# Card limits
## Initial limit
New card holders receive an initial limit based on verified income.
## Increases
The limit increases by 10% after two years of on-time payments. Customers may request a review once every six months.
"""
    for c in chunk_markdown("card-policy", "Card policy", doc, {"product": "card", "effective_date": "2026-07-01"}):
        print(c.metadata["section_path"], "|", c.text.replace("\n", " ")[:90])
```

Each chunk now carries its section path in both the text (helping embeddings and keyword search) and the metadata
(helping filters and citations).

## Enterprise use case

*Contoso Health* indexes 4,000 clinical operations procedures (synthetic for this example) written in a consistent
template: Purpose, Scope, Steps, Exceptions, References. Their first prototype used 512-token fixed chunks.
Evaluation showed that answers about exceptions were often wrong, because the Exceptions heading landed in one chunk
and its contents in another, and many chunks began mid-step.

The redesign:

- Structure-aware split at template headings; the Steps section split per numbered step group with the procedure
  title and step range prepended.
- No overlap within Steps (boundaries are clean), 15% overlap for the free-text Purpose sections.
- Metadata: `procedure_id`, `version`, `effective_date`, `department`, `site`, `access_label`.
- Tables of dosage thresholds kept whole, and additionally loaded into a database for exact lookup.

Retrieval recall on their 300-question evaluation set improved substantially, and citations now point at a named
section that reviewers can open directly.

## Common mistakes

- **Choosing chunk size by folklore** instead of measuring recall on your own questions.
- **Splitting tables and code blocks mid-way,** which destroys their meaning.
- **Dropping headings,** so chunks lose the context of what they describe.
- **Heavy overlap with large K,** sending the same sentences to Claude several times.
- **Not storing a stable chunk ID,** which makes evaluation, citations and incremental re-indexing hard.
- **Re-chunking without re-embedding.** Any change to chunking means every affected vector must be rebuilt.

## Security considerations

- **Carry access labels onto every chunk.** A chunk inherits the most restrictive label of its source document. A
  section-level restriction must not be lost when sections are merged.
- **Strip hidden content deliberately.** Extraction can surface hidden text, comments and white-on-white text, which is a
  common carrier for indirect prompt injection. Decide what to keep, and log what you removed.
- **Redact before indexing** where the use case does not need personal data. Once personal data is in chunks and vectors,
  deletion requests must reach every copy.

## Troubleshooting

| Symptom | Likely chunking cause | Fix |
|---|---|---|
| Answers miss the second half of a procedure | Section split without overlap or parent retrieval | Structure-aware split, or parent-child retrieval |
| Retrieved chunk is "about" the right thing but vague | Too large; many topics per chunk | Smaller chunks or semantic splitting |
| Chunk retrieved but ambiguous ("it", "this limit") | Missing context | Header prepending or contextual descriptions |
| Duplicate passages in the prompt | Overlap plus large K | Deduplicate, reduce overlap |
| Table numbers wrong | Table flattened or split | Keep tables whole; repeat headers; consider SQL retrieval |

## Check your understanding

1. When would you choose structure-aware chunking over fixed-size chunking?
2. What does overlap protect against, and what does it cost?
3. Give two ways to add context to a chunk that would otherwise be ambiguous.
4. Why is a stable chunk ID useful?
5. What is parent-child retrieval and when does it help?

<details>
<summary>Answers</summary>

1. When documents have reliable structure (headings, clauses, FAQ pairs, functions) that matches how people look things
   up; it yields coherent chunks and precise citations.
2. It protects against answers that span a chunk boundary being lost. It costs index size, near-duplicate results and
   duplicated tokens in the prompt.
3. Prepend the document title and section path; store and use metadata; prepend a model-generated contextual
   description (Contextual Retrieval).
4. It lets you track which chunks were retrieved for evaluation, cite and link back, and update or delete only changed
   chunks during re-indexing.
5. You match on small, precise chunks but send their larger parent section to the model. It helps when queries are
   specific but answers need surrounding context.

</details>

## Further reading

- Anthropic, [Contextual Retrieval](https://www.anthropic.com/news/contextual-retrieval).
- Claude docs, [Citations](https://platform.claude.com/docs/en/build-with-claude/citations): describes how the API itself
  chunks documents into sentences for citation purposes.
- Next: [embeddings and indexing](03-embeddings-and-indexing.md). Practise in [lab-11](../19-hands-on-labs/lab-11-rag-pipeline/README.md).

<!-- page-nav:start -->
---

[← Previous: RAG Fundamentals](01-rag-fundamentals.md) · [Module overview](README.md) · [Next: Embeddings and Indexing →](03-embeddings-and-indexing.md)
<!-- page-nav:end -->
