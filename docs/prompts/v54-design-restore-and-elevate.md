# v54 Design Rollback + Elevation Prompt

**What this is:** a production-grade prompt to hand to whatever tool built v54
(Claude Code, Cursor, Lovable, v0, Bolt, Replit, a human designer) to (1) get the
design back to what it was before v54, and (2) take it materially further —
better graphic design, better functionality, and copy a restaurant owner
actually understands.

**How to use it**

1. Fill in the six lines in `PROJECT FACTS` below. Takes 60 seconds.
2. Copy everything between the `COPY FROM HERE` and `COPY TO HERE` markers.
3. Paste it as your first message. Do not add "make it pop" or "be creative" —
   the prompt is deliberately constrained, and loosening it is what produces
   another v54.
4. When the agent returns its Phase 0 report, read it before approving. That
   gate is the whole point.

---

## PROJECT FACTS — fill these in first

```
PRODUCT:        <what it is, one line — e.g. "ops dashboard for Champion Pizza managers">
USERS:          <who opens it daily — e.g. "restaurant owners and store managers, ages 25-60, phone + back-office desktop, English and Spanish">
STACK:          <e.g. Next.js + Tailwind + shadcn/ui | Lovable project | Framer | Streamlit>
GOOD VERSION:   <tag, commit, deploy id, or date of the version you liked — e.g. "v53" or "the deploy from Aug 19">
BAD VERSION:    <v54 — tag/commit/deploy id>
LIVE URL:       <where v54 is deployed right now>
BRAND:          <existing brand colors/fonts/logo, or "none — propose one">
```

---

## ================ COPY FROM HERE ↓ ================

You are a senior product designer and front-end engineer taking over a design
that shipped badly. Version 54 of this product replaced a design people liked
with one they don't. Your job is to restore the previous design exactly, then
elevate it deliberately — not to redesign it again from your own taste.

Read this entire brief before you touch a file. Work in phases. Stop at every
GATE and wait for my approval.

### PROJECT FACTS

<paste your filled-in PROJECT FACTS block here>

### THE ONE RULE

**Restore first, improve second, and never improve by inventing.**

v54 failed because someone changed things that were not broken. Every change you
make from here must be traceable to one of three justifications:

1. It restores the pre-v54 design.
2. It fixes a defect you can name (contrast failure, unreadable on a phone,
   ambiguous copy, a broken state, a slow interaction).
3. I explicitly asked for it.

"It looks more modern," "it feels cleaner," and "this is the current trend" are
not justifications. If you cannot name the defect, leave it alone.

---

## PHASE 0 — FORENSIC RECOVERY (no code changes)

Find the old design. Do not reconstruct it from memory or from screenshots
alone if the source still exists.

**If the project is in git:**

```bash
git log --oneline --all --decorate -40
git tag -l
# Which files did v54 actually touch?
git diff <GOOD>..<BAD> --stat
# Narrow to the visual layer
git diff <GOOD>..<BAD> --stat -- '*.css' '*.scss' '*.tsx' '*.jsx' '*.vue' \
  'tailwind.config*' '*theme*' '*token*' '*global*' 'app/layout*'
# Read the old file verbatim
git show <GOOD>:path/to/file
```

**If the project has no git (Lovable / v0 / Bolt / Framer / Webflow):** use the
tool's own version history or restore point to open the last good version, and
export or screenshot every screen before you change anything. Also check
`web.archive.org` for the live URL. Capture the old CSS from the deployed build
if it is still reachable.

**Produce a written REGRESSION TABLE.** One row per thing v54 changed:

| # | Screen / component | Before (v53) | After (v54) | Verdict | Restore? |
|---|---|---|---|---|---|
| 1 | Dashboard header | 32px bold ink, left | 48px light gray, centered | Worse — lost hierarchy, fails contrast | Yes |

Verdict is one of: **Worse** (restore), **Neutral** (restore, it wasn't asked
for), **Better** (keep, and say why). Be honest — if something in v54 is
genuinely better, defend it in one sentence and keep it.

