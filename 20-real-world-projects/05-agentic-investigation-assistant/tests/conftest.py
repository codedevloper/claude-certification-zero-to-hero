"""Test setup: offline mock mode and import paths for src/ and the shared lab helper."""
import os
import sys
from pathlib import Path

os.environ.setdefault("CLAUDE_LAB_MODE", "mock")

PROJECT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT / "src"))
sys.path.insert(0, str(PROJECT.parents[1] / "19-hands-on-labs" / "common"))

import pytest  # noqa: E402

DATA = PROJECT / "data"


@pytest.fixture
def make_ctx():
    from investigator.__main__ import build_context
    from investigator.approval import ApprovalGate
    from investigator.budget import Budget

    def _make(gate=None, budget=None, client=None):
        return build_context(DATA, DATA / "incident.json", gate or ApprovalGate("queue"), budget or Budget(),
                             client=client)
    return _make
