---
name: nfr-baseline
description: Make non-functional requirements explicit and measurable before build starts - latency and throughput targets, data sensitivity classification, audit and retention obligations, observability needs, and failure and degradation behavior - each written as something you can actually test. Use before building anything user-facing or load-bearing, when a spec covers behavior but not performance or security, before a design decision that depends on scale, or when you suspect an NFR will surface as a launch blocker. Measure the current baseline first, because a target without a baseline is guesswork.
---

# NFR baseline

Making the unwritten requirements testable, before they become launch blockers.

## Why this exists

Non-functional requirements have a characteristic failure pattern: nobody states them, everybody assumes them, and they surface two days before go-live as a blocker. The security review that needs three weeks' notice. The performance target nobody measured. The audit trail a regulator requires and the schema can't produce.

They're skipped because they feel like process, and because the people who hold them — security, compliance, DBAs, SRE — aren't in the room when the requirement is written.

The specific mistake is stating them unmeasurably. "The system should be fast" cannot be tested, so it will not be tested, so it will be argued about at the worst possible moment. "Refund p95 under 1.0s at 50 requests/second" can be tested, and either passes or doesn't.

**Measure the current baseline first.** A target set without knowing today's number is invented, and it's usually either trivially met or impossible.

## When this applies

- Before building anything user-facing or load-bearing
- The spec covers behavior but not performance, security, or operability
- A design decision depends on scale or data sensitivity
- Anything touching personal data, money, or an audit trail

## When it doesn't

- Internal tooling with no meaningful load, data sensitivity, or availability need
- A change to something whose NFRs are already documented and unchanged
- Spikes

## Prerequisites

- `.fde/03-requirements.md` — functional scope
- `.fde/02-system-map.md` — where things live and what's exposed
- Access to monitoring, if it exists, for the baseline measurement

## Procedure

### 1. Measure the current baseline

Before setting any target, establish today's number. Sources, cheapest first: existing APM or monitoring dashboards, log-derived timings, database query statistics, or a crude measurement you take yourself.

Where nothing is measurable, that is itself a finding — an unobservable system cannot have a testable performance target, and `observability-gap` becomes a prerequisite rather than a nice-to-have.

Record baselines with the same discipline as everything else: the number, where it came from, and over what period.

### 2. Work through the categories

Most of these will not apply. Go through all of them anyway — the value is in the five minutes spent confirming that one doesn't, because that's how you find the one that does.

**Performance**
- Latency target, as a percentile, at a stated load. Averages hide everything that matters.
- Throughput — requests, messages, or records per unit time, at peak not average
- Batch completion windows: "must finish before 07:00" is a real and testable requirement

**Scale and growth**
- Current volume, and expected growth over a stated horizon
- Where the design breaks — the volume at which the approach stops working. Worth knowing even when it's far away.

**Availability**
- Uptime expectation, and whether one actually exists in writing
- Acceptable degradation: what should still work when a dependency is down
- Recovery time and recovery point objectives, if anything is stateful

**Data sensitivity** — the category that most often carries a long lead time
- Classification of every field involved: personal, financial, health, or none
- Encryption in transit and at rest, and whether that's already handled by the platform
- Retention and deletion obligations, including the right to erasure
- Cross-border transfer restrictions, which quietly constrain where things can be hosted

**Audit and compliance**
- What must be logged, in what detail, retained for how long
- Who must be able to prove what, to whom
- Whether the change touches anything in an existing regulatory scope. A system already in SOX or PCI scope brings its controls with it.

**Observability**
- What metric moves when this breaks
- What alert fires, and to whom
- Whether a failure would be **silent** — the single most important question here

**Operability**
- Who runs this, and can they
- What manual intervention is possible when it goes wrong
- Configuration and feature-flag control at runtime

### 3. Write each as a testable statement

The whole point. Every NFR needs a metric, a target, and a condition.

