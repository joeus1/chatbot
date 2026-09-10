# Independent AI on the PrimeOps website — go-live record

Joe asked for the Independent AI to be showing, live, and able to converse on
the PrimeOps website. On **2026-09-06** it was not: four hops of the customer
path were broken. On **2026-09-10**, after Joe added the DNS record and set the
Railway variables and the code-side work landed, every hop is connected and the
conversation route answers as an authenticated route should.

This session works from `joeus1/chatbot` and cannot attach the `Halal-Way/*`
repos (cross-owner `add_repo` refusal), so everything below is measured against
the deployed hosts, not read from those repos' source.

## The customer path, then and now

| Hop | 2026-09-06 | 2026-09-10 |
|---|---|---|
| Public site entry point | None anywhere on `www.getprimeops.ai` (release `a71958e`). | Release `7369c59`. Footer link "Ask PrimeOps in the workspace" → `/sign-in`, plus assistant copy on the access page and a paragraph in `llms.txt`. |
| Workspace → backend | `VITE_PRIMEOPS_API_BASE_URL` unset; app showed "This build has no API configured" and ran in Sample mode. | Rebuilt (`index-B5d5k9jW.js`). Calls a same-origin path `/primeops-api`, which proxies to the AEI backend. |
| `api.getprimeops.ai` | NXDOMAIN at the GoDaddy zone, despite being the compiled Auth0 audience. | `CNAME p01f0wdv.up.railway.app`. `/health` and `/ready` both 200. |
| AI conversation route | Every route but health/readiness returned `403 route_not_in_verified_boundary`. | `POST /aei/ai/converse` returns `401 unauthorized` without a token — the route is inside the verified boundary and auth-gated. |
| Spend cap | `daily_tenant_cap: 1.00` | `daily_tenant_cap: 25.00`, `max_invocation_cost: 0.50`, AI enabled. |
| AEI build | `1bf8415` | `fe7b19e` |

The workspace's own call, read out of the bundle: `POST /aei/ai/converse` with
`{message, history}`, an `Authorization: Bearer` token and an
`X-PrimeOps-Tenant-Id` header, expecting `{reply, outcome, degraded_reason}`.

## What is verified, and what is not

**Verified against the live hosts:** DNS resolution, backend readiness, the
raised cap, the same-origin proxy reaching the backend (`/primeops-api/ready`
returns the AEI payload), the conversation route being inside the boundary, and
the public site's entry point and `llms.txt` paragraph.

**Not verified:** an actual model reply. That needs a signed-in operator's
Auth0 token, which this session neither has nor should have. The 401 proves the
route is live and correctly refuses anonymous callers; it does not prove a
tenant gets an answer. **The remaining acceptance test is Joe's:** sign in at
`getprimeops.ai`, open the workspace, ask "What needs my attention before
dinner?", and confirm a reply plus movement in the AEI invocation counters.

## One judgement call left open

The public entry point is a **footer link only** — no nav item, no card, no
mention above the fold. That satisfies "showing" literally, and it is the
conservative choice given the assistant is advisory and holds no tools. Whether
it deserves more prominence is a product decision, not a defect, so it is
recorded here rather than changed.
