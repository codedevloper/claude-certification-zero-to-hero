"""Deterministic pre-checks that run before (and independently of) the model.

Why have them at all when Claude reviews the diff anyway?
  * They are cheap, fast and reproducible, so they make a reliable floor for CI.
  * Secrets are found *before* the diff leaves your network, so they can be redacted
    from the prompt (data minimisation) while still being reported.
  * They give the evaluation harness an independent signal to compare against.

The taint heuristic is deliberately simple: it tracks variables assigned from a
request source within one file's added lines and flags dangerous sinks that use a
source directly or through such a variable. It misses flows across functions and files,
which is exactly where the model review adds value.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

from .diff_parser import FileDiff
from .models import Finding

# --------------------------------------------------------------------------- secrets
SECRET_RULES = [
    ("SR-SEC-001", "AWS access key ID", re.compile(r"\b(?:AKIA|ASIA)[0-9A-Z]{16}\b"), "high"),
    ("SR-SEC-002", "Private key block", re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----"), "critical"),
    ("SR-SEC-003", "GitHub token", re.compile(r"\bgh[pousr]_[A-Za-z0-9]{36,}\b"), "high"),
    ("SR-SEC-004", "Anthropic API key", re.compile(r"sk-ant-(?:api|admin)\d{2}-[A-Za-z0-9_\-]{20,}"), "high"),
    ("SR-SEC-005", "Hardcoded credential assignment",
     re.compile(r"(?i)\b\w*(?:password|passwd|secret|token|api_?key)\w*\s*[:=]\s*['\"]([^'\"\s]{12,})['\"]"), "high"),
]
REDACTION = "[REDACTED-BY-PRECHECK]"

# --------------------------------------------------------------------------- taint
SOURCE = re.compile(
    r"request\.(?:args|form|values|json|get_json|get_data|data|cookies|headers|files)|\binput\(|sys\.argv"
)
ASSIGN = re.compile(r"^\s*([A-Za-z_]\w*)\s*=\s*(.+)$")
SINKS = [
    # (rule id, CWE, title, severity, sink regex, needs string building to be risky)
    ("SR-TNT-089", "CWE-89", "SQL query built from request data", "high",
     re.compile(r"\.(?:execute|executemany|raw)\s*\("), True),
    ("SR-TNT-078", "CWE-78", "OS command built from request data", "high",
     re.compile(r"os\.system\s*\(|os\.popen\s*\(|subprocess\.\w+\(.*shell\s*=\s*True"), False),
    ("SR-TNT-502", "CWE-502", "Untrusted data deserialised", "critical",
     re.compile(r"pickle\.loads?\s*\(|yaml\.load\s*\((?!.*SafeLoader)|marshal\.loads\s*\("), False),
    ("SR-TNT-095", "CWE-95", "Request data passed to eval/exec", "critical",
     re.compile(r"\b(?:eval|exec)\s*\("), False),
]
STRING_BUILDING = re.compile(r"\bf['\"]|['\"]\s*%\s*|['\"]\s*\+|\+\s*['\"]|\.format\(")

# --------------------------------------------------------------------------- injection markers
# Text in the diff that tries to talk to an automated reviewer. Its presence is itself a
# finding (someone is trying to steer the tool) and the model is told to ignore it.
INJECTION = re.compile(
    r"(?i)(ignore (?:all |any )?(?:previous|prior|above) instructions|"
    r"(?:note|message) to (?:the )?(?:ai|llm|automated|claude)\b|"
    r"report no (?:findings|issues|vulnerabilities)|you are now|system prompt)"
)


@dataclass
class PrecheckResult:
    findings: list[Finding]
    redacted_files: list[FileDiff]
    injection_lines: list[tuple[str, int]]


def _secret_findings(fd: FileDiff) -> list[Finding]:
    out = []
    for lineno, text in fd.added.items():
        for rule_id, label, pattern, severity in SECRET_RULES:
            if pattern.search(text):
                out.append(Finding(
                    file=fd.path, line=lineno, cwe="CWE-798", severity=severity,
                    title=f"{label} committed in source",
                    description=f"Line matches the {label.lower()} pattern. Anything committed is visible "
                                "in history to everyone with repository access.",
                    fix="Remove the value, rotate the credential, and load it from a secrets manager or "
                        "environment variable at runtime.",
                    confidence=0.9, sources=[f"precheck:{rule_id}"],
                ))
                break  # one secret finding per line is enough
    return out


def _taint_findings(fd: FileDiff) -> list[Finding]:
    tainted: set[str] = set()
    out = []
    for lineno, text in sorted(fd.added.items()):
        code = text.split("#", 1)[0]
        m = ASSIGN.match(code)
        if m and (SOURCE.search(m.group(2)) or any(re.search(rf"\b{v}\b", m.group(2)) for v in tainted)):
            tainted.add(m.group(1))
        for rule_id, cwe, title, severity, sink, needs_building in SINKS:
            if not sink.search(code):
                continue
            uses_source = bool(SOURCE.search(code)) or any(re.search(rf"\b{v}\b", code) for v in tainted)
            if not uses_source:
                continue
            if needs_building and not STRING_BUILDING.search(code):
                continue  # parameterised query: tainted value passed separately is fine
            out.append(Finding(
                file=fd.path, line=lineno, cwe=cwe, severity=severity, title=title,
                description="Request-controlled data reaches a dangerous sink in the same function "
                            "(intra-file taint heuristic).",
                fix={
                    "CWE-89": "Use a parameterised query: execute('... WHERE borrower = ?', (borrower,)).",
                    "CWE-78": "Avoid shell=True; pass an argument list and validate the value against an allow-list.",
                    "CWE-502": "Never unpickle untrusted input; accept JSON and validate it against a schema.",
                    "CWE-95": "Remove eval/exec; parse the input with a strict parser instead.",
                }[cwe],
                confidence=0.8, sources=[f"precheck:{rule_id}"],
            ))
    return out


def _redact(fd: FileDiff) -> FileDiff:
    lines = []
    for lineno, text, added in fd.lines:
        for _rule, _label, pattern, _sev in SECRET_RULES:
            # Keep the variable name (useful context for the reviewer), drop only the value.
            text = pattern.sub(lambda m: m.group(0).replace(m.group(1), REDACTION) if m.groups() else REDACTION, text)
        lines.append((lineno, text, added))
    return FileDiff(path=fd.path, lines=lines)


def run_prechecks(files: list[FileDiff]) -> PrecheckResult:
    findings: list[Finding] = []
    injection_lines: list[tuple[str, int]] = []
    for fd in files:
        findings += _secret_findings(fd)
        findings += _taint_findings(fd)
        for lineno, text in fd.added.items():
            if INJECTION.search(text):
                injection_lines.append((fd.path, lineno))
                findings.append(Finding(
                    file=fd.path, line=lineno, cwe="CWE-1427", severity="medium",
                    title="Text addressed to an automated reviewer",
                    description="An added line contains instructions aimed at an AI reviewer. The assistant "
                                "treats it as data and ignored it; a human should ask why it is there.",
                    fix="Remove the comment. Security approvals belong in the review system, not in code.",
                    confidence=0.7, sources=["precheck:SR-PI-001"],
                ))
    return PrecheckResult(findings=findings, redacted_files=[_redact(f) for f in files],
                          injection_lines=injection_lines)
