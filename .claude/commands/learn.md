---
description: Distill a reusable pattern or hard-won lesson from this session into a learned skill so future sessions start smarter.
---

Extract a learned skill from this session (topic hint: $ARGUMENTS).

1. Identify the most reusable non-obvious thing established in this session: a debugging path that worked, a repo-specific gotcha, a pattern we settled on after trying alternatives. Skip anything obvious, one-off, or already covered by existing skills in `.claude/skills/`.
2. Write it to `.claude/skills/learned/<kebab-case-name>/SKILL.md` following the continuous-learning skill's format: frontmatter with name and a trigger-rich description, then the pattern, when to use it, and a concrete example from this session (with secrets and customer data stripped).
3. If a learned skill on this topic already exists, merge into it instead of creating a near-duplicate.
4. Show me the skill and where it was saved. It ships with the repo, so it must contain nothing sensitive.
