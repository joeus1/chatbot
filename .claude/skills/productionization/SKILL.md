---
name: productionization
description: The gap between this tutorial-grade Streamlit chatbot and a production app - dependency pinning, secrets handling, bounded history, cost controls, and error handling. Use when hardening streamlit_app.py, preparing a deploy, adding features beyond the demo, or when someone asks "is this production ready".
---

# Chatbot Productionization

`streamlit_app.py` is currently the Streamlit tutorial shape: unpinned
dependencies, a paste-your-API-key input, unbounded history, and a hardcoded
model. Each gap below is ordered by risk; close them top-down as the app grows.

## 1. Secrets (highest risk)

- Replace the `st.text_input` API-key field with `st.secrets["OPENAI_API_KEY"]`
  (`.streamlit/secrets.toml` locally - it is gitignored and must stay so - and
  the Streamlit Cloud secrets UI when deployed). A paste-a-key UI trains users
  to paste keys into browsers and puts the key in session state.
- Never log, echo, or embed the key in errors. The toolkit guard hook blocks
  committing key-shaped strings, but rotation is the only fix once one leaks.

## 2. Reproducible builds

- Pin `requirements.txt`: `streamlit==x.y.z`, `openai==x.y.z` (current
  installed versions, then bump deliberately). Unpinned deps mean every deploy
  is a surprise upgrade.

## 3. Cost and context control

- Bound the history sent to the API: keep the full transcript in
  `st.session_state.messages` for display, but send only the last N turns
  (start with N=20) plus the system prompt. Unbounded history grows cost
  quadratically over a long chat and eventually overflows the context window.
- Set `max_tokens` on completions; put MODEL, N_HISTORY, and the system prompt
  in constants at the top of the file, not inline at call sites.

## 4. Resilience

- Wrap the OpenAI call in try/except: `AuthenticationError` -> friendly
  st.error about the key; `RateLimitError` -> "busy, try again"; generic ->
  log server-side, generic st.error client-side. Never dump a traceback to the
  page.
- Append the user message to state BEFORE the API call and the assistant reply
  only after the stream completes, so a mid-stream rerun neither drops nor
  duplicates turns (see the streamlit-patterns skill for the rerun model).

## 5. First test suite (proposed - see tdd-workflow to implement)

Extract the pure logic out of the script so it becomes testable, then:
- `test_history_bounding`: given 50 turns and N=20, exactly the last 20 plus
  the system prompt are sent; order preserved.
- `test_error_mapping`: each OpenAI exception class maps to the right
  user-facing message and never the raw exception text.
- `test_state_transitions`: user message appended before call, assistant after
  completion; a simulated rerun mid-stream leaves history consistent.
Mock the OpenAI client at the boundary; no network in tests.
