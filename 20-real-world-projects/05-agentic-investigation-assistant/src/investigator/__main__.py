"""Command line entry point.

    python run.py                                     # investigate data/incident.json (mock, offline)
    python run.py --approval-mode file --approvals data/approvals.example.json
    python run.py --report-out report.json --audit-out audit.jsonl
    python run.py --approval-mode interactive         # prompts for each containment action

Non-interactive by default: containment proposals are queued for a human, never executed.
Exit codes: 0 = report produced (complete or partial); 3 = bad input.
"""
from __future__ import annotations

import argparse
import json
import sys
import uuid
from pathlib import Path

from . import mock_llm  # noqa: F401  (registers the offline responder; harmless in live mode)
from ._lab import PROJECT_ROOT, claude_lab
from .agents import investigate
from .approval import ApprovalGate
from .audit import AuditLog
from .budget import Budget
from .logstore import LogStore
from .report import build_final, render_markdown
from .tools import Context


def build_context(data_dir: Path, incident_path: Path, gate: ApprovalGate, budget: Budget, client=None) -> Context:
    incident = json.loads(Path(incident_path).read_text(encoding="utf-8"))
    return Context(client=client or claude_lab.get_client(), incident=incident, store=LogStore(data_dir),
                   budget=budget, audit=AuditLog(run_id=f"run-{uuid.uuid4().hex[:12]}"), gate=gate)


def run(ctx: Context) -> dict:
    status = investigate(ctx)
    return build_final(ctx.incident, ctx.report, ctx.evidence, ctx.gate.decisions, ctx.budget, ctx.audit, status)


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="investigator", description="Agentic incident investigation (self-hosted loop).")
    p.add_argument("--data-dir", default=str(PROJECT_ROOT / "data"))
    p.add_argument("--incident", default=str(PROJECT_ROOT / "data" / "incident.json"))
    p.add_argument("--approval-mode", choices=["queue", "file", "interactive"], default="queue")
    p.add_argument("--approvals", help="JSON approval file for --approval-mode file")
    p.add_argument("--max-model-calls", type=int, default=30)
    p.add_argument("--max-tool-calls", type=int, default=60)
    p.add_argument("--max-tokens", type=int, default=250_000, help="run-wide input+output token budget")
    p.add_argument("--report-out", help="write the structured report (JSON) here")
    p.add_argument("--audit-out", help="write the hash-chained audit trace (JSONL) here")
    args = p.parse_args(argv)

    try:
        gate = ApprovalGate(args.approval_mode, Path(args.approvals) if args.approvals else None)
        budget = Budget(args.max_model_calls, args.max_tool_calls, args.max_tokens)
        claude_lab.banner("investigator: agentic investigation assistant")
        ctx = build_context(Path(args.data_dir), Path(args.incident), gate, budget)
    except (OSError, ValueError, KeyError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 3

    final = run(ctx)
    print(render_markdown(final))
    if args.report_out:
        Path(args.report_out).write_text(json.dumps(final, indent=2), encoding="utf-8")
        print(f"Structured report written to {args.report_out}")
    if args.audit_out:
        ctx.audit.write_jsonl(Path(args.audit_out))
        print(f"Audit trace written to {args.audit_out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