**GATE 0 — Post the regression table and wait. Change nothing yet.**

---

## PHASE 1 — RESTORE THE BASELINE

Restore every row marked Restore. Prefer surgical restoration over a blanket
revert: revert the whole commit only if v54 was purely a design change with no
bug fixes or features riding along in it.

Verify by screenshot, not by belief. Capture every affected screen at **390px,
768px, and 1440px** and place them next to the v53 originals. Any pixel
difference you did not intend is a bug.

Tag or snapshot this state as the **restored baseline** before Phase 2. If
everything after this goes wrong, this is where we roll back to.

**GATE 1 — Post before/after screenshots. Wait.**

---

## PHASE 2 — THE DESIGN SYSTEM

Now build the foundation the old design never had. This is where the real
upgrade comes from: not from new visuals, but from consistency.

Extract everything into tokens. No hardcoded hex, px, or shadow values anywhere
in components after this phase.

### Color

Derive from the existing brand if there is one. If there is not, use this warm,
appetite-forward, high-contrast set — it is built for a food business and for
screens read in bright kitchens:

```
--canvas:    #FAF7F2   /* page background — warm, not clinical white */
--surface:   #FFFFFF   /* cards, sheets */
--surface-2: #F3EEE7   /* inset areas, table header rows */
--line:      #E5DDD3   /* hairlines — 1px, never 2 */

--ink-900:   #1A1512   /* primary text — warm near-black, never #000 */
--ink-600:   #5C534C   /* secondary text */
--ink-400:   #8C8179   /* placeholder, disabled — never for real content */

--brand:     #C3402B   /* primary actions and brand marks ONLY */
--brand-ink: #8E2B1C   /* hover / pressed */

--good:      #1F7A4D   /* money up, confirmed, in stock */
--warn:      #B7791F   /* needs attention, running low */
--bad:       #9B2C2C   /* failed, over budget, 86'd */
```

Rules that matter more than the values:

- **Never encode meaning in color alone.** Brand red and error red will be
  confused. Every state carries an icon and a word, always. A number that is
  down is red *and* has a ▼ *and* says "down 12%".
- Body text must hit **4.5:1** against its background; large text and UI
  chrome **3:1**. Run the check, don't eyeball it. `--ink-400` on `--canvas`
  fails — that is why it is placeholder-only.
- Maximum three surface levels. If you need a fourth, your layout is wrong.
- No gradients on surfaces. One gradient maximum in the entire product, and
  only if it carries brand meaning.

### Typography

- Two families maximum: one for display/headings, one for UI/body. A well-set
  system stack beats a badly-set custom font.
- **Every number that represents money, time, or a count uses
  `font-variant-numeric: tabular-nums`.** Non-aligning digits in a sales column
  is the single most common tell of an amateur dashboard.
- Scale (1.25 ratio, 16px base): `12 / 14 / 16 / 20 / 25 / 31 / 39 / 49`.
  Nothing between steps.
- Body is **16px minimum**, never 14px, never gray-on-gray. Owners read this on
  a phone with flour on their hands.
- Line height: 1.5 body, 1.2 headings. Measure: 60–75 characters max.
- Weights: 400 body, 500 UI labels, 600–700 headings. No 300 weight anywhere.

### Space, shape, depth

- 4px base unit. Allowed values only: `4 8 12 16 24 32 48 64 96`.
- Radii: `4px` inputs, `8px` buttons and cards, `16px` modals and sheets,
  `999px` pills. Pick one and use it everywhere — mixed radii read as sloppy.
- Three elevation levels, warm-tinted, never pure black:
  `0 1px 2px rgba(26,21,18,.06)`, `0 4px 12px rgba(26,21,18,.08)`,
  `0 16px 40px rgba(26,21,18,.12)`.
- **Alignment beats decoration.** Before adding any shadow, border, or
  background, check whether consistent alignment and spacing solves it instead.
  It usually does.

### Motion

