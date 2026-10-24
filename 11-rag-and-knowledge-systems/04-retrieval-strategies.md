# Retrieval Strategies

> **Level:** Advanced · **Time:** ~40 min · **Exam relevance:** CCAR-P D3 (3.6, 3.3, 3.5)

## In plain English

There is more than one way to find the right page. You can look for the exact words (keyword search), look for pages
that mean the same thing (semantic search), ask a librarian to sort a shortlist by relevance (reranking), only search
the shelf for this year and this department (filters), or skip the books entirely and query the spreadsheet where the
numbers live (structured retrieval). Good RAG systems pick, and usually combine, the methods that fit the data and the
questions people actually ask.

## Why it matters

Objective CCAR-P-3.6 asks you to "match retrieval strategy to data shape and query pattern" (see the
[registry](../16-certification-tracks/registry.yaml)). A strategy that works for narrative policy documents can fail
badly on part numbers, tabular data or questions that need aggregation. Retrieval choices also drive the
accuracy–latency–cost trade-off (CCAR-P-3.3): every extra stage adds milliseconds and money.

## How it works

### The strategies

| Strategy | How it scores | Strong at | Weak at |
|---|---|---|---|
| **Lexical (BM25)** | Term frequency and rarity of query words in each chunk | Exact terms, IDs, error codes, names, rare jargon | Synonyms and paraphrase ("car" vs "vehicle") |
| **Dense (embeddings)** | Vector similarity between query and chunk | Paraphrase, natural-language questions, cross-lingual | Exact identifiers, numbers, negation, very rare terms |
| **Hybrid** | Run both and fuse the ranked lists | Mixed query populations, which is most enterprise traffic | Slightly more infrastructure and latency |
| **Reranking** | A cross-encoder or LLM scores each (query, candidate) pair jointly | Precision in the final top K | Added latency and cost per candidate |
| **Contextual retrieval** | Prepend generated chunk context before embedding and BM25 indexing | Chunks that are ambiguous out of context | One-time indexing cost; must regenerate on change |
| **Metadata filters** | Hard constraints on fields (tenant, date, product, access label) | Scoping, freshness, security | Only as good as the metadata |
| **Structured / SQL retrieval** | Translate the question into a query over tables | Counts, sums, comparisons, exact lookups | Unstructured text; needs schema and safe query generation |
| **Query transformation** | Rewrite, expand or decompose the query before searching | Vague or compound questions | Extra model call; can drift from user intent |

### Hybrid fusion

The simplest robust way to combine lexical and dense results is **reciprocal rank fusion (RRF)**: each chunk scores
`sum(1 / (k + rank))` over the lists it appears in (with `k` around 60). It needs no score normalisation, because it
uses ranks, not raw scores. Weighted score blending is an alternative but needs calibration.

### Reranking

