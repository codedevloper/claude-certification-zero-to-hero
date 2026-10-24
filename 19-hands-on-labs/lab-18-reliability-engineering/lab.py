"""Lab 18: Reliability engineering.

Wrap Claude calls in retries with exponential backoff and full jitter, per-call timeouts and an
overall deadline, a circuit breaker, stop_reason handling (max_tokens, refusal, pause_turn) and
idempotent side effects. A fault injector replays the failures in data/fault_plan.json so every
path runs on demand.

Usage (from the repository root):

    CLAUDE_LAB_MODE=mock python 19-hands-on-labs/lab-18-reliability-engineering/lab.py   # offline, free
    CLAUDE_LAB_MODE=live python 19-hands-on-labs/lab-18-reliability-engineering/lab.py   # real API, uses credits

Mock mode runs on a simulated clock, so backoff waits cost no real time. Live mode uses the real
clock and the real API; injected faults are still simulated locally before a request is sent.
"""
from __future__ import annotations

import hashlib
import json
import os
import random
import re
import sys
import tempfile
import time
from pathlib import Path
from types import SimpleNamespace

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "common"))

from claude_lab import MODE, MODEL, Message, TextBlock, banner, get_client, register_mock, text_of  # noqa: E402

DATA = HERE / "data"
OUT_DIR = Path(os.environ.get("LAB_OUTPUT_DIR") or tempfile.gettempdir()) / "claude-labs" / "lab-18"
FALLBACK_MODEL = os.environ.get("CLAUDE_LAB18_FALLBACK_MODEL", "claude-sonnet-5-5")
SYSTEM = ("You write exception notes for Acme Logistics shift leads. Given one shipment exception as JSON, "
          "write a single plain-English paragraph under 60 words: what happened, where, the delay, and the next action. "
          "Do not invent facts that are not in the record.")
MAX_BUDGET = 1024
RETRYABLE_STATUS = {408, 409, 429, 500, 502, 503, 504, 529}

_results: list[tuple[str, bool]] = []


def check(label: str, condition: bool) -> None:
    _results.append((label, bool(condition)))
    print(f"  [{'PASS' if condition else 'FAIL'}] {label}")


# --------------------------------------------------------------------------- clocks
class FakeClock:
    """Simulated time: sleep() advances the clock instantly, so mock runs never wait."""

    def __init__(self) -> None:
        self.t = 0.0

    def now(self) -> float:
        return self.t

    def sleep(self, seconds: float) -> None:
        self.t += max(0.0, seconds)


class RealClock:
    def now(self) -> float:
        return time.monotonic()

    def sleep(self, seconds: float) -> None:
        time.sleep(max(0.0, seconds))


# --------------------------------------------------------------------------- errors
class InjectedAPIError(Exception):
    """Looks enough like anthropic.APIStatusError for the classifier: status_code + response.headers."""

    def __init__(self, status_code: int, message: str, retry_after: float | None = None) -> None:
        super().__init__(f"{status_code} {message}")
        self.status_code = status_code
        headers = {"retry-after": str(retry_after)} if retry_after is not None else {}
        self.response = SimpleNamespace(headers=headers)


class InjectedTimeout(TimeoutError):
    pass


class CircuitOpenError(Exception):
    pass


class DeadlineExceeded(Exception):
    pass


def classify(exc: BaseException) -> str:
    """Return 'retryable' or 'fatal'. Works for SDK errors and the injected ones without importing anthropic."""
    names = {cls.__name__ for cls in type(exc).__mro__}
    if names & {"APITimeoutError", "APIConnectionError"} or isinstance(exc, (TimeoutError, ConnectionError)):
        return "retryable"
    status = getattr(exc, "status_code", None)
    if status is not None and (status in RETRYABLE_STATUS or status >= 500):
        return "retryable"
    return "fatal"  # 400, 401, 403, 404, 413 and anything unknown: retrying will not help


def retry_after_seconds(exc: BaseException) -> float | None:
    headers = getattr(getattr(exc, "response", None), "headers", None) or {}
    try:
        value = headers.get("retry-after")
        return float(value) if value is not None else None
    except (TypeError, ValueError):
        return None


def full_jitter(rng: random.Random, attempt: int, base: float, cap: float) -> float:
    """AWS-style full jitter: uniform between 0 and the capped exponential delay."""
    return rng.uniform(0.0, min(cap, base * (2 ** (attempt - 1))))


