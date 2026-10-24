"""Command-line entry point.

    cd src && python -m docsummary                       # sample document, all audiences
    cd src && python -m docsummary --file ../data/vendor-change-memo.md --audience compliance --json

Non-interactive. Exits 0 on success, 2 if --strict is set and the faithfulness score is below 1.0,
and 1 if the model output could not be used.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from claude_lab import MODE, banner, get_client

from . import DATA_DIR
from . import mock  # noqa: F401  (registers the offline responder)
from .llm import ModelOutputError
from .pipeline import summarise
from .render import render_markdown
from .schemas import AUDIENCES

MAX_INPUT_BYTES = 2_000_000


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="docsummary", description=__doc__.splitlines()[0])
    parser.add_argument("--file", type=Path, default=DATA_DIR / "q3-operations-review.md")
    parser.add_argument("--audience", choices=(*AUDIENCES, "all"), default="all")
    parser.add_argument("--chunk-chars", type=int, default=3500)
    parser.add_argument("--json", action="store_true", help="print the validated JSON instead of Markdown")
    parser.add_argument("--strict", action="store_true", help="exit 2 if any claim is unsupported")
    args = parser.parse_args(argv)

    path = args.file.resolve()
    if not path.is_file() or path.stat().st_size > MAX_INPUT_BYTES:
        print(f"error: {path} is missing or larger than {MAX_INPUT_BYTES} bytes", file=sys.stderr)
        return 1
    text = path.read_text(encoding="utf-8")
    title = next((ln.lstrip("# ").strip() for ln in text.splitlines() if ln.startswith("#")), path.stem)

    banner("Project 01: document summarisation assistant")
    if MODE == "live":
        print("> Cost: live mode uses API credits.\n")
    client = get_client()
    audiences = AUDIENCES if args.audience == "all" else (args.audience,)
    exit_code = 0
    for audience in audiences:
        try:
            result = summarise(text, client=client, title=title, audience=audience, chunk_chars=args.chunk_chars)
        except ModelOutputError as exc:
            print(f"error ({audience}): {exc}", file=sys.stderr)
            return 1
        print(f"--- {audience} | mode={result.mode} chunks={result.chunks} calls={result.tally.calls} "
              f"faithfulness={result.report.score:.2f} est_cost=${result.tally.estimated_cost_usd():.4f}")
        for w in result.warnings:
            print(f"warning: {w}")
        print(json.dumps(result.summary, indent=2) if args.json else render_markdown(result.summary))
        if args.strict and not result.report.passed(1.0):
            exit_code = 2
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
