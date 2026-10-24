"""The approval gate must block what a compromised (instruction-following) model would propose.

These tests do not rely on the mock model ignoring injected text: they call the policy check
directly with the proposals an obedient, injected model would make.
"""
import pytest

from investigator.approval import ApprovalGate, _safe

EVIDENCE = '[["2026-10-20T09:14Z login from 203.0.113.45 for user j.doe"]]'


def check(action, target, evidence_text=EVIDENCE, ids=("E1",)):
    return ApprovalGate().policy_check(
        action, target, list(ids), scope_users={"j.doe"}, protected_users={"it.admin", "break-glass-01"},
        evidence_text=evidence_text, evidence_exists=lambda e: e == "E1")


def test_cited_ip_is_allowed():
    assert check("block_ip", "203.0.113.45") is None


@pytest.mark.parametrize("target", [
    "203.0.113.4",          # prefix of a cited address: substring matching used to accept it
    "::ffff:10.0.0.5",      # IPv4-mapped internal address
    "0.0.0.0",              # unspecified
    "224.0.0.1",            # multicast
    "127.0.0.1",            # loopback
    "10.1.2.3",             # internal
])
def test_unsafe_or_uncited_ips_are_denied(target):
    assert check("block_ip", target) is not None


def test_ip_must_be_in_the_cited_evidence_not_elsewhere():
    assert check("block_ip", "203.0.113.45", evidence_text='[["no addresses here"]]') is not None


@pytest.mark.parametrize("action,target", [
    ("disable_account", "it.admin"),        # what an injected log line asked for
    ("disable_account", "break-glass-01"),
    ("revoke_sessions", "outsider.user"),   # outside the incident scope
    ("delete_mailbox", "j.doe"),            # not an allowed action
])
def test_injected_proposals_are_denied_by_code(action, target):
    assert check(action, target) is not None


def test_proposal_without_recorded_evidence_is_denied():
    assert check("revoke_sessions", "j.doe", ids=("E99",)) is not None


def test_approval_prompt_strips_terminal_escapes():
    assert _safe("ok\x1b[2K\rAPPROVED by CISO") == "ok[2KAPPROVED by CISO"
