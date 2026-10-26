---
name: cutover-plan
description: Plan the moment two systems swap - data migration and backfill, dual-run and reconciliation, the consistency window, traffic shifting, the point of no return, and what abort means at each stage. Use for any migration or replatform where data moves and both systems briefly coexist, when a legacy system is being replaced, or when a go-live has a defined switchover moment. The hardest artifact in the portfolio, because unlike a deploy the thing being changed is state, and state does not roll back cleanly.
---

# Cutover plan

The moment the old thing stops and the new thing starts.

## Why this exists

A deploy changes code. A cutover changes **state**, and state does not roll back cleanly. Once the new system has accepted a transaction the old one never saw, "just switch back" stops being a plan and becomes a data reconciliation project.

That asymmetry is why cutovers deserve a bigger artifact than deploys. The questions that decide whether one succeeds are almost entirely about the seam: what happens to records written during the switch, how you know the two systems agree, and precisely when you lose the ability to go back.

Most failed cutovers were not failures of the new system. They were failures to plan the twenty minutes in the middle.

## When this applies

- Migration or replatform where data moves
- A legacy system being replaced
- Any go-live with a defined switchover moment
- Two systems that will briefly coexist

## When it doesn't

- Ordinary deploys, even risky ones — that's `deploy-runbook`
- Code-only changes with no data movement
- Decommissioning something with no replacement — that's `decommission-plan`

## Prerequisites

Resolve `<workspace>` before reading or writing artifacts: use `FDE_WORKSPACE` if set (report an unavailable explicit path rather than falling back), otherwise the charter's recorded Location (look in `.fde/` and `../*-fde/`), then an existing `.fde/` or `../<repo>-fde/`. If none exists, run core `fde-orient`; do not create a second workspace. All artifact paths below use that location. Follow core workspace conventions for headers; preserve existing sections when appending.

- `<workspace>/traces/data-model.md` — you must know the eras and shapes before moving data
- `<workspace>/06-blast-radius-*.md` — every consumer of both systems
- `<workspace>/07-verification.md` — the new system proven on its own before you plan the swap
- `db-change-management` where schema changes are involved

## Procedure

### 1. Choose the cutover shape

The single most consequential decision, and it should be explicit rather than defaulted into:

| Shape | How it works | Use when |
|---|---|---|
| **Big bang** | Stop old, migrate, start new | Small data, a real outage window is available, rollback is genuinely feasible |
| **Parallel run** | Both process everything; old is authoritative until proven | Correctness matters more than speed; you can afford double-writing |
| **Phased by segment** | Migrate tenants, regions, or product lines in tranches | Data partitions cleanly; blast radius must stay small |
| **Strangler** | Route by route, over months | Long-lived, low-risk, no single moment |

**Parallel run requires isolated effects.** Keep the old system authoritative; route shadow writes to separate storage and suppress or sandbox notifications, payments, events, and external mutations. Define which system alone may perform each real-world action, how retries are deduplicated, and how extra load is bounded. Only compare live traffic after verifying those controls; otherwise rehearse with policy-approved inputs in a lower environment. Switch only after reconciliation succeeds for a stated period.

Where data partitions cleanly, phased is the safest real option: the first tranche is a genuine rehearsal with real data and bounded consequences.

### 2. Plan the data migration as its own operation

Rarely a single copy.

- **Bulk load** — the historical data, moved ahead of time, days or weeks before cutover
- **Delta sync** — the changes since the bulk load, repeated and shrinking
- **Final delta** — the last, smallest sync during the window itself

The rehearsal question that determines everything: **how long does the final delta take?** That duration *is* your cutover window, and it's knowable in advance by rehearsing.

Also decide: what happens to data that fails to migrate? A record that won't transform — because it's from an era nobody remembers — must have a defined destination. Silently dropped is the default and the worst answer.

### 3. Define the consistency window

The seam. Between the final delta and the new system going live, writes are happening somewhere.

Options: freeze writes entirely (simplest, needs a real outage window), queue writes and replay them after (complex, but no downtime), or dual-write during the window (complex, risks divergence).

Whichever you pick, answer explicitly: **what happens to a transaction submitted during the window?** If you can't answer it, you don't have a cutover plan yet.

### 4. Build reconciliation before you need it

You must be able to demonstrate the two systems agree — before cutting over, and after.

Counts by entity and by day, sums of the key measures, spot-checks on the awkward records, and specifically the eras `data-archaeology` identified. Legacy-shaped records are where migration transforms fail, and they're a small enough population to check individually.

Reconciliation is also what tells you the cutover *worked*. "The migration completed" is not evidence; matching totals are.

### 5. Name the point of no return

The most important line in the document.

Somewhere the old system stops being authoritative, or gets written to in a way that can't be undone, or a consumer is repointed irreversibly. **Mark it explicitly.** Everything before it must be verified before you cross.

Then be honest about what's after it. If rollback after that point means "restore from backup and lose the transactions since," say that in those words. A plan claiming reversibility it doesn't have is worse than one honestly admitting a one-way door, because people make different decisions when they know.

### 6. Define abort criteria per stage

