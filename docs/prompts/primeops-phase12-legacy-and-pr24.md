# Phase 12 — `primeops` is legacy, and PR #24 gets fixed

Two decisions from Joe. **Begin only after you have published the Phase 11
close-out and said it is finished.** The instruction to stop after that phase
stands; this is the next unit, not an extension of the current one.

## 1. `primeops_live` is the future. The self-hosted `primeops` is legacy.

Joe has decided. Record it, freeze it, and plan its removal — but do not remove
it in this pass.

What this needs:

- **A written decision record**, in whatever form the repo already uses for
  them, naming `primeops_live` as the surviving tenant model and the
  self-hosted `primeops` as legacy. State what legacy means concretely: no new
  features, no schema additions, security fixes only, and removal once its
  entry points are gone.
- **An inventory of what still reaches it.** `scripts/db-migrate.mjs`,
  `api/_lib/platform-db.js` and `database/migrations/001_pilot_core.sql` are
  the ones already found. Find the rest. A model cannot be retired until the
  list of things pointing at it is known and finite — write the list down even
  where you cannot yet cut the wire.
- **Do not delete anything, and do not migrate data.** Retirement is its own
  piece of work with its own review.

**The part that actually matters, and the reason this was not a free
decision.** `site-quality.yml` stands up a real `postgres:16` and runs the only
genuine integration isolation test in the repo — *against the model now being
retired.* If nothing changes, CI's one real isolation guarantee will be
guarding a corpse while the surviving model is covered only by the rails you
built this phase.

So: **repoint or retire that job.** Your sixteen tenant-isolation tests against
`primeops_live` are the replacement. Before you delete or disable anything,
show that the new tests cover what the old job covered — and where they do not,
say so plainly rather than dropping coverage quietly. Losing a real test in the
course of declaring its target legacy would be the worst possible outcome of
this decision.

## 2. Fix all three failures on PR #24

Joe is the author of PR #24 and has explicitly asked for all three fixed.

**This reverses an earlier instruction and I am saying so explicitly, so you do
not have to guess.** I previously told you not to commit to
`feat/platform-3-0` because it was someone else's working branch. That
constraint is lifted for these three fixes only, by the branch owner. Nothing
else about that branch is open — no merge, no deploy, and no unrelated changes
riding along.

The three:

1. **`primeops_health()` reports `20260814066000`** while the newest migration
   is `20260814068000`. Bump the constant.
2. **`private_tables` expects 31; the branch has 32.** Correct it to 32.
3. **`tenant_deletion_approval` has RLS neither enabled nor forced.** Move the
   separable migration you already wrote (`20260828185900`) onto PR #24's
   branch. That is what you kept it separable for.

**Two traps in doing this, in the order you will hit them.**

The first is a sequencing trap of your own making. If you bump
`primeops_health()` to `20260814068000` and then add `20260828185900` in the
same PR, the check fails again on the newer migration you just introduced. The
constant must end up naming the newest migration *after* your addition, not
before it. Do the arithmetic in that order and prove it by running the
validator on the final tree, not on an intermediate one.

The second: `private_tables` is 32 on `feat/platform-3-0` and 35 on
`seed/synthetic-estate`, because your `brand`, `membership_brand` and
`action_outcome` tables have not landed there. **Set it to 32, not 35.** It
becomes 35 when the seed work lands, and that bump belongs to that change.
Setting it to 35 now makes CI green on a tree that does not have those tables,
which is a check that passes while proving nothing — the thing you refused to
build last phase.

**Then reconcile the branches.** Once `20260828185900` is on
`feat/platform-3-0`, `seed/synthetic-estate` carries a duplicate. Rebase the
seed branch onto the new head and drop the now-redundant commit. You said you
would rebase rather than build on a stale base if that branch moved; it is
about to move because of you.

## Verification

Run the repository's own validator on the final tree of each branch, and report
the "prove closed state" step going from failing to passing with the actual
output. Not an assertion that it should pass.

## What does not change

No seeding. No estate. No real operator data — Job A stays deferred. Harbor
Street and the marketing site untouched. Publish when done, and stop.
