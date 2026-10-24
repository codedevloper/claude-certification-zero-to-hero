# Lab 20: Secure Enterprise AI Architecture with an AI Gateway

> **Level:** Advanced · **Time:** ~90 min · **Cost:** free in mock mode; live mode uses API credits · **Exam relevance:** CCAR-P 5.1, CCAR-P 3.2, CCAR-P 3.1, CCAR-P 1.2, CCAR-P 5.3, CCAR-P 5.4, CCAR-P 6.4

## Objective

In labs 13 to 19 you built individual controls: approvals, injection testing, data protection, evaluation, cost limits, reliability and observability. In a real organisation those controls should not be copied into every application that calls Claude. They belong in one place that every request passes through: an **AI gateway**.

In this lab you run a reference AI gateway, written in about 400 lines of standard-library Python, in front of the Claude API for three fictional tenants. You will:

1. Authenticate callers with a signed bearer token (a stub of what your identity provider would issue) and reject forged or expired tokens with a constant-time comparison.
2. Apply **per-tenant policy** from a JSON file: allowed models, a `max_tokens` cap, effort level, a tool allow-list, tools that need human approval, data-classification rules and a daily token budget.
3. Enforce **rate limits** with a token bucket per tenant.
4. **Classify and redact** personal data before anything leaves the gateway, or block the request when policy says a data class must never be sent.
5. **Screen for prompt injection** in the user's prompt (direct) and in attached documents (indirect), and **spotlight** untrusted documents with keyed delimiters.
6. Offer the model only allow-listed tools, then **check the tools it asks for**. Unknown tools are blocked and high-risk tools are held for approval.
7. **Check the output** for system-prompt leakage (a canary string) and for personal data.
8. Write a **hash-chained audit log** that records every decision without storing raw prompts, and prove that tampering is detected.
9. Read and critique a **threat model** for the design.

## Level, time and cost

| Item | Value |
|---|---|
| Level | Advanced |
| Time | About 90 minutes: 20 to run and read, the rest for the exercises and threat model |
| Mock mode | Free, offline, deterministic, under one second |
| Live mode | 16 requests arrive at the gateway, but only 8 reach the API. The rest are stopped by gateway controls first |

> **Cost:** requires API credits (live mode).

