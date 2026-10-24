#!/usr/bin/env python3
"""Launcher: python 18-mock-examinations/run_mock_exam.py [options]  (see --help)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "engine"))

from mockexam.cli import main  # noqa: E402

if __name__ == "__main__":
    sys.exit(main())
