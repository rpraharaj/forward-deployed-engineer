---
name: enablement-handoff
description: Teach the receiving team to operate and extend what you built, rather than only documenting it - pairing, walkthroughs, deliberately leaving work for them to finish, and confirming they can actually run it without you. Use when an engagement is ending and the team must continue without you, when you have been building alone and knowledge has concentrated, when a team will inherit something unfamiliar, or when the real deliverable is a capable team rather than working code. Distinct from handover-pack, which produces documents.
---

# Enablement handoff

Leaving a team that can carry on.

## Why this exists

`handover-pack` produces documents. Documents are necessary and they are not sufficient — a team can hold a complete, accurate handover pack and still be unable to operate what you built, because reading a runbook and having executed one are different states.

For many engagements the *actual* deliverable is a team that can continue. The code was never the point; the point was capability that persists. Where that's true and you optimize for shipping instead, you produce a technically successful engagement that decays the month you leave.

The mechanism that causes this is worth naming: an FDE working efficiently works alone, and every efficient solo week concentrates knowledge further. By the end you're the only person who understands the thing you were hired to make sustainable. Enablement has to be designed in from the middle of the engagement, because at the end it's too late.

## When this applies

- An engagement is ending and the team must continue
- You've been building alone and knowledge has concentrated
- A team is inheriting something unfamiliar
- The real deliverable is capability, not code
- **From the midpoint of the engagement**, not the end

## When it doesn't

- Genuinely throwaway work
- The receiving team already knows this domain better than you
- Nobody is receiving it — which is a finding to escalate, not a reason to skip this
- You need documents rather than capability — that's `handover-pack`
- Intended end users need to adopt a changed business process — that's `adoption-plan`; technical-team enablement can run alongside it

## Prerequisites

Resolve `<workspace>` before reading or writing artifacts: read `../_shared/workspace-conventions.md` and follow its location and header rules. All artifact paths below use that resolved workspace. Preserve existing sections when appending.

`<workspace>/02b-ownership.md`, `<workspace>/01-environment.md`, and any runbooks — you need to know who is inheriting this and what they must operate. **Do not wait for `09-handover.md`.** Enablement starts at the midpoint; the handover is written at the end and *links* here.

## Procedure

### 1. Work out what they must be able to do

Not "understand" — **do**. Concrete, verifiable capabilities:

- Run it locally and make a change
- Deploy it, and roll it back
- Diagnose the common failure
- Extend it in the way it's most likely to need extending
- Know when to ask for help, and whom

That last one is legitimate and often skipped. A team that knows the boundaries of its own understanding is in far better shape than one that doesn't know what it doesn't know.

Write the list. It's the syllabus, and without it enablement becomes a vague series of chats.

### 2. Find out what they already know

Ask, don't assume. The gap between "this team has never seen this framework" and "this team wrote the surrounding system and just doesn't know this component" is enormous, and teaching to the wrong assumption wastes everyone's time and is mildly insulting in both directions.

Also establish who has **capacity**. Enablement targeted at someone with no time to absorb it is theatre. Better to enable one person properly than to brief five who won't retain it.

### 3. Stop doing the work yourself, from the midpoint

The behavioral change that matters most, and the hardest.

From roughly the midpoint, deliberately **leave work for them**. Not the trivial parts — genuine, representative pieces, done with your support rather than by you. It will be slower. That's the point: the slowness is the transfer.

Concretely:

- Pair on a real change rather than demonstrating one
- Let them drive; you navigate. Sit on your hands.
- Give them the second, third, and fourth instances of a pattern after you did the first
- Have them write a runbook step and then execute it
- Review their work rather than doing it

An FDE who delivers everything personally has optimized for the wrong outcome, and it's the single most common failure of this kind of engagement.

### 4. Walk through, don't present

For each capability on the list, have **them** do it while you watch. Not a demo, not a slide deck — hands on keyboard, following the documentation, with you saying as little as possible.

You'll find gaps immediately: a runbook step that doesn't work as written, an assumption you never noticed making, a piece of terminology only you use. Fix them there and then.

