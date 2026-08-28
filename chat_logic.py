"""Pure chat logic for the Streamlit app.

Everything here is importable without Streamlit so it can be unit-tested
with no network and no UI. The app (`streamlit_app.py`) owns presentation
and session state; this module owns message shaping and error mapping.
"""

from openai import (
    APIConnectionError,
    AuthenticationError,
    RateLimitError,
)

# User-facing copy for API failures. Raw exception text never reaches the
# page: it can contain request details and, for auth errors, hints about
# the key.
AUTH_ERROR_MESSAGE = (
    "OpenAI rejected the configured API key. "
    "Check OPENAI_API_KEY in your Streamlit secrets and try again."
)
RATE_LIMIT_MESSAGE = (
    "The assistant is receiving too many requests right now. "
    "Wait a moment and send your message again."
)
CONNECTION_ERROR_MESSAGE = (
    "Could not reach OpenAI. Check your network connection and try again."
)
GENERIC_ERROR_MESSAGE = (
    "Something went wrong while generating a response. "
    "Your message was kept; try sending it again."
)


def append_message(history, role, content):
    """Append a validated chat turn to `history` in place."""
    if role not in ("user", "assistant"):
        raise ValueError(f"unsupported role: {role!r}")
    if not isinstance(content, str) or not content.strip():
        raise ValueError("message content must be a non-empty string")
    history.append({"role": role, "content": content})


def build_api_messages(history, system_prompt, max_turns):
    """Return the payload sent to the API: system prompt + last `max_turns` turns.

    The full transcript stays in session state for display; only a bounded
    window goes to the API so long chats don't grow cost quadratically or
    overflow the context window.
    """
    if max_turns < 1:
        raise ValueError("max_turns must be at least 1")
    bounded = history[-max_turns:]
    return [{"role": "system", "content": system_prompt}] + [
        {"role": m["role"], "content": m["content"]} for m in bounded
    ]


def friendly_error(exc):
    """Map an OpenAI exception to a user-facing message.

    Never includes `str(exc)`; callers may log the exception server-side.
    """
    if isinstance(exc, AuthenticationError):
        return AUTH_ERROR_MESSAGE
    if isinstance(exc, RateLimitError):
        return RATE_LIMIT_MESSAGE
    # APITimeoutError subclasses APIConnectionError, so one branch covers both.
    if isinstance(exc, APIConnectionError):
        return CONNECTION_ERROR_MESSAGE
    return GENERIC_ERROR_MESSAGE
