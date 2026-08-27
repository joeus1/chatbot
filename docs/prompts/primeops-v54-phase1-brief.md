# PrimeOps v54 — Phase 1 Brief

Paste into the Phase 0 session (`session_018MoDCvgDXmmjHhkTsRrGNX`), which
already holds the repo, the diff, and the regression table.

Decisions made by Joe on the Phase 0 dossier:
- **Calculator: restore, with modeled framing.**
- Everything the dossier marked **Better** stays. All compliance work stays.

## ==================== COPY FROM HERE ↓ ====================

Phase 0 is approved. Your regression table stands, including the four
corrections to my brief — thank you for those; the font and Tailwind
hypotheses were mine and they were wrong.

Two decisions are now made:

1. **Restore the calculator, with v54's modeled/observed state language
   applied.** Your reasoning is accepted: the fix for an over-claiming number
   is to reframe the number, not to delete the page's only interaction.
2. **Everything you marked Better stays.** Rows 10, 12, 13, 15, 18, 19, 20, 21
   and the mobile page-length win are not in scope for restoration.

### The rule still holds

Restore first, improve second, never improve by inventing. Every change traces
to a numbered row in your regression table, to one of the named defects below,
or to an explicit instruction here. If you find something you believe should
change that fits none of those, raise it — do not just do it.

### Do NOT touch

- v53's consultation copy. "30+ years", "experienced consultants",
  "restaurant expert", founder or individual-expert framing stay gone. They are
  prohibited in `11-PUBLIC-CLAIM-PROVENANCE.md` and their omission is
  deliberate.
- `scripts/check-public-claims.mjs` and its manifest. Keep the gate; if your
  work changes a claim-bearing file, update the register in the same commit
  rather than weakening the check.
- The mobile page-length win. 12,334px is inside the 12,350px ceiling. Whatever
  you restore, the page does not go back over it. If restoring the calculator
  pushes it over, cut length elsewhere and say where.
- The seven-state evidence ledger, the capability ledger, the connected
  five-step sequence, the engagement decision table, the form accessibility
  fixes, the individual lucide imports.

---

## The work, in dependency order

### 1. Collapse the two design systems into one — row 02

This is the root cause and everything else is easier after it. Right now
`MarketingSite.css` (414 lines) imports after `Platform2.css` and overrides it,
so every visitor downloads a dark theme the homepage never uses (+51.6% CSS).

- One stylesheet, one token set, one canvas decision.
- The homepage canvas stays **paper** — v54's direction is approved, and this is
  not a rollback to dark. What is being fixed is that the assets were never
  re-made for it.
- Any dark surface that survives (header band, anchors, portal preview) is a
  deliberate token, not a leftover.
- **Target: CSS gzip back at or below the v53 figure of 8,396 bytes.** You are
  deleting a duplicate system, so this should be achievable. Report the number.

### 2. Fix the token bypass you found — §06

In the same pass, because it is one release old and will calcify:

- **33 hardcoded hexes** → tokens. The file declares 13 and bypasses them 61
  times.
- **57 hardcoded px font sizes, 22 of them 12px** → a single shared type scale.
  Use the scale already written in `02-BRAND-SYSTEM.md`: display 64/68 desktop
  and 42/46 mobile, H2 44/48 and 32/36, H3 22/28 and 20/26, body lead 20/31 and
  18/28, body 17/27 and 16/25, label mono 12/16 and 11/15, data mono 13/19 and
  12/18.
- The brand sheet says "do not drop below 16px" and v54 sets 13px form labels,
  12px form status, 14–15px ledger text. **Bring those to the sheet's own
  floor.** CI passes them at a 12px automated floor; the written standard is the
  higher bar and it is the one that matters.
- Adopt a shadow token; remove the two literals.

### 3. Re-anchor the hero for the canvas it actually has — rows 04, 05, 06

The photograph and the CTA were designed for near-black and were never redone
for cream. Fix them **for paper**, not by reverting to dark.

- **The photo.** A dark kitchen still boxed on cream reads as a heavy floating
  rectangle. Options in order of preference: (a) full-bleed it to the viewport
  edge again so it terminates the composition rather than floating in it;
  (b) sit it on a dark anchor block so the image and its ground agree;
  (c) replace it with the approved fictional Harbor Street review as the hero
  visual. Option (c) is the strongest — it puts product truth in the most
  valuable space on the site and it is already an approved illustrative example
  — but it interacts with item 4, so decide after you have the calculator
  working and tell me which you chose and why.
- **The CTA must be the highest-contrast element on the page again.** Forest on
  beige recedes. Find the paper-canvas equivalent of what mint-on-black did.
  Measure it: the primary CTA should have the highest contrast ratio against
  its immediate ground of anything in the first viewport.
