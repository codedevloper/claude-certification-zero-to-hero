"""Append-only, hash-chained audit trace.

Each record carries the SHA-256 of the previous record, so deleting or editing a record
breaks `verify()`. In production, ship records to write-once storage as they are produced;
the chain then lets an auditor prove the exported trace is complete and unmodified.
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

GENESIS = "0" * 64
MAX_FIELD = 4_000  # keep huge tool outputs out of the trace; store a digest instead


def _shrink(value):
    text = json.dumps(value, default=str, sort_keys=True)
    if len(text) <= MAX_FIELD:
        return value
    return {"truncated": True, "sha256": hashlib.sha256(text.encode()).hexdigest(), "preview": text[:500]}


class AuditLog:
    def __init__(self, run_id: str):
        self.run_id = run_id
        self.records: list[dict] = []

    def log(self, actor: str, event: str, **data) -> dict:
        prev = self.records[-1]["hash"] if self.records else GENESIS
        body = {
            "seq": len(self.records) + 1,
            "run_id": self.run_id,
            "ts": datetime.now(timezone.utc).isoformat(timespec="milliseconds"),
            "actor": actor,
            "event": event,
            "data": {k: _shrink(v) for k, v in data.items()},
            "prev_hash": prev,
        }
        body["hash"] = hashlib.sha256(json.dumps(body, sort_keys=True, default=str).encode()).hexdigest()
        self.records.append(body)
        return body

    def verify(self) -> bool:
        prev = GENESIS
        for i, rec in enumerate(self.records, 1):
            body = {k: v for k, v in rec.items() if k != "hash"}
            if rec["seq"] != i or rec["prev_hash"] != prev:
                return False
            if hashlib.sha256(json.dumps(body, sort_keys=True, default=str).encode()).hexdigest() != rec["hash"]:
                return False
            prev = rec["hash"]
        return True

    def write_jsonl(self, path: Path) -> None:
        Path(path).write_text("".join(json.dumps(r, default=str) + "\n" for r in self.records), encoding="utf-8")
