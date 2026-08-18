---
name: estimation
description: Size work under genuine uncertainty, grounded in feasibility findings rather than optimism - ranges rather than points, explicit assumptions, the organizational overheads engineers routinely forget, and a clear statement of what would move the number. Use when asked how long something will take, when a date is being committed to, when a plan needs sizing, or when someone wants a single number and you need to communicate uncertainty honestly. Requires feasibility-probe first - an estimate produced before anyone looked at the code is a guess wearing a number.
---

# Estimation

Putting a number on it without lying.

## Why this exists

Estimates fail for two reasons, and only one of them is about estimating.

The first is **ungrounded sizing** — a number produced before anyone looked at the code. `feasibility-probe` exists to fix that, and this skill depends on it absolutely. Estimating without it is guessing with extra confidence.

The second is that engineers estimate **the coding** and are then held to **the delivery**. The code takes four days; the change lands three weeks later, after review latency, a schema approval, a security scan, a release window, and two rounds of UAT feedback. Nobody was wrong about the coding.

An FDE is exposed on both counts, plus a third: you don't know this organization's overhead yet, and it varies enormously. In some places a PR merges in an hour; in others it takes nine days and two sign-offs.

## When this applies

- "How long will this take?"
- A date is being committed to
- Sizing a delivery plan
- Someone wants a single number

## When it doesn't

- Feasibility hasn't been done — do that first, and say why
- The work is genuinely exploratory. A spike gets a **timebox**, not an estimate.
- Deciding *whether* to do something. That's `solution-design`, where relative cost is enough.

## Prerequisites

- `.fde/04-feasibility.md` — **required.** The change shapes, sites, and deceptive costs are the input.
- `.fde/06-blast-radius-*.md` — coordination cost lives here
- `.fde/00b-access.md` — blocked access is calendar time
- `.fde/02b-ownership.md` — review and approval paths

## Procedure

### 1. Estimate from the feasibility shapes

`feasibility-probe` classified each requirement by shape. The shape predicts cost far better than intuition about difficulty:

| Shape | Sizing note |
|---|---|
| Configuration | Small — unless the config lives in an environment you can't reach, which makes it a queue-wait |
| Extend existing | Small to medium, and predictable |
| New component | Medium, usually the best-estimated shape |
| Modify shared | **Cost is in the callers, not the change.** Count them. |
| Cross-cutting | Largest and most underestimated. Looks small at every individual site. |

Every deceptive cost in the feasibility artifact is a line item. If it wasn't worth listing there, it isn't worth ignoring here.

### 2. Add the overheads engineers forget

Routinely a third to a half of elapsed time, and invisible in a coding estimate:

- **Review latency** — not review effort. How long does a PR actually sit? Measurable: `git log` the merge timestamps against PR creation.
- **Test writing**, including characterization tests if coverage is thin
- **Test data** — in a regulated organization this can dominate. See `test-data-strategy`.
- **CI time**, and the flake rate. A suite that fails spuriously one run in four costs real days.
- **Approvals** — schema, security, architecture, change board. Lead times, not effort.
- **Environment waits** — deploy slots, shared staging contention
- **Rework from feedback** — assume at least one round
- **Coordination** with every team `blast-radius` identified

Measure rather than guess where you can:

```bash
# PR created → merged, if the host CLI exists. Merge-commit dates alone are not review latency.
gh pr list --state merged --limit 20 --json createdAt,mergedAt,title 2>/dev/null
```

If that is empty (squash history, no `gh`, Azure DevOps), ask someone who merges here, or tag review latency `[unverified]`. Do not invent a number from `git log --merges`.

### 3. Give a range, and say what drives it

Single-point estimates are read as commitments regardless of how they're framed. Give three numbers:

- **Optimistic** — everything known is true and nothing waits
- **Likely** — one thing goes wrong, normal review and approval latency
- **Pessimistic** — an unknown resolves badly

The spread is information. A 3–15 day range says something a "7 days" doesn't: that the uncertainty is the story, and reducing it may be more valuable than starting.

**Narrow the range by resolving unknowns, not by choosing a number.** If the spread is uncomfortable, the answer is a spike or an access request, not optimism.

### 4. Separate effort from elapsed time

The distinction that causes the most damage when lost.

