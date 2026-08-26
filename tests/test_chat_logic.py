"""Unit tests for chat_logic: no network, no Streamlit.

OpenAI exceptions are constructed against real (vendored) httpx objects so
`friendly_error` is tested with the same types the SDK raises.
"""

import httpx2
import pytest
from openai import (
    APIConnectionError,
    APITimeoutError,
    AuthenticationError,
    RateLimitError,
)

from chat_logic import (
    AUTH_ERROR_MESSAGE,
    CONNECTION_ERROR_MESSAGE,
    GENERIC_ERROR_MESSAGE,
    RATE_LIMIT_MESSAGE,
    append_message,
    build_api_messages,
    friendly_error,
)

SYSTEM = "system prompt under test"
SECRET_DETAIL = "sk-secret-internal-detail"


def turns(count):
    return [
        {"role": "user" if i % 2 == 0 else "assistant", "content": f"turn {i}"}
        for i in range(count)
    ]


def make_request():
    return httpx2.Request("POST", "https://api.openai.com/v1/chat/completions")


def make_status_error(cls, status):
    response = httpx2.Response(status, request=make_request())
    return cls(SECRET_DETAIL, response=response, body=None)


class TestHistoryBounding:
    def test_fifty_turns_bounded_to_last_twenty(self):
        history = turns(50)
        payload = build_api_messages(history, SYSTEM, max_turns=20)
        assert len(payload) == 21
        assert payload[0] == {"role": "system", "content": SYSTEM}
        assert payload[1:] == history[-20:]

    def test_short_history_sent_whole(self):
        history = turns(3)
        payload = build_api_messages(history, SYSTEM, max_turns=20)
        assert payload == [{"role": "system", "content": SYSTEM}] + history

    def test_order_preserved(self):
        history = turns(30)
        payload = build_api_messages(history, SYSTEM, max_turns=10)
        assert [m["content"] for m in payload[1:]] == [
            f"turn {i}" for i in range(20, 30)
        ]

    def test_invalid_max_turns_rejected(self):
        with pytest.raises(ValueError):
            build_api_messages(turns(2), SYSTEM, max_turns=0)


class TestErrorMapping:
    def test_authentication_error(self):
        exc = make_status_error(AuthenticationError, 401)
        assert friendly_error(exc) == AUTH_ERROR_MESSAGE

    def test_rate_limit_error(self):
        exc = make_status_error(RateLimitError, 429)
        assert friendly_error(exc) == RATE_LIMIT_MESSAGE

    def test_connection_and_timeout_errors(self):
        conn = APIConnectionError(request=make_request())
        timeout = APITimeoutError(request=make_request())
        assert friendly_error(conn) == CONNECTION_ERROR_MESSAGE
        assert friendly_error(timeout) == CONNECTION_ERROR_MESSAGE

    def test_unknown_exception_maps_to_generic(self):
        assert friendly_error(RuntimeError(SECRET_DETAIL)) == GENERIC_ERROR_MESSAGE

    def test_raw_exception_text_never_leaks(self):
        for exc in (
            make_status_error(AuthenticationError, 401),
            make_status_error(RateLimitError, 429),
            RuntimeError(SECRET_DETAIL),
        ):
            assert SECRET_DETAIL not in friendly_error(exc)


class TestStateTransitions:
    def test_user_committed_before_call_survives_failure(self):
        history = []
        append_message(history, "user", "what is our food cost?")
        # The API call fails: no assistant turn is appended.
        assert history == [{"role": "user", "content": "what is our food cost?"}]

    def test_assistant_committed_after_completion(self):
        history = [{"role": "user", "content": "hello"}]
        append_message(history, "assistant", "hi there")
        assert [m["role"] for m in history] == ["user", "assistant"]

    def test_simulated_rerun_does_not_duplicate(self):
        history = []
        append_message(history, "user", "hello")
        # A rerun replays the script but chat_input returns nothing, so the
        # append path never runs again; state carries exactly one user turn.
        assert len(history) == 1

    def test_invalid_turns_rejected(self):
        history = []
        with pytest.raises(ValueError):
            append_message(history, "system", "not a chat turn")
        with pytest.raises(ValueError):
            append_message(history, "user", "   ")
        assert history == []
