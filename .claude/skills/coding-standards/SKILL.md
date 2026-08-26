---
name: coding-standards
description: HalalWay coding standards for Python and TypeScript/React work. Use when writing or reviewing any code in this repo - covers naming, error handling, typing, dependencies, and commit hygiene.
---

# HalalWay Coding Standards

## Universal

- **Follow the file you're in.** Match the existing naming, import style, comment density, and test patterns of the surrounding code before reaching for personal preference.
- **Small, single-purpose functions.** If a function needs a section comment, it wants to be two functions.
- **No dead code on main.** Delete, don't comment out. Git history is the archive.
- **Errors are handled or propagated, never swallowed.** An empty `except`/`catch` block is a bug. Catch the narrowest exception you can act on; include context when re-raising.
- **Names say what, not how.** `overdue_invoices`, not `data2`. Booleans read as predicates: `is_open`, `has_paid`.
- **New dependencies need a reason.** Prefer the standard library or an existing dependency; a new package must be maintained, typed, and worth its supply-chain risk.
- **Secrets never in code.** Environment variables or the platform's secret store; `.env` stays gitignored.

## Python (3.11+)

- Type hints on all public function signatures; `pydantic` models at API boundaries, plain dataclasses internally when validation isn't needed.
- `ruff` clean at the repo's configured settings - fix the code, don't sprinkle `# noqa`.
- f-strings for formatting, never for SQL - queries use bound parameters through SQLAlchemy.
- Timezone-aware datetimes only (`datetime.now(timezone.utc)`); naive datetimes are bugs waiting for a restaurant in another timezone.
- Money is `Decimal` or integer cents, never float.

## TypeScript / React

- No `any` unless quarantined with a comment explaining why; prefer `unknown` + narrowing.
- Components small and pure; derive state, don't mirror it (`useMemo` over copied `useState`).
- All user-visible strings and dates formatted at the edge, logic stays locale-free.
- Handle loading and error states for every async boundary - no spinner-forever paths.

## Commits

- Imperative subject line under 72 chars; body explains why, not what.
- One logical change per commit; formatting-only churn goes in its own commit.
- Never commit commented-out code, debug prints, or `.env` files.
