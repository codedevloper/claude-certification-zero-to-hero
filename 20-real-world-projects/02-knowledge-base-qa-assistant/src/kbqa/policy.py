"""Input and output checks around the model call.

Input: questions are length-limited and stripped of control characters.
Output: the answer is untrusted. It is blocked if it links to domains outside the allowlist or
asks the user to hand over credentials, which are the two things a poisoned knowledge-base page
most often tries to make an assistant say.
"""
from __future__ import annotations

import re

MAX_QUESTION_CHARS = 500
ALLOWED_DOMAINS = frozenset({"acme.example", "intranet.acme.example"})

_CONTROL = re.compile(r"[\x00-\x08\x0b-\x1f\x7f]")
_EMAIL = re.compile(r"[\w.+-]+@([\w-]+(?:\.[\w-]+)+)")
_URL = re.compile(r"https?://([^/\s:]+)", re.I)
# Bare or protocol-relative links: "evil.example/reset", "//evil.example/x", "www.evil.example".
_BARE_PATH = re.compile(r"(?:(?<=[\s(<\"'])|^)(?://)?((?:[a-z0-9-]+\.)+[a-z]{2,24})/", re.I)
_CREDENTIAL_REQUEST = re.compile(
    r"\b(send|email|share|provide|give|tell)\b[^.]{0,60}\b(password|passcode|mfa code|one-time code|credentials?)\b",
    re.I,
)
_NEGATION = re.compile(r"\b(never|not|don't|do not|must not)\b[^.]{0,20}$", re.I)


class QuestionRejected(ValueError):
    pass


def clean_question(question: str) -> str:
    question = _CONTROL.sub(" ", question or "").strip()
    if not question:
        raise QuestionRejected("question is empty")
    if len(question) > MAX_QUESTION_CHARS:
        raise QuestionRejected(f"question is longer than {MAX_QUESTION_CHARS} characters")
    return question


def output_violations(answer: str) -> list[str]:
    problems = []
    for domain in set(_EMAIL.findall(answer) + _URL.findall(answer) + _BARE_PATH.findall(answer)):
        if domain.lower() not in ALLOWED_DOMAINS:
            problems.append(f"mentions external domain '{domain}'")
    for match in _CREDENTIAL_REQUEST.finditer(answer):
        # "Never share your password" is advice, not a request; look just before the verb.
        if not _NEGATION.search(answer[max(0, match.start() - 25): match.start()]):
            problems.append("asks the user to share credentials")
            break
    return problems