# --------------------------------------------------------------------------- circuit breaker
class CircuitBreaker:
    def __init__(self, clock, failure_threshold: int = 3, reset_timeout: float = 20.0) -> None:
        self.clock = clock
        self.failure_threshold = failure_threshold
        self.reset_timeout = reset_timeout
        self.state = "closed"
        self.failures = 0
        self.opened_at = 0.0
        self.transitions: list[str] = []

    def _move(self, new: str) -> None:
        if new != self.state:
            self.transitions.append(f"{self.state}->{new}")
            self.state = new

    def allow(self) -> bool:
        if self.state == "open" and self.clock.now() - self.opened_at >= self.reset_timeout:
            self._move("half_open")  # let one trial request through
        return self.state != "open"

    def record_success(self) -> None:
        self.failures = 0
        self._move("closed")

    def record_failure(self) -> None:
        self.failures += 1
        if self.state == "half_open" or self.failures >= self.failure_threshold:
            self.opened_at = self.clock.now()
            self._move("open")


# --------------------------------------------------------------------------- fault injection
JOB_RE = re.compile(r"\[job:(SHP-\d+)\]")


class FaultInjectingClient:
    """Wraps a client; replays the fault plan for each job before letting a call through."""

    def __init__(self, inner, plan: dict, clock) -> None:
        self.inner = inner
        self.steps = {job: list(steps) for job, steps in plan["jobs"].items()}
        self.clock = clock
        self.calls: dict[str, int] = {}
        self.messages = self

    def create(self, **request):
        content = request["messages"][-1]["content"]
        job = JOB_RE.search(content if isinstance(content, str) else json.dumps(content))
        job_id = job.group(1) if job else "unknown"
        self.calls[job_id] = self.calls.get(job_id, 0) + 1
        queue = self.steps.get(job_id) or []
        if queue:
            step = queue.pop(0)
            kind = step["kind"]
            if kind == "http":
                raise InjectedAPIError(step["status"], step.get("message", "injected"), step.get("retry_after"))
            if kind == "timeout":
                if MODE == "mock":
                    self.clock.sleep(request.get("timeout") or 0)  # the call "hung" until the timeout fired
                raise InjectedTimeout(f"request exceeded {request.get('timeout')}s (injected)")
            if kind == "connection":
                raise ConnectionError("connection reset (injected)")
            if kind == "refusal":
                details = SimpleNamespace(type="refusal", category=step.get("category"),
                                          explanation=step.get("explanation"))
                return Message(content=[], model=request["model"], stop_reason="refusal", stop_details=details)
        return self.inner.messages.create(**request)


# --------------------------------------------------------------------------- mock model
@register_mock
def fake_exception_note(**request):
    if request.get("system") != SYSTEM:
        return None
    content = request["messages"][-1]["content"]
    record = json.loads(content.split("\n", 1)[1])
    note = (f"{record['shipment_id']} ({record['carrier']}) is held at {record['location']}: {record['reason']}. "
            f"Delay so far {record['hours_delayed']} hours. Next action: {record['recommended_action']}.")
    if request["max_tokens"] < 200:
        return Message(content=[TextBlock(note[:60])], model=request["model"], stop_reason="max_tokens")
    return note


# --------------------------------------------------------------------------- resilient caller
class ResilientCaller:
    def __init__(self, client, clock, breaker: CircuitBreaker, rng: random.Random, trace: list, *,
                 max_attempts: int = 5, base_delay: float = 0.5, max_delay: float = 8.0,
                 per_call_timeout: float = 20.0) -> None:
        self.client, self.clock, self.breaker, self.rng, self.trace = client, clock, breaker, rng, trace
        self.max_attempts, self.base_delay, self.max_delay = max_attempts, base_delay, max_delay
        self.per_call_timeout = per_call_timeout
        self.t0 = clock.now()
        self.last_attempts = 0

    def log(self, job: str, event: str, **detail) -> None:
        self.trace.append({"t": round(self.clock.now() - self.t0, 3), "job": job, "event": event, **detail})

    def call(self, job: str, deadline_s: float, **request):
        """Return (response, attempts). Raises CircuitOpenError, DeadlineExceeded or the last error."""
        deadline = self.clock.now() + deadline_s
        self.last_attempts = 0
        for attempt in range(1, self.max_attempts + 1):
            if not self.breaker.allow():
                self.log(job, "short_circuit", state=self.breaker.state)
                raise CircuitOpenError("circuit open; request not sent")
            remaining = deadline - self.clock.now()
            if remaining <= 0:
                raise DeadlineExceeded(f"deadline of {deadline_s}s used up before attempt {attempt}")
            self.last_attempts = attempt
            try:
                resp = self.client.messages.create(timeout=min(self.per_call_timeout, remaining), **request)
            except Exception as exc:  # noqa: BLE001 - classified below, re-raised when fatal
                kind = classify(exc)
                self.log(job, "error", attempt=attempt, kind=kind, error=type(exc).__name__,
                         status=getattr(exc, "status_code", None))
                if kind == "fatal":
                    raise  # a 4xx is the caller's bug; it must not trip the breaker or be retried
                self.breaker.record_failure()
                if self.breaker.state == "open":
                    self.log(job, "circuit_opened", attempt=attempt)
                    raise CircuitOpenError("circuit opened; stop retrying and requeue") from exc
                if attempt == self.max_attempts:
                    raise
                delay = full_jitter(self.rng, attempt, self.base_delay, self.max_delay)
                hinted = retry_after_seconds(exc)
                if hinted is not None:
                    delay = max(delay, hinted)
                if self.clock.now() + delay >= deadline:
                    self.log(job, "deadline_exceeded", attempt=attempt)
                    raise DeadlineExceeded(f"next retry would land after the {deadline_s}s deadline") from exc
                self.log(job, "backoff", attempt=attempt, delay=round(delay, 3), retry_after=hinted)
                self.clock.sleep(delay)
                continue
            self.breaker.record_success()
            self.log(job, "response", attempt=attempt, stop_reason=resp.stop_reason)
            return resp, attempt
        raise RuntimeError("unreachable")


