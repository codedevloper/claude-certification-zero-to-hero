"""Lab 13: human-in-the-loop approvals for risk-tiered tool actions.

Claude works three synthetic service tickets for Acme Logistics (a fictional company) in a
manual tool-use loop. Every tool call passes through a gate that:

  1. validates the arguments against the tool schema,
  2. assigns a risk tier (low / medium / high / blocked) from data/risk_policy.json,
  3. runs low-risk calls, runs medium-risk calls and queues them for after-the-fact review,
  4. pauses high-risk calls until a (simulated) human approver decides, or the request expires,
  5. writes every step to a hash-chained JSONL audit log.

Usage (from the repository root):

    CLAUDE_LAB_MODE=mock python 19-hands-on-labs/lab-13-human-in-the-loop/lab.py   # offline, free
    CLAUDE_LAB_MODE=live python 19-hands-on-labs/lab-13-human-in-the-loop/lab.py   # real API, uses credits

Output files go to $LAB_OUTPUT_DIR/claude-labs/lab-13 (default: the system temp directory).
"""
from __future__ import annotations

import copy
import hashlib
import json
import os
import re
import sys
import tempfile
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "common"))
from claude_lab import MODE, MODEL, TextBlock, ToolUseBlock, banner, get_client, register_mock, text_of  # noqa: E402

DATA = HERE / "data"
OUT = Path(os.environ.get("LAB_OUTPUT_DIR") or tempfile.gettempdir()) / "claude-labs" / "lab-13"

SYSTEM = (
    "You are ACME-OPS-ASSISTANT, the operations assistant for Acme Logistics, a fictional freight company. "
    "You resolve service tickets with the tools provided.\n"
    "Rules:\n"
    "- Check the shipment status before you change anything.\n"
    "- Some actions need human approval. The platform decides which ones; you do not.\n"
    "- If a tool result starts with NOT EXECUTED, do not retry it and do not look for a workaround. "
    "Tell the requester what happens next.\n"
    "- Finish with a short summary for the ticket log, three sentences at most."
)


def _tool(name: str, description: str, props: dict[str, dict]) -> dict:
    return {
        "name": name,
        "description": description,
        "strict": True,
        "input_schema": {
            "type": "object",
            "properties": props,
            "required": list(props),
            "additionalProperties": False,
        },
    }


SID = {"type": "string", "description": "Shipment ID such as SHP-7781"}
TOOLS = [
    _tool("get_shipment_status", "Read the current status, condition and address of a shipment.", {"shipment_id": SID}),
    _tool("reschedule_delivery", "Move the delivery date of a shipment.",
          {"shipment_id": SID, "new_date": {"type": "string", "description": "YYYY-MM-DD"}}),
    _tool("issue_carrier_credit", "Credit the customer account for a shipment problem.",
          {"shipment_id": SID, "amount_usd": {"type": "number"}, "reason": {"type": "string"}}),
    _tool("reroute_shipment", "Change the delivery address of a shipment in transit.",
          {"shipment_id": SID, "new_address": {"type": "string"}}),
    _tool("release_customs_hold", "Ask the broker to release a customs hold.",
          {"shipment_id": SID, "broker_reference": {"type": "string"}}),
]
SCHEMAS = {t["name"]: t["input_schema"] for t in TOOLS}


# --------------------------------------------------------------------------- deterministic infrastructure
class FakeClock:
    """Simulated time, so approval waits and expiry run instantly and reproducibly."""

    def __init__(self) -> None:
        self.now = datetime(2026, 10, 24, 9, 0, 0, tzinfo=timezone.utc)

    def advance(self, seconds: int) -> None:
        self.now += timedelta(seconds=seconds)

    def iso(self) -> str:
        return self.now.strftime("%Y-%m-%dT%H:%M:%SZ")


def canonical(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), default=str)


def sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


