"""Shared helper for the hands-on labs.

Every lab runs in one of two modes, chosen with the CLAUDE_LAB_MODE environment variable:

  mock (default)  Offline and free. A deterministic fake client returns canned responses
                  so the lab's code path runs end to end. Used by CI.
  live            Calls the real Claude API with the official `anthropic` SDK.
                  Needs ANTHROPIC_API_KEY (or an `ant auth login` profile) and uses API credits.

Credentials are never read from files in this repository. Copy `.env.example` to `.env`
(which is git-ignored) or export variables in your shell.

Usage in a lab:

    from claude_lab import get_client, MODEL, register_mock, text_of

    @register_mock
    def fake(**request):
        return "a canned answer for offline mode"

    client = get_client()
    response = client.messages.create(model=MODEL, max_tokens=1024, messages=[...])
    print(text_of(response))
"""
from __future__ import annotations

import json
import os
import uuid
from dataclasses import dataclass, field
from typing import Any, Callable

MODE = os.environ.get("CLAUDE_LAB_MODE", "mock").strip().lower()
# Default to the current Opus model; labs that are cost-sensitive say so and override.
MODEL = os.environ.get("CLAUDE_LAB_MODEL", "claude-opus-5-5")
FAST_MODEL = os.environ.get("CLAUDE_LAB_FAST_MODEL", "claude-haiku-5-5")


# --------------------------------------------------------------------------- mock objects
@dataclass
class TextBlock:
    text: str
    type: str = "text"


@dataclass
class ToolUseBlock:
    name: str
    input: dict
    id: str = field(default_factory=lambda: f"toolu_mock_{uuid.uuid4().hex[:12]}")
    type: str = "tool_use"


@dataclass
class Usage:
    input_tokens: int = 0
    output_tokens: int = 0
    cache_creation_input_tokens: int = 0
    cache_read_input_tokens: int = 0


@dataclass
class Message:
    content: list
    model: str
    stop_reason: str = "end_turn"
    usage: Usage = field(default_factory=Usage)
    id: str = field(default_factory=lambda: f"msg_mock_{uuid.uuid4().hex[:12]}")
    role: str = "assistant"
    type: str = "message"
    stop_details: Any = None


@dataclass
class TokenCount:
    input_tokens: int


Responder = Callable[..., Any]
_responders: list[Responder] = []


def register_mock(fn: Responder) -> Responder:
    """Register a function that fakes Claude in mock mode.

    It receives the same keyword arguments as `messages.create` and may return a str,
    a list of blocks (TextBlock / ToolUseBlock), or a full Message.
    """
    _responders.append(fn)
    return fn


def _estimate_tokens(obj: Any) -> int:
    return max(1, len(json.dumps(obj, default=str)) // 4)


def _to_message(result: Any, request: dict) -> Message:
    if isinstance(result, Message):
        return result
    blocks = [TextBlock(result)] if isinstance(result, str) else list(result)
    stop = "tool_use" if any(getattr(b, "type", "") == "tool_use" for b in blocks) else "end_turn"
    usage = Usage(
        input_tokens=_estimate_tokens({k: request.get(k) for k in ("system", "messages", "tools")}),
        output_tokens=_estimate_tokens([getattr(b, "text", getattr(b, "input", "")) for b in blocks]),
    )
    return Message(content=blocks, model=request.get("model", MODEL), stop_reason=stop, usage=usage)


class _MockMessages:
    def create(self, **request: Any) -> Message:
        _validate_request(request)
        for responder in reversed(_responders):
            result = responder(**request)
            if result is not None:
                return _to_message(result, request)
        last = request["messages"][-1]["content"]
        text = last if isinstance(last, str) else json.dumps(last, default=str)[:200]
        return _to_message(f"[mock response] You asked: {text[:200]}", request)

    def count_tokens(self, **request: Any) -> TokenCount:
        return TokenCount(input_tokens=_estimate_tokens(request))


class _MockBeta:
    def __init__(self, messages: _MockMessages) -> None:
        self.messages = messages


class MockClient:
    """Duck-typed stand-in for `anthropic.Anthropic` covering what the labs use."""

    def __init__(self) -> None:
        self.messages = _MockMessages()
        # Beta parameters (e.g. `betas`, `fallbacks`) are accepted and ignored offline.
        self.beta = _MockBeta(self.messages)

    def with_options(self, **_options: Any) -> "MockClient":
        """Mirror `client.with_options(timeout=..., max_retries=...)`; options are no-ops offline."""
        return self


def _ends_in_server_tool_use(message: dict) -> bool:
    """A trailing assistant turn is allowed when resuming after `pause_turn` (it ends in server-tool use)."""
    content = message.get("content")
    if not isinstance(content, list) or not content:
        return False
    last = content[-1]
    kind = last.get("type") if isinstance(last, dict) else getattr(last, "type", "")
    return kind == "server_tool_use"


def _validate_request(request: dict) -> None:
    """Catch common mistakes offline, mirroring rules of the real API for current models."""
    for key in ("model", "max_tokens", "messages"):
        if key not in request:
            raise ValueError(f"messages.create() missing required argument: {key}")
    msgs = request["messages"]
    if not msgs or msgs[0]["role"] != "user":
        raise ValueError("the first message must have role 'user'")
    if msgs[-1]["role"] == "assistant" and not _ends_in_server_tool_use(msgs[-1]):
        raise ValueError("assistant prefill is not supported on current Claude models")
    for banned in ("temperature", "top_p", "top_k"):
        if banned in request:
            raise ValueError(f"'{banned}' is not supported on current Claude models; tune prompts or effort instead")
    choice = (request.get("tool_choice") or {}).get("type")
    if choice in {"any", "tool"}:
        raise ValueError("forced tool_choice is not supported on current models; use 'auto' with a clear instruction")


# --------------------------------------------------------------------------- public helpers
def get_client():
    """Return a real Anthropic client in live mode, otherwise the offline mock."""
    if MODE == "live":
        try:
            import anthropic
        except ImportError as exc:  # pragma: no cover
            raise SystemExit("Live mode needs the SDK: pip install -r 19-hands-on-labs/requirements.txt") from exc
        return anthropic.Anthropic()  # reads ANTHROPIC_API_KEY or an `ant auth login` profile
    return MockClient()


def text_of(message: Any) -> str:
    """Concatenate the text blocks of a response (ignores thinking and tool blocks)."""
    return "".join(b.text for b in message.content if getattr(b, "type", "") == "text")


def banner(title: str) -> None:
    mode = "LIVE — uses API credits" if MODE == "live" else "MOCK — offline, no credits used"
    print(f"\n=== {title} ===  [{mode}; model={MODEL}]\n")
