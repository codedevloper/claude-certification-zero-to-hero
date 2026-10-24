"""Single-pass or map-reduce summarisation with validation and faithfulness checks."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from claude_lab import FAST_MODEL, MODEL

from . import prompts
from .chunking import chunk_document, estimate_tokens
from .faithfulness import FaithfulnessReport, check_claim, check_summary, normalise, numbers_in
from .llm import UsageTally, call_structured
from .schemas import AUDIENCES, MAP_SCHEMA, SUMMARY_SCHEMA


@dataclass
class SummaryResult:
    summary: dict[str, Any]
    report: FaithfulnessReport
    mode: str
    chunks: int
    tally: UsageTally
    warnings: list[str] = field(default_factory=list)


def _filter_grounded(points: list[dict[str, Any]], source: str, warnings: list[str], label: str) -> list[dict[str, Any]]:
    """Drop map-step points whose quote is not in the source before they reach the reduce step."""
    source_norm, source_numbers = normalise(source), numbers_in(source)
    kept = []
    for p in points:
        if check_claim(p["point"], p["evidence_quote"], source_norm, source_numbers).supported:
            kept.append(p)
        else:
            warnings.append(f"{label}: dropped ungrounded point: {p['point'][:80]}")
    return kept


def _dedupe(points: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen, out = set(), []
    for p in points:
        key = normalise(p["evidence_quote"])
        if key not in seen:
            seen.add(key)
            out.append(p)
    return out


def summarise(
    text: str,
    *,
    client: Any,
    title: str,
    audience: str = "executive",
    chunk_chars: int = 3500,
    single_pass_max_tokens: int = 1500,
    map_model: str = FAST_MODEL,
    reduce_model: str = MODEL,
    drop_unsupported: bool = True,
) -> SummaryResult:
    """Summarise `text` for `audience`.

    Documents under `single_pass_max_tokens` (estimated) go in one request. Longer documents are
    chunked; each chunk is summarised by a cheaper model (map), then one call on the main model
    merges the grounded partial results (reduce). The thresholds are deliberately small so the
    bundled sample exercises both paths; production values would be far larger.
    """
    if audience not in AUDIENCES:
        raise ValueError(f"audience must be one of {AUDIENCES}")
    if not text.strip():
        raise ValueError("document is empty")
    tally = UsageTally()
    warnings: list[str] = []

    if estimate_tokens(text) <= single_pass_max_tokens:
        mode, n_chunks = "single-pass", 1
        user = prompts.reduce_user_from_document(text, title)
    else:
        chunks = chunk_document(text, max_chars=chunk_chars)
        mode, n_chunks = "map-reduce", len(chunks)
        partials: list[dict[str, Any]] = []
        for chunk in chunks:
            result = call_structured(
                client,
                system=prompts.MAP_SYSTEM,
                user=prompts.map_user(chunk.text, chunk.index, len(chunks), title),
                schema=MAP_SCHEMA,
                max_tokens=2000,
                model=map_model,
                tally=tally,
            )
            partials.extend(_filter_grounded(result["key_points"], text, warnings, f"chunk {chunk.index + 1}"))
        user = prompts.reduce_user_from_partials(_dedupe(partials), title)

    summary = call_structured(
        client,
        system=prompts.reduce_system(audience),
        user=user,
        schema=SUMMARY_SCHEMA,
        max_tokens=4000,
        model=reduce_model,
        tally=tally,
    )
    if summary["audience"] != audience:
        warnings.append(f"model returned audience '{summary['audience']}', corrected to '{audience}'")
        summary["audience"] = audience

    limit = prompts.AUDIENCE_GUIDANCE[audience]["max_points"]
    if len(summary["key_points"]) > limit:
        warnings.append(f"trimmed key points from {len(summary['key_points'])} to {limit}")
        summary["key_points"] = summary["key_points"][:limit]

    report = check_summary(summary, text)
    if drop_unsupported and report.unsupported:
        bad = {c.point for c in report.unsupported}
        for key, field_name in (("key_points", "point"), ("action_items", "action")):
            before = len(summary[key])
            summary[key] = [x for x in summary[key] if x[field_name] not in bad]
            if len(summary[key]) < before:
                warnings.append(f"removed {before - len(summary[key])} unsupported item(s) from {key}")
    return SummaryResult(summary, report, mode, n_chunks, tally, warnings)