class AuditLog:
    """Append-only JSONL log. Each record carries the hash of the previous one (a hash chain)."""

    GENESIS = "0" * 64

    def __init__(self, path: Path, clock: FakeClock) -> None:
        self.path, self.clock = path, clock
        self.path.write_text("", encoding="utf-8")
        self.prev, self.seq = self.GENESIS, 0
        self.records: list[dict] = []

    def record(self, event: str, **details: Any) -> dict:
        self.seq += 1
        rec = {"seq": self.seq, "ts": self.clock.iso(), "event": event, **details, "prev_hash": self.prev}
        rec["hash"] = sha256(canonical(rec))
        with self.path.open("a", encoding="utf-8") as fh:
            fh.write(canonical(rec) + "\n")
        self.prev = rec["hash"]
        self.records.append(rec)
        return rec


def verify_chain(lines: list[str]) -> tuple[bool, int | None]:
    """Recompute every hash. Returns (ok, seq of the first bad record)."""
    prev = AuditLog.GENESIS
    for line in lines:
        rec = json.loads(line)
        claimed = rec.pop("hash")
        if rec["prev_hash"] != prev or sha256(canonical(rec)) != claimed:
            return False, rec.get("seq")
        prev = claimed
    return True, None


# --------------------------------------------------------------------------- fake back end
class ShipmentSystem:
    def __init__(self, shipments: dict) -> None:
        self.db = copy.deepcopy(shipments)
        self.credits: list[dict] = []

    def run(self, tool: str, args: dict) -> str:
        ship = self.db.get(args["shipment_id"])
        if ship is None:
            return f"ERROR: unknown shipment {args['shipment_id']}"
        if tool == "get_shipment_status":
            return json.dumps({"shipment_id": args["shipment_id"], **ship})
        if tool == "reschedule_delivery":
            ship["eta"] = args["new_date"]
            return f"EXECUTED: delivery for {args['shipment_id']} moved to {args['new_date']}"
        if tool == "issue_carrier_credit":
            credit_id = f"CR-{len(self.credits) + 1:04d}"
            self.credits.append({"credit_id": credit_id, **args})
            return f"EXECUTED: credit {credit_id} of {args['amount_usd']:.2f} USD applied for {args['shipment_id']}"
        if tool == "reroute_shipment":
            ship["address"] = args["new_address"]
            return f"EXECUTED: {args['shipment_id']} rerouted to {args['new_address']}"
        if tool == "release_customs_hold":
            ship["customs_hold"], ship["status"] = False, "in_transit"
            return f"EXECUTED: release requested for {args['shipment_id']} (broker {args['broker_reference']})"
        return f"ERROR: no handler for {tool}"


# --------------------------------------------------------------------------- policy
def validate_args(schema: dict, args: Any) -> list[str]:
    """Small JSON-schema subset: object, required, additionalProperties false, string/number types."""
    if not isinstance(args, dict):
        return ["arguments must be an object"]
    errors = [f"missing '{k}'" for k in schema["required"] if k not in args]
    errors += [f"unexpected '{k}'" for k in args if k not in schema["properties"]]
    for key, spec in schema["properties"].items():
        if key not in args:
            continue
        val = args[key]
        if spec["type"] == "string" and not (isinstance(val, str) and val.strip()):
            errors.append(f"'{key}' must be a non-empty string")
        if spec["type"] == "number" and (isinstance(val, bool) or not isinstance(val, (int, float)) or val <= 0):
            errors.append(f"'{key}' must be a positive number")
    return errors


def classify(tool: str, args: dict, policy: dict) -> tuple[str, str]:
    rule = policy["tools"].get(tool)
    if rule is None:
        return "blocked", "tool is not on the allow-list"
    for lim in rule.get("hard_limits", []):
        if args.get(lim["field"], 0) > lim["max"]:
            return "blocked", lim["why"]
    tier, why = rule["tier"], rule["why"]
    for esc in rule.get("escalate", []):
        if args.get(esc["field"], 0) > esc["gt"]:
            tier, why = esc["tier"], esc["why"]
    return tier, why


