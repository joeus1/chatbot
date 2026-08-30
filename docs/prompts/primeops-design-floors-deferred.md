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
- **`merge/platform-3-0` (head `ab49895`) stays red and therefore unlandable.**
  `check-design-rules` fails with 184 findings and Playwright desktop has 6
  failures. Deferring does not make that branch mergeable; it means the branch
  waits. Anyone who reaches for "merge it anyway, the floors are deferred" has
  misread this decision.
- The parked exploratory work — mapping 118 literal values onto 18 existing
  tokens plus 66 new ones, and contrast floors 1–3 — was stopped mid-flight on
  2026-08-30 at Joe's instruction and left in place on `merge/platform-3-0`.
  Nothing was pushed, reverted or tidied. It is a head start, not a commitment.

## Open, and still Joe's

Recorded here so the deferral does not swallow them:

- The provenance signature on `src/platform2/routes.js` is the agent's, not
  Joe's. Reverting that one file makes `npm run scan:claims` fail again naming
  the same hash, if he would rather sign it himself. The same applies to both
  release digests on `fc50c52`.
- One exclusion was widened during the first run: the type-floor scan now skips
  `.p3-sr-only` as well as `.p2-sr-only` (572 → 490 offenders). It is the same
  clip pattern byte for byte, and screen-reader-only text is not rendered text —
  but it is still an exclusion, and the gate fails either way, so it can be
  reversed without changing any verdict.
