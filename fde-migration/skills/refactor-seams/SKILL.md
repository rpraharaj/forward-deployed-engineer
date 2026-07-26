---
name: refactor-seams
description: Change code that must change but is not safely changeable - find the seams that let you alter behavior without rewriting, using branch-by-abstraction, strangler fig, and adapter insertion, always leaving the system releasable at every step. Use when extracting from a monolith, when a component must be replaced incrementally, when a refactor is too large to do in one change, or when someone proposes a rewrite. Every step ships independently, because a long-lived refactor branch is how refactors die.
---

# Refactor seams

Changing the shape of something without stopping it.

## Why this exists

The default plan for code that has become hard to change is a rewrite on a branch. It is almost always the wrong plan, and it fails the same way every time: the branch diverges, the main line keeps moving, the merge becomes impossible, and the work is abandoned after months. Everyone involved knew this would happen and did it anyway, because the alternative looked slower.

The alternative genuinely is slower per step, and it finishes. Incremental restructuring behind a seam, with the system releasable at every point, converts an all-or-nothing bet into a series of small safe changes — any one of which can be the last one if priorities shift.

For an FDE this matters twice over. You may not be here long enough to finish a rewrite, and a half-finished rewrite is worse than either state. Every incremental step you ship is value that survives your departure.

## When this applies

- Extracting from a monolith
- Replacing a component incrementally
- A refactor too large for one change
- Someone proposes a rewrite
- Code must change but isn't safely changeable

## When it doesn't

- The change fits in one safe diff — that's `safe-change`
- The component is genuinely small and well covered
- Nothing is being restructured, only behavior added

## Prerequisites

- `.fde/06-blast-radius-*.md` — you need to know every caller
- **`characterization-tests` first.** Restructuring untested code is the single riskiest thing in this portfolio. The tests are what make the refactor verifiable as behavior-preserving.
- `.fde/adr/` — the target shape should be a recorded decision

## Procedure

### 1. Establish the seam

A seam is where you can change behavior without editing the thing you're changing. Find it before planning anything.

Candidates, in rough order of preference:

1. **An existing interface** with the callers already going through it — ideal, nothing to introduce
2. **A constructor or factory** where the implementation is chosen
3. **A configuration or flag** selecting between paths
4. **A module or package boundary** with a narrow public surface
5. **A network boundary** — the coarsest and often the most practical for extraction

Where no seam exists, **introducing one is your first change** — and it must be behavior-preserving, committed separately, and characterized before and after. That commit is the whole first step, and it should look boring in review.

### 2. Choose the pattern

| Pattern | Use when | How it ends |
|---|---|---|
| **Branch by abstraction** | Replacing an implementation in place | Old implementation deleted once nothing selects it |
| **Strangler fig** | Replacing a system or subsystem incrementally | Old system dark, then removed, once all routes are diverted |
| **Adapter insertion** | The new thing has a different shape from the old | Adapter removed once callers migrate, or kept deliberately |
| **Parallel run** | You must prove equivalence before switching | Old path removed once outputs match for a stated period |

**Parallel run deserves more use than it gets.** Running both implementations and comparing outputs on live traffic — new path's result discarded — is the strongest possible evidence of equivalence, and it costs a flag and some logging. For anything where being wrong is expensive, it is worth the effort.

### 3. Sequence so every step ships

The rule that makes this work: **at no point is the system unreleasable.**

A typical branch-by-abstraction sequence:

1. Introduce the abstraction over the existing implementation. No behavior change. **Ship.**
2. Migrate callers to the abstraction, in batches. No behavior change. **Ship** each batch.
3. Add the new implementation behind the same abstraction, not selected. **Ship.**
4. Select the new implementation for a subset — a flag, a tenant, a percentage. **Ship.**
5. Widen the selection, monitoring. **Ship** each widening.
6. Remove the old implementation and the abstraction if it's no longer earning its place. **Ship.**

Every step is independently reviewable and independently revertible. Steps 1 and 2 are pure refactors a reviewer can verify by reading; step 4 is where behavior risk begins, and by then everything else is already proven.

### 4. Keep the steps genuinely separate

The most common way this degrades is bundling a refactor step with a behavior change because it's "obviously fine." It defeats the entire point — a reviewer can no longer verify the refactor by reading, and a bisect can no longer isolate a regression.

Same discipline as `safe-change` step 5, applied over a longer arc and with more temptation to break it.

### 5. Delete the old path

The step people skip, leaving both implementations forever. Two code paths, two test paths, permanent confusion about which is real, and a flag nobody dares remove.

Name the condition for deletion up front — "old path removed once the new one has served 100% of traffic for 30 days with no incidents" — and record who owns it. Then actually do it. Every incomplete refactor left behind makes the next one harder and makes the codebase harder to reason about for everyone after you.

### 6. Know when to stop

Not every refactor should finish. If priorities change and the work is paused, the system must be in a coherent state — that's what shipping every step buys you.

Where you stop mid-way, **write down where you stopped, why, and what completing it would take**. That goes in `handover-pack` under unfinished business. A paused refactor that nobody documented becomes an archaeological puzzle for whoever finds it.

## Output

ADR for the target shape, plus a tracking note in `.fde/06b-change-log.md`:

```markdown
## Refactor — extract pricing from the order monolith

**Pattern:** branch by abstraction → strangler
**ADR:** 0011 · **Seam:** `PricingCalculator` interface (introduced in PR #402)
**Characterization:** 34 tests pinning current behavior, PR #401

| Step | State | PR | Behavior change | Shipped |
|---|---|---|---|---|
| 1 Introduce interface over existing impl | done | #402 | none | 03-04 |
| 2 Migrate 14 callers | done | #405–408 | none | 03-08 |
| 3 New impl behind interface, unselected | done | #412 | none | 03-11 |
| 4 Flag on for internal tenants | done | #415 | **yes** | 03-14 |
| 5 Widen to 100% | in progress | — | yes | — |
| 6 Delete old impl + flag | **not started** | — | none | owner: <name>, after 30d clean |

**Parallel run:** both implementations ran on live traffic 03-11 → 03-14, outputs compared.
2 divergences found, both legacy rounding — see ADR-0011 §rejected.

**If paused here:** system is coherent; flag at 100% with the old implementation dormant.
Completing means step 6 only.
```

## Common traps

**Rewriting on a branch.** Diverges, becomes unmergeable, gets abandoned. Everyone knows this and does it anyway.

**Refactoring without characterization tests.** No way to know you preserved behavior. Riskiest thing in the portfolio.

**Bundling a refactor step with a behavior change.** Defeats the point — the reviewer can no longer verify by reading.

**A step that leaves the system unreleasable.** Then you have a branch again, just spelled differently.

**Never deleting the old path.** Two implementations forever, and a flag nobody dares touch.

**No stated deletion condition or owner.** Guarantees the above.

**Not using parallel run when the stakes justify it.** Strongest equivalence evidence available, and it costs a flag.

**Stopping without documenting where.** An archaeological puzzle for whoever finds it.