- `120ms` micro (hover, press), `200ms` standard (panels, tabs), `320ms`
  overlays. Easing `cubic-bezier(.2,.8,.2,1)`.
- Motion communicates cause and effect. Nothing animates decoratively.
- Honor `prefers-reduced-motion: reduce` — cut duration to 0.01ms, keep opacity.

### Targets

- 44×44px minimum touch target everywhere. **56px** for primary actions on
  tablet, because those get tapped with a thumb over a hot line.
- Visible focus ring on every interactive element: 2px, offset 2px, never
  `outline: none`.

**GATE 2 — Post the token file and one refactored screen. Wait.**

---

## PHASE 3 — GRAPHIC DESIGN, DONE PROPERLY

Apply the system. The goal is a product that looks like it was made by a
company that runs restaurants, not by a design tool.

**Do this:**

- **Lead with the number.** On any screen showing performance, the number the
  owner came for is the largest thing on it — 39px or 49px, tabular, with the
  comparison directly beneath in 14px: "$4,182 today · up $340 from last
  Tuesday." Always compare to something. A number with no context is noise.
- **Use real photography, not illustration.** Food, the actual store, the
  actual staff. If you have no photos, use solid brand color and type — that
  reads as confident. Stock illustration of abstract people reads as a
  template.
- **Density is a feature here.** An owner comparing four locations wants all
  four on one screen. Do not spread six data points across three scroll-lengths
  of whitespace. Calm ≠ empty. Tighten rows, keep the air between *groups*.
- **Give every screen one primary action** in `--brand`, one place, always in
  the same place. Everything else is a secondary or ghost button. If two things
  are competing for primary, the screen is doing two jobs.
- **Design the empty state, the loading state, the error state, and the
  too-much-data state for every screen** before you call it done. Four states,
  not one. The empty state teaches; it never just says "No data."
- **Tables:** sticky header, right-align numbers, left-align text, zebra only
  above 8 rows, a real sort affordance, and on mobile collapse each row into a
  card rather than horizontal-scrolling.
- **Charts:** one idea per chart. Direct-label the series instead of a legend
  where you can. Y-axis starts at zero for bars. No 3D, no donut with 9 slices,
  no dual axes.
- **Icons:** one icon set, one weight, one size grid. Never emoji as UI icons
  in production.

**Do NOT do this — this list is what produced v54:**

- Purple/blue gradient hero. Glassmorphism. Frosted blur panels. Animated
  gradient borders. Floating 3D blobs. Aurora backgrounds.
- Centered marketing-page layout applied to an operational tool.
- Light-gray text on white in the name of "minimalism."
- Thin/300 font weights for anything read at a glance.
- A carousel. Ever.
- A modal for something that could be inline or a side sheet.
- Replacing clear labels with bare icons.
- Dark mode as a redesign. If dark mode is wanted, it is a separate token set,
  shipped separately, and it is not an excuse to change layout.

**GATE 3 — Post screenshots of every redesigned screen at three widths. Wait.**

---

## PHASE 4 — THE WORDS

This is not polish. This is the part the users actually notice.

The reader is a restaurant owner or manager. They are competent, busy, and
often reading on a phone between tickets. They may read English as a second
language. They are not "non-technical" — they run a business with tighter
margins than most software companies. Write to them as a peer, not a beginner.

### The rules

1. **Second person, active voice, present tense.** "You spent $412 more on food
   this week." Not "An increase in COGS has been detected."
2. **Grade 6–8 reading level.** Short sentences. One idea per sentence.
   Sentence case for everything, including buttons and headings.
3. **Keep restaurant words. Kill software words.** They know *prime cost, food
   cost, covers, tickets, comps, 86'd, front of house, par level*. Those are
   their words — use them. They do not want *synchronize, configure, initialize,
   utilize, leverage, workflow, entity, instance, deprecated, provision*.
4. **Buttons say what happens.** "Save changes," "Send to kitchen," "Add
   location." Never "Submit," "OK," "Confirm."
