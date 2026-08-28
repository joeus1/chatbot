#!/bin/sh
# SessionStart autoprompt: what a session cannot cheaply find out for itself.
#
# The standing text lives in .claude/session-prompt.md - edit that, not this.
# Durable rules belong in CLAUDE.md, which is always loaded; repeating them
# here would only spend context twice.
#
# Everything below reports BY EXCEPTION: it prints when something is true and
# actionable, and stays silent otherwise. A hook that emits the same boilerplate
# every session trains the reader to skip it, which costs more than it gives.
#
# This file is byte-identical across chatbot, primeops-site and primeops-aei -
# nothing in it is repo-specific, and the one thing that used to be (whether
# main deploys production) is read from CLAUDE.md instead. Verify with:
#     diff <repo-a>/.claude/hooks/session-prompt.sh <repo-b>/...
#
# Wired in .claude/settings.json ONLY, never .claude/hooks/hooks.json: when the
# plugin is installed alongside the project config both copies of a hook fire,
# and setup.sh survives that only because it takes an atomic lock.
#
# Fail-open like setup.sh: every path exits 0, no network, no writes. A session
# that starts without its banner is a papercut; one that will not start is not.

cd "${CLAUDE_PROJECT_DIR:-.}" 2>/dev/null || exit 0

[ -f .claude/session-prompt.md ] && cat .claude/session-prompt.md

# --- tooling bootstrap ------------------------------------------------------
# setup.sh installs dev tooling in the background behind an atomic mkdir lock.
# Tests run before it finishes fail with import errors that look like real bugs,
# and an install that DIED leaves behind exactly the same lock as one still
# running - the ambiguity that cost a debugging session on 2026-08-27. The log
# exists to resolve it; this is the thing that finally reads it.
if [ -d .claude/.setup-lock ]; then
    if find .claude/.setup-lock -maxdepth 0 -mmin +30 2>/dev/null | grep -q .; then
        echo
        echo "TOOLING: .claude/.setup-lock is over 30 minutes old, so a background install died partway."
        echo "Dev tooling may be missing or half-installed. Check .claude/.setup-log, remove the lock"
        echo "directory, and re-run .claude/hooks/setup.sh before trusting any test or lint result."
    else
        echo
        echo "TOOLING: dev tooling is still installing in the background (.claude/.setup-lock is fresh)."
        echo "Wait for it before running tests or lint, or you will chase spurious import errors."
    fi
elif [ -s .claude/.setup-log ] && grep -qiE 'error|no matching distribution|could not find|failed' .claude/.setup-log 2>/dev/null; then
    echo
    echo "TOOLING: the last background install logged errors. Tail of .claude/.setup-log:"
    tail -5 .claude/.setup-log | sed 's/^/    /'
fi

git rev-parse --is-inside-work-tree >/dev/null 2>&1 || exit 0
branch=$(git rev-parse --abbrev-ref HEAD 2>/dev/null) || exit 0

# --- where this working tree stands -----------------------------------------
dirty=$(git status --porcelain 2>/dev/null | wc -l | tr -d ' ')
ahead=$(git rev-list --count '@{u}..HEAD' 2>/dev/null)
line="Branch \`$branch\`"
[ "${dirty:-0}" -gt 0 ] && line="$line, $dirty uncommitted file(s)"
[ "${ahead:-0}" -gt 0 ] && line="$line, $ahead unpushed commit(s)"
echo
echo "$line."

# Drift against the default branch, read from refs already on disk - never a
# fetch, which would block session start on the network and can hang. That
# makes this as fresh as the last fetch: accurate in a fresh clone, possibly
# stale in a long-lived checkout, and silent rather than wrong when unsure.
base=""
for candidate in origin/main origin/master; do
    git rev-parse --verify -q "$candidate" >/dev/null 2>&1 && { base=$candidate; break; }
done
if [ -n "$base" ] && [ "$branch" != "${base#origin/}" ]; then
    behind=$(git rev-list --count "HEAD..$base" 2>/dev/null)
    if [ "${behind:-0}" -gt 0 ]; then
        echo "This branch is $behind commit(s) behind $base as of the last fetch. Merge the base in"
        echo "before the conflict finds you, and confirm its PR has not already merged - a merged PR"
        echo "cannot take new commits, so follow-up work restarts from the default branch."
    fi
fi

# Whether main deploys production is not hardcoded per repo: it is stated in
# each CLAUDE.md, so that one sentence stays the single source of truth and this
# script stays identical everywhere.
if [ "$branch" = main ] || [ "$branch" = master ]; then
    if grep -qiE 'merging to .?main.? deploys' CLAUDE.md 2>/dev/null; then
        echo "You are on \`$branch\`, and per CLAUDE.md merging here deploys production. Branch first."
    fi
fi

# --- what the last session left behind --------------------------------------
# CLAUDE.md points at these as the carriers of project history; a session that
# has to be told to go read them usually is not told at all.
if [ -f CLAUDE_MEMORY.md ]; then
    recent=$(grep -m1 '^## ' CLAUDE_MEMORY.md 2>/dev/null)
    threads=$(grep -m1 -i 'open threads' CLAUDE_MEMORY.md 2>/dev/null)
    if [ -n "$recent" ] || [ -n "$threads" ]; then
        echo
        [ -n "$recent" ] && echo "Project memory, most recent entry - ${recent#\#\# }"
        [ -n "$threads" ] && echo "$threads"
        echo "Read CLAUDE_MEMORY.md (and HANDOFF.md, if present) before picking up related work."
    fi
fi

exit 0
