#!/bin/sh
# SessionStart bootstrap: give a fresh container the tooling /verify needs -
# pytest (pinned in requirements-dev.txt) and ruff for the lint step.
# Fail-open by design: every failure path exits 0 and changes nothing.
cd "${CLAUDE_PROJECT_DIR:-.}" 2>/dev/null || true

python3 -c "import pytest" >/dev/null 2>&1 && have_pytest=yes
python3 -m ruff --version >/dev/null 2>&1 && have_ruff=yes
[ -n "$have_pytest" ] && [ -n "$have_ruff" ] && exit 0

# In plugin mode this runs inside whatever repo is consuming the toolkit, which
# may have no .claude/ at all. Without this the lock mkdir below fails with
# ENOENT and the whole bootstrap becomes a silent no-op: no pytest, no ruff, and
# /verify failing later for no visible reason.
mkdir -p .claude 2>/dev/null || true

# Reap only a lock we can show is abandoned. A previous version aged the lock
# out after 30 minutes without ever refreshing it, so a genuinely slow install
# had its own live lock reaped, a second install started, and the first job then
# removed the second's lock. Ownership is recorded instead: a live installer is
# never reaped however long it runs, and a dead one is reaped at once rather
# than half an hour later. A fresh lock with no pid yet is left alone - that is
# the installer between mkdir and its first write, not an abandoned run.
if [ -d .claude/.setup-lock ]; then
    lock_pid=$(cat .claude/.setup-lock/pid 2>/dev/null)
    if [ -n "$lock_pid" ] && ! kill -0 "$lock_pid" 2>/dev/null; then
        rm -rf .claude/.setup-lock 2>/dev/null || true
    elif [ -z "$(find .claude/.setup-lock -maxdepth 0 -mmin -180 2>/dev/null)" ]; then
        # Backstop for a pid recycled across a container restart.
        rm -rf .claude/.setup-lock 2>/dev/null || true
    fi
fi

# Install only what this hook claims to install. requirements-dev.txt starts
# with `-r requirements.txt`, so installing it wholesale silently re-pins the
# app's runtime dependencies - and in plugin mode installs an unrelated repo's
# entire dependency set. Dropping the -r lines leaves the dev-only pins.
dev_only=$(grep -vE '^[[:space:]]*(-r|#|$)' requirements-dev.txt 2>/dev/null | tr '\n' ' ')

# Output goes to .claude/.setup-log (gitignored), not /dev/null: a silent
# background install that fails is indistinguishable from one still running,
# which cost real debugging time on 2026-08-27.
# mkdir is atomic, so two SessionStart runs racing here - including the project
# and plugin registrations both firing in one session - cannot both install.
if mkdir .claude/.setup-lock 2>/dev/null; then
    nohup sh -c 'echo $$ >.claude/.setup-lock/pid 2>/dev/null; { pip install --quiet '"$dev_only"' ruff; } >.claude/.setup-log 2>&1; rm -rf .claude/.setup-lock' >/dev/null 2>&1 &
    echo "HalalWay Toolkit: installing test and lint tooling in the background."
fi
exit 0
