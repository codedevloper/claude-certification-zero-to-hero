# CCAR-P Architecture Decision Scenarios

> Sixteen original case studies with options analysis and a recommended decision. They are written for
> this repository, use fictional organisations and are **not** exam questions or reconstructions of exam
> content. Objective IDs refer to [`registry.yaml`](../registry.yaml).

How to use: read the context and constraints, decide yourself *before* reading the analysis, and write one
sentence of rationale. Then compare. The skill being trained is weighing options against stated constraints.

| # | Scenario | Objectives |
|---|---|---|
| 1 | Grant-application screening: workflow or agent? | 1.1, 1.3 |
| 2 | Research synthesis at scale: one agent or many? | 1.4, 2.4 |
| 3 | Procurement assistant: where should approval live? | 1.2, 5.3 |
| 4 | Justifying an AI programme to a CFO | 1.6, 6.2 |
| 5 | Model choice for a field-service copilot | 2.1, 3.3 |
| 6 | Guardrails for an HR policy assistant | 2.2, 5.1 |
| 7 | 140 tools from six MCP servers | 3.1, 3.8 |
| 8 | Shared service account behind a knowledge agent | 3.2 |
| 9 | Product-catalogue search with SKUs | 3.5, 3.6 |
| 10 | Exposing a pricing engine: MCP, API or A2A? | 3.7 |
| 11 | Agent traces at 2 million tasks a month | 3.4, 4.6 |
| 12 | Upgrading the model behind a contract-extraction service | 4.3, 6.5 |
| 13 | A hallucination complaint from a regional manager | 4.4 |
| 14 | EU personal data and US-hosted logging | 5.4 |
| 15 | Fairness in a tenant-screening summary tool | 5.5, 5.3 |
| 16 | Rolling Claude Code out to a regulated engineering org | 7.1, 7.2 |

---

## Scenario 1 — Grant-application screening: workflow or agent?

**Context.** *Northwind Foundation* receives 3,000 grant applications per cycle. Each must be checked for
eligibility (ten published criteria), scored on a five-dimension rubric and summarised for a panel. Staff
currently spend about 40 minutes per application.

**Constraints.** Decisions must be explainable to applicants; panel members make final decisions; budget is
fixed per cycle; eligibility criteria are stable.

| Option | Analysis |
|---|---|
| A. Autonomous agent that reads each application, researches the applicant online and decides | Unbounded cost and latency; web research introduces untrusted content and unverifiable claims; decisions are not the agent's to make. |
| B. Workflow: extract fields → deterministic eligibility rules on extracted fields → rubric scoring with citations → panel summary | Predictable cost; each step testable; eligibility logic stays deterministic and explainable; Claude does what it is good at (extraction, rubric judgement with evidence). |
| C. Single long-context call per application producing everything at once | Simple, but harder to evaluate per step, harder to pinpoint failures, and mixes deterministic logic into a prompt. |
| D. Fine-tune a classifier instead | Needs labelled data that does not exist; does not produce explanations or summaries. |

**Recommended decision: B.** The steps are known in advance, the criteria are stable and explanation is
required. Keep eligibility rules in code operating on extracted, schema-validated fields; use Claude for
extraction and evidence-cited rubric scoring; the panel remains the decision-maker. Run scoring through the
Message Batches API because results are not needed in real time.

---

## Scenario 2 — Research synthesis at scale: one agent or many?

**Context.** *Fabrikam Pharma's* competitive-intelligence team wants weekly briefings that synthesise
hundreds of public filings, trial registries and press releases across 30 competitors.

**Constraints.** Coverage matters more than speed; sources must be cited; the team accepts higher cost for
quality; a single agent previously ran out of useful context halfway through.

| Option | Analysis |
|---|---|
| A. One agent with a larger effort setting | Does not fix context exhaustion from reading-heavy work; quality degrades late in the run. |
| B. Orchestrator–workers: lead agent plans by competitor, workers (cheaper tier) read and return condensed, cited findings, lead synthesises | Parallel, protects the lead's context, cost controlled with a cheaper worker tier; needs clear task specs and output schema per worker. |
| C. Fixed pipeline per competitor with no orchestrator | Works if the plan never changes; misses cross-competitor themes and adaptive follow-ups. |
| D. Put all documents in one 1M-token request | May exceed the window, is expensive per run and dilutes attention; no follow-up research. |

**Recommended decision: B**, with workers returning a structured summary (claim, source ID, quote, date) and
a budget per worker. Evaluate worker tier choice on a sample week before committing; keep the orchestrator on
a stronger tier.

---

## Scenario 3 — Procurement assistant: where should approval live?