# --------------------------------------------------------------------------- approvals
@dataclass
class ApprovalRequest:
    request_id: str
    ticket_id: str
    tool: str
    args: dict
    args_sha256: str
    reason: str
    requested_by: str
    created_at: datetime
    expires_at: datetime
    status: str = "pending"  # pending -> approved | rejected | expired; approved -> consumed
    decided_by: str | None = None
    decision_reason: str | None = None


class ApprovalQueue:
    def __init__(self) -> None:
        self.items: list[ApprovalRequest] = []

    def submit(self, ticket_id: str, tool: str, args: dict, reason: str, requested_by: str,
               clock: FakeClock, ttl: int) -> ApprovalRequest:
        req = ApprovalRequest(
            request_id=f"APR-{len(self.items) + 1:04d}", ticket_id=ticket_id, tool=tool, args=copy.deepcopy(args),
            args_sha256=sha256(canonical(args)), reason=reason, requested_by=requested_by,
            created_at=clock.now, expires_at=clock.now + timedelta(seconds=ttl))
        self.items.append(req)
        return req

    def pending(self) -> list[ApprovalRequest]:
        return [r for r in self.items if r.status == "pending"]

    @staticmethod
    def decide(req: ApprovalRequest, approver: str, allowed_tools: list[str], approve: bool, reason: str) -> None:
        if req.status != "pending":
            raise PermissionError(f"{req.request_id} is already {req.status}")
        if approver == req.requested_by:
            raise PermissionError("separation of duties: the requester cannot approve its own action")
        if req.tool not in allowed_tools:
            raise PermissionError(f"{approver} is not authorised to approve {req.tool}")
        req.status = "approved" if approve else "rejected"
        req.decided_by, req.decision_reason = approver, reason


class SimulatedApprover:
    """Stands in for a person working an approval inbox. Decisions come from data/approver_script.json."""

    def __init__(self, script: dict) -> None:
        self.script = script
        self.ready_at: dict[str, datetime] = {}

    def _rule(self, req: ApprovalRequest) -> dict:
        return next((r for r in self.script["rules"] if r["tool"] == req.tool), self.script["default"])

    def review(self, queue: ApprovalQueue, clock: FakeClock) -> None:
        for req in queue.pending():
            rule = self._rule(req)
            if rule["decision"] == "no_response":
                continue
            ready = self.ready_at.setdefault(req.request_id, req.created_at + timedelta(seconds=rule.get("think_seconds", 60)))
            if clock.now >= ready:
                who = rule["approver"]
                queue.decide(req, who, self.script["approvers"].get(who, []), rule["decision"] == "approve", rule["reason"])


def await_decision(req: ApprovalRequest, queue: ApprovalQueue, approver: SimulatedApprover,
                   clock: FakeClock, poll: int) -> ApprovalRequest:
    """Poll until decided or expired. In production this is a durable pause, not a loop in memory."""
    while True:
        approver.review(queue, clock)
        if req.status != "pending":
            return req
        if clock.now >= req.expires_at:
            req.status = "expired"
            return req
        clock.advance(poll)


def execute_approved(req: ApprovalRequest, tool: str, args: dict, backend: ShipmentSystem) -> str:
    """Run an approved action only if it is exactly what was approved, and only once."""
    if req.status != "approved":
        raise PermissionError(f"{req.request_id} is {req.status}, not approved")
    if tool != req.tool or sha256(canonical(args)) != req.args_sha256:
        raise PermissionError("arguments differ from the approved request")
    req.status = "consumed"
    return backend.run(tool, args)


# --------------------------------------------------------------------------- the gate
@dataclass
class Context:
    policy: dict
    backend: ShipmentSystem
    queue: ApprovalQueue
    approver: SimulatedApprover
    audit: AuditLog
    clock: FakeClock
    notifications: list[str] = field(default_factory=list)
    trace: list[str] = field(default_factory=list)


