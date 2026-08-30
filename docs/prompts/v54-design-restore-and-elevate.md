# PrimeOps v54 — Design Rollback + Elevation Kit

**What this is:** three prompts that undo the v54 redesign of the PrimeOps
frontend and then earn a better one — with the words rewritten for the people
the handoff doc says have to use it: *"a non-developer operator."*

**Where to run it:** the frontend lives in **`Halal-Way/primeops-site`**
(Vercel). Open a Claude Code session with that repo as the source, then paste
Prompt 1. The prompts assume the agent can read git history — that's the whole
of Phase 0.

**Run them in order, in different sessions:**

| # | Prompt | Where | Why |
|---|---|---|---|
| 1 | **The Rescue** | session on `primeops-site` | restores v53, then elevates through 7 gated phases |
| 2 | **The Audit** | a *fresh* session, or a different model | grades the result against a rubric — stops the agent marking its own homework |
| 3 | **The Lock** | back in the working session | writes `DESIGN_RULES.md` + lint enforcement so v55 can't drift back |

---

## Confirmed project facts

Taken from `README.md` and `DEVELOPER_HANDOFF.md` in `joeus1/primeops-fb-os`
— not assumed. These are pre-filled into the prompts; nothing to fill in.

```
PRODUCT     PrimeOps — operational intelligence for multi-brand restaurant
            operators. Closes the loop: detect → diagnose → fix → execute →
            measure → learn. Outcome validation is the moat, not complexity.

REPO        Halal-Way/primeops-site (frontend, Vercel)
            Backend: FastAPI + PostgreSQL/asyncpg + Supabase RLS, on Railway

USERS       Restaurant owners, GMs and store managers across HalalWay's 8
            locations (The Halal Guys, Yumsem Eats, Champion Pizza, CM Chicken),
            plus the external Chamblee GA pilot operator.
            Handoff acceptance criterion, verbatim:
            "Frontend usable by a non-developer operator."

STACK       React · Tailwind CSS · Recharts · Framer Motion
TYPE        Space Mono (data display) + DM Sans (UI text)
            — ALREADY the house system. Do not replace.

MODULES     Labor Engine (reference implementation), Food Cost Engine,
            Rent Burden Analyzer, outcome tracking, sentiment analysis,
            specialist leaderboards, billing tiers, PrimeOps chat
            (POST /api/primeops/chat, 6 tools, multi-turn, multi-tenant)

LOCATIONS   Chamblee 229 · Midtown 285 · Duluth 314 · Buford 330 ·
            Newark 215 · Yonkers 319

DATA        Revel = POS/sales (THG Georgia + Newark)
            Shift4 / SkyTab = Yumsem NJ scheduling + time clock (manual exports)
            Reliable Payroll = payroll
            Three different systems. Never conflate them in a label.
```

---

# PROMPT 1 — THE RESCUE

## ======== COPY FROM HERE ↓ ========

You are a senior product designer and front-end engineer taking over the
PrimeOps frontend after a bad release. Version 54 replaced a design people
liked with one they don't. Restore the previous design exactly, then elevate it
deliberately — do not redesign it again from your own taste.

Read this entire brief before touching a file. Work in phases. Stop at every
GATE and wait for my approval.

### PROJECT FACTS

PRODUCT: PrimeOps — operational intelligence for multi-brand restaurant
operators. It closes the loop: detect → diagnose → fix → execute → measure →
learn. Outcome validation is the product's moat.

REPO: this one — `Halal-Way/primeops-site`, the React frontend deployed on
Vercel. Backend is FastAPI + PostgreSQL + Supabase on Railway.

USERS: restaurant owners, GMs and store managers across HalalWay's 8 locations
(The Halal Guys, Yumsem Eats, Champion Pizza, CM Chicken), plus an external
pilot operator in Chamblee, GA. The project's own acceptance criterion is
literally "Frontend usable by a non-developer operator." Treat that as the
brief, not as a nice-to-have.

STACK: React, Tailwind CSS, Recharts, Framer Motion.

