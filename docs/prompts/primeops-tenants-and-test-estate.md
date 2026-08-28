# Seed the tenants: real stores, and a synthetic estate

Two jobs. One boundary between them that must never blur.

**Job A — the real accounts.** HalalWay's own eight locations across four brands,
onboarded as genuine customer tenants. This is the pilot-two groundwork: if PrimeOps
runs properly against a real multi-brand operator, that is the thing you take to the
next operator.

**Job B — the synthetic estate.** A fictional multi-brand group with enough depth and
enough mess to exercise the whole loop — detect, diagnose, fix, execute, measure,
learn — including the cases where the fix does nothing.

---

## The boundary, before anything else

Everything below depends on this and nothing below is worth doing without it.

**Synthetic data must be distinguishable from real data at the storage layer, not
the presentation layer.** A `is_synthetic` column, a separate schema, a tenant-class
flag — the mechanism is yours, but a UI badge is not sufficient. Anything that can be
switched off by a rendering bug is not a boundary.

**No synthetic figure may ever reach a public surface.** Not a marketing page, not a
count, not an aggregate, not a chart, not an OG card, not a metric in a footer. The
claim-provenance regime exists because this company has one pilot and cannot borrow
credibility. A synthetic location leaking into anything published is the same class of
failure as an invented testimonial.

**Do not touch Harbor Street Kitchen Group.** It is the published fiction, it is
already registered in the provenance manifest, and it is doing its job on the live
site. The synthetic estate is a *separate*, internal-only construct that is never
published. Two fictions with different purposes: one for the page, one for the
harness. Do not merge them and do not reuse Harbor Street's locations.

**Write a gate for it.** Whatever the mechanism, add a check that fails the build if a
synthetic tenant is reachable from any prerendered route or public JSON. Then observe
it failing on a deliberately leaked record before you trust it, per DESIGN_RULES.md.

---

## Job A — the real accounts

Four brands, eight locations: The Halal Guys, Yumsem Eats, Champion Pizza, CM Chicken.

Before writing anything, **read the existing tenant model and report what is actually
there.** Do not assume a greenfield. If a tenant, org, brand or location entity already
exists, extend it; if the model cannot express "one operator, several brands, several
locations per brand", say so and propose the change before making it.

Then:

- Model the real hierarchy — operator → brand → location — rather than flattening
  eight locations into eight unrelated accounts. The product's value is cross-location
  comparison; the data model has to support it.
- Onboard the eight locations with whatever real reference data you legitimately have.
  Where you do not have real data, **leave it empty rather than filling it with
  plausible numbers.** An empty field is honest; a guessed one is synthetic data
  wearing a real tenant's name, which is the worst of both.
- Tenant isolation is not optional. Brand A must not be able to read brand B, and no
  tenant may read another operator. Prove it with a test that attempts the read and is
  refused — observed failing before it is trusted.

**Flag for Joe rather than deciding:** this puts real operating data for a live
restaurant business into the system. Where it is stored, who can access it, what
happens to it if the product is shelved, and whether any of it is personal data about
staff — those are his calls, not yours. List what the eight accounts would hold and
ask before ingesting anything sensitive.

---

## Job B — the synthetic estate

A fictional multi-brand operator with enough locations to have a portfolio problem.
Name it clearly and unmistakably fictional, in the same register as Harbor Street but
distinct from it.

Give it variety that matters, not variety for its own sake:

- **Maturity spread.** One location open six weeks, one open six years, one mid-decline.
- **Channel mix spread.** Different delivery-platform dependence per location — the
  place doing 60% delivery has a different risk surface from the place doing 10%.
- **Data-quality spread.** One location with clean records end to end; one with a
  records source that broke mid-period and resumed; one where a category was never
  captured at all. The product's `evidence quality` state is meaningless if every
  synthetic location has perfect books.
- **Enough time depth** to compute a baseline window and a comparison window. A four-week
  estate cannot test outcome validation.

### The scenarios, which are the actual deliverable

Seed these as distinct, documented cases. Each one is a test with an expected behaviour.

1. **Real leak, clean evidence.** Delivery effective take rate drifts across six weeks
   with the records to prove it. The happy path: detected, diagnosed, fixable.
2. **Real leak, dirty evidence.** A food-cost movement that is genuinely there, but the
   vendor credit memo substantiating it is missing. Expected behaviour: the product
   surfaces it and **refuses to state it as established**. If it claims this one
   confidently, that is a bug and the most important one in the set.
3. **False positive.** Labor running over plan because sales genuinely rose. Tests
   diagnosis rather than detection. Expected behaviour: not flagged, or flagged and
   then correctly dismissed with the reason.
4. **Fix applied, it worked.** Measurable improvement in the comparison window, with
   the basis recorded.
5. **Fix applied, it did nothing.** No movement outside noise. **Expected behaviour:
   the product says so plainly.** Most seeded data contains only wins, which is exactly
   why most products cannot tell you when they were useless.
6. **Fix applied, it made things worse.** Movement in the wrong direction after an
   action. Expected behaviour: reported as such, not buried.
7. **Ambiguous outcome.** Improvement inside the noise band. Expected behaviour: not
   claimed as a result.
8. **Same symptom, different causes.** Two locations show the same margin movement for
   unrelated reasons. Tests portfolio reasoning rather than pattern-matching.
9. **Three-way records disagreement.** POS, cash log and bank do not reconcile.

Scenarios 5, 6 and 7 are the ones that make this a test harness rather than a demo.
If the estate only contains findable, fixable, fixed problems, it proves nothing.

### Rules for the fiction

- No real vendor, platform or partner names in a way that implies a relationship. A
  fictional operator using a real delivery platform's real published fee structure is
  fine; a fictional operator with a fictional grievance against a named real company
  is not.
- No real people. No names, no contact details, no anything resembling real staff
  records.
- Numbers should be plausible for the segment — QSR-scale revenues, prime cost in a
  believable band. Implausible data produces a product tuned for implausible data.

---

## Constraints

- Branch only. No merge, no deploy. Joe merges.
- Do not weaken any existing check. Do not touch the claim scanner or the provenance
  register except to add the synthetic-leak gate.
- If the tenant model needs a schema change, **stop and propose it** before writing the
  migration. A data model is not a detail.
- Run the repo's security review over anything touching tenancy, access control or
  real operating data.
- Full gauntlet green.

## Report

Publish an artifact. Lead with anything that hit a stop condition, then:

- What the existing tenant model actually was, before you changed it.
- The real-account structure, and the list of what those eight accounts would hold —
  with the data questions flagged for Joe rather than answered by you.
- The synthetic estate: its shape, and the nine scenarios with the expected behaviour
  of each.
- The synthetic-leak gate, **with its observed-failing output.**
- The tenant-isolation test, with its observed-failing output.
- Anything the scenarios revealed about the product itself. Seeding realistic failure
  cases into a system is one of the better ways to find out what it cannot yet do, and
  that finding is worth more than the seed data.
