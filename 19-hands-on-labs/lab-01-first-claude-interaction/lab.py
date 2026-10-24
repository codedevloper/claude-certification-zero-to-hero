"""Lab 01: your first Claude interaction.

Sends a single request with a system prompt, inspects every field of the response
(content blocks, stop_reason, usage, ids), continues the conversation for a second
turn, and shows how to detect a truncated answer (stop_reason == "max_tokens").

Run offline (default):   CLAUDE_LAB_MODE=mock python lab.py
Run against the API:      CLAUDE_LAB_MODE=live python lab.py   (uses API credits)
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "common"))
from claude_lab import get_client, MODEL, register_mock, text_of, banner  # noqa: E402
from claude_lab import MODE, Message, TextBlock, Usage  # noqa: E402  (mock-only helpers)

DATA = Path(__file__).resolve().parent / "data"

# A stable system prompt: who Claude is, who it serves, and the boundaries it keeps.
SYSTEM_PROMPT = (DATA / "system_prompt.txt").read_text(encoding="utf-8").strip()

KNOWN_STOP_REASONS = {"end_turn", "max_tokens", "stop_sequence", "tool_use", "pause_turn", "refusal"}


# --------------------------------------------------------------------------- mock responses
# These fake Claude when CLAUDE_LAB_MODE=mock. They are deterministic so the self-checks
# below always see the same answers. In live mode they are never called.
@register_mock
def fake_claude(**request):
    question = request["messages"][-1]["content"]
    if not isinstance(question, str):
        return None
    if request["max_tokens"] < 100:
        # Simulate a response that ran out of room part-way through a sentence.
        partial = "An annual percentage rate (APR) is the yearly cost of borrowing, including"
        return Message(
            content=[TextBlock(partial)],
            model=request["model"],
            stop_reason="max_tokens",
            usage=Usage(input_tokens=212, output_tokens=request["max_tokens"]),
        )
    if "APR" in question and "example" not in question.lower():
        return (
            "An annual percentage rate (APR) is the yearly cost of a loan expressed as a "
            "percentage. Unlike the plain interest rate, it also includes most fees you pay to "
            "take out the loan, such as an origination fee. That makes APR the better number "
            "for comparing two loan offers side by side.\n\n"
            "This is general information, not financial advice. A Northwind Lending loan "
            "specialist can explain the figures on your own offer."
        )
    if "example" in question.lower():
        # The follow-up only makes sense if the earlier turns were sent again.
        assert len(request["messages"]) == 3, "the follow-up must include the conversation history"
        return (
            "Here is a simple illustration with made-up numbers. Offer A has a 9.0% interest "
            "rate and no fees. Offer B has an 8.5% interest rate but adds a 3% origination fee. "
            "Once the fee is spread across the loan term, Offer B's APR can end up higher than "
            "Offer A's, so Offer A may cost less overall even though its headline rate is "
            "higher.\n\nThis is general information, not financial advice."
        )
    return None


# --------------------------------------------------------------------------- lab code
def describe(response) -> None:
    """Print every response field a beginner should know about."""
    print(f"  id            : {response.id}")
    print(f"  model         : {response.model}")
    print(f"  role          : {response.role}")
    print(f"  stop_reason   : {response.stop_reason}")
    print(f"  content blocks: {[block.type for block in response.content]}")
    usage = response.usage
    print(f"  usage         : input_tokens={usage.input_tokens}, output_tokens={usage.output_tokens}")
    request_id = getattr(response, "_request_id", None)  # set by the real SDK from the request-id header
    if request_id:
        print(f"  request id    : {request_id}")


def safe_answer(response) -> str:
    """Check stop_reason before trusting content. Returns the text, or raises."""
    if response.stop_reason == "refusal":
        details = getattr(response, "stop_details", None)
        category = getattr(details, "category", None) if details else None
        raise RuntimeError(f"Claude declined this request (category={category}).")
    if response.stop_reason == "max_tokens":
        raise RuntimeError("The answer was cut off at max_tokens. Raise max_tokens or ask for less.")
    if response.stop_reason not in {"end_turn", "stop_sequence"}:
        raise RuntimeError(f"Unexpected stop_reason for a plain chat call: {response.stop_reason}")
    return text_of(response)


def main() -> int:
    banner("Lab 01 - First Claude interaction")
    client = get_client()

    # Step 1: one request, one response.
    question = "In one short paragraph, what does APR mean on a personal loan?"
    messages = [{"role": "user", "content": question}]
    print("Step 1: single request with a system prompt")
    first = client.messages.create(
        model=MODEL,
        max_tokens=4096,                       # room for adaptive thinking plus a short answer
        system=SYSTEM_PROMPT,
        output_config={"effort": "low"},       # a simple explanation does not need deep reasoning
        messages=messages,
    )
    describe(first)
    answer = safe_answer(first)
    print(f"\n  Claude says:\n  {answer}\n")

    # Step 2: continue the conversation. The API is stateless, so resend the history.
    print("Step 2: a follow-up turn (the full history is sent again)")
    messages.append({"role": "assistant", "content": first.content})
    messages.append({"role": "user", "content": "Can you give me a simple example with made-up numbers?"})
    second = client.messages.create(
        model=MODEL,
        max_tokens=4096,
        system=SYSTEM_PROMPT,
        output_config={"effort": "low"},
        messages=messages,
    )
    describe(second)
    follow_up = safe_answer(second)
    print(f"\n  Claude says:\n  {follow_up}\n")

    # Step 3: what a truncated answer looks like, and how to detect it.
    print("Step 3: a deliberately tiny max_tokens to trigger truncation")
    short = client.messages.create(
        model=MODEL,
        max_tokens=40,
        system=SYSTEM_PROMPT,
        output_config={"effort": "low"},
        messages=[{"role": "user", "content": question}],
    )
    describe(short)
    try:
        safe_answer(short)
        truncated_detected = False
    except RuntimeError as exc:
        truncated_detected = short.stop_reason == "max_tokens"
        print(f"  Handled: {exc}")

    # Self-checks: prove the code paths behaved as intended.
    print("\nSelf-checks")
    # Structural checks must always pass. Wording checks are exact in mock mode but only
    # advisory in live mode, because a real model phrases things its own way.
    checks = {
        "stop_reason is a documented value": all(
            r.stop_reason in KNOWN_STOP_REASONS for r in (first, second, short)
        ),
        "first answer finished normally (end_turn)": first.stop_reason == "end_turn",
        "usage reports input and output tokens": first.usage.input_tokens > 0 and first.usage.output_tokens > 0,
        "history alternates user/assistant/user": [m["role"] for m in messages] == ["user", "assistant", "user"],
        "answer stays inside the system prompt's scope": "not financial advice" in answer.lower(),
        "truncation detected via stop_reason": truncated_detected,
    }
    wording_checks = {"answer stays inside the system prompt's scope"}
    failed = False
    for name, ok in checks.items():
        if ok:
            print(f"  [PASS] {name}")
        elif MODE == "live" and name in wording_checks:
            print(f"  [WARN] {name} (live wording varies; read the answer yourself)")
        else:
            print(f"  [FAIL] {name}")
            failed = True
    if failed:
        return 1
    print("\nAll checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
