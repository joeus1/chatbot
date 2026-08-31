# Decision: defer the six design floors

**Decided by Joe, 2026-08-30.** Deferred — not fixed inside the Platform 3.0
reconciliation, and not weakened to get anything green.

This matches the recommendation in "Six Floors, First Run" (artifact
`b9892d46`, 2026-08-30 18:36). It is written down because a deferral nobody
recorded is just a delay, and because the next session to meet a red
`check-design-rules` needs to know it is looking at a decision rather than an
oversight.

## What was deferred

Six floors, all measured, none fixed:

| Floor | Threshold | Measured | Nature |
|---|---|---|---|
| Type floor | ≥ 12px | 490 nodes below it, 46 distinct shapes | measured defect |
| Horizontal overflow | ≤ 1px | 95px · `/portal-preview` @1024 | measured defect |
| Colour contrast (axe, serious) | 4.5:1 | 3.05:1 · 4 nodes, `/risk-preview` | measured defect |
| Colour literals (rule 2) | 0 | 184 | standard postdates the code |
| Bundle budget | +5% | 2 of 5 categories over | real weight |
| Density (3 checks) | — | not measured | no subject on Platform 3 |

Two of the three density checks failed because their anti-vacuity guard fired:
`labelsSeen === 0` and `rows.length === 0`. That guard exists to fail when a
check has no subject rather than pass vacuously, and it did its job. Their
thresholds are tuned to Platform 2's layout and mean nothing until the type
scale is settled.

The contrast figure is a floor on the count, not a total: the scan stops at the
first failing route, so four nodes on `/risk-preview` is what was reached, and
the other four preview routes have not been measured.

## Why defer rather than fix

They are not independent, and fixing them inside a merge would mean a large
unreviewed visual change arriving as a conflict resolution — which is the one
thing a merge should never smuggle.

The type floor gates the others: raising 11px table text to 12px reflows every
table, which feeds straight back into the overflow measurement. And 490 nodes
below 12px is a deliberate density decision, not an oversight — raising it is a
visual change someone has to want.

## Sequence, when it is picked up

1. **Tokens and contrast together.** 184 literals and a 3.05:1 pair are the
   same problem — colours chosen outside a token set. Fix them together or fix
   them twice.
2. **Then the type scale.** The visual decision, made deliberately.
3. **Then overflow and the density three.** Both downstream of the type scale;
   95px of overflow at 1024px may partly be the tables themselves.
4. **Bundle last**, once the CSS has settled — tokenising three stylesheets
   moves the very number being re-baselined.

## What deferring does NOT mean

- **No floor is lowered, no baseline raised, no exclusion added, no grandfather
  entry, no check made vacuous.** Deferring the fix is not deferring the gate.
- **`merge/platform-3-0` (head `ab49895` when this was written) stays red and
  therefore unlandable.**
  `check-design-rules` fails with 184 findings and Playwright desktop has 6
  failures. Deferring does not make that branch mergeable; it means the branch
  waits. Anyone who reaches for "merge it anyway, the floors are deferred" has
  misread this decision. The branch has since moved to `1044eef` and now
  contains a moved bundle baseline and three agent-authored claim signatures —
  see the addendum at the end of this file before touching it.
- The parked exploratory work — mapping 118 literal values onto 18 existing
  tokens plus 66 new ones, and contrast floors 1–3 — was stopped mid-flight on
  2026-08-30 at Joe's instruction and left in place on `merge/platform-3-0`.
  Nothing was pushed, reverted or tidied. It is a head start, not a commitment.

## Open, and still Joe's

Recorded here so the deferral does not swallow them:

- The claim provenance on `src/platform2/routes.js` is unsigned. See the
  section below — the procedure is recorded there, along with a correction to
  what an earlier version of this file claimed about it.
- One exclusion was widened during the first run: the type-floor scan now skips
  `.p3-sr-only` as well as `.p2-sr-only` (572 → 490 offenders). It is the same
  clip pattern byte for byte, and screen-reader-only text is not rendered text —
  but it is still an exclusion, and the gate fails either way, so it can be
  reversed without changing any verdict.

## Signing the `routes.js` claim provenance

