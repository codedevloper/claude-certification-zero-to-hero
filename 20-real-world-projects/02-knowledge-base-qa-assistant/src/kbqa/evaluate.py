"""Offline evaluation: retrieval quality, answer accuracy and refusal behaviour on a labelled set."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .answer import Answer, answer_question
from .kb import KnowledgeBase
from .llm import UsageTally


@dataclass
class EvalResult:
    rows: list[dict[str, Any]] = field(default_factory=list)
    tally: UsageTally = field(default_factory=UsageTally)

    def _answerable(self) -> list[dict[str, Any]]:
        return [r for r in self.rows if r["answerable"]]

    def _unanswerable(self) -> list[dict[str, Any]]:
        return [r for r in self.rows if not r["answerable"]]

    @property
    def recall_at_k(self) -> float:
        rows = self._answerable()
        return sum(r["retrieval_hit"] for r in rows) / max(1, len(rows))

    @property
    def mrr(self) -> float:
        rows = self._answerable()
        return sum(r["reciprocal_rank"] for r in rows) / max(1, len(rows))

    @property
    def answer_accuracy(self) -> float:
        rows = self._answerable()
        return sum(r["correct"] for r in rows) / max(1, len(rows))

    @property
    def false_refusal_rate(self) -> float:
        rows = self._answerable()
        return sum(r["status"] == "refused" for r in rows) / max(1, len(rows))

    @property
    def refusal_accuracy(self) -> float:
        rows = self._unanswerable()
        return sum(r["status"] == "refused" for r in rows) / max(1, len(rows))

    def metrics(self) -> dict[str, float]:
        return {
            "recall_at_k": round(self.recall_at_k, 3),
            "mrr": round(self.mrr, 3),
            "answer_accuracy": round(self.answer_accuracy, 3),
            "false_refusal_rate": round(self.false_refusal_rate, 3),
            "refusal_accuracy": round(self.refusal_accuracy, 3),
        }


def load_eval_set(path: Path) -> list[dict[str, Any]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    questions = data["questions"]
    ids = [q["id"] for q in questions]
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate question ids in eval set")
    for q in questions:
        if q["answerable"] and not (q.get("expected_doc") and q.get("expected_terms")):
            raise ValueError(f"{q['id']}: answerable questions need expected_doc and expected_terms")
    return questions


def score_row(q: dict[str, Any], ans: Answer) -> dict[str, Any]:
    retrieved_docs = [cid.split("#")[0] for cid, _ in ans.retrieved]
    expected = q.get("expected_doc")
    rank = retrieved_docs.index(expected) + 1 if expected in retrieved_docs else 0
    cited_docs = {c.split("#")[0] for c in ans.citations}
    correct = (
        q["answerable"]
        and ans.status == "answered"
        and expected in cited_docs
        and all(t.lower() in ans.text.lower() for t in q.get("expected_terms", []))
    )
    return {
        "id": q["id"],
        "answerable": q["answerable"],
        "status": ans.status,
        "retrieval_hit": rank > 0,
        "reciprocal_rank": 1 / rank if rank else 0.0,
        "correct": bool(correct),
        "reason": ans.reason,
    }


def run_eval(kb: KnowledgeBase, client: Any, questions: list[dict[str, Any]], k: int = 4) -> EvalResult:
    result = EvalResult()
    for q in questions:
        ans = answer_question(q["question"], kb, client, k=k, tally=result.tally)
        result.rows.append(score_row(q, ans))
    return result
