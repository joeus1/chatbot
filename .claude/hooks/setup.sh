#!/bin/sh
# SessionStart bootstrap: make sure dev tooling exists in fresh containers.
# Fail-open by design - never block or break a session over tooling.
cd "${CLAUDE_PROJECT_DIR:-.}" 2>/dev/null || true
if ! command -v ruff >/dev/null 2>&1; then
    pip install --quiet ruff >/dev/null 2>&1 || true
fi
exit 0