TYPE SYSTEM — ALREADY EXISTS: **Space Mono for data display, DM Sans for UI
text.** This is the house pairing. Do not replace it, do not "modernize" it, do
not add a third family. If v54 changed these fonts, that change alone is a large
part of why the release felt wrong — restoring them is Phase 1 work.

MODULES: Labor Engine (the reference implementation), Food Cost Engine, Rent
Burden Analyzer, outcome tracking, sentiment analysis, specialist leaderboards,
billing tiers, and the PrimeOps chat agent.

REAL LOCATIONS (use these for testing, never Lorem or "Location A"):
Chamblee 229, Midtown 285, Duluth 314, Buford 330, Newark 215, Yonkers 319.

DATA SOURCES — three distinct systems, never conflated in a label:
Revel is POS/sales. Shift4/SkyTab is Yumsem NJ scheduling and time clock.
Reliable Payroll is payroll.

### THE ONE RULE

**Restore first, improve second, and never improve by inventing.**

v54 failed because someone changed things that were not broken. Every change
from here must trace to one of three justifications:

1. It restores the pre-v54 design.
2. It fixes a defect you can name (contrast failure, unreadable on a phone,
   ambiguous copy, a broken state, a slow interaction).
3. I explicitly asked for it.

"It looks more modern," "it feels cleaner," and "this is the current trend" are
not justifications. If you cannot name the defect, leave it alone.

---

## PHASE 0 — FORENSIC RECOVERY (no code changes)

Find the real previous version. Do not reconstruct it from memory.

```bash
git log --oneline --all --decorate -40
git tag -l
# identify the v54 commit/deploy and the last good one before it
git diff <GOOD>..<BAD> --stat
# narrow to the visual layer — for this stack that means:
git diff <GOOD>..<BAD> --stat -- \
  'tailwind.config.*' 'postcss.config.*' \
  '**/*.css' '**/globals.css' '**/index.css' \
  '**/*.jsx' '**/*.tsx' \
  '**/theme*' '**/tokens*' '**/*Chart*' '**/*chart*'
git show <GOOD>:tailwind.config.js
```

Also check the Vercel deployment history for this project — every v54-era
preview URL is still live and is the fastest way to see both versions
side by side without building anything.

Pay specific attention to four things, because they are where this stack goes
wrong fastest:

- **`tailwind.config.js`** — did v54 change `theme.extend` colors, fontFamily,
  spacing or borderRadius? A single edit here restyles everything at once and is
  the most likely single cause of "it all feels off."
- **Fonts** — is Space Mono still on data and DM Sans still on UI text? Diff
  every `font-` class and any `@font-face` / next/font / Google Fonts link.
- **Framer Motion** — did v54 add mount animations, staggered card entrances,
  `layoutId` page transitions, or springy hovers? This is the most common source
  of a redesign that "feels wrong" without anyone being able to point at a pixel.
- **Recharts** — did chart colors, axis formatting, tooltips or chart types
  change? Charts carry the numbers; a restyled chart reads as a broken chart.

**Produce a REGRESSION TABLE.** One row per thing v54 changed:

| # | Screen / component | File | Before (v53) | After (v54) | Verdict | Restore? |
|---|---|---|---|---|---|---|

Verdict is one of **Worse** (restore), **Neutral** (restore — it wasn't asked
for), **Better** (keep, and defend it in one sentence). Be honest: if something
in v54 is genuinely better, say so and keep it.

**GATE 0 — Post the regression table and wait. Change nothing yet.**

---

## PHASE 1 — RESTORE THE BASELINE

Restore every row marked Restore. Prefer surgical restoration over a blanket
revert — revert the whole commit only if v54 was purely visual with no bug fixes
or features riding along.

Verify by screenshot, not by belief. Capture every affected screen at **390px,
768px and 1440px** and place them beside the v53 originals. Any pixel difference
you did not intend is a bug.

Tag this state `design-baseline-v53` before Phase 2. That tag is the emergency
exit for every future release.

**GATE 1 — Post before/after screenshots. Wait.**

---

## PHASE 2 — THE DESIGN SYSTEM

The real upgrade is not new visuals. It is consistency, which this codebase
does not currently enforce.

**Tailwind is the token layer. Use it as one.**

