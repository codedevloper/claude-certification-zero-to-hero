# Logging and Auditability

> **Level:** Intermediate · **Time:** ~40 min · **Exam relevance:** CCAR-P D3 (3.4), CCAR-P D4 (4.6), CCAR-P D5 (5.4)

## In plain English

An audit trail lets you answer, after the fact, "what happened, who caused it, and why?" For an AI system that means
being able to reconstruct which user asked what, which model and prompt version answered, what context it saw, which
tools it called with which arguments, who approved what, and what the final outcome was.

The tension: the most useful logs contain prompts and responses, and prompts and responses often contain personal
data, confidential documents or secrets. Good AI logging captures enough to investigate and prove compliance without
building a second, less-protected copy of your most sensitive data.

Operational observability (latency, errors, cost dashboards) is covered in
[Module 15: observability](../15-production-operations/02-observability.md). This page focuses on security and audit.

## Why it matters

- Repudiation is a STRIDE category for a reason. Without attributable records, you cannot investigate an injection,
  a data leak or a disputed agent action.
- Regulations and frameworks expect it: record-keeping and traceability appear in the EU AI Act's requirements for
  high-risk systems, in the NIST AI RMF "Measure" and "Manage" functions, and in ordinary security standards.
- Logs are your detection layer for prompt injection campaigns, abuse and anomalous agent behaviour.

## How it works

### What to record

| Event | Fields | Why |
|---|---|---|
| Request received | Timestamp, request ID, user ID (pseudonymous), tenant, channel, session/conversation ID | Attribution |
| Model call | Model ID, prompt template version, system prompt hash, tools offered, effort setting, Claude response `id` and request ID, `stop_reason`, usage fields | Reproducibility and cost |
| Retrieval | Document IDs and versions retrieved, ACL decision | Shows what the model could see without copying content |
| Tool call | Tool name, arguments (redacted), policy decision (allow/deny/approval), agent identity, delegated scopes, result status | Core of agent audit |
| Human approval | Approver identity, what they saw, decision, time to decide | Oversight evidence |
| Guardrail event | Screen verdicts, blocked outputs, sanitiser findings | Detection |
| Output delivered | Output hash, length, destinations (UI, email, ticket) | Links decisions to outcomes |
| Configuration change | Prompt, tool, model or policy version changes with author | Change control |

### Content: hash, reference, or store?

| Option | What is logged | Pros | Cons |
|---|---|---|---|
| Metadata only | IDs, versions, counts, decisions | Low risk, cheap | Cannot see what the model said |
| Hash | SHA-256 of prompt and response | Can prove integrity later if content is kept elsewhere | Not readable |
| Reference | Pointer to content in a protected store with its own retention and access control | Investigations possible under control | Two systems to manage |
| Full content in logs | Everything | Easiest debugging | Highest risk; logs become a sensitive data store |

A common enterprise choice: metadata plus hashes in the general logging platform, and full content in a separate,
access-controlled audit store with short retention and break-glass access, enabled per use case after a privacy
review.

### Integrity and access

- Write audit logs to append-only or write-once storage, or ship them to a separate account the application cannot
  modify.
- Chain records (each record includes the hash of the previous one) when tamper evidence matters.
- Restrict who can read content-bearing logs and log every read.
- Set retention deliberately and document it; keep it consistent with your data-retention commitments.

### Using provider-side records

- Every Claude API response has an `id`, and the SDK exposes the request ID (in Python, `response._request_id`,
  populated from the `request-id` header). Log both; Anthropic support uses the request ID.
- The Claude SDKs and API can emit OpenTelemetry spans (beta as of 2026-10-24) with `gen_ai.*` attributes. The
  default content mode is metadata only; full content mode exports prompts and responses to your backend.
- For Claude Enterprise, Anthropic documents audit logs, a Compliance API that gives programmatic access to activity
  and content for compliance purposes, and an activity feed; see
  [enterprise deployment controls](14-enterprise-deployment-controls.md).
