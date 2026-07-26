---
name: nfr-validation
description: Actually measure the non-functional requirements rather than asserting them - performance under realistic load, behavior at failure boundaries, and whether the audit logging exists and contains what it should - reporting measured numbers with the conditions they were measured under. Use before release when NFRs have been declared, when someone claims performance is fine without a number, when a target needs proving for a change board, or when you need to know how the system behaves when a dependency fails. An NFR verified by assertion is not verified.
---

# NFR validation

Measuring what was promised.

## Why this exists

`nfr-baseline` writes down the targets. This skill finds out whether they hold.

The gap between the two is where a specific and common failure lives: everyone agrees performance matters, a target gets written, nobody measures it, and at go/no-go someone says "performance should be fine" — which is a feeling, not evidence, and it is accepted because the alternative is delaying the release to find out.

An FDE is well placed to break that pattern, precisely because you have no stake in the previous assumption. "We haven't measured it" is easier to say when you weren't the one who didn't measure it.

The other half of this skill is failure behavior. Systems are almost never tested for how they behave when a dependency is down, and that is exactly the condition under which they'll be judged.

## When this applies

- Before release, against declared NFRs
- Someone claims performance is fine without a number
- A change board needs evidence, not assurance
- You need to know what happens when a dependency fails
- A change alters data volume, query shape, or call patterns

## When it doesn't

- No NFRs declared — run `nfr-baseline` first, or you're measuring against nothing
- Genuinely trivial internal tooling
- Diagnosing a live performance problem — that's `incident-triage`

## Prerequisites

- `.fde/03b-nfrs.md` — **required.** The targets and the baseline.
- `.fde/07-verification.md` — this appends to it
- Access to a realistic environment, or an honest statement that you don't have one

## Procedure

### 1. Measure the same way the baseline was measured

If the baseline came from an APM p95 over thirty days, a local benchmark is not comparable and the comparison will mislead. Match the method, the percentile, and the conditions — or state plainly that you didn't and that the numbers aren't directly comparable.

Record with every measurement: **what, where, under what load, over what period, at which revision.** A number without its conditions is not evidence; it's a number.

### 2. Load, if performance is in scope

Realistic load matters more than peak load. Take the shape from the baseline — request mix, payload sizes, data volume, concurrency — because a benchmark of one endpoint at full throttle tells you very little about a system whose real traffic is mixed.

Where you have no load environment — normal in enterprise, and the usual case — do not fabricate a pass. Options, in preference order:

1. Measure in staging and state the scale difference explicitly
2. Measure the specific operation in isolation and reason about it, tagged `[inferred]`
3. Ship behind a flag with a staged rollout and measure in production — often the only honest path
4. Record it as an unmeasurable gap and let `release-readiness` weigh it

Option 3 is legitimate and under-used. A 5% rollout with a p95 dashboard is a real measurement under real conditions, and frequently better than any staging approximation.

### 3. Test the failure boundaries

The part that gets skipped. For each dependency, find out what actually happens when it's unavailable, slow, or returning errors — not what the code appears to do.

- Dependency down: does the system degrade as `nfr-baseline` said it should, or fail entirely?
- Dependency **slow**: this is worse than down, and tests differently. Timeouts, connection pool exhaustion, thread starvation, cascading backpressure.
- Partial failure: some requests fail, some succeed
- Recovery: does it come back on its own when the dependency returns, or does it need a restart?

That last one matters disproportionately. A system that stays broken after its dependency recovers turns a five-minute upstream blip into an hour-long outage, and nobody discovers this until it happens.

Slow is the most valuable case to test, and the least tested. Everything handles a fast failure; a dependency at ten seconds is what exhausts the pool.

### 4. Verify the audit and logging obligations

Where `nfr-baseline` recorded an audit requirement, check it produces what was promised — not that logging exists, but that the specific fields are present, at the right level, retained appropriately.

Also check the inverse, which is the failure that ends careers: **is anything in the logs that shouldn't be?** Personal data, card numbers, tokens, full request payloads. Scan against the field list from the data classification.

```bash
# Adapt the field names to the classification in 03b-nfrs.md
grep -riE "(email|card|ssn|passport|token|password)[\"']?\s*[:=]" <log sample> | head
```

### 5. Report numbers with conditions, and be plain about gaps

Every result is a measurement plus its conditions plus a verdict against the target. Where you could not measure something, that is a **gap**, not a pass — and it flows to `release-readiness` as residual risk, which is exactly where it belongs.

Resist rounding a marginal result into a pass. A p95 of 0.98s against a 1.0s target in staging, at a tenth of production volume, is not a pass — it's a number that needs stating with its conditions so someone can make a judgment.

## Output

Append to `.fde/07-verification.md`:

```markdown
## NFR validation

**Date:** <YYYY-MM-DD> · **Revision:** `<SHA>` · **Environment:** staging

| NFR | Target | Measured | Conditions | Verdict |
|---|---|---|---|---|
| N1 Refund p95 | < 1.0s | 0.91s | staging, 50 req/s, 30 min, 12k orders | ✅ but see note |
| N1 at prod volume | < 1.0s | **not measured** | no prod-scale environment | ❌ gap |
| N4 Failure detected < 5 min | — | 90s | killed FX service, alert fired | ✅ |
| N5 Degrade: FX down | original-currency refunds succeed | **fails** — 500s | FX client has no timeout `[confirmed: FxClient:31]` | ❌ |

### Failure-boundary results
| Dependency | Down | Slow (10s) | Recovers unaided |
|---|---|---|---|
| FX service | 500s to caller — no fallback | **Pool exhausted in ~40s**, whole service degrades | No — needs restart |

### Log scan
- No PII found in application logs over a 7-day sample `[confirmed]`
- Audit fields present: actor, timestamp, before/after ✅

### Gaps
| # | Unmeasured | Why | Detectable in prod? |
|---|---|---|---|
| 1 | Prod-volume latency | No load environment | Yes — p95 dashboard, minutes |
```

## Common traps

**Measuring differently from the baseline.** The comparison misleads, and someone will act on it.

**A number without conditions.** Not evidence.

**Fabricating a pass when you couldn't measure.** The precise failure this skill exists to prevent.

**Only testing "dependency down".** Slow is worse, more common, and tests completely differently.

**Not testing recovery.** A system that stays broken after its dependency returns converts a blip into an outage.

**Checking that logging exists rather than what it contains.** The obligation is about content.

**Not scanning for data that shouldn't be logged.** The inverse check, and the one with the worst consequences.

**Rounding a marginal result up.** State it with conditions and let someone judge.