def resume_after_pause(messages: list, response) -> list:
    """pause_turn: send the conversation back with the paused assistant turn appended, unchanged.

    No extra 'continue' user message: the API sees the trailing server-tool block and resumes.
    """
    return [*messages, {"role": "assistant", "content": response.content}]


def summarise(caller: ResilientCaller, record: dict, settings: dict, deadline_s: float) -> dict:
    """One job: call Claude and handle every stop_reason. Returns an outcome dict, never raises."""
    job = record["shipment_id"]
    messages = [{"role": "user", "content": f"[job:{job}] Write the exception note for this record.\n"
                                            + json.dumps(record)}]
    model, budget = MODEL, settings.get("max_tokens", 400)
    outcome = {"job": job, "attempts": 0, "model": model, "notes": []}
    start = caller.clock.now()
    try:
        for _ in range(6):  # bound on stop_reason follow-ups (continuations, fallbacks, budget raises)
            resp, attempts = caller.call(job, deadline_s, model=model, max_tokens=budget, system=SYSTEM,
                                         messages=messages, output_config={"effort": "low"})
            outcome["attempts"] += attempts
            reason = resp.stop_reason
            if reason == "end_turn":
                outcome.update(status="completed", text=text_of(resp), model=model)
                break
            if reason == "max_tokens" and budget < MAX_BUDGET:
                outcome["notes"].append(f"max_tokens at {budget}; raised budget")
                budget = min(budget * 4, MAX_BUDGET)
                continue
            if reason == "refusal":
                details = getattr(resp, "stop_details", None)
                outcome["refusal_category"] = getattr(details, "category", None)
                if model != FALLBACK_MODEL:
                    outcome["notes"].append(f"refusal on {model} (category={outcome['refusal_category']}); "
                                            f"trying {FALLBACK_MODEL}")
                    model = FALLBACK_MODEL
                    continue
                outcome["status"] = "needs_human_review"
                break
            if reason == "pause_turn":
                messages = resume_after_pause(messages, resp)
                continue
            outcome["status"] = f"unhandled_stop_reason:{reason}"
            break
        else:
            outcome["status"] = "gave_up"
    except CircuitOpenError:
        outcome["status"] = "deferred_circuit_open"
        outcome["attempts"] += caller.last_attempts  # requests actually sent; the short-circuited one was not
    except DeadlineExceeded:
        outcome["status"] = "deadline_exceeded"
        outcome["attempts"] += caller.last_attempts
    except Exception as exc:  # noqa: BLE001
        outcome.update(status="failed", error=f"{type(exc).__name__}: {exc}")
        outcome["attempts"] += caller.last_attempts
    outcome["elapsed_s"] = round(caller.clock.now() - start, 2)
    return outcome


# --------------------------------------------------------------------------- idempotent side effects
class LostAck(Exception):
    """The downstream committed the write but the response never reached us."""


