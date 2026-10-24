"""Make the shared lab helper importable (19-hands-on-labs/common/claude_lab.py)."""
from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]
PROJECT_ROOT = Path(__file__).resolve().parents[2]
_COMMON = REPO_ROOT / "19-hands-on-labs" / "common"
if str(_COMMON) not in sys.path:
    sys.path.insert(0, str(_COMMON))

import claude_lab  # noqa: E402  (import after the path insert is intentional)

__all__ = ["claude_lab", "REPO_ROOT", "PROJECT_ROOT"]