Everything — color, font size, spacing, radius, shadow — is defined in
`tailwind.config.js` under `theme.extend`. After this phase, **no arbitrary
values in components**: no `text-[13px]`, no `bg-[#8b5cf6]`, no `p-[18px]`.
Arbitrary values are how a token system dies one commit at a time. Grep for
`-\[` across the components and fix every hit.

**Type — keep the house pairing, tighten how it's applied.**

- **Space Mono** on every number that represents money, a count, a percentage, a
  timestamp, or a store ID. Space Mono is monospaced, so digits already align in
  columns — that is exactly why it was chosen and it is worth protecting.
- **DM Sans** on everything read as language: headings, labels, sentences,
  buttons, errors.
- Never the reverse. Space Mono in a paragraph is hostile to read; DM Sans in a
  sales column makes numbers jitter between rows.
- Scale (1.25 ratio, 16px base): 12 / 14 / 16 / 20 / 25 / 31 / 39 / 49. Nothing
  between steps.
- Body is **16px minimum**. Never 14px, never gray-on-gray. A GM reads this on a
  phone in a kitchen.
- Weights: 400 body, 500 labels, 700 headings. No 300 anywhere.

**Color.** Derive from whatever brand values already exist in the config. Where
gaps remain, this warm, high-contrast set is built for a food business and for
screens read under bright kitchen light:

```
canvas    #FAF7F2   page background — warm, not clinical white
surface   #FFFFFF   cards
surface-2 #F3EEE7   inset areas, table header rows
line      #E5DDD3   hairlines — 1px, never 2
ink-900   #1A1512   primary text — warm near-black, never #000
ink-600   #5C534C   secondary text
ink-400   #8C8179   placeholder/disabled ONLY — never real content
brand     #C3402B   primary actions and brand marks only
good      #1F7A4D   money up, fix confirmed, in stock
warn      #B7791F   needs attention, running low
bad       #9B2C2C   over budget, failed, 86'd
```

Rules that matter more than the values:

- **Never encode meaning in color alone.** Brand red and error red will be
  confused. Every state carries an icon and a word. A number that is down is red
  AND has a ▼ AND says "down 12%".
- Body text hits **4.5:1**; large text and UI chrome **3:1**. Run the check.
- Maximum three surface levels. Needing a fourth means the layout is wrong.
- No gradients on surfaces.

**Space, shape, depth.** 4px base; allowed values only 4 8 12 16 24 32 48 64 96.
Radii: 4px inputs, 8px buttons and cards, 16px modals, 999px pills. Three
elevation levels, warm-tinted, never pure black.

**Framer Motion — this is where v54 most likely went wrong. Constrain it.**

- Wrap the app in `<MotionConfig transition={{ duration: 0.2, ease: [.2,.8,.2,1] }}>`
  and stop passing per-component durations.
- **No mount animations on data.** An owner opening a labor alert at 11pm does
  not want a 600ms staggered card entrance before they can read the number.
  Dashboards render instantly.
- Animate **state changes**, not arrivals: a row expanding, a toast entering, a
  panel sliding, a value counting only when it actually changed.
- No `layoutId` page transitions. No spring physics on hover. No parallax.
- Honor `useReducedMotion()` — return static variants when it's true.

**Recharts — the charts carry the numbers, so treat them as type, not decoration.**

- Always inside `<ResponsiveContainer>`; never a fixed pixel width.
- `tickFormatter` formats money as money: `$4,182`, not `4182`.
- Y-axis starts at zero for bars. `domain={[0, 'auto']}`.
- Faint `<CartesianGrid strokeDasharray="3 3">`, horizontal lines only.
- **Replace the default `<Tooltip>` with a custom one** — the stock Recharts
  tooltip is unthemed and is an instant tell.
- Direct-label the series instead of a `<Legend>` wherever there are ≤3 series.
- One idea per chart. No `<PieChart>` above 5 slices. No dual axes. No 3D.
- Chart colors come from the same tokens as the UI — never Recharts defaults.

**Targets.** 44×44px minimum touch target; 56px for primary actions on tablet,
because those get tapped with a thumb over a hot line. Visible 2px focus ring
with 2px offset on everything interactive. Never `outline: none`.

