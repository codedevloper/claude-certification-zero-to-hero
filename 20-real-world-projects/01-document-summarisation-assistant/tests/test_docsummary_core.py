"""Chunking, schema validation, faithfulness checks and rendering."""
from __future__ import annotations

import pytest

from docsummary.chunking import chunk_document, estimate_tokens
from docsummary.faithfulness import check_summary, normalise, numbers_in
from docsummary.render import escape_md, render_markdown
from docsummary.schemas import MAP_SCHEMA, SUMMARY_SCHEMA, validate

SOURCE = (
    "# Report\n\nLoan servicing processed 184,200 payments in Q3, up 6.4% on Q2.\n\n"
    "Decision: the director approved a pilot starting in October."
)


def _summary(**overrides):
    base = {
        "audience": "executive",
        "headline": "Payments grew 6.4%",
        "summary": "Payments rose to 184,200.",
        "key_points": [
            {"point": "Payments rose 6.4% to 184,200.", "evidence_quote": "processed 184,200 payments in Q3", "category": "metric"}
        ],
        "action_items": [],
        "open_questions": [],
    }
    base.update(overrides)
    return base


def test_chunks_respect_budget_and_keep_all_text(data_dir):
    text = (data_dir / "q3-operations-review.md").read_text()
    chunks = chunk_document(text, max_chars=1500)
    assert len(chunks) > 3
    assert all(len(c.text) <= 1500 for c in chunks)
    joined = " ".join(c.text for c in chunks)
    for sentence in ("Card payments failed for 38 minutes", "Operations headcount was 412"):
        assert sentence in joined


def test_chunks_carry_section_heading():
    text = "## 4. Technology\n\n" + "\n\n".join(f"Paragraph {i} " + "x" * 300 for i in range(6))
    chunks = chunk_document(text, max_chars=700)
    assert len(chunks) > 1
    assert all(c.text.startswith("## 4. Technology") for c in chunks)


def test_long_paragraph_is_split_on_sentences():
    para = " ".join(f"Sentence number {i} is here." for i in range(100))
    chunks = chunk_document(para, max_chars=400)
    assert all(len(c.text) <= 400 for c in chunks)
    assert chunks[0].text.endswith(".")


def test_chunk_budget_minimum():
    with pytest.raises(ValueError):
        chunk_document("text", max_chars=10)


def test_estimate_tokens():
    assert estimate_tokens("a" * 400) == 100


def test_schema_accepts_valid_summary():
    assert validate(_summary(), SUMMARY_SCHEMA) == []


@pytest.mark.parametrize(
    "bad, fragment",
    [
        (_summary(audience="board"), "not one of"),
        ({k: v for k, v in _summary().items() if k != "headline"}, "missing required field 'headline'"),
        (_summary(extra="x"), "unexpected field 'extra'"),
        (_summary(key_points=[{"point": "p", "evidence_quote": "q", "category": "gossip"}]), "not one of"),
        (_summary(key_points="not a list"), "expected array"),
    ],
)
def test_schema_rejects_invalid_summary(bad, fragment):
    errors = validate(bad, SUMMARY_SCHEMA)
    assert any(fragment in e for e in errors), errors


def test_map_schema_rejects_missing_quote():
    assert validate({"key_points": [{"point": "x", "category": "risk"}]}, MAP_SCHEMA)


def test_normalise_and_numbers():
    assert normalise("It’s   *bold*\n") == "it's bold"
    assert numbers_in("184,200 payments, 6.4% and 31 December.") == {"184200", "6.4", "31"}


def test_faithful_summary_scores_one():
    report = check_summary(_summary(), SOURCE)
    assert report.score == 1.0 and report.passed()


def test_invented_number_is_flagged():
    bad = _summary(key_points=[{"point": "Payments rose 9.1%.", "evidence_quote": "processed 184,200 payments in Q3", "category": "metric"}])
    report = check_summary(bad, SOURCE)
    assert report.unsupported[0].unsupported_numbers == ["9.1"]
    assert not report.passed()


def test_fabricated_quote_is_flagged():
    bad = _summary(key_points=[{"point": "Payments rose.", "evidence_quote": "payments rose sharply in every region", "category": "metric"}])
    assert not check_summary(bad, SOURCE).unsupported[0].quote_found


def test_numbers_in_headline_are_checked():
    report = check_summary(_summary(headline="Payments up 12%"), SOURCE)
    assert report.score < 1.0


def test_render_escapes_markdown_injection():
    s = _summary(headline="[click](https://example.invalid) <script>")
    out = render_markdown(s)
    assert "[click](" not in out and "<script>" not in out
    assert escape_md("a|b") == "a\\|b"


def test_render_formats_differ_by_audience():
    exec_md = render_markdown(_summary())
    comp_md = render_markdown(_summary(audience="compliance"))
    assert "What matters" in exec_md and "Source:" not in exec_md
    assert "Risk and control points" in comp_md and "Source:" in comp_md
