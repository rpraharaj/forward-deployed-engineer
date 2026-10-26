---
name: adoption-plan
description: "Plan and assess how intended end users move to a new business workflow, including barriers, process ownership, a bounded pilot, support, fallback, and successful-use measures. Use when a live solution is underused, users keep an old workaround, or rollout needs changes to daily work. Training the receiving technical team to operate the system is enablement-handoff; deploying code is deploy-runbook."
---

# Adoption plan

Make the new workflow usable in the work people actually do.

**Maturity:** experimental — an initial synthetic procedure trial is recorded; live engagement validation is still needed.

## When this applies / when it doesn't

Use for end-user transition, a rollout with unclear process ownership, or evidence that intended users are avoiding a delivered solution.

Use `enablement-handoff` for the technical team maintaining the system, `post-deploy-watch` for release health, and `incident-triage` when active failures are harming users. Do not label a broken workflow a training problem.

## Prerequisites

Resolve `<workspace>` using `../_shared/workspace-conventions.md`; follow its privacy and header rules.

- Intended users, process owner, and the change being introduced
- Workflow observations, agreed behavior, and outcome measures if available
- Technical readiness and known limitations from verification/release artifacts where they exist

Missing usage data or user access is a gap to investigate. Do not infer that users are resistant from low usage alone.

## Procedure

### 1. Name who must do what differently

Separate user groups by task, access, support needs, and constraints. Describe the old action, the new action, why it helps, and who owns the resulting process. Include users whose work changes indirectly through a handoff.

Establish which process changes the owner may approve and which require another control owner. Adoption planning does not authorize bypassing approvals or removing a mandatory fallback.

### 2. Observe barriers with representative users

Have available users attempt a representative task using approved examples. Record the point of friction and evidence: missing permission, missing data, poor fit, unclear output, duplicate entry, lack of trust, incentive conflict, or inaccessible interaction.

Distinguish a product defect, a process defect, and a knowledge gap. Route defects through normal delivery; use targeted instruction for a demonstrated knowledge gap. Record unavailable observations as unverified instead of inventing interviews.

### 3. Design a bounded pilot

Choose an eligible group and task set, start/end dates, process owner, support contact, entry criteria, success measures, and stop/fallback conditions. Account for the extra work of parallel old/new processes and reconcile results before widening.

Do not retire an old workflow merely because training occurred. Determine who authorizes retirement, what evidence they need, and how users regain a workable path if the new one fails. Software rollback and business fallback may be different operations.

### 4. Make support and communication concrete

Prepare role-specific task guidance, the known limitations, an escalation path, and the support capacity needed during the pilot. Link the authoritative runbook rather than duplicating it. Draft announcements and invitations; send only when the user authorizes it.

Use `enablement-handoff` when the receiving technical team also needs capability transfer. It is a parallel activity, not evidence that end users adopted the workflow.

### 5. Measure successful use and act

Use an eligible-population denominator and a defined window: eligible tasks, attempted tasks, successfully completed tasks, exceptions, rework, and fallback use. Pair usage with task quality and business outcomes; logins and training attendance alone do not establish adoption.

Use approved aggregate information, not covert individual monitoring. Record what has been observed separately from planned targets. Widen, revise, pause, or end the pilot according to the agreed evidence and authority. Link benefit claims to `outcome-measurement`.

**Stop** when ownership, barriers, pilot/support/fallback arrangements, measures, and the next review are recorded. If no pilot ran, leave its outcome pending; do not report planned adoption as achieved.

## Output template

Write `<workspace>/adoption/<initiative>.md`:

```markdown
# Adoption — <initiative>

**Engagement:** <name>
**Author:** FDE
**Date:** <YYYY-MM-DD>
**Status:** planned | piloting | reviewed | superseded
**Source revision:** <repo>@<SHA>, or "no repository yet"
**Confidence:** <observed barriers and usage vs. assumptions>

## People and process
| User group | Task | Old/new action | Process owner | Constraint |
|---|---|---|---|---|

## Barriers
| Evidence/window | Barrier | Defect/process/knowledge | Action | Owner |
|---|---|---|---|---|

## Pilot
**Eligible group/tasks:** <scope> · **Window:** <dates> · **Owner:** <role>
**Entry criteria:** <readiness> · **Success:** <thresholds and quality>
**Stop/fallback:** <trigger, action, authority, reconciliation>
**Old-workflow retirement:** <owner and evidence needed, or not planned>

## Support and communication
| Need | Guidance/contact | Capacity | Owner | Drafted/authorized/delivered |
|---|---|---|---|---|

## Readouts
| Window | Eligible/attempted/completed | Quality/rework/fallback | Limits | Decision/owner |
|---|---|---|---|---|

## Next review
<Date, accountable reviewer, unresolved questions, and artifacts to update.>
```

## Common traps

- Calling login counts or workshop attendance adoption
- Blaming users before observing a failed task
- Training people to work around a defect instead of addressing it
- Leaving the old process running indefinitely with no owner or exit criteria
- Widening a pilot despite unmet entry criteria or unsafe fallback
