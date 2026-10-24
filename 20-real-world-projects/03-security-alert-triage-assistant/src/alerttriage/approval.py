"""Human approval gate and a simulated response executor.

Containment actions (isolate a host, disable an account, block an IP, reset credentials) can
cause outages and can be weaponised by an attacker who manipulates alert content. They therefore
run only after a named analyst approves the exact action ID. The executor here is a stand-in for
a SOAR or EDR integration: it records what would happen and refuses anything without a matching
approval. Every decision goes into an append-only audit log.
"""
from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .triage import ProposedAction, TriageDecision

AUTOMATION_IDENTITIES = frozenset({"triage-assistant", "claude", "automation", "system"})
_APPROVER = re.compile(r"^[a-z][a-z0-9._-]{2,63}$")


class ApprovalError(PermissionError):
    pass


@dataclass(frozen=True)
class Approval:
    action_id: str
    decision: str  # "approve" or "deny"
    approver: str
    reason: str


@dataclass
class AuditLog:
    events: list[dict[str, Any]] = field(default_factory=list)

    def record(self, event: str, **details: Any) -> None:
        self.events.append({"time": datetime.now(timezone.utc).isoformat(timespec="seconds"), "event": event, **details})

    def write_jsonl(self, path: Path) -> None:
        with path.open("a", encoding="utf-8") as fh:
            for e in self.events:
                fh.write(json.dumps(e) + "\n")


@dataclass
class ApprovalQueue:
    audit: AuditLog = field(default_factory=AuditLog)
    pending: dict[str, ProposedAction] = field(default_factory=dict)
    decided: dict[str, Approval] = field(default_factory=dict)

    def submit(self, decision: TriageDecision) -> list[ProposedAction]:
        queued = []
        for action in decision.actions:
            if action.needs_approval:
                self.pending[action.action_id] = action
                self.audit.record("approval_requested", action_id=action.action_id, action=action.action_type,
                                  target=action.target, alert_id=decision.alert_id)
                queued.append(action)
        return queued

    def decide(self, approval: Approval) -> None:
        if approval.action_id not in self.pending:
            raise ApprovalError(f"no pending action {approval.action_id!r}")
        if approval.decision not in ("approve", "deny"):
            raise ApprovalError(f"decision must be 'approve' or 'deny', got {approval.decision!r}")
        approver = approval.approver.strip().lower()
        if not _APPROVER.match(approver) or approver in AUTOMATION_IDENTITIES:
            raise ApprovalError(f"approver {approval.approver!r} is not a valid human analyst identity")
        if not approval.reason.strip():
            raise ApprovalError("an approval or denial needs a reason for the audit log")
        self.decided[approval.action_id] = approval
        del self.pending[approval.action_id]
        self.audit.record("approval_decided", action_id=approval.action_id, decision=approval.decision,
                          approver=approver, reason=approval.reason)

    def load_decisions(self, path: Path) -> list[str]:
        """Apply decisions from a JSON file; returns errors instead of stopping on the first one."""
        errors = []
        decisions = json.loads(path.read_text(encoding="utf-8")).get("decisions", {})
        for action_id, d in decisions.items():
            if action_id not in self.pending:
                continue  # decisions for other runs are ignored
            try:
                self.decide(Approval(action_id, d.get("decision", ""), d.get("approver", ""), d.get("reason", "")))
            except ApprovalError as exc:
                errors.append(str(exc))
        return errors


@dataclass
class SimulatedResponder:
    """Stand-in for a SOAR/EDR API. Records actions instead of performing them."""

    queue: ApprovalQueue
    executed: list[dict[str, Any]] = field(default_factory=list)

    def execute(self, action: ProposedAction) -> dict[str, Any]:
        approval = self.queue.decided.get(action.action_id)
        if approval is None or approval.decision != "approve":
            self.queue.audit.record("execution_blocked", action_id=action.action_id, reason="no approval")
            raise ApprovalError(f"{action.action_id}: containment requires an analyst approval")
        record = {"action_id": action.action_id, "action": action.action_type, "target": action.target,
                  "approved_by": approval.approver, "status": "simulated"}
        self.executed.append(record)
        self.queue.audit.record("action_executed", **{k: v for k, v in record.items() if k != "action_id"},
                                action_id=action.action_id)
        return record


def decision_as_dict(decision: TriageDecision) -> dict[str, Any]:
    data = asdict(decision)
    data["actions"] = [asdict(a) | {"needs_approval": a.needs_approval} for a in decision.actions]
    return data
