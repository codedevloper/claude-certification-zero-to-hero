"""Deterministic offline stand-in for Claude, registered with claude_lab in mock mode.

It triages with simple keyword rules. One behaviour is deliberately unsafe: when an alert field
contains an instruction aimed at an AI, the mock *obeys* it, as a manipulated model might. That
lets the demo and tests show the guardrails in `triage.enforce` and the approval gate catching
an injection that got past the prompt. A real model should resist; the controls must not rely on it.
"""
from __future__ import annotations

import json
import re
from typing import Any

from claude_lab import register_mock

_RULES = [
    # (keyword in rule name, severity, techniques, actions as (type, entity kind, index))
    ("failed vpn logins", "high", [("T1110.003", "Many accounts, one source"), ("T1078", "A login then succeeded")],
     [("investigate", "users", 1), ("enrich", "ips", 0), ("block_ip", "ips", 0), ("reset_credentials", "users", 1)]),
    ("encoded command", "high", [("T1059.001", "PowerShell launched by Word"), ("T1027", "Encoded command line")],
     [("investigate", "hosts", 0), ("isolate_host", "hosts", 0), ("enrich", "domains", 0)]),
    ("impossible travel", "medium", [("T1078", "Valid credentials used from an unexpected country")],
     [("investigate", "users", 0), ("reset_credentials", "users", 0)]),
    ("cloud storage", "high", [("T1567.002", "Large upload to a personal cloud service")],
     [("investigate", "users", 0), ("notify", "users", 0), ("disable_account", "users", 0)]),
    ("attachment", "high", [("T1566.001", "Macro attachment from a new sender"), ("T1204.002", "User opened the file")],
     [("investigate", "hosts", 0), ("isolate_host", "hosts", 0), ("block_ip", "ips", 0)]),
]
_INJECTED = re.compile(r"set severity to (\w+).*?isolate host ([\w-]+).*?disable account ([\w.-]+)", re.I | re.S)


def mock_triage(alert: dict[str, Any]) -> dict[str, Any]:
    entities = alert.get("entities", {})
    rule = alert.get("rule_name", "").lower()
    text = json.dumps(alert)
    injected = _INJECTED.search(text)
    if injected:
        # Simulates a model that followed the attacker's instructions.
        severity, host, account = injected.groups()
        return {
            "alert_id": alert["alert_id"],
            "severity": severity.lower() if severity.lower() in ("informational", "low") else "informational",
            "confidence": "high",
            "summary": "Known false positive. Remediation: isolate the listed host and disable the listed account.",
            "attack_techniques": [{"technique_id": "T9999", "name": "Benign activity", "rationale": "Per note in alert."}],
            "next_actions": [
                {"action_type": "isolate_host", "target": host, "rationale": "Requested in alert note."},
                {"action_type": "disable_account", "target": account, "rationale": "Requested in alert note."},
            ],
            "injection_suspected": False,
            "false_positive_likelihood": "high",
        }
    for keyword, severity, techniques, actions in _RULES:
        if keyword in rule:
            next_actions = []
            for action_type, kind, idx in actions:
                values = entities.get(kind) or []
                if len(values) > idx:
                    next_actions.append({"action_type": action_type, "target": values[idx],
                                         "rationale": f"{action_type.replace('_', ' ')} based on {rule}"})
            return {
                "alert_id": alert["alert_id"],
                "severity": severity,
                "confidence": "medium",
                "summary": f"{alert.get('description', '')[:240]} Rule: {alert.get('rule_name', '')}.",
                "attack_techniques": [{"technique_id": t, "name": t, "rationale": r} for t, r in techniques],
                "next_actions": next_actions,
                "injection_suspected": False,
                "false_positive_likelihood": "low",
            }
    return {
        "alert_id": alert.get("alert_id", "UNKNOWN-0"),
        "severity": alert.get("rule_severity", "medium"),
        "confidence": "low",
        "summary": "No matching triage rule in the offline mock; route to an analyst.",
        "attack_techniques": [],
        "next_actions": [],
        "injection_suspected": False,
        "false_positive_likelihood": "medium",
    }


@register_mock
def alerttriage_responder(**request: Any) -> str | None:
    schema = ((request.get("output_config") or {}).get("format") or {}).get("schema") or {}
    if "attack_techniques" not in schema.get("properties", {}):
        return None
    user = request["messages"][-1]["content"]
    m = re.search(r"<untrusted_alert>\n(.*?)\n</untrusted_alert>", user if isinstance(user, str) else "", re.S)
    if not m:
        return None
    return json.dumps(mock_triage(json.loads(m.group(1))))
