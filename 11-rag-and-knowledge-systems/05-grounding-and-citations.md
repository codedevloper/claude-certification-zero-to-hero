# Grounding and Citations

> **Level:** Intermediate · **Time:** ~30 min · **Exam relevance:** CCAR-P D3 (3.5), CCAR-P D5 (5.1, 5.5)

## In plain English

Grounding means the answer is built from sources you supplied, and a citation is the receipt that proves it. When a
colleague says "the hotel cap is 180 EUR", you trust it more if they add "travel policy, section 3". Citations let users,
reviewers and auditors check a claim in seconds instead of taking it on faith.

## Why it matters

- **Trust and verification.** Users can click through to the passage. Reviewers can spot-check answers quickly.
- **Hallucination control.** A claim with no supporting passage is a signal to investigate, and you can measure the rate
  of unsupported claims (see [RAG evaluation](06-rag-evaluation.md)).
- **Regulated work.** In finance, health and legal settings, being able to show which document version justified an
  answer is often a requirement, not a nicety.
- **Transparency.** Showing sources is part of addressing objective CCAR-P-5.5 (bias, fairness and transparency) as well
  as RAG design under CCAR-P-3.5 (see the [registry](../16-certification-tracks/registry.yaml)).

## How it works

You can ground answers in two ways: by **prompting** for quotes and source IDs, or by using the Claude API's built-in
**citations feature**. The built-in feature is usually the better choice for RAG.

### Prompted citations

Ask Claude to cite passage IDs in brackets, as in the [RAG fundamentals](01-rag-fundamentals.md) example. This works
with any output format, but the IDs are just text: you must validate that every cited ID exists and that the quoted
text appears in the passage.

### The citations feature (as of 2026-10-24)

