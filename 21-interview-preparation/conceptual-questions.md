# Conceptual Interview Questions

Thirty questions on LLM and Claude fundamentals, prompting, the API, tools, MCP, RAG, agents and evaluation, with model
answers. They suit AI engineer, solution architect and AI security interviews. All questions are original; none are
taken from any exam.

> **How to use this page:** cover the answer, say yours out loud in under two minutes, then compare. A good answer
> defines the concept, explains the mechanism, gives a trade-off and ends with a practical example. API details are
> **as of 2026-10-24**; see the [Claude API cheat sheet](../22-cheat-sheets/claude-api.md).

Levels: **F** foundational, **I** intermediate, **A** advanced.

---

## Foundations

### 1. (F) What is a large language model, in terms a product manager would understand?

**Model answer:** An LLM is a neural network trained on a very large amount of text to predict the next piece of text
(a token) given everything before it. Repeating that prediction produces fluent answers, code or summaries. Further
training on human feedback and guidelines turns that predictor into an assistant that follows instructions. Two
consequences matter for product decisions: it is very good at language patterns and reasoning over what is in front
of it, and it has no built-in way to know whether a fact is true or current, so you supply sources and verify
important claims. See [01 · Large language models](../01-ai-and-llm-fundamentals/03-large-language-models.md).

### 2. (F) What is a token, and why should an engineer care?

**Model answer:** A token is the unit a model reads and writes, often a word piece; a rough English rule of thumb is
three to four characters per token, but it varies by language and tokenizer. Tokens drive three things: **cost**
(you pay per input and output token), **limits** (context window and `max_tokens` are counted in tokens) and
**latency** (output tokens are generated one at a time). Engineers should measure with the token-counting endpoint
rather than estimate, especially after a model change, because tokenizers differ between model generations.

### 3. (F) What is a context window, and what happens when you exceed it?

**Model answer:** The context window is the maximum number of tokens the model can consider in one request, covering
the system prompt, tools, conversation history, documents and the output. As of 2026-10-24 current Claude models offer
a 1M-token window. If a request is too large the API rejects it, so applications must manage context: retrieve only
relevant passages, summarise or compact old turns, clear stale tool results, and delegate reading to sub-agents. A
large window is not free; more context costs more, adds latency and can dilute attention on what matters.

### 4. (F) Why do LLMs hallucinate, and how do you reduce it?

**Model answer:** The model generates plausible continuations; when the needed fact is missing from its context or
training, a plausible-sounding but wrong answer can still be the most likely output. Leading questions make it worse.
Mitigations: ground answers in supplied sources; give explicit permission to say "I don't know"; ask for quotes or use
citations and verify them in code; decompose claims; compute numbers with code; use evaluations to measure the rate;
and keep humans reviewing high-stakes outputs. No technique gets the rate to zero, so the system design must
tolerate occasional errors.

### 5. (F) What is the difference between the system prompt and the user message?

**Model answer:** The system prompt carries the operator's instructions: role, rules, tone, safety boundaries and
standing context that apply for the whole conversation. User messages carry the end user's requests and data. Keeping
them separate matters for behaviour (system-level rules are given more weight), for security (users and documents
should not be able to impersonate the operator) and for cost (a stable system prompt is ideal for prompt caching).
Task-specific data belongs in user turns, not the system prompt.

### 6. (F) Explain Anthropic's approach to model safety at a high level

