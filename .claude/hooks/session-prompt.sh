#!/bin/sh
# SessionStart autoprompt: the text injected into every session's context.
#
# Two parts, and the split is the point:
#   - .claude/session-prompt.md - the standing text. Edit THAT file, not this
#     one. Plain prose, no JSON escaping, and it diffs like prose.
#   - the block below - state that only exists at session start (branch,
#     uncommitted work, unpushed commits). This is the part CLAUDE.md cannot
#     carry, because CLAUDE.md is static and this is not.
#
# Durable rules belong in CLAUDE.md; it is always loaded. Keep this short -
# every line here competes for attention with those rules on every session.
#
# Wired in .claude/settings.json ONLY, not .claude/hooks/hooks.json: when the
# plugin is installed in a repo that also ships settings.json, both copies of
# a hook fire, and an autoprompt injected twice is just noise. setup.sh is in
# both because it takes a lock; this one is not because it cannot.
#
# Fail-open by design: every path exits 0. A session that starts without its
# banner is a papercut, a session that will not start is not.

# Set per repo: does merging to main deploy production?
DEPLOYS_FROM_MAIN=no

cd "${CLAUDE_PROJECT_DIR:-.}" 2>/dev/null || exit 0

[ -f .claude/session-prompt.md ] && cat .claude/session-prompt.md

git rev-parse --is-inside-work-tree >/dev/null 2>&1 || exit 0

branch=$(git rev-parse --abbrev-ref HEAD 2>/dev/null) || exit 0
dirty=$(git status --porcelain 2>/dev/null | wc -l | tr -d ' ')
ahead=$(git rev-list --count '@{u}..HEAD' 2>/dev/null)

echo
echo "Session state: branch \`$branch\`, $dirty uncommitted file(s)${ahead:+, $ahead unpushed commit(s)}."

if [ "$DEPLOYS_FROM_MAIN" = yes ] && [ "$branch" = main ]; then
    echo "You are on \`main\`, and merging to main deploys production. Branch before committing."
fi

exit 0
