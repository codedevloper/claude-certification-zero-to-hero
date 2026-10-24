"""Read-only access to the synthetic log sources, with stable citation IDs.

Every record gets a citation ID "<source>:<line number>" (1-based line in the JSONL file).
The evidence chain and the final report may only cite IDs that exist here, which is how
the system proves that each claim is grounded in a real log line.
"""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

SOURCES = {
    "auth": "auth_logs.jsonl",
    "vpn": "vpn_logs.jsonl",
    "endpoint": "endpoint_logs.jsonl",
    "directory": "directory.jsonl",
    "intel": "ip_reputation.jsonl",
}
MAX_RESULTS = 25  # keeps tool results (and so context and cost) bounded


def parse_ts(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


class LogStore:
    def __init__(self, data_dir: Path):
        self.records: dict[str, dict] = {}
        self.by_source: dict[str, list[tuple[str, dict]]] = {}
        for source, filename in SOURCES.items():
            rows = []
            path = Path(data_dir) / filename
            for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
                if not line.strip():
                    continue
                cite = f"{source}:{lineno}"
                record = json.loads(line)
                self.records[cite] = record
                rows.append((cite, record))
            self.by_source[source] = rows

    def has(self, cite: str) -> bool:
        return cite in self.records

    def get(self, cite: str) -> dict:
        return self.records[cite]

    def search(self, source: str, *, fields: dict[str, str], start: str = "", end: str = "") -> dict:
        """Exact-match filter on the given fields plus an optional time window."""
        lo = parse_ts(start) if start else None
        hi = parse_ts(end) if end else None
        hits = []
        for cite, rec in self.by_source[source]:
            if any(v and str(rec.get(k, "")) != v for k, v in fields.items()):
                continue
            if (lo or hi) and "ts" in rec:
                ts = parse_ts(rec["ts"])
                if (lo and ts < lo) or (hi and ts > hi):
                    continue
            hits.append({"cite": cite, "record": rec})
        return {"total_matches": len(hits), "returned": min(len(hits), MAX_RESULTS),
                "records": hits[:MAX_RESULTS]}
