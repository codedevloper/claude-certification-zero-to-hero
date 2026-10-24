"""Lab 19: Observability for Claude API calls.

Instruments a small multi-tenant workload with:
  * structured JSON logs (one object per line) with a redaction filter,
  * a correlation ID per request plus the API `request-id` (live mode),
  * token and cost metrics per model,
  * latency percentiles (p50 / p95 / p99, nearest-rank method),
  * OpenTelemetry-style spans written to a local JSONL file (no OTel install needed),
  * simple alert rules (error rate, p95 latency SLO, cost per request).

Usage (from the repository root):

    CLAUDE_LAB_MODE=mock python 19-hands-on-labs/lab-19-observability/lab.py   # offline, free
    CLAUDE_LAB_MODE=live python 19-hands-on-labs/lab-19-observability/lab.py   # real API, uses credits

Output files go to $LAB_OUTPUT_DIR/claude-labs/lab-19 (default: the system temp directory).
Mock mode uses a seeded fake clock, so IDs, timestamps and latencies are identical on every run.
"""
from __future__ import annotations

import json
import logging
import math
import os
import random
import re
import secrets
import sys
import tempfile
import time
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "common"))
from claude_lab import MODE, Message, TextBlock, Usage, banner, get_client, register_mock, text_of  # noqa: E402

OUT_DIR = Path(os.environ.get("LAB_OUTPUT_DIR") or tempfile.gettempdir()) / "claude-labs" / "lab-19"
SEED = 19

# USD per million tokens, as of 2026-10-24 (claude-api skill; confirm on the live pricing page).
# Haiku 5.5 prices apply to prompts of 100K tokens or fewer; above that it is $0.50 / $2.50.
PRICING = {
    "claude-opus-5-5": {"input": 4.00, "output": 20.00, "cache_read": 0.20},
    "claude-sonnet-5-5": {"input": 2.00, "output": 10.00, "cache_read": 0.10},
    "claude-haiku-5-5": {"input": 0.10, "output": 0.50, "cache_read": 0.01},  # cache_read assumed 0.1x input
}
HAIKU_LONG_PROMPT = {"input": 0.50, "output": 2.50, "cache_read": 0.05}
CACHE_WRITE_MULTIPLIER = 1.25  # 5-minute TTL write premium

SLO_P95_MS = 4000
ERROR_RATE_THRESHOLD = 0.05
COST_PER_REQUEST_THRESHOLD = 0.01

EFFORT = {"classify": "low", "summarise": "low", "analyse": "medium"}
MAX_TOKENS = {"classify": 1024, "summarise": 2048, "analyse": 4096}

SYSTEM_PROMPT = (
    "You are the shared assistant behind an internal operations platform. "
    "Answer the task in the user message briefly. For classification tasks reply with the label only."
)


# --------------------------------------------------------------------------- clocks
class FakeClock:
    """Deterministic clock for mock mode. Time only moves when the lab advances it."""

    def __init__(self) -> None:
        self._ns = int(datetime(2026, 10, 24, 9, 0, tzinfo=timezone.utc).timestamp()) * 1_000_000_000

    def now_ns(self) -> int:
        return self._ns

    def advance_ms(self, ms: float) -> None:
        self._ns += int(ms * 1_000_000)


class RealClock:
    def now_ns(self) -> int:
        return time.time_ns()

    def advance_ms(self, ms: float) -> None:  # real time advances on its own
        pass


