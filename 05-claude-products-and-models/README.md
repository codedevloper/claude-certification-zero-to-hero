# Module 05: Claude Products and Models

> **Level:** Beginner to Intermediate · **Time:** ~5 hours including exercises · **Exam relevance:** CCAO-F D2 (2.6), D3, D5 · CCAR-P D2 (2.1), D3 (3.3, 3.7), D7 (7.1)

Claude is not one product. It is a family of models offered through apps, a developer platform, a coding tool and several cloud platforms, with features such as Projects, Artifacts, research, connectors and Skills layered on top. This module maps that ecosystem, explains the model families and how to choose between them, and teaches the configuration skills that business users need most: setting up Projects with good instructions and knowledge, choosing output formats, and connecting Claude safely to other tools.

This module underpins **CCAO-F Domain 3 (Product and Model Selection)** and **Domain 5 (Configuration and Knowledge Management)**. It is also the starting point for CCAR-P model-selection and integration decisions.

> Product features, plan entitlements, model line-ups and prices change frequently. Facts in this module are dated "as of 2026-10-24" and link to the official pages. Check those pages before relying on a detail.

## Learning objectives

After completing this module you will be able to:

1. Describe the Claude product ecosystem: the apps on web, desktop and mobile, the plans, Claude Code, the Claude API and Console, and Claude on Amazon Bedrock, Google Cloud Vertex AI and Microsoft Foundry.
2. Choose the right app feature for a task: a plain chat, a Project, research, an Artifact, a connector or a Skill (CCAO-F 3.1).
3. Explain the current Claude model families (Haiku, Sonnet, Opus, and the frontier Fable line), their trade-offs, and where to find current IDs, context windows and prices (CCAO-F 3.2, CCAR-P 2.1).
4. Match a model to a task's cost, speed and quality requirements, and justify the choice (CCAO-F 3.3, CCAR-P 3.3).
5. Decide when to restart a conversation, summarise it, or persist information in a Project or memory (CCAO-F 3.4).
6. Configure a Project with effective instructions and well-organised knowledge, and keep it up to date (CCAO-F 5.1, 5.3, 5.4).
7. Choose between inline answers, Artifacts and structured data for an output (CCAO-F 2.6).
8. Manage connectors such as Google Drive and Gmail with appropriate permissions (CCAO-F 5.2).

## Page order

| # | Page | What you learn | Time |
|---|---|---|---|
| 1 | [The Claude product ecosystem](01-product-ecosystem.md) | Every surface and feature, and which to use when | 45 min |
| 2 | [Model families](02-model-families.md) | Haiku, Sonnet, Opus and Fable; current models with dates and prices | 35 min |
| 3 | [Model selection](03-model-selection.md) | Cost, speed and quality trade-offs and how to test them | 40 min |
| 4 | [Projects and knowledge management](04-projects-and-knowledge.md) | Instructions, knowledge, memory, and restart/summarise/persist | 50 min |
| 5 | [Artifacts and output formats](05-artifacts-and-output-formats.md) | Inline, Artifact or structured data | 35 min |
| 6 | [Connectors and integrations](06-connectors-and-integrations.md) | Google Workspace, directory and custom connectors, permissions | 40 min |

## Prerequisites

- [Module 01: AI and LLM fundamentals](../01-ai-and-llm-fundamentals/README.md), especially [Tokens](../01-ai-and-llm-fundamentals/04-tokens-and-tokenisation.md) and [Context windows](../01-ai-and-llm-fundamentals/05-context-windows.md).
- [Module 02: Claude fundamentals](../02-claude-fundamentals/README.md).
- [Module 03: Prompt engineering](../03-prompt-engineering/README.md) is recommended, particularly [System prompts and roles](../03-prompt-engineering/07-system-prompts-and-roles.md), before page 4.
- A Claude account. Several features (research, chat search, larger Project knowledge) need a paid plan; the pages say which.

## Exam relevance

Exam facts (item counts, timing and domain weights) are recorded in [`registry.yaml`](../16-certification-tracks/registry.yaml).

| Page | CCAO-F objectives | CCAR-P objectives |
|---|---|---|
| 01 Product ecosystem | CCAO-F-3.1, CCAO-F-4.4 | CCAR-P-3.7, CCAR-P-7.1 |
| 02 Model families | CCAO-F-3.2 | CCAR-P-2.1 |
| 03 Model selection | CCAO-F-3.2, CCAO-F-3.3 | CCAR-P-2.1, CCAR-P-3.3, CCAR-P-4.5 |
| 04 Projects and knowledge | CCAO-F-3.4, CCAO-F-5.1, CCAO-F-5.3, CCAO-F-5.4 | CCAR-P-2.2, CCAR-P-2.4 |
| 05 Artifacts and output formats | CCAO-F-2.5, CCAO-F-2.6, CCAO-F-3.1 | — |
| 06 Connectors and integrations | CCAO-F-5.2, CCAO-F-6.2 | CCAR-P-3.2, CCAR-P-3.7 |

Study-guide cross-references: [CCAO-F Domain 3](../16-certification-tracks/ccao-f/study-guide/domain-3.md), [CCAO-F Domain 5](../16-certification-tracks/ccao-f/study-guide/domain-5.md), [CCAR-P Domain 2](../16-certification-tracks/ccar-p/study-guide/domain-2.md).

## Practice

- [Lab 05: Context management](../19-hands-on-labs/lab-05-context-management/README.md): restart, summarise and persist in code.
- [Lab 06: Model comparison](../19-hands-on-labs/lab-06-model-comparison/README.md): compare models on the same task for quality, speed and cost.
- [Lab 03: Structured outputs](../19-hands-on-labs/lab-03-structured-outputs/README.md): produce machine-readable output.
- [Lab 04: Document-grounded Q&A](../19-hands-on-labs/lab-04-document-grounded-qa/README.md): the API equivalent of Project knowledge.
- Quick reference: [Model selection cheat sheet](../22-cheat-sheets/model-selection.md).

## Next module

Business users on the CCAO-F track should now work through the [CCAO-F track overview](../16-certification-tracks/ccao-f/README.md) and the remaining sections of [Module 04: Context engineering](../04-context-engineering/README.md) that their roadmap lists. Technical learners continue to [Module 06: The Claude API](../06-claude-api/README.md).