In live mode, eight upstream calls are made: two to Claude Haiku 5.5, two to Claude Sonnet 5.5 and four to Claude Opus 5.5. Each prompt is a few hundred tokens and `max_tokens` is capped by tenant policy. Expect a few thousand tokens in total, typically well under USD 0.20 per run as of 2026-10-24 (Opus 5.5 is USD 4 / USD 20 per million input/output tokens; see the [pricing page](https://platform.claude.com/docs/en/about-claude/pricing)). Thinking tokens are billed as output.

Stopping a request at the gateway costs nothing upstream. That is one of the business arguments for putting cheap checks in front of an expensive model.

## Prerequisites

- Python 3.10 or later.
- Labs 07 and 08 (API integration and tool use).
- Strongly recommended, because this lab combines them: [Lab 13](../lab-13-human-in-the-loop/README.md), [Lab 14](../lab-14-prompt-injection-testing/README.md), [Lab 15](../lab-15-sensitive-data-protection/README.md), [Lab 17](../lab-17-cost-optimisation/README.md), [Lab 18](../lab-18-reliability-engineering/README.md) and [Lab 19](../lab-19-observability/README.md).
- Familiarity with the STRIDE threat categories (Spoofing, Tampering, Repudiation, Information disclosure, Denial of service, Elevation of privilege) helps with the threat model.

## Architecture

```mermaid
flowchart LR
    subgraph Clients["Internal client apps (per tenant)"]
        A1[Contoso Health<br/>scheduling app]
        A2[Northwind Lending<br/>servicing console]
        A3[Acme Logistics<br/>depot tool]
    end
    IdP[(Identity provider<br/>stub: HMAC tokens)] -. issues token .-> Clients
    subgraph GW["AI gateway (gateway.py)"]
        direction TB
        S1[1 AuthN<br/>signature + expiry] --> S2[2 Rate limit<br/>token bucket]
        S2 --> S3[3 Tenant policy<br/>model, max_tokens]
        S3 --> S4[4 Data classification<br/>block or redact]
        S4 --> S5[5 Injection screen<br/>+ spotlighting]
        S5 --> S6[6 Token budget<br/>reserve worst case]
        S6 --> S7[7 Upstream call<br/>allow-listed tools only]
        S7 --> S8[8 stop_reason +<br/>tool allow-list / approval]
        S8 --> S9[9 Output checks<br/>canary, PII]
    end
    Clients -->|bearer token + request| S1
    S7 <-->|HTTPS| API[(Claude API)]
    S8 -->|high-risk tool| Q[Approval queue<br/>lab 13]
    GW -->|every decision| AU[(Hash-chained<br/>audit.jsonl)]
    S9 -->|response or block| Clients
    P[(tenants.json<br/>policy)] --> S3
```

The order of the stages is deliberate:

- **Cheap and certain checks first.** Authentication, rate limiting and model policy need no content inspection, so they run before the gateway reads the prompt. A forged token never costs a regular-expression pass, and a flood of requests is stopped before it reaches the expensive stages.
- **Data handling before injection screening.** Personal data is redacted before the injection screen and before anything is logged or hashed, so nothing downstream ever sees the raw values.
- **Budget reservation just before the call.** The gateway reserves the worst case (estimated input plus `max_tokens`) so a tenant cannot exceed its budget with one large request, then charges the real usage afterwards.
- **Response checks after the call.** The model's output is untrusted too. `stop_reason` is checked first, then tool requests, then text.
- **Audit at every exit.** Every return path goes through `_finish()`, so denials are recorded as reliably as successes.

### Threat model

Assets: tenant data in prompts and documents, the Claude API credential held by the gateway, the gateway's system prompt and policy, tool side effects (such as changing a loan's due date), the token budget (money), and the audit trail.

Trust boundaries: client app to gateway (authenticated, but the content is untrusted), third-party documents to gateway (untrusted), gateway to Claude API (trusted transport, but the output is untrusted), and gateway to tool executors (the gateway returns tool requests to the client and never executes them itself).

| # | STRIDE | Threat | OWASP LLM Top 10 (2025) | Gateway control in this lab | Residual risk and next step |
|---|---|---|---|---|---|
| T1 | Spoofing | Caller forges or replays a token to act as another tenant | n/a | HMAC signature, constant-time compare, expiry check; tenant comes only from signed claims | Replay within token lifetime; use short-lived OIDC tokens or mTLS from a real identity provider |
| T2 | Tampering | User or document text overrides the system prompt | LLM01 Prompt Injection | Heuristic direct and indirect screening; spotlighting with keyed boundaries; spoofed tags neutralised; security rules in the system prompt | Heuristics miss paraphrased or encoded attacks; add a classifier model and keep tools least-privilege so a miss has limited impact (lab 14) |
| T3 | Information disclosure | Personal data sent to the model or written to logs | LLM02 Sensitive Information Disclosure | Per-tenant block or redact before the call; secrets always blocked; audit stores counts and hashes only | Regex misses names and free text; use a dedicated detection service and contractual data controls (lab 15) |
| T4 | Information disclosure | Model reveals the system prompt or policy | LLM07 System Prompt Leakage | Canary in the system prompt; output blocked if the canary appears | Paraphrased leaks are not caught; keep secrets out of prompts entirely |
| T5 | Elevation of privilege | Model calls a destructive or out-of-scope tool | LLM06 Excessive Agency | Only allow-listed tools are sent; tool requests re-checked against the allow-list; risky tools held for approval | Argument-level abuse of an allowed tool; validate arguments and scope per user (lab 13) |
| T6 | Tampering | Unsafe output used directly by a client (for example rendered as HTML or run as a command) | LLM05 Improper Output Handling | Output PII redaction; tool inputs returned as structured data rather than text | Clients must still escape and validate output; document this in the integration guide |
| T7 | Denial of service | One tenant floods the gateway or runs up cost | LLM10 Unbounded Consumption | Token bucket per tenant; `max_tokens` cap; daily token budget with worst-case reservation | In-memory state resets on restart and is per instance; move counters to a shared store such as Redis |
| T8 | Repudiation | Insider edits records to hide a decision | n/a | SHA-256 hash chain; verification detects the first edited record | An attacker who can rewrite the whole file can rebuild the chain; anchor the head hash externally or use write-once storage |
| T9 | Information disclosure | Audit hashes reveal short prompts by dictionary guessing | LLM02 | Hashes are of redacted text | Use a keyed HMAC instead of a plain hash for low-entropy fields |
| T10 | Spoofing / supply chain | Gateway calls an impostor endpoint or a tampered SDK | LLM03 Supply Chain | Official SDK, HTTPS, credential only in the gateway | Pin and verify dependencies; restrict egress to the API host |

OWASP category names are from the [OWASP Top 10 for LLM Applications 2025](https://genai.owasp.org/llm-top-10/), checked on 2026-10-24.

### How this lab ties together labs 13 to 19

| Lab | Control | Where it lives in the gateway |
|---|---|---|
| [13 Human-in-the-loop](../lab-13-human-in-the-loop/README.md) | Risk-tiered actions and approvals | `approval_required_tools` in policy; `HOLD_APPROVAL` decision; `approval_queue` |
| [14 Prompt injection testing](../lab-14-prompt-injection-testing/README.md) | Direct versus indirect injection, spotlighting | `injection_score()` with separate thresholds; `spotlight()` with keyed boundaries; canary check |
| [15 Sensitive data protection](../lab-15-sensitive-data-protection/README.md) | Detection, Luhn check, redaction | `find_sensitive()`, `apply_data_rules()` with per-tenant block or redact rules, output redaction |
| [16 Evaluation framework](../lab-16-evaluation-framework/README.md) | Measuring quality and safety | `data/requests.json` with an `expect` column is a small security regression suite; run it on every policy change |
| [17 Cost optimisation](../lab-17-cost-optimisation/README.md) | Model routing and spend control | `allowed_models`, `default_model`, `max_tokens_cap`, `effort` and `daily_token_budget` per tenant |
| [18 Reliability engineering](../lab-18-reliability-engineering/README.md) | Retries, circuit breakers, `stop_reason` | `stop_reason` handling (`refusal`, `max_tokens`); add lab 18's retry wrapper around the upstream call |
| [19 Observability](../lab-19-observability/README.md) | Logs, metrics, traces, redaction in logs | Audit log with request IDs and usage; add lab 19's spans around each pipeline stage |

## Setup

Mock mode needs nothing beyond Python 3.10+. Run every command from the repository root.

For live mode:

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r 19-hands-on-labs/requirements.txt
export ANTHROPIC_API_KEY="sk-ant-..."                         # see ../.env.example
export LAB20_GATEWAY_SIGNING_KEY="$(python -c 'import secrets;print(secrets.token_hex(32))')"   # optional
```

See [`../requirements.txt`](../requirements.txt), [`../.env.example`](../.env.example) and the shared helper [`../common/claude_lab.py`](../common/claude_lab.py). If `LAB20_GATEWAY_SIGNING_KEY` is unset in live mode, a random key is generated for the run. Mock mode uses a fixed, clearly fake key so the output is reproducible.

The audit log is written to `<LAB_OUTPUT_DIR or system temp>/claude-labs/lab-20/audit.jsonl`, outside the repository.

## Walkthrough of the sample code

The lab has two Python files:

- [`gateway.py`](gateway.py) holds the reusable gateway: clock, token authority, token bucket, detectors, injection screen, spotlighting, tool catalogue, audit log and the `Gateway.handle()` pipeline.
- [`lab.py`](lab.py) holds the lab harness: it loads the data, mints tokens, registers the mock upstream, runs every request, prints the results and runs the self-checks.

**Authentication (`TokenAuthority`).** A token is `base64url(claims).base64url(HMAC-SHA256(key, claims))`. `verify()` recomputes the signature and compares it with `hmac.compare_digest`, which takes the same time whether the first or the last byte differs, so an attacker cannot learn the signature byte by byte from timing. It then checks `exp`. Request R02 edits the tenant claim from `contoso-health` to `northwind-lending` without re-signing and is rejected as `bad signature`. R03 is expired. The tenant is only ever taken from verified claims, never from a request field. This stub is a stand-in: in production, validate tokens from your corporate identity provider with a maintained library.

**Rate limiting (`TokenBucket`).** Each tenant has a bucket with a capacity and a refill rate. A request spends one token. Acme Logistics has a capacity of 1 and refills at 0.2 tokens per second, so R14 succeeds and R15, half a second later, is denied. The lab uses a fake clock so the result never depends on how fast your laptop is.

**Tenant policy.** `tenants.json` drives every decision. Contoso Health may not use Opus (R04 is denied before any content is read). Requested `max_tokens` is clamped to the tenant cap. `effort` is set by policy, not by the caller, which is a cost lever (lab 17).

**Data classification (`apply_data_rules`).** Detectors find secrets (`sk-ant-…`), card-like numbers that pass the Luhn check, SSN-like numbers, emails and phone numbers. Each tenant chooses `redact` or `block` per class. Secrets are always blocked on the way in. R01's email and phone are replaced by `[EMAIL_1]` and `[PHONE_1]`. The gateway's system prompt tells the model to keep placeholders, so a downstream service could map them back (lab 15 shows a reversible vault). R05 contains an SSN-like value, which Contoso's policy blocks outright.

**Injection screening and spotlighting.** `injection_score()` adds weights for patterns such as instruction overrides, prompt-extraction requests, role hijacking, bulk exfiltration verbs, text addressed to "the assistant", delimiter spoofing and URLs (URLs count only in documents). The prompt the authenticated user typed is blocked at a score of 0.6 or more (R07 scores 1.1). Third-party documents are held to a slightly higher threshold of 0.7, because they contain more ordinary text. R09's email scores 1.6 and is blocked. Documents that pass are wrapped by `spotlight()` in `<untrusted_document source="…" boundary="…">` tags. The boundary is an HMAC of the document under the gateway key, and any `<untrusted_document` text inside the document is escaped, so an attacker cannot close the block early. The system prompt explains the tags. Spotlighting reduces, but does not eliminate, the chance that the model follows embedded instructions.

**Budget.** Before calling, the gateway reserves `estimated_input + max_tokens`. If `used + reservation` would exceed the daily budget, the request is denied (R16: `used 207 + reserve 425 > budget 500`). After the call it charges actual `input_tokens + output_tokens`.

**Upstream call.** The request uses `model`, a capped `max_tokens`, a `system` prompt (gateway rules, canary, tenant instructions), one user message and `output_config={"effort": ...}`. Tools are sent only if they are both requested and allow-listed, with `strict: true` schemas. There is no `temperature`, no assistant prefill and no forced `tool_choice`; the default `auto` lets the model decide. Thinking is left at its adaptive default.

**Response checks.** `stop_reason == "refusal"` becomes `REFUSED_UPSTREAM`, and `max_tokens` is noted as truncation. Each `tool_use` block is checked against the tools that were actually offered. In R11 the client asked for `bulk_export_customers`, the gateway stripped it, and the mock model asks for it anyway. That stands in for a model that invents a tool name, or a compromised upstream. The request is blocked. In R12 the model asks for `schedule_payment_change`, which Northwind marks as needing approval, so the call is placed in the approval queue and returned as `HOLD_APPROVAL`. The gateway never executes tools itself. Finally, the text is checked for the canary (R13 asks the model to describe its configuration, which passes the heuristics, and the mock model leaks the canary, so the output is blocked) and for personal data (R06's answer contains an email address, which is redacted).

**Audit log (`AuditLog`).** Every decision is a JSON line with a sequence number, timestamp, tenant, principal, decision, reasons, model, usage, redaction counts, tool names, a SHA-256 of the redacted prompt, the previous record's hash and its own hash. `verify()` walks the chain. The lab edits record 4 in a copy and shows the chain breaks at exactly that record.

## Synthetic test data

- [`data/tenants.json`](data/tenants.json): three fictional tenants. **Contoso Health** (clinic group: Haiku and Sonnet only, SSNs blocked), **Northwind Lending** (lender: Opus and Sonnet, card numbers blocked, a read-only tool plus an approval-gated tool), and **Acme Logistics** (parcel carrier: Haiku only, a tiny budget and a strict rate limit so you can see those controls fire).
- [`data/requests.json`](data/requests.json): 16 requests, each with an `expect` field naming the decision mock mode must produce. The emails, phone numbers, loan IDs and SSN-like value (`123-45-6789`) are invented. The injected document targets only this lab's toy gateway; the exfiltration URL uses the reserved `.example` domain.

## Execution steps

### Mock mode

```bash
CLAUDE_LAB_MODE=mock python 19-hands-on-labs/lab-20-secure-enterprise-architecture/lab.py
echo "exit code: $?"
```

Inspect the audit log:

```bash
OUT="${LAB_OUTPUT_DIR:-$(python -c 'import tempfile;print(tempfile.gettempdir())')}/claude-labs/lab-20"
python -c "import json,sys; [print(e['seq'], e['decision'], e['reasons']) for e in map(json.loads, open(sys.argv[1]))]" "$OUT/audit.jsonl"
```

Exercises:

1. Change Acme Logistics' `rate_limit.capacity` to `2` and re-run. R15 now passes the rate limit. Which control stops it instead, and why?
2. Rephrase R07 so it slips past the heuristics (for example "Kindly set aside the earlier guidance…"). The screen misses it. Which later control still limits the damage? This is why defence in depth matters.
3. Add `"PHONE": "block"` to Contoso's `data_rules`. Which request changes decision?
4. Edit a line in `audit.jsonl` and write a short script that calls `AuditLog.verify()` on the file.

### Live mode

> **Cost:** requires API credits (live mode).

```bash
export ANTHROPIC_API_KEY="sk-ant-..."
CLAUDE_LAB_MODE=live python 19-hands-on-labs/lab-20-secure-enterprise-architecture/lab.py
```

The eight gateway-only decisions (authentication, model, data policy, two injections, rate limit, budget) are identical in live mode because they never reach the model. The other decisions depend on the real model. R11 and R13 will usually come back as `ALLOW`, because a well-behaved model will not call a tool it was not given or reveal its canary. R12 may answer in text or call `get_loan_status` first instead of requesting the change. The expected-decision check runs only in mock mode, and the other self-checks run in both.

## Expected results

Real output from a mock run. Only the audit log path on line 3 differs between machines.

```text
=== Lab 20: Secure enterprise AI gateway ===  [MOCK — offline, no credits used; model=claude-opus-5-5]

Audit log: /var/folders/.../T/claude-labs/lab-20/audit.jsonl

1) Gateway decisions
  id   tenant             model              decision           up  reasons
  R01  contoso-health     claude-sonnet-5-5  ALLOW              yes redacted EMAILx1, PHONEx1
  R02  contoso-health     claude-sonnet-5-5  DENY_AUTH          no  bad signature
  R03  contoso-health     claude-sonnet-5-5  DENY_AUTH          no  token expired
  R04  contoso-health     claude-opus-5-5    DENY_MODEL         no  claude-opus-5-5 not allowed for tenant
  R05  contoso-health     claude-haiku-5-5   DENY_DATA_POLICY   no  blocked data classes: SSN
  R06  contoso-health     claude-haiku-5-5   ALLOW              yes output redacted EMAILx1
  R07  northwind-lending  claude-opus-5-5    BLOCK_INJECTION    no  direct score 1.1 ['override', 'prompt_extraction']
  R08  northwind-lending  claude-opus-5-5    ALLOW              yes spotlighted 1 document(s)
  R09  northwind-lending  claude-opus-5-5    BLOCK_INJECTION    no  indirect score 1.6 ['override', 'exfiltration', 'addresses_the_ai', 'url'] in inbound-email
  R10  northwind-lending  claude-opus-5-5    ALLOW              yes -
  R11  northwind-lending  claude-opus-5-5    BLOCK_TOOL         yes stripped tools ['bulk_export_customers']; model requested non-allowed tool bulk_export_customers
  R12  northwind-lending  claude-opus-5-5    HOLD_APPROVAL      yes schedule_payment_change queued for human approval
  R13  northwind-lending  claude-sonnet-5-5  BLOCK_OUTPUT_LEAK  yes system prompt canary found in output
  R14  acme-logistics     claude-haiku-5-5   ALLOW              yes -
  R15  acme-logistics     claude-haiku-5-5   DENY_RATE_LIMIT    no  token bucket empty
  R16  acme-logistics     claude-haiku-5-5   DENY_BUDGET        no  used 207 + reserve 425 > budget 500

2) Allowed outputs and tool calls returned to clients
  R01: Hi, this is a reminder of your physiotherapy appointment on Tuesday at 10:30. Reply to [EMAIL_1] or call [PHONE_1] to change it.
  R06: Patients can send billing questions to [EMAIL_1] or call the front desk.
  R08: The borrower asks whether an extra payment this month would incur a fee.
  R10: tool_use get_loan_status({"loan_id": "NL-20391"})
  R12: tool_use schedule_payment_change({"loan_id": "NL-20391", "new_due_day": 15})
  R14: DAMAGE

