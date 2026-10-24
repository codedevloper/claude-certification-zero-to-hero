import pytest

from secreview.diff_parser import DiffTooLarge, parse_unified_diff
from secreview.prechecks import REDACTION, run_prechecks

SMALL = """diff --git a/x.py b/x.py
--- a/x.py
+++ b/x.py
@@ -10,3 +10,3 @@ def f():
 a = 1
-b = 2
+b = 3
 c = 4
\\ No newline at end of file
"""


def test_parser_tracks_new_line_numbers_and_skips_removed_lines():
    [fd] = parse_unified_diff(SMALL)
    assert fd.path == "x.py"
    assert fd.added == {11: "b = 3"}
    assert [n for n, _, _ in fd.lines] == [10, 11, 12]


def test_parser_ignores_deleted_files():
    diff = "--- a/gone.py\n+++ /dev/null\n@@ -1,1 +0,0 @@\n-x = 1\n"
    assert parse_unified_diff(diff) == []


def test_parser_refuses_oversized_diff():
    with pytest.raises(DiffTooLarge):
        parse_unified_diff("+" * 500_000)


def test_sample_diff_line_numbers(sample_diff):
    files = {fd.path: fd for fd in parse_unified_diff(sample_diff)}
    assert set(files) == {"app/config.py", "app/routes/loans.py"}
    assert "pickle.loads" in files["app/routes/loans.py"].added[33]
    assert 1 not in files["app/routes/loans.py"].added  # context line, not added


def test_prechecks_find_secrets_taint_and_injection(sample_diff):
    pre = run_prechecks(parse_unified_diff(sample_diff))
    got = {(f.file, f.line, f.cwe) for f in pre.findings}
    assert ("app/config.py", 5, "CWE-798") in got
    assert ("app/config.py", 6, "CWE-798") in got
    assert ("app/routes/loans.py", 20, "CWE-89") in got
    assert ("app/routes/loans.py", 33, "CWE-502") in got
    assert ("app/routes/loans.py", 40, "CWE-78") in got
    assert ("app/routes/loans.py", 18) in pre.injection_lines


def test_parameterised_query_is_not_flagged(sample_diff):
    pre = run_prechecks(parse_unified_diff(sample_diff))
    assert not any(f.line == 27 and f.cwe == "CWE-89" for f in pre.findings)


def test_redaction_removes_secret_values_but_keeps_names(sample_diff):
    pre = run_prechecks(parse_unified_diff(sample_diff))
    text = "\n".join(t for fd in pre.redacted_files for _, t, _ in fd.lines)
    assert "AKIAFAKEEXAMPLE00KEY" not in text  # synthetic fake key from data/sample.diff
    assert "synthetic-db-pass-not-a-real-value-0001" not in text
    assert f'DB_PASSWORD = "{REDACTION}"' in text


def test_clean_diff_has_no_precheck_findings(clean_diff):
    assert run_prechecks(parse_unified_diff(clean_diff)).findings == []