Not one abort decision — one per stage, each with a threshold and a named decider. Judgment degrades badly at 3am under pressure, so agree these calmly in advance.

For each stage: what would make us stop, what do we do if we stop, and how long does that take?

Abort before the point of no return should be genuinely cheap. Abort after it is a recovery operation and should be described as one, with its own steps.

### 7. Rehearse the whole thing

Non-negotiable for anything significant. A full dress rehearsal against production-shaped data, timed.

Rehearsal reliably surfaces: the final delta taking four times longer than estimated, a transform failing on legacy records, a consumer nobody knew about, a permission the operator doesn't have, and a step whose written instructions don't work.

Every one of those is cheap to find in a rehearsal and expensive at 2am. **Record the timings** — they become the plan's estimates, and they're the only trustworthy ones.

### 8. Plan the aftermath

A cutover isn't done when traffic moves.

- **Hypercare** — heightened monitoring, who's watching, for how long
- **The old system** — kept running but idle, for how long, and who decides to turn it off. That's `decommission-plan`, and it should be scheduled, not left.
- **Reconciliation after** — ongoing, until confidence is established
- **Rollback availability** — how long can you still go back, and when does that expire

Leaving the old system running indefinitely because nobody decided is the standard outcome, and it costs money and confusion for years.

## Output

Write to `<workspace>/runbooks/cutover-<name>.md`:

```markdown
# Cutover — <old> → <new>

**Engagement:** <name> · **Date planned:** <date> · **Window:** <start>–<end>
**Shape:** phased by region · **Rehearsed:** <date>, <duration>
**Decision owner:** <name> · **Operators:** <names>
**Author:** FDE
**Date:** <YYYY-MM-DD>
**Status:** draft
**Source revision:** <repo>@<short SHA>, or "no repository yet"
**Confidence:** <what is confirmed, inferred, or unverified>

## Summary
<One sentence a release manager understands.>

## Data migration
| Stage | What | When | Duration (rehearsed) | Verified by |
|---|---|---|---|---|
| Bulk load | All history to 03-01 | 03-05 | 6h 20m | count + sum reconciliation |
| Delta 1 | 03-01 → 03-14 | 03-15 | 40m | reconciliation |
| **Final delta** | since delta 1 | **in window** | **12m** | reconciliation, must pass |

**Failed records:** routed to `migration_rejects` with a reason. Rehearsal produced 41,
all pre-2019 era `[confirmed]`. Each reviewed; 38 obsolete, 3 hand-corrected.

## Consistency window
**Approach:** writes frozen at the API layer for the window
**Duration:** ~25 min · **Submitted during window:** rejected with a retryable error `[confirmed]`

## Steps
| # | Stage | Action | Expect | Abort → |
|---|---|---|---|---|
| 1 | pre | Verify delta 1 reconciliation | counts match exactly | A1 (no-op) |
| 2 | freeze | Enable write freeze | writes rejected, reads OK | A1 |
| 3 | sync | Final delta | completes < 20m | A2 |
| 4 | verify | Full reconciliation | counts + sums match | A2 |
| 5 | **POINT OF NO RETURN** | Repoint consumers to new | — | A3 (recovery) |
| 6 | unfreeze | Lift write freeze | writes land in new | A3 |
| 7 | watch | 2h hypercare | error rate at baseline | A3 |

## Point of no return
**Step 5.** After this, the new system accepts writes the old one never sees.
Rollback becomes: restore old from backup, replay from `migration_rejects` and the
new system's write log, **and accept a reconciliation exercise of several hours.**
This is not a clean rollback and should not be described as one.

## Abort criteria
| # | Stage | Condition | Decider | Action |
|---|---|---|---|---|
| A1 | 1–2 | Any reconciliation mismatch | FDE | Lift freeze, reschedule. Cheap. |
| A2 | 3–4 | Final delta > 20m, or mismatch | <name> | Lift freeze, old system authoritative. Cheap. |
| A3 | 5+ | Error rate > baseline ×3 sustained 10m | <name> + <sponsor> | **Recovery operation — see below** |

## Recovery after the point of no return
<Explicit steps. Duration. Who. What data is at risk.>

## Aftermath
**Hypercare:** 48h, <name> · **Old system:** running idle 30 days, decommission ticket <ref>
**Rollback expires:** <date> · **Ongoing reconciliation:** daily for 2 weeks
```

## Common traps

**Treating it like a deploy.** State doesn't roll back cleanly.

**Not rehearsing.** The final delta duration *is* the window, and it's only knowable by measuring.

**No defined consistency window.** If you can't say what happens to a transaction submitted mid-cutover, you don't have a plan.

**No named point of no return.** Then nobody knows when the decision became irreversible.

**Claiming rollback you don't have.** People make different decisions when they know the truth.

**No destination for failed records.** Silently dropped is the default and the worst answer.

**One abort decision for the whole cutover.** Each stage has different costs and needs its own threshold.

**Abort criteria decided in the moment.** Judgment at 3am is not what you want deciding this.

**No plan for the old system.** It runs idle for years because nobody scheduled the decision.
