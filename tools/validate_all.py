#!/usr/bin/env python3
"""Run every repository check. Exit non-zero if any fails.

  python tools/validate_all.py            # content checks (fast, offline)
  python tools/validate_all.py --labs     # also run every lab in mock mode
"""
from __future__ import annotations

import sys

import build_coverage
import build_mock_forms
import build_page_nav
import build_web_bundle
import check_exam_claims
import check_links
import flashcards
import run_lab_smoke
import scan_secrets
import validate_questions


def main() -> int:
    results = []
    for name, fn in [
        ("questions", lambda: validate_questions.validate()),
        ("flashcards", lambda: flashcards.validate()[0]),
        ("links", check_links.check),
        ("exam claims", check_exam_claims.check),
        ("secrets", scan_secrets.scan),
    ]:
        report = fn()
        report.print()
        results.append(report.ok)
    results.append(build_coverage.main(check=True) == 0)
    results.append(build_mock_forms.main(check=True) == 0)
    results.append(build_page_nav.main(check=True) == 0)
    results.append(build_web_bundle.main(check=True) == 0)
    if "--labs" in sys.argv:
        results.append(run_lab_smoke.main([]) == 0)
    ok = all(results)
    print("\nALL CHECKS PASSED" if ok else "\nSOME CHECKS FAILED")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
