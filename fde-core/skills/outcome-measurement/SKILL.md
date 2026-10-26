---
name: outcome-measurement
description: "Define and baseline the business benefit of an engagement, then compare observed results with the original claim, costs, and measurement limits. Use when success has no agreed business measure, a sponsor asks whether delivery created value, or projected savings need checking. Technical latency/load targets belong to nfr-baseline and nfr-validation; immediate release monitoring is post-deploy-watch."
---

# Outcome measurement

Make the value claim testable and keep it separate from delivery status.

**Maturity:** experimental — an initial synthetic procedure trial is recorded; live engagement validation is still needed.

## When this applies / when it doesn't

Use before building when the business result is undefined, and after rollout when a benefit claim needs evidence. Begin a baseline even if post-release results will not be available during the engagement.

Use `verification-plan` for acceptance criteria, `nfr-validation` for technical targets, and `stakeholder-brief` to communicate the result. A technically successful release can have an outcome that remains unmeasured.

## Prerequisites

Resolve `<workspace>` using `../_shared/workspace-conventions.md`; preserve earlier baselines and readouts rather than replacing them.

- Chosen problem and accountable business owner, from the charter or `discovery/opportunities.md` if available
- Approved aggregate data, workflow observations, and the assumptions behind any benefit claim
- Definitions of the affected population, delivery scope, and observation window

If historical data is unavailable, record a prospective baseline plan and the consequence for later comparisons. Do not reconstruct an unobserved baseline from memory and call it measured.

## Procedure

### 1. Define a small set of outcomes

Choose measures the owner can act on: active handling time, completed cases, error/rework rate, risk exposure, or service reach. For each specify numerator, denominator, unit, population, source, period, desired direction, and target owner.

Include a quality or harm guardrail so a faster process cannot pass by dropping hard cases. State who agrees the target and what decision the measurement will inform.

### 2. Capture the baseline and measurement plan

Record the actual baseline, source version, sample/window, exclusions, and confidence. Keep active work separate from waiting time. Plan the post-change window, comparison population, owner, and review date before rollout where possible.

Use approved aggregate evidence and existing measurement tools. Avoid collecting employee/customer identifiers unless policy and the task require them. Record missing access and data limitations explicitly.

### 3. Separate projected benefit from observed benefit

Write assumptions next to the calculation, including expected usage and case volume. Time released is not automatically cash saved; establish whether it reduces paid cost, increases capacity, or improves service.

Include operating, review, support, and change costs where relevant. Avoid counting the same benefit under several measures. Do not annualize a short observation window without labelling it an extrapolation and naming its assumptions.

### 4. Compare like with like

For a readout, record exposure to the new workflow, case mix, volume, staffing, seasonality, and other changes that could explain the result. Compare rates and quality as well as totals. Cite `post-deploy-watch` observations if available, without treating release stability as proof of business benefit.

A before/after change alone establishes an observed association. State attribution limits; use an agreed comparison or controlled experiment only when feasible and authorized. Do not claim the deployment caused every observed improvement.

### 5. Decide what the evidence supports

For each claim state supported, contradicted, or not yet measurable. Separate observations, estimates, and projections in the artifact and in the sponsor summary.

Recommend continue, adjust, investigate, or stop, naming the decision owner. Carry open measurements and their owners into `handover-pack`; `adoption-plan` handles barriers when intended users are not using the workflow. A future review date is a plan, not a completed measurement.

**Stop** when the baseline or its gap, metric definitions, measurement plan, available readout, attribution limits, and next decision are recorded. Do not invent precision to justify the engagement.

## Output template

Write `<workspace>/outcomes/<initiative>.md`:

```markdown
# Outcomes — <initiative>

**Engagement:** <name>
**Author:** FDE
**Date:** <YYYY-MM-DD>
**Status:** planned | baselined | measured | superseded
**Source revision:** <repo>@<SHA>, or "no repository yet"
**Confidence:** <observed vs. projected; attribution limits>

## Value hypothesis
**Owner:** <role> · **Claim:** <benefit> · **Decision:** <what results inform>

## Measures
| Metric | Definition/unit/population | Target and owner | Quality/harm guardrail |
|---|---|---|---|

## Baseline and plan
| Metric | Baseline | Source/window/sample | Exclusions | Post-change window | Reviewer/date |
|---|---|---|---|---|---|

## Benefit and cost assumptions
| Claim | Observed/estimated/projected | Calculation and units | Assumptions | Costs/overlap |
|---|---|---|---|---|

## Readouts
| Date/revision | Exposure/case mix | Result | Comparison | Confounders/limits |
|---|---|---|---|---|

## Position and next decision
| Claim | Supported/contradicted/unmeasured | Evidence | Next action/owner/date |
|---|---|---|---|
```

## Common traps

- Calling a deployed feature a realized benefit
- Converting elapsed waiting time into labor cost savings
- Reporting usage volume without an eligible-population denominator
- Attributing all improvement to the change despite staffing or case-mix changes
- Replacing the original baseline after seeing an inconvenient result