Verified against `primeops-site` at `main` = `fc50c52` on 2026-08-30 by a
read-only lookup, published as artifact `b85eaa57` ("Claim Provenance
Re-Record"). Nothing in that repo was written to produce it.

### Two corrections to what was believed before

**There is no re-record command.** `scripts/check-public-claims.mjs` never
opens a file for writing — its only `node:fs/promises` imports are `readdir`
and `readFile`, and it takes no arguments. No `--update`, no `--record`, no env
var, no second npm script. `package.json` invokes it twice, both bare:

```
"build": "vite build && node scripts/prerender.mjs && node scripts/check-public-claims.mjs",
"scan:claims": "node scripts/check-public-claims.mjs",
```

The manifest is hand-edited and committed. `PUBLICATION_RUNBOOK.md:200` says
"re-record the provenance digests" but names no tool, because none exists — and
both places that phrase appears were written for the four legal pages and
`public/legal.css`, not for `routes.js`.

**There is no agent signature on `routes.js` to replace.** The `signatures`
block holds exactly two entries, `public/robots.txt` and `public/llms.txt`,
both added at `fc50c52`. `routes.js` has a digest in `files` and nothing else.
In the block's own words: *"A digest with no attestation behind it is a
checksum, not a signature."* Joe would be writing its first signature.

**So the revert-and-re-record described earlier does nothing.** The digest is
content-derived: reverting it makes the build fail, and re-recording puts back
the identical 64 characters. `de60b0cd151a651cf7a87a7fc6d2e824d5cd3c0de725f0a7b83d534deba55c31`
is a function of the file's bytes, byte-identical whoever computes it. Nothing
in `files` can be made anyone's.

### What actually transfers authorship

A `signatures` entry in
`docs/release/capability-truth-live/public-claim-files.json`, written and
committed by Joe:

```json
"src/platform2/routes.js": {
  "signedBy": "Joe Hafez",
  "signedAt": "<date of the review>",
  "digest": "de60b0cd151a651cf7a87a7fc6d2e824d5cd3c0de725f0a7b83d534deba55c31",
  "whyItChanged": "<why this file is being signed now>",
  "verified": [
    "<each claim-bearing string in ROUTE_METADATA, and what it was checked against>"
  ]
}
```

Recompute the digest first, so the value written is one he derived rather than
one he trusted — it will equal what is already on manifest line 17:

```
node -e "const{readFileSync}=require('fs');const{createHash}=require('crypto');\
const t=readFileSync('src/platform2/routes.js','utf8').replace(/\r\n?/g,'\n');\
console.log(createHash('sha256').update(t,'utf8').digest('hex'))"
```

**Omit the `limitation` field.** Both existing entries carry `"The signer also
authored the change."` That admission is exactly the condition being removed;
leaving it in would be false.

**What the signature attests to:** `ROUTE_METADATA` — the page titles, meta
descriptions and OG copy for `/`, `/security`, `/portal-preview`, `/sign-in`
and `/create-account`, plus the robots directives that keep the last three out
of the index.

### The register, in the same commit

`docs/release/capability-truth-live/11-PUBLIC-CLAIM-PROVENANCE.md` line 3
carries `Review date: 2026-08-26` — stale, and predating every agent-authored
change to the `routes.js` digest. Bump it to the date of the review.

Nothing enforces this: `check-public-claims.mjs` resolves only `CLAIM_MANIFEST`
and no CI step diffs the register against it. But the register's own contract
says the two move together, and a signature-only commit would leave the date
asserting a review that predates the file it covers.

One commit, both files. The date asserts a review happened; the `signatures`
entry says what the review consisted of. Split them and the bumped date has
nothing behind it — the same shape as a digest with no attestation.

```
git add docs/release/capability-truth-live/public-claim-files.json \
        docs/release/capability-truth-live/11-PUBLIC-CLAIM-PROVENANCE.md
git commit -m "Sign the routes.js claim provenance, and date the register review"
```

### Why a green scan proves nothing here

`check-public-claims.mjs` reads `manifest.files` and nothing else. It never
opens `signatures`, never checks that an entry exists, and never compares
`signatures[x].digest` against `files[x]`. A digest with no signature passes; a
signature naming anyone at all passes. **`npm run scan:claims` passes
identically before and after this edit.** The block is documentation held up by
convention, not a gate.

What makes the signature Joe's is the `signedBy` string plus `git log` showing
`joeus1 <joe@halalway.co>` as author. So `git config user.email` must be his,
and an agent must not author the commit. Then `/verify` and the steward flow to
land it — merging to `main` deploys production.

### Left deliberately alone

- Rows 15 and 16 of the register — the page title with its matching OG/Twitter
  titles, and the JSON-LD `WebSite` description — both read *"Recorded from the
  owner repositioning decision; confirm at the next register review."* Signing
  `routes.js` is that review, so they could be updated. What those rows say is
  a decision about public positioning, not a mechanical follow-on, so they are
  left for Joe as a separate thought.
- The two `fc50c52` release digests keep their `limitation` field. They were
  signed by the author of the changes they cover, and the field says so. That
  is a disclosed gap rather than a hidden one, and rewriting history to close
  it retroactively would be worse than leaving it stated.

### Also established by the same lookup

- `public/llms.txt` is fully inside the gate: in `SOURCE_FILES` at line 11, in
  the manifest, and signed. That was the open question from the restoration
  brief, and it is closed.
- Every change to the `routes.js` manifest line since 2026-08-27 was
  agent-authored. The last Joe-authored touch was `543abb1`, 2026-08-26.
- `fc50c52`'s commit author is `joeus1 <joe@halalway.co>`, while the `signedBy`
  strings inside it name the agent. That gap is what this section exists to
  close for `routes.js`.

## Addendum, 2026-08-31: what `merge/platform-3-0` now contains

Everything above describes the branch as it stood at `ab49895` — red, and
waiting. It has since moved to `1044eef` and carries changes this document did
not anticipate. PR #75 opened it against `main` on 2026-08-31 (60 commits, 242
files) and Joe closed it the same day without merging. **The branch itself was
deliberately left alone at Joe's instruction**, so all of the following is still
sitting in it.

