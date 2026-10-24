"""SARIF 2.1.0 export so CI systems (for example GitHub code scanning) can show findings inline.

Design choices:
  * ruleId is the CWE, so the same weakness groups together across runs.
  * `security-severity` (a numeric string) lets GitHub rank alerts as critical/high/medium/low.
  * Fix text goes into the message only. The SARIF `fixes` object (machine-applicable
    replacements) is intentionally never emitted: no model-written change is applied
    without a human writing and reviewing the patch.
"""
from __future__ import annotations

import hashlib

from . import __version__
from .models import Finding

SARIF_SCHEMA = "https://json.schemastore.org/sarif-2.1.0.json"
LEVEL = {"critical": "error", "high": "error", "medium": "warning", "low": "note", "info": "note"}
SECURITY_SEVERITY = {"critical": "9.5", "high": "8.0", "medium": "5.5", "low": "3.0", "info": "0.0"}


def _fingerprint(f: Finding) -> str:
    return hashlib.sha256(f"{f.file}|{f.cwe}|{f.line}".encode()).hexdigest()[:32]


def to_sarif(findings: list[Finding]) -> dict:
    rules: dict[str, dict] = {}
    results = []
    for f in findings:
        number = f.cwe.split("-", 1)[1]
        rule = rules.setdefault(f.cwe, {
            "id": f.cwe,
            "name": f.cwe.replace("-", ""),
            "shortDescription": {"text": f.title},
            "helpUri": f"https://cwe.mitre.org/data/definitions/{number}.html",
            "properties": {"tags": ["security", f"external/cwe/cwe-{number}"], "security-severity": "0.0"},
        })
        # A rule's severity is the worst severity seen for it in this run.
        if float(SECURITY_SEVERITY[f.severity]) > float(rule["properties"]["security-severity"]):
            rule["properties"]["security-severity"] = SECURITY_SEVERITY[f.severity]
        results.append({
            "ruleId": f.cwe,
            "level": LEVEL[f.severity],
            "message": {"text": f"{f.title}. {f.description} Suggested fix (not applied): {f.fix}"},
            "locations": [{"physicalLocation": {
                "artifactLocation": {"uri": f.file, "uriBaseId": "%SRCROOT%"},
                "region": {"startLine": f.line},
            }}],
            "partialFingerprints": {"secreviewLocation/v1": _fingerprint(f)},
            "properties": {"severity": f.severity, "confidence": f.confidence, "sources": f.sources},
        })
    return {
        "$schema": SARIF_SCHEMA,
        "version": "2.1.0",
        "runs": [{
            "tool": {"driver": {
                "name": "secreview",
                "version": __version__,
                "rules": list(rules.values()),
            }},
            "results": results,
        }],
    }