**Context.** *Contoso Manufacturing* wants an assistant that helps buyers raise purchase orders by reading
supplier quotes (PDFs, emails), comparing them with contracts and creating the PO in the ERP.

**Constraints.** POs above USD 10,000 need manager approval under existing policy; supplier emails are
external content; ERP actions are auditable.

| Option | Analysis |
|---|---|
| A. Instruct the model in the system prompt to ask for approval above USD 10,000 | Advisory only; injection or error could bypass it. |
| B. Agent drafts the PO; a deterministic policy service enforces thresholds and routes to the existing approval workflow; the ERP write uses the buyer's identity | Enforcement outside the model; existing control reused; audit trail intact. |
| C. Require human approval for every PO | Safe but removes most of the value for low-value orders. |
| D. Let the agent create POs and review a weekly sample | Detective, not preventive, for high-value orders. |

**Recommended decision: B.** Put the threshold in code and reuse the organisation's approval workflow. Treat
quote and email content as untrusted. The model proposes; policy and humans dispose.

---

## Scenario 4 — Justifying an AI programme to a CFO

**Context.** *Adventure Works'* CFO asks whether a proposed claims-assist programme is worth funding. The
pilot reduced handling time by 35% on a 200-case sample.

**Constraints.** The CFO wants a cost-benefit view with risk; the pilot used the most capable model at high
effort; production volume is 50 times the pilot.

| Option | Analysis |
|---|---|
| A. Present the 35% time saving multiplied by headcount cost | Ignores run costs, review effort, rework, error costs and the representativeness of the sample. |
| B. Present cost per completed claim (tokens, infrastructure, human review, rework) versus baseline, with sensitivity ranges and an optimisation plan (caching, effort tuning, routing) validated on a larger eval set | Defensible, shows levers, makes uncertainty explicit. |
| C. Ask for funding for a bigger pilot without numbers | Delays the decision without informing it. |
| D. Present industry benchmark ROI figures | Not specific to the organisation; unverifiable. |

**Recommended decision: B**, framed as options (fund full rollout, fund a phased rollout with gates, or stop)
with the decision needed and the metrics that will trigger each gate.

---

## Scenario 5 — Model choice for a field-service copilot

**Context.** *Litware Utilities* technicians use a mobile copilot to diagnose equipment faults from
descriptions and photos. Connectivity is often poor; answers must arrive quickly; wrong advice could cause
safety incidents.

**Constraints.** p95 under 6 seconds; high-risk procedures must cite the manual; volume is 20,000 queries a day.

| Option | Analysis |
|---|---|
| A. Most capable model at maximum effort for everything | Likely misses the latency target and is costly at this volume. |
| B. Smallest model for everything | Fast and cheap but may fail on complex diagnostics. |
| C. Route by classified complexity: fast tier at low effort for lookups; stronger tier for diagnostics; safety-critical procedures always retrieved and cited, with a "contact supervisor" path | Matches capability to need; latency bounded; safety handled by grounding and escalation, not just model size. |
| D. Choose by public benchmark rankings | Benchmarks do not reflect this domain or the latency constraint. |

**Recommended decision: C**, validated with an eval sweep across tiers and effort levels. Also measure the
simpler alternative of one capable tier at low effort, because it avoids routing errors and split caches.
Stream responses to improve perceived latency.

---

## Scenario 6 — Guardrails for an HR policy assistant

**Context.** *Proseware's* HR assistant answers employee policy questions. Testers found it can be talked into
revealing other employees' salary bands by role-play prompts.

**Constraints.** The assistant has a tool that queries the HR system.

| Option | Analysis |
|---|---|
| A. Add stronger wording to the system prompt | Helps marginally; role-play and injection will continue to find gaps. |
| B. Scope the HR tool to the requesting employee's own records using their identity; remove access to others' compensation entirely; add output checks for compensation data about other people | Removes the capability rather than asking the model to withhold it. |
| C. Add a keyword filter on "salary" | Easy to evade and blocks legitimate questions about one's own salary. |
| D. Disable the assistant | Removes value; the problem is solvable. |

**Recommended decision: B**, plus adversarial test cases in the eval suite. The general rule: if the model
must not disclose data, the model should not be able to retrieve it.

---

## Scenario 7 — 140 tools from six MCP servers

**Context.** *Wide World Importers'* operations agent connects to six MCP servers exposing 140 tools. Tool
selection errors are frequent and requests are slow and expensive.

| Option | Analysis |
|---|---|
| A. Switch to a larger model | May improve selection slightly; does not fix context bloat or cost. |
| B. Remove unused tools, consolidate overlapping ones, split read/write, and use tool search with deferred loading for the long tail; give sub-agents per domain their own small tool sets | Reduces tokens and confusion; scales; keeps rarely used tools reachable. |
| C. Put a long "tool usage guide" in the system prompt | Adds more context to an already crowded window. |
| D. Hard-code a fixed sequence of tool calls | Loses the flexibility the agent was built for. |

