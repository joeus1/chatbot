# Independent AI on the PrimeOps website — go-live findings (2026-09-06)

Joe asked for the Independent AI to be showing, live, and able to converse on
the PrimeOps website. It is not, as of the probe below. This records exactly
where the customer path breaks and who can fix each break. Written from the
`joeus1/chatbot` session, which cannot attach the `Halal-Way/*` repos
(cross-owner `add_repo` refusal), so nothing here was changed in those repos.

## What "the website" resolves to

The public site `https://www.getprimeops.ai/` (Halal-Way/primeops-site, Vercel,
release `a71958e`) has **no chat, no assistant, no AI entry point** anywhere:
not in the HTML, not in `assets/main-*.js`, not in `llms.txt`. Its only
serverless route is `POST /api/pilot` (the consultation form). "Start PrimeOps"
goes to `/create-account`, whose page links out to the workspace app and the
AEI signup page.

The AI lives one hop further, in the customer workspace
`https://primeops-workspace-production-production.up.railway.app/` (Auth0
sign-in, routes `/app/today` … `/app/help`). Its bundle carries the
"Ask PrimeOps for help" panel ("Ask about the selected store, number, issue,
action, or source record using text or voice").

## Where the path breaks

| Hop | State | Evidence |
|---|---|---|
| 1. Public site → AI | **Absent.** No link, card, or widget mentions the assistant. | `main-DRVx_Zlb.js` has no chat/assistant strings; only `/api/pilot`. |
| 2. Workspace build → backend | **Unconfigured.** `VITE_PRIMEOPS_API_BASE_URL` was unset at build time, so after sign-in the app shows "This build has no API configured" and runs in Sample mode with synthetic data. | `index-CxEZArfa.js`: the only backend URL literal is the Auth0 audience; the "no API configured" page is compiled in. |
| 3. `api.getprimeops.ai` | **Does not exist in DNS.** NXDOMAIN at the GoDaddy zone (`ns09.domaincontrol.com`). It is the Auth0 audience the workspace is built with. | `cloudflare-dns.com` query → status 3; `www` and apex resolve fine. |
| 4. AEI backend (Railway) | **Healthy but sealed.** `/ready` reports build `1bf8415`, `ai.enabled: true`, `daily_tenant_cap: 1.00`, `routes_declared: 1`. Every other route, with or without a bearer token, returns `403 {"error":"route_not_in_verified_boundary"}`; OpenAPI lists only `/health` and `/ready` ("PrimeOps AEI Recovery Gateway"). | Probed `/api/primeops/chat`, `/api/ai/chat`, `/v1/ai/ask`, `/api/tenants/me` and ten others. |

Auth0 itself answers (`/.well-known/openid-configuration` → 200).

## Context from the earlier session

Session "Independent AI module for customers" (2026-09-05, sources: chatbot,
primeops-site, primeops-aei; branch `claude/independent-ai-module-hcp5k8`)
reported "AI path live on claude-opus-5, production `1bf8415` smoked & ready"
and stopped on one human action: **raise `DAILY_SPEND_CAP` to $25.00 in
Railway**. That matches the `/ready` output (`daily_tenant_cap: "1.00"`). Its
"live" claim is about the backend AI path, not about anything a customer can
reach from the website. Nothing from that branch was pushed to `joeus1/chatbot`.

## What has to happen, and by whom

Human-only (credentials this and any Claude session lack):

1. **DNS**: create `api.getprimeops.ai` at GoDaddy pointing at the AEI Railway
   service (and add it as a custom domain on that service), or change the
   workspace's Auth0 audience and API base to the Railway hostname instead.
2. **Railway**: set `VITE_PRIMEOPS_API_BASE_URL` on the workspace service and
   redeploy it; raise `DAILY_SPEND_CAP` on `primeops-aei` if the $25 figure is
   approved.

Code, in a session with `Halal-Way/primeops-site` + `Halal-Way/primeops-aei`
attached (PRs, not direct pushes — merging to `main` deploys):

3. **Gateway boundary**: declare the AI conversation route inside the AEI
   "verified boundary" so it stops returning `route_not_in_verified_boundary`
   for authenticated tenants. Verify with a real Auth0 token, not a guess.
4. **Workspace**: make "Ask PrimeOps" fail loudly when the API base is unset
   (today it silently degrades to Sample mode), and smoke a real turn end to
   end after 1–3 land.
5. **Public site**: add a visible entry point for the assistant (a nav item
   or card on `/`, and a line in `llms.txt`), pointing signed-in operators to
   the workspace panel. Keep the public site itself chat-free unless a
   separate decision funds an unauthenticated assistant with its own cap.

Acceptance: an operator opens getprimeops.ai, reaches the workspace, signs in,
asks "What needs my attention before dinner?" and gets a model reply that the
AEI `/ready` invocation counters reflect.
