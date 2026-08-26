---
name: continuous-learning
description: Turn hard-won session lessons into permanent skills. Use when a debugging session uncovers a non-obvious cause, a pattern gets settled after trying alternatives, or the same explanation has been needed twice - and at the end of any long task, ask whether something here deserves saving.
---

# Continuous Learning

Knowledge earned in a session dies with the session unless it's written down. This skill turns it into files that load automatically forever after.

## What qualifies

Save it when it is **reusable** (will come up again in this repo), **non-obvious** (cost real effort to figure out), and **not already documented** (check `.claude/skills/` and the repo docs first). Examples:

- A failure mode and its actual root cause ("migrations hang because X holds a lock on Y")
- A repo-specific procedure that isn't in any doc ("regenerating Z requires steps A, B, C in that order")
- A decision and its reasoning, so it doesn't get relitigated ("we chose polling over webhooks here because...")

Do NOT save: generic language knowledge, one-off incident details, anything containing secrets, tokens, customer data, or internal URLs that shouldn't ship in the repo.

## Format

Write to `.claude/skills/<kebab-name>/SKILL.md` - directly under `skills/`. Only `.claude/skills/*/SKILL.md` is discovered; a deeper folder like `skills/learned/<name>/` silently never loads:

```markdown
---
name: <kebab-name>
description: <what it covers AND the situations that should trigger it - this line decides whether it ever loads again, so pack it with the words a future session would use>
---

# <Title>

**Context:** when this applies.

**Pattern:** the actual knowledge - steps, code shape, or explanation.

**Example:** concrete instance from the session that produced it (sanitized).

**Gotchas:** what goes wrong when this is half-applied.
```

## Upkeep

- One topic per skill; merge into an existing learned skill rather than creating near-duplicates.
- Learned skills are repo content: they go through review like code, and a wrong one is worse than none - delete stale ones on sight.
- Trigger manually with `/learn`, or proactively offer at the end of a session that earned something.
