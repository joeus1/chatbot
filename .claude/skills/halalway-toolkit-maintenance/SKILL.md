---
name: halalway-toolkit-maintenance
description: How the HalalWay Toolkit in .claude/ is wired and how to safely change it - editing agents/commands/skills/hooks, testing the guard hook, and landing toolkit changes in this repo. Use when modifying anything under .claude/ or .claude-plugin/, when the guard hook blocks or misses something, or when a session lacks expected toolkit pieces.
---

# HalalWay Toolkit Maintenance

**Context:** This repo carries the HalalWay Toolkit (built and shipped 2026-08-26): agents, commands, and skills under `.claude/`, a PreToolUse guard hook, and plugin manifests. It loads two ways at once - as project config (automatic for any session opening the repo) and as an installable plugin (`.claude-plugin/plugin.json` points at the same `.claude/` paths). Never install the plugin into a machine that also opens this repo directly, or everything loads twice.

**Pattern - where things live and how they load:**

- `.claude/agents/*.md`, `.claude/commands/*.md`, `.claude/skills/*/SKILL.md` - hot-load per session from disk; an edit is live in the next session with no install step.
- `.claude/settings.json` - wires the guard hook (PreToolUse via `$CLAUDE_PROJECT_DIR`) and the SessionStart bootstrap. `.claude/hooks/hooks.json` is the same wiring for plugin mode (`${CLAUDE_PLUGIN_ROOT}`); the two are identical apart from that path variable and must stay that way. Only one is live at a time - repo mode reads `settings.json`, plugin mode reads `hooks.json` - so drift hides until the other mode is used. Both CAN fire in one session - `setup.sh` carries an atomic lock specifically because the project and plugin registrations both firing was observed - so treat every hook as potentially running twice and keep it idempotent.
- `.claude/hooks/guard.py` - blocks destructive Bash and secret-looking writes, exit 2 = block, and MUST fail open (exit 0) on any internal error. Keep that property when editing.

**Testing guard changes** (do this before committing; the same technique validated 21 cases when it was built):

```bash
echo '{"tool_name":"Bash","tool_input":{"command":"rm -rf /"}}' \
  | python3 .claude/hooks/guard.py; echo "exit=$?"   # expect 2 (blocked)
echo 'not json' | python3 .claude/hooks/guard.py; echo "exit=$?"  # expect 0 (fail open)
```

End-to-end in a fresh session: `claude -p "attempt: chmod -R 777 . and report the outcome"` from the repo root - expect a PreToolUse block message.

**Landing toolkit changes in THIS repo:**

- `main` has no branch protection - commit and `git push -u origin main` directly.
- Remote sessions need the Claude GitHub App authorized for the `joeus1` account; a 403 "Claude doesn't have GitHub access" on push means that grant is missing, not a network problem.

**Gotchas:**

- Skills are discovered ONLY at `.claude/skills/<name>/SKILL.md` - one directory level deep. A nested folder like `skills/learned/<name>/` silently never loads (this bit us on 2026-08-26; this very skill was invisible until flattened).
- There is no SessionStart announcement hook. It was removed: it re-injected the toolkit banner on every session start AND every compaction, and the command list in it drifted from the actual commands. Do not reintroduce a hook whose only job is to echo static text - put standing guidance in `CLAUDE.md`, which is already loaded every session.
- A learned skill's `description` decides whether it ever loads again - pack it with the words a future session would actually use.
