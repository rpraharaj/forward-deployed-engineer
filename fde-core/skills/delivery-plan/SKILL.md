---
name: delivery-plan
description: Sequence work by risk rather than convenience - unknowns first so bad news arrives early, slices that are independently shippable, dependencies on other teams surfaced with lead times, and an explicit statement of what would change the plan. Use once feasibility and estimation exist and someone wants an order of work or a schedule, when replanning after a slip, or when a plan exists but nobody has said what would invalidate it. Produces the sequence, not the sizing.
---

# Delivery plan

The order of work, and what would change it.

## Why this exists

Most plans are sequenced by convenience: easiest first, or in the order the requirements were written. That feels productive and it systematically defers the moment you discover the plan was wrong.

The alternative is to sequence by **risk**, so the things most likely to invalidate the plan happen first. It feels slower in week one and it is dramatically cheaper, because a plan that breaks in week one can be re-planned while everyone still has options. The same break in week six is a crisis.

For an FDE there's a second reason. Your credibility rests on being predictable. Delivering something small early, then re-planning honestly when a fact changes, builds more trust than a confident plan that holds until it collapses.

## When this applies

- Feasibility and estimation exist and someone wants a sequence
- Replanning after a slip or a changed fact
- A plan exists but nobody has said what would invalidate it
- Work spans multiple teams or a release window

## When it doesn't

- A single change with no meaningful sequencing decision
- Feasibility hasn't been done — the plan would be fiction
- The question is sizing, not order — that's `estimation`

## Prerequisites

- `.fde/04-feasibility.md` — shapes, sites, deceptive costs
- `.fde/05b-estimate.md` — sizing, if it exists
- `.fde/06-blast-radius-*.md` — coordination needs
- `.fde/00b-access.md` — blocked access is a dependency with a lead time

## Procedure

### 1. Rank by what could invalidate the plan

For each piece of work, ask: **if this goes badly, how much of the rest changes?**

Highest-risk-first means putting these early, regardless of size:

- Every `[unverified]` item from feasibility
- Anything depending on another team's answer or work
- Anything touching a published contract or shared data
- Anything you've never done in this organization — including the first deploy, which is a risk in itself
- Anything with a long lead time, even if it's needed late

**The first deploy deserves specific attention.** Getting something trivial through the entire pipeline — build, review, approval, release window, production — early in the engagement tells you what the real overheads are. Discovering the deploy path in week six, when it turns out to need a CAB submission with ten working days' notice, is a self-inflicted crisis.

### 2. Slice so that each piece is independently shippable

Each slice should be releasable on its own, even behind a flag. Three reasons: it forces the integration problems to surface early, it means a pause leaves the system in a good state, and it means partial delivery is still delivery.

Good slices are **vertical** — a thin path through every layer — not horizontal. "All the database work" is not a slice; it delivers nothing and proves nothing. "One currency working end to end" is.

Where something genuinely cannot be sliced, say so and explain why. That's a risk in its own right.

### 3. Surface dependencies with lead times, not just names

For each dependency on another team, record what you need, from whom, by when, **and the lead time you're assuming**. Then work backwards to the date you must ask.

Requests with long lead times go in the plan as *actions in week one*, not as steps at the point of need. This is the same logic as `access-and-onboarding`, applied to work.

Dependencies you can't confirm are unknowns, and belong early.

### 4. Sequence against the calendar, not just the work

The organization's calendar constrains the plan more than most engineers expect:

- Release windows and freeze periods, including quarter-end and peak trading
- Change board meeting dates and their submission deadlines
- Holidays, and the availability of the specific people you need
- Any external deadline — regulatory, contractual — which is fixed while your scope is not

Work backwards from the release window. A change complete two days after the window is late by however long the next window is away, which in some organizations is a month.

### 5. Say what would change the plan

The section that distinguishes a plan from a wish. List the specific conditions that would trigger a re-plan, and roughly what each does:

> If the reconciliation job turns out to parse positionally, R2 becomes a coordinated change with the finance data team — add 2 weeks and a CAB submission.

Written in advance, this converts a nasty surprise into an anticipated branch. It also makes the eventual conversation vastly easier: you predicted it, and you already know the impact.

### 6. Plan three to five steps deep, no further

A twelve-step plan in an organization you've known for three weeks is fiction, because step two will change it. Plan the next few slices in detail and sketch the rest.

Say explicitly when you'll re-plan — after the first deploy, after the unknowns resolve, at the end of the first slice. A plan with a stated review point is honest; one without implies a confidence you don't have.

## Output template

Write to `.fde/05-delivery-plan.md`:

```markdown
# Delivery plan — <scope>

**Engagement:** <name>
**Author:** FDE
**Date:** <YYYY-MM-DD>
**Status:** draft
**Basis:** `04-feasibility.md`, `05b-estimate.md`
**Next re-plan:** <when, and what triggers it>

## Approach
<Two sentences on the sequencing logic and what it front-loads.>

## Sequence

| # | Slice | Delivers | Why here | Est. elapsed | Depends on |
|---|---|---|---|---|---|
| 0 | Trivial change through full pipeline | Proves the deploy path, measures real overheads | **Highest unknown** — never shipped here | 3–7 d | Deploy access |
| 1 | R1 — single currency end to end | Shippable, flagged off | Vertical slice; validates the approach | 4–8 d | — |
| 2 | R2 — contract change | Consumers on new version | Cross-team coordination has the longest lead time | 8–15 d | Team D confirmation |
| 3 | R3 — reporting | Full scope | Depends on data availability | 5–10 d | Data access (#7) |

## Actions needed in week 1
<Long-lead requests, regardless of when the work happens.>

| Action | Why | Lead time | Owner |
|---|---|---|---|
| Request reporting schema read | Blocks slice 3 | ~10 d | FDE |
| Contact Team D re contract | Blocks slice 2 | unknown — silent since 03-12 | FDE |
| Submit CAB for slice 0 | 10 working days' notice | 10 d | FDE + release manager |

## Calendar constraints
| Constraint | Effect |
|---|---|
| Release windows: Thursdays | Up to 7d wait per slice |
| Freeze: <dates> | Nothing ships; plan around it |
| CAB: fortnightly, Tue | Submissions 10 working days ahead |

## What would change this plan
| # | Condition | Effect |
|---|---|---|
| 1 | Recon job parses positionally | R2 becomes cross-team; +2 weeks, CAB |
| 2 | Reporting access refused | R3 not deliverable as specified; re-scope |
| 3 | Slice 0 reveals a longer deploy path | All estimates shift; re-plan immediately |

## Not planned yet
<What's deliberately left sketched, and when it'll be planned.>
```

## Common traps

**Sequencing by ease.** Defers the discovery that the plan was wrong to the point where it's expensive.

**Horizontal slices.** "All the database work" delivers nothing, proves nothing, and hides integration problems until the end.

**Not shipping something trivial first.** The deploy path is an unknown, and finding out in week six is self-inflicted.

**Dependencies without lead times.** A name is not a plan. Long-lead requests belong in week one.

**Ignoring the calendar.** Two days late for a window can mean a month late.

**No trigger conditions.** Then every surprise is a crisis rather than an anticipated branch.

**Planning twelve steps deep.** Step two will change it. Plan three to five and say when you'll re-plan.

**Silent re-planning.** If the plan changed, say so, early. See `escalation-and-renegotiation`.
