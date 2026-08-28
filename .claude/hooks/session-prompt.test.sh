#!/bin/sh
# Tests for the SessionStart autoprompt (session-prompt.sh).
#
# Run directly - `sh .claude/hooks/session-prompt.test.sh` - or through the
# repo's own test runner, which wraps this file so CI executes it.
#
# Every case here is a behaviour that was once verified by hand. Hand
# verification does not survive the session that did it; this does. POSIX sh,
# no dependencies beyond git.
#
# Byte-identical across chatbot, primeops-site and primeops-aei, like the hook
# it tests.

set -u

HOOK_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
HOOK="$HOOK_DIR/session-prompt.sh"
WORK=$(mktemp -d)
trap 'rm -rf "$WORK"' EXIT INT TERM

passed=0
failed=0
ok()   { passed=$((passed + 1)); }
bad()  { printf '  FAIL  %s\n        %s\n' "$1" "$2"; failed=$((failed + 1)); }

run() { OUT=$(CLAUDE_PROJECT_DIR="$1" sh "$HOOK" 2>&1); RC=$?; }

contains() { case "$OUT" in *"$2"*) ok ;; *) bad "$1" "expected to find: $2" ;; esac; }
absent()   { case "$OUT" in *"$2"*) bad "$1" "expected NOT to find: $2" ;; *) ok ;; esac; }
exit_zero(){ [ "$RC" -eq 0 ] && ok || bad "$1" "exit status $RC, expected 0"; }

fixture() {
    d="$WORK/$1"
    mkdir -p "$d/.claude/hooks"
    cp "$HOOK" "$d/.claude/hooks/session-prompt.sh"
    printf 'BANNER-TEXT\n' > "$d/.claude/session-prompt.md"
    git init -q "$d"
    git -C "$d" symbolic-ref HEAD refs/heads/main
    git -C "$d" config user.email test@example.com
    git -C "$d" config user.name test
    git -C "$d" add -A
    git -C "$d" commit -qm base
    echo "$d"
}

# --- the standing text ------------------------------------------------------
d=$(fixture banner); run "$d"
contains "prints the standing text" "BANNER-TEXT"
exit_zero "banner run"

# The markdown is injected verbatim into every session, so a maintainer note in
# an HTML comment is not free - it is context spent on a reader who is not there.
if [ -f "$HOOK_DIR/../session-prompt.md" ]; then
    OUT=$(cat "$HOOK_DIR/../session-prompt.md"); RC=0
    absent "session-prompt.md carries no HTML comment" "<!--"
fi

# --- background tooling -----------------------------------------------------
d=$(fixture freshlock); mkdir -p "$d/.claude/.setup-lock"; run "$d"
contains "fresh lock says the install is still running" "still installing"
absent   "fresh lock is not reported as death" "died partway"
exit_zero "fresh lock run"

d=$(fixture stalelock); mkdir -p "$d/.claude/.setup-lock"
if touch -d '40 minutes ago' "$d/.claude/.setup-lock" 2>/dev/null; then
    run "$d"
    contains "stale lock is reported as a dead install" "died partway"
    exit_zero "stale lock run"
else
    printf '  SKIP  stale lock (touch -d unsupported here)\n'
fi

d=$(fixture failedinstall)
printf 'Collecting ruff\nERROR: no matching distribution\nsetup-exit=1\n' > "$d/.claude/.setup-log"
run "$d"
contains "a failed install is reported" "install failed (exit 1)"
contains "the failed install log is tailed" "no matching distribution"
exit_zero "failed install run"

d=$(fixture goodinstall)
printf 'Successfully installed ruff-0.8.4\nsetup-exit=0\n' > "$d/.claude/.setup-log"
run "$d"
absent "a successful install stays silent" "TOOLING"
exit_zero "successful install run"

# Regression: benign installer output routinely contains the word "error" -
# http-errors and assertion-error are ordinary transitive packages. Keying on
# prose made every good install look like a failure, every session.
d=$(fixture benignerrorword)
printf 'npm warn deprecated http-errors@1.6.3: no longer supported\nadded 412 packages\nsetup-exit=0\n' > "$d/.claude/.setup-log"
run "$d"
absent "the word 'error' in a successful log does not raise an alarm" "TOOLING"
exit_zero "benign error word run"

# A log with no status marker (written by an older setup.sh) cannot be judged.
# Silence beats guessing: a false alarm every session is worse than no alarm.
d=$(fixture unmarkedlog)
printf 'some output with the word error in it\n' > "$d/.claude/.setup-log"
run "$d"
absent "an unmarked log is not guessed at" "TOOLING"
exit_zero "unmarked log run"

# --- branch state -----------------------------------------------------------
d=$(fixture behind)
git init -q --bare "$WORK/behind-bare.git"
git -C "$d" remote add origin "$WORK/behind-bare.git"
git -C "$d" push -q -u origin main
git -C "$d" checkout -qb feature
git -C "$d" checkout -q main
echo x > "$d/x.txt"; git -C "$d" add -A; git -C "$d" commit -qm ahead1
echo y > "$d/y.txt"; git -C "$d" add -A; git -C "$d" commit -qm ahead2
git -C "$d" push -q origin main
git -C "$d" checkout -q feature
run "$d"
contains "reports how far behind the base branch it is" "2 commit(s) behind origin/main"
exit_zero "behind base run"

d=$(fixture ondeploybranch)
printf 'Merging to `main` deploys the production site.\n' > "$d/CLAUDE.md"
git -C "$d" add -A; git -C "$d" commit -qm claudemd
run "$d"
contains "warns on main when CLAUDE.md says main deploys" "deploys production"
exit_zero "on-main deploy warning run"

d=$(fixture ondeploybranch_nosentence)
printf 'This repo does not deploy from main.\n' > "$d/CLAUDE.md"
git -C "$d" add -A; git -C "$d" commit -qm claudemd
run "$d"
absent "stays quiet on main when CLAUDE.md does not say it deploys" "deploys production"
exit_zero "on-main quiet run"

d=$(fixture clean); run "$d"
absent "a clean tree reports no uncommitted files" "uncommitted"
exit_zero "clean run"

# --- fail open --------------------------------------------------------------
d=$(fixture nomd); rm -f "$d/.claude/session-prompt.md"; run "$d"
exit_zero "missing session-prompt.md"

run "$WORK"
exit_zero "CLAUDE_PROJECT_DIR is not a git repo"

run "/no/such/directory/anywhere"
exit_zero "CLAUDE_PROJECT_DIR does not exist"

d=$(fixture nogit)
mkdir -p "$WORK/fakebin"; printf '#!/bin/sh\nexit 127\n' > "$WORK/fakebin/git"; chmod +x "$WORK/fakebin/git"
OUT=$(CLAUDE_PROJECT_DIR="$d" PATH="$WORK/fakebin:$PATH" sh "$HOOK" 2>&1); RC=$?
exit_zero "git unavailable"
contains "still prints the standing text without git" "BANNER-TEXT"

printf '\n%s passed, %s failed\n' "$passed" "$failed"
[ "$failed" -eq 0 ]
