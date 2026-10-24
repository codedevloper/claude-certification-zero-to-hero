"""Command-line entry point.

    cd src && python -m kbqa                                  # answer the demo questions
    cd src && python -m kbqa --question "How do I request VPN access?"
    cd src && python -m kbqa --eval --min-accuracy 0.8        # run the labelled evaluation set

Non-interactive. Exits 0 on success, 1 on unusable model output or a rejected question, and 2 when
--eval is used with a gate (--min-accuracy / --min-recall) that is not met.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from claude_lab import MODE, banner, get_client

from . import DATA_DIR
from . import mock  # noqa: F401  (registers the offline responder)
from .answer import answer_question
from .evaluate import load_eval_set, run_eval
from .kb import load_kb
from .llm import ModelOutputError, UsageTally
from .policy import QuestionRejected

DEMO_QUESTIONS = [
    "What is the hotel nightly limit in London?",
    "Which multi-factor authentication methods are allowed for the VPN?",
    "What should I do with my password to verify my account?",
    "Does the company offer pet insurance?",
]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="kbqa", description=__doc__.splitlines()[0])
    parser.add_argument("--question", action="append", help="question to answer (repeatable)")
    parser.add_argument("--kb-dir", default=str(DATA_DIR / "kb"))
    parser.add_argument("--k", type=int, default=4, help="chunks to retrieve")
    parser.add_argument("--eval", action="store_true", help="run data/eval_questions.json")
    parser.add_argument("--min-accuracy", type=float, default=0.0)
    parser.add_argument("--min-recall", type=float, default=0.0)
    args = parser.parse_args(argv)

    banner("Project 02: knowledge-base Q&A assistant")
    if MODE == "live":
        print("> Cost: live mode uses API credits.\n")
    kb = load_kb(Path(args.kb_dir))
    print(f"Indexed {len(kb.chunks)} chunks; quarantined {len(kb.quarantined)} chunk(s) for review:")
    for chunk, reason in kb.quarantined:
        print(f"  - {chunk.chunk_id} (pattern: {reason})")
    client = get_client()

    try:
        if args.eval:
            questions = load_eval_set(DATA_DIR / "eval_questions.json")
            result = run_eval(kb, client, questions, k=args.k)
            print(f"\n{'id':5} {'expect':8} {'status':9} {'hit':4} {'ok':4} reason")
            for r in result.rows:
                expect = "answer" if r["answerable"] else "refuse"
                ok = r["correct"] if r["answerable"] else r["status"] == "refused"
                print(f"{r['id']:5} {expect:8} {r['status']:9} {str(r['retrieval_hit'])[0]:4} {str(ok)[0]:4} {r['reason']}")
            metrics = result.metrics()
            print("\nMetrics:", ", ".join(f"{k}={v}" for k, v in metrics.items()))
            print(f"Model calls: {result.tally.calls}, estimated cost: ${result.tally.estimated_cost_usd():.4f}")
            if metrics["answer_accuracy"] < args.min_accuracy or metrics["recall_at_k"] < args.min_recall:
                print("Evaluation gate not met.", file=sys.stderr)
                return 2
            return 0

        tally = UsageTally()
        for question in args.question or DEMO_QUESTIONS:
            ans = answer_question(question, kb, client, k=args.k, tally=tally)
            print(f"\nQ: {ans.question}\nA: {ans.text}")
            if ans.status == "answered":
                print(f"   Sources: {', '.join(ans.citations)} (confidence {ans.confidence}, support {ans.support_ratio:.2f})")
            else:
                print(f"   Refused: {ans.reason}")
        print(f"\nModel calls: {tally.calls}, estimated cost: ${tally.estimated_cost_usd():.4f}")
        return 0
    except (ModelOutputError, QuestionRejected) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
