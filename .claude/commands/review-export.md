---
description: Review and analyze an uploaded export (zip or extracted directory) of this repo, diff it against the current HEAD, and merge in only genuinely new or missing content - never stale content HEAD has already moved past.
---

Given an export path in $ARGUMENTS (a `.zip` or an already-extracted directory),
run the comparison end to end and report findings before changing anything:

1. **Locate and extract.** If $ARGUMENTS is a `.zip`, extract it into the
   scratchpad directory (never inside the repo). If it's a directory, use it
   directly.

2. **Establish which side is authoritative.** Do not assume the export is
   newer just because it was just uploaded. Check for signals: an embedded
   git SHA in the filename, `requirements.txt`/`requirements-dev.txt`
   contents, and how `CLAUDE.md` and the test suite compare to HEAD's (fewer
   pinned dependencies, missing tests, or thinner error handling in the
   export are signs it predates HEAD, not that it's a divergent improvement).

3. **Diff, excluding noise:**
   `diff -rq <export> . --exclude=.git --exclude=__pycache__ --exclude=.venv --exclude=*.pyc`
   Then classify every difference into one of three buckets:
   - **Only in export** - a candidate addition. Check `CLAUDE.md`'s hard
     constraints and `chat_logic.py`'s existing structure for a reason the
     current repo doesn't have it (e.g. logic deliberately kept out of
     `streamlit_app.py` because it isn't unit-testable there). If nothing
     explains the absence, it may be a real gap.
   - **Only in current repo** - expected; ignore.
   - **Differs in both** - read the actual diff, not just the fact that it
     differs. Prefer HEAD's version whenever it has error handling, bounded
     history, or secrets-handling the export lacks - that is hardening, not
     drift to reconcile.

4. **Only merge what survives step 3 as a real, unexplained gap.** Validate
   any such addition against `CLAUDE.md`'s hard constraints (state lives in
   `st.session_state`, expensive objects behind `@st.cache_resource`, API
   keys via `st.secrets`/env only, OpenAI calls wrapped in try/except with a
   friendly `st.error`, bounded history) before adding it. New logic belongs
   in `chat_logic.py` with tests in `tests/`, not inline in
   `streamlit_app.py`.

5. **Never bulk-copy or overwrite.** Bring in individual files/hunks
   deliberately; never replace a current file wholesale with the export's
   version even when they differ, since that risks reverting hardening HEAD
   has that the export doesn't.

6. Run `/verify` on anything actually changed.

Finish with a summary in two sections: **Added** (what came in and why) and
**Skipped** (everything else, with one line on why HEAD's version wins or why
it wasn't a real gap). If nothing survives step 3, say so plainly instead of
manufacturing a change.