**GATE 2 — Post the tailwind config diff and one refactored screen. Wait.**

---

## PHASE 3 — GRAPHIC DESIGN, DONE PROPERLY

Make it look like it was built by a company that runs restaurants, not by a
design tool.

**Make the product's own loop the information architecture.** PrimeOps detects →
diagnoses → fixes → executes → measures → learns. That loop is the differentiator
and it is currently invisible in the UI. Surface it, in owner-language, as the
spine of every finding:

```
What's wrong   →   Why   →   What to do   →   Did it work?
```

"Did it work?" is outcome tracking. It is the moat. It should be the most
visually prominent thing on the screen once a fix has been executed — a green
confirmed result with the dollar figure recovered, not a status chip.

**Do:**

- **Lead with the number.** The figure the owner came for is the largest thing
  on the screen — 39px or 49px, Space Mono, with the comparison right beneath in
  14px DM Sans: "$4,182 today · up $340 from last Tuesday." Always compare to
  something. A number with no context is noise.
- **Name locations like humans do:** "Chamblee (229)", never bare "229", never
  "Store_229".
- **Density is a feature.** An owner comparing 8 locations wants all 8 on one
  screen. Do not spread six data points across three scroll-lengths of
  whitespace. Calm is not empty — tighten rows, keep the air between groups.
- **One primary action per screen**, in brand color, in the same position every
  time.
- **Four states for every screen** before it is done: empty, loading, error,
  too-much-data. The empty state teaches; it never just says "No data."
- **Tables:** sticky header, numbers right-aligned in Space Mono, text
  left-aligned in DM Sans, zebra only above 8 rows, real sort affordances, and
  on mobile each row collapses into a card rather than scrolling sideways.
- Real photography where imagery appears — the actual stores, the actual food.
  No photos? Solid brand color and confident type. Stock illustration of
  abstract people reads as a template.
- One icon set, one weight, one size grid. Never emoji as UI icons.

**Do NOT — this list is what produced v54:**

- Purple/blue gradient hero. Glassmorphism. Frosted blur panels. Animated
  gradient borders. Floating 3D blobs. Aurora backgrounds.
- Centered marketing-page layout applied to an operational tool.
- Light-gray text on white in the name of "minimalism."
- Thin/300 weights on anything read at a glance.
- A carousel. Ever.
- A modal for anything that could be inline or a side sheet.
- Bare icons replacing clear labels.
- Dark mode smuggled in as a redesign. If dark mode is wanted it is a separate
  token set, shipped separately, and it is not a licence to change layout.

**GATE 3 — Post screenshots of every redesigned screen at three widths. Wait.**

---

## PHASE 4 — THE WORDS

The reader is a restaurant owner or GM: competent, busy, often reading on a
phone between tickets, sometimes reading English as a second language. They run
a business on tighter margins than most software companies. Write to them as a
peer, not a beginner.

**Rules**

1. Second person, active voice, present tense. "You spent $412 more on food this
   week." Not "An increase in COGS has been detected."
2. Grade 6–8 reading level. Short sentences, one idea each. Sentence case
   everywhere, including buttons and headings.
3. **Keep restaurant words. Kill software words.** They know prime cost, food
   cost, covers, tickets, comps, 86'd, front of house, par level, PMIX — those
   are their words, use them. They do not want synchronize, configure,
   initialize, utilize, leverage, workflow, entity, instance, provision,
   deprecated, cohort, variance, threshold.
4. **Internal module names are not nav labels.** "Labor Engine," "Rent Burden
   Analyzer," and "Expert Skill Library" are fine in the codebase and wrong on
   screen. Name each by the question it answers.
5. Buttons say what happens: "Save changes," "Send to the team," "Add location."
   Never "Submit," "OK," "Confirm."
6. Errors do three things: say what happened in plain words, say whether their
   data is safe, and give the next step. Never a code without a sentence. Never
   blame the user.
7. **Never conflate the three data systems.** Revel is sales. SkyTab is Yumsem
   scheduling and time clock. Reliable Payroll is payroll. A message that says
   "payroll sync failed" when Revel is down will send a GM to the wrong vendor.
   Name the actual system: "We couldn't reach Revel for Chamblee."