**Model answer:** Anthropic trains Claude to be helpful, honest and harmless, using techniques such as reinforcement
learning from human feedback and Constitutional AI, where a written set of principles guides the model's own
critique and revision during training. It publishes a Responsible Scaling Policy that ties safety measures to
capability levels, and deploys classifiers that can decline certain high-risk requests (surfaced in the API as
`stop_reason: "refusal"`). For builders, the practical point is shared responsibility: the model has safeguards, but
your application still needs access control, output validation, monitoring and human oversight. See
[02 · Anthropic's safety approach](../02-claude-fundamentals/04-anthropic-safety-approach.md).

## Prompting and context

### 7. (F) What makes a prompt effective?

**Model answer:** It states the goal, the audience and use of the output, the necessary context, the constraints, the
output format and what to do when information is missing. It separates instructions from data (for example with XML
tags), explains the reason behind non-obvious rules, and includes examples when the format or tone is hard to
describe. The test is whether a capable new colleague could do the task from the prompt alone. Then you evaluate it
on real inputs and iterate one change at a time.

### 8. (I) When would you use few-shot examples, and what can go wrong?

**Model answer:** Use examples when the desired format, tone or decision boundary is easier to show than describe,
such as classification labels with edge cases or a house writing style. Use three to five varied examples wrapped in
tags, covering tricky cases. Risks: the model copies surface features (length, phrasing, even specific values),
examples that all look alike narrow the output, and examples that contradict instructions confuse it. Examples also
cost tokens on every call, so cache them if the prefix is stable.

### 9. (I) How do you get reliable JSON out of Claude today?

**Model answer:** Use structured outputs: `output_config.format` with a JSON Schema, or the SDK's
`client.messages.parse()` with a typed model, which constrains the response to the schema. For tool arguments, set
`strict: true` on the tool definition. Older tricks such as prefilling the assistant turn with `{` are not supported
on current models and return a 400. Still check `stop_reason` (a `max_tokens` stop means truncated output), and
validate business rules in code, because schema-valid does not mean semantically correct.

### 10. (I) What are adaptive thinking and the effort parameter?

**Model answer:** With adaptive thinking (`thinking={"type": "adaptive"}`), Claude decides when and how much to
reason before answering. The `effort` setting in `output_config` (`low`, `medium`, `high`, `xhigh`, `max`) tunes how
thorough it is and therefore how many tokens it spends. Fixed thinking budgets (`budget_tokens`) are legacy and
rejected on current models. In practice you set effort per route: low for chat and classification, higher for coding,
multi-step agents and analysis, and you measure quality and cost per completed task before raising the default.

### 11. (I) What is context engineering, and how is it different from prompt engineering?

**Model answer:** Prompt engineering is about wording instructions. Context engineering is about deciding **what
information occupies the context window at each step** of a system: which documents are retrieved, what history is
kept or summarised, which tools are loaded, what memory is injected, and in what order. It treats context as a scarce
resource. Techniques include retrieval, compaction, clearing old tool results, progressive disclosure with Skills,
sub-agents with isolated contexts, and caching stable prefixes. For agents it usually matters more than prompt
wording. See [04 · What is context engineering](../04-context-engineering/01-what-is-context-engineering.md).

### 12. (I) How does prompt caching work and how do you know it is working?

**Model answer:** Caching stores the processed prefix of a request (tools, then system, then messages, in that order)
so later requests with an identical prefix read it at a fraction of the input price and with lower latency. You mark
breakpoints with `cache_control` or use automatic caching; the default lifetime is five minutes, refreshed on each
read, with a one-hour option. Any byte change before a breakpoint invalidates it, so put stable content first and
volatile data (timestamps, user questions) last. Verify with `usage.cache_read_input_tokens` on repeat requests; zero
means something in the prefix is changing.

### 13. (A) A conversation has run for hours and quality is dropping. What are your options?

**Model answer:** Diagnose first: is the context full of stale tool output, contradictory instructions or irrelevant
history? Options, cheapest first: clear old tool results (context editing); summarise and restart with the summary;
use server-side compaction on supported models; move durable facts to a memory store or Project knowledge;
re-state key instructions with a mid-conversation system message where supported; and split work across sub-agents
so each has a focused context. Keep the transcript append-only where possible to preserve caching and thinking-block
validity.

## The API

### 14. (F) Walk me through a Messages API request and response

**Model answer:** A request names the `model`, sets `max_tokens`, and sends `messages`, an alternating list starting
with a user turn, plus optional `system`, `tools`, `thinking` and `output_config`. The response contains a list of
content blocks (text, tool use, thinking), a `stop_reason`, and `usage` with input, output and cache token counts.
The client must check `stop_reason` before using content: `end_turn` is a finished answer, `max_tokens` is
truncated, `tool_use` asks you to run tools, `pause_turn` asks you to continue, and `refusal` means a safeguard
declined.

### 15. (I) When would you stream, and when would you use batches?

**Model answer:** Stream when a person is waiting (chat UIs show tokens as they arrive) or when outputs are long, since
large non-streaming requests risk HTTP timeouts. Use Message Batches for work that can wait: overnight
classification, back-fills, evaluations. Batches cost 50% less, take up to 24 hours (most finish within an hour), and
return results in any order keyed by `custom_id`. They are complementary: a product might stream interactive answers
and batch the nightly analytics over the same prompts.

### 16. (I) How should a client handle errors and rate limits?

**Model answer:** Separate retryable from non-retryable errors. 400, 401, 403 and 404 mean fix the request or
credentials; retrying is wasteful. 429, 500, 529 and connection errors are retryable with exponential backoff and
jitter, honouring `retry-after`. The SDKs retry a couple of times by default. Add concurrency limits so bursts do not
cause retry storms, an overall deadline per request, idempotency for side effects, and logging of the request ID.
Reduce pressure structurally with caching, shorter outputs and batching.

## Tools, MCP and agents

### 17. (F) How does tool use work end to end?

**Model answer:** You describe tools with a name, a description and a JSON Schema for inputs. Claude decides whether
to call one and returns `tool_use` blocks with arguments; the response stops with `stop_reason: "tool_use"`. Your code
runs the tools, then sends a user message containing a `tool_result` for every call (errors marked `is_error`).
Claude continues, possibly calling more tools, until it answers. The model never executes anything itself: your code
holds the credentials and decides what really runs, which is where validation and authorisation belong.

### 18. (I) What makes a good tool definition?

**Model answer:** A clear, specific name; a description written like documentation (what it does, when to use it and
when not, what it returns, input formats); a tight schema with enums, required fields and no extra properties; and
results that are concise, informative and actionable, including helpful error messages. Fewer, well-scoped tools beat
many overlapping ones. Separate read and write operations so permissions and approvals can differ. Test tool
selection with a routing evaluation set.

### 19. (I) What is MCP and what problem does it solve?

**Model answer:** The Model Context Protocol is an open, JSON-RPC-based standard for connecting AI applications to
external systems. Servers expose tools, resources and prompts; hosts such as Claude Code or Claude Desktop connect
through clients. It replaces many bespoke integrations with one reusable server per system, the way a common port
standard lets many devices work with many computers. Transports are stdio for local servers and Streamable HTTP for
remote ones, with OAuth-based authorization for HTTP. The current revision (2026-07-28) is stateless, carrying
version and capabilities on each request.

### 20. (I) What is the difference between a workflow and an agent?

**Model answer:** In a workflow, your code defines the steps (chain, route, parallelise, evaluate and retry) and the
model fills in each step. In an agent, the model decides the next step in a loop, choosing tools until the goal is
met. Workflows are cheaper, more predictable and easier to test; agents handle open-ended tasks whose path cannot be
known in advance. Start with the simplest design that meets the requirement, and add autonomy only where it pays for
its extra cost and risk. See [10 · Workflows vs agents](../10-agentic-ai/01-workflows-vs-agents.md).

### 21. (A) When do multi-agent systems help, and when do they hurt?

**Model answer:** They help when work splits into independent parts that can run in parallel (researching many
sources), when sub-tasks would flood a single context with reading, or when different parts need different tools or
models. They hurt when the task is tightly coupled, because agents duplicate work, lose shared understanding and
multiply token costs. Good designs give each sub-agent a clear objective, boundary and output format, return concise
summaries to an orchestrator, and are justified by an evaluation showing they beat a single agent.

### 22. (A) What are Agent Skills, and how do they relate to progressive disclosure?

**Model answer:** A Skill is a folder with a `SKILL.md` file (name, description and instructions) plus optional
scripts and reference files. Only the name and description sit in context; the body loads when the skill is relevant,
and supporting files load only when needed. That is progressive disclosure: capabilities are discoverable without
paying their full context cost upfront. Skills package know-how and procedures, whereas MCP connects to live systems;
they are often used together.

## RAG and knowledge

### 23. (F) Explain retrieval-augmented generation

**Model answer:** RAG answers questions using your own content: documents are split into chunks, indexed (often as
embeddings in a vector store, sometimes with keyword search too), and at query time the most relevant chunks are
retrieved and placed in the prompt with instructions to answer from them. It gives the model current, private
knowledge without retraining, and supports citations. Its quality depends mostly on retrieval: chunking, embeddings,
hybrid search, reranking, metadata filters, access control and index freshness.

### 24. (I) How would you choose chunk size?

**Model answer:** Empirically. Start from document structure (sections and headings) rather than a fixed character
count, aim for chunks that hold one self-contained idea, add modest overlap or a context header (document title,
section) to each chunk, and then measure recall@k on a labelled question set at a few sizes. Small chunks improve
precision but lose context; large chunks keep context but dilute relevance and cost more tokens. Different document
types (FAQ, contracts, code) may need different strategies.

### 25. (I) RAG or long context: how do you decide?

**Model answer:** If the knowledge is small, stable and needed as a whole, putting it in context with prompt caching
is simpler and avoids retrieval misses. If the corpus is large, changes often, needs per-user access control, or most
of it is irrelevant to any one question, RAG is better and cheaper per query. Hybrid designs are common: retrieve a
handful of documents, then give Claude whole documents rather than tiny fragments. Decide with an eval comparing
accuracy, latency and cost. See [11 · RAG vs long context](../11-rag-and-knowledge-systems/07-rag-vs-long-context.md).

## Evaluation and operations

### 26. (I) How do you evaluate an LLM feature?

**Model answer:** Define success criteria first (accuracy, format validity, latency, cost, safety). Build a dataset
from real or realistic inputs, including edge cases and adversarial ones. Grade with code where possible (exact
match, schema checks), with a model-based grader using a clear rubric for open-ended quality, and with humans for
calibration and high-stakes cases. Run the suite on every prompt or model change, track results over time, and
sample production traffic to keep the dataset representative.

### 27. (I) What are the risks of using an LLM as a judge?

**Model answer:** Judges can be biased toward longer answers, toward their own style, or toward the first option shown;
they can be inconsistent with vague rubrics; and they can miss factual errors they cannot verify. Mitigations: specific
rubrics with examples, binary or narrow scales, asking for reasoning before the score, randomising order in pairwise
comparisons, grounding the judge with reference answers, and periodically checking agreement with human labels.

### 28. (I) How do you pick a model for a new workload?

**Model answer:** Start from requirements: quality bar, latency, volume, budget and data constraints. Build a small
eval, then test the candidates (for example Claude Opus 5.5, Sonnet 5.5 and Haiku 5.5 as of 2026-10-24) at a couple
of effort levels. Compare cost per completed task, not per call. Often a more capable model at lower effort beats a
smaller model at higher effort. Route by sub-task where that helps, batch what can wait, and re-run the eval when new
models ship. See the [model selection cheat sheet](../22-cheat-sheets/model-selection.md).

### 29. (A) What does observability mean for an LLM system?

**Model answer:** Being able to answer, for any output, what produced it and what it cost. Log per request: model and
version, prompt template version, parameters, retrieved document IDs, tool calls and results, `stop_reason`, token
usage including cache reads, latency and the request ID, with sensitive data redacted. Trace multi-step agents as a
span tree. Track metrics (error rate, refusals, cost per task, cache hit rate, eval scores on sampled traffic) and
alert on drift. OpenTelemetry tracing is supported by the SDKs.

### 30. (A) How do you manage a model upgrade safely?

**Model answer:** Treat it like a dependency upgrade. Read the migration guide for removed parameters and behaviour
changes; re-baseline token counts; run the full eval suite on the new model with current prompts, then with prompts
adjusted for the new model; compare quality, latency and cost; roll out behind a flag or to a percentage of traffic;
monitor; and keep the old model available until confidence is high. Pin model IDs in configuration so changes are
deliberate and auditable. See [15 · Model upgrades](../15-production-operations/08-model-upgrades-and-change-management.md).
