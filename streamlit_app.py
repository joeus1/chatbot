import logging
import os

import streamlit as st
from openai import APIError, OpenAI

from chat_logic import (
    EMPTY_RESPONSE_MESSAGE,
    GENERIC_ERROR_MESSAGE,
    append_message,
    build_api_messages,
    drop_last_message,
    friendly_error,
    should_keep_turn,
)

MODEL = "gpt-4o-mini"
MAX_HISTORY_TURNS = 20
MAX_COMPLETION_TOKENS = 1024
SYSTEM_PROMPT = (
    "You are a helpful, concise assistant. Answer plainly and say so when "
    "you are unsure."
)

logger = logging.getLogger(__name__)


def get_api_key():
    """Read the API key from Streamlit secrets, falling back to the environment.

    Accessing `st.secrets` raises when no secrets file exists at all, so the
    lookup is wrapped rather than assumed.
    """
    try:
        key = st.secrets.get("OPENAI_API_KEY", "")
    # Broad on purpose. A missing file raises StreamlitSecretNotFoundError, but
    # an unreadable or malformed secrets.toml raises something else again, and
    # every one of those cases should fall through to the environment rather
    # than replace the page with a traceback. If neither source has a key the
    # app already says so, with instructions.
    except Exception:  # noqa: BLE001
        key = ""
    return key or os.environ.get("OPENAI_API_KEY", "")


@st.cache_resource
def get_client(api_key):
    return OpenAI(api_key=api_key)


st.title("💬 Chatbot")
st.caption("A chat assistant powered by the OpenAI API.")

api_key = get_api_key()
if not api_key:
    st.error(
        "No OpenAI API key is configured. Add `OPENAI_API_KEY` to "
        "`.streamlit/secrets.toml` (see `.streamlit/secrets.toml.example`) "
        "or set it as an environment variable, then reload.",
        icon="🗝️",
    )
    st.stop()

client = get_client(api_key)

if "messages" not in st.session_state:
    st.session_state.messages = []

with st.sidebar:
    if st.button("Clear conversation", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# chat_input does not trim, so a space-only submission arrives as a truthy
# string that append_message rejects. Normalising here keeps that rejection
# from surfacing as a traceback on the one call outside the try below.
prompt = (st.chat_input("Ask anything") or "").strip()
if prompt:
    # The user turn is committed to state before the API call so a mid-stream
    # rerun neither drops the question nor duplicates it.
    append_message(st.session_state.messages, "user", prompt)
    with st.chat_message("user"):
        st.markdown(prompt)

    try:
        stream = client.chat.completions.create(
            model=MODEL,
            messages=build_api_messages(
                st.session_state.messages, SYSTEM_PROMPT, MAX_HISTORY_TURNS
            ),
            max_tokens=MAX_COMPLETION_TOKENS,
            stream=True,
        )
        with st.chat_message("assistant"):
            response = st.write_stream(stream)
        # Only a completed reply is committed; a failed stream leaves the
        # user turn in place for a clean retry.
        if isinstance(response, str) and response.strip():
            append_message(st.session_state.messages, "assistant", response)
        elif isinstance(response, str):
            # The call succeeded and streamed nothing. That is not a failure,
            # and calling it one invites a retry of an already-billed request.
            st.info(EMPTY_RESPONSE_MESSAGE, icon="💬")
        else:
            st.error(GENERIC_ERROR_MESSAGE, icon="⚠️")
    except APIError as exc:
        logger.warning("OpenAI API call failed: %s", type(exc).__name__)
        # A turn the API will reject every time has to come back out, or the
        # bounded window can never evict it and the chat stays wedged. It is
        # still on screen for this run; the next rerun renders without it.
        if not should_keep_turn(exc):
            drop_last_message(st.session_state.messages, "user")
        st.error(friendly_error(exc), icon="⚠️")
    except Exception:
        logger.exception("Unexpected failure during completion")
        st.error(GENERIC_ERROR_MESSAGE, icon="⚠️")
