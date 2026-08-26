---
description: Run this repo's pre-commit verification - syntax check, lint if available, secrets check - and report pass/fail.
---

Run these verification checks in order and stop to fix anything that fails:

1. `python -m compileall -q .` - syntax check
2. `ruff check .` if ruff is installed (`pip install ruff` is fine in a scratch env); otherwise note it was skipped
3. Grep the diff for anything that looks like a committed secret (`sk-`, `api_key =`, `secrets.toml`) and confirm `.streamlit/secrets.toml` is not tracked by git
4. If dependencies changed: `pip install -r requirements.txt` in a scratch environment to confirm it resolves

Extra focus: $ARGUMENTS

This repo has no test suite yet - if the change adds meaningful logic beyond UI wiring, propose the first `pytest` tests for it. Report each check's result; green means safe to commit.