- Keep the "Illustrative operating scene" disclosure — it is required. Make it
  a quiet caption, not a headline-adjacent apology.

### 4. Restore the calculator, with modeled framing — rows 08, 09

Bring back `SampleAssessment` and `OpportunityChart` to the homepage. The
interaction is the point: it was the only reason to touch the page.

**The framing rules, drawn from the claim register and the brand sheet:**

- **Never a single large dollar total as the hero of the module.** The brand
  sheet is explicit: *never use display size for a modeled value.* The output
  renders in IBM Plex Mono at data size, not display size.
- **Every output is labelled `Modeled`** and sits beside the observed inputs it
  came from. The seven-state vocabulary v54 introduced — provided, observed,
  calculated, open, modeled, assigned, pending — already exists in the evidence
  ledger. Reuse it here; do not invent a second vocabulary.
- **Show a range, not a point estimate**, or show the arithmetic. "Based on the
  figures you entered" — never "you will save".
- **The fictional disclosure sits adjacent to the module**, per the register's
  requirement for the Harbor Street example.
- **No prohibited phrasing.** Run `check-public-claims.mjs` before you consider
  this done, and if the module adds a claim-bearing string, add it to the
  register in the same commit.
- Keep the `aria-live` region on the computed output and the analytics
  engagement event.
- The chart keeps what it already did right: bars measured from zero against
  `Math.max(...drivers, 1)`, money through `fmtMoney`.

**On the JS budget — measure before you build.** You reported 996 bytes of
headroom against the 78,666 limit.

- `OpportunityChart.jsx` and `leakMath.js` already ship for `/portal-preview`.
  Check whether they are in a shared chunk — if so, restoring them on the
  homepage may cost far less than the headroom suggests. Report the real
  delta.
- If it still exceeds: first look for dead weight the two-stylesheet cleanup
  exposes, and confirm `computeLeaks` / `validateInputs` are not currently
  shipping unreferenced.
- If it genuinely does not fit, **stop and tell me the number.** Do not silently
  raise `check-bundle-budget.mjs`. Raising the budget is a decision with a
  reason attached, and it is mine to make.

### 5. Rewire the entrance animations — row 07

Three reduced-motion-guarded keyframes (`p2-hero-in`, `p2-settle`, `p2-rise`)
still compile and ship but select `.p2-*` classes that v54 renamed to `.ops-*`.
They are dead bytes and the page arrives with no entrance.

- Rewire them to the current class names, or delete them outright. Shipping
  dead keyframes is the one option that is not acceptable.
- If you rewire: keep them behind `prefers-reduced-motion: no-preference`, keep
  them short, and keep them off anything that delays reading a number.
- Motion is on the hero and on section arrival only. Nothing animates on data.

### 6. The remaining small fixes

- **Row 03** — `theme-color` follows whatever the final canvas decision is.
- **§06 borders** — `#939d95` at 2.46:1 and `#668070` at 3.77:1 are used as
  input and button borders, so axe stays quiet and the fields are effectively
  invisible. Bring both to 3:1 minimum against their ground.
- **`overflow: clip` on `.ops-site`** — this hides horizontal overflow instead
  of surfacing it, so a too-wide child can never fail a check. Remove it and fix
  whatever it was hiding, or justify keeping it.
- **Rows 11, 14, 16, 17** you marked Neutral/Restore. Take them in that order of
  cost and tell me which you judged worth doing; the page title (row 17) is a
  live indexed production page and a SEO change bundled into a design release —
  flag it separately rather than folding it in silently.

---

## Verification before you call Phase 1 done

- Both commits built and screenshotted at 390 / 768 / 1440, before and after.
- CSS gzip reported against the 8,396-byte v53 baseline. JS gzip reported
  against the 78,666 limit.
- Mobile page height reported against the 12,350px ceiling.
- Contrast ratios for: the primary CTA against its ground, both repaired
  borders, and the muted-text pair (v53 managed 9.62:1, v54 5.81:1 — report
  where you land).
- `npm run lint`, `npm test` (169 tests), `npm run test:e2e`,
  `npm run scan:secrets`, `check-public-claims.mjs`, `budget:bundle`, and both
  Lighthouse runs. Lighthouse must not regress from 100 desktop / 99 mobile.
- The four "do not touch" items confirmed untouched.
- No hardcoded hex or px font size left outside the token block — report the
  count, which should be 0 and 0.

## Report format

Per work item: the regression row or defect it answers, what you changed, the
measured numbers, and before/after screenshots. Then a short list of anything
you chose **not** to do and why. Flag every judgement call — especially the
hero photo decision in item 3 — rather than burying it.

Work on a branch. Do not open a PR and do not merge; merging to `main` deploys
production. This is a review gate like the last one.

## ==================== COPY TO HERE ↑ ====================
