"""Convenience launcher: `python run.py [options]` == `python -m investigator` with src/ on the path."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from investigator.__main__ import main  # noqa: E402

if __name__ == "__main__":
    sys.exit(main())
