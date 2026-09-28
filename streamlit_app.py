import logging
import os
from pathlib import Path

import streamlit as st
from openai import APIError, OpenAI

from chat_logic import (
    EMPTY_RESPONSE_MESSAGE,
    GENERIC_ERROR_MESSAGE,
    UPLOAD_TYPES,
    UploadError,
    append_message,
    build_api_messages,
    display_text,
    drop_last_message,
    friendly_error,
    load_system_prompt,
    should_keep_turn,
    upload_to_turn,
)

MODEL = "gpt-4o-mini"
MAX_HISTORY_TURNS = 20
# A full review carries three tables and seven sections; 1024 cut it mid-table.
MAX_COMPLETION_TOKENS = 4096
SYSTEM_PROMPT_PATH = Path(__file__).parent / "prompts" / "schedule_review.md"

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


@st.cache_resource
def get_system_prompt():
    return load_system_prompt(SYSTEM_PROMPT_PATH)


def complete_turn(client, system_prompt):
    """Stream one assistant reply for the history already in session state.

    The caller has committed the user turn before this runs, so a mid-stream
    rerun neither drops the question nor duplicates it. Only a completed reply
    is committed; a failed stream leaves the user turn in place for a retry.
    """
    try:
        stream = client.chat.completions.create(
            model=MODEL,
            messages=build_api_messages(
                st.session_state.messages, system_prompt, MAX_HISTORY_TURNS
            ),
            max_tokens=MAX_COMPLETION_TOKENS,
            stream=True,
        )
        with st.chat_message("assistant"):
            response = st.write_stream(stream)
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


st.title("📋 PrimeOps Schedule Review")
st.caption(
    "Upload the schedule you already made, answer a few preset questions about "
    "each person, and get findings, a proposed fix and feedback. Not a payroll "
    "tool: no pay, hours worked or timeclock data is read. People are named by "
    "first name and last initial only."
)

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
system_prompt = get_system_prompt()

if "messages" not in st.session_state:
    st.session_state.messages = []
if "sent_upload" not in st.session_state:
    st.session_state.sent_upload = None

with st.sidebar:
    st.subheader("Schedule")
    upload = st.file_uploader(
        "Upload this period's schedule",
        type=list(UPLOAD_TYPES),
        help=(
            "CSV, TSV, TXT, XLSX, or a PNG/JPG/WEBP photo or screenshot. The "
            "file goes to OpenAI for the review and is not stored by this app. "
            "Only the file name appears in the transcript."
        ),
    )
    st.caption("Or paste the schedule as text in the chat.")
    if st.button("Clear conversation", use_container_width=True):
        st.session_state.messages = []
        st.session_state.sent_upload = None
        st.rerun()

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(display_text(message))

# An upload is sent once, as its own user turn, the first time it appears.
# The uploader keeps returning the same file on every rerun, so the turn is
# keyed on name and size to stop it being re-sent after each chat message.
if upload is not None:
    upload_key = (upload.name, upload.size)
    if upload_key != st.session_state.sent_upload:
        try:
            content, display = upload_to_turn(upload.name, upload.getvalue())
        except UploadError as exc:
            st.error(str(exc), icon="📎")
        else:
            st.session_state.sent_upload = upload_key
            append_message(st.session_state.messages, "user", content, display=display)
            with st.chat_message("user"):
                st.markdown(display)
            complete_turn(client, system_prompt)

# chat_input does not trim, so a space-only submission arrives as a truthy
# string that append_message rejects. Normalising here keeps that rejection
# from surfacing as a traceback on the one call outside the try below.
prompt = (st.chat_input("Paste a schedule, or answer the questions") or "").strip()
if prompt:
    append_message(st.session_state.messages, "user", prompt)
    with st.chat_message("user"):
        st.markdown(prompt)
    complete_turn(client, system_prompt)
