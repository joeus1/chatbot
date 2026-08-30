"""Pure chat logic for the Streamlit app.

Everything here is importable without Streamlit so it can be unit-tested
with no network and no UI. The app (`streamlit_app.py`) owns presentation
and session state; this module owns message shaping and error mapping.
"""

from openai import (
    APIConnectionError,
    AuthenticationError,
    BadRequestError,
    RateLimitError,
    UnprocessableEntityError,
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
NON_RETRYABLE_MESSAGE = (
    "OpenAI could not process that message, so it was removed from the "
    "conversation. Try a shorter or rephrased version - and use Clear "
    "conversation if it keeps happening, since a long history can cause "
    "this too."
)
EMPTY_RESPONSE_MESSAGE = (
    "The assistant returned an empty reply. Nothing failed - ask again or "
    "rephrase if you were expecting an answer."
)


def append_message(history, role, content):
    """Append a validated chat turn to `history` in place."""
    if role not in ("user", "assistant"):
        raise ValueError(f"unsupported role: {role!r}")
    if not isinstance(content, str) or not content.strip():
        raise ValueError("message content must be a non-empty string")
    history.append({"role": role, "content": content})


def drop_last_message(history, role):
    """Remove the final turn in place if it has `role`.

    Returns True when a turn was removed, so callers can tell the difference
    between undoing their own append and finding nothing to undo.
    """
    if history and history[-1]["role"] == role:
        history.pop()
        return True
    return False


def should_keep_turn(exc):
    """Whether the user's turn should stay in history after `exc`.

    Auth, rate-limit, connection and server errors are all worth retrying with
    the same message unchanged, so the turn stays and the user can resend once
    the key, the quota or the network is fixed.

    A 400 or 422 is caused by the request content itself - an over-long context
    or rejected content. Keeping that turn would make every later message fail
    identically, and the bounded window can never evict it, so the chat wedges
    until the whole conversation is cleared.
    """
    return not isinstance(exc, (BadRequestError, UnprocessableEntityError))


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
    # Checked after the config-caused errors above, which keep their own copy.
    if not should_keep_turn(exc):
        return NON_RETRYABLE_MESSAGE
    return GENERIC_ERROR_MESSAGE
