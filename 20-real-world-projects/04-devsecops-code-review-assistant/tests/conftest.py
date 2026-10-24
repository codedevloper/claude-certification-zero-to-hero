"""Test setup: offline mock mode and import paths for src/ and the shared lab helper."""
import os
import sys
from pathlib import Path

os.environ.setdefault("CLAUDE_LAB_MODE", "mock")

PROJECT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT / "src"))
sys.path.insert(0, str(PROJECT.parents[1] / "19-hands-on-labs" / "common"))

import pytest  # noqa: E402


@pytest.fixture
def sample_diff() -> str:
    return (PROJECT / "data" / "sample.diff").read_text(encoding="utf-8")


@pytest.fixture
def clean_diff() -> str:
    return (PROJECT / "data" / "clean.diff").read_text(encoding="utf-8")
