"""Lab 15: Sensitive data protection for Claude API calls.

Detects synthetic personally identifiable information (PII) in support tickets, replaces it
with reversible tokens from a keyed vault *before* anything is sent to Claude, checks the
model's output for leaks, and only rehydrates tokens for roles that are allowed to see them.

Usage (from the repository root):

    CLAUDE_LAB_MODE=mock python 19-hands-on-labs/lab-15-sensitive-data-protection/lab.py
    CLAUDE_LAB_MODE=live python 19-hands-on-labs/lab-15-sensitive-data-protection/lab.py

Optional environment variables:

    LAB15_VAULT_KEY   secret used to key the token vault (any string). If unset, a random
                      per-run key is generated, so token suffixes change between runs.
    LAB_OUTPUT_DIR    where the audit file is written (default: the system temp directory).

All data in ./data is synthetic: example.com / .invalid e-mail domains, 555-01xx phone
numbers, published payment-card test numbers and SSN-like values in ranges that are never
issued as Social Security numbers.
"""
from __future__ import annotations

import hashlib
import hmac
import json
import os
import re
import secrets
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "common"))
from claude_lab import MODEL, banner, get_client, register_mock, text_of  # noqa: E402

OUT_DIR = Path(os.environ.get("LAB_OUTPUT_DIR") or tempfile.gettempdir()) / "claude-labs" / "lab-15"

# --------------------------------------------------------------------------- self-check helper
_results: list[tuple[str, bool]] = []


def check(label: str, condition: bool) -> None:
    _results.append((label, bool(condition)))
    print(f"  [{'PASS' if condition else 'FAIL'}] {label}")


# --------------------------------------------------------------------------- detection
@dataclass(frozen=True)
class Finding:
    type: str
    start: int
    end: int
    raw: str
    normalised: str


EMAIL_RE = re.compile(r"(?<![\w.+-])[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)*\.[A-Za-z]{2,}\b")
# North American style numbers: optional +1, area code with or without brackets, 3-3-4 digits.
PHONE_RE = re.compile(r"(?<![\d+])(?:\+?1[\s.-]?)?(?:\(\d{3}\)|\d{3})[\s.-]?\d{3}[\s.-]\d{4}(?!\d)")
# 13-19 digits: an unbroken run, 4-4-4-x groups, or the 4-6-5 layout used by some cards.
CARD_RE = re.compile(
    r"(?<![\d-])(?:\d{13,19}|\d{4}[ -]\d{4}[ -]\d{4}[ -]\d{1,7}|\d{4}[ -]\d{6}[ -]\d{5})(?![\d-])"
)
SSN_RE = re.compile(r"(?<![\d-])(\d{3})-(\d{2})-(\d{4})(?![\d-])")


def luhn_ok(digits: str) -> bool:
    """Luhn (mod 10) checksum used by payment cards. Filters out order numbers and IDs."""
    total = 0
    for i, ch in enumerate(reversed(digits)):
        d = int(ch)
        if i % 2 == 1:
            d *= 2
            if d > 9:
                d -= 9
        total += d
    return total % 10 == 0


def ssn_like_ok(area: str, group: str, serial: str) -> bool:
    """Reject shapes that can never be a taxpayer identifier.

    Area 000 and 666, group 00 and serial 0000 are never issued. Area 900-999 is not used for
    SSNs but is used for Individual Taxpayer Identification Numbers (ITINs), which are just as
    sensitive, so this lab keeps flagging it. That is also why the synthetic data can use the
    900 range safely: those values are not anyone's SSN.
    """
    return area not in {"000", "666"} and group != "00" and serial != "0000"


def detect(text: str) -> list[Finding]:
    """Return non-overlapping findings. Higher-confidence detectors claim spans first."""
    findings: list[Finding] = []
    claimed: list[tuple[int, int]] = []

    def free(s: int, e: int) -> bool:
        return all(e <= cs or s >= ce for cs, ce in claimed)

    def add(kind: str, m: re.Match, norm: str) -> None:
        if free(m.start(), m.end()):
            findings.append(Finding(kind, m.start(), m.end(), m.group(0), norm))
            claimed.append((m.start(), m.end()))

    for m in EMAIL_RE.finditer(text):
        add("EMAIL", m, m.group(0).lower())
    for m in CARD_RE.finditer(text):
        digits = re.sub(r"\D", "", m.group(0))
        if 13 <= len(digits) <= 19 and luhn_ok(digits):
            add("CARD", m, digits)
    for m in SSN_RE.finditer(text):
        if ssn_like_ok(*m.groups()):
            add("SSN", m, "".join(m.groups()))
    for m in PHONE_RE.finditer(text):
        digits = re.sub(r"\D", "", m.group(0))
        if len(digits) == 11 and digits.startswith("1"):
            digits = digits[1:]
        add("PHONE", m, digits)
    return sorted(findings, key=lambda f: f.start)


