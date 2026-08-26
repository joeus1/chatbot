---
name: streamlit-patterns
description: Patterns for this Streamlit + OpenAI chatbot app - use when modifying streamlit_app.py or extending the chatbot. Covers rerun model, session state, secrets, and streaming.
---

# Chatbot App Patterns

This repo is a single-file Streamlit app (`streamlit_app.py`) calling the OpenAI API. Streamlit reruns the whole script top-to-bottom on every interaction - design for that.

## Rerun model & state

- Anything that must survive an interaction lives in `st.session_state` (message history does; never rebuild it from scratch on rerun).
- Initialize state defensively: `if "messages" not in st.session_state: st.session_state.messages = []`.
- Expensive or repeat-stable work goes behind `@st.cache_data` (data) or `@st.cache_resource` (clients/connections) - construct the OpenAI client once via `st.cache_resource`, not on every rerun.
- Widget keys: give explicit `key=` to widgets that are created conditionally, or state gets orphaned.

## Secrets & keys

- Prefer `st.secrets["OPENAI_API_KEY"]` (`.streamlit/secrets.toml`, gitignored) over asking users to paste keys; if the paste-a-key UX stays, keep `type="password"` and never write the key to logs, state dumps, or error messages.
- Never commit `secrets.toml` or hardcode a key. A key that reaches a commit must be rotated.

## Chat & streaming

- Use `st.chat_message` / `st.chat_input` for the conversation UI and `st.write_stream` for streaming completions - perceived latency matters more than total latency.
- Append the user message to history before the API call; append the assistant reply after the stream completes, so a mid-stream rerun doesn't drop or duplicate turns.
- Wrap API calls in try/except: show a friendly `st.error` for auth/rate-limit failures and keep the app usable; don't dump raw tracebacks to the page.
- Bound the history sent to the API (last N turns or token-trimmed) so long chats don't blow the context window or the bill.

## Hygiene

- Pin versions in `requirements.txt` once the app matters (`streamlit==x.y.z`, `openai==x.y.z`) so deploys are reproducible.
- Model names, temperature, and system prompt belong in constants at the top of the file, not scattered through the call sites.
