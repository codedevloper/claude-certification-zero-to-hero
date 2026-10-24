# CCAR-P Practical Exercises

> Architect-level exercises with concrete deliverables. Each one maps to CCAR-P objectives in
> [`registry.yaml`](../registry.yaml). All organisations and data are fictional. Do them in writing: the act
> of producing the artefact is what builds exam-ready judgement.

Work in a folder of your own (for example `my-ccar-p-work/`). Where an exercise uses a lab, run the lab in mock
mode first (`CLAUDE_LAB_MODE=mock`, the default) and switch to live mode only when you want real numbers.

> **Cost:** requires API credits (live mode). Every exercise can be completed in mock mode; live runs are
> optional and only needed for real latency, token and quality figures.

| # | Exercise | Domain(s) | Deliverable | Time |
|---|---|---|---|---|
| 1 | Pattern selection ADR | 1, 6 | ADR | 90 min |
| 2 | Context and model plan | 2 | Context budget and model-routing table | 60 min |
| 3 | Agent threat model | 3, 5 | Threat model and control matrix | 2 h |
| 4 | Evaluation plan | 4 | Eval plan with datasets, graders and release gate | 2 h |
| 5 | Claude Code team configuration | 7 | Settings, hooks, CLAUDE.md, MCP config | 90 min |
| 6 | RAG design | 3 | RAG design document | 2 h |
| 7 | Integration mechanism review | 3 | Options analysis | 60 min |
| 8 | Compliance control mapping | 5 | Control matrix | 90 min |
| 9 | Stakeholder pack and SLOs | 6 | One-page brief and SLO table | 60 min |
| 10 | Operational debugging drill | 4, 7 | Incident timeline and fix plan | 60 min |

---

## Exercise 1 — Pattern selection ADR (CCAR-P-1.1, 1.3, 1.5, 6.2)

**Scenario.** *Litware Legal Services* reviews incoming commercial leases for 14 clause types (renewal,
indemnity, assignment, and so on). Paralegals spend about 90 minutes per lease. Leases are 20–120 pages. The
firm wants a first-pass review that flags non-standard clauses against its playbook, with a partner signing off.

**Tasks.**

1. Write a value hypothesis with a baseline and target.
2. Decompose the work into steps; mark which are deterministic, which need Claude and which need a human.
3. Compare three options: single long-context call, workflow (extract → compare to playbook → draft memo), and
   orchestrator–workers (one worker per clause family).
4. Choose one and write an ADR using the template in the [Domain 6 guide](study-guide/domain-6.md).

**Deliverable.** `adr-001-lease-review-pattern.md` with context, options (with cost, latency, quality and risk
for each), decision, consequences and a review date.

**Success criteria.** The decision is justified by the constraints (document length, need for clause-level
traceability, partner sign-off); the ADR names how the decision will be validated (which eval) and what would
cause it to be revisited.

**Hint.** Clause-level structured output with page citations makes the partner's review faster and makes the
system evaluable per clause type.

---

## Exercise 2 — Context and model plan (CCAR-P-2.1, 2.2, 2.4, 2.5)

**Scenario.** *Adventure Works Travel* runs a booking-support assistant: 40,000 conversations a day, average
8 turns, a fare-rules and itinerary-policy section of roughly 15,000 tokens, 12 tools, per-customer itinerary
data and a requirement for p95 time to first token under 2 seconds.

**Tasks.**

1. Produce a context budget per request (tools, system, retrieved policy, history, output).
2. Propose a caching layout (what is frozen, where breakpoints go, what is volatile) and list three silent
   invalidators you will guard against.
3. Propose model and effort per route (greeting/FAQ, booking change, complaint) with a test plan to confirm.
4. Decide which of the 12 tools should be deferred behind tool search, and which instructions should become a
   Skill.

**Deliverable.** A two-page plan with a table for each task. Use
[Lab 05](../../19-hands-on-labs/lab-05-context-management/README.md) and
[Lab 17](../../19-hands-on-labs/lab-17-cost-optimisation/README.md) to check token and cache figures.

**Success criteria.** Volatile data is after the last breakpoint; per-route choices are tied to eval
evidence; the plan uses current API rules (no sampling parameters, no prefill, adaptive thinking with
`effort`).

---

## Exercise 3 — Agent threat model (CCAR-P-3.1, 3.2, 5.1, 5.2)

**Scenario.** *Proseware IT* plans an internal IT-helpdesk agent that reads tickets and email, searches the
knowledge base, resets passwords through an identity-management API, and can add users to groups.

