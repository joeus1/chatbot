#!/bin/sh
# SessionStart bootstrap: give a fresh container the tooling /verify needs -
# pytest (pinned in requirements-dev.txt) and ruff for the lint step.
# Fail-open by design: every failure path exits 0 and changes nothing.
cd "${CLAUDE_PROJECT_DIR:-.}" 2>/dev/null || true

python3 -c "import pytest" >/dev/null 2>&1 && have_pytest=yes
python3 -m ruff --version >/dev/null 2>&1 && have_ruff=yes
[ -n "$have_pytest" ] && [ -n "$have_ruff" ] && exit 0

# Clear a lock left behind by an install that died (older than 30 minutes).
if [ -d .claude/.setup-lock ] && [ -z "$(find .claude/.setup-lock -maxdepth 0 -mmin -30 2>/dev/null)" ]; then
    rmdir .claude/.setup-lock 2>/dev/null || true
fi

# Output goes to .claude/.setup-log (gitignored), not /dev/null: a silent
# background install that fails is indistinguishable from one still running,
# which cost real debugging time on 2026-08-27.
# mkdir is atomic, so concurrent SessionStart runs - including the project and
# plugin registrations both firing in one session - cannot both install.
if mkdir .claude/.setup-lock 2>/dev/null; then
    nohup sh -c 'rc=0; { if [ -f requirements-dev.txt ]; then pip install --quiet -r requirements-dev.txt || rc=$?; fi; pip install --quiet ruff || rc=$?; } >.claude/.setup-log 2>&1; echo "setup-exit=$rc" >>.claude/.setup-log; rmdir .claude/.setup-lock' >/dev/null 2>&1 &
    echo "HalalWay Toolkit: installing test and lint tooling in the background."
fi
exit 0
