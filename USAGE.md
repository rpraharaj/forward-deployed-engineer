# FDE Skills — User guide

An operator's manual for the forward deployed engineer skill portfolio.

**Currently built:** 50 skills across seven packs — `fde-core` (34) plus six optional packs. The seven additions for discovery, outcomes, adoption, product feedback, and AI are experimental.
**Why it's shaped this way:** [DESIGN.md](DESIGN.md) · **What was tested:** [VALIDATION.md](VALIDATION.md)

[Install](#install) · [Start a session](#start-in-your-working-project) · [Choose and invoke](#choose-and-invoke-a-skill) · [Worked walkthrough](#your-first-day) · [Review outputs](#review-and-continue) · [Resume](#resume-or-switch-agents) · [All 50 skills](#skill-reference) · [Troubleshooting](#troubleshooting)

---

## What this is

A portable set of agent skills and playbooks for an engineer who gets dropped into unfamiliar organizations and is expected to deliver — from a vague ask through to something running in production — on a stack they didn't choose, in a codebase nobody has documented, using the coding agent and authorized tools available to the team.

The skills focus on delivery procedures rather than language-specific code generation. They encode the **procedures** an experienced FDE follows and the **artifacts** those procedures produce, so the work is grounded, legible to the client team, and survives your departure.

---

## Install

Start with `fde-core` for the general delivery lifecycle. Add the pack that matches the engagement archetype `fde-orient` identifies. A specialized pack can be used separately when its prerequisites and engagement artifacts already exist.

Use the local installer to copy complete skills and shared resources into your working project's skill directory. For Codex:

```bash
python3 /path/to/forward-deployed-engineer/scripts/install-skills.py \
  --dest /path/to/your-project/.agents/skills --packs fde-core
```

Add optional packs to `--packs`, for example `fde-core fde-data fde-ai`. The installer requires Python 3.10+ and no third-party packages. It preserves unrelated skills and refuses conflicts; copied installations are snapshots. Follow the [integration and update guide](docs/integrations.md) for Codex, the optional Claude Code plugin route, and manual use in other hosts.

| Pack | Install when the engagement is | Skills |
|---|---|---|
| `fde-core` | general delivery lifecycle | 34 |
| `fde-data` | analytics, ETL, warehouse, reporting, schema change | 3 |
| `fde-migration` | replatform, EOL upgrade, cutover, decommission | 4 |
| `fde-platform` | integration, contract design, COTS (SAP/Salesforce/ServiceNow) | 3 |
| `fde-operate` | running what you shipped — pipelines, watch, observability | 3 |
| `fde-product` | vendor FDEs turning permitted field evidence into shared product improvements | 1 |
| `fde-ai` | delivered AI task evaluation and boundaries on agent tool actions | 2 |

The split is deliberate. Native skill hosts expose metadata before loading selected procedures, with discovery and context budgets that vary by host. Installing only what the engagement needs keeps that catalog focused.

Check the active agent's skill list and explicitly invoke an installed skill. In Codex, use `$fde-orient`; automatic matching and discovery are host-specific.

In hosts with automatic matching enabled, describing the situation can select a relevant skill. For example, *"I've just been assigned to a payments system I've never seen"* should suggest `fde-orient`. Explicit invocation is useful when checking discovery or choosing a specific procedure.

## Start in your working project

Install the library's skills into the project you are investigating, then open that project in the coding agent. A session opened in the FDE library checkout will otherwise investigate the library itself. The library is not the customer's application.

For a local Codex session, after installation:

```bash
cd /path/to/your-project
codex
```

Use your host's project-opening workflow for a desktop or IDE session. Read applicable team instructions before starting. The installer does not create or change those instructions.

Keep these locations distinct:

| Location | Purpose | When it changes |
|---|---|---|
| Library checkout, such as `forward-deployed-engineer/fde-core/skills/` | Canonical procedures and resources | When maintaining or updating the library |
| Working project's `.agents/skills/` in the Codex route | Installed skill copies, including `_shared/` references | When deliberately installing or refreshing packs |
| Resolved engagement workspace, often `.fde/` | Findings, decisions, plans, evidence, and handover records | As the engagement progresses |
| Existing working guide, or `<workspace>/repo-guide.md` | Commands, conventions, layout, and landmines for the next session | When new reusable facts are verified |

Do not write engagement findings into the installed skill folders. Ask the team whether installed copies and engagement artifacts belong in version control; they are separate decisions.

### Set the engagement workspace

Use `fde-orient` to open a new engagement or resume an existing one. It reads local evidence first, asks only for missing facts, records open questions, and settles the workspace location and commit/ignore choice.

Resolution follows the [shared workspace conventions](fde-core/skills/_shared/workspace-conventions.md):

1. An existing directory explicitly set by `FDE_WORKSPACE`.
2. The charter's `## Workspace` → **Location** field, located in `.fde/00-engagement.md` or a sibling engagement workspace.
3. An existing `.fde/` at the working repository root.
4. An existing `../<repo-name>-fde/` adjacent to the checkout.
5. Agree and initialize a location through `fde-orient` when none exists.

An explicitly configured but unavailable path must be resolved; later skills do not silently fall back. `<workspace>` in a procedure means the resolved path, not a literal folder name.

For an external workspace, a shell-launched session can inherit the setting:

```bash
mkdir -p /path/to/billing-fde
export FDE_WORKSPACE=/path/to/billing-fde
cd /path/to/your-project
codex
```

These are example paths to replace. A desktop session opened elsewhere may not inherit that shell variable; state the location in the prompt and record it in the charter. Keep restricted originals and credentials in approved storage, with permitted evidence references in the workspace.

## Choose and invoke a skill

Choose the next skill for the question you need answered, not a whole lifecycle at once. Check its prerequisites and stopping condition. Do not run a skill that is not installed or assume it can obtain unavailable access.

| Situation | Start with | Expected result |
|---|---|---|
| New or unclear engagement | `fde-orient` | Goal, boundaries, owners, workspace, and a short next-step sequence |
| Several possible customer problems | `use-case-selection` | A constrained comparison and first investigation |
| Unfamiliar codebase | `repo-recon` | A bounded map with evidence and gaps |
| Vague requested behavior | `requirements-to-spec` | Testable requirements and explicit exclusions |
| Requirements exist but effort is uncertain | `feasibility-probe` | Requirements grounded in the actual system |
| Well-scoped, authorized code change | `safe-change` | A verified change and change record |
| Incident affecting users | `incident-triage` | Impact and stabilization evidence before a broad discovery exercise |

### Natural-language requests

In a host with automatic matching enabled, describe the situation:

```text
I've inherited a billing service and need to assess multi-currency refunds.
We have repository access and can write local notes, but no production access.
Help me establish scope and the next investigation before implementing anything.
```

The intended starting skill is `fde-orient`. Check what the agent actually selects; natural-language matching is host-dependent and is not guaranteed by these examples.

### Explicit invocation

In Codex, enter this in the conversation, not in a terminal:

```text
$repo-recon Use the existing engagement charter to map this repository.
Record entry points, persistence, dependencies, tests, and coverage limits.
Do not implement a change.
```

Use the host's own skill selector or invocation syntax in other agents. The [integration guide](docs/integrations.md) separates Codex, the optional Claude Code plugin route, and untested hosts; a `$` invocation is not universal syntax.

### Manual use without native discovery

Point the agent at the complete checkout and specify the entry file:

```text
Read /path/to/forward-deployed-engineer/fde-core/skills/repo-recon/SKILL.md
and its required references, then follow it for the application project that is open.
Use the engagement workspace recorded in its charter. Stop after the map and
working guide; do not change application code.
```

The host must be able to read that location and provide the task's required tools. Keep sibling skills and shared resources available. This route does not establish automatic discovery or tested compatibility for an otherwise untested host.

### Give the agent enough context

A useful task prompt includes:

```text
Goal: <the decision or result needed>
Current state: <what exists and what has already been tried>
Scope: <system, task, or requirement; explicit exclusions>
Evidence: <repo, permitted examples, existing artifacts, and access gaps>
Workspace: <recorded location or existing charter>
Allowed actions: <inspection, local checks, edits, or other authorized work>
Success: <what you will review and what should remain explicitly unverified>
```

Unknowns can remain unknown. Ask the agent to record the gap and the owner or next evidence needed, rather than inventing a sponsor decision, interview, estimate, or executed result.

---

## The mental model

Three ideas. Everything else follows from them.

**1. Artifacts, not conversations.** Every skill persists its findings in the resolved engagement workspace: `.fde/` by default, or the external location recorded in the charter / `FDE_WORKSPACE`. A finding that lives only in a chat transcript is gone next session, and gone entirely when you leave. The workspace *is* the engagement's memory. Preserve existing project instructions; use `<workspace>/repo-guide.md` when no suitable working guide exists, and read it explicitly when switching agents. The `.fde/` paths in this walkthrough are examples of the default location.

**2. Evidence or a confidence tag.** Every claim carries a `file.java:88` citation, a command and its output, or one of three tags — `[confirmed]`, `[inferred]`, `[unverified]`. This is what makes you credible in week two rather than quietly routed around after being confidently wrong once.

**3. Skills compose.** Each reads the artifacts the previous ones wrote. `feasibility-probe` reads the system map and the spec rather than re-deriving them. Run them roughly in order and the work accumulates instead of repeating.

---

## Your first day

A worked example: assess a multi-currency refund change in an unfamiliar billing service, then continue toward delivery only as scope and evidence permit. This is an illustrative sequence, not a record of a tested customer deployment or a fixed two-day schedule. `.fde/` below means the workspace agreed for this example.

The prompts identify the intended skill. Use explicit invocation if the host's automatic matching selects something else. Review each result before continuing; the sequence can stop at an assessment and does not authorize deployment.

### 1. Open the engagement

> *"I've been assigned to the billing service at a client. They want me to add multi-currency refunds. I don't know anything about the system yet."*

Use **`fde-orient`**. It reads local evidence, asks only for missing facts about the ask, sponsor, timing, success, access, and prior attempts, and records unanswered questions. It classifies the engagement (here: *brownfield enhancement*) and opens the agreed workspace. The charter separates the stated ask from any suspected underlying need.

**Produces:** `.fde/00-engagement.md`

### 2. Get access moving before anything else

> *"What access am I going to need, and what should I request first?"*

Use **`access-and-onboarding`**. Enumerate required access, known approvers and lead times, and unknown owners. Prepare requests in dependency order; submit them only through the authorized organizational route. A skill does not grant the permissions it records.

Access lead times can block later work. Record the legitimate production evidence needed and its approval path early; do not assume direct production access is required or permitted.

**Produces:** `.fde/00b-access.md`

### 3. Set a context budget if the repo is large

> *"This monorepo has 30,000 files."*

Use **`context-strategy`**. Size the problem and set the approach: what to search, script, read, or delegate when supported and authorized. Name a bounded working set and persist the next step.

Use it for large trees, long engagements, or repeated loss of context. A small, understood, single-session task may not need it.

**Produces:** `.fde/00c-context.md` and a recorded working-guide location, with updates or a reason for deferral.

### 4. Map the system

> *"Help me understand this codebase."*

Use **`repo-recon`** for a bounded breadth-first pass: entry points, module boundaries, what the system stores, what it talks to, where churn concentrates, test topology, and risks. Run local checks only within the permitted scope; distinguish inspected code from observed execution.

It stops when you can answer five questions without looking anything up. That stopping rule is deliberate — depth comes later, and only where the work lands.

**Produces:** `.fde/02-system-map.md` and a durable working guide

### 5. Write down what's actually being asked

> *"The ticket just says 'support multi-currency refunds'. That's all I've got."*

Use **`requirements-to-spec`**. Separate the stated ask from the underlying need, write acceptance criteria as observable behavior, identify unhappy paths, and record exclusions. For refunds, the stakeholders still need to decide matters such as currency/rate policy, rounding, failures, and audit behavior; these are questions to resolve, not product rules supplied by the example.

**Produces:** `.fde/03-requirements.md`

### 6. Ground it in the real code

> *"How hard is this actually?"*

Use **`feasibility-probe`** against `.fde/03-requirements.md` and `.fde/02-system-map.md`. Per requirement: does the capability exist, which files and boundaries would change, and what evidence is missing? Trace a particular flow when the broad map cannot answer it.

For example, the probe might find an existing conversion helper, a published contract needing coordination, or no usable historical-rate data. Report only findings supported by the actual repository. This guide supplies neither those findings nor a firm estimate.

**Produces:** `.fde/04-feasibility.md`

### 7. Build it

> *"Let's implement R1."*

Use **`safe-change`** only once R1 is scoped and implementation is authorized. Establish a test baseline, inspect the affected behavior and callers, add characterization coverage where needed, make a bounded change, and verify the requirement. Prepare rollback and satisfy the skill's prerequisites; do not infer implementation permission from the earlier assessment request.

**Produces:** the change, plus `.fde/06b-change-log.md`

### 8. Decide whether to ship

> *"Are we ready to go live?"*

Use **`release-readiness`** after the applicable verification, rollout/rollback, ownership, and change-control evidence exists. It assesses the evidence, states residual unknowns, and recommends a release position. A recommendation does not execute a deployment or replace required release authority.

**Produces:** `.fde/08-release-readiness.md`

### What you should be able to inspect

The assessment portion creates only the artifacts required for its actual scope. A possible layout is:

```text
.fde/
├── 00-engagement.md
├── 00b-access.md            # if access planning was needed
├── 00c-context.md           # if context planning was needed
├── 02-system-map.md
├── 03-requirements.md
├── 04-feasibility.md
└── repo-guide.md            # only if no suitable existing guide exists
```

Inspect a feasibility row by asking: **which requirement, what source evidence, what needs changing, what remains unknown, and who resolves it?** An answer such as “conversion exists” without a source and its limits is not enough to support an estimate. Keep unfinished measurements and owner questions open.

For complete examples actually produced during the scoped native Codex trials, inspect the [synthetic system map](eval/portability-trials/codex-2026-10-27/existing-working-guide/.fde/02-system-map.md) and [portable working guide](eval/portability-trials/codex-2026-10-27/portable-guide-fallback/.fde/repo-guide.md). Their observed commands, source revisions, and unverified behavior are explicit. These examples concern the synthetic Parcel Desk project, not the illustrative billing change above.

## Review and continue

Before treating an artifact as an input to the next skill:

- Confirm its engagement, scope, source revision, date, and status. A map from another revision may need a focused refresh.
- Follow important citations and distinguish observed results from estimates, plans, or unrun checks. A favorable summary cannot establish a missing required measurement.
- Check unresolved questions, owners, prerequisites, and the stopping condition. Record unknown ownership rather than assigning a person without evidence.
- Correct misunderstandings in the relevant artifact while preserving earlier evidence and unrelated sections. Mark superseded findings so a later reader can identify the current position.

Then request one bounded next step, for example:

```text
Use requirements-to-spec to clarify the refund behavior in the charter.
Read the current system map, retain unanswered owner questions, and stop after
draft acceptance criteria. Do not implement or deploy anything yet.
```

When prerequisites cannot be supplied, use the [missing-input guidance](#when-an-upstream-artifact-is-missing). A provisional investigation can carry a confidence limit; it cannot waive a mandatory access, safety, or release control.

## Resume or switch agents

Before ending a session, update the relevant artifacts, working guide, current revision, unresolved questions, and exact next step. Preserve existing project instructions rather than creating a competing copy for each host.

In a new session, open the same working project and make the required skills available through that host's integration. Explicitly request the relevant files:

```text
Continue the refund assessment. Read .fde/00-engagement.md, the working guide
recorded there, .fde/02-system-map.md, and .fde/03-requirements.md.
Check whether their revision still matches the affected code. Summarize gaps,
then probe R1's feasibility only. Keep the other requirements pending.
```

Use the actual filenames and workspace, and mention only artifacts that exist. The charter or context notes record the guide; it may be an existing `AGENTS.md`, `CLAUDE.md`, another team file, or `<workspace>/repo-guide.md`. Automatic loading differs by host. The detailed [context conventions](fde-core/skills/_shared/agent-context.md) explain preservation and explicit reads.

---

## Skill reference

Waves 1–3 are in `fde-core`. Waves 4–5 name the pack explicitly. Requests illustrate intended selection rather than guaranteeing automatic matching. Artifact paths are relative to the resolved workspace; some skills append to existing records rather than creating a new file.

### Wave 1 — the spine

| Skill | Example request | Produces |
|---|---|---|
| **`fde-orient`** | "new client", "just been assigned", "dropped into", "where do I start" | `00-engagement.md` |
| **`access-and-onboarding`** | "can't get access", "waiting on permissions", "what do I need to request" | `00b-access.md` |
| **`context-strategy`** | "this repo is huge", "running out of context", "where do I even start reading" | working guide, working set |
| **`repo-recon`** | "help me understand this repo", "what does this system do" | `02-system-map.md`, working guide |
| **`requirements-to-spec`** | "they want us to add X", vague ticket, "nobody's defined done" | `03-requirements.md` |
| **`feasibility-probe`** | "how hard would it be", "can we do X by <date>", "this plan feels optimistic" | `04-feasibility.md` |
| **`safe-change`** | "let's implement", "make this change" — in code you don't own | the change, `06b-change-log.md` |
| **`release-readiness`** | "are we ready to ship", "CAB needs a submission", "go/no-go" | `08-release-readiness.md` |

### Wave 2 — depth where the risk is

| Skill | Example request | Produces |
|---|---|---|
| **`env-bootstrap`** | "can't build this", "works on my machine", broken local setup | `01-environment.md` |
| **`knowledge-interview`** | "meeting the person who built this", "the code can't tell me why" | `interviews/<date>-<person>.md` |
| **`trace-the-flow`** | "what happens when a customer does X", "how does this actually work" | `traces/<operation>.md` |
| **`blast-radius`** | "what breaks if we touch this", before anything shared or published | `06-blast-radius-<change>.md` |
| **`characterization-tests`** | "no tests here and I need to change it", "nobody knows what it does" | tests + change-log note |
| **`test-data-strategy`** | "tests need data I don't have", "can we copy prod?" | `03c-test-data.md` |
| **`verification-plan`** | "how do we know this works", before claiming done | `07-verification.md` |
| **`deploy-runbook`** | "how do we actually ship this", first risky deploy | `runbooks/deploy-<change>.md` |

### Wave 3 — organizational

The skills for the reasons engagements actually fail. Technical work dying for non-technical reasons is the FDE's most common failure mode.

| Skill | Example request | Produces |
|---|---|---|
| **`ownership-map`** | "who owns this", "who do I need to review this" | `02b-ownership.md` |
| **`estimation`** | "how long will this take", a date is being committed | `05b-estimate.md` |
| **`delivery-plan`** | "what order", "what's the sequence", replanning after a slip | `05-delivery-plan.md` |
| **`nfr-baseline`** | spec covers behavior but not performance/security/audit | `03b-nfrs.md` |
| **`solution-design`** | "how should we build this", more than one plausible approach | `adr/NNNN-<slug>.md` |
| **`change-control-navigation`** | "CAB", "freeze period", "it's done but can't ship" | `08b-change-control.md` |
| **`stakeholder-brief`** | sponsor needs an update, a decision is needed outside the team | `briefs/<date>-<topic>.md` |
| **`escalation-and-renegotiation`** | "the plan isn't achievable", a dependency isn't moving | logged in the charter |
| **`incident-triage`** | "prod is broken", alert fired, start of a rescue | `incidents/<date>-<slug>.md` |
| **`handover-pack`** | engagement ending, rotating off | `09-handover.md` |
| **`enablement-handoff`** | "the team has to run this without me" | `09b-enablement.md` |

Three skills load per-stack references on detection rather than hardcoding a language: `repo-recon` (entry points across nine stacks), `trace-the-flow` (following DI, reflection, event buses, generated code), and `characterization-tests` (test harnesses and approval-test tooling).

### Wave 4 — deeper investigation and specialized delivery

Core skills below are available in `fde-core`; other rows name the optional pack to install before use. Artifact paths are relative to the resolved engagement workspace unless the row explicitly describes a code/schema change.

| Skill | Pack | Example request | Produces |
|---|---|---|---|
| `git-archaeology` | core | "Why does this old retry limit exist?" | `traces/why-<symbol>.md` |
| `nfr-validation` | core | "Show whether the change meets the agreed latency and load targets" | NFR evidence appended to `07-verification.md` |
| `security-compliance-check` | core | "Check the change's data handling and required security review" | Security evidence appended to `08-release-readiness.md` |
| `data-archaeology` | fde-data | "What do these tables and identifiers actually mean?" | `traces/data-model.md` |
| `data-pipeline-work` | fde-data | "Change this ETL pipeline without breaking data correctness" | Pipeline change and `traces/pipeline-<name>.md` |
| `db-change-management` | fde-data | "Plan this schema change and backfill" | Migration/rollback section in `runbooks/deploy-<change>.md` and change-log summary |
| `dependency-upgrade` | fde-migration | "Move off this unsupported library version" | Upgrade change and `05c-upgrade-matrix.md` |
| `refactor-seams` | fde-migration | "Replace this legacy implementation in stages" | Target-shape ADR and tracking in `06b-change-log.md` |
| `cutover-plan` | fde-migration | "How do we switch to the replacement safely?" | `runbooks/cutover-<name>.md` |
| `decommission-plan` | fde-migration | "Retire this system without stranding consumers" | `runbooks/decommission-<system>.md` |
| `ci-forensics` | fde-operate | "Why does CI fail when local checks pass?" | `07b-ci-notes.md` and fixes where authorized |
| `observability-gap` | fde-operate | "Could we detect this failure before users do?" | Monitoring changes and incident notes or `07c-observability.md` |
| `post-deploy-watch` | fde-operate | "What should we watch after rollout?" | Dated observations and decision thresholds in the deploy runbook |
| `contract-design` | fde-platform | "Define a compatible API or event contract" | `adr/NNNN-contract-<name>.md` and a machine-readable schema in the repository |
| `integration-adapter` | fde-platform | "Integrate with this unreliable external system" | Adapter change and `traces/<external-system>.md` |
| `cots-configuration` | fde-platform | "Configure or extend this vendor platform?" | `05d-cots-assessment.md` and decision ADRs |

### Wave 5 — discovery, outcomes, adoption, and field learning

These seven procedures are experimental. Use them for the named situation; a clear small task does not need a new discovery or adoption workstream.

| Skill | Pack | Example request | Produces under the resolved workspace |
|---|---|---|---|
| `workflow-discovery` | core | "Map how finance actually handles invoices across email and spreadsheets" | `discovery/workflow-<name>.md` |
| `use-case-selection` | core | "We have five possible problems; where should we start?" | `discovery/opportunities.md` |
| `outcome-measurement` | core | "Did this engagement deliver the claimed business benefit?" | `outcomes/<initiative>.md`, retaining its baseline and dated readouts |
| `adoption-plan` | core | "It's live but users keep the old workaround" | `adoption/<initiative>.md` |
| `field-to-product` | fde-product | "Turn a recurring workaround into a permitted shared-product proposal" | `product-feedback/<topic>.md` |
| `ai-evaluation` | fde-ai | "Compare the delivered assistant on representative held-out tasks" | `ai/evaluation-<workflow>.md` |
| `agent-action-safety` | fde-ai | "Verify what this agent is allowed to cause through its tools" | `ai/action-safety-<workflow>.md` |

Human workflow discovery complements code tracing; opportunity selection precedes implementation design; business benefit differs from technical NFR measurement; user adoption complements operator enablement. Product feedback carries explicit confidentiality/reuse boundaries. The AI pack evaluates the delivered system, not this repo's skill-selection evaluator. Plans, blocked checks, and observed results remain labelled separately.

---

## Workflows by engagement type

`fde-orient` picks one of these and sequences it. All 50 skills exist; install the pack the charter names before sequencing pack skills. Paths show main stages; insert each stage's actual prerequisites when needed.

| Engagement | Path |
|---|---|
| **Brownfield enhancement** | orient → access → env-bootstrap → recon → requirements → feasibility → trace → blast-radius → characterization → safe-change → verification → deploy-runbook → release-readiness |
| **Assessment only** | orient → recon → feasibility → blast-radius → stakeholder-brief |
| **Rescue / stabilization** | incident-triage → orient *(reclassify honestly)* → env-bootstrap → recon → ci-forensics *(fde-operate)* → verification-plan → delivery-plan |
| **Integration** | orient → recon *(both sides)* → requirements → NFR baseline → feasibility → blast-radius → contract-design → integration-adapter *(fde-platform)* → verification → release-readiness |
| **Migration / replatform** | orient → recon → data-archaeology *(fde-data)* → solution-design → refactor-seams *(fde-migration)* → verification → cutover-plan *(fde-migration)* → post-deploy-watch *(fde-operate, or core runbook fallback)* |
| **Spike / PoC** | orient → timeboxed feasibility → stakeholder-brief |
| **Greenfield in an existing organization** | orient → platform recon → requirements → nfr-baseline → solution-design → build → verification → deploy-runbook |
| **Version / EOL upgrade** | orient → recon → dependency-upgrade *(fde-migration)* → blast-radius → characterization → staged deploy-runbook → verification |
| **Data / analytics** | orient → recon → data-archaeology → data-pipeline-work *(both fde-data)* → test-data-strategy → release-readiness |
| **COTS / package** | orient → platform/configuration recon → requirements → cots-configuration *(fde-platform)* → change-control-navigation → cutover-plan *(only with fde-migration)* |
| **Decommission** | orient → recon → decommission-plan *(fde-migration)* |
| **Regulatory / audit-driven** | requirements from the obligation → feasibility → nfr-baseline → change-control-navigation → release-readiness |
| **Open problem / opportunity selection** | workflow-discovery → use-case-selection → outcome-measurement *(baseline)* → requirements → feasibility |
| **AI workflow / agent delivery** | requirements → feasibility → design → ai-evaluation *(plan)* → agent-action-safety *(policy, if tool actions)* → build → action-boundary tests → ai-evaluation *(candidate)* → verification → release-readiness; AI skills require fde-ai |
| **Field lessons for a shared product** | permitted deployment evidence → field-to-product *(fde-product)* → product-owner decision |

Brownfield enhancement — the most common engagement type — is covered end to end in `fde-core`.

Fifteen archetypes are defined in total — see [DESIGN.md §7](DESIGN.md). If none fits, `fde-orient` will say so rather than force one, and compose a path from first principles. After release, use `adoption-plan` and dated `outcome-measurement` readouts when the engagement includes those responsibilities; they do not replace release checks.

---

## Conventions you'll see everywhere

### Confidence tags

| Tag | Means |
|---|---|
| `[confirmed]` | Read the code, or ran it and observed the result |
| `[inferred]` | Strong structural signal, not directly verified |
| `[unverified]` | Believed but untested — always names what would resolve it |

The `[unverified]` items are not noise to be tidied away. In `feasibility-probe` and `release-readiness` they *are* the risk register.

### Artifact headers

Every artifact opens with **Engagement**, **Author**, **Date**, **Status**, **Source revision**, and **Confidence**. The source revision matters most: precise line citations against an unrecorded commit go stale silently, and a reader who trusts them will be misled. If no repository exists, record "no repository yet" rather than inventing a revision. See the [complete header conventions](fde-core/skills/_shared/workspace-conventions.md#artifact-header).

### The workspace

`.fde/` in the repo root by default. Numbered files give whoever inherits it a reading order. Gaps are normal — a workspace with missing numbers is honest, not incomplete.

Two decisions `fde-orient` will ask about once: where the workspace lives (some organizations won't accept a new top-level directory), and whether it's committed or gitignored. Both are defensible; the point is to decide rather than drift.

**Never goes in the workspace:** secrets or credential values, customer data, or anything a named individual said in confidence.

---

## When an upstream artifact is missing

Skills read each other's outputs. If `feasibility-probe` runs without a system map, it will say so and offer to run `repo-recon` first.

You can override this for a genuinely narrow piece of work — a one-hour spike doesn't need the full chain. The skill will then note the missing input in its Confidence line:

> **Confidence:** No blast-radius analysis was run — impact assessment is `[inferred]` from the system map only.

That's an honest artifact. What the skills won't do is silently reconstruct a missing input inline, because that produces an uncited version of something that should have been durable.

---

## What is built vs what is tested

All 50 skills are built. What remains untested is most of their **procedures** — see [VALIDATION.md](VALIDATION.md) for the precise coverage statement. The seven new procedures remain experimental after passing their initial synthetic scenario checks. Requests and criteria are in `eval/procedure-scenarios.json`; executed results and artifact snapshots are indexed by `eval/procedure-results.json`.

Historical triggering results are 42/43 first choice on Claude before the description edits, then 43/43 on Grok, both for the earlier catalog. Those runs used the older permissive reply parser and did not establish valid runtime metadata. The repaired evaluator requires valid YAML and explicit answer syntax; the expanded 82-query suite covers all 50 skill descriptions. Consult the latest validation entry for actual execution results. Four skills have historical repository-based trials (`repo-recon`, `blast-radius`, `env-bootstrap`, `characterization-tests`), seven others have synthetic artifact trials, and native Codex trials add partial coverage of `context-strategy` and `handover-pack`. The remaining 37 have no recorded procedure trial. Shared-reference checks do not add to the skill count.

If you hit a skill whose procedure doesn't fit your situation, that's a finding worth recording — it's better evidence than anything in the design document.

Where a procedure does not fit, the coding agent handles the work without a skill — you just don't get the artifact template. Keep writing to the workspace with the same header and confidence conventions so the chain stays intact.

---

## Troubleshooting

### Skill absent or not selected

Separate installation/discovery from matching. In the local Codex route, check the installed files from the working project:

```bash
ls .agents/skills/fde-orient/SKILL.md
ls .agents/skills/repo-recon/SKILL.md
ls .agents/skills/_shared/workspace-conventions.md
```

If files are absent, confirm the installer destination and selected pack. The library checkout alone does not install skills into another project. If files exist, inspect the host's skill list, restart the session if needed, and try explicit invocation. If that works but a natural-language request selects a different skill, state the situation and intended scope more precisely. Use the host-specific locations in the [integration guide](docs/integrations.md) for other installation routes.

Duplicate project and user installations can expose conflicting versions. Identify which path the host used, and deliberately retain the intended version; do not remove unrelated skills or change global settings blindly.

### Missing pack or broken references

If the request needs an optional skill, install its pack before invoking it. For an integration engagement, for example, run this from the working project after replacing the library path:

```bash
python3 /path/to/forward-deployed-engineer/scripts/install-skills.py \
  --dest .agents/skills --packs fde-core fde-platform
```

If `../_shared/...` or `references/...` cannot be read, confirm that the complete skill and resource folders are available. Do not copy only `SKILL.md` or flatten reference directories. Sibling references, such as a blast-radius reference into `trace-the-flow`, need the corresponding core folder too. Use the installer or the complete checkout for manual use.

### Installer conflict or stale copies

An "Existing files conflict" or symlink conflict stops the installer before copying new folders. It is not permission to overwrite team files. Identify the affected folder, compare it with the source, and follow the [deliberate update procedure](docs/integrations.md#updating-an-installation): back up and remove only copies you intend to replace, then reinstall. Keep any local edits for review. Pulling the library does not update previously copied skills automatically.

### Missing or misplaced engagement artifacts

Check the active session's `FDE_WORKSPACE`, then the charter's Location and the [resolution order](#set-the-engagement-workspace). For a shell-launched session, inspect only that setting:

```bash
printenv FDE_WORKSPACE
```

An unset value allows the remaining resolution steps. An explicitly set but missing directory is a blocker. Resolve it or deliberately choose another location through `fde-orient`; do not create a second workspace silently. A desktop session may have a different environment, so record the chosen location in the charter and state it in the prompt.

`<workspace>` and `<initiative>` in procedures are placeholders. Replace them with the resolved directory and a descriptive name; do not create literal placeholder paths. When an output is absent, ask whether the skill stopped on a prerequisite, produced a response without writing, or wrote to another recorded location.

### Missing inputs, access, or executable checks

Use the upstream skill when its artifact is required. If only a provisional investigation is possible, record the absent evidence, resulting confidence limit, owner, and next permitted step. Do not describe a proposed interview, unrun test, or inaccessible production check as completed. A missing mandatory control remains a gate, even when analysis can continue.

If a host or command fails before the skill runs, distinguish that runtime/setup problem from a procedure failure. Record the command category, exit status, and sanitized diagnostic; keep credentials and raw sensitive traces out of reports. An attempted run with no usable result is unverified, not a pass.

### Too much work, repeated context, or the wrong kind of action

Choose one phase and stopping condition. For an assessment, say "inspect and write findings; stop before implementation". If the request spans mapping, requirements, and delivery, run the next bounded skill and review its result before expanding scope.

When the agent starts rediscovering prior work, point it to the existing charter, working guide, current revision, and relevant artifacts using the [resume example](#resume-or-switch-agents). Automatic context loading differs between agents.

For a short engagement, keep only the artifacts needed for its decisions, and make upstream gaps explicit. For example, an assessment may stop with a charter, system map, and a scoped findings brief. Artifact numbers and lifecycle tables are reading aids, not a demand to execute every skill.

---

## Adapting this

The portfolio is written to be edited. Two things to preserve if you change anything:

**The evidence discipline.** It's the convention every other part depends on, and the one that makes the difference between being trusted and being tolerated.

**Stack-agnosticism.** No SKILL.md body should name Maven, npm, or pytest. Stack specifics belong in `_shared/stack-detection.md` or a `references/` file loaded only when detected. If you find yourself writing a stack assumption into a skill body, push it down a level.

Everything else — templates, ordering, the artifact numbering — is yours to change to fit how your organization actually works.
