# chatbot

Streamlit chat app calling the OpenAI API: `streamlit_app.py` owns UI and
session state; `chat_logic.py` holds the pure, unit-tested message and
error-mapping logic.

## Commands

- Run locally: `streamlit run streamlit_app.py`
- Dependencies: `pip install -r requirements.txt` (dev: `-r requirements-dev.txt`)
- Tests: `python -m pytest`
- `/verify` runs syntax + lint + secrets checks before committing

## Hard constraints

- Streamlit reruns the whole script on every interaction: durable state lives in `st.session_state`, expensive objects behind `@st.cache_resource`
- API keys via `st.secrets` / environment - never hardcoded, never logged; `.streamlit/secrets.toml` stays gitignored
- Wrap OpenAI calls in try/except with a friendly `st.error`; bound the history sent to the API

See the `streamlit-patterns` skill for full patterns and `productionization` for the hardening roadmap. The HalalWay Toolkit in `.claude/` provides agents (planner, architect, code-reviewer, security-reviewer, tdd-guide, build-error-resolver, refactor-cleaner, doc-updater) and commands (`/plan /review /security /tdd /fix /ship /cleanup /learn /verify`).
