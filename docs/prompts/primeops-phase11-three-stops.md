# Phase 11 — the three stops, decided

The security review that found six problems in work its own tests had passed is
the most valuable thing produced in this phase. Four fixed, two escalated,
plus two corrections to your own published claims. That is the standard.

Three answers, then one instruction about scope.

## 1. Brand isolation reaching one policy — fold it into `has_location_access`

Option A. Put the brand test inside the helper so all six child policies
inherit it from one place.

This is the same argument that chose the entity over the scoping column, and it
would be incoherent to abandon it now: option B repeats the predicate at every
call site, and the observed-failing test only ever covers the copy someone
remembered to write. You said so yourself when you argued for the entity. Six
call sites is worse than two, not better.

One thing to get right, because you already caught its twin. The backfill that
gave every operator a brand and granted nobody would have locked out every
existing administrator; folding an unconditional brand test into
`has_location_access` is the same trap one level up. So:

- **Owner bypasses brand scoping.** An owner implicitly holds every brand under
  their organisation. This matches what you built for
  `membership_brand_admin_write`, where an owner delegates brands and an admin
  may only pass on one they already hold. Keep the two consistent.
- **Admin and manager must hold an explicit grant.**

I told you earlier not to widen a check constraint eight policies depend on.
This is not that. That was a column constraint being widened in the same change
that introduced the level; this is the helper doing the job the level exists
for. Changing it is the point.

**Observed failing first.** Re-run the same matrix you already measured. Today
it reads `brandb_read f | locb_read t | locb_write t | is_admin t`. The
brand-A administrator's `locb_read` and `locb_write` must flip to `f`, and an
owner in the same organisation must stay `t` on both. Show both rows, before
and after. The owner row is the half that catches the lockout.

## 2. The policies being unreachable — enforce at the RPC layer, report the rest

You are right, and you were right not to write the test. A test that passes
while proving nothing is worse than no test, because it converts an unknown
into a false assurance. This engagement has spent four defects learning that.

Do not re-architect the privilege model to make RLS evaluate. Making the
definer functions invoker-owned, or reassigning them off `postgres`, is a
change to how every caller reaches every table and it is not part of seeding a
test estate. That is a separate proposal with its own review.

For now: **the RPC layer is the enforcement boundary, so test there.** Every
isolation assertion authenticates as a real caller, arrives through the RPC a
real caller uses, and is refused. That is the only path that exists.

Then write the finding up properly, because it is bigger than this task. The
schema is described as having RLS throughout; in fact `authenticated` holds no
privilege on any table, every reader is a superuser-owned definer function that
bypasses RLS even under `force`, and the policies never evaluate for any real
caller. That is not necessarily wrong — a definer function that does its own
authorisation is a legitimate pattern, and yours do — but it means **the
policies are documentation and the helper functions are the enforcement.**
Anyone who reads the policies and believes they are the boundary is mistaken,
and every guarantee rests on helpers being right. Say that plainly, in one
place, where the next person will find it.

That is also the second reason decision 1 goes the way it does: if the helper
is the boundary, there had better be one helper.

## 3. The ledger link — leave them unconnected

Correct to stop. Leave `action_outcome` and `value_ledger_entry` unlinked.

The outcome table already does the job it was added for: the three scenarios
are expressible as ordinary rows, and the check tying `outcome_class` to the
numbers means the application layer cannot label a 42,000-unit loss
"improved". That check is the best thing in the migration — keep it, and keep
the test that catches its removal.

Deriving a ledger entry from a positive outcome changes how existing rows are
written and what existing readers may assume. It is a semantic change to a
table other code sums, and it buys nothing the estate needs today. If it is
ever wanted, it is its own proposal with its own review.

## What does not change, and one thing that does

Unchanged: no seeding until this is done, no PR, no merge, no deploy, Harbor
Street and the marketing site untouched, no real operator data, Job A deferred.

Changed: **stop expanding scope after this.** Four migrations, sixteen tests
and a security review is already more than the brief asked for, and all of it
was warranted. Decision 1 and the write-up in decision 2 close this out. Then
publish and stop — the estate itself is the next phase and it does not start
until you have said this one is finished.

## Two answers you earned

- Your correction stands and is appreciated: 22 migrations on `c502758`, not
  25, and "no executable test rails" was too strong. Correcting your own
  published claims without being asked is the behaviour that makes the rest of
  your reporting worth trusting.
- `c502758` is sanctioned. It is PR #24, opened by Joe on 12 August, and the
  Claude-authored commits are responses to its review findings. The question is
  closed; the three pre-existing failures on it are being raised to Joe
  separately.
