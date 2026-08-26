---
name: steward
description: PR-driving and landing conventions for the chatbot repo - how changes land (direct push to main), what a 403 on push means, and the shared HalalWay branch rules. Use when landing, pushing, watching a PR, or hitting GitHub access errors in this repo.
---

# PR Steward - chatbot

## Landing a change

1. `main` has NO branch protection: commit and `git push -u origin main`
   directly. PRs are optional here - use one only when review is wanted.
2. Validate before every push - that's `/verify`: `python -m compileall -q .`,
   `ruff check .` (install ruff if missing), and the secrets checks
   (`.streamlit/secrets.toml` must stay untracked).
3. If a push returns **403 "Claude doesn't have GitHub access to
   joeus1/chatbot"**, that is a missing Claude GitHub App grant for the
   `joeus1` account - not a network problem and not worth retrying. The owner
   fixes it at https://github.com/apps/claude/installations/select_target.
   Commit locally and say exactly this.

## Shared HalalWay rules (apply here too)

- Work from a branch or main pulled fresh; after any merge elsewhere, restart
  working branches from `origin/main` - never stack on merged history.
- Never rebase, amend, or force-push shared history; `--force-with-lease` only
  on branches you own (the guard hook enforces this).
- If you do open a PR: merge-commit method, keep it green, address every
  review comment, and restart the branch after it merges.