def gate(block: Any, ticket_id: str, ctx: Context) -> dict:
    tool, args = block.name, block.input
    base = {"ticket": ticket_id, "tool": tool, "tool_use_id": block.id}
    ctx.audit.record("tool_proposed", **base, args_sha256=sha256(canonical(args)), args=args)

    def result(text: str, is_error: bool = False) -> dict:
        out = {"type": "tool_result", "tool_use_id": block.id, "content": text}
        if is_error:
            out["is_error"] = True
        return out

    errors = validate_args(SCHEMAS[tool], args) if tool in SCHEMAS else []
    tier, why = ("blocked", "; ".join(errors)) if errors else classify(tool, args, ctx.policy)
    ctx.audit.record("tier_assigned", **base, tier=tier, why=why)
    ctx.trace.append(f"  {tool:<22} tier={tier:<7} ({why})")

    if tier == "blocked":
        ctx.audit.record("tool_blocked", **base, why=why)
        return result(f"NOT EXECUTED: blocked by policy ({why}).", True)
    if tier == "low":
        out = ctx.backend.run(tool, args)
        ctx.audit.record("tool_executed", **base, actor="agent", outcome=out[:120])
        return result(out)
    if tier == "medium":
        out = ctx.backend.run(tool, args)
        note = f"{ticket_id}: {tool} ran without pre-approval and is queued for review -> {out}"
        ctx.notifications.append(note)
        ctx.audit.record("tool_executed", **base, actor="agent", outcome=out[:120])
        ctx.audit.record("post_review_queued", **base)
        return result(out)

    # high risk: pause for a human decision
    req = ctx.queue.submit(ticket_id, tool, args, why, ctx.policy["requester_identity"], ctx.clock,
                           ctx.policy["approval_ttl_seconds"])
    ctx.audit.record("approval_requested", **base, request_id=req.request_id, expires_at=req.expires_at.isoformat())
    asked_at = ctx.clock.now
    await_decision(req, ctx.queue, ctx.approver, ctx.clock, ctx.policy["poll_interval_seconds"])
    waited = int((ctx.clock.now - asked_at).total_seconds())
    ctx.audit.record("approval_decided", **base, request_id=req.request_id, status=req.status,
                     decided_by=req.decided_by, reason=req.decision_reason, waited_seconds=waited)
    ctx.trace.append(f"  {'':<22} {req.request_id} -> {req.status} after {waited // 60} min"
                     + (f" by {req.decided_by}" if req.decided_by else ""))
    if req.status == "approved":
        out = execute_approved(req, tool, args, ctx.backend)
        ctx.audit.record("tool_executed", **base, actor=f"agent (approved by {req.decided_by})",
                         request_id=req.request_id, outcome=out[:120])
        return result(out)
    if req.status == "rejected":
        return result(f"NOT EXECUTED: {req.request_id} was rejected by {req.decided_by}. Reason: {req.decision_reason}. "
                      "Do not retry.", True)
    return result(f"NOT EXECUTED: {req.request_id} expired after {ctx.policy['approval_ttl_seconds'] // 60} minutes "
                  "with no decision. It stays open for manual follow-up. Do not retry.", True)


# --------------------------------------------------------------------------- agent loop
def run_ticket(client: Any, ticket: dict, ctx: Context, max_steps: int = 6) -> str:
    messages: list[dict] = [{
        "role": "user",
        "content": f"Ticket {ticket['ticket_id']} from {ticket['customer']} via {ticket['channel']}:\n{ticket['text']}",
    }]
    for _ in range(max_steps):
        resp = client.messages.create(
            model=MODEL, max_tokens=2048, system=SYSTEM, tools=TOOLS, tool_choice={"type": "auto"},
            messages=messages, output_config={"effort": "medium"},
        )
        if resp.stop_reason == "refusal":
            ctx.audit.record("model_refused", ticket=ticket["ticket_id"])
            return "[model declined this ticket; routed to a human]"
        if resp.stop_reason == "max_tokens":
            return "[response hit max_tokens; ticket routed to a human]"
        messages.append({"role": "assistant", "content": resp.content})
        if resp.stop_reason != "tool_use":
            return text_of(resp).strip()
        results = [gate(b, ticket["ticket_id"], ctx) for b in resp.content if getattr(b, "type", "") == "tool_use"]
        messages.append({"role": "user", "content": results})  # all results in one message
    ctx.audit.record("step_budget_exhausted", ticket=ticket["ticket_id"])
    return "[step budget exhausted; ticket routed to a human]"


