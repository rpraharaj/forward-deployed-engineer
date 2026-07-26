---
name: handover-pack
description: Consolidate an engagement into what the receiving team actually needs - refreshed CLAUDE.md, runbooks, ADRs, known issues, and explicitly the open risks and unfinished business that most handovers omit. Use when an engagement is ending, when rotating to another team, when someone else will take over work in progress, or when you want the work to survive your departure. Write it before the last week, not during it.
---

# Handover pack

Making the work outlive you.

## Why this exists

An FDE leaves. That's the defining feature of the role, and it means an engagement is only as valuable as what remains after you go.

The default handover is a meeting and a link to a branch. Three months later the team has drifted from the design, doesn't know why a decision was made, has re-broken something you fixed, and is quietly working around a flag nobody dares remove.

The section that matters most is the one almost every handover omits: **the open risks and unfinished business.** Handovers get written to look like successful conclusions, so the awkward parts — the untested rollback, the consumer who never replied, the assumption nobody validated — get smoothed away. Those are precisely what the receiving team needs, and precisely what they can't reconstruct.

## When this applies

- An engagement is ending or you're rotating off
- Someone else takes over work in progress
- A contract or phase boundary
- **Two weeks before you leave**, not in the final days

## When it doesn't

- Short engagements where the artifacts already are the handover — point at `.fde/` and walk them through it
- Work that will genuinely never be touched again, which is rarer than it seems
- Teaching the team to operate what you built — that's `enablement-handoff`, and it's a different activity that should happen alongside this

## Prerequisites

The `.fde/` workspace. This skill consolidates rather than creates — if the artifacts were kept as you went, this is an afternoon. If they weren't, it's a week, and it'll be worse.

## Procedure

### 1. Start two weeks out

The single most important instruction. A handover written in the final days is rushed, and the final days are exactly when people want your time for other things.

Starting early also means you can **test it**: give it to someone and watch them try to use it. Every gap they hit is one you can still close.

### 2. Identify who's actually receiving it

Handovers written for a generic reader help nobody. Establish specifically: who maintains this now, what do they already know, and what have they never seen?

A team that built the surrounding system needs a completely different document from a team inheriting something foreign. Where the receiving team doesn't exist yet — genuinely common, and a real risk — say so prominently. An unowned system is the finding, not a gap in your document.

### 3. Refresh `CLAUDE.md` first

The highest-return artifact, because it loads automatically for anyone using Claude Code on this repo. Everything in it is knowledge nobody has to look up.

Update: build and test commands including the workarounds, the layout map, conventions that differ from the language default, landmines, and where things live. Keep it under about 200 lines — see `context-strategy` step 6.

Where the repository had a `CLAUDE.md` before you, keep its voice and structure. This is a contribution to their file, not a replacement.

### 4. Consolidate the durable artifacts

Not everything in `.fde/` is worth keeping. Sort it:

**Keep and promote into the repository proper:**
- Runbooks — deploy, rollback, cutover. These get used.
- ADRs — the reasoning behind decisions, which is unreconstructable
- The system map, if it's still accurate
- Environment setup and its workarounds

**Keep in the workspace:** feasibility, blast radius, verification records. Historical evidence, occasionally consulted.

**Mark superseded:** anything now inaccurate. Don't delete it — mark it, with a pointer to what replaced it. See `../_shared/workspace-conventions.md`. A stale document that looks current is worse than a missing one.

**Check citations.** An artifact full of `file.java:88` references against a revision that has moved on is misleading. Either re-verify the load-bearing ones or note the drift in the header.

### 5. Write the open risks section honestly

The part that earns the document. Everything you know that could bite them:

- **Unverified assumptions** — every `[unverified]` still open, and what would resolve it
- **Known issues** you didn't fix, and why
- **Feature flags** still in place, who owns removing them, and what happens if they're flipped
- **Deferred work** and what happens if it stays deferred
- **Fragile areas** — where you'd be careful, and why
- **Dependencies** you never got answers on
- **Things you'd do differently**, which is the most useful and least written thing in any handover

