"""Document summarisation assistant (project 01).

Summarises long synthetic business documents with a map-reduce pipeline, audience-specific
formats, structured output and faithfulness checks. Runs offline in mock mode by default.
"""
from __future__ import annotations

import sys
from pathlib import Path


def _add_lab_helper_to_path() -> None:
    """Make `claude_lab` (19-hands-on-labs/common) importable without installing anything."""
    for parent in Path(__file__).resolve().parents:
        candidate = parent / "19-hands-on-labs" / "common"
        if (candidate / "claude_lab.py").is_file():
            if str(candidate) not in sys.path:
                sys.path.insert(0, str(candidate))
            return
    raise ImportError("could not find 19-hands-on-labs/common/claude_lab.py above this package")


_add_lab_helper_to_path()

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data"
