# PrimeOps — Phase 4: Put the Product on the Page

The competitive gap, measured rather than felt. Phases 1–3 restored and hardened
the page. This one closes the only gap that can be closed right now.

## ==================== COPY FROM HERE ↓ ====================

Phases 1–3 are done and the branch is sound. This is a different problem.

Joe's read is that the site still looks weaker than Restaurant365 and Jolt. I
fetched both homepages rather than guessing, and he is right. Here is the gap,
measured:

| | Product UI on the homepage | Desktop page length |
|---|---|---|
| Restaurant365 | ~40% | ~6,000px |
| Jolt | ~30–40% | long |
| **PrimeOps** | **0%** | **9,174px** |

**The page is 50% longer than Restaurant365's and shows no product at all.**

This is not a craft problem. After Phase 1–3 the typography, token discipline
and contrast are arguably tighter than either competitor's. The problem is that
they show the software working and we show a stock photograph captioned
"Illustrative operating scene."

Restaurant365 leads with an interactive product ecosystem and a "+12.3%" figure
above the fold. Jolt leads with named operators — Baskin Robbins, Zaxby's,
Dairy Queen. We lead with a woman at a laptop.

### What this pass is, and is not

**It adds product VISIBILITY. It does not add product CLAIMS.**

That distinction is the whole brief. Everything the claim register prohibits
stays prohibited, and nothing in this pass gets to soften it:

- No customer logos, counts, ratings, badges, or testimonials. We do not have
  them, and inventing or implying them is out of the question.
- No named individuals, tenure, media, or founder positioning.
- Every product surface stays explicitly labelled as illustrative or fictional,
  using the vocabulary already approved.
- `check-public-claims.mjs` stays intact and passing.

The competitors' proof advantage is real and cannot be designed away. They have
thousands of customers; PrimeOps has a pilot at Chamblee that has not gone live.
**The site looks earlier because the company is earlier.** When the Chamblee
outcome loop runs end to end, that is the case study, and it will be worth more
than anything on either of their pages. Until then we do not borrow credibility.

What we can fix today is that a visitor cannot see the product.

---

## 1. Pay for it before you spend it

Do not add height. The page is at 12,261px against a 12,350px ceiling with 89px
of headroom, and Phase 1 already squeezed spacing to get there.

**Cut the duplication first.** Your own Phase 1 report raised it and did not act,
correctly, because it was outside that brief's scope. It is inside this one:

> The six questions in "Questions from the weekly review" are near-restatements
> of the six lead questions in the capability ledger below it — "Are delivery
> payouts matching the signed rate?" against "Are payouts matching the
> agreement?" — costing about 630px on a phone.

That duplication is v54's. Resolve it — merge, cut, or restructure — and report
what you recovered. Nothing of substance may be lost; if the two sections carry
genuinely different information, say so and find the height elsewhere instead.

**Then re-measure before adding anything.** The height budget for this pass is
what you actually recovered, not what you hoped to.

---

## 2. Put a real product surface on the page

The mini portal preview (row 11) was removed by v54 and left out of Phase 1 for
height and JS budget reasons — **not for claim reasons**. Your own words:

> "The genuine loss — the only glimpse of the real product — is real, and I
> would like to fix it."

Fix it now.

**Strongly prefer a zero-JS product surface.** The initial-route budget has
1,887 bytes of headroom and the async chunk has 193 — mounting the live
`PortalPreview` component on the homepage would blow both. You almost certainly
do not need the interactive portal here. You need a visitor to *see* the product.

In order of preference:

1. **Prerendered static markup** — a real, non-interactive rendering of the
   portal or an operating review, built from the same fictional data, prerendered
   into the HTML so it costs nothing at runtime and works with JS disabled.
2. **An optimised still** of the real interface, through the existing image
   pipeline (`public/images/platform-2/` already ships AVIF/WebP at 720/1280).
   Near-zero budget cost. Must carry the same illustrative labelling and go into
   the asset manifest.
3. **The live component**, only if 1 and 2 genuinely cannot show the product
   honestly — and then stop and tell Joe the byte cost rather than deciding.

**Budget note:** the 662-byte `data.js` split you measured and named in Phase 1
now has a purpose. Take it if you need the room, as its own commit, with the
before and after numbers. `permittedGrowth` stays at 0.05, and the JS baseline is
not raised without Joe.

**Target, so this is checkable rather than a matter of taste:** at least **25%**
of homepage document height should be product surface — real interface, real
states, real numbers, all fictional-labelled. Competitors sit at 30–40%. Measure
it and report the percentage.

---

## 3. Make the loop the spine, not a section

PrimeOps's documented moat is outcome validation — detect → diagnose → fix →
execute → **measure** → learn. Neither Restaurant365 nor Jolt leads with
"did the fix actually work?" They are horizontal feature sites: *here are our
seven modules*. That is the wedge, and right now it is invisible.

Structure the page's spine in operator language:

```
What's wrong   →   Why   →   What to do   →   Did it work?
```

"Did it work?" is the differentiator. Once a fix has run it should be the most
prominent thing on the screen — a confirmed result with the figure recovered,
in the approved Modeled/observed vocabulary. Not a status chip. Not "outcome
recorded: positive delta."

**Do not become them.** Explicitly do not add: a seven-module feature grid, a
"trusted by" strip with nothing in it, an ecosystem wheel, expandable
accordions hiding the substance, or a horizontal everything-platform pitch.
The register pushed away from generic analytics-SaaS for good reasons, and the
answer to looking thin is not to imitate the people who look thick.

---

## 4. The hero

It currently leads with a dark kitchen photograph, full-bleed, captioned
"Illustrative operating scene." That is the least valuable element on the most
valuable space on the site, and it is exactly where both competitors put product.

Phase 1 chose the full-bleed photo over the Harbor Street review with sound
reasoning — a seven-row ledger turns a ten-second read into a document, and it
duplicated the section below. That reasoning still holds for *that* element. It
does not settle whether the hero should show product at all.

Reconsider it now that height exists. Options, your call, with reasons:

- Product surface beside the headline, the way both competitors do it.
- A single decisive number in the approved framing, with the product behind it.
- Keep the photograph, if you can argue it beats showing the software.

Whatever you choose, the required disclosure stays and the CTA stays the
highest-contrast element in the first viewport (currently 15.10:1).

---

## Verify

- **Product surface as a percentage of document height** — report the number at
  390 and 1440. Target ≥25%.
- **Page height must not grow.** Report mobile and desktop before and after,
  against the 12,350px and 12,500px ceilings.
- Screenshots at 390 / 768 / 1440, before and after, side by side.
- Full gauntlet: lint, unit, e2e, build, claims scan, secrets scan,
  `budget:bundle`, both Lighthouse runs. No regression from 100 desktop /
  99 mobile. Budget passing on all three keys.
- `check-public-claims.mjs` passing, scanner unchanged, register updated in the
  same commit if any claim-bearing file changes.
- Confirm no customer logo, count, rating, badge, testimonial, named individual
  or tenure claim was added anywhere.

Publish a Phase 4 report as an artifact, in the same manner as the earlier
passes. Branch only: no PR, no merge.

If you conclude the 25% target cannot be met honestly without either a budget
raise or a claim the register forbids, **stop and say so with the numbers**
rather than hitting the target by weakening either.

## ==================== COPY TO HERE ↑ ====================
