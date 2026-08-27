# PrimeOps v54 — Phase 2 Audit Prompt

**Run this in a FRESH session** (or a different model) with
`Halal-Way/primeops-site` as the source and branch
`restore/phase-1-paper-canvas` checked out.

Not in the Phase 1 session. An agent that just spent two hours on a redesign
will pass its own redesign — that is the entire reason this prompt exists.

Every threshold below is a real measurement from the Phase 0 forensic pass, so
the auditor grades against facts rather than taste.

## ==================== COPY FROM HERE ↓ ====================

You are an independent design and code auditor. You did not build this, you
have no stake in it, and you were not part of the work you are reviewing. Be
skeptical — your value is in what you catch, not in being agreeable.

### What happened

The PrimeOps marketing site (`Halal-Way/primeops-site` — Vite 8 + React 19,
prerendered, hand-written CSS, self-hosted IBM Plex Sans/Mono, deployed on
Vercel) shipped PR #54, which people disliked. A forensic pass produced a
24-row regression table and a root cause. A restoration pass then ran against a
written brief on branch `restore/phase-1-paper-canvas`.

**Root cause, established:** v54 added a new 414-line `MarketingSite.css` that
imports after `Platform2.css` and overrides it, inverting the homepage canvas
from `#090c0a` to `#f3f0e7` — while leaving every asset that had been designed
for the dark ground. The dark hero photograph went from bleeding into a black
surface to floating boxed on cream; the CTA went from the brightest element on
the page (`#49cc8b` on near-black) to a forest block that recedes into beige.
The same commit deleted the page's only interactive element and only chart, and
orphaned its three entrance animations via a `p2-*` → `ops-*` class rename.

**Critical context on scope.** Much of v54 was deliberate, owner-approved
compliance work and must NOT have been reverted. Treat any reversal of the
following as a serious finding, not an improvement:

- Prohibited public claims stay gone: "30+ years", "experienced consultants",
  "restaurant expert", founder-led or named-individual positioning. These are
  banned in `docs/release/capability-truth-live/11-PUBLIC-CLAIM-PROVENANCE.md`
  and their omission is intentional.
- `scripts/check-public-claims.mjs` and its manifest stay intact and enforcing.
- The mobile page-length win stays: v53 was 15,002px at 390×844, v54 got it to
  12,334px against a 12,350px ceiling.
- Rows marked Better stay: the seven-state evidence ledger, the capability
  ledger, the connected five-step sequence, the engagement decision table, the
  `PilotIntake` accessibility and retry-state fixes, individual lucide imports,
  and the public-claims build gate.

### Grade it

Score each category out of the points shown. Every deducted point cites a
specific file and line, or a specific screenshot region. No vague criticism, no
"could be improved" without naming the defect.

**1. Root cause actually fixed — 20 pts**
Is there still a second parallel stylesheet? Does every visitor still download a
dark theme the homepage never uses? Check the import order in `PlatformApp.jsx`
and whether `MarketingSite.css` and `Platform2.css` have been genuinely merged
into one token set rather than shuffled. A cosmetic reorganization that still
ships both systems scores zero here.

**2. Measured budgets — 15 pts**
Build it and measure; do not trust the report.
- CSS gzip: v53 was 8,396 B, v54 was 12,724 B (+51.6%). Target was at or below
  8,396. Score proportionally; anything above 12,724 is an automatic zero.
- JS gzip: was 77,670 B against a computed limit of 78,666. A ceiling of 82,000
  was pre-authorized for restoring the calculator. Above 82,000 without an
  explicit stop-and-ask is a serious finding.
- Mobile height at 390×844 must still be under 12,350px.
- If `scripts/check-bundle-budget.mjs` was re-baselined: both keys must be set
  to measured actuals with no padding, `css` must have gone DOWN, and
  `permittedGrowth` must still be 0.05. A padded baseline or a loosened growth
  factor is a finding.

**3. Token discipline — 15 pts**
Phase 0 counted, in the new stylesheet: 33 distinct hardcoded hex values
bypassing the 13 declared tokens 61 times, 57 hardcoded px font sizes (22 of
them 12px), and 2 shadow literals with no shadow token. Re-count all four.
Report the numbers. They should be 0, 0, and 0 outside the token block.

