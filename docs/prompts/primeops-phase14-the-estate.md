# Phase 14 — build the synthetic estate

Joe has said to start it. This is Job B from the original brief, and Job A
(the eight real HalalWay locations) stays deferred exactly as it was.

## Before you seed

Finish the brand-isolation matrix first — it is already in flight. **If it
shows the fold did not reach all six tables, or that an owner is locked out,
fix that before any seeding.** The estate's scenarios rest on brand isolation
being real; seeding on top of an unverified boundary means every later test
result is ambiguous. If the matrix is clean, carry straight on.

## Build the honest scenarios first

Scenarios 5, 6 and 7 — the fix that did nothing, the fix that made things
worse, the outcome inside the noise band — are **the first three you build,
not the last three.**

Two reasons. If they turn out to be unbuildable, that is the finding, and it
should surface while there is still budget to act on it rather than after the
six comfortable cases are done. And building the successes first creates
exactly the pressure that softens the honest ones into near-misses. You said
yourself that `action_outcome`'s check tying `outcome_class` to the numbers is
what stops the application layer calling a 42,000-unit loss "improved" — build
the rows that exercise that check before the rows that never touch it.

Publish after those three and **stop.** That is a checkpoint, not a finish
line: I want to see that the harness can represent failure before it
represents anything else. Then the remaining six.

## Scope — build the minimum that exercises the thing

Do not build a large estate. Build the smallest one that can actually test
what needs testing:

- **Two operators**, so cross-tenant isolation has something to cross.
- **At least two brands under one operator**, so brand isolation has something
  to isolate and a brand-level rollup has something to roll up.
- **At least two locations per brand**, so "one location is broken while the
  brand is fine" is distinguishable from "the brand is broken" — the
  distinction you used to argue for a first-class brand entity.

More locations than that adds rows without adding coverage. If you find a
scenario that genuinely cannot be expressed at this size, say which and why,
and I will widen it deliberately rather than by drift.

## Properties the seed itself must have

- **Deterministic.** A fixed seed, so a failing test is reproducible rather
  than a story about a run nobody can repeat.
- **Idempotent and re-runnable.** This is a harness that will be reset
  repeatedly. Running it twice must not double the estate or fail.
- **Reversible**, with a teardown, held to the same standard as the migration
  reverse scripts: exercised, not assumed.
- **Every insert states its classification.** `data_classification` is not
  null with no default precisely so nothing can be seeded without saying what
  it is. That column is the boundary; do not add a default to make seeding
  convenient.

## Unchanged, and not negotiable

- **Invented names throughout.** No real HalalWay business names, addresses,
  staff or figures — and equally, no synthetic location wearing a real name.
  "The Halal Guys — 53rd & 6th" as a synthetic row is the same error in
  reverse.
- **Job A stays deferred.** No real operator data. The `real_identities` gate
  is still false and the backup gates are still untested.
- **Harbor Street Kitchen Group untouched.** It is the published fiction in
  the provenance manifest.
- **No synthetic figure reaches a public surface.** The estate has no public
  surface; keep it that way.
- **Where there is no data, leave it empty.** An empty field is honest.
- Branch `seed/synthetic-estate`. No PR, no merge, no deploy.

## Report

Publish at the checkpoint and again at the end. At the checkpoint I want the
three honest scenarios shown as actual rows with their `outcome_class` and
numbers, and the check demonstrated refusing a mislabelled one — observed
failing, as everything else here has been.