**Recommended decision: B.** Audit tool usage from traces first to find dead and overlapping tools. Keep at
least one tool non-deferred and never defer the search tool itself.

---

## Scenario 8 — Shared service account behind a knowledge agent

**Context.** *Woodgrove Bank's* internal knowledge agent searches SharePoint-style document libraries using
a single service account with read access to all libraries. Employees in one department received excerpts
from another department's restricted documents.

| Option | Analysis |
|---|---|
| A. Tell the model not to share restricted content | The model cannot know the requester's entitlements reliably. |
| B. Index ACL metadata and filter retrieval by the requester's group memberships at query time, or query the source with the user's delegated token | Enforces entitlements before content reaches the model. |
| C. Separate indexes per department | Works for coarse boundaries but breaks for cross-department users and fine-grained permissions. |
| D. Post-filter answers with a classifier | Content has already been exposed to the model and may leak through paraphrase. |

**Recommended decision: B** (delegated user tokens where the source supports them, ACL-filtered retrieval
otherwise), with periodic entitlement-sync checks and an access-violation test set.

---

## Scenario 9 — Product-catalogue search with SKUs

**Context.** *Tailspin Outfitters'* staff assistant answers product questions over 80,000 catalogue entries.
Most queries contain SKUs or model numbers; dense-vector search returns similar but wrong products.

| Option | Analysis |
|---|---|
| A. Larger chunks | Does not fix identifier matching. |
| B. Hybrid retrieval (BM25 plus dense) with SKU and attribute metadata filters, record-level chunks, and re-ranking; exact SKU lookups through a catalogue tool | Matches the data shape (structured records) and query pattern (identifiers). |
| C. Load the whole catalogue into context | Far too large and expensive per request. |
| D. Fine-tune the embedding model | Expensive and slower to deliver than adding lexical retrieval; may still miss exact identifiers. |

**Recommended decision: B.** Route queries with an exact identifier straight to a structured lookup tool; use
hybrid retrieval for descriptive queries. Track recall@k separately for identifier and descriptive queries.

---

## Scenario 10 — Exposing a pricing engine: MCP, API or A2A?

**Context.** *Margie's Travel* has a pricing engine. Three consumers want it: a single internal web app's
assistant, Claude Code for the pricing team, and a partner's booking agent operated by another company.

| Option | Analysis |
|---|---|
| A. One MCP server for all three | Good for the internal multi-host need; exposing raw pricing tools to an external organisation's agent shares too much and complicates identity. |
| B. Direct tools for the web app; an internal MCP server for Claude Code and future internal hosts; an agent-to-agent interface (task-level contract: "quote this itinerary") for the partner | Each mechanism matches its consumer's reuse and trust needs. |
| C. A public REST API for everyone, wrapped by each consumer | Workable but forgoes MCP's discovery for internal hosts and leaves the partner integrating at too low a level. |
| D. Give the partner VPN access to the internal MCP server | Crosses a trust boundary with internal tool granularity. |

**Recommended decision: B.** If the web app's needs grow or more hosts appear, it can move to the MCP server
later. Document contracts, versioning and identity for the A2A interface.

---

## Scenario 11 — Agent traces at 2 million tasks a month

**Context.** *Fourth Coffee's* order-exception agent handles 2 million tasks a month. Engineers cannot tell why
certain tasks take 15 turns; storing full transcripts for everything is costly and includes customer data.

| Option | Analysis |
|---|---|
| A. Log everything forever | Cost and privacy risk; no better analysis. |
| B. OpenTelemetry traces for every task with span metadata (model, effort, tokens, latency, tool name, `stop_reason`, prompt version), redacted payloads; full payload capture for a stratified sample and for anomalies (high turn counts, errors); dashboards and alerts on turns per task | Complete metrics, affordable detail, privacy controls. |
| C. Sample 1% of tasks with full payloads only | Misses rare failure patterns and gives no complete metrics. |
| D. Rely on the provider console | Useful for usage and cost, but lacks your task, tool and business context. |

**Recommended decision: B**, plus a weekly review of the slowest trajectories feeding new eval cases.

---

## Scenario 12 — Upgrading the model behind a contract-extraction service

**Context.** *Litware Legal Services* runs a contract-extraction service on an older model that has a
published retirement date. A newer model is available.