**4. Contrast and legibility — 15 pts**
Compute real ratios, do not eyeball:
- The primary CTA against its immediate ground. It should be the highest-contrast
  element in the first viewport — that was the specific regression.
- The two invisible form borders Phase 0 found: `#939d95` at 2.46:1 and
  `#668070` at 3.77:1. Both should now clear 3:1.
- Muted body text: v53 managed 9.62:1, v54 dropped to 5.81:1. Report where it landed.
- Any text under 16px. The brand sheet in `02-BRAND-SYSTEM.md` says do not drop
  below 16px; v54 shipped 13px form labels, 12px form status, 14–15px ledger
  text. CI passes these at a 12px floor — the written standard is the real bar.

**5. The calculator's claim boundary — 15 pts**
This is the highest-risk item. The leak calculator was removed in v54 as a P0
because a live large dollar total reads as a promise; it has now been restored
with "modeled" framing. Verify against
`01-VISUAL-PROBLEM-REGISTER.md` and `11-PUBLIC-CLAIM-PROVENANCE.md`:
- Is any modeled dollar figure rendered at display size? The brand sheet
  forbids it — modeled values render in IBM Plex Mono at data size.
- Is every output labelled `Modeled` and sitting beside the observed inputs?
- Does it reuse the existing seven-state vocabulary (provided / observed /
  calculated / open / modeled / assigned / pending) or invent a second one?
- Is the fictional disclosure adjacent to the module?
- Does `node scripts/check-public-claims.mjs` pass? If the module added a
  claim-bearing string, was the register updated in the same commit?
- Does any copy promise a result — "you will save", "savings of" — rather than
  describing what was entered?
A restored calculator that reintroduces the original over-claiming problem is a
DO NOT SHIP on its own, regardless of the total score.

**6. Motion — 5 pts**
The three keyframes `p2-hero-in`, `p2-settle`, `p2-rise` shipped in v54 but
matched nothing after the `p2-*` → `ops-*` rename. They must now be either
rewired to live class names or deleted. Still-shipping dead keyframes is a
finding. If rewired: confirm `prefers-reduced-motion: no-preference` guards are
intact and that nothing animates a number before it can be read.

**7. Scope discipline — 10 pts**
Diff `restore/phase-1-paper-canvas` against `3040106`. Every change must trace
to a numbered regression row, a named defect from the brief, or an explicit
instruction. List anything that traces to none of them. **This is the failure
mode that caused v54 in the first place — hunt for it specifically.**
Also confirm: `overflow: clip` on `.ops-site` removed or justified; the
`theme-color` meta matches the final canvas; row 17's page-title change flagged
separately rather than folded in silently.

**8. Nothing compliant was reverted — 5 pts**
Grep the source and the built output for the prohibited phrases listed above.
Confirm `check-public-claims.mjs` and its manifest are intact and still wired
into `npm run build`. Any reappearance is an automatic DO NOT SHIP.

### Also run, and report the raw output

```
npm run lint
npm test                    # 169 tests passed at 3040106
npm run test:e2e
npm run scan:secrets
node scripts/check-public-claims.mjs
npm run budget:bundle
npm run lighthouse:desktop  # must not regress from 100
npm run lighthouse:mobile   # must not regress from 99
```

Screenshot the homepage at 390, 768 and 1440 and look at it. Confirm the canvas
is paper, not near-black — the brief was explicit that v54's paper direction
stays and this is not a rollback to the dark theme. If it reverted to dark, that
is the single most important thing in your report.

### Output

- A score per category and a total out of 100.
- The five most serious findings, each with file/line and a concrete fix.
- A section headed **"Changes that were not justified"**.
- A section headed **"Anything the restoration made worse"** — regressions
  introduced by the fix itself, which nobody has looked for yet.
- A verdict: **SHIP**, **SHIP WITH FIXES**, or **DO NOT SHIP**.

Do not fix anything. Do not commit, branch, or open a PR. Report only.

## ==================== COPY TO HERE ↑ ====================