# --------------------------------------------------------------------------- mock model
MOCK_PLANS = {
    "T-1001": [
        ("I'll confirm the shipment first.", [("get_shipment_status", {"shipment_id": "SHP-7781"})]),
        ("Damage is confirmed. Requesting the credit.",
         [("issue_carrier_credit", {"shipment_id": "SHP-7781", "amount_usd": 450, "reason": "Damage claim CLM-220"})]),
    ],
    "T-1002": [
        ("Checking the shipment before any change.", [("get_shipment_status", {"shipment_id": "SHP-7790"})]),
        ("Requesting the reroute.",
         [("reroute_shipment", {"shipment_id": "SHP-7790", "new_address": "99 Harbour Road, Port Example"})]),
    ],
    "T-1003": [
        ("Checking the hold.", [("get_shipment_status", {"shipment_id": "SHP-7802"})]),
        ("Requesting the release and the goodwill credit.", [
            ("release_customs_hold", {"shipment_id": "SHP-7802", "broker_reference": "BRK-5521"}),
            ("issue_carrier_credit", {"shipment_id": "SHP-7802", "amount_usd": 60, "reason": "Goodwill for customs delay"}),
        ]),
    ],
}


@register_mock
def mock_ops_agent(**request: Any) -> Any:
    if "ACME-OPS-ASSISTANT" not in str(request.get("system", "")):
        return None
    msgs = request["messages"]
    ticket = re.search(r"Ticket (T-\d+)", msgs[0]["content"]).group(1)
    turn = sum(1 for m in msgs if m["role"] == "assistant")
    plan = MOCK_PLANS.get(ticket, [])
    if turn < len(plan):
        say, calls = plan[turn]
        return [TextBlock(say)] + [ToolUseBlock(name=n, input=a) for n, a in calls]
    outcomes = [r["content"] for r in msgs[-1]["content"] if isinstance(r, dict)]
    lines = []
    for text in outcomes:
        if text.startswith("EXECUTED"):
            lines.append("Done: " + text.split(": ", 1)[1] + ".")
        elif "rejected" in text:
            lines.append("An approver rejected the request, so nothing changed; we will confirm the request with the customer.")
        elif "expired" in text:
            lines.append("The request is waiting for a human decision and stays open for follow-up.")
        else:
            lines.append(text)
    return f"{ticket} summary: " + " ".join(lines)


# --------------------------------------------------------------------------- main
RESULTS: list[bool] = []


def check(label: str, condition: bool) -> None:
    RESULTS.append(bool(condition))
    print(f"  [{'PASS' if condition else 'FAIL'}] {label}")


