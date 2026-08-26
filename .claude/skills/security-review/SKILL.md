---
name: security-review
description: Security checklist and patterns - use when adding authentication, handling user input, touching payments or secrets, creating API endpoints, or working with tenant data.
---

# Security Review

Run through this checklist whenever code touches input, identity, money, or secrets. For a full audit, delegate to the security-reviewer agent.

## Input

- Every external input (request body, query params, headers, webhooks, file uploads, LLM output used as data) is validated at the boundary - pydantic/zod schema, allowlist over blocklist.
- SQL through bound parameters only; never f-strings/template literals into queries.
- Shell: avoid `shell=True`/string-built commands; pass argument arrays. User input never becomes a file path without normalization + prefix check.
- Rendered output escaped by default; `dangerouslySetInnerHTML`/`innerHTML`/`v-html` need sanitization and a justification.

## Identity & access

- Every new endpoint declares its auth requirement explicitly - "forgot to add the dependency" must be impossible to miss in review.
- Authorization is object-level: check the caller owns/belongs to the resource id in the request, not just that they're logged in.
- Multi-tenant queries always scoped by tenant id from the session - never from the request body.
- Sessions/tokens: expiry set, rotation on privilege change, `secrets` module (not `random`) for anything guessable, constant-time comparison for secret values.

## Money

- Server computes all amounts; client-sent prices are display-only.
- Webhook handlers verify signatures (Stripe: `stripe.Webhook.construct_event`) and are idempotent - duplicate delivery must not double-charge or double-credit.
- Refund/credit paths get the same authz scrutiny as charge paths.

## Secrets & data

- No secrets in code, logs, error messages, or client bundles (`VITE_`-prefixed vars ship to the browser - treat them all as public).
- A secret that ever hit a commit is burned: rotate it; deleting the line does not un-leak it.
- Errors to clients are generic; details go to server logs. PII kept out of logs.
- CORS: explicit origins, not `*`, when credentials are involved.

## Fetching & dependencies

- Server-side fetches of user-supplied URLs need an allowlist (SSRF).
- New dependencies: check the package is the real one (typosquatting), maintained, and pinned by the lockfile.
