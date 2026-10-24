"""Lab 02: improve a prompt step by step and measure each change with a rubric.

Four prompt versions (data/prompt_versions.json) write the same customer email from the
same synthetic delivery tickets (data/tickets.json). A deterministic, code-graded rubric
scores every output, so you can see which change moved which criterion.

Run offline (default):   CLAUDE_LAB_MODE=mock python lab.py
Run against the API:      CLAUDE_LAB_MODE=live python lab.py   (uses API credits)
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from string import Template

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "common"))
from claude_lab import get_client, MODEL, register_mock, text_of, banner  # noqa: E402
from claude_lab import MODE  # noqa: E402

DATA = Path(__file__).resolve().parent / "data"
TICKETS = json.loads((DATA / "tickets.json").read_text(encoding="utf-8"))
VERSIONS = json.loads((DATA / "prompt_versions.json").read_text(encoding="utf-8"))
MAX_WORDS = 120


# --------------------------------------------------------------------------- rubric
def ticket_text(ticket: dict) -> str:
    """Render the ticket as plain labelled lines (the data the prompt wraps)."""
    return "\n".join(
        [
            f"Customer name: {ticket['customer_name']}",
            f"Order ID: {ticket['order_id']}",
            f"Original delivery date: {ticket['original_date']}",
            f"New delivery date: {ticket['new_date']}",
            f"Support contact: {ticket['support_contact']}",
            f"Internal note: {ticket['internal_note']}",
        ]
    )


INTERNAL_CODE = re.compile(r"\b(?:EXC-\d+|[A-Z]{3}-\d)\b|\bVan \d+\b")


def score(email: str, ticket: dict) -> dict[str, bool]:
    """Seven yes/no criteria. Each one is cheap to check in code and maps to a requirement."""
    first_name = ticket["customer_name"].split()[0]
    lowered = email.lower()
    leaks = INTERNAL_CODE.findall(email) + [n for n in ticket["internal_names"] if n in email]
    return {
        "greets customer by name": first_name in email,
        "apologises": "sorry" in lowered or "apolog" in lowered,
        "states the new date": ticket["new_date"] in email,
        "gives a way to get help": ticket["support_contact"] in email,
        "no internal codes or staff names": not leaks,
        f"at most {MAX_WORDS} words": len(email.split()) <= MAX_WORDS,
        "uses the subject-line format": email.startswith(f"Subject: Update on your order {ticket['order_id']}"),
    }


# --------------------------------------------------------------------------- mock responses
def _prompt_level(request: dict) -> int:
    """Infer which prompt techniques are present, so the fake output improves realistically."""
    system = request.get("system") or ""
    user = request["messages"][-1]["content"]
    return 1 + ("Audience:" in system) + ("<ticket>" in user) + ("<example>" in user)


@register_mock
def fake_email_writer(**request):
    user = request["messages"][-1]["content"]
    if not isinstance(user, str) or "Order ID:" not in user:
        return None
    ticket = next(t for t in TICKETS if t["order_id"] in user)
    first = ticket["customer_name"].split()[0]
    level = _prompt_level(request)
    if level == 1:  # vague prompt: internal jargon leaks, no date, rambling
        return (
            f"Delivery update for order {ticket['order_id']}.\n\n"
            f"Exception {ticket['internal_note'].split(':')[0].split()[0]} was raised. "
            f"{ticket['internal_note']} The operations team has reviewed the situation and the "
            "parcel has been placed back into the network for onward processing. Depending on "
            "route capacity and any further exceptions, delivery should take place in the coming "
            "days. Further updates will be issued through the usual channels as and when the "
            "status changes in the tracking system. We appreciate everyone's patience while the "
            "depot works through the backlog created by the incident and thank all staff "
            "involved for their efforts in resolving the issue as quickly as possible."
        )
    if level == 2:  # role and audience fix the tone, but internal detail still leaks
        return (
            f"Hi {first},\n\nWe're sorry your parcel is late. Because of an issue logged as "
            f"{INTERNAL_CODE.findall(ticket['internal_note'])[0]} at our depot, your order "
            f"{ticket['order_id']} will now arrive on {ticket['new_date']}. If you need help, "
            f"contact {ticket['support_contact']}.\n\nAcme Logistics"
        )
    if level == 3:  # constraints met, but the format varies from email to email
        return (
            f"Dear {first},\n\nWe apologise for the delay to order {ticket['order_id']}. A problem "
            f"on the original route means your parcel will now arrive on {ticket['new_date']}. "
            f"You don't need to do anything. For help, email {ticket['support_contact']}.\n\n"
            "Kind regards,\nAcme Logistics"
        )
    return (
        f"Subject: Update on your order {ticket['order_id']}\n\nHi {first},\n\n"
        f"We're sorry: your parcel will now arrive on {ticket['new_date']} instead of "
        f"{ticket['original_date']} because of a problem on the original delivery route. "
        f"You don't need to do anything. If you have questions, email {ticket['support_contact']} "
        "and quote your order number.\n\nAcme Logistics Customer Care"
    )


# --------------------------------------------------------------------------- lab code
def run_version(client, version: dict, ticket: dict) -> str:
    kwargs = {
        "model": MODEL,
        "max_tokens": 4096,
        "output_config": {"effort": "low"},  # short drafting task
        "messages": [{"role": "user", "content": Template(version["user"]).substitute(ticket_text=ticket_text(ticket))}],
    }
    if version["system"]:
        kwargs["system"] = version["system"]
    response = client.messages.create(**kwargs)
    if response.stop_reason != "end_turn":
        raise RuntimeError(f"{version['version']}: unexpected stop_reason {response.stop_reason}")
    return text_of(response).strip()


def main() -> int:
    banner("Lab 02 - Prompt improvement with a rubric")
    client = get_client()
    totals: list[tuple[str, int, int]] = []
    per_criterion: dict[str, list[int]] = {}

    for version in VERSIONS:
        print(f"--- {version['version']}: {version['change']}")
        version_score, version_max = 0, 0
        for ticket in TICKETS:
            email = run_version(client, version, ticket)
            result = score(email, ticket)
            version_score += sum(result.values())
            version_max += len(result)
            for name, ok in result.items():
                per_criterion.setdefault(name, []).append(int(ok))
            missed = [name for name, ok in result.items() if not ok]
            print(f"  {ticket['ticket_id']}: {sum(result.values())}/{len(result)}"
                  + (f"  missed: {', '.join(missed)}" if missed else ""))
            if ticket is TICKETS[0]:
                preview = email.replace("\n", " ")
                print(f"    preview: {preview[:150]}{'...' if len(preview) > 150 else ''}")
        totals.append((version["version"], version_score, version_max))
        print()

    print("Score by version")
    print(f"  {'version':<30} {'score':>7}  bar")
    for name, got, out_of in totals:
        print(f"  {name:<30} {got:>3}/{out_of:<3}  {'#' * got}")

    print("\nSelf-checks")
    scores = [got for _, got, _ in totals]
    checks = {
        "rubric is deterministic (same email, same score)": score("Hi Priya", TICKETS[0]) == score("Hi Priya", TICKETS[0]),
        "rubric catches a leaked internal code": not score("EXC-4471 Hi Priya", TICKETS[0])["no internal codes or staff names"],
        "rubric catches a leaked staff name": not score("Tomas says hi", TICKETS[0])["no internal codes or staff names"],
        "every version was scored on every ticket": all(len(v) == len(VERSIONS) * len(TICKETS) for v in per_criterion.values()),
        "final version beats the baseline": scores[-1] > scores[0],
        "no version scored lower than the one before": all(b >= a for a, b in zip(scores, scores[1:])),
        "final version meets every criterion": scores[-1] == totals[-1][2],
    }
    quality_checks = {"final version beats the baseline", "no version scored lower than the one before",
                      "final version meets every criterion"}
    failed = False
    for name, ok in checks.items():
        if ok:
            print(f"  [PASS] {name}")
        elif MODE == "live" and name in quality_checks:
            print(f"  [WARN] {name} (live outputs vary; inspect the missed criteria above)")
        else:
            print(f"  [FAIL] {name}")
            failed = True
    if failed:
        return 1
    print("\nAll checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
