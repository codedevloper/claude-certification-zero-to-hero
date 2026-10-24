# CCAR-P Revision Notes

> Condensed notes for the final two weeks. Exam facts come from [`registry.yaml`](../registry.yaml);
> API and product facts are as of 2026-10-24. Each section links to the full study guide.

**Exam at a glance:** 63 items (multiple-choice and multiple-response), 120 minutes, scaled score 720 on
100–1,000 to pass, USD 175, valid 12 months. Updated guides publish 2026-11-17; updated content from
2026-12-07. Details: [README](README.md), [exam day](exam-day.md).

| Domain | Weight | Rough items (of 63) |
|---|---|---|
| 1 Solution Design & Architecture | 17% | ~11 |
| 2 Models, Prompting & Context | 13% | ~8 |
| 3 Integration | 19% | ~12 |
| 4 Evaluation, Testing & Optimization | 16% | ~10 |
| 5 Governance, Safety & Risk | 14% | ~9 |
| 6 Stakeholders & Lifecycle | 14% | ~9 |
| 7 Developer Productivity & Enablement | 7% | ~4 |

Item counts per domain are our estimates from the weights, not official figures.

---

## Domain 1 — Solution design ([guide](study-guide/domain-1.md))

- Simplest tier first: single augmented call → workflow → agent → multi-agent. Escalate with evidence.
- Agent only if all four hold: **complex** task, enough **value**, Claude **viable**, **cost of error**
  manageable.
- Workflow = code controls flow; agent = model controls flow. Hybrid (workflow shell, bounded agent inside a
  step) is often best.
- Workflow patterns: chain (with gates), router, parallel (sectioning/voting), evaluator–optimiser,
  orchestrator–workers.
- Multi-agent pays off for parallel work, context protection and privilege separation; costs tokens and
  debuggability. Workers get minimal tools, clear specs, output schemas; return condensed results.
- End-to-end = input (validate, redact, tag untrusted) → processing → output (validate, encode, risk gate) →
  **feedback** (telemetry, reviewer edits → evals → gated release).
- Decompose by function, data (map-reduce), time (plan/approve/execute), risk (isolate risky step) and
  verification (generate vs check).
- Value per **completed task**, including retries, review and rework.

## Domain 2 — Models, prompting, context ([guide](study-guide/domain-2.md))

- Models (2026-10-24): `claude-opus-5-5` (default), `claude-sonnet-5-5`, `claude-haiku-5-5`,
  `claude-fable-5-1` (most capable). No date suffixes. All 1M context.
- Request rules: no `temperature`/`top_p`/`top_k`; no prefill; no forced `tool_choice` (`any`/`tool`);
  thinking adaptive; depth via `output_config.effort` (`low` … `max`); `budget_tokens` is legacy.
- Opus 5.5's effort default is `medium`; set effort explicitly per route.
- Selection: eval first, start capable, step down effort then tier; compare against "strong model, low
  effort" before building cascades (caches are model-scoped).
- Guardrails in layers: input, prompt, call (structured outputs, strict tools), output, action.
- Few-shot: 3–5 diverse examples in tags. Reasoning: adaptive thinking + effort over hand-written scaffolds.
- Context: smallest high-signal set. Token counting endpoint; compaction (summarises, beta); context editing
  (clears tool results/thinking, beta); sub-agents for reading-heavy work.
- Caching: prefix match over tools → system → messages; ≤4 breakpoints; volatile content last; verify
  `cache_read_input_tokens`. Mid-conversation `system` messages keep the cached prefix.
- Skills: description up front, body on demand (progressive disclosure).

## Domain 3 — Integration ([guide](study-guide/domain-3.md))

- Capability bloat: generic tools, read+write in one tool, too many/overlapping tools, unapproved actions.
  Fix with narrow intent-level tools, `strict: true`, read/write split, approvals, tool search.
- Auth: model never holds secrets; delegated user tokens where entitlements matter; authorise every tool call
  server-side; MCP HTTP auth is OAuth 2.1-based; no token passthrough; workload identity instead of
  long-lived keys.
- Accuracy–latency: tier, effort, retrieval depth, re-ranking, critic loops, voting vs streaming and caching.
  Justify with eval numbers against the SLO.
- Observability: traces per task, spans per call; tokens incl. cache fields; `stop_reason` mix; quality
  sampling; redaction.