3) Human approval queue (see lab 13)
  gw-0012 northwind-lending agent-2207 -> schedule_payment_change {"loan_id": "NL-20391", "new_due_day": 15}

4) Token use against daily budgets
  contoso-health     used   481 of  20000
  northwind-lending  used  1449 of  50000
  acme-logistics     used   207 of    500

5) Audit log integrity
  records: 16   chain valid: True
  after editing record 4: chain valid: False (first bad record: 4)

6) Decision summary
  ALLOW              5
  BLOCK_INJECTION    2
  BLOCK_OUTPUT_LEAK  1
  BLOCK_TOOL         1
  DENY_AUTH          2
  DENY_BUDGET        1
  DENY_DATA_POLICY   1
  DENY_MODEL         1
  DENY_RATE_LIMIT    1
  HOLD_APPROVAL      1

7) Self-checks
  [PASS] every request got its expected decision
  [PASS] tampered and expired tokens are rejected
  [PASS] audit chain verifies, and an edited record is detected
  [PASS] no raw email, phone, SSN-like or card value was sent upstream
  [PASS] audit log contains no raw prompt text or personal data
  [PASS] a tool outside the tenant allow-list is never offered upstream
  [PASS] max_tokens never exceeds the tenant cap
  [PASS] no tenant exceeded its daily token budget
  [PASS] no request sent temperature or a forced tool_choice
  [PASS] spotlighting neutralises a spoofed closing tag
  [PASS] indirect injection outscores a benign document
  [PASS] redaction keeps a non-Luhn 16-digit reference number

