---
name: fde-orient
description: "Open a new engagement as a forward deployed engineer - establish what you have actually been asked to do, classify the engagement type, set up the .fde workspace, and produce a sequenced plan of which skills to run. Use when starting at a new client, joining an unfamiliar team, being assigned to a project you know nothing about, or when someone says \"I've been dropped into X and don't know where to start\". Also use when an engagement changes shape mid-flight (an enhancement turns into a rescue, scope shifts, the sponsor changes) and the original plan no longer fits. Scope note - this opens an engagement once, at the start. It is not the skill for a specific technical question inside an engagement already underway: sizing a change is feasibility-probe, mapping a codebase is repo-recon, getting access is access-and-onboarding."
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

Resolve the workspace the same way later skills will — see `../_shared/workspace-conventions.md`. Do not assume `.fde/` in the repo root.

```bash
# Order: $FDE_WORKSPACE, then .fde/, then a sibling *-fde/
if [ -n "$FDE_WORKSPACE" ]; then
  if [ -f "$FDE_WORKSPACE/00-engagement.md" ]; then
    cat "$FDE_WORKSPACE/00-engagement.md"
  else
    printf '%s\n' 'No charter at the configured FDE_WORKSPACE; resolve or initialize that location in step 6. Do not fall back.'
  fi
elif [ -f .fde/00-engagement.md ]; then
  cat .fde/00-engagement.md
else
  ls -d .fde ../*-fde 2>/dev/null
fi
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

### 4. Flag stated ask vs suspected real problem — do not workshop the spec

Ask yourself, and where it is cheap to ask the user: **what happens if we don't do this?** Record the stated ask verbatim and, if they differ, one sentence on the suspected real problem.

Do **not** turn this into requirements gathering. Unpacking actors, acceptance criteria, and out-of-scope is `requirements-to-spec`. Orient that spends the sponsor's patience on the spec is why they go quiet when you need them later.

If the current human process is unclear, sequence `workflow-discovery`. If several problems compete, use `use-case-selection` before choosing requirements. For a chosen initiative, establish its business baseline with `outcome-measurement`; use `adoption-plan` when end users must change their daily work. These are conditional paths, not gates on an already-clear small task.

### 5. Classify the archetype

Only name skills that exist. Pack skills are marked; if that pack is not installed, say so and substitute the nearest core skill rather than inventing a procedure.

| Archetype | Pack to install | Characteristic path |
|---|---|---|
| **Brownfield enhancement** | core | `repo-recon` → `requirements-to-spec` → `feasibility-probe` → `trace-the-flow` → `blast-radius` → `characterization-tests` → `safe-change` → `verification-plan` → `release-readiness` |
| **Greenfield in an existing org** | core | `repo-recon` *(of the platform)* → `requirements-to-spec` → `nfr-baseline` → `solution-design` → build → `verification-plan` → `deploy-runbook` |
| **Integration** | **`fde-platform`** | `repo-recon` *(both sides)* → `requirements-to-spec` → `nfr-baseline` → `feasibility-probe` → `blast-radius` → `contract-design` → `integration-adapter` → `verification-plan` → `release-readiness` |
| **Migration / replatform** | **`fde-migration` + `fde-data` + `fde-operate`** | `repo-recon` → `data-archaeology` → `solution-design` → `refactor-seams` → `verification-plan` → `cutover-plan` → `post-deploy-watch` |
| **Rescue / stabilization** | **`fde-operate`** | `incident-triage` → `repo-recon` → `ci-forensics` → `verification-plan` → `delivery-plan` *(replan honestly; do not build until it is stable)* |
| **Assessment only** | core | `repo-recon` → `feasibility-probe` → `blast-radius` → `stakeholder-brief` |
| **Version / EOL upgrade** | **`fde-migration`** | `repo-recon` → `dependency-upgrade` → `blast-radius` → `characterization-tests` → `deploy-runbook` *(staged)* → `verification-plan` |
| **Data / analytics** | **`fde-data`** | `repo-recon` → `data-archaeology` → `data-pipeline-work` → `test-data-strategy` → `release-readiness` |
| **COTS / package** | **`fde-platform`** | `repo-recon` *(of platform config)* → `requirements-to-spec` → `cots-configuration` → `change-control-navigation` → `cutover-plan` *(if `fde-migration` is also installed)* |
| **Decommission** | **`fde-migration`** | `repo-recon` → `decommission-plan` |
| **Regulatory / audit-driven** | core | `requirements-to-spec` *(from the obligation)* → `feasibility-probe` → `nfr-baseline` → `change-control-navigation` → `release-readiness` |
| **Spike / PoC** | core | timeboxed `feasibility-probe` → `stakeholder-brief` |
| **Open problem / opportunity selection** | core | `workflow-discovery` → `use-case-selection` → `outcome-measurement` *(baseline)* → `requirements-to-spec` → `feasibility-probe` |
| **AI workflow / agent delivery** | **`fde-ai`** | `requirements-to-spec` → `feasibility-probe` → `solution-design` → `ai-evaluation` *(plan)* → `agent-action-safety` *(policy, if actions)* → build → `agent-action-safety` *(test)* → `ai-evaluation` *(candidate)* → `verification-plan` → `release-readiness` |
| **Field lessons for a shared product** | **`fde-product`** | permitted deployment evidence → `field-to-product` → product-owner decision; accepted work returns to the ordinary delivery path |

These paths show the main stages, not every prerequisite. Before sequencing a stage, read that skill's prerequisites and insert missing required work; do not skip it because it is absent from the table. If an optional pack is unavailable, use the core fallback and record the gap. In particular, without `fde-operate`, keep the watch plan and dated observations in core `deploy-runbook`.

Two notes worth carrying: **regulatory work** inverts the usual negotiation — the date is fixed and scope only appears negotiable, so `escalation-and-renegotiation` fires earlier than elsewhere. **COTS work** surprises engineers most: the binding constraint is the vendor's upgrade path, and the right answer is often "don't build that."

**If no archetype fits, say so.** Compose a path from the four disciplines below and state plainly in the charter that you are improvising. Forcing a bad fit produces a plan that looks authoritative and points the wrong way — worse than an honest gap.

> Every skill applies these regardless of archetype: ground claims in evidence, establish blast radius before changing anything, leave a durable artifact, and draft the way back before going forward.

### 6. Settle the workspace

Two decisions, both easy now and awkward later:

- **Location** — `.fde/` in the repo root by default. Honour `FDE_WORKSPACE` if already set. Some organizations won't accept a new top-level directory; then use `../<repo>-fde/`. Record whichever you chose, and write every later artifact there.
- **Committed or ignored** — committed artifacts are inheritable and reviewable; ignored ones avoid a hygiene argument with a team you just met. Ask, don't assume.

Then create the workspace and write the charter. See `../_shared/workspace-conventions.md`.

### 7. Sequence the work, and name the pack

Produce a short ordered list of the next three to five **installed** skills, each with a reason. Not the whole archetype path — a plan beyond about five steps in an unfamiliar organization is fiction, because step two will change it.

`access-and-onboarding` comes first in almost every engagement, because access lead times are the one constraint you cannot compress later. If it's not first, be able to say why.

If the archetype needs `fde-data`, `fde-migration`, `fde-platform`, `fde-operate`, `fde-product`, or `fde-ai`, tell the user to install that pack before those skills can run:

```bash
claude plugin marketplace add /path/to/FDE-Claude
claude plugin install fde-<pack>@fde-skills
```

For local development, load the core and selected pack for one session with `claude --plugin-dir /path/to/FDE-Claude/fde-core --plugin-dir /path/to/FDE-Claude/fde-<pack>`.

Do not sequence a pack skill that is not installed. Substitute a core skill and record the gap in the charter.

## Output template

Write to `<workspace>/00-engagement.md` (the location you just decided):

```markdown
# Engagement charter — <name>