Retrieve broadly (for example 50–150 candidates) for recall, then rerank to a small top K for precision. Rerankers
see the query and the passage together, so they judge relevance better than vector similarity alone. Options include
dedicated reranker models (Anthropic's embeddings page lists Voyage AI rerankers) or using a fast Claude model to
score candidates, which is flexible but costlier per query.

### Contextual Retrieval

Anthropic's [Contextual Retrieval](https://www.anthropic.com/news/contextual-retrieval) article (September 2024)
addresses chunks that lose meaning when cut from their document. For each chunk, a Claude model is given the whole
document and the chunk and asked for a short context (typically 50–100 tokens) that situates the chunk. That context is
prepended before both embedding (**contextual embeddings**) and BM25 indexing (**contextual BM25**). Prompt caching
makes this affordable, because the full document is the cached prefix for every chunk in it.

Results the article reports on its test sets, measured as top-20 retrieval failure rate:

| Configuration | Reduction in retrieval failures |
|---|---|
| Contextual embeddings | 35% |
| Contextual embeddings + contextual BM25 | 49% |
| Contextual embeddings + contextual BM25 + reranking | 67% |

These are the article's numbers on its own datasets. Treat them as evidence that the technique is worth testing, not
as a guarantee for your corpus. The article also notes that if your whole knowledge base is under roughly 200,000
tokens, you may not need retrieval at all (see [RAG vs long context](07-rag-vs-long-context.md)).

### Metadata filters

Filters are hard constraints: a chunk that fails the filter is never a candidate. Use them for:

- **Security:** tenant ID, access labels, data classification, derived from the authenticated identity.
- **Scope:** product, region, language, document type.
- **Freshness:** `effective_date <= today`, `status = current`.

Derive filters from trusted context (the session, the user's directory groups), and optionally from the query itself
using structured outputs ("which product does this question mention?"). Never let the model widen a security filter.

### Structured retrieval

When the answer lives in rows and columns ("how many open claims in region West over 30 days?"), semantic search over
text chunks is the wrong tool. Options:

- **Text-to-SQL** with a read-only database role, an allow-listed set of views, row-level security, query timeouts and
  result-size limits. Validate the generated query before running it.
- **Predefined query tools** (for example `get_open_claims(region, min_age_days)`) exposed via
  [tool use](../07-tool-use-and-function-calling/README.md). Safer and more predictable than free SQL.
- **Hybrid answers:** SQL for the numbers, document retrieval for the policy that explains them.

### Matching strategy to data shape and query pattern

| Data shape | Typical query pattern | Recommended starting point |
|---|---|---|
| Narrative prose (policies, guides) | Natural-language "how do I…" | Dense or hybrid + reranking; structure-aware chunks |
| Technical docs with codes, part numbers, error IDs | Exact identifier lookups mixed with questions | Hybrid (BM25 is essential) + reranking |
| Short FAQ pairs | Paraphrased questions | Dense over question text; small chunks |
| Tables, ledgers, metrics | Aggregation, comparison, exact values | Structured / SQL retrieval or query tools |
| Multi-tenant SaaS content | Any, scoped to one customer | Mandatory tenant pre-filter + hybrid |
| Rapidly changing content (tickets, news) | "Latest", "current" | Date filters + recency boost + frequent refresh |
| Ambiguous chunks (contracts, financial filings) | Specific clauses or figures | Contextual retrieval + hybrid + reranking |
| Code repositories | Symbol names and behaviour | Hybrid, or agentic search with grep-style tools |
| Small, stable corpus (well under the context window) | Anything | Consider long context with caching instead of retrieval |

### Latency and cost budget

A typical production pipeline might spend tens of milliseconds on BM25 and ANN search, more on reranking (depending on
candidates and model), and most of its time in generation. Measure each stage. If you must cut latency, reduce
reranker candidates or move to a lighter reranker before you drop hybrid search, and cache frequent queries' retrieval
results where content permissions allow it.

## Example

Hybrid retrieval with BM25, a dense scorer and reciprocal rank fusion (standard library only, reusing the toy
embedder idea from [embeddings and indexing](03-embeddings-and-indexing.md)), followed by contextual chunk generation
with Claude using prompt caching on the document.

```python
"""Hybrid retrieval: BM25 + dense + reciprocal rank fusion."""
import math
import re
from collections import Counter

def tokens(text: str) -> list[str]:
    return re.findall(r"[a-z0-9\-]+", text.lower())

class BM25:
    def __init__(self, docs: dict[str, str], k1: float = 1.5, b: float = 0.75):
        self.docs = {i: tokens(t) for i, t in docs.items()}
        self.avgdl = sum(len(d) for d in self.docs.values()) / len(self.docs)
        self.df = Counter(term for d in self.docs.values() for term in set(d))
        self.k1, self.b, self.n = k1, b, len(self.docs)

    def rank(self, query: str) -> list[str]:
        scores = {}
        for doc_id, d in self.docs.items():
            tf = Counter(d)
            s = 0.0
            for term in tokens(query):
                if term not in tf:
                    continue
                idf = math.log(1 + (self.n - self.df[term] + 0.5) / (self.df[term] + 0.5))
                s += idf * tf[term] * (self.k1 + 1) / (tf[term] + self.k1 * (1 - self.b + self.b * len(d) / self.avgdl))
            if s > 0:
                scores[doc_id] = s
        return sorted(scores, key=scores.get, reverse=True)

def dense_rank(query: str, docs: dict[str, str]) -> list[str]:
    """Stand-in for vector search: cosine over character trigrams (captures fuzzy overlap)."""
    def grams(t: str) -> Counter:
        t = f"  {t.lower()}  "
        return Counter(t[i:i + 3] for i in range(len(t) - 2))
    q = grams(query)
    def cos(a: Counter, b: Counter) -> float:
        dot = sum(a[g] * b[g] for g in a)
        return dot / (math.sqrt(sum(v * v for v in a.values())) * math.sqrt(sum(v * v for v in b.values())) or 1)
    return sorted(docs, key=lambda i: cos(q, grams(docs[i])), reverse=True)

def rrf(rankings: list[list[str]], k: int = 60) -> list[str]:
    fused: Counter = Counter()
    for ranking in rankings:
        for rank, doc_id in enumerate(ranking, start=1):
            fused[doc_id] += 1 / (k + rank)
    return [d for d, _ in fused.most_common()]

DOCS = {
    "e-401": "Error E-401 on the handheld scanner means the battery firmware is out of date.",
    "bat-1": "Scanner batteries should be charged overnight and replaced every 18 months.",
    "net-7": "If the scanner cannot reach the warehouse network, re-pair it with the access point.",
}

if __name__ == "__main__":
    query = "scanner shows E-401"
    lexical, dense = BM25(DOCS).rank(query), dense_rank(query, DOCS)
    print("BM25 :", lexical)
    print("Dense:", dense)
    print("RRF  :", rrf([lexical, dense])[:2])
```

Generating contextual descriptions for chunks (indexing time). The document goes first with a cache breakpoint so every
chunk from the same document reuses the cached prefix.

> **Cost:** requires API credits (live mode).

```python
import anthropic

client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY

def contextualise(document: str, chunk: str) -> str:
    response = client.messages.create(
        model="claude-haiku-5-5",  # a fast, low-cost model suits bulk indexing work
        max_tokens=200,
        system="You write short retrieval context for document chunks.",
        messages=[{
            "role": "user",
            "content": [
                {"type": "text", "text": f"<document>\n{document}\n</document>",
                 "cache_control": {"type": "ephemeral"}},  # stable prefix, cached across chunks
                {"type": "text", "text": (
                    f"<chunk>\n{chunk}\n</chunk>\n"
                    "In one or two sentences, state what this chunk is about and where it sits in the document, "
                    "naming the entity, product or period it refers to. Reply with the context only."
                )},
            ],
        }],
    )
    if response.stop_reason != "end_turn":
        raise RuntimeError(f"stop_reason={response.stop_reason}")
    # Verify caching works: after the first chunk, cache_read_input_tokens should be > 0
    print("cache read tokens:", response.usage.cache_read_input_tokens)
    return "".join(b.text for b in response.content if b.type == "text").strip()

# Index text = contextualise(doc, chunk) + "\n\n" + chunk, for both embeddings and BM25.
```

The cached prefix must meet the model's minimum cacheable length; very short documents will not cache, which is fine
because they are cheap anyway. Batch processing can cut the cost of large backfills further when latency does not
matter (see [batch processing](../06-claude-api/05-batch-processing.md)).

## Enterprise use case

*Fabrikam Industrial* supports field technicians with a maintenance assistant. Query logs showed two populations:
40% of queries contained an error code or part number ("E-401", "PN-88213"), and 60% were descriptive ("scanner won't
connect after firmware update").

- Dense-only retrieval missed many code queries because rare identifiers were blurred in embedding space.
- BM25-only missed descriptive queries phrased differently from the manuals.
- **Decision:** hybrid with RRF, 100 candidates, reranked to the top 8, with a `product_line` pre-filter from the
  technician's work order. Parts inventory questions ("is PN-88213 in stock at depot 4?") were routed to a read-only
  inventory query tool instead of document search.
- Contextual retrieval was added for the service bulletins, where chunks such as "applies to units shipped after the
  revision" were meaningless without the bulletin title.

The architecture decision record captured the latency cost of reranking (measured, and within the 2-second SLA) and
the rejected alternative of a larger embedding model (higher cost, no improvement on code queries).

## Common mistakes

- **Dense-only retrieval for identifier-heavy corpora.** Add BM25.
- **Reranking too few candidates.** A reranker cannot promote a chunk that was never retrieved.
- **Using vector search for aggregation questions.** "How many…" needs structured retrieval.
- **Model-generated SQL with write permissions** or without validation, row-level security and limits.
- **Treating published benchmark gains as guaranteed.** Validate every stage on your own evaluation set.
- **Filters derived from the prompt for security scope.** Derive them from authenticated identity.

## Security considerations

- **Text-to-SQL is code execution.** Use read-only roles, allow-listed views, parameterisation where possible, query
  timeouts and row limits. Treat the generated query as untrusted. See [insecure output handling](../12-ai-security/06-insecure-output-handling.md).
- **Query rewriting can be manipulated.** A user prompt might try to rewrite the query to remove filters. Keep security
  filters outside the model's control.
- **Contextualisation sends whole documents to the model.** Confirm that the data classification allows it and that
  the indexing job runs under appropriate data-handling terms.
- **Reranker and embeddings providers see every query.** Include them in your data-flow diagram and vendor review.

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| Codes and IDs not found | Dense-only retrieval | Add BM25, hybrid fusion |
| Right chunk in candidates but not in final K | Weak or no reranking | Add a reranker; tune K |
| Good recall, slow responses | Too many reranker candidates | Reduce candidates; lighter reranker |
| Wrong numbers on aggregate questions | Using document retrieval for tabular data | Route to SQL or query tools |
| Ambiguous chunks retrieved for many queries | Missing context | Header prepending or contextual retrieval |
| No results for some users | Filters too strict, or post-filtering | Pre-filter; inspect metadata coverage |

## Check your understanding

1. Your corpus is maintenance manuals full of error codes and part numbers. Which retrieval strategy do you start with,
   and why?
2. What does reciprocal rank fusion combine, and why does it avoid score normalisation?
3. In Contextual Retrieval, where is the generated context used, and what makes it affordable?
4. A user asks, "What was the average approval time per region last quarter?" Which strategy fits?
5. Why should security filters not be derived from the model's interpretation of the query?

<details>
<summary>Answers</summary>

1. Hybrid (BM25 plus dense) with reranking. BM25 handles exact identifiers, dense handles descriptive questions.
2. It combines ranked lists from different retrievers using ranks only (1 / (k + rank)), so incomparable raw scores do not
   need calibrating.
3. It is prepended to each chunk before embedding and before BM25 indexing. Prompt caching of the full document across
   that document's chunks makes it affordable.
4. Structured retrieval: a SQL query or a predefined query tool over the approvals data, possibly plus document retrieval
   for definitions.
5. The model can be manipulated by user or document content; security scope must come from authenticated identity and be
   enforced by the retrieval service.

</details>

## Further reading

- Anthropic, [Contextual Retrieval](https://www.anthropic.com/news/contextual-retrieval).
- Claude docs, [Prompt caching](https://platform.claude.com/docs/en/build-with-claude/prompt-caching).
- Claude docs, [Embeddings](https://platform.claude.com/docs/en/build-with-claude/embeddings) (rerankers section).
- Next: [grounding and citations](05-grounding-and-citations.md). Practise hybrid retrieval in
  [lab-11](../19-hands-on-labs/lab-11-rag-pipeline/README.md).