class TicketService:
    """A fake downstream ticketing API. With idempotency on, repeated keys return the first ticket."""

    def __init__(self, lose_ack_for: set[str], honour_keys: bool = True) -> None:
        self.tickets: list[dict] = []
        self.by_key: dict[str, dict] = {}
        self.lose_ack_for = set(lose_ack_for)
        self.honour_keys = honour_keys

    def create(self, idempotency_key: str, payload: dict) -> dict:
        if self.honour_keys and idempotency_key in self.by_key:
            return {**self.by_key[idempotency_key], "replayed": True}
        ticket = {"ticket": f"TCK-{len(self.tickets) + 1:04d}", "shipment_id": payload["shipment_id"]}
        self.tickets.append(ticket)
        self.by_key[idempotency_key] = ticket
        if payload["shipment_id"] in self.lose_ack_for:
            self.lose_ack_for.discard(payload["shipment_id"])
            raise LostAck("write committed, response lost")
        return {**ticket, "replayed": False}


def idempotency_key(record: dict) -> str:
    """Derived from the business identity, so every retry of the same action sends the same key."""
    raw = f"acme|create_ticket|{record['shipment_id']}|{record['exception_code']}"
    return hashlib.sha256(raw.encode()).hexdigest()[:24]


def create_ticket(service: TicketService, record: dict, note: str, retries: int = 3) -> tuple[dict, int]:
    key = idempotency_key(record)
    for attempt in range(1, retries + 1):
        try:
            return service.create(key, {"shipment_id": record["shipment_id"], "note": note}), attempt
        except LostAck:
            continue
    raise RuntimeError("ticket creation failed")


