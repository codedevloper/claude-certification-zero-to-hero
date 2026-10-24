"""Scoring and weak-area analysis.

Scores are raw percent-correct. They are NOT Anthropic scaled scores (100–1,000,
cut score 720); the official scaling method is not public, so no conversion is attempted.
Multiple-response items are scored all-or-nothing, which is an assumption of this
tool, not a published rule of the official exam.
"""
from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass, field

from .bank import Question, Track

WEAK_THRESHOLD = 70.0  # percent; below this a domain is flagged for review


def parse_answer(raw: str) -> tuple[str, ...]:
    letters = [c for c in raw.upper() if c.isalpha()]
    return tuple(sorted(set(letters)))


def is_correct(q: Question, given: tuple[str, ...] | None) -> bool:
    return given is not None and tuple(sorted(given)) == q.answer


@dataclass
class Result:
    track: Track
    questions: list[Question]
    responses: dict[str, tuple[str, ...] | None]
    elapsed_seconds: float
    timed_out: bool = False
    domain_scores: dict[int, tuple[int, int]] = field(default_factory=dict)

    def __post_init__(self) -> None:
        tally: dict[int, list[int]] = defaultdict(lambda: [0, 0])
        for q in self.questions:
            tally[q.domain][1] += 1
            if is_correct(q, self.responses.get(q.id)):
                tally[q.domain][0] += 1
        self.domain_scores = {d: (c, t) for d, (c, t) in sorted(tally.items())}

    @property
    def correct(self) -> int:
        return sum(c for c, _ in self.domain_scores.values())

    @property
    def total(self) -> int:
        return len(self.questions)

    @property
    def percent(self) -> float:
        return 100.0 * self.correct / self.total if self.total else 0.0

    def domain_percent(self, d: int) -> float:
        c, t = self.domain_scores[d]
        return 100.0 * c / t if t else 0.0

    def missed(self) -> list[Question]:
        return [q for q in self.questions if not is_correct(q, self.responses.get(q.id))]

    def weak_domains(self) -> list[int]:
        return [d for d in self.domain_scores if self.domain_percent(d) < WEAK_THRESHOLD]

    def recommendations(self) -> list[str]:
        """Modules to revisit, most-missed first."""
        counts = Counter(q.module for q in self.missed() if q.module)
        return [m for m, _ in counts.most_common(8)]

    def to_record(self, mode: str) -> dict:
        return {
            "track": self.track.code,
            "mode": mode,
            "total": self.total,
            "correct": self.correct,
            "percent": round(self.percent, 1),
            "elapsed_seconds": round(self.elapsed_seconds),
            "timed_out": self.timed_out,
            "domains": {str(d): {"correct": c, "total": t} for d, (c, t) in self.domain_scores.items()},
        }