**Engagement:** <name>
**Author:** FDE
**Date:** <YYYY-MM-DD>
**Status:** draft
**Source revision:** <repo>@<short SHA>, or "no repository yet"
**Confidence:** <what here is established vs. still assumed>

## Workspace
- **Location:** `.fde/` | `$FDE_WORKSPACE` | `../<repo>-fde/`
- **Committed to VCS:** yes | no
- **Decided by:** <who, when>
- **Packs needed:** core | + `fde-data` | + `fde-migration` | + `fde-platform` | + `fde-operate` | + `fde-product` | + `fde-ai`

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

**Accepting the stated ask at face value.** The person briefing you is often relaying someone else's request. Flag the difference in one sentence; do not run `requirements-to-spec` inside this skill.

**Sequencing a pack skill that is not installed.** The plan then names a procedure the session cannot load. Install the pack, or substitute a core skill and say so.

**Interrogating on day one.** Six batched questions read as competence; twenty sequential ones read as an audit. Infer everything you can first.

**Over-planning.** A twelve-step plan in an organization you've known for two hours is theatre. Three to five steps, then re-plan.

**Skipping the charter because it feels like overhead.** It is thirty minutes that later skills read instead of re-deriving, and it is the artifact that protects you when someone says in week six that the goal was always something else.

**Mistaking a rescue for an enhancement.** The most common misclassification. Signals: a date that's already slipped, a team that answers carefully, a predecessor nobody names, "it mostly works." Classify it as a rescue and the plan changes fundamentally — stabilize and re-plan honestly before building anything.

**Forcing an archetype.** If it doesn't fit, say it doesn't fit.