Facts from the Claude [Citations documentation](https://platform.claude.com/docs/en/build-with-claude/citations),
checked 2026-10-24:

- **Turn it on per document.** Add `"citations": {"enabled": true}` to each `document` content block. Enable it on all
  documents in a request or none.
- **Document types:**

| Type | Source | How the API chunks it for citation | Citation location returned |
|---|---|---|---|
| Plain text | `{"type": "text", "media_type": "text/plain", "data": ...}` or a Files API `file_id` | Split into sentences | `char_location` (start and end character index) |
| PDF | base64, URL or `file_id` | Text extracted and split into sentences; images and scanned pages without text cannot be cited | `page_location` (start and end page number) |
| Custom content | `{"type": "content", "content": [text blocks...]}` | No further chunking: each block you provide is a citable unit | `content_block_location` (block indices) |

- **What comes back.** The response is split into several `text` blocks. Blocks that rely on sources carry a
  `citations` list. Each citation includes `cited_text`, the document index and title, and the location fields.
- **Token economics.** Enabling citations adds a small number of input tokens. The `cited_text` field does not count
  toward output tokens, and is not counted as input when you pass it back in later turns.
- **Reliability.** Because the API extracts `cited_text` from your documents, citations always point at real locations
  in the documents you provided.
- **Incompatible with structured outputs.** Enabling citations together with `output_config.format` returns a 400 error,
  because citations interleave with text. If you need JSON and sources, either use citations and post-process, or use
  structured outputs with a schema field for source IDs and validate those yourself.
- **Works with prompt caching, token counting and batches.** Put `cache_control` on large document blocks that you
  reuse; the citation blocks in responses are not cached, but the documents are.

### RAG chunks as citable units

The docs make a useful distinction for RAG:

- Put each retrieved chunk into its **own plain text document** if you want Claude to be able to cite individual
  sentences inside the chunk.
- Put retrieved chunks into a **custom content document** (one content block per chunk) if you want each chunk to be
  cited whole, or you have already chunked the text the way you want.

### Search result blocks

For RAG, the `search_result` content block lets Claude cite your retrieved content the way it cites web search results,
carrying the `source` and `title` you supply. Per the
[search results documentation](https://platform.claude.com/docs/en/build-with-claude/search-results) (checked
2026-10-24), it is part of the standard Messages API with no beta header, and you can provide it in two places:

1. **Returned from your own retrieval tool** inside a `tool_result`, which suits agentic search where Claude decides when
   to search.
2. **As top-level user content,** when you have already retrieved results.

Shape:

```json
{
  "type": "search_result",
  "source": "https://wiki.example.internal/travel-policy#hotels",
  "title": "Travel policy, section 3: Hotels",
  "content": [{"type": "text", "text": "Hotel nightly cap is 180 EUR in tier-1 cities..."}],
  "citations": {"enabled": true}
}
```

Citations then come back with type `search_result_location`, including `source`, `title`, `cited_text`, the
`search_result_index` and the block range within the result.

### Grounding beyond citations

Citations show where a claim came from; they do not prove the claim is a faithful reading. Strengthen grounding with:

- A system prompt that says to answer only from the provided sources and to state when they do not contain the answer.
- A relevance threshold on retrieval so that weak matches produce "not found" instead of a stretched answer.
- A post-check that every sentence of substance carries at least one citation (for high-stakes answers).
- Periodic human review of a sample of cited answers.

## Example

Grounded Q&A over retrieved chunks with the citations feature, then rendering footnotes.

> **Cost:** requires API credits (live mode).

```python
"""Answer with API citations over retrieved chunks, then render footnotes."""
import anthropic

client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY

retrieved = [
    {"title": "Travel policy §3 Hotels (v2026-07)",
     "text": "Hotel nightly cap is 180 EUR in tier-1 cities and 120 EUR elsewhere. "
             "Exceptions need written approval from a cost-centre owner."},
    {"title": "Travel policy §5 Expenses (v2026-07)",
     "text": "Receipts are required for any expense above 25 EUR. Claims must be filed within 30 days."},
]

documents = [
    {
        "type": "document",
        "source": {"type": "text", "media_type": "text/plain", "data": chunk["text"]},
        "title": chunk["title"],
        "citations": {"enabled": True},  # enable on every document, or on none
    }
    for chunk in retrieved
]

response = client.messages.create(
    model="claude-opus-5-5",
    max_tokens=1024,
    system=("Answer using only the provided documents. If they do not contain the answer, say so. "
            "Be concise."),
    messages=[{"role": "user", "content": [
        *documents,
        {"type": "text", "text": "Can I book a 200 EUR hotel in a tier-1 city, and what do I need?"},
    ]}],
)

if response.stop_reason not in ("end_turn", "max_tokens"):
    raise RuntimeError(f"Unexpected stop_reason: {response.stop_reason}")
if response.stop_reason == "max_tokens":
    print("[warning] answer truncated; raise max_tokens")

answer_parts, footnotes = [], []
for block in response.content:
    if block.type != "text":
        continue
    answer_parts.append(block.text)
    for c in block.citations or []:
        footnotes.append(f'{c.document_title}: "{c.cited_text.strip()}"')
        answer_parts.append(f"[{len(footnotes)}]")

print("".join(answer_parts))
for i, note in enumerate(footnotes, start=1):
    print(f"  [{i}] {note}")
```

Returning `search_result` blocks from a retrieval tool in an agentic loop looks like this (one `tool_result` whose
content is a list of search results):

```python
def search_tool_result(tool_use_id: str, hits: list[dict]) -> dict:
    return {
        "type": "tool_result",
        "tool_use_id": tool_use_id,
        "content": [
            {
                "type": "search_result",
                "source": hit["url"],
                "title": hit["title"],
                "content": [{"type": "text", "text": hit["text"]}],
                "citations": {"enabled": True},
            }
            for hit in hits
        ],
    }
```

## Enterprise use case

*Contoso Health* (fictional) built a policy assistant for clinic administrators. Compliance required that every answer
about patient-data handling show the policy, version and section.

- Retrieved chunks are passed as plain text documents titled `"<policy name> v<version> §<section>"`, with citations
  enabled.
- The UI renders each citation as a link to the exact section of that version in the document management system.
- A guard rejects any answer of more than one sentence that has no citations and replaces it with "I could not find this
  in current policy; contact the privacy office."
- Because the downstream case system needed JSON, the team kept citations for the user-facing answer and made a
  separate structured-outputs call for the case record, rather than trying to combine the two features in one request.

## Common mistakes

- **Combining citations with `output_config.format`,** which returns a 400.
- **Enabling citations on some documents and not others** in the same request.
- **Expecting citations from scanned PDFs** without extractable text, or from images inside PDFs.
- **Rendering citations without the document version,** so users click through to a newer version that says
  something different.
- **Treating a citation as proof of correctness.** It proves provenance, not faithful interpretation; still evaluate.
- **Discarding the citation data** when storing conversation history, making later audits impossible.

## Security considerations

- **Citations can surface restricted text.** `cited_text` is verbatim source text. Only send documents the user is
  allowed to see, so that citations cannot leak anything new.
- **Escape before rendering.** `cited_text` and titles come from documents; treat them as untrusted when rendering HTML.
  See [insecure output handling](../12-ai-security/06-insecure-output-handling.md).
- **Source URLs are data, not instructions.** Do not let a document-supplied URL trigger automatic fetches.
- **Retain audit evidence.** For regulated answers, log the question, the retrieved chunk IDs, index version and the
  citations returned, under your logging and retention policy.

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| 400 error mentioning citations and format | Citations used with structured outputs | Remove `output_config.format` or citations |
| No citations returned | Citations not enabled on documents, or question answered from general knowledge | Enable on all documents; instruct to answer only from sources |
| PDF answer has no page citations | Scanned PDF without text layer | OCR the PDF or supply extracted text |
| Citations too coarse | Custom content blocks are large | Use plain text documents (sentence-level) or smaller blocks |
| Citations too fine for bullet lists | Sentence splitting on lists | Use custom content with one block per bullet |

## Check your understanding

1. Which citation location type do you get for plain text, PDF and custom content documents?
2. Does `cited_text` count toward output tokens?
3. You need a JSON response with sources. Why can't you just enable citations and structured outputs together, and what
   can you do instead?
4. When would you put RAG chunks into custom content documents rather than plain text documents?
5. Name two places a `search_result` block can appear.

<details>
<summary>Answers</summary>

1. `char_location` for plain text, `page_location` for PDF, `content_block_location` for custom content.
2. No. It is provided for convenience and does not count toward output tokens.
3. The API rejects the combination with a 400 because citations interleave with text. Use citations and transform the
   result yourself, or use structured outputs with a source-ID field that you validate.
4. When you want each chunk to be cited as a whole unit, or you have already chunked text the way you want and do not
   want sentence splitting.
5. Inside a `tool_result` returned by your own retrieval tool, or directly as top-level user content.

</details>

## Further reading

- Claude docs, [Citations](https://platform.claude.com/docs/en/build-with-claude/citations).
- Claude docs, [Search results](https://platform.claude.com/docs/en/build-with-claude/search-results).
- In this repository: [vision, documents and citations](../06-claude-api/04-vision-documents-and-citations.md),
  [lab-04 document-grounded Q&A](../19-hands-on-labs/lab-04-document-grounded-qa/README.md).

<!-- page-nav:start -->
---

[← Previous: Retrieval Strategies](04-retrieval-strategies.md) · [Module overview](README.md) · [Next: RAG Evaluation →](06-rag-evaluation.md)
<!-- page-nav:end -->
