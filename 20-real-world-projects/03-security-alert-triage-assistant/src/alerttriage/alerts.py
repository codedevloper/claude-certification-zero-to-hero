"""Load and sanitise SIEM alerts before any of their content reaches the model.

Alert fields are attacker-influenced: an email subject, a command line, a user agent or a file
name can all carry text written by the attacker. This module:
- keeps only the expected top-level fields;
- validates entity values (host names, user names, IPs, domains) with strict patterns, so the
  entity list can later be trusted as the set of allowed containment targets;
- truncates long strings and limits nesting depth;
- scans every string for text that looks like instructions to an AI system.
"""
from __future__ import annotations

import ipaddress
import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .schemas import SEVERITIES

MAX_STRING = 1000
MAX_DEPTH = 4
ENTITY_KINDS = ("hosts", "users", "ips", "domains")
_ENTITY_PATTERNS = {
    "hosts": re.compile(r"^[A-Za-z0-9][A-Za-z0-9-]{0,62}$"),
    "users": re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$"),
    "domains": re.compile(r"^(?=.{1,253}$)([A-Za-z0-9-]{1,63}\.)+[A-Za-z]{2,63}$"),
}
INJECTION_PATTERNS = [
    re.compile(p, re.I)
    for p in (
        r"ignore (all |any )?(previous|prior|above) instructions",
        r"\b(system|admin) (note|message|prompt)\b.{0,40}\b(ai|assistant|triage|model)\b",
        r"\bnote to (the )?(ai|assistant|model|llm)\b",
        r"\b(set|change|lower) (the )?severity to\b",
        r"\b(isolate|disable|block|delete|wipe)\b.{0,40}\bto complete remediation\b",
        r"\byou are now\b",
        r"\bknown false positive\b",
    )
]


class AlertRejected(ValueError):
    pass


@dataclass
class SanitisedAlert:
    alert_id: str
    rule_name: str
    rule_severity: str
    source: str
    timestamp: str
    description: str
    entities: dict[str, list[str]]
    evidence: dict[str, Any]
    injection_flags: list[str] = field(default_factory=list)
    dropped: list[str] = field(default_factory=list)

    def all_entities(self) -> set[str]:
        return {v for values in self.entities.values() for v in values}

    def for_prompt(self) -> dict[str, Any]:
        return {
            "alert_id": self.alert_id,
            "rule_name": self.rule_name,
            "rule_severity": self.rule_severity,
            "source": self.source,
            "timestamp": self.timestamp,
            "description": self.description,
            "entities": self.entities,
            "evidence": self.evidence,
        }


def _clip(value: Any, path: str, flags: list[str], depth: int = 0) -> Any:
    if depth > MAX_DEPTH:
        return "[nested data removed]"
    if isinstance(value, str):
        for pattern in INJECTION_PATTERNS:
            if pattern.search(value):
                flags.append(f"{path}: matches '{pattern.pattern}'")
                break
        return value if len(value) <= MAX_STRING else value[:MAX_STRING] + " [truncated]"
    if isinstance(value, dict):
        return {str(k)[:64]: _clip(v, f"{path}.{k}", flags, depth + 1) for k, v in list(value.items())[:50]}
    if isinstance(value, list):
        return [_clip(v, f"{path}[{i}]", flags, depth + 1) for i, v in enumerate(value[:50])]
    if isinstance(value, (int, float, bool)) or value is None:
        return value
    return str(value)[:MAX_STRING]


def _valid_entity(kind: str, value: Any) -> bool:
    if not isinstance(value, str):
        return False
    if kind == "ips":
        try:
            ipaddress.ip_address(value)
            return True
        except ValueError:
            return False
    return bool(_ENTITY_PATTERNS[kind].match(value))


def sanitise(raw: dict[str, Any]) -> SanitisedAlert:
    if not isinstance(raw, dict):
        raise AlertRejected("alert must be a JSON object")
    alert_id = raw.get("alert_id")
    if not isinstance(alert_id, str) or not re.fullmatch(r"[A-Z]{2,10}-\d{1,10}", alert_id):
        raise AlertRejected(f"invalid alert_id: {alert_id!r}")
    severity = raw.get("rule_severity")
    if severity not in SEVERITIES:
        raise AlertRejected(f"{alert_id}: invalid rule_severity {severity!r}")

    flags: list[str] = []
    dropped = [k for k in raw if k not in {"alert_id", "rule_name", "rule_severity", "source", "timestamp",
                                           "description", "entities", "evidence"}]
    entities: dict[str, list[str]] = {}
    raw_entities = raw.get("entities") or {}
    for kind in ENTITY_KINDS:
        values = raw_entities.get(kind) or []
        good = [v for v in values if _valid_entity(kind, v)]
        dropped += [f"entities.{kind}: {str(v)[:40]!r}" for v in values if not _valid_entity(kind, v)]
        entities[kind] = good[:25]

    def text(key: str) -> str:
        return _clip(str(raw.get(key, "")), key, flags)

    evidence = _clip(raw.get("evidence") or {}, "evidence", flags)
    return SanitisedAlert(
        alert_id=alert_id,
        rule_name=text("rule_name"),
        rule_severity=severity,
        source=text("source"),
        timestamp=text("timestamp"),
        description=text("description"),
        entities=entities,
        evidence=evidence if isinstance(evidence, dict) else {"value": evidence},
        injection_flags=flags,
        dropped=dropped,
    )


def load_alerts(directory: Path) -> list[SanitisedAlert]:
    alerts = []
    for path in sorted(directory.glob("*.json")):
        if path.stat().st_size > 256_000:
            raise AlertRejected(f"{path.name}: alert file larger than 256 KB")
        alerts.append(sanitise(json.loads(path.read_text(encoding="utf-8"))))
    return alerts
