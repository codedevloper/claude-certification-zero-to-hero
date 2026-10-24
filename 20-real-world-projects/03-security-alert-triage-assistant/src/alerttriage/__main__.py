"""Command-line entry point.

    cd src && python -m alerttriage                                   # triage all sample alerts
    cd src && python -m alerttriage --approvals ../data/sample_approvals.json
    cd src && python -m alerttriage --alert ../data/alerts/ALRT-1005-phishing-attachment.json --json

Non-interactive. Containment actions stay pending unless a decisions file approves them by action
ID. Exits 0 on success, 1 on invalid input or unusable model output.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from claude_lab import MODE, banner, get_client

from . import DATA_DIR
from . import mock  # noqa: F401  (registers the offline responder)
from .alerts import AlertRejected, load_alerts, sanitise
from .approval import ApprovalQueue, SimulatedResponder, decision_as_dict
from .llm import ModelOutputError, UsageTally
from .triage import Catalog, triage_alert


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="alerttriage", description=__doc__.splitlines()[0])
    parser.add_argument("--alerts-dir", type=Path, default=DATA_DIR / "alerts")
    parser.add_argument("--alert", type=Path, help="triage a single alert file")
    parser.add_argument("--approvals", type=Path, help="JSON file of analyst decisions keyed by action ID")
    parser.add_argument("--audit-log", type=Path, help="append audit events to this JSONL file")
    parser.add_argument("--json", action="store_true", help="print decisions as JSON")
    args = parser.parse_args(argv)

    banner("Project 03: security alert triage assistant")
    if MODE == "live":
        print("> Cost: live mode uses API credits.\n")
    try:
        if args.alert:
            alerts = [sanitise(json.loads(args.alert.read_text(encoding="utf-8")))]
        else:
            alerts = load_alerts(args.alerts_dir)
    except (AlertRejected, OSError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    client, catalog, tally = get_client(), Catalog.load(DATA_DIR), UsageTally()
    queue = ApprovalQueue()
    decisions = []
    for alert in alerts:
        try:
            decision = triage_alert(alert, client, catalog, tally=tally)
        except ModelOutputError as exc:
            print(f"error ({alert.alert_id}): {exc}; route to an analyst", file=sys.stderr)
            return 1
        decisions.append(decision)
        queue.submit(decision)
        if args.json:
            print(json.dumps(decision_as_dict(decision), indent=2))
            continue
        changed = "" if decision.severity == decision.model_severity else f" (model said {decision.model_severity})"
        print(f"[{decision.alert_id}] severity={decision.severity}{changed} confidence={decision.confidence} "
              f"injection_suspected={decision.injection_suspected}")
        print(f"  {decision.summary}")
        for t in decision.techniques:
            print(f"  ATT&CK {t['technique_id']} {t['name']}")
        for a in decision.actions:
            gate = "NEEDS APPROVAL" if a.needs_approval else "advisory"
            print(f"  {a.action_id:14} {a.action_type:18} {a.target:28} {gate}")
        for w in decision.warnings:
            print(f"  guardrail: {w}")
        if alert.injection_flags:
            print(f"  pre-screen: {len(alert.injection_flags)} field(s) contain instruction-like text")
        print()

    if args.approvals:
        for err in queue.load_decisions(args.approvals):
            print(f"approval rejected: {err}", file=sys.stderr)
    responder = SimulatedResponder(queue)
    for decision in decisions:
        for action in decision.actions:
            approval = queue.decided.get(action.action_id)
            if approval and approval.decision == "approve":
                rec = responder.execute(action)
                print(f"EXECUTED (simulated) {rec['action_id']} {rec['action']} {rec['target']} approved by {rec['approved_by']}")
            elif approval:
                print(f"DENIED {action.action_id} by {approval.approver}: {approval.reason}")
    print(f"Pending analyst approval: {', '.join(sorted(queue.pending)) or 'none'}")
    print(f"Model calls: {tally.calls}, estimated cost: ${tally.estimated_cost_usd():.4f}")
    if args.audit_log:
        queue.audit.write_jsonl(args.audit_log)
        print(f"Audit events appended to {args.audit_log}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
