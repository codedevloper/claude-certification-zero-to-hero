import json

from claude_lab import get_client

from secreview.__main__ import main
from secreview.dedupe import deduplicate
from secreview.models import Finding
from secreview.pipeline import run_review
from secreview.reviewer import ReviewError


def _f(line, cwe="CWE-89", sev="high", src="claude", conf=0.8):
    return Finding("a.py", line, cwe, sev, "t", "d", "f", conf, [src])


def test_dedupe_merges_same_location_and_boosts_agreement():
    out = deduplicate([_f(5, src="precheck:R1", conf=0.8), _f(5, sev="critical", conf=0.7)])
    assert len(out) == 1
    assert out[0].severity == "critical"
    assert out[0].confidence == 0.9
    assert out[0].sources == ["claude", "precheck:R1"]


def test_dedupe_keeps_adjacent_secrets_separate():
    assert len(deduplicate([_f(5, cwe="CWE-798"), _f(6, cwe="CWE-798")])) == 2


def test_dedupe_merges_multiline_reviewer_comment():
    assert len(deduplicate([_f(18, cwe="CWE-1427"), _f(19, cwe="CWE-1427")])) == 1


def test_pipeline_end_to_end_mock(sample_diff):
    result = run_review(sample_diff, get_client())
    keys = {(f.file, f.line, f.cwe) for f in result.findings}
    assert ("app/routes/loans.py", 24, "CWE-862") in keys     # only the model can see missing authZ
    assert ("app/routes/loans.py", 20, "CWE-89") in keys
    assert len(result.rejected) == 2                         # hallucinated line + malformed item
    assert len(keys) == len(result.findings)                 # no duplicates survive
    assert result.model_error is None


def test_injection_comment_does_not_suppress_findings(sample_diff):
    result = run_review(sample_diff, get_client())
    loans = [f for f in result.findings if f.file == "app/routes/loans.py" and f.cwe != "CWE-1427"]
    assert len(loans) >= 4
    assert any(f.cwe == "CWE-1427" for f in result.findings)


def test_model_failure_falls_back_to_prechecks(sample_diff, monkeypatch):
    def boom(*a, **k):
        raise ReviewError("stop_reason=refusal")
    monkeypatch.setattr("secreview.pipeline.review", boom)
    result = run_review(sample_diff, get_client())
    assert result.model_error and result.findings
    assert all(any(s.startswith("precheck") for s in f.sources) for f in result.findings)


def test_sarif_shape(sample_diff):
    sarif = run_review(sample_diff, get_client()).sarif
    assert sarif["version"] == "2.1.0" and "sarif-2.1.0" in sarif["$schema"]
    run = sarif["runs"][0]
    rule_ids = {r["id"] for r in run["tool"]["driver"]["rules"]}
    for res in run["results"]:
        assert res["ruleId"] in rule_ids
        assert res["level"] in {"error", "warning", "note"}
        region = res["locations"][0]["physicalLocation"]["region"]
        assert isinstance(region["startLine"], int) and region["startLine"] >= 1
        assert "fixes" not in res  # suggestions only, never machine-applied
    json.dumps(sarif)  # serialisable


def test_cli_writes_sarif_and_honours_fail_on(tmp_path, capsys):
    out = tmp_path / "r.sarif"
    assert main(["--sarif-out", str(out)]) == 0
    assert json.loads(out.read_text())["version"] == "2.1.0"
    assert main(["--fail-on", "high"]) == 1
    capsys.readouterr()


def test_cli_clean_diff_passes_gate(tmp_path):
    from secreview._lab import PROJECT_ROOT
    assert main(["--diff", str(PROJECT_ROOT / "data" / "clean.diff"), "--fail-on", "low"]) == 0


def test_cli_missing_file_is_input_error():
    assert main(["--diff", "does-not-exist.diff"]) == 3