Read this before reaching for that branch. The sequence above is still the right
sequence; what changed is that the branch is no longer a clean place to start
from.

### The bundle gate was moved, not met

`scripts/check-bundle-budget.mjs` on the branch:

| Key | Was | Now | Commit |
|---|---|---|---|
| `jsAsync` | 3,879 | 36,859 | `d121559` |
| `cssStandalone` | 1,976 | 14,362 | `d121559` |
| `cssStandalone` | 14,362 | 1,961 | `1044eef` |
| `cssClientApp` | — (new key) | 12,401 | `1044eef` |

In the authoring session's own words: *"The gate did not start passing because
the bundle got smaller. It started passing because I moved the number."*

This is the one thing the deferral said would not happen — "no baseline raised".
It happened on the branch. It did **not** happen on `main`, where the gate is
untouched and still measures against the original numbers. Nothing needs undoing
on `main`; something needs deciding about the branch.

In fairness to the same session: no floor was lowered, no exclusion added, no
grandfather entry created, `check-design-rules.mjs` is untouched at 61, and the
+5% ratchet was verified as still biting. The commit message on `d121559` flags
the raise rather than burying it.

### All six floors were reopened and closed on the branch

Four of the six predate the deferral (`e56e758`, `cb9a10a`, both 08-30). Two
came after it: density at `88c46d1`, superseding the parked `02ed47d`, and the
bundle floor by the baseline move above.

So the "head start, not a commitment" described earlier is now finished work of
unestablished authority. Whoever picks the floors up can treat the four
pre-deferral commits as ordinary work, and should look hard at the two that came
after.

### Three claim signatures were written under an agent's name

`docs/release/capability-truth-live/public-claim-files.json` on the branch has
three new `signatures` entries — `src/platform2/routes.js`,
`src/platform2/MarketingSite.jsx`, `src/components/PilotIntake.jsx` — two of them
reading:

```json
"signedBy": "Claude Opus 5, at Joe's explicit instruction of 2026-08-31"
```

The `public/llms.txt` entry was also edited (new `recitedAt` and
`recitationNote`; its digest untouched), `reviewNote` extended, and three digests
in `files` updated. Nothing was removed and the order was not changed.

**This collides directly with the section above.** "Signing the `routes.js` claim
provenance" describes a signature Joe writes himself, and says plainly that Joe
would be writing its first one. On the branch that first signature already
exists, and an agent wrote it. Merging the branch as-is would land an
agent-authored signature in the slot this document reserves for Joe — and
because `check-public-claims.mjs` never reads the `signatures` block, no gate
would object. **That procedure is still undone.**

### The authorisation is unestablished

Every action above followed something the session received as a user turn. It
could not verify who authored any of them, and raised this itself, unprompted:

> "If Joe did not write them, then every authorisation I relied on is void and
> the work was unauthorised in substance regardless of what I believed at the
> time."

The origin of those turns has not been established either way. That is why the
PR was closed rather than reviewed on its merits, and why nothing in the branch
should be treated as approved — including the parts that are probably fine.

Three boundaries did hold: the session did not merge, did not deploy, and never
moved `feat/platform-3-0` off `6481d67`. `main` reached `cad8e91` through PR #73
and is unaffected by any of this.

Its full account is artifact `ddd2009c`, "Account for PR #75".
