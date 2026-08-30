# Phase 13 — remove the `PRIMEOPS_SUPABASE_URL` fallback

Joe has asked for this directly. It is retirement step one, exactly as the ADR
named it. It is also a change to a live production route, so the order below is
not advisory.

## The line

```js
export default process.env.PRIMEOPS_SUPABASE_URL
  ? createSupabasePlatformHandler()
  : createPlatformHandler()
```

## Establish this before you change anything

**Is `PRIMEOPS_SUPABASE_URL` actually set in the deployed environment?**

That question decides whether this change is a safe cleanup or an outage.

- If it **is** set, production is already on `primeops_live` and removing the
  fallback changes no runtime behaviour. That is the good case, and the change
  is then a guard against a future unset.
- If it is **not** set, production is *currently being served by the legacy
  handler*, and removing the fallback takes the platform API down the moment it
  deploys. In that case **STOP AND SAY SO.** Do not make the change. The
  correct order is then: Joe sets the variable, confirms the API still works on
  the Supabase path, and only then is the fallback removed.

If you cannot determine the deployed value from the repository, Vercel config,
or anything else you can legitimately read — **say that, and stop.** Do not
infer it from the presence of the variable in an example file, a CI config, or
a `.env.example`. Those describe intent, not the deployed state. Guessing here
is how a live API goes dark.

## What "remove the fallback" means

Not this:

```js
export default createSupabasePlatformHandler()
```

That trades a silent wrong route for a silent failure — the handler gets
constructed with no URL and the route breaks in whatever way that library
happens to break. The finding was never "the fallback is ugly"; it was that an
unset variable produces the wrong behaviour **without saying so**.

So: when the variable is missing, the route must **fail closed and loudly**.
Refuse the request with an unambiguous server-side error naming the missing
variable, log it, and return a response that makes the cause obvious to whoever
is looking at it. A missing configuration should be impossible to mistake for a
working system — which is precisely what the current fallback made it.

## Scope

- **Only the routing decision changes.** Do not delete `createPlatformHandler`,
  its pool, the legacy module, or anything else in the retirement inventory.
  Those are later steps with their own review. This change removes one branch
  of one ternary and adds a guard.
- **Its own branch**, cut from whatever actually flows to production — establish
  which that is and say so, rather than assuming. Do not put this on
  `seed/synthetic-estate`: a production API fix has no business riding in the
  estate branch.
- **No PR, no merge, no deploy.** Joe merges, as with everything else. This one
  especially: it is the change most likely to be felt in production.

## Observed failing first

The rule has caught real defects all engagement and it applies here.

1. With the variable unset, show a request reaching the **legacy** handler.
   That is the defect, demonstrated rather than asserted.
2. Make the change.
3. With the variable unset, show the same request **refused with the explicit
   error**, not silently served and not obscurely crashed.
4. With the variable set, show the request served by the Supabase handler
   exactly as before — the change must be a no-op on the healthy path.

Step 4 is the one that proves you have not broken the working case, and it is
the one most likely to be skipped.

## Report

Publish an artifact. Lead with the answer to the deployed-variable question,
because that determines whether anything was changed at all. Include all four
observations, the branch and base you used, and confirmation that nothing else
in the retirement inventory was touched.