**Tasks.**

1. Draw a data-flow diagram (Mermaid) with trust boundaries: requester, email content, agent host, Claude
   API, MCP servers, identity system.
2. Apply STRIDE plus LLM-specific threats (direct and indirect prompt injection, excessive agency,
   exfiltration through tool arguments, insecure output handling, supply chain).
3. For each threat, rate likelihood and impact, choose controls and name an owner.
4. Identify the capability-bloat and authorisation gaps in the proposed design and redesign the tool set.

**Deliverable.** `threat-model-helpdesk-agent.md` containing the diagram, a threat table (ID, threat,
component, likelihood, impact, controls, residual risk, owner) and the redesigned tool list.

**Success criteria.** Group membership changes and password resets are gated (approval or verified-identity
flow), the agent acts with the requester's delegated rights or a narrowly scoped service identity, email
content is treated as untrusted, and logs are redacted. Validate your injection controls with
[Lab 14](../../19-hands-on-labs/lab-14-prompt-injection-testing/README.md).

---

## Exercise 4 — Evaluation plan (CCAR-P-4.1, 4.2, 4.3, 4.4)

**Scenario.** *Fourth Coffee Finance* wants to replace a manual invoice-coding process (assigning general
ledger codes and cost centres to supplier invoices) with Claude. Current accuracy by staff is about 96%.

**Tasks.**

1. Define primary, secondary and guardrail metrics.
2. Design the dataset: sources, size, stratification, labelling guidelines, splits, versioning, refresh.
3. Choose graders per metric (code, LLM judge, human) and describe how you will calibrate the judge.
4. Define the release gate and an online rollout (shadow, canary, A/B) with rollback triggers.
5. Write a diagnosis playbook: for each likely failure, the first diagnostic and the likely fix.

**Deliverable.** `eval-plan-invoice-coding.md`. Build a small version of the harness with
[Lab 16](../../19-hands-on-labs/lab-16-evaluation-framework/README.md).

**Success criteria.** The test set is held out; cost per completed invoice and p95 latency sit beside
accuracy; there is at least one security metric (for example, invoices with embedded instructions must not
change coding behaviour).

---

## Exercise 5 — Claude Code team configuration (CCAR-P-7.1, 7.2, 3.2)

**Scenario.** *Blue Yonder Airlines'* platform team (25 engineers) maintains Terraform and Python services. They
want Claude Code to run tests and linters freely, never read credentials, never apply Terraform, and to query
the internal runbook wiki.

**Tasks.**

1. Write a shared `.claude/settings.json` with `allow`, `ask` and `deny` rules and at least one hook.
2. Write the hook script (for example, block `terraform apply` and any command referencing the production
   workspace) and explain why it is a hook and not a CLAUDE.md rule.
3. Write a concise `CLAUDE.md` (under 80 lines) with build, test and convention guidance.
4. Write a project `.mcp.json` entry for a read-only wiki MCP server, with credentials from environment
   variables.
5. List what belongs in organisation-managed settings instead.

**Deliverable.** A folder with the four files plus a README explaining each choice. Exercise it with
[Lab 10](../../19-hands-on-labs/lab-10-claude-code-workflows/README.md).

**Success criteria.** No secrets in any file; deny rules cover `.env*` and credential paths; destructive
infrastructure commands are blocked by a hook and an `ask` or `deny` rule; precedence is explained correctly
(managed over everything; local over shared project over user).

---

## Exercise 6 — RAG design (CCAR-P-3.5, 3.6, 4.4, 5.4)

**Scenario.** *Woodgrove Bank's* operations staff need answers from 25,000 procedure documents (policies,
forms, product sheets, rate tables), many restricted to specific departments. Queries mix natural language
with product codes, and some questions need the current rate rather than a document.

**Tasks.**

1. Choose chunking per document type (policies, forms, tables) and justify.
2. Specify metadata and indexing (hybrid search, ACL filtering, versioning, deletion propagation).
3. Specify the retrieval flow (query rewriting, top-k, re-ranking, citation requirements, "not found" path).
4. Decide whether any part is better served by long context or by a live tool.
5. Define RAG-specific metrics: retrieval recall@k, citation precision, faithfulness, answer correctness.

**Deliverable.** `rag-design-ops-procedures.md` with a Mermaid pipeline diagram and decision tables. Prototype
with [Lab 11](../../19-hands-on-labs/lab-11-rag-pipeline/README.md).

