# PrimeOps v54 — Phase 3 Fix Pass

Sent to the Phase 1 session, which owns `restore/phase-1-paper-canvas`.

Closes the independent audit (75/100, SHIP WITH FIXES). The three blocking
findings are all gate failures, so each fix is sequenced to **prove the gate
catches what it missed** before the defect itself is fixed.

## ==================== COPY FROM HERE ↓ ====================

The independent audit came back: **75/100, SHIP WITH FIXES**, no DO NOT SHIP.

It confirmed the hard parts. The second stylesheet is gone, the canvas held at
paper across all three widths, the budget instrument survived adversarial
testing (it rewrote the entry HTML to try to duck the eager bucket and the
bytes landed in `jsAsync`, exit 1), the calculator clears its claim boundary on
every substantive criterion, and not one line of compliance work was reverted.
Your own numbers all matched independent measurement — 76,779 / 3,879 / 10,196,
baselines, contrast figures, 12,261px.

It also found a live bug that three green gates missed. That is what this pass
is for.

### The sequencing rule for this pass

Findings 01, 02 and 03 are one story: a defect, and two gates that should have
caught it and did not. **Fix the gates first and watch them fail on the
un-fixed defect.** A gate fix that is never observed failing is not verified —
it is hoped for. Concretely:

1. Fix the axe gate (03). Run it. **It must now FAIL**, reporting the 1:1
   contrast on `.form-head > div > strong`. Paste that failure output.
2. Fix the spec that measures the loading state (02). Prove it can fail —
   temporarily make the drawer tab-reachable, confirm the assertion goes red,
   revert the mutation. Paste both.
3. Only then fix the invisible heading (01). Re-run. Both gates go green for
   the right reason.

If step 1 does not fail, the gate fix is wrong and finding 01 is still
invisible to CI. Stop and say so rather than proceeding.

---

## Must fix — these block the ship

### 01 · The consultation form heading is invisible
`src/platform2/Platform2.css:136`, consequence of `:358`

