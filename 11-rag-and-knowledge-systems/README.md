# Module 11 — RAG and Knowledge Systems

> **Level:** Intermediate to Advanced · **Time:** ~5 hours including the lab · **Exam relevance:** CCAR-P D3 (primary), D4

Retrieval-augmented generation (RAG) is how you give Claude knowledge it was never trained on: your policies,
your product docs, your tickets, your contracts. This module takes you from "what is RAG" to designing,
evaluating and choosing between RAG, long context and agentic search for production systems.

## Learning objectives

By the end of this module you can:

1. Explain the two halves of a RAG pipeline (offline indexing and online retrieval plus generation) and where each one fails.
2. Choose a chunking strategy (fixed, recursive, semantic, structure-aware) and set overlap and metadata to suit the documents.
3. Select an embeddings provider and a vector store, and plan for index refresh, versioning and re-embedding. You can state
   what Anthropic's documentation says about embeddings, since Anthropic does not ship its own embeddings model.
4. Match a retrieval strategy (BM25, dense, hybrid, reranking, contextual retrieval, metadata filters, structured/SQL
   retrieval) to the shape of the data and the pattern of the queries.
5. Ground answers in sources using the Claude API citations feature and `search_result` content blocks, and know their limits.
6. Measure a RAG system with separate retrieval metrics and generation metrics, and diagnose which half is failing.
7. Decide between RAG, putting everything in a long context window, and agentic search, and justify the choice to stakeholders.

## Page order

| # | Page | What you learn |
|---|---|---|
| 1 | [RAG fundamentals](01-rag-fundamentals.md) | The pipeline, its vocabulary and its failure points |
| 2 | [Chunking strategies](02-chunking-strategies.md) | How to split documents so retrieval can find the right piece |
| 3 | [Embeddings and indexing](03-embeddings-and-indexing.md) | Embedding models, vector stores, refresh and versioning |
| 4 | [Retrieval strategies](04-retrieval-strategies.md) | Lexical, dense, hybrid, reranking, contextual retrieval, filters, SQL |
| 5 | [Grounding and citations](05-grounding-and-citations.md) | Making answers traceable with the citations feature |
| 6 | [RAG evaluation](06-rag-evaluation.md) | Retrieval metrics, generation metrics and an evaluation loop |
| 7 | [RAG vs long context vs agentic search](07-rag-vs-long-context.md) | Choosing the right knowledge architecture |

## Prerequisites

- [Module 04 — Context engineering](../04-context-engineering/README.md), especially [managing long context](../04-context-engineering/02-managing-long-context.md) and [prompt caching](../04-context-engineering/03-prompt-caching.md).
- [Module 06 — Claude API](../06-claude-api/README.md), especially [vision, documents and citations](../06-claude-api/04-vision-documents-and-citations.md).
- [Module 07 — Tool use](../07-tool-use-and-function-calling/README.md), because agentic search treats retrieval as a tool.
- Comfortable reading Python 3.10+.

## Exam relevance

This module underpins the following Claude Certified Architect – Professional (CCAR-P) objectives. Objective IDs and
wording come from [`registry.yaml`](../16-certification-tracks/registry.yaml).

| Objective | Summary | Pages |
|---|---|---|
| **CCAR-P-3.5** | Design RAG pipelines with suitable chunking and indexing | 01, 02, 03 |
| **CCAR-P-3.6** | Match retrieval strategy to data shape and query pattern | 04, 07 |
| CCAR-P-3.3 (secondary) | Evaluate accuracy–latency trade-offs and justify configuration | 04, 07 |
| CCAR-P-3.8 (secondary) | Evaluate progressive discovery versus monolithic context | 07 |
| CCAR-P-4.1 (secondary) | Define evaluation metrics | 06 |

The CCAR-P study guide for [Domain 3](../16-certification-tracks/ccar-p/study-guide/domain-3.md) links back here.

## Practise it

- Lab: [lab-11 — RAG pipeline](../19-hands-on-labs/lab-11-rag-pipeline/README.md) builds chunking, hybrid retrieval and cited answers that run offline in mock mode.
- Lab: [lab-04 — Document-grounded Q&A](../19-hands-on-labs/lab-04-document-grounded-qa/README.md) is the beginner warm-up for citations.
- Project: [Knowledge-base Q&A assistant](../20-real-world-projects/02-knowledge-base-qa-assistant/README.md) is the end-to-end version with tests.
- When something goes wrong: [RAG troubleshooting](../24-troubleshooting/rag.md).

## Next module

Continue to [Module 12 — AI security](../12-ai-security/README.md). Retrieved documents are untrusted input, and
[indirect prompt injection](../12-ai-security/03-indirect-prompt-injection.md) is the main security risk that RAG introduces.
