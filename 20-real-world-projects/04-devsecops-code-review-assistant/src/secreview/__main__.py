"""Command line entry point.

    python run.py                                   # review data/sample.diff (mock mode, offline)
    python run.py --diff pr.diff --sarif-out out.sarif --fail-on high
    git diff origin/main...HEAD | python run.py --diff -

Exit codes: 0 = completed and below --fail-on threshold; 1 = findings at or above the
threshold; 2 = the model step failed and --require-model was set; 3 = bad input.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from ._lab import PROJECT_ROOT, claude_lab
from .diff_parser import DiffTooLarge
from .models import SEVERITIES, SEVERITY_RANK
from .pipeline import run_review


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="secreview", description="Security review of a unified diff.")
    parser.add_argument("--diff", default=str(PROJECT_ROOT / "data" / "sample.diff"),
                        help="path to a unified diff, or '-' for stdin (default: data/sample.diff)")
    parser.add_argument("--sarif-out", help="write SARIF 2.1.0 to this path")
    parser.add_argument("--fail-on", choices=["none", *SEVERITIES], default="none",
                        help="exit 1 if any finding is at or above this severity (default: none)")
    parser.add_argument("--require-model", action="store_true",
                        help="exit 2 if the Claude review step fails instead of continuing with pre-checks only")
    parser.add_argument("--json", action="store_true", help="print the full result as JSON")
    args = parser.parse_args(argv)

    try:
        diff_text = sys.stdin.read() if args.diff == "-" else Path(args.diff).read_text(encoding="utf-8")
        claude_lab.banner("secreview: DevSecOps code review assistant")
        result = run_review(diff_text, claude_lab.get_client())
    except (OSError, DiffTooLarge) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 3

    if args.sarif_out:
        Path(args.sarif_out).write_text(json.dumps(result.sarif, indent=2), encoding="utf-8")

    if args.json:
        print(json.dumps({
            "findings": [f.to_dict() for f in result.findings],
            "rejected": [{"reason": r.reason, "raw": r.raw} for r in result.rejected],
            "model_error": result.model_error, "usage": result.usage,
        }, indent=2))
    else:
        print(f"Pre-check findings: {result.precheck_count}   Model findings accepted: {result.model_count}   "
              f"Rejected model items: {len(result.rejected)}")
        if result.injection_lines:
            where = ", ".join(f"{p}:{n}" for p, n in result.injection_lines)
            print(f"Reviewer-directed text detected (ignored as instructions, reported as a finding): {where}")
        if result.model_error:
            print(f"WARNING model step skipped: {result.model_error}")
        print(f"\n{len(result.findings)} finding(s) after de-duplication:\n")
        for f in result.findings:
            print(f"  [{f.severity.upper():8}] {f.cwe:9} {f.file}:{f.line}  {f.title}")
            print(f"             sources={','.join(f.sources)} confidence={f.confidence}")
            print(f"             suggested fix (not applied): {f.fix}")
        for r in result.rejected:
            print(f"  [REJECTED] {r.reason}")
        if args.sarif_out:
            print(f"\nSARIF written to {args.sarif_out}")

    if result.model_error and args.require_model:
        return 2
    if args.fail_on != "none" and result.worst_severity_rank() >= SEVERITY_RANK[args.fail_on]:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
