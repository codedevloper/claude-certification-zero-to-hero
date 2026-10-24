#!/usr/bin/env python3
"""Validate every practice-question bank.

Checks: JSON Schema, globally unique IDs, ID/track/domain consistency, objective
exists in the registry and belongs to the file's domain, answer keys are valid
options, multiple-response `select` matches the key, every distractor has a
"why incorrect" rationale, explanations do not name a different letter as correct,
referenced modules exist, and near-duplicate stems are flagged.
"""
from __future__ import annotations

import json
import re
import sys
from difflib import SequenceMatcher

from common import ROOT, SCHEMA_PATH, Report, objective_index, question_files

try:
    import jsonschema
except ImportError:  # pragma: no cover - optional dependency
    jsonschema = None

CORRECT_CLAIM = re.compile(r"\b(?:option\s+)?\(?([A-F])\)?\s+is\s+(?:the\s+)?(?:correct|right|best)\b", re.IGNORECASE)


def validate() -> Report:
    report = Report("practice questions")
    objectives = objective_index()
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    validator = jsonschema.Draft202012Validator(schema) if jsonschema else None
    if validator is None:
        report.warn("jsonschema not installed; structural schema validation skipped")

    seen: dict[str, str] = {}
    stems: list[tuple[str, str]] = []

    for path in question_files():
        rel = path.relative_to(ROOT)
        try:
            bank = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            report.error(f"{rel}: invalid JSON ({exc})")
            continue
        if validator:
            for err in validator.iter_errors(bank):
                loc = "/".join(str(p) for p in err.path)
                report.error(f"{rel}: schema: {loc}: {err.message}")
        track, domain = bank.get("track"), bank.get("domain")

        for q in bank.get("questions", []):
            qid = q.get("id", "<missing id>")
            where = f"{rel} {qid}"
            if qid in seen:
                report.error(f"{where}: duplicate ID (also in {seen[qid]})")
            seen[qid] = str(rel)
            if not qid.startswith(f"{track}-D{domain}-"):
                report.error(f"{where}: ID does not match file track/domain {track}/D{domain}")

            obj = objectives.get(q.get("objective", ""))
            if obj is None:
                report.error(f"{where}: unknown objective {q.get('objective')}")
            elif obj["track"] != track or obj["domain"] != domain:
                report.error(f"{where}: objective {q['objective']} is not in {track} domain {domain}")

            options = set(q.get("options", {}))
            answer = q.get("answer", [])
            if not set(answer) <= options:
                report.error(f"{where}: answer {answer} not among options {sorted(options)}")
            if q.get("type") == "single" and len(answer) != 1:
                report.error(f"{where}: single-answer question must have exactly one key")
            if q.get("type") == "multiple":
                if len(answer) < 2:
                    report.error(f"{where}: multiple-response question needs 2+ keys")
                if q.get("select") != len(answer):
                    report.error(f"{where}: select={q.get('select')} but answer has {len(answer)} keys")
            wrong = options - set(answer)
            why = set(q.get("why_incorrect", {}))
            if why != wrong:
                report.error(f"{where}: why_incorrect keys {sorted(why)} must equal distractors {sorted(wrong)}")

            for claimed in CORRECT_CLAIM.findall(q.get("explanation", "")):
                if claimed.upper() not in answer:
                    report.error(f"{where}: explanation claims {claimed} is correct but key is {answer}")

            module = q.get("module", "")
            if module and not (ROOT / module.split("#")[0]).exists():
                report.error(f"{where}: module path does not exist: {module}")

            stem = (q.get("scenario", "") + " " + q.get("question", "")).lower()
            stems.append((qid, stem))

    # Near-duplicate detection (cheap pre-filter on length, then ratio).
    stems.sort(key=lambda s: len(s[1]))
    for i, (id_a, a) in enumerate(stems):
        for id_b, b in stems[i + 1:]:
            if len(b) > len(a) * 1.3:
                break
            if SequenceMatcher(None, a, b).ratio() > 0.85:
                report.error(f"{id_a} and {id_b} are near-duplicates (>85% similar)")

    check_cueing(report)
    report.warn(f"{len(seen)} questions checked") if seen else report.error("no questions found")
    return report


# Bank-level answer-cueing limits. A well-written bank should not be answerable by test-taking tricks.
MAX_LONGEST_KEY_RATE = 0.40      # share of items where the key is the longest option (or the k longest)
POSITION_TOLERANCE = (0.5, 1.6)  # each letter's share of keys vs. its expected share
MIN_EXPECTED_FOR_POSITION_CHECK = 6


def longest_is_key(q: dict) -> bool:
    opts = q.get("options", {})
    k = len(q.get("answer", []))
    if not opts or not k:
        return False
    longest = sorted(opts, key=lambda letter: -len(opts[letter]))[:k]
    return set(longest) == set(q["answer"])


def cueing_stats(questions: list[dict]) -> dict:
    """Longest-option rate and per-letter observed/expected key counts for one bank."""
    expected: dict[str, float] = {}
    observed: dict[str, int] = {}
    for q in questions:
        opts = q.get("options", {})
        share = len(q.get("answer", [])) / max(len(opts), 1)
        for letter in opts:
            expected[letter] = expected.get(letter, 0.0) + share
        for letter in q.get("answer", []):
            observed[letter] = observed.get(letter, 0) + 1
    longest = sum(longest_is_key(q) for q in questions)
    return {
        "longest_rate": longest / len(questions) if questions else 0.0,
        "positions": {letter: (observed.get(letter, 0), round(expected[letter], 1)) for letter in sorted(expected)},
    }


def check_cueing(report: Report) -> None:
    banks: dict[str, list[dict]] = {}
    for path in question_files():
        bank = json.loads(path.read_text(encoding="utf-8"))
        banks.setdefault(bank.get("track", "?"), []).extend(bank.get("questions", []))
    for track, questions in sorted(banks.items()):
        stats = cueing_stats(questions)
        if stats["longest_rate"] > MAX_LONGEST_KEY_RATE:
            report.error(
                f"{track}: the key is the longest option in {stats['longest_rate']:.0%} of items "
                f"(limit {MAX_LONGEST_KEY_RATE:.0%}); balance option lengths"
            )
        low, high = POSITION_TOLERANCE
        for letter, (obs, exp) in stats["positions"].items():
            if exp >= MIN_EXPECTED_FOR_POSITION_CHECK and not low * exp <= obs <= high * exp:
                report.error(
                    f"{track}: option {letter} is the key {obs} times vs ~{exp} expected; "
                    "run python tools/shuffle_options.py"
                )


if __name__ == "__main__":
    r = validate()
    r.print()
    sys.exit(0 if r.ok else 1)