8. Numbers are formatted like money, not like data: `$4,182`, not `4182.00`.
   "Up $340 from last Tuesday," not "+8.85% WoW."
9. No filler: "Please note that," "In order to," "Simply," "Just," seamlessly,
   effortlessly, powerful, robust, cutting-edge, revolutionize, empower, unlock,
   supercharge.
10. Plan for Spanish. Keep strings in one file, no text baked into images, 30%
    width headroom for longer translations.

**Build a REWRITE TABLE for every string in the product.** The standard:

| Where | v54 says | Rewrite to |
|---|---|---|
| Nav | Labor Engine | Staff costs |
| Nav | Food Cost Engine | Food costs |
| Nav | Rent Burden Analyzer | Rent |
| Nav | Outcome Tracking | Did it work? |
| Nav | Specialist Leaderboards | What advice actually worked |
| Nav | Analytics Dashboard | How you're doing |
| Alert | Margin leak detected: labor variance | You're paying $380 a week more in staff than this store should |
| Alert | COGS variance exceeds configured threshold | You spent $412 more on food than usual this week. See what changed |
| Empty | No data available | No sales yet today. Numbers show up here as orders come in. |
| Error | Error: integration sync failed (code 502) | We couldn't reach Revel for Chamblee. Your sales are safe — we'll keep trying. Retry now |
| Error | Error 500: Internal server error | Something broke on our end — not your fault. Nothing you entered was lost. We're fixing it. |
| Outcome | Outcome recorded: positive delta | It worked. You saved $310 last week. |
| Settings | Configure integration settings | Connect your POS |
| Onboarding | Complete your onboarding flow | Let's get your first store set up |
| Confirm | Are you sure you want to delete this item? This action cannot be undone. | Delete the Tuesday lunch special? You can't undo this. |
| Button | Submit | Save changes |
| Loading | Loading… | Getting today's numbers… |

Apply the same treatment to every heading, label, tooltip, toast, empty state,
error, chat response template and email.

**GATE 4 — Post the complete rewrite table before applying it. Wait.**

---

## PHASE 5 — FUNCTIONALITY

- **Skeletons, not spinners**, for anything over 300ms, shaped like the content
  that's coming.
- **Optimistic updates with undo** — apply immediately, toast with "Undo" for 8
  seconds. This retires most "Are you sure?" dialogs; keep the dialog only for
  genuinely unrecoverable actions.
- **Autosave with a visible "Saved" marker** on any form over three fields.
- **Inline validation on blur**, saying how to fix it, next to the field.
- **Date-range presets first:** Today, Yesterday, This week, Last week, This
  month, Last month — then a custom picker. Nobody opens a calendar to see
  yesterday.
- **Every metric compares to a prior period** by default, with a toggle between
  "vs last week" and "vs last year."
- **Drill-down everywhere** — every summary number clicks through to the rows
  behind it, and every recommendation clicks through to the data that produced it.
- **Location switcher is global and persistent** — 8 locations, and a GM should
  never lose their place switching between them.
- **Export to CSV and a clean print/PDF layout.** These go to partners,
  accountants, and Omar. The repo already uses `docx` and `wkhtmltopdf` on the
  backend — wire the frontend to them rather than inventing a new path.
- **Sticky bottom action bar on mobile** so the primary action stays
  thumb-reachable.
- **Keyboard support:** `/` focuses search, `Esc` closes, arrows move in tables,
  `Cmd/Ctrl+S` saves. Tab order follows visual order.

---

## PHASE 6 — VERIFY BEFORE CLAIMING DONE

No success report without evidence:

- Screenshots of every screen at 390 / 768 / 1440.
- Contrast audit output showing every text/background pair passing.
- Lighthouse: Performance ≥ 90, Accessibility ≥ 95 on the main screens.
- **Real-content test** using real data: "Champion Pizza — Yonkers (319)" as the
  longest name, a six-figure dollar amount, a zero state, an error state, a
  200-row table, all 8 locations at once.
- `grep -rn -- '-\[' src/` returns nothing in components (no arbitrary Tailwind
  values left).