Resist the urge to make this section look tidy. A handover that reads as a clean success and omits three known risks is a document that will be resented in month two.

### 6. Say what only you currently know

There's always tacit knowledge — the thing that isn't in any artifact because it never fit anywhere. The quirk in the deploy that needs a wait between steps. The person who actually knows the batch job. The reason the retry count is what it is.

Write a plain list. It doesn't need structure; it needs to exist.

This is the inverse of `knowledge-interview` — you're now the person with context nobody else has, and the same problem applies.

### 7. Walk someone through it

Live, with the person receiving it, using the document. Not a presentation — have them navigate while you watch.

You'll find gaps immediately: things you assumed were obvious, terminology only you use, a runbook step that doesn't work as written. Fix them while you still can.

If nobody is available for this, note it. A handover nobody has walked through is untested, and should say so.

### 8. Leave a way to be reached, honestly

State what you're realistically available for and for how long. A vague "let me know if you need anything" is worse than "I can answer questions for two weeks; after that, contact <name>."

Being honest about the limit is kinder than an open offer you won't be able to keep.

## Output template

Write to `.fde/09-handover.md`:

```markdown
# Handover — <engagement>

**Engagement:** <name>
**Author:** FDE
**Date:** <YYYY-MM-DD>
**Receiving:** <team / person> · **Walked through:** <date, with whom, or "not yet">
**Source revision:** <repo>@<short SHA>

## What was done
<Three or four sentences. What changed, what state it's in.>

## Current state
| Item | Status | Notes |
|---|---|---|
| R1 multi-currency refunds | Live since 03-19 | Flag `refund-currency` at 100% |
| R2 contract v2 | Live | Team D still on v1; no deadline agreed |
| R3 reporting | **Not built** | Descoped — data unavailable, see ADR-0009 |

## Open risks — read this section

| # | Risk | Impact if it lands | What would resolve it | Owner |
|---|---|---|---|---|
| 1 | Recon job may parse the refund payload positionally — never confirmed | Silent failure at month-end | 1h reading `finops-batch` once access is granted | **unowned** |
| 2 | Flag `refund-currency` still in place | Two code paths; cleanup never done | Remove after 30 days clean | <name> |
| 3 | Team D never confirmed contract compatibility | Coordinated release needed if they have a strict parser | Get a response | <name> |

## Known issues not fixed
| What | Why not | Where |
|---|---|---|

## Fragile areas
| Where | Why | What to do instead |
|---|---|---|

## Things only I currently know
<Plain list. Tacit knowledge that fits nowhere else.>

- The staging deploy needs ~90s between migration and app deploy or health checks fail. Not documented anywhere; found the hard way.
- R. Silva (left the company) wrote the recon job — M. Chen in finance has the most context on what it produces.

## Where everything is
| What | Where |
|---|---|
| Working aid for Claude Code | `CLAUDE.md` |
| Deploy + rollback | `.fde/runbooks/deploy-refund-currency.md` |
| Decisions and why | `.fde/adr/` |
| System map | `.fde/02-system-map.md` |

## Superseded
<Artifacts no longer accurate, and what replaced them.>

## What I'd do differently
<Honest. The most useful section and the least written.>

## Contact
Available for questions until <date>. After that: <name>.
```

## Common traps

**Writing it in the last week.** Rushed, and competing with everything else people want from you.

**Omitting the awkward parts.** The three known risks you smoothed away are what the team needs, and leaving them out is noticed in month two.

**Writing for a generic reader.** Establish who's actually receiving it and what they already know.

**Not walking someone through it.** Untested documentation, and the gaps are invisible to the author.

**Leaving stale artifacts unmarked.** A document that looks current and isn't is worse than a missing one.

**Not saying who owns the flag.** It'll be there in three years and nobody will dare remove it.

**Skipping the tacit knowledge.** It doesn't fit anywhere, which is exactly why it needs its own list.

**No "what I'd do differently."** The most valuable section, and the one people skip because it feels like admitting fault. It isn't — it's the last piece of judgment you can hand over.

**A vague offer of future help.** Give a real date. It's kinder than an offer you can't keep.
