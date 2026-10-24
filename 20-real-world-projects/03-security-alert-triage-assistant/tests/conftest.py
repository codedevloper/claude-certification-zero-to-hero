"""Test setup: force offline mock mode and make the package importable from src/."""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

os.environ["CLAUDE_LAB_MODE"] = "mock"  # tests must never reach the network

PROJECT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT / "src"))

import pytest  # noqa: E402

import alerttriage  # noqa: E402,F401  (adds 19-hands-on-labs/common to sys.path)
import alerttriage.mock  # noqa: E402,F401
import claude_lab  # noqa: E402


class ScriptedClient:
    """Fake client that returns queued replies, after applying claude_lab's request checks."""

    def __init__(self, replies, stop_reason="end_turn"):
        self.replies = list(replies)
        self.stop_reason = stop_reason
        self.requests = []
        self.messages = self

    def create(self, **request):
        claude_lab._validate_request(request)
        self.requests.append(request)
        reply = self.replies.pop(0)
        text = reply if isinstance(reply, str) else json.dumps(reply)
        return claude_lab.Message(content=[claude_lab.TextBlock(text)], model=request["model"], stop_reason=self.stop_reason)


@pytest.fixture
def data_dir() -> Path:
    return PROJECT / "data"


@pytest.fixture
def mock_client():
    return claude_lab.get_client()


@pytest.fixture
def scripted():
    return ScriptedClient


@pytest.fixture
def catalog():
    from alerttriage.triage import Catalog

    return Catalog.load(PROJECT / "data")


@pytest.fixture
def alerts():
    from alerttriage.alerts import load_alerts

    return {a.alert_id: a for a in load_alerts(PROJECT / "data" / "alerts")}


@pytest.fixture
def raw_alert():
    """A minimal valid raw alert that tests can modify."""
    return {
        "alert_id": "ALRT-9001",
        "rule_name": "Impossible travel between two successful sign-ins",
        "rule_severity": "high",
        "source": "identity-provider",
        "timestamp": "2026-10-24T00:00:00Z",
        "description": "Synthetic test alert.",
        "entities": {"hosts": ["WS-0001"], "users": ["j.tester"], "ips": ["192.0.2.55"], "domains": []},
        "evidence": {"note": "nothing unusual"},
    }
