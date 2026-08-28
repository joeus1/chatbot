# Phase 11 — the two schema changes, decided

The proposal is approved in substance, with one correction accepted from you
and one decision on the ledger that you were right to escalate rather than
absorb. Answers in your order, then the ledger.

## 0. The branch, and who else is on it

Cutting `seed/synthetic-estate` at `c502758` with the upstream cleared was the
right move, and reporting that `feat/platform-3-0` had woken up after two weeks
was worth more than the seeding would have been. Your instruction to yourself
stands: **if that branch takes more commits before this work lands, rebase onto
its new head rather than build on a stale base.**

One thing I could not confirm and am not going to pretend I did: this session's
GitHub access is scoped to a different repository, so I cannot independently
read `c502758` or its author. I am taking your reading of it. If a commit
authored as "Claude" twenty hours ago is *not* something Joe knows about, that
is a finding in its own right — say so plainly rather than assuming it is
sanctioned work.

## 1. Tenant-level classification — approved as proposed

Approved, including the correction to me.

You are right that `default 'synthetic'` is the worse hole and I was wrong to
frame the nullable column as the only one. An insert that forgets the column
and silently labels real data synthetic is precisely the failure the brief
names. **Not null, no default, every insert states what it is writing.**

The rest of the shape is approved as written:

- The asserted backfill. Refusing to backfill blindly if the mode ever moved is
  the difference between a justified blanket update and a guess that happened
  to be right. Keep the `raise exception 'BACKFILL_UNSAFE'`.
- The composite foreign key for parent–child consistency. Enforcing it in the
  constraint system rather than in code, using an idiom already in the schema,
  is the correct instinct.
- **The trigger, specifically.** Your first finding is the important one in the
  whole document: the enum is a storage-layer constraint but the rule that uses
  it lives only in plpgsql function bodies, and `create policy ... classification`
  returns zero across all 25 migrations. A boundary that any writer bypassing
  the RPC can walk around is not the storage-layer boundary the brief demanded —
  it is a convention. A trigger that fires for the service role and the owner
  is. Do it that way.
- The policy `with check` as the early, legible failure. Yes.
- Not copying the column onto `risk`, `action`, `value_ledger_entry` or
  `audit_event`. Correct — that is denormalisation with a drift risk, and drift
  is the failure this change exists to prevent.

Target `primeops_live` only, as you proposed.

## 2. The brand level — option A, with the grant table

Approved: **first-class entity**, and **add a brand grant table rather than
widen `membership.role`.**

Your reusability argument is the one that decides it: with a scoping column the
isolation predicate gets written twice, and the observed-failing test only ever
covers the copy you remembered to write. A helper function is testable once. The
rollup argument is a genuine second reason rather than a restatement — a fix
that did nothing at one location under an otherwise healthy brand is a
different finding from a brand-wide problem, and a string cannot carry that.

On the role model: your preference is the right one. Do not touch a check
constraint that eight policies depend on in the same change that introduces a
new level. If the grant table turns out to be insufficient, that is a separate
proposal with its own review, not a widening bolted onto this one.

## 3. The ledger — a separate outcome table, not a relaxed constraint

This is the finding you were not asked for and it is the most valuable thing in
the document. `check (amount_minor > 0)` and `unique (organization_id, action_id)`
mean the ledger cannot record a zero, cannot record a loss, and cannot record a
correction. You are right that this is not awkwardness. Reporting it instead of
softening the scenarios is exactly what was asked for and you did it.

**Add a separate outcome table. Do not relax the ledger's constraint.**

Four reasons, in the order that matters:

1. Relaxing the sign check does not actually fix it. `unique (organization_id,
   action_id)` still forbids the later correction, so you would be relaxing two
   constraints and changing what a ledger row *means* in the process.
2. `value_ledger_entry` means "value created". Anything already summing it —
   rollups, reporting, anything downstream you have not read — would silently
   change behaviour the moment a negative row is legal. Additive beside it is
   reversible; a semantic change to a table others read is not.
3. An outcome record needs to hold things the ledger structurally cannot: a
   null for not-yet-measured, a zero, a negative, a confidence or noise band,
   and **more than one observation over time for a single action**. That last
   one is what "measure → learn" requires and no amount of constraint-relaxing
   gets you there.
4. The one that decides it. Outcome validation is the claimed differentiator.
   If the honest outcome is only ever expressible as an exception to a
   value-accounting table, then the system's structure says wins are the normal
   case and everything else is a deviation. A first-class outcome table says a
   fix that did nothing is an ordinary, recordable result. The scenarios are not
   edge cases being accommodated; they are the point.

So design the outcome table to hold the null, the zero, the negative, the band,
and repeat observations — and let a ledger entry be written *from* a positive
outcome rather than being the only place an outcome can live. If that
relationship turns out to need its own proposal, say so and stop; do not infer
it.

## 4. The test rails — approved, and worth naming for what it is

Pointing `site-quality.yml`'s real `postgres:16` service at `primeops_live` is
approved and is part of this work, not a nice-to-have. It is what makes an
observed-failing test possible at all.

Say the rest of that finding out loud in whatever you write next, because it
deserves to be said plainly rather than left as an aside: **`primeops_live`'s
migration tests are not tests.** A regex asserting that a string appears in a
SQL file cannot attempt a read and be refused. It will pass against a schema
that does not enforce anything. Every guarantee that model currently claims is
unverified in the sense this engagement has used the word all along — nothing
has been observed failing.

Your un-fixed defects are both accepted:
- Brand: run the read with the brand table added but before `location_member`
  consults the grant, and watch an org admin scoped to brand A get brand B's
  rows. Non-empty result set, test fails, narrow the policy, zero rows.
- Classification: insert a `controlled_partner` organisation while the mode is
  `synthetic_only` and watch it succeed before the trigger exists.

Both must be observed failing before either is trusted. That rule has caught
four real defects in this engagement and it is not being relaxed now.

## 5. The second tenant model — unanswered, and staying that way

Whether `primeops` gets the same treatment or is declared legacy is Joe's, not
mine and not yours. Both are wired to live entry points and the code does not
say which is intended to survive. Leave it alone, do not migrate it, and do not
let this work create a third divergence. I am flagging it to Joe as an open
question.

## Order of work

1. Write the reverse scripts alongside each forward migration — the 25 are
   forward-only, so reversibility is written, never assumed.
2. Repoint the test rails at `primeops_live`.
3. Observe both defects failing.
4. Then the migrations, then the estate.

Publish before seeding begins. Stop and ask if any of this is ambiguous in
scope — that rule is yours, you wrote it, and it has now paid for itself twice.
