# Fix brief — a latin-1 encode failure blocks the assistant's replies

Hand this to a session with `Halal-Way/primeops-aei` (and `primeops-site` if the
error-surfacing change lands there). This session works from `joeus1/chatbot`
and cannot attach those repos, so nothing below was read from that source — it
is inferred from the deployed behaviour and from the workspace bundle.

## Before you start: the live screen cannot tell you it is fixed

The AEI backend redeployed after this was observed — build `fe7b19e` on
2026-09-10, build `c0d3b2c` on 2026-09-13 — and nobody has re-tested. So the
defect may already be gone.

**Do not settle that by asking the assistant a question.** A reply that comes
back proves only that *that* reply was ASCII; the model may simply not have
used an em dash. A live ask can confirm the bug is still present, but it can
never confirm it is gone.

The conclusive check forces the character instead of hoping for it, and it does
not need a token or a signed-in screen — which matters, because the session
reading this has the repo and no Auth0 credentials:

> Exercise the converse response path with a reply string that contains
> `U+2014`, by stubbing the model client to return one. If that path encodes
> and returns it intact, the defect is gone; if it raises, it is still live.

Write that as the regression test either way (see Acceptance). If the path
already handles it, confirm a test pins the behaviour and stop; if it raises,
everything below applies.

## The failure, as an operator saw it

Signed in at `app.getprimeops.ai` as tenant **HalalWay LLC**, asking the
built-in suggested question "Which store needs help first?", the Ask PrimeOps
panel returned:

```
The assistant could not answer. 'latin-1' codec can't encode character
'\u2014' in position 10: ordinal not in range(256) Nothing was substituted.
```

`\u2014` is how Python escapes an em dash in an exception message, so that
is the form to grep logs for, not the character itself. The message is a
`UnicodeEncodeError`, rendered verbatim into the operator's screen.

## What this rules in and out

**The plumbing is fine.** DNS, the same-origin proxy, Auth0, tenant scoping and
the `/aei/ai/converse` route all worked — the request got far enough to hold a
string and then fail while encoding it. This is not a boundary, auth, or
routing problem.

**The user's input is not the source.** The question asked was
`Which store needs help first?` — pure ASCII, no em dash anywhere in it. The
offending character enters server-side.

**Beyond that, the source is open.** It is either the model's reply or a string
the backend composes; the evidence does not separate those, and the ordering
below is by likelihood, not by proof.

**Latin-1 points at a header.** Python encodes HTTP header values as latin-1;
request and response bodies are UTF-8 by default. A latin-1
`UnicodeEncodeError` on a text path is the signature of non-ASCII text being
placed in a header, or of an explicit `.encode("latin-1")`.

## Where to look, in order

1. **Any header carrying model or tenant text** on the converse path — an
   attestation, audit, reason, or trace header. The workspace already sends
   `X-PrimeOps-Attestation` on decision calls, so header-carried prose is an
   established pattern here and is the first place to check.
2. **The outbound call to the model provider** — a system prompt, tenant label,
   or idempotency value passed as a header rather than in the body.
3. **Any explicit `.encode("latin-1")`** or a library pinned to it, including
   the SMTP/email path and the forensic-evidence writer, if either is touched
   during a converse turn.

`position 10` means the em dash is the eleventh character of whatever string is
being encoded, which should identify it quickly once the candidate strings are
in front of you.

## Severity

Em dashes are extremely common in generated prose. If this fires on the model's
reply, it breaks a large share of answers — possibly most of them. Treat it as
blocking for the assistant's go-live, not as a polish item.

## Second defect, same screen

The raw Python exception text reaches the operator. Internal error detail
should be logged server-side and replaced with a plain sentence the operator
can act on, in the same register as the rest of the product's copy. The
existing "Nothing was substituted" phrasing is right and should stay; the codec
traceback should not be beside it.

## Acceptance

Two gates, and the deterministic one carries the weight:

1. **Forced, and required:** a regression test drives a reply containing
   `U+2014` through the full converse response path and gets it back intact.
   This is what proves the fix, and it runs without a token.
2. **Live, and corroborating only:** an operator signed in at
   `app.getprimeops.ai` asks "Which store needs help first?" and gets a written
   reply, with the backend's invocation counters moving. Passing this does not
   by itself prove the defect is fixed, for the reason given at the top.
