"""Evidence chain: every claim must cite log lines that exist in the log store."""
from __future__ import annotations

from dataclasses import dataclass, field

from .logstore import LogStore

MAX_CLAIM = 600


class EvidenceError(ValueError):
    pass


@dataclass
class Evidence:
    id: str
    claim: str
    citations: list[str]
    recorded_by: str
    excerpts: dict[str, dict] = field(default_factory=dict)  # copied from the store, not from the model


class EvidenceChain:
    def __init__(self, store: LogStore):
        self.store = store
        self.items: dict[str, Evidence] = {}

    def add(self, claim: str, citations: list[str], recorded_by: str) -> Evidence:
        claim = (claim or "").strip()
        if not claim:
            raise EvidenceError("claim is empty")
        if len(claim) > MAX_CLAIM:
            raise EvidenceError(f"claim longer than {MAX_CLAIM} characters")
        if not citations:
            raise EvidenceError("a claim needs at least one citation")
        unknown = [c for c in citations if not self.store.has(c)]
        if unknown:
            raise EvidenceError(f"unknown citation(s): {', '.join(unknown)}")
        ev = Evidence(id=f"E{len(self.items) + 1}", claim=claim, citations=list(dict.fromkeys(citations)),
                      recorded_by=recorded_by, excerpts={c: self.store.get(c) for c in citations})
        self.items[ev.id] = ev
        return ev

    def has(self, evidence_id: str) -> bool:
        return evidence_id in self.items