- RAG: structure-aware or parent–child chunking; contextual chunks; metadata (ACL, version, date); hybrid
  search for identifiers; re-rank; cite; "not found" path.
- Retrieval by data shape: prose → dense + re-rank; codes → hybrid; tables → query tool; multi-hop → agentic
  retrieval; small stable corpus → long context + cache; live data → tool.
- Mechanism: one app → direct tool; many hosts → MCP; mature CLI for dev agents → CLI in sandbox; other
  owner/org → A2A task contract.
- Progressive discovery (tool search, Skills, retrieval, sub-agents) beats monolithic context at scale;
  keep one tool and the search tool non-deferred.

## Domain 4 — Evaluation ([guide](study-guide/domain-4.md))

- Metrics: accuracy, grounding, format, latency (TTFT, p95), cost per completed task, safety, security,
  business. Pair every target with a guardrail metric.
- Dataset: real traffic first, synthetic for rare cases, adversarial for security; stratify; label with
  guidelines; dev/validation/test split; version; refresh from production failures.
- Graders: code (cheap, deterministic), LLM judge (rubric, sources, calibration, randomised order), human
  (ground truth, calibration).
- A/B: offline first; shadow → canary → A/B; pre-registered metric and sample size; one change at a time.
- Diagnosis: check `stop_reason`, retrieved chunks, prompt contradictions, tier/effort sweeps (model mismatch
  vs prompt failure), trajectory reads for agents.
- Optimise: free wins (cache, trim, lean tools) → batch/parallel/stream → effort → tier → architecture.
- Monitor: per-call logs with prompt version and tokens; OTel traces; alert on change.

## Domain 5 — Governance ([guide](study-guide/domain-5.md))

- Defence in depth; least privilege is the most reliable injection control.
- Failure modes: hallucination, direct/indirect injection, exfiltration, excessive agency, insecure output
  handling, supply chain, over-reliance, drift, bias, availability.
- HITL by impact × reversibility × confidence; irreversible high-impact → always human approval.
- Reviewer UX: show evidence and exact action; easy reject/edit; measure reviewers.
- GDPR: lawful basis, minimisation, rights incl. erasure (propagate to vector stores), DPIA, transfers,
  retention. HIPAA: BAA-covered services, minimum necessary, audit, encryption. FedRAMP: authorised platform
  and boundary. Confirm vendor coverage; it varies by platform and contract.
- Fairness: sliced evals, counterfactual tests, exclude irrelevant attributes, humans own decisions about
  people. Transparency: disclose AI, explain with sources, route to a human.
- Frameworks: NIST AI RMF (Govern, Map, Measure, Manage), ISO/IEC 42001, OWASP Top 10 for LLM Applications.

## Domain 6 — Stakeholders and lifecycle ([guide](study-guide/domain-6.md))

- Discovery: value, users, data, integration, risk, quality, NFRs, organisation. Get real examples early.
- Communicate options with consequences per audience; quality as measured rates, not promises.
- ADR: context, options, decision, consequences, status, evidence, date.
- SLOs across availability, latency, quality, cost; degraded modes and fallbacks.
- Handover pack: architecture, ADRs, prompt/config registry, eval suite, threat model, runbooks,
  implementation guide, RACI.
- Lifecycle: discovery → design → prototype → build → handoff → monitor → iterate → model change → retire.
  Pin model IDs; plan migrations before retirement dates.

## Domain 7 — Enablement ([guide](study-guide/domain-7.md))

- Settings precedence: managed → `--settings` → project local → shared project → user. Lists merge.
- Permissions: `allow` / `ask` / `deny` rules like `Bash(make test)`, `Read(./.env)`. Shared allow rules wait
  for workspace trust; deny/ask apply immediately. `auto`/`bypassPermissions` default modes not honoured from
  project/local settings.
- Guidance → CLAUDE.md, Skills. Enforcement → permissions, hooks, managed settings, CI.
- Project MCP servers in `.mcp.json`, no secrets inside.
- Subagents (isolated context, limited tools), Skills (on demand), plugins (distribution), headless
  `claude -p`, Agent SDK.
- Ops debugging: read-only agents for incident timelines; 400s after upgrade → removed parameters; 429 →
  backoff and `retry-after`; cost spikes → cache invalidators and runaway loops.
