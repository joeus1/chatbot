# Fix brief — the assistant fails on any reply containing an em dash

Hand this to a session with `Halal-Way/primeops-aei` (and `primeops-site` if the
error-surfacing change lands there). This session works from `joeus1/chatbot`
and cannot attach those repos.

## The failure, as an operator sees it

Signed in at `app.getprimeops.ai` as tenant **HalalWay LLC**, asking the
built-in suggested question "Which store needs help first?", the Ask PrimeOps
panel returns:

```
The assistant could not answer. 'latin-1' codec can't encode character
'—' in position 10: ordinal not in range(256) Nothing was substituted.
```

`—` is an em dash. That message is a Python `UnicodeEncodeError`, rendered
verbatim into the operator's screen.

## What this rules in and out

**The plumbing is fine.** DNS, the same-origin proxy, Auth0, tenant scoping and
the `/aei/ai/converse` route all worked — the request got far enough to produce
or handle a string and then fail while encoding it. This is not a boundary,
auth, or routing problem.

**The user's input is not the source.** The question asked was
`Which store needs help first?` — pure ASCII, and no em dash anywhere in it.
The offending character therefore enters server-side: either in the model's
reply or in a string the backend composes.

**Latin-1 points at a header.** Python encodes HTTP header values as latin-1;
request and response bodies are UTF-8 by default. An `UnicodeEncodeError` for
latin-1 on a text path is the signature of non-ASCII text being placed in a
header, or of an explicit `.encode("latin-1")`.

## Where to look, in order

1. **Any header carrying model or tenant text** on the converse path — an
   attestation, audit, reason, or trace header. The workspace already sends
   `X-PrimeOps-Attestation` on decision calls, so header-carried prose is an
   established pattern in this codebase and is the first place to check.
2. **The outbound call to the model provider** — a system prompt, tenant label,
   or idempotency value passed as a header rather than in the body.
3. **Any explicit `.encode("latin-1")`** or a library pinned to it, including
   the SMTP/email path and the forensic-evidence writer, if either is touched
   during a converse turn.

`position 10` means the em dash is the eleventh character of whatever string is
being encoded, which should identify it quickly once the candidate strings are
in front of you.

## Severity

Em dashes are extremely common in generated prose. If this fires on the
model's reply, it breaks a large share of answers — possibly most of them.
Treat it as blocking for the assistant's go-live, not as a polish item.

## Second defect, same screenshot

The raw Python exception text reaches the operator's screen. Internal error
detail should be logged server-side and replaced with a plain sentence the
operator can act on, in the same register as the rest of the product's copy.
The existing "Nothing was substituted" phrasing is right and should stay; the
codec traceback should not be beside it.

## Acceptance

An operator signed in at `app.getprimeops.ai` asks "Which store needs help
first?" and gets a written reply containing an em dash, with the backend's
invocation counters moving. Add a regression test that sends a reply
containing `—` through the full converse response path.
