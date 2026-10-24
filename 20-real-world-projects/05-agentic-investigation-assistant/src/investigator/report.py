"""Final report: validation of the model's submission and rendering for humans.

The model proposes the narrative (verdict, findings, timeline). The system adds the parts
the model must not be trusted to state: which actions were actually executed or queued
(from the approval gate), the evidence excerpts (from the log store), budget use and the
audit-chain status.
"""
from __future__ import annotations

import re
from datetime import datetime

VERDICTS = ("confirmed_compromise", "likely_compromise", "benign", "inconclusive")
CONTROL = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")


class ReportError(ValueError):
    pass


def _text(value, limit=2_000) -> str:
    return CONTROL.sub("", str(value))[:limit]


def validate_report(raw: dict, evidence) -> dict:
    errors = []
    if raw.get("verdict") not in VERDICTS:
        errors.append(f"verdict must be one of {VERDICTS}")
    conf = raw.get("confidence")
    if isinstance(conf, bool) or not isinstance(conf, (int, float)) or not 0 <= conf <= 1:
        errors.append("confidence must be a number between 0 and 1")
    if not str(raw.get("summary", "")).strip():
        errors.append("summary is empty")
    findings = raw.get("findings") or []
    if raw.get("verdict") in ("confirmed_compromise", "likely_compromise") and not findings:
        errors.append("a compromise verdict needs at least one finding")
    for i, f in enumerate(findings, 1):
        ids = f.get("evidence_ids") or []
        if not ids:
            errors.append(f"finding {i} cites no evidence")
        missing = [e for e in ids if not evidence.has(e)]
        if missing:
            errors.append(f"finding {i} cites unknown evidence {missing}")
    for i, t in enumerate(raw.get("timeline") or [], 1):
        try:
            datetime.fromisoformat(str(t.get("ts", "")).replace("Z", "+00:00"))
        except ValueError:
            errors.append(f"timeline entry {i} has an invalid timestamp")
        missing = [e for e in (t.get("evidence_ids") or []) if not evidence.has(e)]
        if missing:
            errors.append(f"timeline entry {i} cites unknown evidence {missing}")
    if errors:
        raise ReportError("; ".join(errors))
    return {
        "verdict": raw["verdict"],
        "confidence": float(conf),
        "summary": _text(raw["summary"]),
        "timeline": sorted(({"ts": _text(t["ts"], 40), "event": _text(t["event"], 400),
                             "evidence_ids": list(t["evidence_ids"])} for t in raw.get("timeline") or []),
                           key=lambda t: t["ts"]),
        "findings": [{"statement": _text(f["statement"], 800), "evidence_ids": list(f["evidence_ids"])}
                     for f in findings],
        "open_questions": [_text(q, 400) for q in raw.get("open_questions") or []],
    }


def build_final(incident: dict, report: dict | None, evidence, decisions, budget, audit, stop_reason: str) -> dict:
    """Combine the validated model report with facts the system itself is the source of."""
    if report is None:  # budget exhausted, refusal or step limit: still produce something useful
        report = {"verdict": "inconclusive", "confidence": 0.0,
                  "summary": f"Investigation stopped before a report was submitted ({stop_reason}). "
                             "The recorded evidence below is complete up to that point; a human must finish it.",
                  "timeline": [], "findings": [], "open_questions": ["Complete the investigation manually."]}
    return {
        "incident_id": incident["incident_id"],
        "title": incident["title"],
        "run_status": stop_reason,
        **report,
        "evidence": [{"id": e.id, "claim": e.claim, "citations": e.citations, "recorded_by": e.recorded_by,
                      "excerpts": e.excerpts} for e in evidence.items.values()],
        "actions": [{"action": d.action, "target": d.target, "status": d.status, "reason": d.reason,
                     "evidence_ids": d.evidence_ids} for d in decisions],
        "budget": budget.snapshot(),
        "audit": {"records": len(audit.records), "chain_valid": audit.verify(), "run_id": audit.run_id},
    }


def render_markdown(final: dict) -> str:
    lines = [f"# Investigation report {final['incident_id']}", "",
             f"**{final['title']}**", "",
             f"- Verdict: **{final['verdict']}** (confidence {final['confidence']:.2f})",
             f"- Run status: {final['run_status']}",
             f"- Budget used: {final['budget']}",
             f"- Audit trace: {final['audit']['records']} records, hash chain valid = {final['audit']['chain_valid']}",
             "", "## Summary", "", final["summary"], "", "## Findings", ""]
    lines += [f"{i}. {f['statement']} [{', '.join(f['evidence_ids'])}]" for i, f in enumerate(final["findings"], 1)] \
        or ["None."]
    lines += ["", "## Timeline", ""]
    lines += [f"- {t['ts']}: {t['event']} [{', '.join(t['evidence_ids'])}]" for t in final["timeline"]] or ["None."]
    lines += ["", "## Evidence chain", ""]
    for e in final["evidence"]:
        lines.append(f"- **{e['id']}** {e['claim']}")
        lines.append(f"  - cites: {', '.join(e['citations'])} (recorded by {e['recorded_by']})")
    lines += ["", "## Containment actions", ""]
    lines += [f"- {a['action']} `{a['target']}`: **{a['status']}** ({a['reason']})" for a in final["actions"]] \
        or ["None proposed."]
    lines += ["", "## Open questions", ""]
    lines += [f"- {q}" for q in final["open_questions"]] or ["None."]
    return "\n".join(lines) + "\n"
