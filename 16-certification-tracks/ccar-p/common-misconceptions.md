# CCAR-P Common Misconceptions

> Twenty-six architect-level misconceptions with corrections. Each maps to objectives in
> [`registry.yaml`](../registry.yaml). Product facts are as of 2026-10-24.

| # | Misconception | Correction | Objective |
|---|---|---|---|
| 1 | "Agents are the modern default; workflows are legacy." | Start with the simplest tier that meets the need. Workflows are cheaper, faster and easier to test; agents are justified only when the path cannot be known in advance, the value supports the cost and errors are recoverable. | 1.3 |
| 2 | "More agents means better results." | Multi-agent systems add tokens, latency and coordination failures. Use them for parallelisable work, context protection or privilege separation, and prove the gain with evals. | 1.4 |
| 3 | "The architecture is done when the model call works." | A design without a feedback loop (outcome capture, eval refresh, gated release) cannot detect drift or regressions. | 1.2 |
| 4 | "ROI equals time saved per request times headcount cost." | Measure cost per completed task including retries, human review, rework and error costs, against a real baseline, with sensitivity ranges. | 1.6 |
| 5 | "Always use the most capable model to be safe." | Capability is one dimension. Choose per route against an eval, latency SLO and cost; often the right move is lowering effort before changing tier. | 2.1 |
| 6 | "A cheaper model in a cascade always saves money." | Routing adds calls and misroutes, and caches are model-scoped, so each model pays its own cache writes. Measure the strongest model at lower effort first. | 2.1, 4.5 |
| 7 | "Setting a low temperature makes outputs deterministic." | Current models reject `temperature`, `top_p` and `top_k`. Consistency comes from clear instructions, examples, structured outputs and evals. | 2.2 |
| 8 | "Prefilling the assistant turn is the best way to force JSON." | Prefill is not supported on current models. Use structured outputs (`output_config.format` or `messages.parse`) or `strict: true` tools. | 2.2 |
| 9 | "Forcing a tool with `tool_choice` guarantees the call." | Forced `tool_choice` (`any`/`tool`) returns an error on Opus 5.5, Sonnet 5.5, Fable 5.1 and Mythos 5.1. Use `auto` plus a clear instruction, strict tool schemas, or structured outputs. | 2.2, 3.1 |
| 10 | "A 1M-token context window means retrieval is obsolete." | Large contexts cost more, slow responses and can distract the model. RAG still wins for large, changing or permission-filtered corpora; long context wins for small, stable ones (with caching). | 2.4, 3.6 |
| 11 | "Prompt caching works automatically if the prompt is mostly the same." | Caching is an exact prefix match. A timestamp, reordered tools or edited earlier content invalidates everything after it. Verify `cache_read_input_tokens`. | 2.5 |
| 12 | "A strongly worded system prompt prevents data leakage." | Instructions are advisory and can be bypassed. If the model must not disclose data, it should not be able to retrieve it: scope tools and retrieval to the user's entitlements. | 2.2, 3.2, 5.1 |
| 13 | "More tools make an agent more capable." | Extra and overlapping tools cause wrong selections, inflate context and widen the attack surface. Fewer, narrower, intent-level tools plus progressive discovery perform better. | 3.1, 3.8 |
| 14 | "A service account is fine because the agent is internal." | A shared, broad credential lets any user reach any data through the agent (confused deputy). Use delegated user identity or tightly scoped service identities, and authorise every tool call server-side. | 3.2 |
| 15 | "MCP is always the right integration choice." | MCP shines for reuse across hosts. For one application with a few operations, a direct tool is simpler and smaller; for another organisation's capability, a task-level agent-to-agent contract fits better. | 3.7 |
| 16 | "Dense vector search handles every query type." | Identifiers, codes and rare terms need lexical or hybrid retrieval; tables need query tools; live data needs API calls. | 3.5, 3.6 |
| 17 | "Logging every prompt in full is good observability." | Full payload logging creates privacy and cost problems. Log structured metadata for everything, redact payloads, and keep full detail for samples and anomalies under access control. | 3.4, 4.6, 5.4 |
| 18 | "An LLM judge is objective." | Judges show position, verbosity and self-preference biases and drift. Use rubrics, include sources, randomise order and calibrate against human labels. | 4.2 |
| 19 | "If the eval score went up, the change is better." | Scores tuned on the same set overfit. Use dev/validation/held-out test splits, check per-slice results, and confirm online with shadow or canary traffic. | 4.2, 4.3 |
| 20 | "Hallucinations mean you need a bigger model." | Many hallucinations come from retrieval misses, missing "not found" paths or ambiguous instructions. Diagnose by inspecting retrieved context and sweeping tiers before switching. | 4.4 |
| 21 | "Human-in-the-loop makes any design safe." | Reviewers rubber-stamp when they see only conclusions or face alert fatigue. Show evidence and the exact action, route only judgement cases, and audit reviewer performance. | 5.3 |
| 22 | "Our provider is certified, so we are compliant." | Provider attestations cover the provider's scope. Your logging, retention, vector stores, regions and access controls are your responsibility; confirm what each offering covers. | 5.4 |
| 23 | "Fairness is satisfied if aggregate accuracy is high." | Aggregates hide weak slices. Evaluate by language, region and other lawful slices, run counterfactual tests, and keep humans accountable for decisions about people. | 5.5 |
| 24 | "CLAUDE.md rules are enough to keep Claude Code away from secrets." | CLAUDE.md is guidance. Use deny rules (ideally managed), hooks and credential isolation for anything that must never happen. | 7.1 |
| 25 | "Project settings can switch the whole team into bypass mode." | `auto` and `bypassPermissions` as a default mode are not honoured from project or local settings; managed settings override everything else. | 7.1 |
| 26 | "Launch is the finish line." | Models are deprecated on schedules and behaviour changes between versions. Budget for monitoring, iteration, eval upkeep and planned migrations. | 6.5 |

See the [decision scenarios](decision-scenarios.md) for worked examples of several of these, and the
[readiness assessment](readiness-assessment.md) to find which ones you still hold.