# --------------------------------------------------------------------------- tokenisation vault
TOKEN_RE = re.compile(r"\[(EMAIL|PHONE|CARD|SSN)_([0-9A-F]{8})\]")


def mask(kind: str, value: str) -> str:
    """Partial display for roles that may know a value exists but not see it."""
    if kind == "CARD":
        return f"**** **** **** {value[-4:]}"
    if kind == "SSN":
        return f"***-**-{value[-4:]}"
    if kind == "PHONE":
        return f"***-***-{value[-4:]}"
    if kind == "EMAIL":
        local, _, domain = value.partition("@")
        return f"{local[:1]}***@{domain}"
    return "[REDACTED]"


# Which entity types each role may see in clear text after rehydration.
ROLE_POLICY: dict[str, set[str]] = {
    "case_handler": {"EMAIL", "PHONE", "CARD", "SSN"},
    "support_agent": {"EMAIL", "PHONE"},
    "analytics": set(),
}


class TokenVault:
    """Deterministic, keyed, reversible tokenisation.

    The token is an HMAC of (type, normalised value), so the same value always maps to the same
    token within one key, which keeps references consistent across tickets without revealing
    the value. The mapping back to the raw value lives only in this process (in production:
    an encrypted store with its own access controls and retention).
    """

    def __init__(self, key: bytes) -> None:
        self._key = key
        self._forward: dict[tuple[str, str], str] = {}
        self._reverse: dict[str, tuple[str, str, str]] = {}  # token -> (type, normalised, raw)
        self.audit: list[dict] = []

    def token_for(self, f: Finding) -> str:
        k = (f.type, f.normalised)
        if k not in self._forward:
            digest = hmac.new(self._key, f"{f.type}:{f.normalised}".encode(), hashlib.sha256).hexdigest()
            token = f"[{f.type}_{digest[:8].upper()}]"
            self._forward[k] = token
            self._reverse[token] = (f.type, f.normalised, f.raw)
        return self._forward[k]

    def redact(self, text: str) -> tuple[str, list[Finding]]:
        findings = detect(text)
        out, cursor = [], 0
        for f in findings:
            out.append(text[cursor:f.start])
            out.append(self.token_for(f))
            cursor = f.end
        out.append(text[cursor:])
        return "".join(out), findings

    def known(self, token: str) -> bool:
        return token in self._reverse

    def raw_values(self) -> list[str]:
        return [raw for _, _, raw in self._reverse.values()] + [n for _, n, _ in self._reverse.values()]

    def rehydrate(self, text: str, role: str, purpose: str) -> str:
        allowed = ROLE_POLICY.get(role, set())

        def repl(m: re.Match) -> str:
            token = m.group(0)
            if token not in self._reverse:
                return "[UNKNOWN_TOKEN]"
            kind, norm, raw = self._reverse[token]
            clear = kind in allowed
            self.audit.append({"role": role, "purpose": purpose, "token": token, "type": kind, "revealed": clear})
            return raw if clear else mask(kind, norm)

        return TOKEN_RE.sub(repl, text)


def vault_key() -> tuple[bytes, str]:
    env = os.environ.get("LAB15_VAULT_KEY")
    if env:
        return env.encode(), "LAB15_VAULT_KEY"
    return secrets.token_bytes(32), "random per-run key"


# --------------------------------------------------------------------------- leak checks
def leak_check(output: str, vault: TokenVault) -> list[str]:
    """Return a list of problems with model output. Empty means the output is safe to store."""
    problems = []
    for f in detect(output):
        problems.append(f"raw {f.type} pattern in output")
    lowered = output.lower()
    compact = re.sub(r"[\s().-]", "", output)
    for value in set(vault.raw_values()):
        if value.lower() in lowered or (value.isdigit() and value in compact):
            problems.append("exact vault value echoed in output")
            break
    for m in TOKEN_RE.finditer(output):
        if not vault.known(m.group(0)):
            problems.append(f"unknown token {m.group(0)} (invented or tampered)")
    return problems


# --------------------------------------------------------------------------- Claude call
SYSTEM = (
    "You are the Northwind Lending support summariser. Tickets have had personal data replaced "
    "with tokens such as [EMAIL_1A2B3C4D]. Copy any token you need exactly as written. Never "
    "guess, reconstruct or invent personal data or tokens. Reply with three short lines: "
    "'Issue:', 'Contact:', 'Next step:'."
)

