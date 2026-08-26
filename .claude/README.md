# HalalWay Toolkit

In-house Claude Code toolkit for HalalWay repos. Everything here loads automatically for anyone who opens this repository with Claude Code — no marketplace, no network fetch, no install step.

## What's included

**Agents** (`agents/`) — delegate with the Agent/Task tool, or Claude picks them up proactively:

| Agent | Use |
|---|---|
| `planner` | Step-by-step implementation plans before coding (read-only) |
| `architect` | System design trade-offs and recommendations (read-only) |
| `code-reviewer` | Reviews diffs for correctness, data-safety, maintainability |
| `security-reviewer` | Secrets, injection, authz, tenant isolation, money paths |
| `tdd-guide` | Red-green-refactor implementation, tests first |
| `build-error-resolver` | Minimal-diff fixes for broken builds/types/lint |
| `refactor-cleaner` | Evidence-based dead code and duplicate removal |
| `doc-updater` | Syncs READMEs/docs/examples with what a diff changed |

**Commands** (`commands/`): `/plan`, `/review`, `/security`, `/tdd`, `/fix` (bug fix, reproduction-test-first), `/ship` (verify → commit → push, gated on green), `/cleanup`, `/learn` (save a session lesson as a skill), `/verify` (runs this repo's actual lint + test gauntlet).

**Skills** (`skills/`): `coding-standards`, `tdd-workflow`, `security-review`, `continuous-learning`, plus a repo-specific patterns skill. Skills saved by `/learn` accumulate under `skills/learned/`.

**Hooks** (`hooks/` + `settings.json`): a tested PreToolUse guard that deterministically blocks destructive commands (`rm -rf /`-class deletes, force pushes without lease, `curl | sh`, `chmod 777`, hard resets to origin/main) and blocks writes containing real-looking secrets (OpenAI/Stripe/AWS/GitHub/Slack keys, private key blocks) or untracked-`.env`-into-git mistakes. Fails open on any internal error, so it can never wedge a session. A SessionStart hook announces the toolkit.

## Installing elsewhere as a plugin

This repo also carries plugin manifests (`.claude-plugin/` at the repo root), so the toolkit can be installed into any other project or machine:

```
/plugin marketplace add Halal-Way/primeops-aei
/plugin install halalway-toolkit@halalway
```

If you install it as a plugin, don't also copy this `.claude/` directory into the same project, or agents and commands will be defined twice.

## Editing

These are plain Markdown files — edit them like code, review them like code. Keep agent descriptions accurate (they control when Claude auto-delegates) and keep `/verify` in sync with the repo's real check commands.
