# Phase 14b — the remaining six scenarios

The checkpoint cleared. Joe has asked for the rest.

## The bar the six have to meet

The three honest rows are now the reference standard, and the risk has inverted.
Before, the danger was softening a failure into a success. Now it is building
six successes that are *less rigorous* than the three failures — a `no_change`
row with a measured band beside an `improved` row that just asserts itself.

So: **every one of the six carries the same evidence the three do.** A band
established the same way, over a comparable period, with the class earned by
the numbers rather than chosen for the story. An `improved` outcome with no
band is exactly as dishonest as a `no_change` with an invented one.

If a scenario genuinely cannot carry a band — if it is the kind of result that
has no measurable comparison — then it is `inconclusive` with a null band, like
Threadneedle, and it says so. Do not manufacture a band to make a row look
finished.

## Before you build: say what the six are

List the six as you understand them from the original brief, in one line each,
before writing any of them. If any looks unbuildable, wrong, or redundant now
that the schema exists, say so then rather than after. I do not have the
enumeration in front of me and I would rather find a mismatch in a list than in
a seeded table.

## Scope — reuse the estate, do not grow it

Same two operators, three brands, five locations. The six new scenarios attach
to the estate that already exists.

If one of them genuinely needs a shape that isn't there — a third operator, a
brand with one location, a location with no manager — **name it and say why**,
and I will widen deliberately. Growing the estate quietly to make a scenario fit
is the drift the bound exists to prevent.

## Carry the properties forward

- **The round trip must still hold at nine.** `synthetic-estate.mjs verify`
  prints every table at down / up / up-again / down. Nine scenarios must return
  every table to zero, not just the three. A teardown that was correct at three
  rows and leaks at nine is the class of thing you caught in the reverse chain.
- **Determinism and idempotency survive.** Derived v5 UUIDs, not generated ones.
- **Every insert states its classification.** And specifically: you found that
  `evidence_object` and `evidence_scan_job` already carry
  `NOT NULL DEFAULT 'synthetic'`. If any of the six touches those tables,
  **state the classification explicitly anyway.** Relying on that default is
  precisely the convenience the finding is about, and doing it in the same
  change that reports it would be a poor look.
- **Re-run the rename matrix across all nine**, not just the original three,
  and re-run it against the check-removed schema. Five refusals on three rows
  proved the check works on those rows; the point is that it works on every row.

## Unchanged

Invented names only, no real HalalWay names or figures, no synthetic row wearing
a real name. Harbor Street untouched. Job A deferred. No public surface. Where
there is no data, leave it empty. Branch `seed/synthetic-estate`. No PR, no
merge, no deploy.

## If you need a schema change, stop

The migrations are settled at 27. If one of the six cannot be expressed without
altering the schema, **stop and say which and why** rather than adding a
migration to make a scenario fit. That was the rule for the first three and it
is the rule for these.

## Report

Publish when all nine are in. Show the six as stored rows with their classes,
amounts and bands, the way the three were shown. Full round trip at nine, the
rename matrix across all nine, and the gauntlet.