| Option | Analysis |
|---|---|
| A. Change the model ID and deploy | Request parameters may now be rejected (sampling parameters, prefill, forced tool choice, `budget_tokens`), behaviour and token counts change, and there is no evidence of quality. |
| B. Read migration notes, update request shapes (structured outputs, adaptive thinking, effort), re-baseline tokens with the token-counting endpoint, run the full eval on both models, tune prompts and effort, shadow then canary with rollback, update the ADR | Controlled, evidence-based, reversible. |
| C. Wait until retirement forces the change | Risks an outage and a rushed migration. |
| D. Switch to a different provider | Bigger change with more risk; not motivated by evidence. |

**Recommended decision: B**, scheduled well before the retirement date.

---

## Scenario 13 — A hallucination complaint from a regional manager

**Context.** *Contoso Retail's* store-policy assistant told a store manager that a returns policy allowed 60
days; the policy says 30. The manager escalates to the CIO.

| Option | Analysis |
|---|---|
| A. Switch to the most capable model | May not fix a retrieval or source problem. |
| B. Reproduce: inspect the retrieved chunks and the prompt for this query; classify the failure (retrieval miss, wrong or outdated source, generation error); add the case and close variants to the eval set; fix the identified cause; communicate findings and the fix to the manager and CIO | Root-cause driven; prevents regressions; keeps stakeholders informed. |
| C. Add "never make mistakes about returns" to the prompt | Not a fix. |
| D. Remove returns questions from scope | Overreaction without diagnosis. |

**Recommended decision: B.** A typical root cause in a case like this is chunking that dropped heading
context, so a 60-day rule for a different product category (for example, a membership tier) was retrieved
and presented as the general rule. The fix then belongs in chunking and metadata, not in the model choice.

---

## Scenario 14 — EU personal data and US-hosted logging

**Context.** *Fabrikam Bank EU* processes EU customers' messages with Claude. The central observability
platform is in the US and stores full prompts for 13 months.

| Option | Analysis |
|---|---|
| A. Keep as is because the provider is compliant | Provider compliance does not cover your logging choices. |
| B. Redact or pseudonymise personal data before logs leave the EU region, keep full payloads (if needed at all) in an EU store with short retention and restricted access, document transfers and update the DPIA | Applies minimisation, storage limitation and transfer controls. |
| C. Turn off all logging | Breaks auditability and operations. |
| D. Encrypt logs in the US store | Encryption helps confidentiality but does not address minimisation, retention or transfer obligations. |

**Recommended decision: B**, with legal review. Also confirm the processing region and data-retention
configuration of the model platform itself.

---

## Scenario 15 — Fairness in a tenant-screening summary tool

**Context.** *Blue Yonder Property* wants Claude to summarise rental applications for leasing agents.

| Option | Analysis |
|---|---|
| A. Let Claude recommend approve or decline | Consequential decision about people in a regulated area; high fairness and legal risk. |
| B. Claude produces a factual, structured summary of verified documents with protected and irrelevant attributes excluded; agents decide using the existing criteria; counterfactual fairness tests and slice evals; applicants informed of AI assistance and offered human contact | Keeps humans accountable; measurable fairness; transparent. |
| C. Use Claude only for applicants with incomplete files | Inconsistent treatment; still biased if unmeasured. |
| D. Do not tell applicants AI is used | Fails transparency expectations and may breach regulation. |

**Recommended decision: B**, with legal review of the jurisdiction's tenant-screening and AI rules.

---

## Scenario 16 — Rolling Claude Code out to a regulated engineering org

**Context.** *Woodgrove Bank's* 300 engineers want Claude Code. Security requires that no production secrets
are read, all tool use is auditable, and production deployments remain human-approved.

| Option | Analysis |
|---|---|
| A. Each engineer configures their own settings | Inconsistent and unenforceable. |
| B. Managed settings with deny rules for secrets and credential paths, allowed models and telemetry export; a template repository with shared project settings, hooks that block production-targeting commands, `ask` rules on push; a curated plugin with review subagents and skills; read-only MCP servers with per-user auth; phased rollout with metrics | Central policy plus team flexibility; enforcement by configuration and hooks. |
| C. Ban Claude Code | Pushes engineers to unmanaged tools. |
| D. Allow bypass mode for speed in CI | Removes the controls security requires. |

**Recommended decision: B.** Remember that managed settings take precedence over everything else and that
shared-project allow rules wait for workspace trust while deny rules apply immediately.

---

Further practice: [practical exercises](practical-exercises.md), [common misconceptions](common-misconceptions.md),
and the domain study guides ([1](study-guide/domain-1.md), [2](study-guide/domain-2.md),
[3](study-guide/domain-3.md), [4](study-guide/domain-4.md), [5](study-guide/domain-5.md),
[6](study-guide/domain-6.md), [7](study-guide/domain-7.md)).
