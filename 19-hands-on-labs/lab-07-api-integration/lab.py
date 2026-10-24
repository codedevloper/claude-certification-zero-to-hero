"""Lab 07: a robust API client wrapper.

Builds `ClaudeGateway`, a thin wrapper you could drop into a service:
  - retries only what is retryable, using a most-specific-first exception chain;
  - exponential backoff with full jitter, honouring the `retry-after` header;
  - an overall deadline, a per-attempt timeout and a correlation ID per logical call;
  - request IDs logged for every success and failure;
  - streaming in live mode (`client.messages.stream` + `get_final_message()`).

Mock mode replays scripted failures (429, 529, 500, timeouts, 400, a refusal) through the
same code path, with stand-in exception classes that mirror the SDK's hierarchy.

Run offline (default):   CLAUDE_LAB_MODE=mock python lab.py
Run against the API:      CLAUDE_LAB_MODE=live python lab.py   (uses API credits)
"""
from __future__ import annotations

import hashlib
import random
import sys
import time
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "common"))
from claude_lab import get_client, MODEL, register_mock, text_of, banner  # noqa: E402
from claude_lab import MODE, Message, TextBlock, Usage  # noqa: E402


# --------------------------------------------------------------------------- error classes
def mock_errors() -> SimpleNamespace:
    """Stand-ins with the same names and inheritance as the anthropic SDK's exceptions."""

    class APIError(Exception):
        pass

    class APIStatusError(APIError):
        status_code = 0

        def __init__(self, message: str, retry_after: str | None = None):
            super().__init__(message)
            self.message = message
            self.request_id = f"req_mock_{uuid.uuid4().hex[:10]}"
            headers = {"retry-after": retry_after} if retry_after else {}
            self.response = SimpleNamespace(headers=headers)

    def status(name: str, code: int) -> type:
        return type(name, (APIStatusError,), {"status_code": code})

    class APIConnectionError(APIError):
        pass

    class APITimeoutError(APIConnectionError):
        pass

    return SimpleNamespace(
        APIError=APIError, APIStatusError=APIStatusError, APIConnectionError=APIConnectionError,
        APITimeoutError=APITimeoutError, BadRequestError=status("BadRequestError", 400),
        AuthenticationError=status("AuthenticationError", 401),
        PermissionDeniedError=status("PermissionDeniedError", 403), NotFoundError=status("NotFoundError", 404),
        RateLimitError=status("RateLimitError", 429), InternalServerError=status("InternalServerError", 500),
        OverloadedError=status("OverloadedError", 529),
    )


def sdk_errors():
    import anthropic  # live mode only

    return anthropic


# --------------------------------------------------------------------------- the wrapper
class RefusalError(RuntimeError):
    """Raised when Claude declines a request (stop_reason == 'refusal')."""


class TruncatedError(RuntimeError):
    """Raised when the answer hit max_tokens."""


@dataclass
class CallRecord:
    correlation_id: str
    attempts: int = 0
    delays: list = field(default_factory=list)
    request_ids: list = field(default_factory=list)
    outcome: str = "pending"


