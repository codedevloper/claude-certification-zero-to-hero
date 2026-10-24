"""Merge findings that describe the same weakness at the same place.

Two findings are duplicates when they share the file and CWE and the same line. A few CWEs
describe things that naturally span several lines (a multi-line comment aimed at the reviewer),
so LINE_TOLERANCE widens the match for those only. A blanket tolerance would wrongly merge two
different secrets committed on adjacent lines.
The merged finding keeps the highest severity, the highest confidence, the union of sources and
the most detailed description. Agreement between a pre-check and the model raises confidence.
"""
from __future__ import annotations

from .models import SEVERITY_RANK, Finding

LINE_TOLERANCE = {"CWE-1427": 2}  # per-CWE; everything else must match the exact line
AGREEMENT_BONUS = 0.1


def deduplicate(findings: list[Finding]) -> list[Finding]:
    merged: list[Finding] = []
    for f in sorted(findings, key=lambda x: (x.file, x.cwe, x.line)):
        match = next((m for m in merged if m.file == f.file and m.cwe == f.cwe
                      and abs(m.line - f.line) <= LINE_TOLERANCE.get(f.cwe, 0)), None)
        if match is None:
            merged.append(Finding(**{**f.to_dict(), "sources": list(f.sources)}))
            continue
        if SEVERITY_RANK[f.severity] > SEVERITY_RANK[match.severity]:
            match.severity = f.severity
        if len(f.description) > len(match.description):
            match.description = f.description
        if len(f.fix) > len(match.fix):
            match.fix = f.fix
        match.confidence = max(match.confidence, f.confidence)
        match.sources = sorted(set(match.sources) | set(f.sources))
    for m in merged:
        kinds = {s.split(":")[0] for s in m.sources}
        if {"precheck", "claude"} <= kinds:
            m.confidence = round(min(1.0, m.confidence + AGREEMENT_BONUS), 2)
    return sorted(merged, key=lambda x: (-SEVERITY_RANK[x.severity], x.file, x.line))
