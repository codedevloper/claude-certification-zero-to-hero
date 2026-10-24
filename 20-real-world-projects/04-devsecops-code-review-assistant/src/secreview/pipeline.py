"""End-to-end pipeline: parse -> pre-check -> redact -> Claude review -> validate -> dedupe -> SARIF."""
from __future__ import annotations

from dataclasses import dataclass, field

from . import mock_llm  # noqa: F401  (registers the offline responder; harmless in live mode)
from .dedupe import deduplicate
from .diff_parser import parse_unified_diff
from .models import SEVERITY_RANK, Finding, Rejected
from .prechecks import run_prechecks
from .reviewer import ReviewError, review
from .sarif import to_sarif


@dataclass
class PipelineResult:
    findings: list[Finding]
    rejected: list[Rejected] = field(default_factory=list)
    precheck_count: int = 0
    model_count: int = 0
    model_error: str | None = None
    injection_lines: list[tuple[str, int]] = field(default_factory=list)
    summary: str = ""
    usage: dict = field(default_factory=dict)

    @property
    def sarif(self) -> dict:
        return to_sarif(self.findings)

    def worst_severity_rank(self) -> int:
        return max((SEVERITY_RANK[f.severity] for f in self.findings), default=-1)


def run_review(diff_text: str, client) -> PipelineResult:
    files = parse_unified_diff(diff_text)
    pre = run_prechecks(files)
    result = PipelineResult(findings=[], precheck_count=len(pre.findings), injection_lines=pre.injection_lines)
    model_findings: list[Finding] = []
    if any(fd.added for fd in files):
        try:
            # The model only ever sees the redacted copy of the diff.
            reviewed = review(client, pre.redacted_files, pre.findings)
            model_findings = reviewed.findings
            result.rejected = reviewed.rejected
            result.summary = reviewed.summary
            result.usage = reviewed.usage
        except ReviewError as exc:
            # Fail safe: keep the deterministic findings and tell CI the model step did not run.
            result.model_error = str(exc)
    result.model_count = len(model_findings)
    result.findings = deduplicate(pre.findings + model_findings)
    return result
