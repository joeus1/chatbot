"""Bounds on what one public session can send: pasted length, turn count, and
the server-side upload ceiling.

The pure checks are tested directly; the wiring in `streamlit_app.py` is
tested with Streamlit's AppTest and a fake OpenAI client, so nothing here
touches the network.
"""

import tomllib
from pathlib import Path
from types import SimpleNamespace

import openai
import pytest
import streamlit as st
from streamlit.testing.v1 import AppTest

import chat_logic
from chat_logic import (
    MAX_CHAT_MESSAGE_CHARS,
    MAX_UPLOAD_IMAGE_BYTES,
    MAX_USER_TURNS_PER_SESSION,
    MESSAGE_TOO_LONG_MESSAGE,
    SESSION_TURN_LIMIT_MESSAGE,
    MessageError,
    check_chat_message,
    session_turn_limit_reached,
)

ROOT = Path(__file__).resolve().parent.parent
APP = str(ROOT / "streamlit_app.py")


def history(user_turns):
    out = []
    for i in range(user_turns):
        out.append({"role": "user", "content": f"q{i}"})
        out.append({"role": "assistant", "content": f"a{i}"})
    return out


# --- pasted message length -------------------------------------------------


def test_message_at_the_limit_is_accepted():
    check_chat_message("x" * MAX_CHAT_MESSAGE_CHARS)


def test_message_over_the_limit_is_refused_with_its_copy():
    with pytest.raises(MessageError) as exc:
        check_chat_message("x" * (MAX_CHAT_MESSAGE_CHARS + 1))
    assert str(exc.value) == MESSAGE_TOO_LONG_MESSAGE
    assert f"{MAX_CHAT_MESSAGE_CHARS:,}" in MESSAGE_TOO_LONG_MESSAGE


def test_chat_and_upload_text_bounds_stay_equal():
    # A schedule that fits as an upload must fit pasted, and the reverse.
    assert MAX_CHAT_MESSAGE_CHARS == chat_logic.MAX_UPLOAD_TEXT_CHARS


# --- session turn cap ------------------------------------------------------


def test_limit_not_reached_one_turn_short():
    assert not session_turn_limit_reached(history(MAX_USER_TURNS_PER_SESSION - 1))


def test_limit_reached_at_the_cap():
    assert session_turn_limit_reached(history(MAX_USER_TURNS_PER_SESSION))


def test_only_user_turns_count():
    # A trailing assistant reply must not tip a session over its budget.
    assert not session_turn_limit_reached(history(2) + [{"role": "assistant", "content": "x"}], limit=3)


def test_dropped_turn_frees_its_slot():
    full = history(MAX_USER_TURNS_PER_SESSION)
    assert chat_logic.drop_last_message(full, "assistant")
    assert chat_logic.drop_last_message(full, "user")
    assert not session_turn_limit_reached(full)


def test_upload_turns_count_as_user_turns():
    parts = [{"type": "text", "text": "sheet"}]
    turns = []
    chat_logic.append_message(turns, "user", parts, display="Uploaded schedule: `a.csv`")
    assert session_turn_limit_reached(turns, limit=1)


# --- server-side upload ceiling --------------------------------------------


def test_config_caps_upload_size_at_the_largest_accepted_file():
    config = tomllib.loads((ROOT / ".streamlit" / "config.toml").read_text())
    server = config["server"]
    assert server["maxUploadSize"] * 1024 * 1024 == MAX_UPLOAD_IMAGE_BYTES
    # Room for the biggest legitimate paste (4 bytes per character), with slack.
    assert server["maxMessageSize"] * 1024 * 1024 > 4 * MAX_CHAT_MESSAGE_CHARS


def test_config_is_not_gitignored():
    ignored = (ROOT / ".gitignore").read_text().splitlines()
    assert ".streamlit/config.toml" not in ignored
    assert ".streamlit/" not in ignored


# --- app wiring ------------------------------------------------------------


@pytest.fixture
def fake_openai(monkeypatch):
    calls = []

    class FakeClient:
        def __init__(self, *args, **kwargs):
            self.chat = SimpleNamespace(completions=SimpleNamespace(create=self._create))

        @staticmethod
        def _create(**kwargs):
            calls.append(kwargs)
            return iter(["ok"])

    monkeypatch.setattr(openai, "OpenAI", FakeClient)
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test-not-real")
    st.cache_resource.clear()
    yield calls
    st.cache_resource.clear()


def new_app():
    at = AppTest.from_file(APP, default_timeout=30)
    at.run()
    assert not at.exception
    return at


def test_overlong_paste_is_refused_and_never_sent(fake_openai):
    at = new_app()
    at.chat_input[0].set_value("x" * (MAX_CHAT_MESSAGE_CHARS + 1)).run()
    assert not at.exception
    assert [e.value for e in at.error] == [MESSAGE_TOO_LONG_MESSAGE]
    assert at.session_state.messages == []
    assert fake_openai == []


def test_paste_at_the_limit_is_sent(fake_openai):
    at = new_app()
    at.chat_input[0].set_value("x" * MAX_CHAT_MESSAGE_CHARS).run()
    assert not at.exception
    assert not at.error
    assert len(fake_openai) == 1
    assert [m["role"] for m in at.session_state.messages] == ["user", "assistant"]


def test_chat_box_advertises_the_length_limit(fake_openai):
    at = new_app()
    assert at.chat_input[0].max_chars == MAX_CHAT_MESSAGE_CHARS


def test_session_at_its_turn_limit_disables_chat_and_warns(fake_openai):
    at = new_app()
    at.session_state.messages = history(MAX_USER_TURNS_PER_SESSION)
    at.run()
    assert not at.exception
    assert at.chat_input[0].disabled
    assert [w.value for w in at.warning] == [SESSION_TURN_LIMIT_MESSAGE]


def test_session_one_turn_short_still_accepts_a_message(fake_openai):
    at = new_app()
    at.session_state.messages = history(MAX_USER_TURNS_PER_SESSION - 1)
    at.run()
    assert not at.chat_input[0].disabled
    assert not at.warning
    at.chat_input[0].set_value("last one").run()
    assert len(fake_openai) == 1
    # That message used the last slot, so the box is now locked.
    assert at.chat_input[0].disabled
    assert [w.value for w in at.warning] == [SESSION_TURN_LIMIT_MESSAGE]


def test_clear_conversation_restores_the_budget(fake_openai):
    at = new_app()
    at.session_state.messages = history(MAX_USER_TURNS_PER_SESSION)
    at.run()
    assert at.chat_input[0].disabled
    at.sidebar.button[0].click().run()
    assert not at.exception
    assert not at.chat_input[0].disabled
    assert not at.warning
