"""Deterministic faithfulness checks: is every claim in the summary traceable to the source?

Two cheap checks catch most unfaithful summaries without a second model call:
1. Evidence check: each evidence_quote must appear verbatim (after whitespace and punctuation
   normalisation) in the source document.
2. Number check: every number in a point must also appear somewhere in the source. Invented,
   rounded or calculated figures are the most damaging summarisation error for business readers.

An optional LLM-as-judge pass can be added on top in live mode, but these checks run on every
request at zero cost and are what the tests pin down.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

_QUOTE_MAP = str.maketrans({"‘": "'", "’": "'", "“": '"', "”": '"', "–": "-", "—": "-"})
_NUMBER = re.compile(r"\d[\d,]*(?:\.\d+)?")


def normalise(text: str) -> str:
    text = text.translate(_QUOTE_MAP).lower()
    text = re.sub(r"[*_`#>]", "", text)
    return re.sub(r"\s+", " ", text).strip()


def numbers_in(text: str) -> set[str]:
    """Numbers as written, without thousands separators or trailing full stops."""
    return {m.group(0).replace(",", "").rstrip(".") for m in _NUMBER.finditer(text)}


@dataclass
class PointCheck:
    point: str
    quote_found: bool
    unsupported_numbers: list[str]

    @property
    def supported(self) -> bool:
        return self.quote_found and not self.unsupported_numbers


@dataclass
class FaithfulnessReport:
    checks: list[PointCheck] = field(default_factory=list)

    @property
    def score(self) -> float:
        return 1.0 if not self.checks else sum(c.supported for c in self.checks) / len(self.checks)

    @property
    def unsupported(self) -> list[PointCheck]:
        return [c for c in self.checks if not c.supported]

    def passed(self, threshold: float = 1.0) -> bool:
        return self.score >= threshold


def check_claim(point: str, quote: str, source_norm: str, source_numbers: set[str]) -> PointCheck:
    quote_norm = normalise(quote)
    quote_found = bool(quote_norm) and len(quote_norm) >= 12 and quote_norm in source_norm
    unsupported = sorted(n for n in numbers_in(point) if n not in source_numbers)
    return PointCheck(point=point, quote_found=quote_found, unsupported_numbers=unsupported)


def check_summary(summary: dict[str, Any], source: str) -> FaithfulnessReport:
    source_norm = normalise(source)
    source_numbers = numbers_in(source)
    report = FaithfulnessReport()
    for kp in summary.get("key_points", []):
        report.checks.append(check_claim(kp["point"], kp["evidence_quote"], source_norm, source_numbers))
    for item in summary.get("action_items", []):
        report.checks.append(check_claim(item["action"], item["evidence_quote"], source_norm, source_numbers))
    # The headline and summary paragraph have no quotes, but their numbers must still be real.
    for free_text in (summary.get("headline", ""), summary.get("summary", "")):
        bad = sorted(n for n in numbers_in(free_text) if n not in source_numbers)
        if bad:
            report.checks.append(PointCheck(point=free_text, quote_found=True, unsupported_numbers=bad))
    return report