# --------------------------------------------------------------------------- main
def main() -> int:
    wall_start = time.monotonic()
    banner("Lab 18: Reliability engineering")
    records = {r["shipment_id"]: r for r in json.loads((DATA / "shipment_exceptions.json").read_text())["exceptions"]}
    plan = json.loads((DATA / "fault_plan.json").read_text())
    clock = FakeClock() if MODE == "mock" else RealClock()
    rng = random.Random(plan["seed"])
    trace: list[dict] = []

    client = get_client()
    if hasattr(client, "with_options"):
        client = client.with_options(max_retries=0)  # this lab owns retries; avoid retrying twice
    faulty = FaultInjectingClient(client, plan, clock)

    reset_timeout = 20.0 if MODE == "mock" else 5.0
    breaker = CircuitBreaker(clock, failure_threshold=3, reset_timeout=reset_timeout)
    caller = ResilientCaller(faulty, clock, breaker, rng, trace)
    settings = plan.get("job_settings", {})

    def show(o: dict) -> None:
        extra = "; ".join(o["notes"])
        timing = f"elapsed {o['elapsed_s']:>5}s" if MODE == "mock" else "elapsed varies"
        print(f"  {o['job']}  {o['status']:<22} attempts={o['attempts']}  {timing}  {extra}")

    outcomes: dict[str, dict] = {}
    print("Phase 1: transient errors, a fatal error and stop_reason handling\n")
    for job in ["SHP-1001", "SHP-1002", "SHP-1003", "SHP-1004", "SHP-1005", "SHP-1006", "SHP-1007"]:
        outcomes[job] = summarise(caller, records[job], settings.get(job, {}), deadline_s=60)
        show(outcomes[job])

    print("\nPhase 2: a sustained outage trips the circuit breaker\n")
    deferred = []
    for job in ["SHP-2001", "SHP-2002"]:
        calls_before = faulty.calls.get(job, 0)
        o = summarise(caller, records[job], {}, deadline_s=60)
        o["api_calls_while_open"] = faulty.calls.get(job, 0) - calls_before if o["status"] == "deferred_circuit_open" else None
        outcomes[job] = o
        show(o)
        if o["status"] == "deferred_circuit_open":
            deferred.append(job)
    print(f"  breaker state: {breaker.state}; requeueing {deferred} after {reset_timeout + 1:.0f}s")
    clock.sleep(reset_timeout + 1)
    for job in deferred:
        o = summarise(caller, records[job], {}, deadline_s=60)
        o["requeued"] = True
        outcomes[job + "/retry"] = o
        show(o)
    print(f"  breaker transitions: {breaker.transitions}")

    print("\nPhase 3: an overall deadline stops a retry storm\n")
    deadline_caller = ResilientCaller(faulty, clock, CircuitBreaker(clock, failure_threshold=10), rng, trace)
    outcomes["SHP-3001"] = summarise(deadline_caller, records["SHP-3001"], {}, deadline_s=3)
    show(outcomes["SHP-3001"])

    print("\nPhase 4: idempotent side effects (create one ticket per completed note)\n")
    completed = {o["job"]: o for o in outcomes.values() if o.get("status") == "completed"}
    service = TicketService(set(plan.get("lost_ticket_ack", [])))
    naive = TicketService(set(plan.get("lost_ticket_ack", [])), honour_keys=False)
    for job, o in sorted(completed.items()):
        ticket, tries = create_ticket(service, records[job], o["text"])
        create_ticket(naive, records[job], o["text"])
        flag = " (ack lost, retried with the same key, replayed)" if ticket["replayed"] else ""
        print(f"  {job} -> {ticket['ticket']} after {tries} attempt(s){flag}")
    print(f"  tickets with idempotency keys: {len(service.tickets)}; without keys: {len(naive.tickets)}")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "trace.jsonl").write_text("\n".join(json.dumps(e) for e in trace) + "\n", encoding="utf-8")
    (OUT_DIR / "outcomes.json").write_text(json.dumps(outcomes, indent=2), encoding="utf-8")
    print(f"\n  trace ({len(trace)} events) and outcomes written to {OUT_DIR}")

    print("\nSelf-checks")
    o = outcomes
    check("classifier: 400/401/403/404 are fatal",
          all(classify(InjectedAPIError(s, "x")) == "fatal" for s in (400, 401, 403, 404)))
    check("classifier: 408/409/429/500/529 and timeouts are retryable",
          all(classify(InjectedAPIError(s, "x")) == "retryable" for s in (408, 409, 429, 500, 529))
          and classify(InjectedTimeout()) == "retryable")
    jit = random.Random(1)
    check("full jitter stays within [0, cap]", all(0 <= full_jitter(jit, a, 0.5, 8.0) <= 8.0 for a in range(1, 12)))
    check("SHP-1001 completed first time", o["SHP-1001"]["status"] == "completed" and o["SHP-1001"]["attempts"] == 1)
    waits_1002 = [e["delay"] for e in trace if e["job"] == "SHP-1002" and e["event"] == "backoff"]
    check("SHP-1002 honoured retry-after (waited >= 2s) then completed",
          o["SHP-1002"]["status"] == "completed" and waits_1002 and waits_1002[0] >= 2)
    check("SHP-1003 survived 529 + 500 in 3 attempts", o["SHP-1003"]["status"] == "completed" and o["SHP-1003"]["attempts"] == 3)
    check("SHP-1004 recovered from a timeout", o["SHP-1004"]["status"] == "completed" and o["SHP-1004"]["attempts"] == 2)
    check("SHP-1005 failed fast on 400 with one attempt",
          o["SHP-1005"]["status"] == "failed" and o["SHP-1005"]["attempts"] == 1 and faulty.calls["SHP-1005"] == 1)
    check("SHP-1006 completed despite a small max_tokens budget", o["SHP-1006"]["status"] == "completed")
    if MODE == "mock":
        check("SHP-1006 hit max_tokens and raised its budget", any("max_tokens" in n for n in o["SHP-1006"]["notes"]))
    check("SHP-1007 refusal recorded its category and fell back",
          o["SHP-1007"]["refusal_category"] == "cyber" and o["SHP-1007"]["model"] == FALLBACK_MODEL
          and o["SHP-1007"]["status"] == "completed")
    check("outage opened the breaker and SHP-2002 was short-circuited without an API call",
          o["SHP-2001"]["status"] == "deferred_circuit_open" and o["SHP-2001"]["attempts"] == 3
          and o["SHP-2002"]["status"] == "deferred_circuit_open"
          and o["SHP-2002"]["api_calls_while_open"] == 0)
    check("breaker went closed -> open -> half_open -> closed",
          breaker.transitions == ["closed->open", "open->half_open", "half_open->closed"])
    check("both deferred jobs completed after requeue",
          all(o[f"{j}/retry"]["status"] == "completed" for j in ("SHP-2001", "SHP-2002")))
    check("SHP-3001 stopped at the deadline after 2 calls",
          o["SHP-3001"]["status"] == "deadline_exceeded" and o["SHP-3001"]["attempts"] == 2
          and faulty.calls["SHP-3001"] == 2)
    check("one ticket per completed job despite a lost ack", len(service.tickets) == len(completed))
    check("without idempotency keys the lost ack creates a duplicate", len(naive.tickets) == len(completed) + 1)
    paused = resume_after_pause([{"role": "user", "content": "q"}], SimpleNamespace(content=["block"]))
    check("pause_turn resume appends the assistant turn and no extra user message",
          paused[-1] == {"role": "assistant", "content": ["block"]} and len(paused) == 2)
    if MODE == "mock":
        check("mock run finished in under 20 s of real time", time.monotonic() - wall_start < 20)

    failed = [label for label, ok in _results if not ok]
    print(f"\n{len(_results) - len(failed)}/{len(_results)} checks passed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