- For Claude Code, organisations can monitor usage through OpenTelemetry metrics and audit settings changes with
  `ConfigChange` hooks, per the [Claude Code security](https://code.claude.com/docs/en/security) page.

## Example

A structured audit logger for an agent loop. It redacts arguments, hashes content, chains records for tamper
evidence and writes JSON lines that any SIEM can ingest.

```python
"""audit_log.py - structured, hash-chained audit records for LLM and tool events."""
import hashlib
import json
import time
import uuid
from pathlib import Path

REDACT_KEYS = {"password", "token", "authorization", "ssn", "account_number", "api_key"}


def _sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _redact(obj):
    if isinstance(obj, dict):
        return {k: "[REDACTED]" if k.lower() in REDACT_KEYS else _redact(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_redact(v) for v in obj]
    return obj


class AuditLog:
    def __init__(self, path: Path):
        self.path = path
        self.prev = "0" * 64
        if path.exists():
            lines = path.read_text().splitlines()
            if lines:
                self.prev = json.loads(lines[-1])["record_hash"]

    def write(self, event: str, **fields) -> dict:
        record = {"ts": time.time(), "event_id": str(uuid.uuid4()), "event": event,
                  "prev_hash": self.prev, **_redact(fields)}
        record["record_hash"] = _sha(json.dumps(record, sort_keys=True))
        with self.path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record, sort_keys=True) + "\n")
        self.prev = record["record_hash"]
        return record


def verify_chain(path: Path) -> bool:
    prev = "0" * 64
    for line in path.read_text().splitlines():
        rec = json.loads(line)
        claimed = rec.pop("record_hash")
        if rec["prev_hash"] != prev or _sha(json.dumps(rec, sort_keys=True)) != claimed:
            return False
        prev = claimed
    return True


if __name__ == "__main__":
    log = AuditLog(Path("audit.jsonl"))
    log.write("model_call", request_id="req_mock_1", user="u-4821", tenant="t-north",
              model="claude-opus-5-5", prompt_version="triage-v7",
              prompt_sha=_sha("...full prompt..."), stop_reason="tool_use",
              usage={"input_tokens": 1830, "output_tokens": 212})
    log.write("tool_call", request_id="req_mock_1", agent="agent:triage@prod", tool="lookup_account",
              args={"account_number": "12345678", "fields": ["status"]}, decision="allow")
    print("chain valid:", verify_chain(Path("audit.jsonl")))
```

In production, ship these records to write-once storage and alert on: denied tool calls per user, sanitiser
findings, screen blocks, refusals, and unusual volumes of retrieval per user.

## Enterprise use case

*Northwind Lending* must show regulators how an AI-assisted hardship decision was reached. Its audit design:

- Each case has a case ID that links the model calls, retrieved policy document versions, tool calls and the
  reviewer's final decision.
- General logs hold metadata and hashes; full prompts and responses go to an audit store in a separate cloud account
  with seven-year retention aligned to the lending record policy, encrypted with a customer-managed key, readable only
  by the compliance team through a logged break-glass process.
- Monthly, the compliance team samples 50 cases and replays them against the logged prompt versions to confirm the
  records are complete. Gaps become incidents.
- Security monitoring alerts when a single user triggers more than five denied tool calls in an hour, a pattern that
  caught a prompt-injection test campaign during the pilot.

## Common mistakes

- Logging everything to the general logging platform with default retention.
- Logging nothing but latency and errors, so incidents cannot be reconstructed.
- No prompt or model version in logs, so you cannot tell which configuration produced an answer.
- Log viewers that render model output as HTML (stored XSS in internal tools).
- Conversation or trace IDs that contain email addresses or customer numbers.

## Security considerations

- Logs are a data store: include them in data-protection impact assessments, retention schedules and access reviews.
- Logging full content to a third-party observability vendor is a data transfer; check contracts and residency.
- Under zero-data-retention arrangements with a provider, your own logs may become the only copy of prompts and
  responses. That raises, not lowers, the bar for protecting them.
- Protect against log injection: escape newlines and control characters in user and model text.

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| Cannot link a tool call to the user who caused it | Request ID not propagated through the agent loop | Pass a correlation ID through every layer; log it on every record |
| Logs too expensive | Full content at high volume | Metadata plus hashes by default; sample full content |
| Chain verification fails | Records edited or written out of order | Investigate as a potential tampering incident; ensure single writer |

## Check your understanding

1. Name four fields every model-call audit record should contain.
2. What are the trade-offs between logging metadata only and logging full content?
3. Why might zero data retention at the provider increase your own logging obligations?
4. How does hash chaining provide tamper evidence?

<details>
<summary>Answers</summary>

1. Any four of: request ID, user/tenant, model ID, prompt version or hash, tools offered, `stop_reason`, usage fields,
   timestamp, response ID.
2. Metadata-only is low risk and cheap but cannot show what the model said; full content enables investigation but
   turns logs into a sensitive data store requiring strict access, retention and privacy controls.
3. Because the provider keeps no copy, your logs may be the only record available for investigations and compliance,
   so they must be complete and well protected.
4. Each record includes the hash of the previous record; altering or deleting a record breaks every subsequent hash,
   which verification detects.

</details>

## Further reading

- Anthropic: [OpenTelemetry for the Claude API](https://platform.claude.com/docs/en/manage-claude/opentelemetry)
- Anthropic: [Claude Code monitoring usage](https://code.claude.com/docs/en/monitoring-usage)
- OWASP: [Logging Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html)
- In this repository: [observability](../15-production-operations/02-observability.md),
  [Lab 19: observability](../19-hands-on-labs/lab-19-observability/README.md),
  [Project 05: agentic investigation assistant](../20-real-world-projects/05-agentic-investigation-assistant/README.md)

<!-- page-nav:start -->
---

[← Previous: Secrets Management for AI Systems](10-secrets-management.md) · [Module overview](README.md) · [Next: AI Governance →](12-ai-governance.md)
<!-- page-nav:end -->
