"""Offline stand-in for Claude used in mock mode (CLAUDE_LAB_MODE=mock).

It reads the numbered diff out of the prompt and applies a few keyword rules, so the
pipeline runs end to end with realistic output. It deliberately also returns:
  * a duplicate of a pre-check finding (to exercise de-duplication), and
  * one finding on a line that is not in the diff and one with a malformed CWE
    (to exercise validation, which must reject both).
It ignores the injection comment in the sample diff, as the real model is instructed to.
"""
from __future__ import annotations

import json
import re

from ._lab import claude_lab

LINE = re.compile(r"^L(\d+)\s*\+\| (.*)$")
FILE = re.compile(r'^<file path="([^"]+)">$')

RULES = [
    (re.compile(r"\.execute\(f[\"']"), "CWE-89", "high", "SQL injection via f-string query",
     "User input is interpolated into SQL.", "Use a parameterised query."),
    (re.compile(r"pickle\.loads\(request"), "CWE-502", "critical", "Insecure deserialisation of request body",
     "pickle.loads on attacker-controlled bytes allows remote code execution.", "Accept JSON and validate it."),
    (re.compile(r"shell=True"), "CWE-78", "high", "OS command injection",
     "A request parameter is formatted into a shell command.", "Pass an argument list without shell=True; allow-list the format."),
    (re.compile(r"\[REDACTED-BY-PRECHECK\]"), "CWE-798", "high", "Hardcoded credential",
     "A credential literal was committed (value redacted before review).", "Move it to a secrets manager and rotate it."),
    (re.compile(r"@bp\.route\(\"/admin/"), "CWE-862", "high", "Privileged route without authorisation check",
     "The write-off endpoint changes loan state but has no authentication or role check.",
     "Require an authenticated session and an explicit role check (for example @require_role('collections_admin'))."),
]


@claude_lab.register_mock
def fake_secreview(**request):
    if "You are secreview" not in str(request.get("system", "")):
        return None
    prompt = request["messages"][-1]["content"]
    findings, current = [], None
    for row in prompt.splitlines():
        m = FILE.match(row)
        if m:
            current = m.group(1)
            continue
        m = LINE.match(row)
        if not (m and current):
            continue
        lineno, code = int(m.group(1)), m.group(2)
        for pattern, cwe, sev, title, desc, fix in RULES:
            if pattern.search(code):
                findings.append({"file": current, "line": lineno, "cwe": cwe, "severity": sev, "title": title,
                                 "description": desc, "fix": fix, "confidence": 0.85})
    if findings:  # two deliberately bad items to prove validation works
        first = findings[0]["file"]
        findings.append({"file": first, "line": 9999, "cwe": "CWE-22", "severity": "high", "title": "Path traversal",
                         "description": "Hallucinated location.", "fix": "n/a", "confidence": 0.4})
        findings.append({"file": first, "line": findings[0]["line"], "cwe": "SQLi", "severity": "urgent",
                         "title": "Malformed item", "description": "Bad CWE and severity.", "fix": "n/a",
                         "confidence": 2})
    summary = f"{len(findings)} candidate issue(s) found." if findings else "No security issues in the added lines."
    return json.dumps({"findings": findings, "summary": summary})
