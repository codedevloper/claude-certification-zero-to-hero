"""Human approval gate for write (containment) actions.

Policy is checked in code before any human is asked:
  * the action must be on the allow-list,
  * the target must be in the incident scope (or, for IPs, appear in cited evidence),
  * protected accounts (privileged or break-glass) can never be actioned by the agent,
  * the proposal must cite recorded evidence.
Only then does the configured approver decide. Approved actions are SIMULATED: this
project never touches a real identity provider, VPN or firewall.
"""
from __future__ import annotations

import ipaddress
import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

ACTIONS = ("revoke_sessions", "disable_account", "block_ip")
# Internal ranges the agent may never block. Checked explicitly because Python's `is_private`
# also covers the documentation ranges (RFC 5737) that this project's synthetic data uses.
INTERNAL_NETS = [ipaddress.ip_network(n) for n in ("10.0.0.0/8", "172.16.0.0/12", "192.168.0.0/16",
                                                   "127.0.0.0/8", "169.254.0.0/16", "fc00::/7", "::1/128")]
IP_CANDIDATE = re.compile(r"[0-9A-Fa-f:.]{3,45}")
CONTROL_CHARS = re.compile(r"[\x00-\x08\x0b-\x1f\x7f-\x9f]")


def _canonical_ip(value: str):
    """Parse an IP and unwrap IPv4-mapped IPv6 (::ffff:10.0.0.5 is really 10.0.0.5)."""
    ip = ipaddress.ip_address(value.strip())
    mapped = getattr(ip, "ipv4_mapped", None)
    return mapped or ip


def _ips_in(text: str) -> set:
    found = set()
    for token in IP_CANDIDATE.findall(text):
        try:
            found.add(_canonical_ip(token))
        except ValueError:
            continue
    return found


def _safe(text: str) -> str:
    """Strip control characters (ANSI escapes, carriage returns) before showing model text to a human."""
    return CONTROL_CHARS.sub("", str(text))


@dataclass
class Decision:
    action: str
    target: str
    status: str          # executed_simulated | queued_for_approval | denied_by_policy | denied_by_approver
    reason: str
    evidence_ids: list[str] = field(default_factory=list)
    justification: str = ""


class ApprovalGate:
    def __init__(self, mode: str = "queue", approvals_file: Path | None = None,
                 prompt: Callable[[str], str] | None = None):
        if mode not in ("queue", "file", "interactive"):
            raise ValueError("approval mode must be queue, file or interactive")
        self.mode = mode
        self.prompt = prompt or input
        self.approved: set[str] = set()
        self.approver = "none"
        if mode == "file":
            if approvals_file is None:
                raise ValueError("--approvals is required with --approval-mode file")
            data = json.loads(Path(approvals_file).read_text(encoding="utf-8"))
            self.approved = {str(x) for x in data.get("approved", [])}
            self.approver = str(data.get("approved_by", "approval file"))
        self.decisions: list[Decision] = []

    def policy_check(self, action: str, target: str, evidence_ids: list[str], *, scope_users: set[str],
                     protected_users: set[str], evidence_text: str, evidence_exists: Callable[[str], bool]) -> str | None:
        if action not in ACTIONS:
            return f"action '{action}' is not on the allow-list"
        if not evidence_ids or not all(evidence_exists(e) for e in evidence_ids):
            return "proposal must cite at least one recorded evidence ID"
        if action in ("revoke_sessions", "disable_account"):
            if target in protected_users:
                return f"'{target}' is a protected account; only a human may act on it"
            if target not in scope_users:
                return f"'{target}' is outside the incident scope"
        if action == "block_ip":
            try:
                ip = _canonical_ip(target)
            except ValueError:
                return f"'{target}' is not an IP address"
            if (any(ip in net for net in INTERNAL_NETS if net.version == ip.version)
                    or ip.is_unspecified or ip.is_loopback or ip.is_link_local or ip.is_multicast or ip.is_reserved):
                return "blocking internal, reserved or special-purpose addresses is not allowed from the agent"
            # Exact address match against the evidence this proposal cites (not a substring:
            # 203.0.113.4 must not match 203.0.113.45).
            if ip not in _ips_in(evidence_text):
                return "IP does not appear in the cited evidence"
        return None

    def decide(self, action: str, target: str, justification: str, evidence_ids: list[str],
               policy_error: str | None) -> Decision:
        key = f"{action}:{target}"
        if policy_error:
            d = Decision(action, target, "denied_by_policy", policy_error, evidence_ids, justification)
        elif self.mode == "queue":
            d = Decision(action, target, "queued_for_approval", "non-interactive run: waiting for a human",
                         evidence_ids, justification)
        elif self.mode == "file":
            ok = key in self.approved
            d = Decision(action, target, "executed_simulated" if ok else "queued_for_approval",
                         f"approved by {self.approver}" if ok else "not in approval file", evidence_ids, justification)
        else:
            answer = self.prompt(f"\nAPPROVAL REQUIRED: {_safe(key)}\n  justification: {_safe(justification)}\n"
                                 f"  evidence: {_safe(', '.join(evidence_ids))}\nApprove? [y/N] ").strip().lower()
            ok = answer in ("y", "yes")
            d = Decision(action, target, "executed_simulated" if ok else "denied_by_approver",
                         "approved interactively" if ok else "declined interactively", evidence_ids, justification)
        self.decisions.append(d)
        return d
