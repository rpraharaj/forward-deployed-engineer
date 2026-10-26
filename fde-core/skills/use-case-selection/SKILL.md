---
name: use-case-selection
description: "Compare competing customer problems or potential use cases and recommend where an engagement should start, using impact evidence, data readiness, feasibility, sponsorship, risk, and time to first value. Use when there are several opportunities and no chosen problem. Sequencing already-scoped work is delivery-plan; choosing an implementation approach is solution-design."
---

# Use case selection

Choose a problem worth pursuing before committing to a solution.

**Maturity:** experimental — an initial synthetic procedure trial is recorded; live engagement validation is still needed.

## When this applies / when it doesn't

Use for a broad mandate, competing requests from several teams, or a shortlist whose priority has been asserted without evidence. The outcome may be an investigation or a decision to defer all candidates.

Skip when the problem is already selected. Use `delivery-plan` for the order of agreed work, `solution-design` for competing implementation approaches, and `feasibility-probe` for grounding a selected specification in code.

## Prerequisites

Resolve `<workspace>` using `../_shared/workspace-conventions.md`; follow its header and evidence rules.

- A bounded candidate list and the decision-maker, from the charter if available
- Workflow observations, existing metrics, stakeholder requests, or other available evidence
- Known deadlines, access restrictions, and non-negotiable controls

`discovery/workflow-*.md` is useful but optional. Missing evidence becomes a question to resolve, not a prerequisite chain that invents certainty.

## Procedure

### 1. Express each candidate as a problem

Give each a stable ID, affected user, observable pain, current workaround, and desired outcome. Separate a request for a particular technology from the need underneath it. Merge duplicates only when their users, constraints, and outcomes really match.

### 2. Establish what can be compared

Agree the criteria and decision authority before scoring. Consider impact and frequency, affected population, data/access readiness, accountable sponsor, delivery feasibility, adoption barriers, controls, and time to a useful result.

Use ranges or ordinal ratings with cited evidence. Missing data stays unknown. Record estimated effort as provisional until `feasibility-probe` and `estimation` ground it; this screening does not produce a delivery commitment.

### 3. Apply constraints before ranking

Separate hard exclusions from uncertainties and preferences. No permitted data access, no lawful/approved delivery route, or no owner able to accept the outcome may make a candidate unready. A high impact score does not cancel a hard constraint.

Name the smallest investigation that could resolve a load-bearing unknown. Do not quietly score unknown readiness as zero or assume it will be granted.

### 4. Compare robustly

Use a qualitative comparison unless weighted scoring actually helps. If using weights, record who chose them and check whether plausible changes reverse the winner. Show uncertainty and trade-offs instead of hiding them in one total.

Separate the highest potential value from the best first engagement. An early candidate should have a reachable user, a measurable result, a bounded slice, and a realistic route to data and approval.

### 5. Recommend a first move

State pursue, investigate, defer, or reject for each candidate, with the reason and condition for reconsideration. Include doing nothing or improving the existing process where credible.

For the preferred candidate, define the first slice, success signal, owner, constraints, and next evidence needed. Route to `outcome-measurement` for a business baseline and `requirements-to-spec` for behavior; run `feasibility-probe` before a firm estimate. Draft the decision request; do not send it without authorization.

**Stop** when each candidate has a disposition and the recommended next action is checkable. If evidence cannot distinguish candidates, recommend the discriminating investigation rather than manufacturing a winner.

## Output template

Write `<workspace>/discovery/opportunities.md`; preserve prior decisions when revising:

```markdown
# Opportunity selection — <scope>

**Engagement:** <name>
**Author:** FDE
**Date:** <YYYY-MM-DD>
**Status:** draft | decided | superseded
**Source revision:** <repo>@<SHA>, or "no repository yet"
**Confidence:** <evidence quality and unresolved uncertainties>

## Decision needed
**Decider:** <role> · **By:** <date> · **Recommendation:** <first move>

## Candidates
| ID | User/problem | Outcome | Current workaround | Evidence |
|---|---|---|---|---|

## Comparison
| ID | Impact/frequency | Data/access | Sponsor/adoption | Feasibility/time | Risk/controls | Confidence |
|---|---|---|---|---|---|---|

## Constraints and unknowns
| ID | Constraint or unknown | Consequence | To resolve | Owner |
|---|---|---|---|---|

## Dispositions
| ID | Pursue/investigate/defer/reject | Why | Revisit condition |
|---|---|---|---|

## First slice
**User:** <role> · **Result:** <observable> · **Success signal:** <measure>
**Next evidence:** <bounded investigation> · **Owner:** <role>
**Decision record:** <who decided, when; or pending>
```

## Common traps

- Ranking the loudest sponsor as the highest value
- Committing to dates from screening-level effort guesses
- Letting a weighted total conceal missing access or required controls
- Selecting an impressive demonstration with no path to sustained use
- Treating lack of evidence as evidence that a problem is small
