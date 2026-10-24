#!/usr/bin/env python3
"""Run every lab entry point in mock mode and fail if any exits non-zero or takes too long.

  python tools/run_lab_smoke.py            # all labs
  python tools/run_lab_smoke.py lab-08     # labs whose folder name contains "lab-08"
"""
from __future__ import annotations

import os
import subprocess
import sys
import time

from common import LABS_DIR, ROOT, Report

TIMEOUT = 60


def main(filters: list[str]) -> int:
    report = Report("lab smoke tests (mock mode)")
    env = {**os.environ, "CLAUDE_LAB_MODE": "mock", "PYTHONDONTWRITEBYTECODE": "1"}
    env.pop("ANTHROPIC_API_KEY", None)  # guarantee no live calls
    labs = sorted(p for p in LABS_DIR.glob("lab-*/lab.py") if not filters or any(f in p.parent.name for f in filters))
    if not labs:
        report.error("no labs found")
    for lab in labs:
        start = time.monotonic()
        try:
            proc = subprocess.run([sys.executable, str(lab)], cwd=lab.parent, env=env, capture_output=True,
                                  text=True, timeout=TIMEOUT, stdin=subprocess.DEVNULL)
        except subprocess.TimeoutExpired:
            report.error(f"{lab.parent.name}: timed out after {TIMEOUT}s")
            continue
        took = time.monotonic() - start
        if proc.returncode != 0:
            tail = (proc.stderr or proc.stdout).strip().splitlines()[-8:]
            report.error(f"{lab.parent.name}: exit {proc.returncode}\n      " + "\n      ".join(tail))
        else:
            print(f"  ok   {lab.parent.name} ({took:.1f}s)")
    missing = [p.name for p in LABS_DIR.glob("lab-*") if p.is_dir() and not (p / "lab.py").exists()]
    for name in missing:
        report.error(f"{name}: no lab.py entry point")
    report.print()
    return 0 if report.ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
