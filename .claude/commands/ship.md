---
description: Verify, commit, and push the current work in one gated flow - checks must pass before the commit happens.
---

Ship the current work ($ARGUMENTS may narrow what to include or add context for the commit message):

1. Run `git status` and `git diff` - list what would ship and flag anything that looks accidental (debug prints, commented-out code, unrelated files, large binaries). Leave those out.
2. Run the repo verification (`/verify` checks). If anything fails, STOP and fix it first - never commit red.
3. Stage the intended files explicitly (no blind `git add -A` if unrelated changes are present).
4. Commit with an imperative subject under 72 chars and a body explaining why.
5. Push to the current branch with `git push -u origin <branch>`. Never push directly to main/master - if we're on it, create a branch first and say so.
6. Report: what shipped, checks that passed, and the branch it went to.