def iso(ns: int) -> str:
    return datetime.fromtimestamp(ns / 1e9, tz=timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


# --------------------------------------------------------------------------- redaction
EMAIL = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
API_KEY = re.compile(r"\bsk-ant-[A-Za-z0-9_\-]{8,}")
SSN_LIKE = re.compile(r"\b\d{3}-\d{2}-\d{4}\b")
CARD_LIKE = re.compile(r"\b(?:\d[ -]?){12,18}\d\b")


def luhn_ok(number: str) -> bool:
    digits = [int(d) for d in number if d.isdigit()]
    if not 13 <= len(digits) <= 19:
        return False
    total = 0
    for i, d in enumerate(reversed(digits)):
        if i % 2 == 1:
            d *= 2
            if d > 9:
                d -= 9
        total += d
    return total % 10 == 0


def redact(text: str) -> tuple[str, int]:
    """Replace secrets and personal data with typed markers. Returns (text, count)."""
    count = 0

    def sub(pattern: re.Pattern, label: str, s: str, check=None) -> str:
        nonlocal count

        def repl(m: re.Match) -> str:
            nonlocal count
            if check and not check(m.group(0)):
                return m.group(0)
            count += 1
            return f"[REDACTED:{label}]"

        return pattern.sub(repl, s)

    text = sub(API_KEY, "API_KEY", text)
    text = sub(EMAIL, "EMAIL", text)
    text = sub(SSN_LIKE, "SSN", text)
    text = sub(CARD_LIKE, "CARD", text, check=luhn_ok)
    return text, count


class RedactingFilter(logging.Filter):
    """Last line of defence: redacts every string field before a record is written."""

    def filter(self, record: logging.LogRecord) -> bool:
        fields = getattr(record, "fields", {})
        for key, value in list(fields.items()):
            if isinstance(value, str):
                fields[key] = redact(value)[0]
        record.msg = redact(str(record.msg))[0]
        return True


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        fields = dict(getattr(record, "fields", {}))
        payload = {"ts": fields.pop("ts", None), "level": record.levelname, "event": record.getMessage()}
        payload.update(fields)
        return json.dumps(payload, sort_keys=False)


def build_logger(path: Path) -> logging.Logger:
    logger = logging.getLogger("lab19")
    logger.setLevel(logging.DEBUG)
    logger.handlers.clear()
    logger.propagate = False
    handler = logging.FileHandler(path, mode="w", encoding="utf-8")
    handler.setFormatter(JsonFormatter())
    handler.addFilter(RedactingFilter())
    logger.addHandler(handler)
    return logger


# --------------------------------------------------------------------------- tracing
@dataclass
class Span:
    trace_id: str
    span_id: str
    parent_span_id: str | None
    name: str
    kind: str
    start_time_unix_nano: int
    end_time_unix_nano: int = 0
    attributes: dict[str, Any] = field(default_factory=dict)
    status: dict[str, str] = field(default_factory=lambda: {"code": "UNSET"})
    events: list[dict[str, Any]] = field(default_factory=list)

    def set_error(self, error_type: str, message: str) -> None:
        self.status = {"code": "ERROR", "message": message}
        self.attributes["error.type"] = error_type
        self.events.append({"name": "exception", "attributes": {"exception.type": error_type, "exception.message": message}})


class FileTracer:
    """A tiny tracer that writes OTel-shaped spans to JSONL. Swap for the real OTel SDK in production."""

    def __init__(self, clock, rng: random.Random, path: Path) -> None:
        self.clock, self.rng, self.path = clock, rng, path
        self.path.write_text("", encoding="utf-8")
        self.finished: list[Span] = []

    def _hex(self, bits: int) -> str:
        if MODE == "mock":
            return f"{self.rng.getrandbits(bits):0{bits // 4}x}"
        return secrets.token_hex(bits // 8)

    def new_trace_id(self) -> str:
        return self._hex(128)

    @contextmanager
    def span(self, name: str, trace_id: str, parent: Span | None, kind: str = "INTERNAL", **attrs: Any) -> Iterator[Span]:
        s = Span(trace_id, self._hex(64), parent.span_id if parent else None, name, kind, self.clock.now_ns(), attributes=dict(attrs))
        try:
            yield s
        finally:
            s.end_time_unix_nano = self.clock.now_ns()
            if s.status["code"] == "UNSET":
                s.status = {"code": "OK"}
            self.finished.append(s)
            with self.path.open("a", encoding="utf-8") as fh:
                fh.write(json.dumps(s.__dict__) + "\n")


# --------------------------------------------------------------------------- cost and stats
def cost_usd(model: str, usage: Any) -> float:
    inp = getattr(usage, "input_tokens", 0) or 0
    out = getattr(usage, "output_tokens", 0) or 0
    c_write = getattr(usage, "cache_creation_input_tokens", 0) or 0
    c_read = getattr(usage, "cache_read_input_tokens", 0) or 0
    price = PRICING[model]
    if model == "claude-haiku-5-5" and (inp + c_write + c_read) > 100_000:
        price = HAIKU_LONG_PROMPT
    total = (
        inp * price["input"]
        + c_write * price["input"] * CACHE_WRITE_MULTIPLIER
        + c_read * price["cache_read"]
        + out * price["output"]
    )
    return total / 1_000_000


def percentile(values: list[float], p: float) -> float:
    """Nearest-rank percentile: the smallest value with at least p% of samples at or below it."""
    if not values:
        return 0.0
    ordered = sorted(values)
    rank = max(1, math.ceil(p / 100 * len(ordered)))
    return ordered[rank - 1]


# --------------------------------------------------------------------------- mock mode
class SimulatedAPIError(Exception):
    def __init__(self, status_code: int, error_type: str) -> None:
        super().__init__(f"{status_code} {error_type}")
        self.status_code = status_code
        self.error_type = error_type


class SimulatedTimeout(Exception):
    error_type = "timeout"


FAULTS: dict[str, str] = {}  # prompt -> fault name (mock mode only)
LABELS = {
    "patient portal": "ACCESS", "co-pay": "BILLING", "lab results": "ACCESS", "receipt": "BILLING",
    "Kade Street": "ADDRESS", "crushed": "DAMAGE", "Ferry": "DELAY",
    "clearer": "PRAISE", "download": "QUESTION", "too loud": "COMPLAINT",
}


@register_mock
def fake_claude(**request: Any):
    if request.get("system") != SYSTEM_PROMPT:
        return None
    prompt = request["messages"][-1]["content"]
    fault = FAULTS.get(prompt)
    if fault == "overloaded":
        raise SimulatedAPIError(529, "overloaded_error")
    if fault == "timeout":
        raise SimulatedTimeout("request exceeded client timeout")
    if prompt.startswith("Classify"):
        return next((label for key, label in LABELS.items() if key in prompt), "QUESTION")
    if prompt.startswith("Summarise"):
        if "autopay" in prompt:
            return "Customer reported a failed autopay payment and asked for a callback."
        if "key" in prompt:
            return "A developer exposed an API key in a chat channel and asked for it to be rotated."
        return "Short summary: " + prompt.split(":", 1)[1].strip().split(";")[0].rstrip(".") + "."
    if request["max_tokens"] < 200:
        text = "Main risks: account takeover changing dates, missed payments from accidental changes, and"
        return Message(content=[TextBlock(text)], model=request["model"], stop_reason="max_tokens",
                       usage=Usage(input_tokens=len(json.dumps(request["messages"])) // 4, output_tokens=request["max_tokens"]))
    return ("Likely drivers, ranked: (1) staffing gaps reduce capacity at peak hours; (2) the process change "
            "adds variance while people adapt; (3) external constraints lengthen routes. Next steps: measure each "
            "driver separately for two weeks, then run one controlled change at a time and compare against a baseline.")


def simulated_latency_ms(rng: random.Random, model: str, output_tokens: int) -> float:
    base = {"claude-haiku-5-5": 250, "claude-sonnet-5-5": 600, "claude-opus-5-5": 1400}[model]
    per_token = {"claude-haiku-5-5": 2, "claude-sonnet-5-5": 6, "claude-opus-5-5": 12}[model]
    latency = base + per_token * output_tokens + rng.uniform(0, 300)
    if rng.random() < 0.12:  # occasional slow tail, as seen with queueing or long thinking
        latency *= 3
    return round(latency, 1)


# --------------------------------------------------------------------------- instrumented call
@dataclass
class Record:
    request_id: str
    trace_id: str
    tenant: str
    route: str
    model: str
    status: str
    stop_reason: str | None
    latency_ms: float
    input_tokens: int
    output_tokens: int
    cost: float
    error_type: str | None = None
    api_request_id: str | None = None


def handle(row: dict, client, tracer: FileTracer, clock, rng: random.Random, log: logging.Logger) -> Record:
    model, route, tenant, prompt = row["model"], row["route"], row["tenant"], row["prompt"]
    max_tokens = row.get("max_tokens", MAX_TOKENS[route])
    request_id = f"req-{rng.getrandbits(48):012x}" if MODE == "mock" else f"req-{secrets.token_hex(6)}"
    trace_id = tracer.new_trace_id()
    base = {"request_id": request_id, "trace_id": trace_id, "tenant": tenant, "route": route, "model": model}

    with tracer.span("lab19.handle_request", trace_id, None, kind="SERVER",
                     **{"app.request_id": request_id, "app.tenant": tenant, "app.route": route}) as root:
        with tracer.span("lab19.redact_preview", trace_id, root) as red:
            preview, hits = redact(prompt)
            red.attributes["app.redactions"] = hits
            clock.advance_ms(0.4)
        # A careless developer logs the raw prompt at DEBUG: the filter still redacts it.
        log.debug("llm.request.debug", extra={"fields": {**base, "ts": iso(clock.now_ns()), "prompt": prompt}})

        attrs = {
            "gen_ai.operation.name": "chat",
            "gen_ai.provider.name": "anthropic",
            "gen_ai.request.model": model,
            "gen_ai.request.max_tokens": max_tokens,
        }
        with tracer.span(f"chat {model}", trace_id, root, kind="CLIENT", **attrs) as span:
            start = clock.now_ns()
            try:
                response = client.messages.create(
                    model=model,
                    max_tokens=max_tokens,
                    system=SYSTEM_PROMPT,
                    messages=[{"role": "user", "content": prompt}],
                    output_config={"effort": EFFORT[route]},
                )
            except Exception as exc:  # record, then decide (lab 18 covers retries)
                error_type = getattr(exc, "error_type", None) or type(exc).__name__
                if MODE == "mock":
                    clock.advance_ms(8000.0 if isinstance(exc, SimulatedTimeout) else 120.0)
                latency = round((clock.now_ns() - start) / 1e6, 1)
                span.set_error(error_type, str(exc)[:120])
                root.set_error(error_type, "upstream call failed")
                log.error("llm.request.failed", extra={"fields": {
                    **base, "ts": iso(clock.now_ns()), "latency_ms": latency, "error_type": error_type,
                    "status_code": getattr(exc, "status_code", None), "prompt_preview": preview[:80]}})
                return Record(request_id, trace_id, tenant, route, model, "error", None, latency, 0, 0, 0.0, error_type)

            usage = response.usage
            if MODE == "mock":
                clock.advance_ms(simulated_latency_ms(rng, model, usage.output_tokens))
            latency = round((clock.now_ns() - start) / 1e6, 1)
            cost = cost_usd(model, usage)
            api_request_id = getattr(response, "_request_id", None)
            cache_read = getattr(usage, "cache_read_input_tokens", 0) or 0
            cache_write = getattr(usage, "cache_creation_input_tokens", 0) or 0
            span.attributes.update({
                "gen_ai.response.model": response.model,
                "gen_ai.response.finish_reasons": [response.stop_reason],
                # The GenAI convention counts cache reads and writes inside input_tokens;
                # the Messages API's usage.input_tokens excludes them, so add them back here.
                "gen_ai.usage.input_tokens": usage.input_tokens + cache_read + cache_write,
                "gen_ai.usage.cache_read.input_tokens": cache_read,
                "gen_ai.usage.cache_write.input_tokens": cache_write,
                "gen_ai.usage.output_tokens": usage.output_tokens,
                "app.cost_usd": round(cost, 8),
            })
            if api_request_id:
                span.attributes["anthropic.request.id"] = api_request_id

            level, event = logging.INFO, "llm.request.completed"
            if response.stop_reason == "max_tokens":
                level, event = logging.WARNING, "llm.request.truncated"
            elif response.stop_reason == "refusal":
                level, event = logging.WARNING, "llm.request.refused"
            log.log(level, event, extra={"fields": {
                **base, "ts": iso(clock.now_ns()), "api_request_id": api_request_id,
                "stop_reason": response.stop_reason, "input_tokens": usage.input_tokens,
                "output_tokens": usage.output_tokens, "cost_usd": round(cost, 8), "latency_ms": latency,
                "prompt_preview": preview[:80], "response_preview": redact(text_of(response))[0][:60]}})
            return Record(request_id, trace_id, tenant, route, model, "ok", response.stop_reason, latency,
                          usage.input_tokens, usage.output_tokens, cost, api_request_id=api_request_id)


# --------------------------------------------------------------------------- main
RESULTS: list[tuple[str, bool]] = []


def check(label: str, condition: bool) -> None:
    RESULTS.append((label, bool(condition)))
    print(f"  [{'PASS' if condition else 'FAIL'}] {label}")


def main() -> int:
    banner("Lab 19: Observability")
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    log_path, span_path = OUT_DIR / "app.log.jsonl", OUT_DIR / "spans.jsonl"
    print(f"Writing logs and spans to: {OUT_DIR}")

    rows = [json.loads(line) for line in (HERE / "data" / "requests.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
    if MODE == "mock":
        FAULTS.update({r["prompt"]: r["fault"] for r in rows if r.get("fault")})

    clock = FakeClock() if MODE == "mock" else RealClock()
    rng = random.Random(SEED)
    tracer = FileTracer(clock, rng, span_path)
    log = build_logger(log_path)
    client = get_client()

    print("\n1) Per-request results")
    print(f"  {'#':>2} {'tenant':<18} {'model':<18} {'route':<9} {'status':<6} {'stop':<10} {'lat_ms':>8} {'in':>5} {'out':>5} {'cost_usd':>10}")
    records: list[Record] = []
    for i, row in enumerate(rows, 1):
        r = handle(row, client, tracer, clock, rng, log)
        records.append(r)
        clock.advance_ms(250)  # gap between requests
        print(f"  {i:>2} {r.tenant:<18} {r.model:<18} {r.route:<9} {r.status:<6} {str(r.stop_reason or r.error_type):<10.10} "
              f"{r.latency_ms:>8.1f} {r.input_tokens:>5} {r.output_tokens:>5} {r.cost:>10.6f}")
    for handler in log.handlers:
        handler.close()

    print("\n2) Metrics by model")
    print(f"  {'model':<18} {'requests':>8} {'errors':>6} {'in_tok':>7} {'out_tok':>7} {'cost_usd':>10}")
    for model in PRICING:
        rs = [r for r in records if r.model == model]
        print(f"  {model:<18} {len(rs):>8} {sum(r.status == 'error' for r in rs):>6} {sum(r.input_tokens for r in rs):>7} "
              f"{sum(r.output_tokens for r in rs):>7} {sum(r.cost for r in rs):>10.6f}")
    total_cost = sum(r.cost for r in records)
    errors = sum(r.status == "error" for r in records)
    error_rate = errors / len(records)
    latencies = [r.latency_ms for r in records]
    p50, p95, p99 = (percentile(latencies, p) for p in (50, 95, 99))
    print(f"  total cost: ${total_cost:.6f}   error rate: {error_rate:.1%} ({errors}/{len(records)})")

    print("\n3) Latency percentiles (nearest-rank, all requests incl. errors)")
    print(f"  p50={p50:.1f} ms   p95={p95:.1f} ms   p99={p99:.1f} ms   (SLO: p95 <= {SLO_P95_MS} ms)")

    print("\n4) Alert rules")
    rules = [
        ("error_rate > 5%", error_rate > ERROR_RATE_THRESHOLD, f"{error_rate:.1%}"),
        (f"p95_latency > {SLO_P95_MS} ms", p95 > SLO_P95_MS, f"{p95:.1f} ms"),
        ("max cost/request > $0.01", max(r.cost for r in records) > COST_PER_REQUEST_THRESHOLD, f"${max(r.cost for r in records):.6f}"),
    ]
    for name, firing, value in rules:
        print(f"  {'FIRING' if firing else 'ok    '}  {name:<28} observed {value}")

    log_lines = log_path.read_text(encoding="utf-8").splitlines()
    span_lines = span_path.read_text(encoding="utf-8").splitlines()
    print("\n5) Sample redacted log line (request 4, DEBUG raw-prompt log)")
    debug_lines = [json.loads(line) for line in log_lines if '"llm.request.debug"' in line]
    sample = debug_lines[3]
    print("  " + json.dumps({k: sample[k] for k in ("ts", "level", "event", "request_id", "prompt")})[:400])

    print("\n6) Span tree for request 1")
    spans = [json.loads(line) for line in span_lines]
    first = [s for s in spans if s["trace_id"] == records[0].trace_id]
    for s in sorted(first, key=lambda s: (s["parent_span_id"] is not None, s["start_time_unix_nano"])):
        indent = "  " if s["parent_span_id"] is None else "    └─ "
        dur = (s["end_time_unix_nano"] - s["start_time_unix_nano"]) / 1e6
        keys = {k: v for k, v in s["attributes"].items() if k.startswith("gen_ai.usage") or k == "gen_ai.request.model"}
        print(f"  {indent}{s['name']} [{s['kind']}] {dur:.1f} ms status={s['status']['code']} {json.dumps(keys) if keys else ''}")

    print("\n7) Self-checks")
    raw_text = log_path.read_text(encoding="utf-8")
    check("redact() masks email, API key, SSN-like and Luhn-valid card",
          redact("a@b.example sk-ant-api03-FAKE-not-a-real-key 123-45-6789 4111-1111-1111-1111")[1] == 4)
    check("redact() leaves a non-Luhn 16-digit order number alone",
          redact("order 1234 5678 9012 3456")[1] == 0)
    check("percentile() nearest-rank on 1..100 gives 50/95/99",
          [percentile(list(range(1, 101)), p) for p in (50, 95, 99)] == [50, 95, 99])
    check("log file has one valid JSON object per line",
          all(isinstance(json.loads(line), dict) for line in log_lines))
    check("no raw email, card number or API key reached the log file",
          not EMAIL.search(raw_text) and "4111 1111" not in raw_text and "sk-ant-" not in raw_text)
    check("redaction markers are present in the log file", "[REDACTED:EMAIL]" in raw_text and "[REDACTED:API_KEY]" in raw_text)
    check("three spans per request", len(spans) == 3 * len(records))
    check("trace_id is 32 hex chars and span_id 16 hex chars",
          all(re.fullmatch(r"[0-9a-f]{32}", s["trace_id"]) and re.fullmatch(r"[0-9a-f]{16}", s["span_id"]) for s in spans))
    ids = {(s["trace_id"], s["span_id"]) for s in spans}
    check("every child span's parent exists in the same trace",
          all(s["parent_span_id"] is None or (s["trace_id"], s["parent_span_id"]) in ids for s in spans))
    check("request IDs are unique", len({r.request_id for r in records}) == len(records))
    check("total cost equals the sum of per-model costs",
          abs(total_cost - sum(sum(r.cost for r in records if r.model == m) for m in PRICING)) < 1e-12)
    check("failed calls are ERROR spans with error.type",
          sum(1 for s in spans if s["kind"] == "CLIENT" and s["status"]["code"] == "ERROR" and "error.type" in s["attributes"]) == errors)
    if MODE == "mock":
        check("mock: two injected faults recorded and error-rate alert fires", errors == 2 and rules[0][1])
        check("mock: truncated response logged at WARNING", '"llm.request.truncated"' in raw_text)

    failed = [label for label, ok in RESULTS if not ok]
    print(f"\n{len(RESULTS) - len(failed)}/{len(RESULTS)} self-checks passed.")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