SENT_PAYLOADS: list[str] = []  # what left the process in mock mode (an egress log)

CANNED_ISSUES = {
    "NWL-4471": ("Duplicate charge on the March loan payment.", "Refund the duplicate payment after billing confirms it."),
    "NWL-4472": ("Hardship application needs updated tax and contact details.", "Route to the hardship team to update the file."),
    "NWL-4473": ("Autopay failed and a partner-store order was declined.", "Check the autopay mandate and the card status."),
    "NWL-4474": ("Customer asks to close the line of credit.", "Send the account closure confirmation form."),
}


@register_mock
def fake_summariser(**request):
    if "Northwind Lending support summariser" not in str(request.get("system", "")):
        return None
    SENT_PAYLOADS.append(json.dumps(request, default=str))
    user = request["messages"][-1]["content"]
    ticket_id = re.search(r"NWL-\d{4}", user).group(0)
    issue, step = CANNED_ISSUES.get(ticket_id, ("General enquiry.", "Reply to the customer."))
    tokens = [m.group(0) for m in TOKEN_RE.finditer(user) if m.group(1) in {"EMAIL", "PHONE"}]
    contact = ", ".join(dict.fromkeys(tokens)) or "no contact details given"
    return f"Issue: {issue}\nContact: {contact}\nNext step: {step}"


def summarise(client, ticket_id: str, redacted_text: str) -> str:
    response = client.messages.create(
        model=MODEL,
        max_tokens=1024,
        system=SYSTEM,
        messages=[{"role": "user", "content": f"Ticket {ticket_id}:\n<ticket>\n{redacted_text}\n</ticket>"}],
        output_config={"effort": "low"},
    )
    if response.stop_reason != "end_turn":
        raise RuntimeError(f"unexpected stop_reason {response.stop_reason!r} for {ticket_id}")
    return text_of(response)


# --------------------------------------------------------------------------- evaluation
def evaluate_detector(path: Path) -> dict:
    stats: dict[str, dict[str, int]] = {}
    misses = []
    for line in path.read_text(encoding="utf-8").splitlines():
        row = json.loads(line)
        expected = {(e["type"], e["value"].lower()) for e in row["entities"]}
        got = {(f.type, f.normalised) for f in detect(row["text"])}
        for kind in {"EMAIL", "PHONE", "CARD", "SSN"}:
            s = stats.setdefault(kind, {"tp": 0, "fp": 0, "fn": 0})
            exp_k = {e for e in expected if e[0] == kind}
            got_k = {g for g in got if g[0] == kind}
            s["tp"] += len(exp_k & got_k)
            s["fp"] += len(got_k - exp_k)
            s["fn"] += len(exp_k - got_k)
        for e in expected - got:
            misses.append((row["id"], e[0]))
        for g in got - expected:
            misses.append((row["id"], f"false positive {g[0]}"))
    return {"per_type": stats, "misses": misses}


def prf(s: dict[str, int]) -> tuple[float, float]:
    p = s["tp"] / (s["tp"] + s["fp"]) if s["tp"] + s["fp"] else 1.0
    r = s["tp"] / (s["tp"] + s["fn"]) if s["tp"] + s["fn"] else 1.0
    return p, r


