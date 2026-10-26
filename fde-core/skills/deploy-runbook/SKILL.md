---
name: deploy-runbook
description: Write the executable deployment procedure - pre-checks, ordered steps, what to observe after each, the specific conditions that trigger a rollback, and the rollback procedure itself - so that someone who is not the author can run it at 2am. Use before the first deploy of anything new or risky, when a release needs a documented procedure for a change board, when the deploy path exists only in one person's head, or when asked "how do we actually ship this". Insists the rollback is rehearsed rather than merely written.
---

# Deploy runbook

The procedure someone else can execute under pressure.

## Why this exists

Deployment knowledge in large organizations tends to live in one engineer's head, reconstructed each time from memory and a scroll through last quarter's chat history. That works until the deploy happens at 11pm on a Friday, or the engineer is on leave, or the person executing is a release manager who has never seen this service.

There's a second, sharper reason. **A rollback plan that has never been executed is a hypothesis.** The most common discovery during a real incident is that the migration wasn't reversible, or the rollback takes forty minutes, or it requires a permission the person on call doesn't have. All three are cheap to find out in advance and expensive to find out at the time.

## When this applies

- First deploy of anything new or risky
- A change board or auditor needs a documented procedure
- The deploy path exists only in someone's head
- Anything with a migration, a flag, or coordination between components

## When it doesn't

- Routine deploys through a mature, well-understood pipeline — don't add ceremony to something that works
- Local or throwaway environments
- A migration with a cutover window — that's `cutover-plan` *(fde-migration)*, which is a bigger artifact

## Prerequisites

Resolve `<workspace>` before reading or writing artifacts: read `../_shared/workspace-conventions.md` and follow its location and header rules. All artifact paths below use that resolved workspace. Preserve existing sections when appending.

- `<workspace>/06-blast-radius-*.md` — determines how careful the procedure must be
- `<workspace>/07-verification.md` — what's proven and what's a gap
- `<workspace>/01-environment.md` — the deploy commands, usually discoverable from CI
- `<workspace>/08b-change-control.md` — who may press the button, freeze windows, CAB ref. If missing, offer `change-control-navigation` rather than inventing SoD.

Read the CI/CD configuration before writing anything. The existing pipeline is the real deploy path, and a runbook that contradicts it is worse than none.

A cutover window is `cutover-plan` *(fde-migration)*. The observation window after a routine deploy is `post-deploy-watch` *(fde-operate)*. If those packs are not installed, keep rollback and watch sections in this runbook and say so.

## Procedure

### 1. Establish how deployment actually happens

Not how it's supposed to happen. Find the pipeline definition, the environments it targets, what's automated, what's manual, and who can trigger it.

Specifically establish:

- **Gates** — approvals, quality thresholds, freeze windows
- **Order** — if several components deploy, what depends on what
- **Segregation of duties** — in many regulated organizations the author may not deploy. That changes who this document is for.
- **Existing conventions** — if the team has a runbook format, match it

### 2. Write the pre-checks

Conditions that must hold before starting. Each must be checkable in under a minute, and each must have an explicit answer — a pre-check nobody can evaluate is decoration.

Typical: verification complete and gaps accepted, approvals obtained, no freeze in effect, dependencies deployed, the right build artifact identified by version or SHA, rollback rehearsed, the people who need to be present are present, monitoring visible.

**Name the artifact precisely.** "Deploy the latest build" is how the wrong thing gets deployed. Version, tag, or commit SHA.

### 3. Write the steps in execution order

Each step gets: **what to do**, **the exact command or UI action**, **what you expect to see**, and **what to do if you don't**.

That last column is what makes it a runbook rather than a checklist. "Run the migration" is a note to self; "run the migration, expect `V219 applied` in the output, and if you see a lock timeout, stop and go to step R2" is a procedure.

Order matters and is worth thinking about explicitly:

- Schema changes usually go first, and should be backward compatible so the old code keeps working
- Deploy behind a disabled flag where one exists, so deployment and activation are separate decisions
- For staged rollouts, name the stages and the dwell time at each

**Write for someone who has never seen this service.** Absolute paths, full commands, no implied context. The test is whether a competent engineer who isn't you could run it at 2am.

### 4. Say what to observe, with numbers

After each meaningful step, state what to look at and what "good" looks like.

Vague observation instructions get skipped. "Check the dashboard" is skipped; "check `refund_errors` on the payments dashboard — expect < 5/min, current baseline is 1/min" is not.

Include the baseline. Someone unfamiliar with the service cannot tell whether a number is alarming without knowing what normal is.

### 5. Define rollback triggers before you deploy

The conditions under which you abandon the deploy — written down **in advance**, because judgment degrades under pressure and a threshold agreed calmly at 3pm is worth more than one negotiated at midnight.

Each trigger needs a number and an observation window. "Error rate elevated" is not a trigger; "`refund_errors` above 20/min sustained for 5 minutes" is.

Also name **who decides**. Under pressure, an unclear decision-maker costs more time than the rollback itself.

### 6. Write the rollback procedure, then rehearse it

Same standard as the forward path: exact steps, expected results, and how long it takes.

Cover explicitly:

