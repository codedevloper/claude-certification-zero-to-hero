"""Local progress tracking.

Stored as JSON in ~/.claude-cert-zero-to-hero/progress.json (override with the
MOCKEXAM_PROGRESS environment variable). Only question IDs, scores and timestamps
are stored — never names, emails or any other personal information.
"""
from __future__ import annotations

import json
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path

DEFAULT_PATH = Path.home() / ".claude-cert-zero-to-hero" / "progress.json"


def progress_path() -> Path:
    return Path(os.environ.get("MOCKEXAM_PROGRESS", DEFAULT_PATH)).expanduser()


def load() -> dict:
    path = progress_path()
    if not path.exists():
        return {"version": 1, "attempts": [], "questions": {}}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {"version": 1, "attempts": [], "questions": {}}
    data.setdefault("attempts", [])
    data.setdefault("questions", {})
    return data


def save(data: dict) -> None:
    path = progress_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    # Atomic write so an interrupted run never corrupts history.
    fd, tmp = tempfile.mkstemp(dir=path.parent, prefix=".progress-", suffix=".json")
    with os.fdopen(fd, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2)
    os.replace(tmp, path)


def record(data: dict, attempt: dict, per_question: dict[str, bool]) -> dict:
    attempt = {**attempt, "finished_at": datetime.now(timezone.utc).isoformat(timespec="seconds")}
    data["attempts"].append(attempt)
    for qid, ok in per_question.items():
        stats = data["questions"].setdefault(qid, {"seen": 0, "correct": 0, "last_correct": None})
        stats["seen"] += 1
        stats["correct"] += int(ok)
        stats["last_correct"] = ok
    return data


def weak_question_ids(data: dict) -> set[str]:
    """Questions answered wrongly the last time they were seen."""
    return {qid for qid, s in data["questions"].items() if s.get("last_correct") is False}


def reset() -> None:
    path = progress_path()
    if path.exists():
        path.unlink()
