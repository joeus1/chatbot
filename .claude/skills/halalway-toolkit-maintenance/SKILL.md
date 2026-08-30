---
name: halalway-toolkit-maintenance
description: How the HalalWay Toolkit in .claude/ is wired and how to safely change it - editing agents/commands/skills/hooks, testing the guard hook, and landing toolkit changes in this repo. Use when modifying anything under .claude/ or .claude-plugin/, when the guard hook blocks or misses something, or when a session lacks expected toolkit pieces.
---

# HalalWay Toolkit Maintenance

**Context:** This repo carries the HalalWay Toolkit (built and shipped 2026-08-26): agents, commands, and skills under `.claude/`, a PreToolUse guard hook, and plugin manifests. It loads two ways at once - as project config (automatic for any session opening the repo) and as an installable plugin (`.claude-plugin/plugin.json` points at the same `.claude/` paths). Never install the plugin into a machine that also opens this repo directly, or everything loads twice.

**Pattern - where things live and how they load:**

- `.claude/agents/*.md`, `.claude/commands/*.md`, `.claude/skills/*/SKILL.md` - hot-load per session from disk; an edit is live in the next session with no install step.
- `.claude/settings.json` - wires the guard hook (PreToolUse via `$CLAUDE_PROJECT_DIR`), the setup bootstrap, and the SessionStart autoprompt. `.claude/hooks/hooks.json` is the same wiring for plugin mode (`${CLAUDE_PLUGIN_ROOT}`); the two are identical apart from that path variable and must stay that way, with one deliberate exception below. Only one is live at a time - repo mode reads `settings.json`, plugin mode reads `hooks.json` - so drift hides until the other mode is used. Both CAN fire in one session - `setup.sh` carries an atomic lock specifically because the project and plugin registrations both firing was observed - so treat every hook as potentially running twice and keep it idempotent.
- `.claude/session-prompt.md` - the standing text injected into every session, printed by `.claude/hooks/session-prompt.sh`. The hook then adds, only when true: background-tooling status read from `.setup-lock`/`.setup-log`, branch plus uncommitted and unpushed counts, how far behind `origin/main` the branch is, an on-main deploy warning, and the newest `CLAUDE_MEMORY.md` entry with its open threads. Edit the markdown; the hook needs no changes.
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
- The old SessionStart announcement hook was removed for cause: it re-injected a static toolkit banner on every session start AND every compaction, and its command list drifted from the actual commands. The autoprompt that replaced it is not a return to that - it reports BY EXCEPTION, printing only what is true and actionable. Keep it that way; a hook whose only job is to echo static text belongs in `CLAUDE.md`, which is already loaded every session.
- The SessionStart autoprompt text lives in `.claude/session-prompt.md`, one per repo - edit that, not `settings.json`, and not the hook. Keep its command list matching the actual commands, and update every repo when it changes.
- `session-prompt.sh` is wired in `settings.json` ONLY, never `hooks.json` - that is the exception to keeping the two in sync. A hook registered in both fires twice; `setup.sh` survives that because it takes an atomic lock, but a second copy of the autoprompt would just inject the banner twice.
- `session-prompt.sh` is byte-identical in all three repos and must stay that way - `md5sum */.claude/hooks/session-prompt.sh` is the check. Its behaviour is covered by `.claude/hooks/session-prompt.test.sh` (also byte-identical), which each repo's own runner wraps so CI executes it - `tests/test_session_prompt_hook.py` under pytest, `tests/session-prompt-hook.test.js` under vitest. Run it directly with `sh .claude/hooks/session-prompt.test.sh` while editing the hook. Nothing in it is repo-specific: it reports by exception, so anything that does not apply to a repo simply stays silent there.
- The on-main deploy warning is read from CLAUDE.md, by grepping for the sentence "Merging to `main` deploys". That keeps one source of truth, but it means REWORDING THAT SENTENCE SILENTLY DISABLES THE WARNING. Keep the phrase intact in primeops-site and primeops-aei, or update the grep in the same commit.
- The autoprompt is what finally reads `.claude/.setup-log` and `.claude/.setup-lock`, distinguishing an install still running from one that died - the ambiguity that cost a session on 2026-08-27. `primeops-site` had a lock stranded from 2026-08-26 that this surfaced on its first run; its `setup.sh` had never received the stale-lock recovery or the logging that chatbot and primeops-aei got.
- A learned skill's `description` decides whether it ever loads again - pack it with the words a future session would actually use.
- Never judge a background install by grepping `.setup-log` for words like "error": `http-errors` and `assertion-error` are ordinary transitive packages, so that reported every healthy install as a failure. `setup.sh` records `setup-exit=<status>` as the log's last line and the autoprompt keys on that; a log with no marker is not guessed at. When adding an install step to `setup.sh`, accumulate its status (`|| rc=$?`) rather than letting `$?` report only the last command - that masked a real pip failure behind a later success.
- A populated `node_modules` is not an installed one. A half-finished `npm ci` leaves the directory full and `.bin` empty, and the old primeops-site guard counted that as installed, so the tree could never repair itself; the guard now treats an empty `.bin` as no install.