def main() -> None:
    banner("Lab 15: Sensitive data protection")
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Detector quality on the labelled set -------------------------------------------
    print("Step 1: detector precision and recall on data/labelled_samples.jsonl")
    ev = evaluate_detector(HERE / "data" / "labelled_samples.jsonl")
    total = {"tp": 0, "fp": 0, "fn": 0}
    print(f"  {'type':<6} {'TP':>3} {'FP':>3} {'FN':>3} {'precision':>10} {'recall':>7}")
    for kind in ("EMAIL", "PHONE", "CARD", "SSN"):
        s = ev["per_type"][kind]
        for k in total:
            total[k] += s[k]
        p, r = prf(s)
        print(f"  {kind:<6} {s['tp']:>3} {s['fp']:>3} {s['fn']:>3} {p:>10.2f} {r:>7.2f}")
    p_all, r_all = prf(total)
    print(f"  {'ALL':<6} {total['tp']:>3} {total['fp']:>3} {total['fn']:>3} {p_all:>10.2f} {r_all:>7.2f}")
    print(f"  Misses and false positives: {ev['misses'] or 'none'}")
    check("no false positives on order numbers, IDs and invalid SSN shapes", total["fp"] == 0)
    check("overall precision >= 0.95", p_all >= 0.95)
    check("overall recall >= 0.85 (known gaps: spelled-out e-mail, 7-digit phone)", r_all >= 0.85)
    check("non-Luhn 16-digit runs are not flagged as cards", not detect("Invoice 1234 5678 9012 3456"))
    check("Luhn-valid test card is flagged", [f.type for f in detect("4111 1111 1111 1111")] == ["CARD"])
    check("area 000 / 666 and group 00 are rejected", not detect("000-12-3456 666-12-3456 123-00-4567"))

    # 2. Redact tickets before the API call --------------------------------------------
    key, key_source = vault_key()
    vault = TokenVault(key)
    print(f"\nStep 2: redact tickets before sending (vault key source: {key_source})")
    tickets = [json.loads(l) for l in (HERE / "data" / "support_tickets.jsonl").read_text(encoding="utf-8").splitlines()]
    originals: list[str] = []
    redacted: dict[str, str] = {}
    for t in tickets:
        red, findings = vault.redact(t["text"])
        redacted[t["id"]] = red
        originals.extend(f.raw for f in findings)
        kinds = ", ".join(f.type for f in findings) or "none"
        print(f"  {t['id']}: {len(findings)} finding(s) [{kinds}]")
        print(f"    redacted: {red}")
    check("every ticket after redaction has no detectable PII", all(not detect(r) for r in redacted.values()))
    t1 = vault.redact("dana.okafor@example.com")[0]
    t2 = vault.redact("DANA.OKAFOR@example.com")[0]
    check("tokens are deterministic for the same normalised value", t1 == t2)

    # 3. Call Claude with redacted text only -------------------------------------------
    print("\nStep 3: summarise redacted tickets with Claude")
    client = get_client()
    summaries: dict[str, str] = {}
    for t in tickets:
        summaries[t["id"]] = summarise(client, t["id"], redacted[t["id"]])
        print(f"  {t['id']} ->")
        for line in summaries[t["id"]].splitlines():
            print(f"    {line}")
    if SENT_PAYLOADS:  # only populated in mock mode, where we can inspect the egress log
        egress = "\n".join(SENT_PAYLOADS)
        check("no raw PII value left the process (egress log scan)", not any(v in egress for v in originals))

    # 4. Leak checks on model output ----------------------------------------------------
    print("\nStep 4: leak checks on model output")
    clean = True
    for tid, text in summaries.items():
        problems = leak_check(text, vault)
        clean &= not problems
        print(f"  {tid}: {'clean' if not problems else problems}")
    check("all real summaries pass the leak check", clean)
    bad = summaries["NWL-4471"] + "\nCard used: 4111 1111 1111 1111. See also [CARD_DEADBEEF]."
    bad_problems = leak_check(bad, vault)
    print(f"  simulated bad output -> {bad_problems}")
    check("leak check blocks a raw card number", any("CARD" in p for p in bad_problems))
    check("leak check blocks an invented token", any("unknown token" in p for p in bad_problems))

    # 5. Role-based rehydration ----------------------------------------------------------
    print("\nStep 5: rehydrate the redacted NWL-4471 ticket for different roles")
    views = {}
    for role in ("case_handler", "support_agent", "analytics"):
        views[role] = vault.rehydrate(redacted["NWL-4471"], role=role, purpose="ticket follow-up")
        print(f"  {role}:")
        print(f"    {views[role]}")
    check("case_handler sees the full card number", "4111 1111 1111 1111" in views["case_handler"])
    check("support_agent sees contact details but only a masked card",
          "dana.okafor@example.com" in views["support_agent"] and "**** **** **** 1111" in views["support_agent"])
    check("analytics sees only masked values",
          "dana.okafor@example.com" not in views["analytics"] and "d***@example.com" in views["analytics"])
    rows = len(vault.audit)
    check("every rehydration is audited", rows == 9 and all("revealed" in a for a in vault.audit))

    audit_path = OUT_DIR / "rehydration_audit.jsonl"
    audit_path.write_text("\n".join(json.dumps(a) for a in vault.audit) + "\n", encoding="utf-8")
    print(f"\nAudit log ({rows} rows, tokens only, no raw values) written to {audit_path}")
    check("audit log contains no raw PII", not any(v in audit_path.read_text(encoding="utf-8") for v in originals))

    failed = [label for label, ok in _results if not ok]
    print(f"\nSelf-checks: {len(_results) - len(failed)}/{len(_results)} passed")
    if failed:
        sys.exit(1)


if __name__ == "__main__":
    main()
