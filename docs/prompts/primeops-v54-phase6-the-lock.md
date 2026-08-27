# Phase 6 — The Lock

Make v55 unable to repeat v54.

Branch: `restore/phase-1-paper-canvas`. Branch only. No PR. Nothing merged.

---

## Why this phase exists

v54 was not a bad taste event. It was a **structural** one, and the structure is still there.

A second stylesheet was layered over the first and inverted the canvas from `#090c0a` to
`#f3f0e7`. Every asset that had been designed for the dark ground stayed exactly where it
was. Nothing in the build objected. Lint passed, tests passed, the budget passed, Lighthouse
passed — and the site shipped reading as a brochure where an instrument used to be.

Five phases of work have now restored it. **None of that work is protected.** Every gate
that exists today would let the same change through again tomorrow.

Your job is to close that. Not to add taste rules — to make the specific failure modes that
produced v54 mechanically impossible, or where that is impossible, mechanically visible.

---

## Deliverable 1 — `DESIGN_RULES.md`

At the repo root. Written for whoever touches this site next, human or model, with no memory
of any of this. Each rule states **the rule**, **why it exists** (cite the incident, not a
principle), and **what enforces it** (a named check, or "review only" said plainly).

Do not write aspirational rules. Every rule must be one you can point at real damage for.

Cover at minimum:

**One ground, one stylesheet.** The marketing surface has a single source of truth for
canvas, ink and line. No second stylesheet may redefine them. This is the literal v54
mechanism.

**Tokens are the only source of colour.** v54 bypassed them. Raw hex outside the token
block is how a ground gets changed in one place and not the other seven.

**Changing the canvas is a whole-system change.** If the ground token changes, every asset
anchored to the old ground must be re-anchored in the same commit — photography, shadows,
overlays, chart ink, borders. A canvas change that touches only the canvas is the v54 bug
by definition.

**The page shows the product; it does not describe it.** Phase 4 built the measurement.
Product surface is the union of rendered software surfaces over document height. State the
merged floor at 390 / 768 / 1440 as measured on the final commit. Falling below it is a
regression, not a style preference.

**Nothing animates on data.** Phase 4 removed the hero settle animation rather than
retargeting it. Say why: motion on a number reads as decoration and undermines the number.

**Fonts are IBM Plex Sans and IBM Plex Mono, self-hosted.** No webfont CDN link tags.

**The claim boundary is not a design surface.** `check-public-claims.mjs` and the provenance
register are load-bearing. Point at them; do not restate their contents here or they will
drift out of sync.

**Height ceilings hold.** State the current mobile ceiling and where it came from.

**A gate is not verified until it has been observed failing.** This rule has now caught
three real defects — an invisible form heading, a vacuous e2e spec, and an invalid
definition list written by the same session that strengthened the check. It earns its place
by evidence, so record the evidence.

---

## Deliverable 2 — CI enforcement

Automate what can be automated. Be honest about what cannot.

Strong candidates:

- **Token redefinition** — fail if any stylesheet other than the designated source defines a
  canvas/ink/line token. This is the single highest-value check in this phase; it is the one
  that would have caught v54 on the day.
- **Raw hex outside the token block** — fail on colour literals in component CSS.
- **Product-surface floor** — Phase 4's measurement script, run as a gate against the merged
  floor at all three widths.
- **Webfont CDN link tags** — fail on any external font stylesheet.

Existing gates to leave alone but reference: claims, secrets, bundle budget (including the
`public/` fix from Phase 5), height ceilings, axe, Lighthouse.

### The gates-first rule applies to every check you add

For each new gate:

1. Write the gate.
2. **Introduce the exact defect it exists to catch, and watch it fail.**
3. If it does not fail, the gate is wrong. Stop and say so rather than shipping a green
   check that enforces nothing.
4. Remove the defect. Confirm green.

Report the observed-failing output for every gate. A check that has only ever been seen
passing is decoration.

**If a rule cannot be enforced mechanically, do not fake it.** Put it in `DESIGN_RULES.md`
under a clearly marked review-only heading. A rule everyone believes is automated and isn't
is worse than one everyone knows is manual.

---

## Deliverable 3 — make it unmissable

- Reference `DESIGN_RULES.md` from `CLAUDE.md` so every session loads it before touching the
  site.
- If a PR template exists, add the design checklist to it. If not, do not create one.

---

## Deliverable 4 — kill the stale handoff docs

**This is not housekeeping. These documents actively caused damage in this project.**

The June handoff docs describe a stack this repo has never had — they name Tailwind,
Recharts, Framer Motion, and a Space Mono / DM Sans pairing. None of it is true. A session
briefed from those documents wrote four wrong premises into a work plan before your Phase 0
forensics caught it.

Find them. For each: correct it if it has current value, delete it if it does not, and if
you are unsure, mark it clearly and prominently as historical and superseded. Leaving a
confidently wrong document in the repo is leaving a trap.

List what you found and what you did to each.

---

## Constraints

- Branch only. No PR. Nothing merged.
- No customer logo, count, rating, badge, testimonial, named individual, tenure, media or
  founder claim, anywhere. Automatic stop and report.
- No baseline or limit raised without Joe.
- Full gauntlet green at the end, including everything you just added.
- Do not weaken an existing check to make a new one pass.
- Do not rewrite an assertion to make it pass vacuously.

---

## Report

Publish a Phase 6 artifact. Lead with anything that hit a stop condition.

Then:

1. `DESIGN_RULES.md` — the rules, and the incident each one is anchored to.
2. Every gate added, **with its observed-failing output**. Green-only evidence is not
   evidence.
3. What you could not automate and why, stated plainly.
4. The stale docs: found, and what you did with each.
5. Full gauntlet result. Commit SHA. Confirm branch-only.

If a deliverable cannot be done honestly within these constraints, do the others in full and
report exactly what you left undone and why. Do not scale the work down on your own
judgement.