| Unusable | Testable |
|---|---|
| "Should be fast" | "Refund p95 < 1.0s at 50 req/s sustained" |
| "Must be secure" | "No PII in application logs; verified by log scan against the field list" |
| "Should handle growth" | "Correct behavior at 10× current volume (400k orders/day)" |
| "Needs an audit trail" | "Every refund records actor, timestamp, before/after amount; retained 7 years" |
| "Should degrade gracefully" | "With the FX service down, refunds in the original currency still succeed" |

Apply the same test as acceptance criteria: **could someone else check this and get the same answer?**

### 4. Find who holds each requirement

Many NFRs aren't the sponsor's to set. Security classifications come from security, retention from compliance or legal, availability from whoever owns the SLA.

Identify the holder for each — `ownership-map` helps — and **find out the lead time for their involvement now**. A security review needing three weeks' notice is a scheduling fact that must enter the delivery plan immediately, not a discovery to be made at go-live.

### 5. Separate the real from the aspirational

Some stated NFRs are genuine constraints; others are preferences that will not actually block a release. Confusing them wastes effort in both directions.

Ask, for each: **what happens if we miss this?** A regulatory retention requirement and an aspirational latency target both look like requirements on paper and behave completely differently in a go/no-go conversation.

Mark each **must** or **should**, and record who decides.

### 6. Hand them to verification

Each NFR becomes a row in `07-verification.md` needing a measurement, and `release-readiness` rates the category. An NFR that never reaches the verification plan will not be checked — which is exactly how they become launch blockers.

## Output template

Write to `.fde/03b-nfrs.md`:

```markdown
# Non-functional requirements — <scope>

**Engagement:** <name>
**Author:** FDE
**Date:** <YYYY-MM-DD>
**Status:** draft | confirmed by <name>
**Confidence:** <which are confirmed with the holder vs. assumed>

## Baseline
| Aspect | Current | Source | Period |
|---|---|---|---|
| Refund p95 | 0.7s | APM dashboard | 30 days |
| Refund volume | 40k/day, peak 3k/h | warehouse query | 90 days |
| PII in logs | none observed | log scan, 7 days | — |

## Requirements

| # | Category | Requirement (testable) | Must/Should | Holder | Confirmed |
|---|---|---|---|---|---|
| N1 | Performance | Refund p95 < 1.0s at 50 req/s | must | Platform SRE | ✅ 03-14 |
| N2 | Data | `currency` is not PII; no classification change | must | Security | ⏳ requested 03-12 |
| N3 | Audit | Refund records actor + before/after; retained 7y | must | Compliance | ✅ existing control |
| N4 | Observability | Failure detected within 5 min via `refund_errors` | should | FDE | — |
| N5 | Degradation | FX service down → original-currency refunds still succeed | should | Product | ⏳ |

## Long-lead involvement
| Who | What | Lead time | Requested |
|---|---|---|---|
| Security | Classification review | 3 weeks | 03-12 |
| DBA | Schema review | 2–11 d | not yet |

## Silent-failure analysis
<Which failures would NOT be noticed, and what it would take to notice them. Usually the most valuable section.>

- A refund stored with the wrong currency would be **silent** — no validation, no alert. Detected at month-end reconciliation, up to 30 days later.

## Not applicable
<Categories considered and excluded, with a one-line reason. Prevents re-litigating.>
```

## Common traps

**Setting a target without a baseline.** Invented numbers are either trivially met or impossible, and both waste effort.

**Unmeasurable statements.** "Should be fast" will not be tested and will be argued about at go-live.

**Averages instead of percentiles.** The mean hides exactly the behavior users notice.

**Skipping the categories that seem irrelevant.** The five minutes confirming one doesn't apply is how you find the one that does.

**Missing the lead times.** A three-week security review discovered at go-live is a three-week slip.

**Not asking who holds the requirement.** You cannot set a data classification, and guessing at one is worse than asking.

**Confusing must with should.** They behave completely differently in a go/no-go, and conflating them wastes effort in both directions.

**Skipping the silent-failure question.** A failure nobody detects is far more dangerous than one that pages someone at 3am.

**NFRs that never reach the verification plan.** Then they aren't checked, and they resurface as blockers.
