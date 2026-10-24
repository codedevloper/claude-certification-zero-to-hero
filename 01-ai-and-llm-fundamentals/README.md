# Module 01: AI and LLM Fundamentals

> **Level:** Beginner · **Time:** ~4 hours including exercises · **Exam relevance:** CCAO-F D2, D3, D6 · CCAR-P D2, D5

This module assumes you have never used an AI model. By the end you will understand what is actually happening when you type a question into a chat box and a large language model writes back, and why it sometimes gets things confidently wrong. Every later module builds on the vocabulary introduced here: *model*, *training*, *token*, *context window*, *hallucination*.

You do not need to write code for this module. A few pages show small Python snippets, but they are optional.

## Learning objectives

After completing this module you will be able to:

1. Explain in plain language what artificial intelligence (AI), machine learning and deep learning are, and how they relate to each other.
2. Describe what makes *generative* AI different from AI that classifies or predicts.
3. Explain how a large language model (LLM) produces text by predicting one token at a time, and what pre-training and fine-tuning contribute.
4. Define a token, estimate token counts for ordinary text, and explain why tokens matter for cost, speed and limits.
5. Explain what a context window is, what counts towards it, and what happens when a conversation grows too long.
6. Define hallucination, give three common causes, and apply at least four techniques to reduce or catch it.
7. Give a balanced account of what LLMs do well and badly, so you can decide when to use one and when not to.

## Page order

| # | Page | What you learn | Time |
|---|---|---|---|
| 1 | [What is AI?](01-what-is-ai.md) | AI, machine learning, deep learning, and where LLMs fit | 25 min |
| 2 | [Generative AI](02-generative-ai.md) | Models that create new content rather than label existing content | 25 min |
| 3 | [Large language models](03-large-language-models.md) | Next-token prediction, transformers, pre-training and fine-tuning | 35 min |
| 4 | [Tokens and tokenisation](04-tokens-and-tokenisation.md) | The units models read and write, and why they drive cost | 30 min |
| 5 | [Context windows](05-context-windows.md) | The model's working memory and how to stay within it | 30 min |
| 6 | [Hallucinations](06-hallucinations.md) | Why models invent facts and how to catch it | 35 min |
| 7 | [Capabilities and limitations](07-capabilities-and-limitations.md) | A realistic picture of strengths and weaknesses | 30 min |

Read the pages in order. Each ends with a short "Check your understanding" quiz; if you miss more than one answer, reread the "How it works" section before moving on.

## Prerequisites

- None. If you can use a web browser and read English, you are ready.
- Optional: complete [Environment setup](../00-getting-started/environment-setup.md) if you want to run the small Python examples.

## How this module connects to the exams

Both supported certifications assume you understand these fundamentals, even though no exam domain is named "AI basics". The exam facts themselves (item counts, timing, weights) are recorded in [`registry.yaml`](../16-certification-tracks/registry.yaml).

| Page | CCAO-F objectives | CCAR-P objectives |
|---|---|---|
| 03 Large language models | CCAO-F-3.2 | CCAR-P-2.1 |
| 04 Tokens | CCAO-F-3.3, CCAO-F-3.4 | CCAR-P-2.4, CCAR-P-4.5 |
| 05 Context windows | CCAO-F-3.4 | CCAR-P-2.4, CCAR-P-3.8 |
| 06 Hallucinations | CCAO-F-2.1, CCAO-F-2.2, CCAO-F-2.3, CCAO-F-2.4 | CCAR-P-4.4, CCAR-P-5.2 |
| 07 Capabilities and limitations | CCAO-F-4.5, CCAO-F-6.1 | CCAR-P-5.2, CCAR-P-6.2 |

CCAO-F (Claude Certified Associate – Foundations) is for business and knowledge workers. CCAR-P (Claude Certified Architect – Professional) is for solution architects and senior engineers. See [Choose your path](../00-getting-started/choose-your-path.md) if you are unsure which applies to you.

## Practice

- [Lab 01: First Claude interaction](../19-hands-on-labs/lab-01-first-claude-interaction/README.md) lets you send a first message (offline in mock mode, so no account is needed).
- [Lab 04: Document-grounded Q&A](../19-hands-on-labs/lab-04-document-grounded-qa/README.md) shows one of the main defences against hallucination.
- [Lab 05: Context management](../19-hands-on-labs/lab-05-context-management/README.md) makes context windows tangible.
- The [fundamentals flashcard deck](../23-flashcards/decks/fundamentals.yaml) covers the vocabulary in this module.

## Next module

Continue to [Module 02: Claude Fundamentals](../02-claude-fundamentals/README.md), where you apply these ideas to Claude specifically and have your first conversation.
