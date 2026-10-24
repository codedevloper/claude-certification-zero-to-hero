import json

import pytest

from investigator.approval import ApprovalGate
from investigator.audit import AuditLog
from investigator.budget import Budget, BudgetExceeded
from investigator.evidence import EvidenceError
from investigator.report import ReportError, validate_report
from investigator.tools import ROLE_TOOLS, TOOL_DEFS, dispatch, tool_params


def test_logstore_citations_and_filters(make_ctx):
    ctx = make_ctx()
    assert ctx.store.get("auth:7")["ip"] == "203.0.113.45"
    hits = ctx.store.search("auth", fields={"user": "dana.reyes", "ip": "203.0.113.45"},
                            start="2026-10-21T02:48:00Z", end="2026-10-21T02:51:00Z")
    assert [h["cite"] for h in hits["records"]] == ["auth:5", "auth:6", "auth:7"]


def test_audit_chain_detects_tampering():
    log = AuditLog("run-test")
    for i in range(3):
        log.log("tester", "event", n=i)
    assert log.verify()
    log.records[1]["data"]["n"] = 99
    assert not log.verify()
    log2 = AuditLog("run-test")
    log2.log("a", "x")
    log2.log("a", "y")
    del log2.records[0]
    assert not log2.verify()


def test_evidence_requires_real_citations(make_ctx):
    ev = make_ctx().evidence
    with pytest.raises(EvidenceError):
        ev.add("claim", [], "orchestrator")
    with pytest.raises(EvidenceError):
        ev.add("claim", ["auth:999"], "orchestrator")
    e = ev.add("claim", ["auth:7"], "orchestrator")
    assert e.id == "E1" and e.excerpts["auth:7"]["user"] == "dana.reyes"


def test_specialists_have_no_write_or_control_tools():
    for role in ("identity_analyst", "network_analyst", "endpoint_analyst"):
        assert all(TOOL_DEFS[t][0] == "read" for t in ROLE_TOOLS[role])
    assert all(t["strict"] and t["input_schema"]["additionalProperties"] is False for t in tool_params("orchestrator"))


def test_dispatcher_enforces_role_allow_list(make_ctx):
    ctx = make_ctx()
    out, err = dispatch(ctx, "identity_analyst", "propose_action",
                        {"action": "disable_account", "target": "dana.reyes", "justification": "x", "evidence_ids": []})
    assert err and "not available" in out
    out, err = dispatch(ctx, "orchestrator", "search_auth_logs", {})
    assert err
    assert ctx.gate.decisions == []


@pytest.mark.parametrize("args", [
    {"user": "Robert'); DROP TABLE", "ip": "", "event": "", "start": "", "end": ""},
    {"user": "", "ip": "not-an-ip", "event": "", "start": "", "end": ""},
    {"user": "", "ip": "", "event": "", "start": "yesterday", "end": ""},
    {"user": "", "ip": "", "event": "", "start": "", "end": "", "extra": "x"},
    {"user": ""},
])
def test_dispatcher_validates_inputs(make_ctx, args):
    out, err = dispatch(make_ctx(), "identity_analyst", "search_auth_logs", args)
    assert err and out.startswith("Invalid input")


def test_tool_results_are_labelled_untrusted(make_ctx):
    out, err = dispatch(make_ctx(), "identity_analyst", "search_auth_logs",
                        {"user": "dana.reyes", "ip": "", "event": "login_success", "start": "", "end": ""})
    payload = json.loads(out)
    assert not err and "untrusted" in payload["note"] and payload["total_matches"] == 3


def test_tool_call_budget():
    b = Budget(max_tool_calls=1)
    b.before_tool_call()
    with pytest.raises(BudgetExceeded):
        b.before_tool_call()


def _propose(ctx, action, target, ids):
    return dispatch(ctx, "orchestrator", "propose_action",
                    {"action": action, "target": target, "justification": "test", "evidence_ids": ids})


def test_policy_blocks_protected_out_of_scope_and_uncited(tmp_path, make_ctx):
    approvals = tmp_path / "a.json"
    approvals.write_text(json.dumps({"approved": ["disable_account:it.admin", "disable_account:sam.okafor",
                                                  "block_ip:10.8.0.77"]}))
    ctx = make_ctx(gate=ApprovalGate("file", approvals))
    ctx.evidence.add("VPN address used", ["vpn:3"], "orchestrator")
    # Approved in the file, but policy wins: protected account, out of scope, internal IP, no evidence.
    assert "protected" in _propose(ctx, "disable_account", "it.admin", ["E1"])[0]
    assert "outside the incident scope" in _propose(ctx, "disable_account", "sam.okafor", ["E1"])[0]
    assert "internal" in _propose(ctx, "block_ip", "10.8.0.77", ["E1"])[0]
    assert "evidence" in _propose(ctx, "revoke_sessions", "dana.reyes", [])[0]
    assert all(d.status == "denied_by_policy" for d in ctx.gate.decisions)


def test_interactive_approval_uses_human_answer(make_ctx):
    answers = iter(["y", "n"])
    ctx = make_ctx(gate=ApprovalGate("interactive", prompt=lambda _msg: next(answers)))
    ctx.evidence.add("takeover", ["auth:7"], "orchestrator")
    _propose(ctx, "revoke_sessions", "dana.reyes", ["E1"])
    _propose(ctx, "disable_account", "dana.reyes", ["E1"])
    assert [d.status for d in ctx.gate.decisions] == ["executed_simulated", "denied_by_approver"]


def test_report_validation(make_ctx):
    ev = make_ctx().evidence
    ev.add("x", ["auth:7"], "orchestrator")
    good = {"verdict": "likely_compromise", "confidence": 0.7, "summary": "s",
            "timeline": [{"ts": "2026-10-21T02:50:17Z", "event": "e", "evidence_ids": ["E1"]}],
            "findings": [{"statement": "f", "evidence_ids": ["E1"]}], "open_questions": []}
    assert validate_report(good, ev)["verdict"] == "likely_compromise"
    for bad in ({**good, "verdict": "pwned"}, {**good, "confidence": 3},
                {**good, "findings": [{"statement": "f", "evidence_ids": ["E9"]}]},
                {**good, "findings": []},
                {**good, "timeline": [{"ts": "later", "event": "e", "evidence_ids": []}]}):
        with pytest.raises(ReportError):
            validate_report(bad, ev)
