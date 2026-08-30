# Phase 11 — the three blockers, answered

You stopped and asked instead of proceeding. That was correct, and it is the
first time the scope rule you wrote in Phase 10 has been exercised by the
session that wrote it. The survey is also better work than the seeding would
have been: you found that Platform 3.0 already implements the storage-layer
synthetic boundary the brief demanded, and you said so plainly instead of
claiming you had designed it. Keep that standard.

Three answers, in the order you asked them.

## 1. Which branch owns this — `feat/platform-3-0`

You are right that JSON fixtures on `restore/phase-1-paper-canvas` would
produce exactly the presentation-only boundary the brief forbids, and right to
refuse to build it. The restore branch is finished; it is a marketing site and
it has no database. It has nothing to do with this work and you should not
touch it again for this job.

Cut a new branch from `origin/feat/platform-3-0` named `seed/synthetic-estate`
and work there. The branch-only instruction restates unchanged and now applies
to that branch: **no PR, no merge, no deploy.** Do not commit directly to
`feat/platform-3-0` either — it is someone's working branch, not yours.

Before you start, check whether `feat/platform-3-0` has moved since your survey
and whether anyone else is committing to it. If it is actively moving, say so
rather than silently branching from a moving target.

## 2. The two schema changes — propose, do not write

Write the proposal. Do not write a migration, and do not write one "ready to
apply pending approval" either — a migration that exists is a migration that
gets run.

The proposal covers both changes in one document:

**Tenant-level classification.** You found `data_classification` on the
evidence tables and absent from `organization` and `location`. Propose adding
it, and be specific about the enforcement, not just the column: which policies
change, how the `CUSTOMER_DATA_DISABLED` function extends to cover tenancy
rows, and what happens to rows that exist today with no classification. A
nullable column with no default is a hole; say how you would avoid one.

**The brand level.** Do not assume a third table is the answer. The brief said
operator → brand → location because that is HalalWay's shape, but the
requirement is *isolation* — brand A must not be able to read brand B under one
operator — and isolation can be delivered by a first-class entity or by a
scoping column with a policy behind it. Argue both, recommend one, and say what
the isolation test looks like under each. Whichever you recommend, the test
must be observed failing before it is trusted; describe the un-fixed defect you
would run it against.

Also state what the proposal *costs*: 25 migrations exist, and anything you
propose has to be reversible and has to not break what is already live behind
Supabase RLS.

Publish the proposal as an artifact. I will read it and decide before anything
is written.

## 3. Real operator data — out of scope, for now

No. Job A is deferred and you should not seed the eight real locations.

Your own finding decides it: `real_identities` is false, and the constraint
that guards it requires a tested `isolated_restore`, which is also false.
Someone built that gate deliberately. The correct response to a deliberate
safety control is to satisfy it or wait, never to route around it because the
task would be easier without it. There is no tested restore path today, so
real operating data would be going somewhere it cannot be recovered from. That
alone settles it, before the personal-data question about staff is even
reached.

So: **do not create the four brands or the eight locations as real tenants.
Do not put HalalWay's real business names, addresses, staff, or figures into
any table.** The estate you build is synthetic and it uses invented names.
Naming a synthetic location "The Halal Guys — 53rd & 6th" is real data wearing
a synthetic label, which is the same error as the reverse and equally
forbidden.

Job B proceeds alone once the schema questions are settled, exactly as you
said it could.

## What does not change

- **Harbor Street Kitchen Group stays untouched.** It is the published
  fiction, registered in the provenance manifest. Leave `marketingContent.js`
  alone entirely.
- **No synthetic figure may reach a public surface.** The site is live and
  correct at `47c0cb58`. Nothing you do here goes near it.
- **Scenarios 5, 6 and 7 survive as specified** — the fix that did nothing,
  the fix that made things worse, the outcome inside the noise band. They are
  the reason this is a test harness and not a demo. If the schema work makes
  them awkward to express, that is a finding to report, not a reason to soften
  them into successes.
- **Where you do not have data, leave it empty.** An empty field is honest.

## Order of work

1. Confirm the branch state and cut `seed/synthetic-estate`.
2. Write and publish the schema proposal. Stop there.

Do not begin seeding on the assumption the proposal will be approved.
