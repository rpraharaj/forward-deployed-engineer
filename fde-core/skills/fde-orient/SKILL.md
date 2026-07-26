---
name: fde-orient
description: Open a new engagement as a forward deployed engineer - establish what you have actually been asked to do, classify the engagement type, set up the .fde workspace, and produce a sequenced plan of which skills to run. Use when starting at a new client, joining an unfamiliar team, being assigned to a project you know nothing about, or when someone says "I've been dropped into X and don't know where to start". Also use when an engagement changes shape mid-flight (an enhancement turns into a rescue, scope shifts, the sponsor changes) and the original plan no longer fits. Scope note - this opens an engagement once, at the start. It is not the skill for a specific technical question inside an engagement already underway: sizing a change is feasibility-probe, mapping a codebase is repo-recon, getting access is access-and-onboarding.
---

# FDE Orient

The front door to an engagement. Everything else in the portfolio reads the charter this produces.

## Why this exists

The most expensive mistakes an FDE makes are made in the first week, before anyone knows enough to catch them: solving the stated ask instead of the real problem, mapping a system nobody needed mapped, or committing to a date before knowing what the code looks like. Those mistakes are cheap to prevent and very expensive to unwind — by the time they surface you've spent your credibility budget on the wrong thing.

This skill exists to spend thirty minutes establishing what is actually going on, and to leave a written charter that later skills read instead of re-deriving.

## When this applies

- Starting at a new organization, client, or team
- Assigned to a project or system you don't know
- An engagement changes character and the plan no longer fits
- You're several days in and realize nobody wrote down what "done" means

## When it doesn't

- A single well-defined task inside a system you already know — just do the task
- An active production incident. Run `incident-triage`; orient afterwards if you're staying.
- The charter already exists and is current. Read it and continue.

## Prerequisites

None. This is the entry point.

## Procedure

### 1. Check for an existing engagement

```bash
cat .fde/00-engagement.md 2>/dev/null || ls -d .fde ../*-fde 2>/dev/null
```

