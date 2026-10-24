#!/usr/bin/env python3
"""Lightweight local secret scan (CI additionally runs gitleaks).

Flags strings that look like real credentials. Obvious placeholders such as
`sk-ant-...`, `your-api-key` or `<YOUR_KEY>` are allowed.
"""
from __future__ import annotations

import re
import sys

from common import ROOT, Report, iter_text_files

PATTERNS = {
    "Anthropic API key": re.compile(r"sk-ant-(?:api|admin)\d{2}-[A-Za-z0-9_\-]{20,}"),
    "AWS access key": re.compile(r"\b(?:AKIA|ASIA)[0-9A-Z]{16}\b"),
    "GitHub token": re.compile(r"\bgh[pousr]_[A-Za-z0-9]{36,}\b"),
    "Slack token": re.compile(r"\bxox[abprs]-[A-Za-z0-9-]{10,}\b"),
    "Private key block": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----"),
    "Google API key": re.compile(r"\bAIza[0-9A-Za-z_\-]{35}\b"),
    "Generic assigned secret": re.compile(
        r"(?i)\b(?:api[_-]?key|secret|password|token)\b\s*[:=]\s*['\"](?![<{$])[A-Za-z0-9/+_\-]{24,}['\"]"
    ),
}
ALLOW = re.compile(r"(?i)example|placeholder|your[-_]|dummy|fake|redacted|xxxx|synthetic|not-a-real|test-only")


def scan() -> Report:
    report = Report("secret scan")
    for path in iter_text_files():
        if path.name == "scan_secrets.py":
            continue
        rel = path.relative_to(ROOT)
        for lineno, line in enumerate(path.read_text(encoding="utf-8", errors="ignore").splitlines(), 1):
            for label, pat in PATTERNS.items():
                for m in pat.finditer(line):
                    # Judge the matched value itself: a real key must not slip through just because
                    # the same line also contains a word like "example".
                    if not ALLOW.search(m.group(0)):
                        report.error(f"{rel}:{lineno}: possible {label}")
                        break
        if path.name == ".env":
            report.error(f"{rel}: real .env file must not be committed (use .env.example)")
    return report


if __name__ == "__main__":
    r = scan()
    r.print()
    sys.exit(0 if r.ok else 1)
