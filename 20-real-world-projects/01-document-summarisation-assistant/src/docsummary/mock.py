"""Deterministic offline stand-in for Claude, registered with claude_lab in mock mode.

It is an extractive summariser: it picks source sentences by simple rules, so its quotes are
always verbatim and its numbers always real. That makes it a good baseline for tests; the
tests use separate fake clients to simulate unfaithful or malformed model output.
"""
from __future__ import annotations

import json
import re
from typing import Any

from claude_lab import register_mock

from .prompts import AUDIENCE_GUIDANCE

_LABEL = re.compile(r"^(Decision|Action|Risk):\s*")


def _sentences(text: str) -> list[str]:
    out = []
    for para in re.split(r"\n\s*\n", text):
        para = para.strip()
        if not para or para.startswith("#") or para.lower().startswith("synthetic document"):
            continue
        for line in para.splitlines():
            line = re.sub(r"^\d+\.\s+", "", line.strip())
            for s in re.split(r"(?<=[.!?])\s+(?=[A-Z])", line):
                if len(s) >= 30:
                    out.append(s.strip())
    return out


def _categorise(sentence: str) -> str:
    low = sentence.lower()
    if sentence.startswith("Decision") or "approved" in low:
        return "decision"
    if sentence.startswith("Action") or "owner:" in low or " will " in low:
        return "action"
    if sentence.startswith("Risk") or re.search(r"\b(findings?|breach\w*|delinquency|overspend|late|rated \w+ risk)\b", low):
        return "risk"
    if re.search(r"\d", sentence):
        return "metric"
    return "finding"


_PRIORITY = {"decision": 0, "risk": 1, "action": 2, "metric": 3, "finding": 4}


def extract_points(text: str, limit: int = 6) -> list[dict[str, str]]:
    sentences = _sentences(text)
    ranked = sorted(range(len(sentences)), key=lambda i: (_PRIORITY[_categorise(sentences[i])], i))[:limit]
    points = []
    for i in sorted(ranked):
        s = sentences[i]
        point = _LABEL.sub("", s)
        points.append({"point": point[:1].upper() + point[1:], "evidence_quote": s, "category": _categorise(s)})
    return points


def _between(text: str, tag: str) -> str | None:
    m = re.search(rf"<{tag}>\n?(.*?)\n?</{tag}>", text, re.S)
    return m.group(1) if m else None


def _shorten(text: str, limit: int) -> str:
    if len(text) <= limit:
        return text
    return text[:limit].rsplit(" ", 1)[0] + "..."


def build_summary(points: list[dict[str, str]], audience: str) -> dict[str, Any]:
    guide = AUDIENCE_GUIDANCE[audience]
    focus = guide["focus"]
    order = sorted(range(len(points)), key=lambda i: (focus.index(points[i]["category"]) if points[i]["category"] in focus else len(focus), i))
    chosen = [points[i] for i in order[: guide["max_points"]]]
    actions = []
    for p in points:
        if p["category"] in ("action", "decision"):
            owner = re.search(r"owner:\s*([^,)]+)", p["evidence_quote"])
            actions.append({
                "action": p["point"],
                "owner": owner.group(1).strip() if owner else "Not stated",
                "evidence_quote": p["evidence_quote"],
            })
    risks = [p for p in points if p["category"] == "risk"][:2]
    headline = _shorten(chosen[0]["point"], 110) if chosen else "No key points found"
    return {
        "audience": audience,
        "headline": headline,
        "summary": " ".join(p["point"] for p in chosen[:2]),
        "key_points": chosen,
        "action_items": actions[:5],
        "open_questions": [f"What is the mitigation plan and timeline for this risk: {_shorten(r['point'], 70)}" for r in risks],
    }


@register_mock
def docsummary_responder(**request: Any) -> str | None:
    schema = ((request.get("output_config") or {}).get("format") or {}).get("schema") or {}
    props = schema.get("properties", {})
    user = request["messages"][-1]["content"]
    if not isinstance(user, str):
        return None
    if set(props) == {"key_points"}:
        section = _between(user, "document_section") or ""
        return json.dumps({"key_points": extract_points(section)})
    if "headline" in props and "action_items" in props:
        m = re.search(r"for the '(\w+)' audience", request.get("system", ""))
        audience = m.group(1) if m else "executive"
        partials = _between(user, "partial_summaries")
        if partials is not None:
            points = json.loads(partials)
        else:
            points = extract_points(_between(user, "document") or "", limit=10)
        return json.dumps(build_summary(points, audience))
    return None
