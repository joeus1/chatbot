---
description: Fix a bug the disciplined way - reproduce it with a failing test first, then fix, then verify nothing else broke.
---

Fix this bug test-first: $ARGUMENTS

1. **Reproduce.** Locate the faulty code path and write the smallest test that reproduces the bug. Run it and confirm it fails on the current code for the reported reason. If you cannot reproduce it, stop and report what you tried - do not "fix" what you can't observe.
2. **Root-cause.** Explain in one or two sentences why the code misbehaves. The fix must target the cause, not the symptom.
3. **Fix minimally.** Change only what the root cause requires.
4. **Verify.** The reproduction test now passes; run the full relevant suite to prove nothing else regressed. Consider and add sibling cases (same bug shape elsewhere, boundary values).
5. Report: root cause, the fix (file:line), the new test, and the passing suite output.
