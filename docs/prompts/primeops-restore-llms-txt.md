# Restore `public/llms.txt`

Joe has asked for it back. It was deleted by the capability-truth release
(patch 1/6, Codex, 26 August) alongside the AI-crawler blocks in `robots.txt`.

The exact 38-line, 2,798-byte deleted content is preserved verbatim at
`docs/prompts/assets/primeops-llms.txt.restore`.

## Why it is worth restoring

It was the most explicitly honest public document in the repository, and what it
did was *disclose* rather than claim. It stated that the sample assessment and
portal preview use synthetic data, that estimated opportunities are illustrative
and not guaranteed outcomes, that generated imagery is not customer photography
or endorsement — and it enumerated what the build does **not** represent as
active: provider-backed authentication, customer organisations, row-level
security, encrypted customer storage, MFA, session revocation, private uploads,
audit retention, backup restoration, transactional identity email.

Deleting it removed a public statement of limits. Nothing in the deletion list
justifies it on claim grounds.

## Already verified here

The restored content was run against all twelve `FORBIDDEN` patterns in
`scripts/check-public-claims.mjs`. **No matches.** It will not fail the pattern
half of the claim scan. That is checked, not assumed.

## Three things not to restore blindly

**1. The contact line.** The file says `Contact: support@getprimeops.ai`. The
capability-truth release deliberately split `demo@` (consultation routing) from
`support@` (account, privacy, security). A general product summary probably
still points at `support@`, but confirm that against the split rather than
leaving a line that predates it.

**2. The pointer in `robots.txt`.** The same patch removed
`# Plain-text product summary for LLMs: https://www.getprimeops.ai/llms.txt`.
Restore the file without the pointer and it exists with nothing referring to it.
Restore both or neither.

**3. Staleness — the part that actually matters.** The "Customer account release
state" paragraph asserts that sign-in and account-creation routes are
deliberately closed and lists a specific set of controls as not active. **Verify
every one of those statements against current `main` before republishing.** The
Platform 3 work has moved since 26 August, and a disclosure that has gone stale
is worse than no disclosure — it stops being a limit and becomes a false claim,
which is precisely what the guard exists to prevent. If any line is no longer
accurate, say which and stop; do not quietly reword it.

## A question for Joe, not for you to decide

`llms.txt` is claim-bearing but is **not** in `SOURCE_FILES` or the provenance
manifest — it is only reached through the `dist/` sweep, so it gets the pattern
scan but no human signature. Arguably it belongs in the manifest, since it makes
statements about what the product does and does not do. That would mean Joe
signs its hash. **Recommend it, do not do it.**

## Mechanics

Its own branch cut from `main`, not `seed/synthetic-estate` — this is a
main-side public file and has nothing to do with the estate. Do this **after**
the six scenarios, not interleaved. No PR, no merge, no deploy.

Run `npm run scan:claims` and the build before reporting, and say whether
`llms.txt` appears in the scanned file count.