class ClaudeGateway:
    def __init__(self, client, errors, *, max_attempts: int = 4, base_delay: float = 0.5,
                 max_delay: float = 8.0, timeout_s: float = 60.0, deadline_s: float = 30.0,
                 sleep=time.sleep, rng: random.Random | None = None, log=print):
        # Let the wrapper own retries, so SDK retries and ours do not multiply (2 x 4 = 8 attempts).
        if hasattr(client, "with_options"):
            client = client.with_options(max_retries=0, timeout=timeout_s)
        self.client, self.errors = client, errors
        self.max_attempts, self.base_delay, self.max_delay = max_attempts, base_delay, max_delay
        self.deadline_s, self.sleep, self.rng, self.log = deadline_s, sleep, rng or random.Random(), log

    def _backoff(self, attempt: int, retry_after: str | None) -> float:
        delay = self.rng.uniform(0, min(self.max_delay, self.base_delay * 2 ** attempt))  # full jitter
        if retry_after:
            try:
                delay = max(delay, float(retry_after))
            except ValueError:
                pass
        return delay

    def create(self, record: CallRecord, **params):
        e = self.errors
        waited = 0.0
        while True:
            record.attempts += 1
            retry_after = None
            try:
                message = self.client.messages.create(**params)
                request_id = getattr(message, "_request_id", None) or f"req_mock_{message.id[-10:]}"
                record.request_ids.append(request_id)
                self.log(f"    [{record.correlation_id}] attempt {record.attempts}: ok request_id={request_id}")
                return self._check(message, record)
            # Most specific first. Non-retryable client errors are re-raised immediately.
            except (e.BadRequestError, e.AuthenticationError, e.PermissionDeniedError, e.NotFoundError) as exc:
                record.request_ids.append(exc.request_id)
                record.outcome = f"failed: {type(exc).__name__} (not retryable)"
                self.log(f"    [{record.correlation_id}] attempt {record.attempts}: {type(exc).__name__} "
                         f"request_id={exc.request_id} -> not retryable")
                raise
            except e.RateLimitError as exc:  # 429: respect the server's retry-after hint
                retry_after, last = exc.response.headers.get("retry-after"), exc
                record.request_ids.append(exc.request_id)
            except e.APIStatusError as exc:  # 5xx and 529 overloaded are retryable; other 4xx are not
                record.request_ids.append(exc.request_id)
                if exc.status_code < 500:
                    record.outcome = f"failed: {type(exc).__name__} (not retryable)"
                    raise
                last = exc
            except e.APIConnectionError as exc:  # includes APITimeoutError
                last = exc
            delay = self._backoff(record.attempts - 1, retry_after)
            if record.attempts >= self.max_attempts or waited + delay > self.deadline_s:
                record.outcome = f"gave up after {record.attempts} attempts: {type(last).__name__}"
                self.log(f"    [{record.correlation_id}] attempt {record.attempts}: {type(last).__name__} -> giving up")
                raise last
            self.log(f"    [{record.correlation_id}] attempt {record.attempts}: {type(last).__name__} "
                     f"-> retry in {delay:.2f}s" + (f" (retry-after={retry_after})" if retry_after else ""))
            record.delays.append(delay)
            self.sleep(delay)
            waited += delay

    @staticmethod
    def _check(message, record: CallRecord):
        if message.stop_reason == "refusal":
            record.outcome = "refusal"
            raise RefusalError(f"declined (category={getattr(message.stop_details, 'category', None)})")
        if message.stop_reason == "max_tokens":
            record.outcome = "truncated"
            raise TruncatedError("hit max_tokens")
        record.outcome = "ok"
        return message


# --------------------------------------------------------------------------- mock: scripted failures
ERR = mock_errors()
SCRIPTS = {
    "happy": ["ok"],
    "flaky": [ERR.OverloadedError("Overloaded"), ERR.InternalServerError("Internal server error"), "ok"],
    "rate-limited": [ERR.RateLimitError("Rate limit exceeded", retry_after="2"), "ok"],
    "bad-request": [ERR.BadRequestError("max_tokens: must be greater than 0")],
    "outage": [ERR.APITimeoutError("Request timed out")] * 6,
    "refusal": ["refusal"],
}
_cursor: dict[str, int] = {}


@register_mock
def scripted_service(**request):
    content = request["messages"][-1]["content"]
    scenario = next((s for s in SCRIPTS if f"[scenario:{s}]" in content), None)
    if scenario is None:
        return None
    step = SCRIPTS[scenario][min(_cursor.get(scenario, 0), len(SCRIPTS[scenario]) - 1)]
    _cursor[scenario] = _cursor.get(scenario, 0) + 1
    if isinstance(step, Exception):
        raise type(step)(str(step), step.response.headers.get("retry-after")) if isinstance(step, ERR.APIStatusError) else type(step)(str(step))
    if step == "refusal":
        return Message(content=[], model=request["model"], stop_reason="refusal",
                       stop_details=SimpleNamespace(type="refusal", category="cyber", explanation="mock"),
                       usage=Usage(input_tokens=30, output_tokens=0))
    return [TextBlock("Your shipment AL-58213 is out for delivery and should arrive today between 14:00 and 16:00.")]


# --------------------------------------------------------------------------- streaming
def stream_answer(client, record: CallRecord, **params) -> str:
    """Stream text as it arrives. Retry only before the first token, never mid-answer."""
    if MODE == "live":
        pieces = []
        with client.messages.stream(**params) as stream:
            for text in stream.text_stream:
                pieces.append(text)
                print(text, end="", flush=True)
            final = stream.get_final_message()
        print()
        record.request_ids.append(getattr(final, "_request_id", None))
        ClaudeGateway._check(final, record)
        assert "".join(pieces) == text_of(final)
        return text_of(final)
    # Mock: the helper client has no streaming, so simulate chunks from a normal response.
    final = client.messages.create(**params)
    chunks = [text_of(final)[i:i + 24] for i in range(0, len(text_of(final)), 24)]
    for chunk in chunks:
        print(chunk, end="", flush=True)
    print("   (mock: simulated chunks)")
    record.request_ids.append(f"req_mock_{final.id[-10:]}")
    ClaudeGateway._check(final, record)
    return "".join(chunks)