The uncomfortable silences are productive. Resist filling them by taking over.

### 5. Rehearse the things that only happen under pressure

Deploy and rollback specifically. Reading a rollback procedure and having executed one are different states of readiness, and the difference only shows at 2am.

Have them run the deploy to a lower environment, and run the rollback. Time it. This doubles as the rehearsal `deploy-runbook` and `release-readiness` require, so it's free.

Where a realistic incident can be simulated cheaply, do that too — break something in staging and let them diagnose it.

### 6. Transfer the relationships, not just the knowledge

You've built connections the team may not have: the person in the platform team who answers quickly, the DBA who explained the locking behavior, the contact at Team D.

Introduce them explicitly, in writing, before you leave. A warm introduction costs one message and saves the receiving team weeks of finding the right person by trial and error.

Record these in `02b-ownership.md` so they survive the introduction.

### 7. Confirm rather than assume

Enablement has an actual test: **can they do the things on the list, without you, while you're still available to watch them fail?**

Check it before you leave, not after. The purpose of confirming early is that there's still time to fix what the check reveals.

Where they can't yet, that's information — say so plainly in the handover, with what's still needed. An honest "the team cannot currently roll this back unaided" is far more useful than a handover implying otherwise, and it's the kind of thing a delivery lead can still act on.

## Output template

Write to `<workspace>/09b-enablement.md`. `handover-pack` links here; do not merge the two templates into one file.

```markdown
# Enablement — <engagement>

**Engagement:** <name>
**Receiving team:** <names> · **Author:** FDE · **Date:** <YYYY-MM-DD>
**Status:** in progress | confirmed
**Source revision:** <repo>@<short SHA>
**Confidence:** what they have demonstrated vs. what you only discussed

## Capability checklist

| # | They can… | Method | Confirmed | Notes |
|---|---|---|---|---|
| 1 | Run locally and make a change | Paired on R2 | ✅ 03-14 | M. Chen and T. Nakamura both |
| 2 | Deploy to staging | They ran it, I watched | ✅ 03-18 | 12 min, matched the runbook |
| 3 | Roll back | Rehearsed in staging | ✅ 03-19 | 4 min |
| 4 | Diagnose the common failure | Simulated pool exhaustion | ✅ 03-20 | Found it in ~15 min |
| 5 | Extend to a new currency | They did GBP unaided | ✅ 03-21 | PR #431, no help needed |
| 6 | Know when to escalate | Discussed; boundaries written down | ⚠️ partial | See "still needed" |

## Work they completed
<What they did rather than you. The real evidence of transfer.>

- GBP currency support — PR #431, entirely theirs
- Deploy runbook steps 4–8 — written by T. Nakamura after running it

## Relationships transferred
| Who | For what | Introduced |
|---|---|---|
| J. Okafor, Platform | Registry and pipeline questions | ✅ 03-15, in #payments |
| S. Mehta, DBA | Schema changes, locking | ✅ 03-17 |

## Still needed
<Honest. What they can't yet do unaided, and what would close it.>

- Nobody has run a production deploy — staging only. First prod deploy should be paired with the release engineer.
- The reconciliation interaction is understood by one person. Single point of failure.

## Boundaries
<What they should escalate rather than attempt, and to whom.>
```

## Common traps

**Leaving enablement to the end.** By then knowledge has concentrated for months and there's no time to redistribute it.

**Doing the work because it's faster.** It is faster, and it's the wrong optimization. The slowness of pairing is the transfer.

**Presenting instead of watching.** A demo teaches you what you already know. Their hands on the keyboard teaches you both.

**Filling the silences.** When they're stuck, wait. Taking over ends the learning.

**Enabling people with no capacity.** One person properly is worth five briefed.

**Assuming what they know.** The gap between "never seen this" and "wrote the surrounding system" is enormous.

**Only enabling the happy path.** Rollback and diagnosis are what they'll need under pressure, and reading isn't rehearsing.

**Not transferring relationships.** A warm introduction costs one message and saves weeks.

**Claiming enablement without checking.** It has an actual test. Run it while there's still time to act on the result.
