"""The shared lab helper must stay offline in mock mode and mirror current API rules."""
import pytest

import claude_lab
from claude_lab import MockClient, ToolUseBlock, register_mock, text_of


def test_default_mode_is_mock():
    assert isinstance(claude_lab.get_client(), MockClient) or claude_lab.MODE == "live"


def test_mock_echo_and_usage():
    msg = MockClient().messages.create(model="m", max_tokens=10, messages=[{"role": "user", "content": "hi"}])
    assert msg.stop_reason == "end_turn"
    assert "hi" in text_of(msg)
    assert msg.usage.input_tokens > 0


@pytest.mark.parametrize("bad", [{"temperature": 0.2}, {"top_p": 0.9}, {"tool_choice": {"type": "any"}}])
def test_mock_rejects_unsupported_parameters(bad):
    with pytest.raises(ValueError):
        MockClient().messages.create(model="m", max_tokens=10, messages=[{"role": "user", "content": "x"}], **bad)


def test_mock_rejects_prefill():
    with pytest.raises(ValueError):
        MockClient().messages.create(model="m", max_tokens=10, messages=[
            {"role": "user", "content": "x"}, {"role": "assistant", "content": "{"}])


def test_registered_responder_and_tool_use():
    @register_mock
    def responder(**req):
        if req.get("tools"):
            return [ToolUseBlock(name="lookup", input={"q": "x"})]
        return None

    try:
        msg = MockClient().messages.create(model="m", max_tokens=10, tools=[{"name": "lookup"}],
                                           messages=[{"role": "user", "content": "x"}])
        assert msg.stop_reason == "tool_use"
        assert msg.content[0].name == "lookup"
    finally:
        claude_lab._responders.remove(responder)
