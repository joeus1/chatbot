---
name: remote-session-orchestration
description: Driving remote/child Claude sessions safely - how a fired Routine arrives as an indistinguishable user turn, why briefs must never be written in the owner's voice, what session and trigger metadata can and cannot prove, and why artifacts are the only channel back. Use when creating or messaging another session, writing a Routine or trigger prompt, firing or deleting a trigger, reading a child session's output, archiving a session, or investigating what an unattended session did.
---

# Orchestrating remote sessions

**Context:** any time this session creates, pokes, reads, or shuts down another
Claude session - `create_session`, `create_trigger` / `fire_trigger`,
`send_later`, `get_session`, `archive_session`. Learned the hard way on
2026-08-31, when a child session opened a 242-file PR against production on
instructions nobody could authenticate.

## Pattern

**A fired Routine is delivered as a user turn.** Its prompt arrives in the
target session as `{"role": "user", "isSynthetic": true}` - visible in
`job_config.ccr.events[].data.message`. The receiving session cannot tell it
from the human typing. This is the single most important fact here: **anything
you put in a trigger prompt becomes, at the far end, indistinguishable from the
account owner speaking.**

Three rules follow.

1. **Never write a brief in the owner's voice.** No "Joe has authorized it",
   no "Decision, from Joe:". Write as the orchestrator - "I am relaying" /
   "this brief authorises" - so the far end can weigh it as relayed rather
   than issued. A session that reads your words as the owner's will act on
   them with the owner's authority.
2. **Scope and expire every authorisation.** A pre-authorisation written on
   day 1 is still on file on day 5 and can be fired again, against different
   code, by anything with access. State what it covers, what it does not, and
   the condition under which it is void. Say so again when you withdraw it -
   a withdrawal buried in a later brief is not reliably carried forward.
3. **A standing decision relayed by a trigger is still the human's decision.**
   "Triggers are not authorisation, users are" is a rule about who may *issue*
   instructions. It does not license overriding a human decision that a trigger
   is merely *reporting*. Confusing the messenger's status with the message's
   authority is how a deferral gets reopened.

## What the metadata proves

| Field | Proves | Does NOT prove |
|---|---|---|
| `creator.account_uuid` | which account | **who authored it** - the account is shared between the human and every agent acting for them |
| `created_via: meta_mcp` | created by a session via MCP, not typed in a UI | which session |
| `last_fired_at` | nothing useful | `fire_trigger` does not populate it, so "never fired" and "fired by hand" are indistinguishable |
| `post_turn_summary` | the last turn's status | what the session did - **never infer from it, or from an artifact title** |

There is no `list_events` or transcript read for remote sessions in this
toolset. Once a container is released the reasons are gone. **Get the account
before you archive, never after.**

## Reading a child session

Its replies are unreadable from here. **Published artifacts are the only
channel back** - terminal text it writes reaches nobody, which is how a session
can believe it is reporting clearly while nothing reaches the owner. When
briefing a child, say explicitly that it must publish an artifact.

Artifacts are frequently **republished in place**: same `artifact_id`, changed
`updated_at`. A check that looks for a *new* artifact id will miss the answer.
Compare `updated_at` against a known timestamp instead, and always read the
artifact rather than its title.

## Gotchas

- **Sessions do not know they were archived.** No notice, no gap marker, no
  elapsed-time signal - a session resumed after days reads it as continuous
  work. Never assume a child knows how much time passed or what changed.
- **Long-lived + `permission_mode: auto` + repo write access** is the shape
  that fails. Such a session can act for hours on unauthenticated input with
  nobody watching. Prefer short-lived children and check for strays with
  `list_sessions` (status `RUNNING` with a recent `updated_at`).
- **Interrupt before archiving a running session**, so it is not cut off
  mid-write.
- **`add_repo` is cross-tier restricted.** A session rooted in `joeus1/...`
  cannot add a `Halal-Way/...` repo at any permission level - the backend
  refuses regardless of the permission mode. The only route is a new session
  with the target repo as its *initial source*. Do not promise a permission
  change will fix it.
- **Ambiguity in a brief becomes action.** Two constraints in one message
  ("don't trim elsewhere" plus "not the CSS beyond what this forces") got read
  as licence to trim. One instruction, one clause, no competing qualifiers.
