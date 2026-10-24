"""Deterministic offline stand-in for Claude, registered with claude_lab in mock mode.

It behaves like a careful but simple reader: it picks the supplied document that shares the most
content words with the question, answers with that document's best-matching sentence, and says
"not answerable" when the overlap is weak. It never invents text, so tests that need bad model
behaviour use scripted fake clients instead.
"""
from __future__ import annotations

import html
import json
import re
from typing import Any

from claude_lab import register_mock

from .bm25 import tokenize

_DOC = re.compile(r'<document id="([^"]+)"[^>]*>\n(.*?)\n</document>', re.S)


def mock_answer(question: str, documents: list[tuple[str, str]]) -> dict[str, Any]:
    q = set(tokenize(question))
    best: tuple[int, str, str] | None = None
    for doc_id, text in documents:
        overlap = len(q & set(tokenize(text)))
        if best is None or overlap > best[0]:
            best = (overlap, doc_id, text)
    if not q or best is None or best[0] < 2 or best[0] / len(q) < 0.6:
        return {"answerable": False, "answer": "", "citations": [], "confidence": "low"}
    _, doc_id, text = best
    sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if s.strip()]
    covered: set[str] = set()
    picked: list[int] = []
    for _ in range(2):  # greedily pick up to two sentences that cover the most question words
        # Ties go to sentences with figures (most policy answers are a number), then to earlier ones.
        gains = [(len((q & set(tokenize(s))) - covered), bool(re.search(r"\d", s)), -i)
                 for i, s in enumerate(sentences) if i not in picked]
        if not gains or max(gains)[0] == 0:
            break
        _, _, neg_i = max(gains)
        picked.append(-neg_i)
        covered |= q & set(tokenize(sentences[-neg_i]))
    answer = " ".join(sentences[i] for i in sorted(picked))
    return {
        "answerable": True,
        "answer": answer,
        "citations": [doc_id],
        "confidence": "high" if best[0] / len(q) >= 0.8 else "medium",
    }


@register_mock
def kbqa_responder(**request: Any) -> str | None:
    schema = ((request.get("output_config") or {}).get("format") or {}).get("schema") or {}
    if "answerable" not in schema.get("properties", {}):
        return None
    user = request["messages"][-1]["content"]
    if not isinstance(user, str):
        return None
    m = re.search(r"<question>(.*?)</question>", user, re.S)
    question = html.unescape(m.group(1)) if m else ""
    documents = [(html.unescape(i), html.unescape(t)) for i, t in _DOC.findall(user)]
    return json.dumps(mock_answer(question, documents))