If a charter exists, read it. Decide with the user whether this is a **continuation** (read it, proceed, don't restart) or a **re-orientation** (the engagement changed; supersede the old charter rather than editing it, so the history of what was believed survives).

### 2. Infer before you ask

Every question you ask that the filesystem could have answered spends the user's patience for no reason. Gather first:

```bash
pwd && ls -a && git remote -v 2>/dev/null && git log --oneline -10 2>/dev/null
```

Read any `README`, `CONTRIBUTING`, `docs/`, or `CLAUDE.md`. Note what stack is present (see `../_shared/stack-detection.md`) and how active the repository is.

You are looking for: does a system already exist, is it maintained, how big is it, and does the repository suggest what it does.

### 3. Ask only the gaps

Ask these in **one batch**, not as an interrogation. Skip any you can already answer. If the user doesn't know an answer, that itself is a finding — record it as an open question with an owner.

1. **What exactly were you asked to do?** Request it verbatim if possible — the original wording carries ambiguity that a paraphrase silently resolves in the wrong direction.
2. **Who asked, and who is the actual sponsor?** These are frequently different people, and the second one defines success.
3. **What's driving the timing?** A regulatory date, a contract, a peak-season freeze, and "the manager would like it soon" impose completely different constraints.
4. **What does done look like?** If nobody can answer this, that is the single most important thing to fix this week.
5. **What access do you have right now?** Feeds straight into `access-and-onboarding`.
6. **What's already been tried, and by whom?** Rescue engagements almost always have a history, and repeating a failed approach is a fast way to lose the room.

### 4. Separate the stated ask from the real problem

Ask yourself, and where sensible ask the user: **what happens if we don't do this?** The answer usually reveals the actual need, which is often adjacent to the request rather than identical to it.

A request to "make the nightly batch faster" may be a need to have figures ready for a 7am meeting — solvable by running it earlier, or by producing a partial result first, neither of which involves optimizing anything.

Record both. The stated ask is what you were asked; the real problem is what you'll be judged on. Where they differ, say so explicitly in the charter — that sentence is often the highest-value thing an FDE writes all engagement.

### 5. Classify the archetype

| Archetype | Signals | Characteristic path |
|---|---|---|
| **Brownfield enhancement** | Existing maintained system, new feature | recon → requirements → feasibility → trace → blast-radius → characterization → safe-change → verify → release |
| **Greenfield in an existing org** | Nothing built yet, but platform constraints exist | recon *(of the platform)* → requirements → nfr-baseline → solution-design → build → verify → deploy-runbook |
| **Integration** | Two systems that must talk | recon *(both sides)* → contract discovery → integration-adapter → blast-radius → verify → release |
| **Migration / replatform** | Move from X to Y, data moves, both run for a while | recon → data-archaeology → solution-design → **cutover-plan** → refactor-seams → dual-run → cutover → post-deploy-watch |
| **Rescue / stabilization** | Late, broken, or a team in distress | incident-triage → recon → ci-forensics → verification-plan → stabilize → delivery-plan *(replan honestly)* |
| **Assessment only** | "Tell us what you think" — no code change expected | recon → feasibility → blast-radius → stakeholder-brief |
| **Version / EOL upgrade** | External deadline, fixed scope, vendor support ending | recon → dependency-upgrade → blast-radius → characterization → incremental cutover → verify |
| **Data / analytics** | Pipelines, warehouse, reporting | recon → data-archaeology → data-pipeline-work → test-data-strategy → reconciliation → release |
| **COTS / package** | SAP, Salesforce, ServiceNow, Workday, Guidewire | recon *(of platform config)* → requirements → cots-configuration → change-control → cutover |
| **Decommission** | Turning something off | recon → consumer discovery → decommission-plan → staged darkening → archival |
| **Regulatory / audit-driven** | Obligation or audit finding drives it, date is fixed | requirements *(from the obligation)* → feasibility → nfr-baseline → change-control → evidence pack |
| **Spike / PoC** | Timeboxed, answer a question, decision is the output | timeboxed feasibility → stakeholder-brief |

Two notes worth carrying: **regulatory work** inverts the usual negotiation — the date is fixed and scope only appears negotiable, so `escalation-and-renegotiation` fires earlier than elsewhere. **COTS work** surprises engineers most: the binding constraint is the vendor's upgrade path, and the right answer is often "don't build that."

**If no archetype fits, say so.** Compose a path from the four disciplines below and state plainly in the charter that you are improvising. Forcing a bad fit produces a plan that looks authoritative and points the wrong way — worse than an honest gap.

> Every skill applies these regardless of archetype: ground claims in evidence, establish blast radius before changing anything, leave a durable artifact, and draft the way back before going forward.

### 6. Settle the workspace

Two decisions, both easy now and awkward later:

- **Location** — `.fde/` in the repo root by default. Some organizations won't accept a new top-level directory; then use `../<repo>-fde/`. Record whichever you chose.
- **Committed or ignored** — committed artifacts are inheritable and reviewable; ignored ones avoid a hygiene argument with a team you just met. Ask, don't assume.

Then create the workspace and write the charter. See `../_shared/workspace-conventions.md`.

### 7. Sequence the work

Produce a short ordered list of the next three to five skills, each with a reason. Not the whole archetype path — a plan beyond about five steps in an unfamiliar organization is fiction, because step two will change it.

`access-and-onboarding` comes first in almost every engagement, because access lead times are the one constraint you cannot compress later. If it's not first, be able to say why.

## Output template

Write to `.fde/00-engagement.md`:

```markdown
# Engagement charter — <name>

**Engagement:** <name>
**Author:** FDE
**Date:** <YYYY-MM-DD>
**Status:** draft
**Source revision:** <repo>@<short SHA>, or "no repository yet"
**Confidence:** <what here is established vs. still assumed>

## Workspace
- **Location:** `.fde/`
- **Committed to VCS:** yes | no
- **Decided by:** <who, when>

## The ask
**As stated:** <verbatim>
**Requested by:** <name, role>
**Sponsor:** <name, role — the person whose problem this is>

## The real problem
<What breaks if this isn't done. Where this differs from the stated ask, say so explicitly.>

## Definition of done
<Observable conditions. If unknown, say so and name who must decide.>

## Archetype
**<archetype>** — <why this one fits>

## Constraints
| Constraint | Detail | Source |
|---|---|---|
| Deadline | | |
| Freeze / release window | | |
| Compliance regime | | |
| Team availability | | |
| Environment / access limits | | |

## Stakeholders
| Name | Role | Interest | Consulted or informed |
|---|---|---|---|

## History
<What's been tried, by whom, why it didn't land. Rescue engagements: fill this in properly.>

## Open questions
| # | Question | Who can answer | Blocking? |
|---|---|---|---|

## Assumptions
<Each one is a thing that, if wrong, changes the plan. Tag confidence.>

## Planned sequence
1. `<skill>` — <why>
2. ...

## Log
| Date | Change |
|---|---|
| <date> | Charter created |
```

## Common traps

**Accepting the stated ask at face value.** The person briefing you is often relaying someone else's request, filtered through their own model of what's possible. Ask what happens if it isn't done.

**Interrogating on day one.** Six batched questions read as competence; twenty sequential ones read as an audit. Infer everything you can first.

**Over-planning.** A twelve-step plan in an organization you've known for two hours is theatre. Three to five steps, then re-plan.

**Skipping the charter because it feels like overhead.** It is thirty minutes that later skills read instead of re-deriving, and it is the artifact that protects you when someone says in week six that the goal was always something else.

**Mistaking a rescue for an enhancement.** The most common misclassification. Signals: a date that's already slipped, a team that answers carefully, a predecessor nobody names, "it mostly works." Classify it as a rescue and the plan changes fundamentally — stabilize and re-plan honestly before building anything.

**Forcing an archetype.** If it doesn't fit, say it doesn't fit.
