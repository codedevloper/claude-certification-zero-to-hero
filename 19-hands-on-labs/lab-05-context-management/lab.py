"""Lab 05: context management - token counting, compaction and prompt caching.

Part A counts tokens before sending, and checks a request against a budget.
Part B compacts a long support conversation: older turns become a summary, recent
turns stay verbatim, and the key facts must survive.
Part C compares two prompt layouts for caching. The "bad" layout puts a timestamp at
the top of the system prompt, so the cached prefix changes on every request; the "good"
layout keeps the prefix stable and moves volatile data after the cache breakpoint. It
reads cache_creation_input_tokens and cache_read_input_tokens and prices both layouts.

Run offline (default):   CLAUDE_LAB_MODE=mock python lab.py
Run against the API:      CLAUDE_LAB_MODE=live python lab.py   (uses API credits)
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "common"))
from claude_lab import get_client, MODEL, register_mock, text_of, banner  # noqa: E402
from claude_lab import FAST_MODEL, MODE, Message, TextBlock, Usage  # noqa: E402

DATA = Path(__file__).resolve().parent / "data"
HANDBOOK = (DATA / "support_handbook.md").read_text(encoding="utf-8")
CONVERSATION = json.loads((DATA / "long_conversation.json").read_text(encoding="utf-8"))

INSTRUCTIONS = (
    "You are a Northwind Lending support agent. Follow the handbook in <handbook> exactly. "
    "Reply in at most three sentences."
)
# Facts that must survive compaction, or the agent will ask the customer to repeat themselves.
KEY_FACTS = ["NL-APP-7731", "payslip", "48 months", "email"]
HISTORY_BUDGET_TOKENS = 450      # deliberately small so this short demo triggers compaction
KEEP_RECENT_MESSAGES = 4         # always keep the latest turns verbatim

# Pricing for claude-opus-5-5 from the claude-api skill (cached 2026-10-06), checked 2026-10-24.
# Cache writes with the default 5-minute TTL cost 1.25x base input; cache reads cost $0.20/MTok.
PRICE_PER_MTOK = {"input": 4.00, "cache_write_5m": 5.00, "cache_read": 0.20, "output": 20.00}
TIMESTAMPS = ["2026-10-24T09:00:01Z", "2026-10-24T09:00:17Z", "2026-10-24T09:00:42Z"]
QUESTIONS = [
    "My payslip upload keeps failing. What should I check?",
    "Can I change my direct debit date?",
    "I think I'll miss next month's payment. What happens now?",
]


# --------------------------------------------------------------------------- mock: cache simulator
def _est(obj) -> int:
    return max(1, len(json.dumps(obj, default=str)) // 4)


_MOCK_CACHE: set[str] = set()
MIN_CACHEABLE_TOKENS = 512  # per the claude-api skill for claude-opus-5-5; check the docs for your model


@register_mock
def fake_cached_answer(**request):
    """Simulate prefix caching: everything up to the last cache_control marker is the prefix."""
    system = request.get("system")
    if not isinstance(system, list) or not any("cache_control" in block for block in system):
        return None
    last_marker = max(i for i, block in enumerate(system) if "cache_control" in block)
    prefix = {"tools": request.get("tools"), "system": system[: last_marker + 1]}
    prefix_tokens = _est(prefix)
    suffix_tokens = _est({"system": system[last_marker + 1:], "messages": request["messages"]})
    key = hashlib.sha256(json.dumps(prefix, sort_keys=True).encode()).hexdigest()
    created = read = 0
    if prefix_tokens >= MIN_CACHEABLE_TOKENS:
        if key in _MOCK_CACHE:
            read = prefix_tokens
        else:
            _MOCK_CACHE.add(key)
            created = prefix_tokens
    else:
        suffix_tokens += prefix_tokens
    question = request["messages"][-1]["content"]
    answers = {
        "payslip": "Check the file is a PDF, JPG or PNG under 10 MB and not password-protected, then upload it again through the portal.",
        "direct debit": "Yes, you can change your collection date once every twelve months in the portal.",
        "miss": "Thank you for telling us early. I'm transferring you to our Customer Care team, who can talk through your options.",
    }
    text = next((a for k, a in answers.items() if k in question), "Please check the portal for details.")
    return Message(
        content=[TextBlock(text)],
        model=request["model"],
        usage=Usage(input_tokens=suffix_tokens, output_tokens=_est(text),
                    cache_creation_input_tokens=created, cache_read_input_tokens=read),
    )


@register_mock
def fake_summariser(**request):
    content = request["messages"][-1]["content"]
    if not isinstance(content, str) or "<conversation_to_summarise>" not in content:
        return None
    return (
        "Customer applied for 12,000 EUR (application NL-APP-7731), stage documents pending. "
        "Passport and an August utility bill uploaded. Payslip uploads failed because the PDFs were "
        "password-protected; customer will upload unprotected copies. Customer asked to change the term "
        "from 36 to 48 months; request noted for underwriting. Preferred contact: email, not phone."
    )


@register_mock
def fake_follow_up(**request):
    msgs = request["messages"]
    if not isinstance(msgs[0]["content"], str) or "<conversation_summary>" not in msgs[0]["content"]:
        return None
    return ("Your term change request to 48 months is noted on NL-APP-7731 for the underwriter, and we'll "
            "contact you by email once the payslips have been reviewed.")


# --------------------------------------------------------------------------- part A: counting
def count(client, model: str, system, messages) -> int:
    """Use the token counting endpoint; never a third-party tokenizer."""
    return client.messages.count_tokens(model=model, system=system, messages=messages).input_tokens


# --------------------------------------------------------------------------- part B: compaction
def compact(client, history: list[dict]) -> list[dict]:
    """Summarise older turns, keep recent turns verbatim. Returns a new history list."""
    older, recent = history[:-KEEP_RECENT_MESSAGES], history[-KEEP_RECENT_MESSAGES:]
    transcript = "\n".join(f"{m['role'].upper()}: {m['content']}" for m in older)
    response = client.messages.create(
        model=FAST_MODEL,  # summarisation is a good fit for the smaller, cheaper model
        max_tokens=2048,
        output_config={"effort": "low"},
        system="You compress support conversations so another agent can continue them.",
        messages=[{
            "role": "user",
            "content": (
                "Summarise this conversation in at most 80 words. Keep every identifier, amount, date, "
                "document status, open request and customer preference exactly as stated.\n\n"
                f"<conversation_to_summarise>\n{transcript}\n</conversation_to_summarise>"
            ),
        }],
    )
    if response.stop_reason != "end_turn":
        raise RuntimeError(f"summary incomplete: stop_reason={response.stop_reason}")
    summary = text_of(response).strip()
    # The summary becomes the first user turn. Consecutive user turns are allowed; the API merges them.
    return [{"role": "user", "content": f"<conversation_summary>\n{summary}\n</conversation_summary>"}] + recent


# --------------------------------------------------------------------------- part C: caching
def system_blocks(layout: str, timestamp: str) -> list[dict]:
    handbook_block = {"type": "text", "text": f"<handbook>\n{HANDBOOK}\n</handbook>",
                      "cache_control": {"type": "ephemeral"}}
    if layout == "bad":
        # A changing value at the very top: every byte after it is a new prefix, so nothing is reused.
        return [{"type": "text", "text": f"Current time: {timestamp}\n{INSTRUCTIONS}"}, handbook_block]
    return [{"type": "text", "text": INSTRUCTIONS}, handbook_block]


def cost(usage) -> float:
    p = PRICE_PER_MTOK
    return (usage.input_tokens * p["input"] + usage.cache_creation_input_tokens * p["cache_write_5m"]
            + usage.cache_read_input_tokens * p["cache_read"] + usage.output_tokens * p["output"]) / 1_000_000


def run_layout(client, layout: str) -> list:
    usages = []
    for timestamp, question in zip(TIMESTAMPS, QUESTIONS):
        user = question if layout == "bad" else f"[received {timestamp}] {question}"  # volatile data last
        response = client.messages.create(
            model=MODEL, max_tokens=2048, output_config={"effort": "low"},
            system=system_blocks(layout, timestamp),
            messages=[{"role": "user", "content": user}],
        )
        if response.stop_reason != "end_turn":
            raise RuntimeError(f"stop_reason={response.stop_reason}")
        u = response.usage
        usages.append(u)
        print(f"  {layout:<4} req {len(usages)}: input={u.input_tokens:>5}  cache_write={u.cache_creation_input_tokens:>5}  "
              f"cache_read={u.cache_read_input_tokens:>5}  output={u.output_tokens:>4}  cost=${cost(u):.5f}")
    return usages


def main() -> int:
    banner("Lab 05 - Context management")
    client = get_client()

    print("Part A: count tokens before you send")
    system = [{"type": "text", "text": INSTRUCTIONS}, {"type": "text", "text": f"<handbook>\n{HANDBOOK}\n</handbook>"}]
    handbook_tokens = count(client, MODEL, system, [{"role": "user", "content": "hello"}])
    history_tokens = count(client, MODEL, INSTRUCTIONS, CONVERSATION)
    print(f"  system prompt + handbook     : {handbook_tokens} tokens")
    print(f"  14-message conversation      : {history_tokens} tokens (budget {HISTORY_BUDGET_TOKENS})")
    over_budget = history_tokens > HISTORY_BUDGET_TOKENS
    print(f"  over budget?                 : {over_budget}\n")

    print("Part B: compact older turns, keep recent turns verbatim")
    compacted = compact(client, CONVERSATION) if over_budget else CONVERSATION
    compacted_tokens = count(client, MODEL, INSTRUCTIONS, compacted)
    print(f"  messages: {len(CONVERSATION)} -> {len(compacted)}; tokens: {history_tokens} -> {compacted_tokens}")
    print(f"  summary : {compacted[0]['content'].splitlines()[1][:160]}...")
    follow_up = client.messages.create(
        model=MODEL, max_tokens=2048, output_config={"effort": "low"}, system=INSTRUCTIONS,
        messages=compacted + [{"role": "user", "content": "So what happens next with my application and the term change?"}],
    )
    print(f"  follow-up answer using the compacted history: {text_of(follow_up)}\n")

    print("Part C: prompt caching layouts (3 requests each)")
    _MOCK_CACHE.clear()
    bad = run_layout(client, "bad")
    good = run_layout(client, "good")
    bad_cost, good_cost = sum(map(cost, bad)), sum(map(cost, good))
    print(f"  total cost  bad=${bad_cost:.5f}  good=${good_cost:.5f}  saving={100 * (1 - good_cost / bad_cost):.0f}%")
    print("  (prices: claude-opus-5-5 as of 2026-10-24; mock token counts are estimates)\n")

    print("Self-checks")
    summary_text = compacted[0]["content"]
    checks = {
        "conversation exceeded the budget and was compacted": over_budget and len(compacted) < len(CONVERSATION),
        "compacted history fits the budget": compacted_tokens <= HISTORY_BUDGET_TOKENS,
        "recent turns kept verbatim": compacted[-KEEP_RECENT_MESSAGES:] == CONVERSATION[-KEEP_RECENT_MESSAGES:],
        "summary preserves every key fact": all(f.lower() in summary_text.lower() for f in KEY_FACTS),
        "history still starts with a user turn": compacted[0]["role"] == "user",
        "bad layout never reads from cache": all(u.cache_read_input_tokens == 0 for u in bad),
        "good layout writes once, then reads": good[0].cache_creation_input_tokens > 0
        and all(u.cache_read_input_tokens > 0 for u in good[1:]),
        "good layout is cheaper overall": good_cost < bad_cost,
    }
    live_advisory = {"summary preserves every key fact", "compacted history fits the budget",
                     "good layout writes once, then reads", "good layout is cheaper overall"}
    failed = False
    for name, ok in checks.items():
        if ok:
            print(f"  [PASS] {name}")
        elif MODE == "live" and name in live_advisory:
            print(f"  [WARN] {name} (live behaviour varies; see Troubleshooting)")
        else:
            print(f"  [FAIL] {name}")
            failed = True
    if failed:
        return 1
    print("\nAll checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