5. **Errors do three things:** say what happened in plain words, say whether
   their data is safe, and give them the next step. Never show a code without a
   sentence. Never blame the user.
6. **Numbers are formatted like money, not like data.** `$4,182` not `4182.00`.
   Round in summaries; be exact in detail views. Say "up $340 from last
   Tuesday," not "+8.85% WoW."
7. **No filler.** Delete "Please note that," "In order to," "Simply," "Just,"
   "seamlessly," "effortlessly," "powerful," "robust," "cutting-edge,"
   "revolutionize," "empower," "unlock," "supercharge," "game-changing."
8. **Consider Spanish.** If any meaningful share of the staff reads Spanish,
   plan for a second locale now — keep strings in one file, avoid text baked
   into images, and leave 30% width headroom for longer translations.

### Rewrite table — build one of these for every string in the product

| Where | v54 says | Rewrite to |
|---|---|---|
| Dashboard title | Analytics Dashboard | How you're doing |
| Empty state | No data available | No sales yet today. Numbers show up here as orders come in. |
| Sync error | Error: integration sync failed (code 502) | We couldn't reach DoorDash. Your orders are safe — we'll keep trying. Retry now |
| Cost alert | COGS variance exceeds configured threshold | You spent $412 more on food than usual this week. See what changed |
| Settings | Configure integration settings | Connect your delivery apps |
| Onboarding | Complete your onboarding flow | Let's get your first location set up |
| Retention | Churn risk cohort identified | 23 regulars haven't ordered in 30 days |
| Save | Submit | Save changes |
| Server error | Error 500: Internal server error | Something broke on our end — not your fault. Nothing you entered was lost. We're fixing it. |
| Confirm delete | Are you sure you want to delete this item? This action cannot be undone. | Delete the Tuesday lunch special? You can't undo this. |
| Loading | Loading… | Getting today's numbers… |

Apply the same treatment to every heading, label, tooltip, toast, empty state,
error, and email. Post the full table.

**GATE 4 — Post the complete rewrite table before applying it. Wait.**

---

## PHASE 5 — FUNCTIONALITY

Design is how it works. Add these:

- **Skeletons, not spinners,** for anything over 300ms — matched to the shape of
  the content that's coming.
- **Optimistic updates with undo.** Apply the change immediately, show a toast
  with "Undo" for 8 seconds. This replaces most "Are you sure?" dialogs.
  Keep the dialog only for genuinely destructive, unrecoverable actions.
- **Autosave with a visible "Saved" marker** on any form longer than three
  fields. Never lose a manager's work to a dropped connection.
- **Inline validation on blur,** not on submit. Say how to fix it, next to the
  field.
- **Date-range presets first:** Today, Yesterday, This week, Last week, This
  month, Last month — then a custom picker. Nobody wants to open a calendar to
  see yesterday.
- **Every metric compares to a prior period** by default. Toggle between "vs
  last week" and "vs last year."
- **Drill-down everywhere.** Every summary number is clickable down to the rows
  behind it.
- **Export** to CSV and to a clean print/PDF layout. Owners send these to
  accountants and partners.
- **Offline tolerance** if this is used on the floor: queue writes, show a clear
  "You're offline — 3 changes will send when you reconnect" bar.
- **Sticky bottom action bar on mobile** so the primary action is always
  thumb-reachable.
- **Keyboard support on desktop:** `/` focus search, `Esc` close, arrow keys in
  tables, `Cmd/Ctrl+S` save. Tab order follows visual order.

---

## PHASE 6 — VERIFY BEFORE YOU CLAIM DONE

Do not report success on any of this without evidence.

- Screenshots of every screen at 390 / 768 / 1440, light and dark if dark ships.
- Contrast audit output showing every text/background pair passing.
- Lighthouse: Performance ≥ 90, Accessibility ≥ 95 on the main screens.
- **Real-content test:** the longest real location name, a six-figure dollar
  amount, a zero state, an error state, a 200-row table, a two-character name.
  Lorem ipsum hides every layout bug you have.
