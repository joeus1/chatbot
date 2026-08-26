---
description: Review the current diff (or a named target) for correctness, data-safety, and maintainability defects.
---

Use the code-reviewer agent to review $ARGUMENTS (if no target is given, review the current uncommitted diff plus any commits on this branch not on the default branch).

Then relay the findings ranked by severity with file:line references, and state clearly whether it is safe to commit. Do not apply fixes unless I ask.