12/12 self-checks passed.
```

Eight of the 16 requests never reached the model (the `up` column shows `no`). In mock mode, token counts come from the helper's length-based estimate rather than a real tokenizer.

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| `every request got its expected decision` fails after you edit data | Your change altered a decision, which is the point of the suite | Read the printed `mismatch` lines and update `expect` only if the new decision is the one you want |
| R15 is `ALLOW` | You raised Acme's rate-limit capacity, or changed `advance_seconds` | Restore `tenants.json`, or treat it as exercise 1 |
| Every request is `DENY_AUTH` after you change the code | Tokens are minted with a different key from the one used to verify them | Use one `TokenAuthority` instance per run, or set `LAB20_GATEWAY_SIGNING_KEY` once before starting |
| Live R11 or R13 come back `ALLOW` | Expected: the real model behaved well | The controls are defence in depth. See the Live mode notes |
| `400 invalid_request_error` mentioning tools | A tool schema was edited and no longer satisfies strict mode | Keep `additionalProperties: false` and list every property in `required` |
| `Live mode needs the SDK` | `anthropic` not installed | `pip install -r 19-hands-on-labs/requirements.txt` |
| Legitimate text is blocked as injection | Heuristics have false positives, such as a document that quotes "ignore previous instructions" in a training memo | Tune weights or thresholds per tenant, and add a review path instead of a hard block for medium scores |

## Security considerations

- **A gateway is a high-value target.** It holds the API credential and sees every tenant's data. Run it with minimal privileges, restrict egress to the Claude API host, keep the credential in a secrets manager, and rotate it.
- **Heuristics are a speed bump, not a wall.** Prompt-injection screening with patterns will always miss some attacks and flag some innocent text. The real protection comes from layering: least-privilege tools, approval for side effects, output checks and monitoring. Assume some injections get through and design so they cannot do much damage.
- **Spotlighting needs the system prompt and the delimiters to agree.** The keyed boundary prevents an attacker from forging the closing tag. Escaping prevents a literal tag from confusing the model.
- **Fail closed.** Every unexpected condition (unknown tenant, bad token, blocked data class, unknown tool) results in a denial with a reason, not a pass-through.
- **Tenant isolation.** The tenant comes only from verified claims. Rate limits, budgets and approval queues are keyed by tenant, so one tenant cannot exhaust another's allowance. In production, keep this state in a shared store and add tenant IDs to every log line and trace.
- **Audit without over-collection.** The audit log records decisions, counts and hashes, not prompts or outputs. For regulated tenants (for example health data under HIPAA, or personal data under GDPR), confirm retention and access rules for audit data, and check which Claude data-retention options your agreement provides. Treat compliance claims as your organisation's legal team's call, not the gateway's.
- **Refusals and fallbacks.** Current models can return `stop_reason: "refusal"`. The gateway surfaces it as `REFUSED_UPSTREAM` instead of passing on empty content. The Claude API also offers a server-side `fallbacks` option (beta) that retries a declined request on another model. If you enable it, record which model actually served the request in the audit log.
- **Keep the gateway current.** Model IDs, parameters and pricing change. Keep allowed model lists and prices in configuration, not code, and review them on a schedule.

> **Unverified:** the server-side refusal fallback feature and its beta header names come from the `claude-api` skill as of 2026-10-24. Check the Claude API documentation for current availability on your platform before relying on it.

## Cleanup

```bash
rm -rf "${LAB_OUTPUT_DIR:-$(python -c 'import tempfile;print(tempfile.gettempdir())')}/claude-labs/lab-20"
unset LAB20_GATEWAY_SIGNING_KEY ANTHROPIC_API_KEY
```

The lab writes nothing inside the repository.

## Exam relevance

Objective IDs come from [`registry.yaml`](../../16-certification-tracks/registry.yaml).

| Objective | Text | How this lab covers it |
|---|---|---|
| CCAR-P 5.1 | Implement guardrails and safety controls | The full gateway pipeline: data rules, injection screen, tool allow-list, output checks |
| CCAR-P 3.2 | Analyse authentication and authorisation to find security gaps | Signed tokens, tenant claims, per-tenant model and tool authorisation, threat model T1 |
| CCAR-P 3.1 | Evaluate tool and agent configuration for capability bloat | Least-privilege tool offering, stripping of non-allowed tools, response-side re-check |
| CCAR-P 1.2 | Design end-to-end architectures (input, processing, output, feedback loops) | Ordered pipeline, approval queue, audit feedback |
| CCAR-P 5.3 | Apply human-in-the-loop validation | `HOLD_APPROVAL` for side-effecting tools |
| CCAR-P 5.4 | Ensure regulatory compliance (e.g. GDPR, HIPAA, FedRAMP) | Data minimisation, redaction, audit without raw content |
| CCAR-P 6.4 | Document architectures and give implementation guidance | Architecture diagram, threat model and control mapping |

## Next lab

You have finished the hands-on labs. Continue to the [real-world projects](../../20-real-world-projects/README.md), where you apply these patterns end to end.