- Keyboard-only pass through the primary flow, plus one screen-reader pass.
- Tested on a real phone, not a resized browser window.
- Nothing marked "Restore" in the Phase 0 table has drifted back.

**Ship safely.** `design-baseline-v53` stays tagged. Put Phase 3+ behind a
Vercel preview deployment before promoting to production. I want a one-step
rollback, not another emergency.

**Report format.** Per phase: what changed, why (tied to a regression row, a
named defect, or my explicit request), before/after screenshots, and anything
you chose *not* to do and why. Flag every judgment call instead of burying it.

## ======== COPY TO HERE ↑ ========

---

# PROMPT 2 — THE AUDIT

Run this in a **fresh session**, ideally a different model, with the finished
branch checked out. An agent grading its own redesign will pass itself.

## ======== COPY FROM HERE ↓ ========

You are an independent design auditor. You did not build this and you have no
stake in it. Someone redesigned the PrimeOps restaurant-operations frontend
(React + Tailwind + Recharts + Framer Motion) after a bad release, against a
strict brief. Grade the result. Be skeptical — your value is in what you catch,
not in being agreeable.

Score each category out of the points shown. For every point deducted, cite the
specific file and line, or the screenshot region. No vague criticism.

**1. Restoration fidelity — 20 pts**
Diff the current branch against the pre-v54 baseline tag. Did anything the brief
marked "restore" fail to come back? Did the agent quietly keep v54 choices while
claiming to restore? Is Space Mono still on data and DM Sans still on UI text?

**2. Token discipline — 15 pts**
`grep -rn -- '-\[' src/` — any arbitrary Tailwind values left in components?
Any hardcoded hex, px font size, or shadow outside `tailwind.config.js`?
Deduct 3 points per category still leaking.

**3. Contrast and legibility — 15 pts**
Compute actual contrast ratios for every text/background pair. Body text below
4.5:1 or under 16px is an automatic 5-point deduction each. Check the chart
labels and axis ticks too — those get missed.

**4. State coverage — 15 pts**
For every screen, does an empty, loading, error and overflow state exist in the
code? Not "is it handled" — does it have a designed treatment? List every screen
missing one.

**5. Copy — 20 pts**
Grade against the brief's voice rules. Flag: any remaining software jargon;
any internal module name used as a nav label ("Labor Engine", "Rent Burden
Analyzer"); any error naming the wrong data system (Revel is sales, SkyTab is
Yumsem scheduling, Reliable Payroll is payroll); any button not saying what it
does; any error lacking what-happened / is-my-data-safe / what-next. Estimate
reading grade level and report it.

**6. Motion and charts — 10 pts**
Any Framer Motion mount animation on dashboard data? Any `layoutId` page
transition? Is `useReducedMotion` honored? Are Recharts tooltips custom or still
the unthemed default? Do bar charts start at zero? Is money formatted via
`tickFormatter`?

**7. The anti-slop check — 5 pts**
Gradient heroes, glassmorphism, frosted panels, centered marketing layout,
carousels, emoji-as-icons, thin font weights, bare icons without labels. Any one
present costs the full 5.

**Output:**
- A score per category and a total out of 100.
- The five most serious findings, each with file/line and a concrete fix.
- One section headed **"Changes that were not justified"** — anything altered
  that the brief did not ask for and that fixes no nameable defect. This is the
  failure mode that caused v54; hunt for it specifically.
- A verdict: SHIP, SHIP WITH FIXES, or DO NOT SHIP.

## ======== COPY TO HERE ↑ ========

---

# PROMPT 3 — THE LOCK

Run this last, in the working session. It converts the brief from a
conversation into enforcement, so v55 can't quietly drift back.

## ======== COPY FROM HERE ↓ ========

The redesign is approved. Now make it impossible to undo by accident. Create
enforcement that outlives this conversation.

