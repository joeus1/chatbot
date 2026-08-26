---
description: Find and safely remove dead code, duplicates, and unused dependencies in the given scope.
---

Use the refactor-cleaner agent on scope: $ARGUMENTS (default scope: files changed on this branch, or ask me for a scope if the branch is clean).

Only provably dead code may be removed, tests must stay green after every batch, and the final report must list each removal with the evidence it was dead.
