"""Data types shared across the pipeline."""
from __future__ import annotations

from dataclasses import asdict, dataclass, field

SEVERITIES = ("critical", "high", "medium", "low", "info")
SEVERITY_RANK = {name: rank for rank, name in enumerate(reversed(SEVERITIES))}  # info=0 ... critical=4


@dataclass
class Finding:
    """One security finding tied to an added line of the diff."""

    file: str
    line: int
    cwe: str            # "CWE-89"
    severity: str       # one of SEVERITIES
    title: str
    description: str
    fix: str            # human-readable suggestion; never applied automatically
    confidence: float   # 0.0 - 1.0
    sources: list[str] = field(default_factory=list)  # "precheck:<rule>" and/or "claude"

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class Rejected:
    """A model-proposed finding that failed validation, kept for the audit trail."""

    raw: dict
    reason: str
