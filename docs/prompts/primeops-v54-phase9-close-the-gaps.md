# Phase 9 — Close the gaps

Joe has chosen all three open items. Branch only: `restore/phase-1-paper-canvas`.
No pull request, no merge, no deploy. He merges himself.

Five commits, in this order. The order matters and is explained.

---

## Why this order

Extending the colour check comes **before** tokenising, because the check currently
reads hex only. Extending it to `rgb()`, `hsl()`, `oklch()` and named colours will
surface literals in the same app routes that the hex-only scan never counted. Tokenise
first and you tokenise 61, then discover more. Extend first and the list grows to its
true size before anything is touched.

Fixing the og-card generator comes before the image budget, because regenerating the
PNG changes its bytes. Set a baseline from the corrected state, not the drifted one.

---

## 1 — og-card generator drift

`scripts/generate-og-card.mjs` mirrors token values by hand and its `muted` is
`#526057` against a live `#414d45`.

Correct the constant **and regenerate the PNG in the same commit.** Changing one
without the other leaves code and asset disagreeing, which is the state you already
flagged. If the generator mirrors other tokens by hand, check every one of them and
report any further drift you find.

---

## 2 — The colour-literal check reads hex only

Extend `check-design-rules.mjs` to catch `rgb()`, `rgba()`, `hsl()`, `hsla()`,
`oklch()`, `color()` and CSS named colours — anything that sets a colour without
going through a token.

**Gates-first.** For each added form, introduce a literal of that exact form on the
marketing surface and watch the check fail on it. A form you never saw fail is a form
you have not actually covered. Report the observed-failing output per form.

Then report the honest number: the grandfather list was 61 hex pairs. What is it once
every colour form is counted? That number is the real scope of item 4.

---

## 3 — The bundle budget does not weigh images

Extend it, the same way `public/` was extended.

- **Gates-first:** place an oversized image, watch the gate fail, remove it, confirm green.
- Baseline from the state *after* the og-card regeneration in commit 1.
- **If existing image weight exceeds what you would set as a sane limit, STOP and report
  the number.** Do not raise a baseline, do not exclude a file. Joe decides.

---

## 4 — Tokenise the app-route literals

Portal, access and security pages, so rule 2 can drop its grandfather list entirely.

This is the item that carries real risk, and the reason it is survivable is that
**a correct tokenisation is a no-op.** Every computed colour must be identical before
and after. So prove it that way:

- Capture computed `color`, `background-color`, `border-color`, `outline-color` and
  `fill` for every affected element, at 390 and 1440, at rest **and** in every
  interactive state the rules cover — hover, focus-visible, disabled, active — with
  transitions settled. Before and after.
- **The required result is zero differences.** You did exactly this for the
  `!important` swap and got 0 across 21 measurements. Same technique, larger surface.
- Any difference is a bug in the tokenisation, not an improvement. Fix it or revert
  that mapping and report it.
- Before/after screenshots of all three routes at both widths.

If a literal has **no** exact token equivalent, do NOT invent a token and do NOT snap it
to the nearest one. Leave it grandfathered, and list every such case with the value and
why. A shorter honest list beats a zero achieved by changing colours.

Its own commit. Nothing else rides along.

---

## 5 — The 1440 margin

Product surface at 1440 is 24.574% against a 24.5 floor. Margin: 0.074 of a point.

**The margin is a symptom, not the goal.** Do not add surface or trim height to move a
ratio — that is the Phase 5 trap and it is still forbidden.

Diagnose instead: main's merged content cost 0.43 of a point at 1440. Where did that
height go, and is any of it genuinely worth cutting on editorial merit? If yes, cut it
and report the delta. If no, say so plainly and leave the page alone.

**"No change, the constraint stands" is an acceptable and possibly correct outcome.**
A gate sitting close to its floor is a gate about to do its job. Report which answer
the content gave you.

---

## Constraints

- Branch only. No PR. No merge. No deploy. Joe merges.
- Each item its own commit, so any one can be reverted alone.
- No claim added anywhere. Automatic stop.
- No baseline raised, no floor lowered, no check weakened, no assertion made vacuous.
- No grandfather entry added for anything other than item 4's honest residue.
- Full gauntlet green at the end, including everything you just extended.

## Report

Publish a Phase 9 artifact. Lead with anything that hit a stop condition.

Per item: what changed, the observed-failing proof for every gate touched, and the
numbers. For item 2, the true literal count once all colour forms are counted. For
item 4, the computed-style diff result and any literal left grandfathered with its
reason. For item 5, which answer the content gave. Full gauntlet, commit SHAs,
branch-only confirmed.
