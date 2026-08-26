# chatbot

Single-file Streamlit chat app (`streamlit_app.py`) calling the OpenAI API.

## Commands

- Run locally: `streamlit run streamlit_app.py`
- Dependencies: `pip install -r requirements.txt`
- `/verify` runs syntax + lint + secrets checks before committing

## Hard constraints

- Streamlit reruns the whole script on every interaction: durable state lives in `st.session_state`, expensive objects behind `@st.cache_resource`
- API keys via `st.secrets` / environment - never hardcoded, never logged; `.streamlit/secrets.toml` stays gitignored
- Wrap OpenAI calls in try/except with a friendly `st.error`; bound the history sent to the API

See the `streamlit-patterns` skill for full patterns. The HalalWay Toolkit in `.claude/` provides agents (planner, architect, code-reviewer, security-reviewer, tdd-guide, build-error-resolver, refactor-cleaner, doc-updater) and commands (`/plan /review /security /tdd /fix /ship /cleanup /learn /verify`).
