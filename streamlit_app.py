import logging
import os
from pathlib import Path

import streamlit as st
from openai import APIError, OpenAI

from chat_logic import (
    EMPTY_RESPONSE_MESSAGE,
    GENERIC_ERROR_MESSAGE,
    MAX_CHAT_MESSAGE_CHARS,
    SESSION_TURN_LIMIT_MESSAGE,
    UPLOAD_TYPES,
    MessageError,
    UploadError,
    append_message,
    build_api_messages,
    check_chat_message,
    display_text,
    drop_last_message,
    friendly_error,
    load_system_prompt,
    session_turn_limit_reached,
    should_keep_turn,
    upload_to_turn,
)

# gpt-4o over gpt-4o-mini: the review is three tables and a set of refusals
# the prompt spells out, and the smaller model drifts on both. Both accept
# image input, which the photo upload path needs.
MODEL = "gpt-4o"
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

    Returns False when the user turn was dropped as non-retryable, so a caller
    that recorded the turn as sent can un-record it.
    """
    kept = True
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
            kept = not drop_last_message(st.session_state.messages, "user")
        st.error(friendly_error(exc), icon="⚠️")
    except Exception:
        logger.exception("Unexpected failure during completion")
        st.error(GENERIC_ERROR_MESSAGE, icon="⚠️")
    return kept


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
try:
    system_prompt = get_system_prompt()
except (OSError, ValueError):
    logger.exception("system prompt could not be loaded")
    st.error(
        f"The system prompt at `{SYSTEM_PROMPT_PATH}` is missing or empty, so the "
        "app cannot review anything. Restore the file and reload.",
        icon="📄",
    )
    st.stop()

if "messages" not in st.session_state:
    st.session_state.messages = []
# Uploads are tracked by Streamlit's per-upload-event file_id, so a corrected
# sheet re-exported under the same name and size is a new upload and a
# rejected one is refused once. Both are reset with the conversation.
if "sent_upload" not in st.session_state:
    st.session_state.sent_upload = None
if "rejected_upload" not in st.session_state:
    st.session_state.rejected_upload = None
# The uploader widget keeps its file across reruns, including the one Clear
# triggers; bumping its key is how the widget itself is reset, so the old
# schedule is not re-sent, and re-billed, the moment the transcript is empty.
if "uploader_key" not in st.session_state:
    st.session_state.uploader_key = 0

with st.sidebar:
    st.subheader("Schedule")
    upload = st.file_uploader(
        "Upload this period's schedule",
        type=list(UPLOAD_TYPES),
        key=f"uploader-{st.session_state.uploader_key}",
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
        st.session_state.rejected_upload = None
        st.session_state.uploader_key += 1
        st.rerun()

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(display_text(message))

# An upload is sent once, as its own user turn, the first time it appears.
# The uploader returns the same file on every rerun, so the turn is keyed on
# the upload event's file_id to stop it being re-sent after each message.
# Checked before the turn is appended, so a session at its limit sends nothing.
turn_limit_reached = session_turn_limit_reached(st.session_state.messages)
if upload is not None and not turn_limit_reached:
    rejected = st.session_state.rejected_upload
    if rejected is not None and rejected[0] == upload.file_id:
        # Refused already; show the same reason without parsing it again.
        st.error(rejected[1], icon="📎")
    elif upload.file_id != st.session_state.sent_upload:
        try:
            content, display = upload_to_turn(upload.name, upload.getvalue())
        except UploadError as exc:
            st.session_state.rejected_upload = (upload.file_id, str(exc))
            st.error(str(exc), icon="📎")
        else:
            # Recorded before the call so a rerun mid-stream cannot send the
            # file twice; un-recorded if the API rejects the turn outright, so
            # the same file can be sent again once it has been fixed.
            st.session_state.sent_upload = upload.file_id
            append_message(st.session_state.messages, "user", content, display=display)
            with st.chat_message("user"):
                st.markdown(display)
            if not complete_turn(client, system_prompt):
                st.session_state.sent_upload = None

# The limit is read again here: an upload accepted above may have used the
# last turn, and a stale answer would let the chat box add one more.
turn_limit_reached = session_turn_limit_reached(st.session_state.messages)
if turn_limit_reached:
    st.warning(SESSION_TURN_LIMIT_MESSAGE, icon="⏱️")

# chat_input does not trim, so a space-only submission arrives as a truthy
# string that append_message rejects. Normalising here keeps that rejection
# from surfacing as a traceback on the one call outside the try below.
# max_chars stops a paste in the browser only; check_chat_message is the
# server-side bound, and a refused message is never added to the history.
prompt = (
    st.chat_input(
        "Paste a schedule, or answer the questions",
        max_chars=MAX_CHAT_MESSAGE_CHARS,
        disabled=turn_limit_reached,
    )
    or ""
).strip()
if prompt and not turn_limit_reached:
    try:
        check_chat_message(prompt)
    except MessageError as exc:
        st.error(str(exc), icon="✂️")
    else:
        append_message(st.session_state.messages, "user", prompt)
        with st.chat_message("user"):
            st.markdown(prompt)
        complete_turn(client, system_prompt)
        # The box above rendered before this turn was added; rerun so a turn
        # that used the last slot locks it now, not on the next interaction.
        if session_turn_limit_reached(st.session_state.messages):
            st.rerun()