- Keyboard-only pass through the primary flow, and one screen-reader pass.
- Tested on an actual phone, not just a resized browser window.
- Confirm nothing from the Phase 0 regression table marked "Restore" has
  drifted back.

### Ship safely

Keep the restored baseline tagged. Put the Phase 3+ changes behind a flag or
ship them to a preview URL first. I want to be able to roll back to the v53
look in one step, without another emergency.

### Report format

For each phase: what changed, why (tied to a regression row, a named defect, or
my explicit request), before/after screenshots, and anything you chose not to do
and why. Flag every judgment call you made instead of burying it.

## ================ COPY TO HERE ↑ ================

---

## Appendix A — Short version

For tools with a small context window, or a quick pass:

> Version 54 of this product replaced a design people liked with one they don't.
> Do three things, in order, stopping for approval after each.
> **1)** Find the pre-v54 version in git or version history, diff it against
> v54, and give me a table of every visual change with a Worse/Neutral/Better
> verdict — no code changes yet.
> **2)** Restore everything marked Worse or Neutral, verified with before/after
> screenshots at 390px, 768px and 1440px.
> **3)** Then improve it, but only with named defects as justification: pull all
> colors, type, spacing, radii and shadows into tokens; body text 16px minimum
> at 4.5:1 contrast; tabular numerals on every money figure; lead each screen
> with one big number plus a comparison to last period; give every screen an
> empty, loading, error and overflow state; one primary action per screen; and
> rewrite every string for a busy restaurant owner — second person, plain
> English, grade 6–8, keep restaurant words like prime cost and 86'd, kill
> software words like sync, configure and utilize, and make every button say
> what it does. No gradients, no glassmorphism, no gray-on-white text, no thin
> font weights, no carousels, no emoji as icons. Do not change anything you
> cannot name a defect for.

---

## Appendix B — Voice cheat sheet

Pin this next to whoever writes strings.

| Instead of | Say |
|---|---|
| Utilize / leverage | Use |
| Initialize / provision | Set up |
| Synchronize | Update |
| Configure | Set up, or Choose |
| Authentication failed | We couldn't sign you in |
| Invalid input | That date isn't in the past — pick another |
| Operation successful | Saved |
| No results found | Nothing matches "chicken." Try a shorter word. |
| Insufficient permissions | Only owners can change this. Ask <name> to do it. |
| Processing your request | Working on it… |
| Optimize your workflow | Get orders out faster |
| Actionable insights | What to fix this week |
| Revenue analytics | Sales |
| Labor cost variance | You spent $280 more on staff than planned |

**The test:** read the sentence out loud to someone standing behind a counter.
If they'd need a follow-up question, rewrite it.

---

## Appendix C — Acceptance checklist

Paste as a follow-up message when the agent says it is finished.

```
Before I accept this, confirm each with evidence:

[ ] Every row in the Phase 0 regression table is resolved — restored or
    defended in one sentence
[ ] Before/after screenshots at 390 / 768 / 1440 for every changed screen
[ ] Zero hardcoded colors, font sizes, spacings, radii or shadows in components
[ ] Contrast audit passes 4.5:1 body / 3:1 large and UI — paste the output
[ ] Body text is 16px or larger everywhere
[ ] Tabular numerals on every money, time and count figure
[ ] Every screen has empty, loading, error and overflow states — screenshot all four
[ ] Exactly one primary action per screen, in a consistent position
[ ] No state is communicated by color alone
[ ] Full string rewrite table applied, no software jargon left
[ ] Every button label says what happens
[ ] Every error says what happened, whether data is safe, and what to do next
[ ] Keyboard-only pass through the primary flow completed
[ ] Tested with real longest/largest/emptiest content, not placeholder text
[ ] Tested on a real phone
[ ] Lighthouse Performance ≥ 90, Accessibility ≥ 95
[ ] The restored baseline is tagged and rollback is one step
[ ] List everything you changed that was NOT in the regression table or my
    explicit requests, with the defect each one fixes
```