def main() -> int:
    banner("Lab 13: human-in-the-loop approvals")
    OUT.mkdir(parents=True, exist_ok=True)
    load = lambda name: json.loads((DATA / name).read_text(encoding="utf-8"))  # noqa: E731
    tickets, policy = load("tickets.json"), load("risk_policy.json")
    clock = FakeClock()
    ctx = Context(policy=policy, backend=ShipmentSystem(load("shipments.json")), queue=ApprovalQueue(),
                  approver=SimulatedApprover(load("approver_script.json")),
                  audit=AuditLog(OUT / "audit.jsonl", clock), clock=clock)
    client = get_client()

    summaries = {}
    for ticket in tickets:
        print(f"--- {ticket['ticket_id']} ({ticket['customer']}) ---")
        ctx.trace.clear()
        summaries[ticket["ticket_id"]] = run_ticket(client, ticket, ctx)
        print("\n".join(ctx.trace))
        print(f"  final: {summaries[ticket['ticket_id']]}\n")

    print("Medium-risk actions queued for after-the-fact review:")
    for note in ctx.notifications:
        print(f"  - {note}")

    (OUT / "approvals.json").write_text(json.dumps(
        [{k: (v.isoformat() if isinstance(v, datetime) else v) for k, v in vars(r).items()} for r in ctx.queue.items],
        indent=2), encoding="utf-8")
    counts: dict[str, int] = {}
    for rec in ctx.audit.records:
        counts[rec["event"]] = counts.get(rec["event"], 0) + 1
    print("\nAudit events: " + ", ".join(f"{k}={v}" for k, v in counts.items()))
    print(f"Files written to {OUT}: audit.jsonl, approvals.json\n")

    # ------------------------------------------------------------ self-checks
    print("Self-checks (control logic, always enforced):")
    lines = (OUT / "audit.jsonl").read_text(encoding="utf-8").splitlines()
    check("audit hash chain verifies", verify_chain(lines)[0])
    tampered = list(lines)
    rec = json.loads(tampered[2])
    rec["tier"] = "low"
    tampered[2] = canonical(rec)
    ok, bad = verify_chain(tampered)
    check(f"editing record 3 breaks the chain (first bad seq = {bad})", not ok and bad == 3)

    probe = ToolUseBlock(name="export_customer_list", input={"format": "csv"})
    check("tool not on the allow-list is blocked", gate(probe, "T-TEST", ctx).get("is_error") is True)
    tier, _ = classify("issue_carrier_credit", {"shipment_id": "SHP-7781", "amount_usd": 9000, "reason": "x"}, policy)
    check("credit above the hard limit is blocked outright", tier == "blocked")
    check("schema validation rejects missing and extra fields",
          len(validate_args(SCHEMAS["reroute_shipment"], {"shipment_id": "SHP-1", "extra": 1})) == 2)

    q = ApprovalQueue()
    req = q.submit("T-TEST", "reroute_shipment", {"shipment_id": "SHP-7790", "new_address": "A"}, "test",
                   policy["requester_identity"], clock, 900)
    try:
        q.decide(req, policy["requester_identity"], ["reroute_shipment"], True, "self")
        check("requester cannot approve its own request", False)
    except PermissionError:
        check("requester cannot approve its own request", req.status == "pending")
    q.decide(req, "ops.lead@acme-logistics.example", ["reroute_shipment"], True, "ok")
    scratch = ShipmentSystem(load("shipments.json"))
    try:
        execute_approved(req, "reroute_shipment", {"shipment_id": "SHP-7790", "new_address": "B"}, scratch)
        check("changed arguments after approval are refused", False)
    except PermissionError:
        check("changed arguments after approval are refused", True)
    execute_approved(req, "reroute_shipment", {"shipment_id": "SHP-7790", "new_address": "A"}, scratch)
    try:
        execute_approved(req, "reroute_shipment", {"shipment_id": "SHP-7790", "new_address": "A"}, scratch)
        check("an approval can be used only once", False)
    except PermissionError:
        check("an approval can be used only once", True)

    approvals = {e["request_id"] for e in ctx.audit.records if e["event"] == "approval_decided" and e["status"] == "approved"}
    high_exec = [e for e in ctx.audit.records if e["event"] == "tool_executed" and e.get("request_id")]
    check("every approval-backed execution has an approved decision",
          all(e["request_id"] in approvals for e in high_exec))

    if MODE == "mock":
        print("\nSelf-checks (scripted mock scenario):")
        db = ctx.backend.db
        check("T-1001: 450 USD credit paused, approved, then applied",
              any(c["amount_usd"] == 450 for c in ctx.backend.credits))
        check("T-1002: rejected reroute left the address unchanged", db["SHP-7790"]["address"].startswith("200 Market"))
        check("T-1003: unanswered customs release expired and did not run", db["SHP-7802"]["customs_hold"] is True)
        check("T-1003: 60 USD credit ran as medium risk and was queued for review",
              any("60.00 USD" in n for n in ctx.notifications))
        check("model was told about the rejection and the expiry",
              "rejected" in summaries["T-1002"] and "waiting for a human" in summaries["T-1003"])
    else:
        print("\nLive mode: scenario outcomes depend on the model's choices, so only control checks are asserted.")

    failed = RESULTS.count(False)
    print(f"\n{len(RESULTS) - failed}/{len(RESULTS)} checks passed.")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
