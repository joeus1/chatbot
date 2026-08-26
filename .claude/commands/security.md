---
description: Run a security review of the current diff or a named path - secrets, injection, authz, tenant isolation, money paths.
---

Use the security-reviewer agent on $ARGUMENTS (if no target is given, review the current branch's changes against the default branch).

Relay confirmed findings with severity, attack scenario, and the specific fix for each. Apply only fixes I approve, unless a finding is a committed secret - flag those immediately as needing rotation, since removing a secret from the working tree does not un-leak it from git history.