- **Code** — revert and redeploy? Which artifact do you go back to?
- **Schema** — is the migration reversible? Additive changes usually are; destructive ones are not, and "restore from backup" needs a tested procedure and an RTO.
- **Data written in the new shape** — what happens to records created between deploy and rollback? This is the question people forget, and it's often the one that makes rollback partial rather than clean.
- **Flags** — is disabling sufficient, or does partially-written state persist?
- **Downstream** — did anything irreversible leave the system? A published event, a sent notification, a partner call.

**Then rehearse it in a non-production environment and record how long it took.** This is the step that distinguishes a real runbook from a document. It routinely surfaces something surprising, and the whole point is to be surprised in staging rather than in production.

If rehearsal isn't possible, say so plainly — `release-readiness` treats an unrehearsed rollback as a material gap, and it should.

### 7. Identify the one-way doors

Points after which rollback is no longer clean. A destructive migration, a consumed message, a partner notification, an irreversible external call.

Mark them in the step list. If there's a one-way door, everything before it should be verified before crossing, and the team should know exactly where the point of no return sits.

### 8. Cover the post-deploy watch

Who watches, what, for how long, and what would still trigger a rollback after the deploy "completed." Use `post-deploy-watch` *(fde-operate)* if installed; otherwise keep the watch record here. A deploy isn't done when the pipeline goes green — it's done when the observation window closes without incident.

## Output template

Write to `<workspace>/runbooks/deploy-<service-or-change>.md`:

```markdown
# Deploy runbook — <change>

**Engagement:** <name>
**Author:** FDE
**Date:** <YYYY-MM-DD>
**Status:** draft | rehearsed | executed
**Artifact:** `<service>:<version>` — commit `<SHA>`
**Estimated duration:** <n> min · **Rollback duration:** <n> min (rehearsed <date>)
**Executed by:** <role — note if segregation of duties applies>
**Source revision:** <repo>@<short SHA>, or "no repository yet"
**Confidence:** <what is confirmed, inferred, or unverified>

## Summary
<One sentence a release manager understands.>

## Pre-checks
- [ ] Verification complete; gaps accepted — `07-verification.md`
- [ ] CAB approved — ref `<id>`
- [ ] No freeze in effect
- [ ] Dependencies deployed: <list>
- [ ] Artifact `<version>` present in registry
- [ ] Rollback rehearsed — <date>, <duration>
- [ ] Monitoring open: <dashboard link>
- [ ] Present: <roles>

## Steps

| # | Action | Command | Expect | If not |
|---|---|---|---|---|
| 1 | Snapshot current version | `<cmd>` | Records `v2.3.1` | Stop — can't roll back without it |
| 2 | Apply migration | `<cmd>` | `V219 applied` | Lock timeout → **R2** |
| 3 | Deploy, flag OFF | `<cmd>` | Pods healthy within 3 min | Rollout stalls → **R1** |
| 4 | Smoke check | `<cmd>` | HTTP 200, version `v2.4.0` | → **R1** |
| 5 | Enable flag at 5% | `<cmd>` | Flag shows 5% | — |
| 6 | **Observe 15 min** | dashboard | `refund_errors` < 5/min (baseline 1/min); p95 < 1.0s | → **R3** |
| 7 | Ramp to 100% | `<cmd>` | Flag at 100% | → **R3** |
| 8 | **Observe 30 min** | dashboard | as step 6 | → **R3** |

## One-way doors
| After step | What becomes irreversible | Verify before crossing |
|---|---|---|
| — | None identified — migration is additive `[confirmed]` | — |

## Rollback triggers
| # | Condition | Window | Decision |
|---|---|---|---|
| 1 | `refund_errors` > 20/min | 5 min sustained | On-call engineer, no escalation needed |
| 2 | p95 > 2.0s | 5 min sustained | On-call engineer |
| 3 | Any data inconsistency | immediate | Stop, escalate to <name> |

## Rollback

**Rehearsed:** yes — staging, <date>, 4 min

| # | Action | Command | Expect |
|---|---|---|---|
| R1 | Redeploy previous artifact | `<cmd>` | `v2.3.1` healthy |
| R2 | Migration | none — additive, safe to leave | — |
| R3 | Disable flag | `<cmd>` | Flag at 0%, errors return to baseline within 2 min |

**Records written while enabled:** rows with `currency` set remain; old code ignores the column `[confirmed]`.

## Post-deploy watch
**Who:** <name> · **Duration:** <n> hours · **Watching:** <metrics>
**Still-rollback-able until:** <when>

## Execution log
| Date | Environment | Outcome | Notes |
|---|---|---|---|
```

## Common traps

**Writing a rollback you haven't run.** A hypothesis, not a plan. Rehearse it and record the duration.

**"Deploy the latest build."** Name the version or SHA.

**Steps with no expected result.** Then the executor can't tell success from failure, which is the whole job.

**Observation instructions without numbers or baselines.** Someone unfamiliar can't judge whether a value is alarming.

**Rollback triggers decided in the moment.** Judgment degrades under pressure. Agree thresholds in advance.

**No named decision-maker.** Ambiguity costs more time than the rollback.

**Ignoring data written in the new shape.** The question that makes rollback partial rather than clean.

**Assuming you'll be the one running it.** Segregation of duties, leave, and on-call rotation all say otherwise. Write for a stranger.

**Treating pipeline-green as done.** It's done when the observation window closes.