**Success criteria.** Permissions are enforced at retrieval time with the caller's identity; current rates
come from a live tool rather than the index; tables are not chunked as prose; the design distinguishes
retrieval failures from generation failures in its metrics.

---

## Exercise 7 — Integration mechanism review (CCAR-P-3.7, 3.8)

**Scenario.** *Margie's Travel* has three integration needs: (a) a single web app needs to call a pricing
endpoint; (b) the CRM must be usable from Claude Code, a sales assistant and Claude apps; (c) a partner airline
offers a rebooking agent that owns its own policies and data.

**Tasks.** For each need, evaluate direct tool, CLI, MCP and agent-to-agent; choose one; describe identity and
authorisation; estimate context cost; describe how tools are discovered (all loaded versus progressive).

**Deliverable.** A one-page options table with decisions and rationale.

**Success criteria.** (a) avoids unnecessary protocol overhead; (b) uses a reusable protocol with per-user auth;
(c) delegates a task across an organisational boundary with an explicit contract instead of exposing raw tools.

---

## Exercise 8 — Compliance control mapping (CCAR-P-5.4, 5.5, 5.3)

**Scenario.** *Contoso Health* (EU and US operations) plans a patient-message triage assistant.

**Tasks.** Build a control matrix mapping obligations (GDPR minimisation, data-subject rights, transfers, DPIA;
HIPAA BAA, minimum necessary, audit controls) to architecture controls, evidence and owners. Add a fairness
section (language slices, counterfactual tests) and a HITL design for urgent messages.

**Deliverable.** `control-matrix-triage.md`. Use
[Lab 15](../../19-hands-on-labs/lab-15-sensitive-data-protection/README.md) for redaction patterns.

**Success criteria.** Every obligation has a control and evidence; unverifiable vendor-coverage claims are
labelled for confirmation with legal and the vendor; urgent cases never wait for model output alone.

---

## Exercise 9 — Stakeholder pack and SLOs (CCAR-P-6.1, 6.3, 6.4)

**Scenario.** Continue Exercise 4. The CFO wants a launch date; the controller worries about audit; the AP team
worries about job changes.

**Tasks.** Write a one-page executive brief (outcome, options, recommendation, decision needed), an SLO table
(availability, latency, quality, cost, with measurement method), a RACI for operations and a feedback-loop
description.

**Deliverable.** `stakeholder-pack-invoice-coding.md`.

**Success criteria.** Quality is stated as a measured rate with a test-set reference; each audience's concern
is addressed explicitly; ownership after handoff is unambiguous.

---

## Exercise 10 — Operational debugging drill (CCAR-P-4.4, 4.6, 7.3)

**Scenario.** After a release, a summarisation service shows: cost up 70%, `cache_read_input_tokens` near zero,
p95 latency up 40%, and 3% of responses ending with `stop_reason: "max_tokens"`.

**Tasks.** Write the incident timeline, hypotheses ranked by likelihood, the diagnostic for each, and the fix.
Then describe how you would use headless Claude Code with read-only log access to speed the investigation, and
what you would add to the eval suite and dashboards to catch this earlier.

**Deliverable.** `incident-2026-xx-summary-cost.md`. Practise with
[Lab 18](../../19-hands-on-labs/lab-18-reliability-engineering/README.md) and
[Lab 19](../../19-hands-on-labs/lab-19-observability/README.md).

**Success criteria.** You identify a likely cache invalidator introduced in the release (for example a
timestamp added to the system prompt or a reordered tool list), connect it to both cost and latency, handle the
truncation separately (right-size `max_tokens` or reduce verbosity), and add alerts on cache hit ratio and
`stop_reason` mix.

---

## Self-review rubric

Score each deliverable 0–2 on each line:

| Criterion | 0 | 1 | 2 |
|---|---|---|---|
| Constraint fit | Ignores stated constraints | Addresses some | Every choice traced to a constraint |
| Options analysis | Single answer | Options without consequences | Options with cost, latency, quality, risk |
| Security and governance | Missing | Generic | Specific controls with owners |
| Measurability | No metrics | Metrics without method | Metrics, method, thresholds |
| Accuracy of facts | Outdated API or product facts | Minor errors | Current and dated |

A total of 8 or more out of 10 per deliverable indicates exam-level judgement on that topic. See also the
[decision scenarios](decision-scenarios.md) and the [readiness assessment](readiness-assessment.md).