- **Effort** — person-days of actual work
- **Elapsed** — calendar time from start to done

Three days of effort can be three weeks elapsed: two days blocked on a DBA ticket, four on review, and a release window on Thursdays. Give both, and be explicit that a stakeholder asking "how long" almost always means elapsed while an engineer answering almost always means effort.

### 5. State the assumptions as conditions

Every estimate rests on assumptions. Make them explicit and falsifiable, because an assumption that fails silently is what turns a slip into a surprise:

> Assumes the DBA schema approval takes under 5 working days *(observed range: 2–11 on recent tickets)*. If it exceeds that, add the excess directly to elapsed time.

That phrasing does real work. It tells the reader which number moves, by how much, and when they'll know — converting a broken assumption from a surprise into a tracked condition.

### 6. Say what you'd need to be more confident

Close with it. Usually one to three items: an access grant, a two-hour spike, an answer from another team.

This is often the most actionable thing in the document. "I can give you ±2 days instead of ±8 if I can get read access to the reporting schema" is a trade a delivery lead will take immediately.

### 7. Re-estimate when facts change, and say so

An estimate is a statement about what was known on a date. When an unknown resolves badly, re-estimate and communicate it **immediately** — see `escalation-and-renegotiation`.

A delivery lead who learns about a two-week slip four weeks late has lost the options they had at week one. That, not the slip, is what damages trust.

## Output template

Write to `.fde/05b-estimate.md`, or a section of the delivery plan:

```markdown
# Estimate — <scope>

**Engagement:** <name>
**Author:** FDE
**Date:** <YYYY-MM-DD>
**Basis:** `04-feasibility.md` @ `<SHA>`
**Confidence:** <and where the uncertainty concentrates>

## Headline
**Effort: <n>–<n> person-days · Elapsed: <n>–<n> working days**

<Two sentences. What drives the spread, and what would narrow it.>

## By requirement

| Req | Shape | Effort (O/L/P) | Notes |
|---|---|---|---|
| R1 | extend existing | 1 / 2 / 3 | Well understood |
| R2 | cross-cutting, 11 sites | 3 / 5 / 10 | Contract change → consumer coordination |
| R3 | new component | 2 / 3 / 5 | Blocked on data availability — see assumptions |

**Coding subtotal:** 6 / 10 / 18 person-days

## Overheads

| Item | Elapsed | Basis |
|---|---|---|
| Review latency | 2–5 d | Observed median 3d on this repo |
| Schema approval | 2–11 d | Recent DBA tickets |
| Test data | 1–3 d | No masking pipeline — see `03c-test-data.md` |
| Release window | 0–7 d | Thursdays only |
| One rework round | 1–3 d | Assumed |

## Effort vs elapsed
- **Effort:** 6–18 person-days
- **Elapsed:** 12–40 working days
- **Why they differ:** approval and review latency dominate; most of the calendar is waiting.

## Assumptions
| # | Assumption | If false | Impact |
|---|---|---|---|
| 1 | Schema approval < 5d | Observed up to 11d | +6d elapsed |
| 2 | Team D confirms contract compatibility | Silent since 03-12 | +5d or a redesign |

## Not included
<Explicitly out: production support, documentation beyond the workspace, training, post-release monitoring beyond the watch window.>

## To increase confidence
| # | What | Would narrow | Cost |
|---|---|---|---|
| 1 | Read access to reporting schema | R3 from ±3d to ±1d | 1 access request |
| 2 | 2h spike on the recon job | R2 from ±5d to ±2d | 2 hours |
```

## Common traps

**Estimating without feasibility.** A guess wearing a number, and it will be quoted back to you.

**Estimating coding, being held to delivery.** The overheads are a third to a half of elapsed time.

**A single number.** Read as a commitment however you frame it.

**Conflating effort and elapsed.** The stakeholder means elapsed; you mean effort. Say both.

**Narrowing the range by optimism.** Resolve an unknown or keep the range.

**Assumptions that fail silently.** Write them as falsifiable conditions with a stated impact.

**No re-estimate when facts change.** The late slip damages trust far more than the slip.

**Padding instead of stating uncertainty.** A padded point estimate loses the information a range carries, and someone will eventually notice the padding.

**Estimating in the room.** Say what you know — the shape — and come back with a number. A figure produced under social pressure becomes the commitment.
