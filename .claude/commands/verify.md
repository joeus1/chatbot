---
description: Run this repo's pre-commit verification - syntax check, lint if available, secrets check - and report pass/fail.
---

Run these verification checks in order and stop to fix anything that fails:

1. `python -m compileall -q .` - syntax check
2. `python3 -m ruff check .` if ruff is installed (`pip install ruff` is fine in a
   scratch env); otherwise note it was skipped. Use `python3 -m ruff`, not bare
   `ruff`: a stray `ruff` earlier on PATH would lint by a different version.
3. `python3 -m pytest` - the unit suite over `chat_logic.py`. This must pass.
4. Grep the diff for anything that looks like a committed secret (`sk-`, `api_key =`, `secrets.toml`) and confirm `.streamlit/secrets.toml` is not tracked by git
5. If dependencies changed: `pip install -r requirements.txt` in a scratch environment to confirm it resolves

Extra focus: $ARGUMENTS

Behavior lives in `chat_logic.py` precisely so it can be tested - new logic there needs tests in `tests/` in the same change, not a follow-up. Report each check's result; green means safe to commit.
