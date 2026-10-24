# Module 02: Claude Fundamentals

> **Level:** Beginner · **Time:** ~4 hours including exercises · **Exam relevance:** CCAO-F D1, D5, D6 · CCAR-P D2, D5

Module 01 explained language models in general. This module is about Claude specifically: how Anthropic trains it, what happens when you send it a message, how to hold a productive first conversation, the basics of a good prompt, and how Anthropic and you share responsibility for using it safely.

If you have never used Claude before, this is where you start doing rather than reading.

## Learning objectives

After completing this module you will be able to:

1. Explain at a conceptual level how Claude is trained, including pre-training, reinforcement learning from human feedback (RLHF) and Constitutional AI.
2. Explain why Claude conversations are stateless, and how the system, user and assistant roles fit together.
3. Start a conversation in a Claude app, attach a file, iterate on a response and know when to start a new chat.
4. Write a prompt that states the task, context, audience, format and constraints, and improve it based on the result.
5. Describe Anthropic's safety approach: the Usage Policy, the Responsible Scaling Policy and Claude's constitution.
6. Apply responsible-use practices: data sensitivity, verification, disclosure and following organisational AI policy.

## Page order

| # | Page | What you learn | Time |
|---|---|---|---|
| 1 | [How Claude works](01-how-claude-works.md) | Training, statelessness and conversation roles | 40 min |
| 2 | [Your first conversation](02-first-conversation.md) | A guided walk-through in the Claude app | 40 min |
| 3 | [Prompt fundamentals](03-prompt-fundamentals.md) | The building blocks of a clear request | 40 min |
| 4 | [Anthropic's safety approach](04-anthropic-safety-approach.md) | Usage Policy, Responsible Scaling Policy, constitution | 35 min |
| 5 | [Responsible use](05-responsible-use.md) | Your responsibilities as a user or builder | 35 min |

## Prerequisites

- [Module 01: AI and LLM fundamentals](../01-ai-and-llm-fundamentals/README.md), or equivalent familiarity with tokens, context windows and hallucinations.
- A Claude account for the hands-on parts (a free account is enough). If you cannot create one, you can still follow along and run the labs offline in mock mode; see [Environment setup](../00-getting-started/environment-setup.md).

## Exam relevance

Exam facts (item counts, timing, weights) are recorded in [`registry.yaml`](../16-certification-tracks/registry.yaml).

| Page | CCAO-F objectives | CCAR-P objectives |
|---|---|---|
| 01 How Claude works | CCAO-F-3.4, CCAO-F-5.3 | CCAR-P-2.2 |
| 02 First conversation | CCAO-F-1.3, CCAO-F-3.1, CCAO-F-3.4 | — |
| 03 Prompt fundamentals | CCAO-F-1.1, CCAO-F-1.2, CCAO-F-1.3, CCAO-F-1.4 | CCAR-P-2.2, CCAR-P-2.3 |
| 04 Anthropic's safety approach | CCAO-F-6.1, CCAO-F-6.4 | CCAR-P-5.1, CCAR-P-5.5 |
| 05 Responsible use | CCAO-F-6.1, CCAO-F-6.2, CCAO-F-6.3, CCAO-F-6.4, CCAO-F-2.4 | CCAR-P-5.3, CCAR-P-5.4 |

## Practice

- [Lab 01: First Claude interaction](../19-hands-on-labs/lab-01-first-claude-interaction/README.md): send a message with system and user roles (mock mode by default).
- [Lab 02: Prompt improvement](../19-hands-on-labs/lab-02-prompt-improvement/README.md): improve a weak prompt step by step.
- [Lab 15: Sensitive data protection](../19-hands-on-labs/lab-15-sensitive-data-protection/README.md): an advanced lab on keeping sensitive data out of prompts; skim the README now and return later.

## Next module

Business users heading for CCAO-F can continue to [Module 03: Prompt engineering](../03-prompt-engineering/README.md) and then [Module 05: Claude products and models](../05-claude-products-and-models/README.md). Everyone should complete Module 03 before Module 05.