**1. Write `DESIGN_RULES.md` at the repo root.** The non-negotiables, stated so
a new contributor or a future AI agent can follow them without this chat: the
Space Mono / DM Sans split and what each is for; the token-only rule (everything
in `tailwind.config.js`, no arbitrary values); 16px body minimum; 4.5:1 contrast
floor; the four required states per screen; one primary action per screen; never
meaning-by-color-alone; the Framer Motion constraints; the Recharts constraints;
the copy voice rules including the keep-restaurant-words / kill-software-words
list and the Revel-vs-SkyTab-vs-Reliable-Payroll distinction. Include the
do-NOT list verbatim.

**2. Reference it from `CLAUDE.md`** (create it if absent) so every future Claude
Code session in this repo loads the rules automatically. One line pointing at
`DESIGN_RULES.md`, plus the single sentence: "Restore first, improve second, and
never improve by inventing — every visual change needs a named defect."

**3. Add machine enforcement** that fails CI, not just advice:

- An ESLint rule or a `grep` check in CI that fails on arbitrary Tailwind values
  (`-\[` in `src/**/*.{jsx,tsx}`).
- A stylelint config banning raw hex outside `tailwind.config.js`.
- A contrast test: a small script that reads the token pairs from the Tailwind
  config and asserts every documented text/background combination clears 4.5:1
  (3:1 for large text). Fail the build on a regression.
- A Lighthouse CI budget: Performance ≥ 90, Accessibility ≥ 95 on the main
  routes.

**4. Add a PR template checklist** at `.github/pull_request_template.md` with the
short form: screenshots at 390/768/1440 for any visual change · no new arbitrary
values · four states present · contrast checked · copy follows
`DESIGN_RULES.md` · named defect for every visual change.

Show me each file before writing it. Keep the CI additions fast — if the checks
take more than a minute they'll get disabled within a month.

## ======== COPY TO HERE ↑ ========

---

## Appendix — voice cheat sheet

| Instead of | Say |
|---|---|
| Utilize / leverage | Use |
| Initialize / provision | Set up |
| Synchronize | Update |
| Configure | Set up, or Choose |
| Variance / threshold exceeded | You spent $412 more than usual |
| Cohort | Group of customers |
| Authentication failed | We couldn't sign you in |
| Invalid input | That date isn't in the past — pick another |
| Operation successful | Saved |
| Insufficient permissions | Only owners can change this. Ask Joe to do it. |
| Processing your request | Working on it… |
| Optimize your workflow | Get orders out faster |
| Actionable insights | What to fix this week |
| Revenue analytics | Sales |
| Labor cost variance | You spent $280 more on staff than planned |
| Outcome recorded | It worked — here's what you saved |

**The test:** read the sentence out loud to someone standing behind a counter.
If they'd need a follow-up question, rewrite it.

---

## Appendix — acceptance checklist

Paste as a follow-up when the agent says it's finished.

```
Before I accept this, confirm each with evidence:

[ ] Every row in the Phase 0 regression table is resolved — restored, or
    defended in one sentence
[ ] Space Mono is still on data, DM Sans still on UI text
[ ] Before/after screenshots at 390 / 768 / 1440 for every changed screen
[ ] grep -rn -- '-\[' src/ returns nothing in components
[ ] No hardcoded hex, px font size, or shadow outside tailwind.config.js
[ ] Contrast audit passes 4.5:1 body and 3:1 large/UI — paste the output
[ ] Body text is 16px or larger everywhere
[ ] Every screen has empty, loading, error and overflow states — screenshot all four
[ ] Exactly one primary action per screen, in a consistent position
[ ] No state is communicated by color alone
[ ] No Framer Motion mount animation on dashboard data; useReducedMotion honored
[ ] Recharts tooltips are custom, bars start at zero, money uses tickFormatter
[ ] Full string rewrite table applied — no internal module names in the nav
[ ] No error message names the wrong data system (Revel / SkyTab / Reliable Payroll)
[ ] Every button label says what happens
[ ] Every error says what happened, whether data is safe, and what to do next
[ ] Tested with all 8 real locations and real dollar amounts, not placeholder text
[ ] Keyboard-only pass through the primary flow completed
[ ] Tested on a real phone
[ ] Lighthouse Performance >= 90, Accessibility >= 95
[ ] design-baseline-v53 is tagged and rollback is one step
[ ] List everything you changed that was NOT in the regression table or my
    explicit requests, with the defect each one fixes
```
