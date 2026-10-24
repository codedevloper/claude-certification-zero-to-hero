"""End-to-end pipeline in mock mode, request shape, and handling of bad model output."""
from __future__ import annotations

import pytest

from docsummary.__main__ import main
from docsummary.llm import ModelOutputError, UsageTally, call_structured
from docsummary.pipeline import summarise
from docsummary.schemas import SUMMARY_SCHEMA

MEMO = "vendor-change-memo.md"
REVIEW = "q3-operations-review.md"


def _good_summary(points):
    return {"audience": "executive", "headline": "h", "summary": "s", "key_points": points, "action_items": [], "open_questions": []}


@pytest.mark.parametrize("audience", ["executive", "engineering", "compliance"])
def test_long_document_uses_map_reduce_and_is_faithful(mock_client, data_dir, audience):
    text = (data_dir / REVIEW).read_text()
    result = summarise(text, client=mock_client, title="Q3 review", audience=audience)
    assert result.mode == "map-reduce" and result.chunks >= 2
    assert result.tally.calls == result.chunks + 1
    assert result.summary["audience"] == audience
    assert result.report.score == 1.0
    assert 0 < len(result.summary["key_points"]) <= {"executive": 5, "engineering": 8, "compliance": 6}[audience]


def test_short_document_uses_single_pass(mock_client, data_dir):
    result = summarise((data_dir / MEMO).read_text(), client=mock_client, title="Memo", audience="compliance")
    assert result.mode == "single-pass" and result.tally.calls == 1
    assert result.report.passed()


def test_audiences_produce_different_selections(mock_client, data_dir):
    text = (data_dir / REVIEW).read_text()
    ex = summarise(text, client=mock_client, title="t", audience="executive").summary["key_points"]
    co = summarise(text, client=mock_client, title="t", audience="compliance").summary["key_points"]
    assert [p["point"] for p in ex] != [p["point"] for p in co]


def test_requests_follow_current_api_rules(scripted):
    client = scripted([_good_summary([])])
    call_structured(client, system="s", user="u", schema=SUMMARY_SCHEMA)
    req = client.requests[0]
    assert req["output_config"]["format"] == {"type": "json_schema", "schema": SUMMARY_SCHEMA}
    assert req["model"] == "claude-opus-5-5"
    for banned in ("temperature", "top_p", "top_k", "tool_choice"):
        assert banned not in req
    assert req["messages"][-1]["role"] == "user"


def test_unsupported_points_are_removed(scripted):
    source = "Payments reached 184,200 in Q3. The incident lasted 38 minutes."
    summary = _good_summary([
        {"point": "Payments reached 184,200.", "evidence_quote": "Payments reached 184,200 in Q3.", "category": "metric"},
        {"point": "The incident lasted 45 minutes.", "evidence_quote": "The incident lasted 38 minutes.", "category": "finding"},
    ])
    result = summarise(source, client=scripted([summary]), title="t", audience="executive")
    assert result.report.score == 0.5
    assert [p["point"] for p in result.summary["key_points"]] == ["Payments reached 184,200."]
    assert any("removed 1 unsupported" in w for w in result.warnings)


def test_ungrounded_map_points_never_reach_reduce(scripted):
    text = "## Section\n\n" + "\n\n".join(f"Paragraph {i} reports that volume was {i}00 units in the period." for i in range(1, 200))
    map_reply = {"key_points": [
        {"point": "Volume was 100 units.", "evidence_quote": "Paragraph 1 reports that volume was 100 units in the period.", "category": "metric"},
        {"point": "Revenue doubled.", "evidence_quote": "Revenue doubled year on year.", "category": "finding"},
    ]}
    from docsummary.chunking import chunk_document
    n = len(chunk_document(text, 3500))
    client = scripted([map_reply] * n + [_good_summary([])])
    result = summarise(text, client=client, title="t")
    reduce_prompt = client.requests[-1]["messages"][0]["content"]
    assert "Revenue doubled" not in reduce_prompt
    assert reduce_prompt.count("Paragraph 1 reports") == 1  # deduplicated across chunks
    assert any("dropped ungrounded" in w for w in result.warnings)


def test_audience_mismatch_and_overlong_lists_are_corrected(scripted):
    pts = [{"point": f"Point {i}.", "evidence_quote": "Payments reached 184,200 in Q3.", "category": "metric"} for i in range(9)]
    reply = _good_summary(pts) | {"audience": "engineering"}
    result = summarise("Payments reached 184,200 in Q3.", client=scripted([reply]), title="t", audience="executive", drop_unsupported=False)
    assert result.summary["audience"] == "executive"
    assert len(result.summary["key_points"]) == 5


@pytest.mark.parametrize("reply, stop, message", [
    ("not json", "end_turn", "not valid JSON"),
    ({"audience": "executive"}, "end_turn", "schema validation"),
    ("{}", "max_tokens", "max_tokens"),
    ("", "refusal", "declined"),
])
def test_bad_responses_raise(scripted, reply, stop, message):
    with pytest.raises(ModelOutputError, match=message):
        call_structured(scripted([reply], stop_reason=stop), system="s", user="u", schema=SUMMARY_SCHEMA)


def test_empty_document_and_bad_audience_rejected(mock_client):
    with pytest.raises(ValueError):
        summarise("   ", client=mock_client, title="t")
    with pytest.raises(ValueError):
        summarise("text", client=mock_client, title="t", audience="board")


def test_usage_tally_cost():
    class U:
        input_tokens, output_tokens = 1_000_000, 100_000
    tally = UsageTally()
    tally.add("claude-haiku-5-5", U())
    assert tally.estimated_cost_usd() == pytest.approx(0.10 + 0.05)


def test_cli_runs_non_interactively(capsys):
    assert main(["--audience", "executive", "--strict"]) == 0
    out = capsys.readouterr().out
    assert "mode=map-reduce" in out and "faithfulness=1.00" in out


def test_cli_rejects_missing_file(tmp_path):
    assert main(["--file", str(tmp_path / "missing.md")]) == 1
