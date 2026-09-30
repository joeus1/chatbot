# chatbot

PrimeOps Schedule Review: a Streamlit app calling the OpenAI API. A manager
uploads a schedule, answers B1–B7 business-context questions and Q1–Q10 neutral
job-observation questions for each person, and gets findings, a proposed fix
and coaching guidance. `streamlit_app.py` owns UI and session state; `chat_logic.py` holds the
pure, unit-tested message, upload and error-mapping logic; the system prompt
is the document at `prompts/schedule_review.md`. `manager_guidance.py` is the
canonical question catalog, rendered in the app and inserted into the prompt
by `chat_logic.load_system_prompt`. Federal reference sources and guidance
limits are in `docs/federal_productivity_guidance.md`.

## Commands

- Run locally: `streamlit run streamlit_app.py`
- Dependencies: `pip install -r requirements.txt` (dev: `-r requirements-dev.txt`)
- Tests: `python -m pytest`
- `/verify` runs syntax + lint + secrets checks before committing

## Hard constraints

- Streamlit reruns the whole script on every interaction: durable state lives in `st.session_state`, expensive objects behind `@st.cache_resource`
- API keys via `st.secrets` / environment - never hardcoded, never logged; `.streamlit/secrets.toml` stays gitignored
- Wrap OpenAI calls in try/except with a friendly `st.error`; bound the history sent to the API
- Business demand and individual observations stay separate; missing evidence stays unknown. No employee scores, rankings, adverse-action recommendations or protected personal information; this is coaching guidance, not a legal-compliance determination.

See the `streamlit-patterns` skill for full patterns and `productionization` for the hardening roadmap. The HalalWay Toolkit in `.claude/` provides agents (planner, architect, code-reviewer, security-reviewer, tdd-guide, build-error-resolver, refactor-cleaner, doc-updater) and commands (`/plan /review /security /tdd /fix /ship /cleanup /learn /verify /review-export`).