`.ops-site .pilot-section` sets `color: var(--on-forest)` (#fbfaf6) and it
inherits into the form. `.pilot-form` sets a `var(--surface)` background —
also #fbfaf6 — and never resets `color`. Labels, inputs and the subtitle each
re-declare their own colour and survive. `.form-head strong` sets only
`font-size` and `line-height`, so the 22px heading on the primary conversion
form renders at **1.00:1** and is not visible.

This branch introduced it: the base carried the reset at
`MarketingSite.css:226` in `3040106` — `.ops-site .pilot-form { … color:
var(--ops-ink); … }` — and the merge dropped it.

Add `color: var(--ink)` to the `.pilot-form` rule. One declaration, re-covering
the whole form subtree exactly as the base did. Then check the same class of
defect elsewhere: any rule that sets a background without setting a colour,
inside a subtree that inherits a light `color`. The merge may have dropped more
than one reset.

### 02 · A fifth spec still measures the loading state
`tests/e2e/focus-and-keyboard.spec.js:55–63`

"closed portal drawer is out of the tab order" calls `page.goto('/portal-preview')`
then `page.evaluate` in a twelve-iteration Tab loop. The auditor reproduced it:
immediately after `goto` the document reads
`{portalLoaded:false, loadingState:true, drawerExists:false}` and body text is
"LOADING THE SYNTHETIC PORTAL PREVIEW…". Across all twelve presses the portal
never loads and `activeElement` never leaves BODY. The assertion is negative —
`expect(trapped).toBe(false)` — so **a page with one sentence on it passes every
time.** The only guard on the drawer's tab-trapping can never fail.

Route it through `gotoRoute`. Then sweep the whole e2e suite for the same shape
rather than fixing only the named line: any `page.evaluate`,
`locator.evaluateAll` or `AxeBuilder.analyze` that runs against a route without
first awaiting a real element. The auditor judged the other seven raw portal
navigations safe because they assert through auto-waiting matchers — confirm
that yourself and report the list you checked.

### 03 · The axe gate reads the wrong bucket
`tests/e2e/site.spec.js:209–217`

Axe **did** catch finding 01. It filed it under `results.incomplete`, because
an exact 1:1 ratio can be deliberate hiding rather than a defect:

```
color-contrast → [".form-head > div > strong"]
"Element has a 1:1 contrast ratio with the background"
```

The assertion filters `results.violations` only, so the worst contrast defect
on the page routes around the gate that exists to catch it.

Assert on `incomplete` too. At minimum fail on any `incomplete` entry with
`id === 'color-contrast'` carrying a 1:1 message. Consider whether other
`incomplete` ids deserve the same treatment, but do not turn the whole bucket
into a hard failure without checking what else lands there — report what you
find before widening it.

---

## Should fix — land before or alongside

### 04 · Dark-theme residue behind a paper page
`src/platform2/Platform2.css:34, :90, :91`

Measured in-browser on the homepage: `html` background `rgb(9,12,10)`, `body`
background `rgb(9,12,10)`, root `color-scheme: dark`. `.ops-site` paints paper
over the top and sets `color-scheme:light` on itself, so the page looks right —
but the ground behind it does not. Line 91 hardcodes `background:#090c0a` on
body; line 90 gives `html` the fallback `var(--p2-bg,#090c0a)`, and `--p2-bg` is
never defined at that level, so the fallback applies.

Visible consequences: the overscroll gutter on iOS and macOS shows near-black
behind a paper page, and the viewport scrollbar and native control defaults take
their scheme from the root's dark rather than the descendant's light.

Point `html` and `body` at the marketing canvas, and move `color-scheme:dark`
off `:root` onto `.p2-site` where the dark instrument routes actually live.
Verify both the paper homepage and the dark routes still look correct.

### 05 · The register still orders the calculator's removal
`docs/release/capability-truth-live/01-VISUAL-PROBLEM-REGISTER.md:20`

The standing P0 row reads, verbatim: "Remove the public leak calculator from
the homepage." The branch restores it. The only documentation change across all
four commits is two lines of `public-claim-files.json`. The shipped state
contradicts an approved P0 with no recorded decision reversing it.

The row's acceptance criteria are met — the modeled total sits at y≈6,732,
outside the first three viewports at every width, and the fictional disclosure
is adjacent. **The remedy wording was overridden, not the safety property.**
That distinction is the point: amend the row to record the new remedy
(restored under Modeled framing, below the third viewport, at the H3 step),
that Joe approved the reversal on 2026-08-27, and that the original acceptance
criteria still hold and were re-verified. Do not weaken the criteria.

### 06 · Drop the unjustified hover extension
`src/platform2/Platform2.css:640–644`

v53 carried `.p2-control-list article:hover{transform:translateX(3px)}` for one
family, so restoring that on `.ops-control-boundary` is defensible — keep it.
Extending the identical transform to `.ops-capability-ledger > article` and
`.ops-questions li` is new behaviour on two surfaces that never had it, and no
regression row asks for it. Your own comment — "hover feedback on the surfaces
that were previously inert" — describes an improvement, not a restoration.

Drop those two. It is small, and that is exactly why it matters: it is the
reflex that produced v54.

### 07 · Name the access-route rules
`src/platform2/Platform2.css:403–405, :470`

Four new rules style `.p2-access-page .pilot-*` on a route declared out of
scope. The auditor judged them fair — unprefixing the shared `.pilot-*` block
during the merge changed what the access page inherited, so something had to
restore its layout. A necessary consequence, not scope creep. But it was not
named. Add a comment at the rule and a line in the report saying so.

---

## Raise, do not do

Report on each; do not act without a decision.

- **The budget's `public/` blind spot.** Both the old script and the new one
  read `dist/assets` only, and the eager regex is anchored to `/assets/`. A
  script served from the dist root — anything in `public/` — is invisible to all
  three budgets. The auditor demonstrated it: a 400KB gzip file loaded by a
  plain `<script src="/vendor-blob.js">` passes with exit 0. Pre-existing, but
  the rewrite was the natural moment to close it. Cost it and recommend.
- **Thirteen dark tokens declared on the homepage element and never
  overridden.** `MarketingSite.jsx:218` renders `className="p2-site p2-marketing
  ops-site"`, so the wrapper carries both palettes and `.ops-site` wins on
  source order. `--p2-bg`, `--p2-text`, `--p2-green` and ten others stay dark.
  All current consumers live under `.p2-portal`, `.p2-access-page` or
  `.p2-security-page`, so there is no live defect — but it is the same
  override-by-source-order shape as the original root cause, and any future
  homepage rule reaching for a `--p2-*` token silently renders dark on paper.
- **The async chunk has 193 bytes of headroom** and CSS has 509. Defensible as
  a deliberate floor, but it will fire on the next small change to
  `PortalPreview`. Say so in the report so whoever hits it knows it was set at
  the floor on purpose rather than mis-measured.
- **The type-floor test enforces 12px, not the brand sheet's 16px.** 116 nodes
  render under 16px, all token-driven (`--t-label:12px`, `--t-data:13px`,
  `--t-nav:15px`) and no prose below 17px. The suite would not catch a drift
  toward the small end of that scale.
- **Document the 40 → 32px mobile section padding** in the brand sheet as a
  deliberate exception with its reason — it holds a hard gate, and left
  undocumented it will be rediscovered as a mistake.

---

## Verify

Re-run the full gauntlet: lint, unit, e2e, build, claims scan, secrets scan,
`budget:bundle`, both Lighthouse runs. Nothing may regress from 100 desktop /
99 mobile, and the budget must still pass on all three keys.

Then the specific proofs this pass exists for:

- The axe gate observed **failing** on the un-fixed heading, then passing.
- The tab-order spec observed **failing** on a deliberately tab-reachable
  drawer, then passing.
- The homepage screenshotted at 390 / 768 / 1440 with the form heading visible.
- `html` and `body` backgrounds re-measured after the 04 fix, on both the paper
  homepage and a dark route.

Update the Phase 1 Restoration Report artifact
(285a41fb-bfb9-4073-94e8-1c85a5bfabf5) — republish to the same URL — with a
closing section covering what this pass changed and what was raised rather than
done.

Still branch-only: no PR, no merge.

## ==================== COPY TO HERE ↑ ====================