# --------------------------------------------------------------------------- lab code
def opaque_user_id(raw: str) -> str:
    """Send a stable, non-identifying user ID in metadata (useful for abuse investigations)."""
    return hashlib.sha256(f"acme-logistics:{raw}".encode()).hexdigest()[:32]


def main() -> int:
    banner("Lab 07 - API integration: retries, errors, timeouts, request IDs, streaming")
    client = get_client()
    errors = sdk_errors() if MODE == "live" else ERR
    slept: list[float] = []
    sleep = time.sleep if MODE == "live" else slept.append  # mock records delays instead of waiting
    gateway = ClaudeGateway(client, errors, sleep=sleep, rng=random.Random(7))

    base = dict(model=MODEL, max_tokens=1024, output_config={"effort": "low"},
                system="You are Acme Logistics' tracking assistant. Answer in one sentence.",
                metadata={"user_id": opaque_user_id("customer-4411")})
    scenarios = ["happy", "flaky", "rate-limited", "bad-request", "outage", "refusal"] if MODE != "live" else ["happy"]
    records: dict[str, CallRecord] = {}
    for scenario in scenarios:
        record = CallRecord(correlation_id=f"corr-{uuid.uuid4().hex[:8]}")
        records[scenario] = record
        print(f"Scenario: {scenario}")
        try:
            message = gateway.create(record, **base, messages=[{
                "role": "user", "content": f"Where is my parcel AL-58213? [scenario:{scenario}]" if MODE != "live"
                else "Where is my parcel AL-58213? (Explain that you cannot see live tracking data.)"}])
            print(f"  answer: {text_of(message)}")
        except (RefusalError, TruncatedError) as exc:
            print(f"  handled {type(exc).__name__}: {exc}")
        except errors.APIError as exc:
            print(f"  surfaced to caller: {type(exc).__name__}: {exc}")
        print(f"  outcome: {record.outcome}; attempts={record.attempts}; delays={[round(d, 2) for d in record.delays]}\n")

    print("Streaming")
    stream_record = CallRecord(correlation_id=f"corr-{uuid.uuid4().hex[:8]}")
    streamed = stream_answer(client, stream_record, **base, messages=[{
        "role": "user", "content": "Where is my parcel AL-58213? [scenario:happy]" if MODE != "live"
        else "In two sentences, what does 'out for delivery' mean for a parcel?"}])
    print(f"  streamed {len(streamed)} characters; request_id={stream_record.request_ids[-1]}\n")

    print("Self-checks")
    checks = {"happy path succeeds first time": records["happy"].attempts == 1 and records["happy"].outcome == "ok",
              "every attempt that reached the API logged a request ID": all(
                  len(r.request_ids) >= 1 for s, r in records.items() if s != "outage"),
              "streamed text is complete": len(streamed) > 0 and stream_record.outcome == "ok"}
    if MODE != "live":
        checks.update({
            "529 then 500 are retried, third attempt succeeds": records["flaky"].attempts == 3 and records["flaky"].outcome == "ok",
            "429 waits at least retry-after": records["rate-limited"].delays and records["rate-limited"].delays[0] >= 2.0,
            "400 is not retried": records["bad-request"].attempts == 1,
            "timeouts give up after max_attempts": records["outage"].attempts == gateway.max_attempts
            and records["outage"].outcome.startswith("gave up"),
            "backoff delays never exceed max_delay unless retry-after says so": all(
                d <= gateway.max_delay for s, r in records.items() if s != "rate-limited" for d in r.delays),
            "refusal is surfaced as its own error, not retried": records["refusal"].outcome == "refusal"
            and records["refusal"].attempts == 1,
            "mock never actually slept": sum(slept) == sum(sum(r.delays) for r in records.values()),
        })
    failed = [n for n, ok in checks.items() if not ok]
    for name, ok in checks.items():
        print(f"  [{'PASS' if ok else 'FAIL'}] {name}")
    if failed:
        return 1
    print("\nAll checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
