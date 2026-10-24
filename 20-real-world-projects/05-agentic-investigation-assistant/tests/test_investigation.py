import json

from claude_lab import Message, TextBlock, Usage, get_client

from investigator.__main__ import main, run
from investigator.budget import Budget


class RecordingClient:
    """Wraps the mock client and keeps every request for contract checks."""

    def __init__(self):
        self.inner = get_client()
        self.requests = []
        self.messages = self

    def create(self, **request):
        self.requests.append({**request, "messages": list(request["messages"])})  # snapshot: the loop appends later
        return self.inner.messages.create(**request)


def test_end_to_end_mock_investigation(make_ctx):
    ctx = make_ctx()
    final = run(ctx)
    assert final["run_status"] == "completed"
    assert final["verdict"] == "confirmed_compromise"
    assert final["audit"]["chain_valid"] is True
    # Every evidence item cites real log lines; every finding cites recorded evidence.
    ids = {e["id"] for e in final["evidence"]}
    assert all(ctx.store.has(c) for e in final["evidence"] for c in e["citations"])
    assert all(f["evidence_ids"] and set(f["evidence_ids"]) <= ids for f in final["findings"])
    # Non-interactive default: nothing executed, everything waits for a human.
    assert final["actions"] and all(a["status"] == "queued_for_approval" for a in final["actions"])


def test_planted_instruction_is_not_followed(make_ctx):
    final = run(make_ctx())
    assert final["verdict"] != "benign"
    assert not any(a["target"] == "it.admin" for a in final["actions"])


def test_requests_follow_current_api_rules(make_ctx):
    client = RecordingClient()
    run(make_ctx(client=client))
    assert client.requests
    for req in client.requests:
        for banned in ("temperature", "top_p", "top_k", "tool_choice"):
            assert banned not in req
        assert req["thinking"] == {"type": "adaptive"}
        assert req["messages"][-1]["role"] == "user"
        assert req["model"] in ("claude-opus-5-5", "claude-haiku-5-5")
    orch = [r for r in client.requests if r["system"].startswith("ROLE: orchestrator")]
    assert orch and all(r["model"] == "claude-opus-5-5" for r in orch)


def test_budget_exhaustion_yields_partial_report(make_ctx):
    final = run(make_ctx(budget=Budget(max_model_calls=4)))
    assert final["verdict"] == "inconclusive"
    assert "budget exhausted" in final["run_status"]
    assert final["audit"]["chain_valid"]


def test_refusal_stops_cleanly(make_ctx):
    class Refuses:
        def __init__(self):
            self.messages = self

        def create(self, **request):
            return Message(content=[TextBlock("")], model="stub", stop_reason="refusal", usage=Usage(5, 0))

    final = run(make_ctx(client=Refuses()))
    assert final["verdict"] == "inconclusive" and "refusal" in final["run_status"]
    assert final["actions"] == []


def test_cli_writes_report_and_audit(tmp_path, capsys):
    report, audit = tmp_path / "r.json", tmp_path / "a.jsonl"
    assert main(["--report-out", str(report), "--audit-out", str(audit)]) == 0
    data = json.loads(report.read_text())
    assert data["incident_id"] == "INC-2026-0417"
    lines = [json.loads(x) for x in audit.read_text().splitlines()]
    assert lines[0]["event"] == "run_start" and lines[-1]["event"] == "run_end"
    assert any(r["event"] == "approval_decision" for r in lines)
    capsys.readouterr()


def test_cli_rejects_file_mode_without_approvals():
    assert main(["--approval-mode", "file"]) == 3
