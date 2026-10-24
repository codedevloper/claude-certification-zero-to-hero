# Glossary

Plain-English definitions of the terms used in this repository, in alphabetical order, each linked to the page that
explains it in depth. Product and API terms reflect Claude as of 2026-10-24; check the official docs for changes.

[A](#a) · [B](#b) · [C](#c) · [D](#d) · [E](#e) · [F](#f) · [G](#g) · [H](#h) · [I](#i) · [J](#j) · [K](#k) ·
[L](#l) · [M](#m) · [N](#n) · [O](#o) · [P](#p) · [Q](#q) · [R](#r) · [S](#s) · [T](#t) · [U](#u) · [V](#v) ·
[W](#w) · [Z](#z)

## A

- **Acceptable-use policy (AI)**: An organisation's rules for which AI tools staff may use, with which data and under what review. See [12 · AI governance](12-ai-security/12-ai-governance.md).
- **acceptEdits mode**: A Claude Code permission mode that automatically accepts file edits in the working directory. See [09 · Permissions and settings](09-claude-code/04-permissions-and-settings.md).
- **Adaptive thinking**: `thinking={"type": "adaptive"}`; Claude decides when and how much to reason before answering. See [03 · Reasoning and thinking](03-prompt-engineering/04-reasoning-and-thinking.md).
- **Agent**: A system in which the model chooses its next step and tools in a loop until a goal is met. See [10 · Workflows vs agents](10-agentic-ai/01-workflows-vs-agents.md).
- **Agent loop**: The repeating cycle of model call, tool execution and result return that drives an agent. See [10 · The agent loop](10-agentic-ai/03-the-agent-loop.md).
- **Agent SDK (Claude Agent SDK)**: Claude Code's harness packaged as a library, with built-in file, shell and web tools, for building your own agents. See [09 · Headless, CI and the Agent SDK](09-claude-code/09-headless-ci-and-agent-sdk.md).
- **Agent Skills**: Folders with a `SKILL.md` file and optional scripts that give Claude packaged know-how, loaded on demand. See [04 · Progressive disclosure and Skills](04-context-engineering/06-progressive-disclosure-and-skills.md).
- **Architecture decision record (ADR)**: A short document recording a design decision, the options and the reasoning. See [13 · Architecture decision records](13-enterprise-ai-architecture/07-architecture-decision-records.md).
- **Artifact**: Standalone content (document, code, diagram, small app) shown in its own panel in the Claude apps. See [05 · Artifacts and output formats](05-claude-products-and-models/05-artifacts-and-output-formats.md).
- **Assistant prefill**: Ending a request with a partial assistant message to steer output; not supported on current Claude models. See [03 · Structured output](03-prompt-engineering/06-structured-output.md).
- **Audit log**: A tamper-evident record of prompts, tool calls, approvals and outcomes used for investigation and compliance. See [12 · Logging and auditability](12-ai-security/11-logging-and-auditability.md).
- **Auto mode**: A Claude Code permission mode in which a classifier reviews actions instead of prompting the user. See [09 · Permissions and settings](09-claude-code/04-permissions-and-settings.md).

## B

- **Batch processing (Message Batches)**: Asynchronous processing of many requests at 50% of standard prices, completing within 24 hours. See [06 · Batch processing](06-claude-api/05-batch-processing.md).
- **Bias (model)**: Systematic unfairness in outputs across groups or perspectives. See [14 · Safety and red-team evals](14-evaluation-and-testing/07-safety-and-red-team-evals.md).
- **BM25**: A classic keyword-ranking algorithm often combined with vector search in hybrid retrieval. See [11 · Retrieval strategies](11-rag-and-knowledge-systems/04-retrieval-strategies.md).
- **bypassPermissions mode**: A Claude Code mode that skips permission prompts; only for isolated, disposable environments. See [09 · Permissions and settings](09-claude-code/04-permissions-and-settings.md).

## C

- **Cache breakpoint**: A `cache_control` marker that ends a cacheable prefix; up to four per request. See [04 · Prompt caching](04-context-engineering/03-prompt-caching.md).
- **Capability bloat**: Giving an agent more tools or broader tools than it needs, which hurts accuracy and security. See [07 · Tool design best practices](07-tool-use-and-function-calling/05-tool-design-best-practices.md).
- **Chain-of-thought**: Having a model reason step by step before answering; on current Claude models usually achieved with adaptive thinking. See [03 · Reasoning and thinking](03-prompt-engineering/04-reasoning-and-thinking.md).
- **Chunking**: Splitting documents into retrievable pieces for RAG. See [11 · Chunking strategies](11-rag-and-knowledge-systems/02-chunking-strategies.md).
- **Citations**: A feature that links answer text to exact passages in supplied documents. See [06 · Vision, documents and citations](06-claude-api/04-vision-documents-and-citations.md).
- **Claude apps**: Claude on the web, desktop and mobile for chat, Projects, artifacts and research. See [05 · Product ecosystem](05-claude-products-and-models/01-product-ecosystem.md).
- **Claude Code**: Anthropic's agentic coding tool for the terminal, IDEs, desktop and web. See [09 · What is Claude Code](09-claude-code/01-what-is-claude-code.md).
- **Claude Partner Network**: Anthropic's partner programme; organisations in it are currently eligible for the Claude certification exams. See [16 · Certification tracks](16-certification-tracks/README.md).
- **CLAUDE.md**: A Markdown file of persistent project or user instructions that Claude Code loads into context. See [09 · CLAUDE.md and memory](09-claude-code/03-claude-md-and-memory.md).
- **Cloud platforms**: Access to Claude through Amazon Bedrock, Google Vertex AI or Microsoft Foundry, with platform-specific auth and feature availability. See [06 · Cloud platforms](06-claude-api/07-cloud-platforms.md).
- **Compaction**: Summarising earlier conversation to free context space, manually or server-side. See [04 · Compaction and context editing](04-context-engineering/05-compaction-and-context-editing.md).
- **Confused deputy**: A component with broad privileges tricked into acting for a party that lacks them. See [12 · Agent identity and permissions](12-ai-security/09-agent-identity-and-permissions.md).
- **Connector**: An integration that lets Claude read from or act in another service, often via MCP. See [05 · Connectors and integrations](05-claude-products-and-models/06-connectors-and-integrations.md).
- **Constitutional AI**: Anthropic's training approach using written principles to guide self-critique and revision. See [02 · Anthropic's safety approach](02-claude-fundamentals/04-anthropic-safety-approach.md).
- **Context editing**: Clearing specific old content, such as stale tool results, from the conversation. See [04 · Compaction and context editing](04-context-engineering/05-compaction-and-context-editing.md).
- **Context engineering**: Deciding what information occupies the context window at each step. See [04 · What is context engineering](04-context-engineering/01-what-is-context-engineering.md).
- **Context window**: The maximum tokens a model considers in one request, input and output together. See [01 · Context windows](01-ai-and-llm-fundamentals/05-context-windows.md).
- **Cost per completed task**: Total spend to finish a unit of work, including retries and extra turns; the right basis for comparing models. See [15 · Cost optimisation](15-production-operations/03-cost-optimisation.md).
- **count_tokens**: The API endpoint that counts input tokens before sending a request. See [06 · Token counting and cost](06-claude-api/08-token-counting-and-cost.md).
- **custom_id**: The identifier you attach to each batch request; results must be matched by it. See [06 · Batch processing](06-claude-api/05-batch-processing.md).

## D

- **Data exfiltration**: Unauthorised transfer of data out of a system, for example via injected instructions and an outbound channel. See [12 · Data exfiltration and disclosure](12-ai-security/04-data-exfiltration-and-disclosure.md).
- **Data minimisation**: Sending only the data a task needs into prompts and tools. See [13 · Data governance and compliance](13-enterprise-ai-architecture/05-data-governance-and-compliance.md).
- **Data poisoning**: Corrupting training or knowledge-base content to manipulate outputs. See [12 · Supply chain risks](12-ai-security/07-supply-chain-risks.md).
- **Data residency**: Requirements on where data is stored or processed geographically. See [13 · Data governance and compliance](13-enterprise-ai-architecture/05-data-governance-and-compliance.md).
- **Decomposition**: Breaking a complex task into smaller, separately solvable steps. See [03 · Task decomposition and chaining](03-prompt-engineering/05-task-decomposition-and-chaining.md).
- **Deny rule**: A Claude Code permission rule that blocks a tool or pattern; evaluated before ask and allow rules. See [09 · Permissions and settings](09-claude-code/04-permissions-and-settings.md).
- **Direct prompt injection**: Malicious instructions typed by the user to override intended behaviour. See [12 · Prompt injection](12-ai-security/02-prompt-injection.md).

## E

- **Effort**: The `output_config.effort` setting (`low` to `max`) that tunes how thorough Claude is and how many tokens it spends. See [03 · Reasoning and thinking](03-prompt-engineering/04-reasoning-and-thinking.md).
- **Elicitation**: An MCP client feature letting a server ask the user for more information. See [08 · Architecture](08-model-context-protocol/02-architecture.md).
- **Embedding**: A numeric vector representing meaning, used for semantic search. See [11 · Embeddings and indexing](11-rag-and-knowledge-systems/03-embeddings-and-indexing.md).
- **Evaluation (eval)**: A repeatable test of model or system behaviour against defined criteria and data. See [14 · Why evaluate](14-evaluation-and-testing/01-why-evaluate.md).
- **Evaluation dataset**: The curated inputs, expected outputs and edge cases an eval runs on. See [14 · Building eval datasets](14-evaluation-and-testing/03-building-eval-datasets.md).
- **Evaluator–optimiser**: A workflow where one call generates and another critiques until criteria are met. See [10 · Workflow patterns](10-agentic-ai/02-workflow-patterns.md).
- **Excessive agency**: More tools, permissions or autonomy than a task needs (OWASP LLM06). See [12 · Tool misuse and excessive agency](12-ai-security/05-tool-misuse-and-excessive-agency.md).

## F

- **Fallback (refusal fallback)**: An API option that retries a refused request on a designated model on supported models and platforms. See [06 · Messages API](06-claude-api/02-messages-api.md).
- **Few-shot prompting**: Including a few examples of desired input and output in the prompt. See [03 · Examples and few-shot](03-prompt-engineering/03-examples-few-shot.md).
- **Files API**: Upload a file once and reference it by `file_id` in later requests. See [06 · Vision, documents and citations](06-claude-api/04-vision-documents-and-citations.md).
- **Fine-tuning**: Further training a model on task data; most Claude solutions use prompting, retrieval and tools instead. See [01 · Large language models](01-ai-and-llm-fundamentals/03-large-language-models.md).

## G

- **Generative AI**: AI that produces new content such as text, code or images. See [01 · Generative AI](01-ai-and-llm-fundamentals/02-generative-ai.md).
- **Grounding**: Tying answers to supplied, verifiable sources. See [11 · Grounding and citations](11-rag-and-knowledge-systems/05-grounding-and-citations.md).
- **Guardrails**: Controls inside and around a model that constrain inputs, outputs and actions. See [12 · Enterprise deployment controls](12-ai-security/14-enterprise-deployment-controls.md).

## H

- **Hallucination**: Confident output that is false or unsupported by sources. See [01 · Hallucinations](01-ai-and-llm-fundamentals/06-hallucinations.md).
- **Harness**: The loop and context management around a model that turns it into an agent. See [10 · Managed agents and the Agent SDK](10-agentic-ai/06-managed-agents-and-agent-sdk.md).
- **Headless mode**: Running Claude Code non-interactively with `claude -p`, for scripts and CI. See [09 · Headless, CI and the Agent SDK](09-claude-code/09-headless-ci-and-agent-sdk.md).
- **Hook**: A command or handler Claude Code runs at a lifecycle event such as `PreToolUse`. See [09 · Hooks](09-claude-code/06-hooks.md).
- **Host (MCP)**: The AI application that connects to MCP servers through clients. See [08 · Architecture](08-model-context-protocol/02-architecture.md).
- **Human-in-the-loop (HITL)**: A design where people review or approve model outputs or actions at defined points. See [10 · Human in the loop](10-agentic-ai/05-human-in-the-loop.md).
- **Hybrid search**: Combining keyword and vector retrieval. See [11 · Retrieval strategies](11-rag-and-knowledge-systems/04-retrieval-strategies.md).

## I

- **Idempotency**: Designing an operation so repeating it has no extra effect; essential when retrying tool calls. See [15 · Reliability engineering](15-production-operations/05-reliability-engineering.md).
- **Incident response**: The process for containing, investigating and recovering from failures or attacks. See [15 · Incident response](15-production-operations/07-incident-response.md).
- **Indirect prompt injection**: Instructions hidden in content the model processes, such as documents, web pages or tool results. See [12 · Indirect prompt injection](12-ai-security/03-indirect-prompt-injection.md).
- **Insecure (improper) output handling**: Passing model output unvalidated into HTML, SQL, shells or APIs (OWASP LLM05). See [12 · Insecure output handling](12-ai-security/06-insecure-output-handling.md).

## J

- **JSON Schema**: A standard for describing JSON structure, used in tool definitions and structured outputs. See [07 · Defining tools](07-tool-use-and-function-calling/02-defining-tools.md).
- **JSON-RPC 2.0**: The message format MCP uses for requests, responses and notifications. See [08 · Architecture](08-model-context-protocol/02-architecture.md).

## K

- **Knowledge base**: The curated content a RAG system or Project draws on. See [05 · Projects and knowledge](05-claude-products-and-models/04-projects-and-knowledge.md).

## L

- **Large language model (LLM)**: A neural network trained on large text corpora to predict tokens and generate language. See [01 · Large language models](01-ai-and-llm-fundamentals/03-large-language-models.md).
- **Latency**: Time to respond; often measured as time to first token and total time. See [15 · Latency optimisation](15-production-operations/04-latency-optimisation.md).
- **Least privilege**: Granting only the permissions a component needs. See [12 · Agent identity and permissions](12-ai-security/09-agent-identity-and-permissions.md).
- **LLM-as-judge**: Using a model with a rubric to grade outputs. See [14 · Grading methods](14-evaluation-and-testing/04-grading-methods.md).
- **Long context**: Placing large documents directly in the context window rather than retrieving fragments. See [11 · RAG vs long context](11-rag-and-knowledge-systems/07-rag-vs-long-context.md).

## M

- **Managed Agents**: An Anthropic-hosted agent surface that runs the loop and a per-session sandbox for you. See [10 · Managed agents and the Agent SDK](10-agentic-ai/06-managed-agents-and-agent-sdk.md).
- **Managed settings**: Organisation-enforced Claude Code settings with the highest precedence. See [09 · Team rollout](09-claude-code/08-team-rollout.md).
- **max_tokens**: The required cap on output tokens per response; hitting it truncates output. See [06 · Messages API](06-claude-api/02-messages-api.md).
- **MCP (Model Context Protocol)**: An open protocol for connecting AI applications to external tools and data. See [08 · What is MCP](08-model-context-protocol/01-what-is-mcp.md).
- **MCP server**: A program exposing tools, resources and prompts over MCP. See [08 · Building an MCP server](08-model-context-protocol/03-building-an-mcp-server.md).
- **Memory (agent)**: Information persisted across sessions, such as files or stores the agent reads and writes. See [04 · Memory and persistence](04-context-engineering/04-memory-and-persistence.md).
- **Messages API**: The `POST /v1/messages` endpoint through which all Claude generation flows. See [06 · Messages API](06-claude-api/02-messages-api.md).
- **Misinformation (OWASP LLM09)**: False or misleading output that users rely on. See [12 · OWASP LLM mapping](12-ai-security/owasp-llm-mapping.md).
- **Mock mode**: This repository's offline lab mode, using a fake client with canned responses. See [19 · Hands-on labs](19-hands-on-labs/README.md).
- **Model selection**: Choosing a model by capability, latency, cost and constraints, measured on evals. See [05 · Model selection](05-claude-products-and-models/03-model-selection.md).
- **Multi-agent system**: Several agents, often an orchestrator and workers, cooperating on a task. See [10 · Multi-agent architecture](10-agentic-ai/04-multi-agent-architecture.md).

## N

- **NIST AI RMF**: The NIST AI Risk Management Framework, organised as Govern, Map, Measure and Manage. See [12 · AI governance](12-ai-security/12-ai-governance.md).

## O

- **OAuth 2.1**: The authorization framework MCP uses for HTTP servers. See [08 · MCP security](08-model-context-protocol/05-mcp-security.md).
- **Observability**: Logs, metrics and traces that explain what a system did and why. See [15 · Observability](15-production-operations/02-observability.md).
- **Orchestrator–workers**: A pattern where a lead model delegates subtasks to workers and synthesises results. See [10 · Workflow patterns](10-agentic-ai/02-workflow-patterns.md).
- **output_config**: The request object holding `effort`, structured output `format` and task budgets. See [06 · Messages API](06-claude-api/02-messages-api.md).
- **OWASP Top 10 for LLM Applications**: A ranked list of LLM application risks (2025 edition). See [12 · OWASP LLM mapping](12-ai-security/owasp-llm-mapping.md).

## P

- **Parallel tool use**: Claude requesting several tool calls in one response; return all results in one message. See [07 · The tool-use loop](07-tool-use-and-function-calling/03-the-tool-use-loop.md).
- **Parallelisation (workflow)**: Running independent model calls concurrently, by sectioning or voting. See [10 · Workflow patterns](10-agentic-ai/02-workflow-patterns.md).
- **pause_turn**: A stop reason indicating a long server-tool turn paused and should be continued. See [07 · Server tools](07-tool-use-and-function-calling/04-server-tools.md).
- **Permission mode**: The Claude Code setting (`default`, `acceptEdits`, `plan`, `auto`, `dontAsk`, `bypassPermissions`) that governs prompts. See [09 · Permissions and settings](09-claude-code/04-permissions-and-settings.md).
- **PII (personal data)**: Information identifying a person, subject to privacy law and policy. See [12 · Data exfiltration and disclosure](12-ai-security/04-data-exfiltration-and-disclosure.md).
- **Plan mode**: A Claude Code mode where Claude explores read-only and proposes a plan before editing. See [09 · Permissions and settings](09-claude-code/04-permissions-and-settings.md).
- **Plugin (Claude Code)**: A package bundling skills, commands, subagents, hooks and MCP servers. See [09 · Commands, skills and subagents](09-claude-code/05-commands-skills-subagents.md).
- **Production readiness**: The checklist of reliability, security, cost and operational criteria before launch. See [15 · Production readiness](15-production-operations/01-production-readiness.md).
- **Progressive disclosure**: Loading detailed context only when needed, as Skills do. See [04 · Progressive disclosure and Skills](04-context-engineering/06-progressive-disclosure-and-skills.md).
- **Project (Claude apps)**: A workspace with custom instructions and knowledge files shared across chats. See [05 · Projects and knowledge](05-claude-products-and-models/04-projects-and-knowledge.md).
- **Prompt**: The instructions and content sent to a model. See [02 · Prompt fundamentals](02-claude-fundamentals/03-prompt-fundamentals.md).
- **Prompt caching**: Reusing a processed request prefix for lower cost and latency. See [04 · Prompt caching](04-context-engineering/03-prompt-caching.md).
- **Prompt chaining**: Sequential calls where each output feeds the next. See [03 · Task decomposition and chaining](03-prompt-engineering/05-task-decomposition-and-chaining.md).
- **Prompt engineering**: Designing prompts to get reliable, useful outputs. See [03 · Prompt engineering](03-prompt-engineering/README.md).
- **Prompt injection**: Input that manipulates a model into ignoring intended instructions (OWASP LLM01). See [12 · Prompt injection](12-ai-security/02-prompt-injection.md).
- **Prompt template**: A reusable prompt with variables filled per request, versioned like code. See [03 · System prompts and roles](03-prompt-engineering/07-system-prompts-and-roles.md).
- **Prompts (MCP primitive)**: User-controlled reusable templates exposed by an MCP server. See [08 · Architecture](08-model-context-protocol/02-architecture.md).

## Q

- **Query rewriting**: Reformulating a user question into a better search query before retrieval. See [11 · Retrieval strategies](11-rag-and-knowledge-systems/04-retrieval-strategies.md).

## R

- **RAG (retrieval-augmented generation)**: Retrieving relevant content at query time and adding it to the prompt. See [11 · RAG fundamentals](11-rag-and-knowledge-systems/01-rag-fundamentals.md).
- **Rate limit**: A cap on requests or tokens per minute; exceeding it returns HTTP 429. See [15 · Rate limits and capacity](15-production-operations/06-rate-limits-and-capacity.md).
- **Recall@k**: The share of queries whose correct source appears in the top k retrieved results. See [11 · RAG evaluation](11-rag-and-knowledge-systems/06-rag-evaluation.md).
- **Red teaming**: Adversarial testing to find safety and security failures. See [14 · Safety and red-team evals](14-evaluation-and-testing/07-safety-and-red-team-evals.md).
- **Refusal**: A `stop_reason` indicating a safety classifier declined the request. See [06 · Messages API](06-claude-api/02-messages-api.md).
- **Reranking**: Re-scoring retrieved candidates with a more precise model. See [11 · Retrieval strategies](11-rag-and-knowledge-systems/04-retrieval-strategies.md).
- **Resources (MCP primitive)**: Application-controlled data an MCP server exposes for reading into context. See [08 · Architecture](08-model-context-protocol/02-architecture.md).
- **Responsible Scaling Policy (RSP)**: Anthropic's policy tying safety measures to model capability levels. See [02 · Anthropic's safety approach](02-claude-fundamentals/04-anthropic-safety-approach.md).
- **Responsible use**: Using AI in ways that are lawful, fair, transparent and appropriately supervised. See [02 · Responsible use](02-claude-fundamentals/05-responsible-use.md).
- **Retry with backoff**: Retrying transient failures after increasing delays with jitter. See [06 · Errors, rate limits and retries](06-claude-api/06-errors-rate-limits-retries.md).
- **ROI (return on investment)**: Business value delivered relative to cost, used to justify AI projects. See [13 · Business value and ROI](13-enterprise-ai-architecture/08-business-value-and-roi.md).
- **Routing**: A workflow that classifies input and sends it to a specialised prompt or model. See [10 · Workflow patterns](10-agentic-ai/02-workflow-patterns.md).

## S

- **Sampling (MCP)**: A client feature allowing a server to request a completion from the host's model. See [08 · Architecture](08-model-context-protocol/02-architecture.md).
- **Sandbox**: An isolated environment for running code or tools with limited access. See [12 · Enterprise deployment controls](12-ai-security/14-enterprise-deployment-controls.md).
- **Secrets management**: Storing and injecting credentials securely, never in prompts or code. See [12 · Secrets management](12-ai-security/10-secrets-management.md).
- **Semantic search**: Finding content by meaning using embeddings. See [11 · Embeddings and indexing](11-rag-and-knowledge-systems/03-embeddings-and-indexing.md).
- **Sensitive information disclosure**: Revealing data the user should not see (OWASP LLM02). See [12 · Data exfiltration and disclosure](12-ai-security/04-data-exfiltration-and-disclosure.md).
- **Server tools**: Tools such as web search, web fetch and code execution that run on Anthropic's infrastructure. See [07 · Server tools](07-tool-use-and-function-calling/04-server-tools.md).
- **Settings precedence (Claude Code)**: Managed, then command line, then project local, then shared project, then user. See [09 · Permissions and settings](09-claude-code/04-permissions-and-settings.md).
- **SLA / SLO**: Service-level agreement or objective, the commitments on availability, latency and support. See [13 · Stakeholder communication](13-enterprise-ai-architecture/06-stakeholder-communication.md).
- **Slash command**: A `/command` in Claude Code, built in or defined as a skill. See [09 · Commands, skills and subagents](09-claude-code/05-commands-skills-subagents.md).
- **stdio transport**: The MCP transport that runs a server as a local subprocess over standard input and output. See [08 · Architecture](08-model-context-protocol/02-architecture.md).
- **stop_reason**: The response field that says why generation ended; check it before using content. See [06 · Messages API](06-claude-api/02-messages-api.md).
- **Streamable HTTP**: The MCP transport for remote servers using HTTP POST and optional SSE streams. See [08 · Architecture](08-model-context-protocol/02-architecture.md).
- **Streaming**: Receiving a response incrementally as server-sent events. See [06 · Streaming](06-claude-api/03-streaming.md).
- **Strict tool use**: `strict: true` on a tool definition, guaranteeing arguments match the schema. See [07 · Defining tools](07-tool-use-and-function-calling/02-defining-tools.md).
- **Structured outputs**: Constraining a response to a JSON Schema via `output_config.format`. See [03 · Structured output](03-prompt-engineering/06-structured-output.md).
- **Subagent**: A delegated agent with its own context window and tools, returning a summary. See [09 · Commands, skills and subagents](09-claude-code/05-commands-skills-subagents.md).
- **Supply chain risk (AI)**: Risk from third-party models, data, packages, plugins and MCP servers (OWASP LLM03). See [12 · Supply chain risks](12-ai-security/07-supply-chain-risks.md).
- **System prompt**: Operator instructions that set role, rules and context for a conversation. See [03 · System prompts and roles](03-prompt-engineering/07-system-prompts-and-roles.md).
- **System prompt leakage**: Disclosure of system prompt contents (OWASP LLM07). See [12 · OWASP LLM mapping](12-ai-security/owasp-llm-mapping.md).

## T

- **Task budget**: A beta token budget that lets Claude pace an agentic loop. See [10 · Agent reliability](10-agentic-ai/07-agent-reliability.md).
- **Temperature**: A sampling parameter in older models; current Claude models reject it. See [06 · Messages API](06-claude-api/02-messages-api.md).
- **Threat model**: A structured analysis of assets, threats and controls. See [12 · LLM threat modelling](12-ai-security/01-llm-threat-modelling.md).
- **Time to first token (TTFT)**: Latency until the first output token arrives. See [15 · Latency optimisation](15-production-operations/04-latency-optimisation.md).
- **Token**: The unit of text a model processes and the basis for cost and limits. See [01 · Tokens and tokenisation](01-ai-and-llm-fundamentals/04-tokens-and-tokenisation.md).
- **Token passthrough**: Forwarding a client's token to downstream services; forbidden for MCP servers. See [08 · MCP security](08-model-context-protocol/05-mcp-security.md).
- **Tool poisoning**: Malicious instructions hidden in tool descriptions or metadata. See [12 · MCP server security](12-ai-security/08-mcp-server-security.md).
- **tool_choice**: The request setting for tool selection; `auto` or `none` on Opus 5.5, Sonnet 5.5, Fable 5.1 and Mythos 5.1. See [07 · Defining tools](07-tool-use-and-function-calling/02-defining-tools.md).
- **Tool Runner**: An SDK helper that runs the tool-use loop for tools you define. See [07 · The tool-use loop](07-tool-use-and-function-calling/03-the-tool-use-loop.md).
- **tool_result**: The block returning a tool's output to Claude, matched to a `tool_use` id. See [07 · The tool-use loop](07-tool-use-and-function-calling/03-the-tool-use-loop.md).
- **Tool use (function calling)**: Letting Claude request calls to functions you define. See [07 · Tool use fundamentals](07-tool-use-and-function-calling/01-tool-use-fundamentals.md).
- **tool_use**: The content block (and stop reason) in which Claude requests a tool call. See [07 · Tool use fundamentals](07-tool-use-and-function-calling/01-tool-use-fundamentals.md).
- **Tools (MCP primitive)**: Model-controlled functions an MCP server exposes. See [08 · Architecture](08-model-context-protocol/02-architecture.md).
- **Trust boundary**: A line in a design where data or control passes between parties of different trust. See [12 · LLM threat modelling](12-ai-security/01-llm-threat-modelling.md).

## U

- **Unbounded consumption**: Uncontrolled resource or cost use from runaway requests or loops (OWASP LLM10). See [15 · Rate limits and capacity](15-production-operations/06-rate-limits-and-capacity.md).
- **Usage object**: Token counts in each response, including cache creation and cache read tokens. See [06 · Token counting and cost](06-claude-api/08-token-counting-and-cost.md).

## V

- **Vector and embedding weaknesses**: Risks in RAG stores such as leakage across tenants or poisoning (OWASP LLM08). See [12 · OWASP LLM mapping](12-ai-security/owasp-llm-mapping.md).
- **Vector database**: A store optimised for similarity search over embeddings. See [11 · Embeddings and indexing](11-rag-and-knowledge-systems/03-embeddings-and-indexing.md).
- **Vision**: Claude's ability to read images and PDFs supplied as content blocks. See [06 · Vision, documents and citations](06-claude-api/04-vision-documents-and-citations.md).

## W

- **Web fetch tool**: A server tool that retrieves the content of URLs already present in the conversation. See [07 · Server tools](07-tool-use-and-function-calling/04-server-tools.md).
- **Web search tool**: A server tool that lets Claude search the web and cite results. See [07 · Server tools](07-tool-use-and-function-calling/04-server-tools.md).
- **Workflow**: A system where code defines the steps and the model fills them in. See [10 · Workflow patterns](10-agentic-ai/02-workflow-patterns.md).
- **Workspace (Claude Console)**: A grouping of API keys, limits and settings inside an organisation. See [06 · Getting started with the API](06-claude-api/01-getting-started-with-the-api.md).

## Z

- **Zero data retention (ZDR)**: An arrangement under which request data is not retained after processing; some models require standard retention instead. See [13 · Data governance and compliance](13-enterprise-ai-architecture/05-data-governance-and-compliance.md).
- **Zero-shot prompting**: Asking for a task without examples. See [03 · Examples and few-shot](03-prompt-engineering/03-examples-few-shot.md).
