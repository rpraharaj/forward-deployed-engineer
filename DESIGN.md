# FDE Skill Portfolio — Design

**Status:** Waves 1–3 built — `fde-core` complete at 27 skills, 5 shared references, 3 per-stack references. Wave 4 archetype packs designed, not yet written.
**Scope:** A portfolio of Claude Code skills that let one engineer be dropped into any team, in any organization, on any stack, and carry work from *requirement* to *go-live*.
**How to use what's built:** [USAGE.md](USAGE.md) · **Cold-start test results:** [VALIDATION.md](VALIDATION.md)

---

## 1. The role we're equipping

A Forward Deployed Engineer is hired into a large organization and rotated across teams. In any given quarter they might be asked to add a feature to a fifteen-year-old billing system, integrate two products after an acquisition, rescue a late migration, or stand up something new inside a platform nobody has documented.

They arrive with no context, no relationship capital, and no institutional memory. They are expected to produce something credible in days.

**The bottleneck is never writing code.** It is building an accurate enough mental model of an unfamiliar system, fast enough that a team who didn't ask for you starts trusting your judgment. Everything downstream — the design, the estimate, the change, the release — is gated on that.

So this portfolio is weighted toward **comprehension, grounding, blast radius, and verifiable claims**, not code generation. Claude already knows how to write a service. What it does not know is *the procedure for producing a system map that the team who owns the system agrees with.*

---

## 2. Operating constraints that shape every skill

These are not incidental. Each one changes how the skills must be written.

| Constraint | Consequence for design |
|---|---|
| **Claude Code is the only tool** | Assume filesystem, `git`, and a shell. Do not assume Jira/Confluence/GitHub MCP servers exist. Where they help, treat them as an optional accelerator with a filesystem fallback. |
| **Often no internet** | No dependence on WebSearch/WebFetch. Every skill must reach its conclusion from repo-local evidence and the running system. |
| **Locked-down machine** | Cannot install arbitrary tooling. Prefer what ships with the repo (its own build tool, its own test runner) over anything global. |
| **Stack is unknown until arrival** | Skills **detect, then adapt**. No skill hardcodes Maven, npm, or `pytest` in its main body. |
| **Proprietary code, real compliance** | Artifacts must be safe to leave behind. Never write secrets, customer data, or credentials into generated docs. |
| **The FDE has no authority** | Output must persuade, not assert. Claims that can't be evidenced get labelled as such, not laundered into confident prose. |
| **The FDE leaves** | Every skill produces a durable artifact. Work that lives only in a chat transcript is work that evaporates. |

---

## 3. Design principles

These are the things that make forty-three separate skills feel like one system.

### 3.1 Artifact-first
Every skill produces a **named file in a known location**, not just an answer in the terminal. This is what makes the FDE's work legible to the team, reviewable by a lead, and inheritable by whoever comes next. It also lets skills compose: the output of `repo-recon` is the input to `feasibility-probe`.

### 3.2 Evidence discipline
Every factual claim in an artifact carries one of:
- a `path/to/file.ext:142` citation, or
- a command and its observed output, or
- an explicit confidence tag.

Three tags, used consistently across all skills:

- **`[confirmed]`** — read the code, or ran it and observed the result
- **`[inferred]`** — strong signal from naming, structure, or convention, not directly verified
- **`[unverified]`** — believed but untested; needs someone with access or context to confirm

This is the single most important convention in the portfolio. It is the difference between an FDE who is trusted in week two and one who is quietly routed around after being confidently wrong once.

### 3.3 Detect, then load
Skills that need stack knowledge run a detection routine first, then read only the matching reference file. This is how the portfolio stays stack-agnostic without becoming vague:

```
safe-change/
├── SKILL.md                    ← universal procedure, no stack specifics
└── references/
    ├── stack-detection.md      ← shared: how to identify the stack
    ├── jvm.md                  ← loaded only if detected
    ├── dotnet.md
    ├── node-ts.md
    ├── python.md
    └── go.md
```

The SKILL.md body stays short and universal. The depth lives one level down and costs nothing until needed.

### 3.4 Cheap before expensive
Every comprehension skill orders its investigation from cheapest to most expensive: filenames → structure → targeted reads → running the thing. Skills should state explicitly when to stop. An FDE who spends three days building a perfect model of a system they need to change in one place has failed differently, but has still failed.

### 3.5 Reversibility as a first-class output
For anything that touches a running system, "how do I undo this" is not an appendix. `safe-change`, `release-readiness`, and `post-deploy-watch` all treat the rollback path as a required section, drafted before the forward path is executed.

### 3.6 Narrow skills, explicit routing
A skill that does four things gets a fuzzy description and triggers unreliably — and the description is the primary triggering mechanism. So skills stay narrow and single-purpose, and one entry-point skill (`fde-orient`) handles sequencing. Depth goes into `references/`, never into scope creep.

---

## 4. The lifecycle model

The portfolio maps to the arc an FDE actually walks, from a vague ask to something running in production.

```
  LAND                FRAME            UNDERSTAND        DESIGN
  ─────               ─────            ──────────        ──────
  access-onboarding   requirements     trace-the-flow    solution-design
  context-strategy    feasibility      archaeology       contract-design
  env-bootstrap       delivery-plan    blast-radius      nfr-baseline
  repo-recon          estimation
  ownership-map
  knowledge-interview

       BUILD              VERIFY             SHIP                 SUSTAIN
       ─────              ──────             ────                 ───────
       characterization   verification       release-readiness    post-deploy-watch
       safe-change        test-data          deploy-runbook       incident-triage
       refactor-seams     ci-forensics       cutover-plan         observability-gap
       dependency-upgrade nfr-validation     change-control       handover-pack
       db-change-mgmt     security-check     decommission-plan    enablement-handoff
       data-pipeline
       cots-configuration

     ← stakeholder-brief and escalation-and-renegotiation run across all phases →
```

Phases are a **default order, not a gate sequence**. Real engagements skip, loop, and reorder — the routing layer (§7) handles that.

---

## 5. Skill catalog

### 5.1 Entry point

| Skill | Purpose |
|---|---|
| **`fde-orient`** | The front door. Establishes the engagement: what archetype is this (§7), who are the stakeholders, what is the actual goal vs. the stated ask, what are the constraints, what does "done" mean. Creates the `.fde/` workspace and writes the engagement charter. Then recommends the sequence of skills to run. Invoked once per engagement; re-run when scope shifts. |

**Artifact:** `.fde/00-engagement.md`

---

### 5.2 Phase: LAND

| Skill | Triggers when | What it does | Artifact |
|---|---|---|---|
| **`env-bootstrap`** | "I can't build this", first day in a repo, broken local setup | Detects build system, runtime versions, package registries, required services, config/secret sources. Gets to a working build → test → run loop. Records every workaround discovered, because the next person will hit them too. | `.fde/01-environment.md` |
| **`repo-recon`** | Dropped into an unfamiliar codebase, "help me understand this repo" | Structured first pass: entry points, module boundaries, layering, churn hotspots (`git log` frequency), size/complexity outliers, test topology, dead zones, config surface. Deliberately breadth-first — it maps the territory, it does not explore any one region deeply. | `.fde/02-system-map.md` + a draft `CLAUDE.md` |
| **`ownership-map`** | Before asking anyone for anything; PR needs reviewers; "who owns this?" | Derives ownership and decision rights from evidence: `CODEOWNERS`, commit authorship over time, review patterns, ticket references in commit messages, directory-level activity. Distinguishes *who wrote it* from *who maintains it now* — usually different people, and the second group is the one that matters. | `.fde/02b-ownership.md` |

**Why `ownership-map` is a real skill and not a footnote:** an FDE's most common failure is technical work that dies politically. Knowing who must be consulted before a change is as load-bearing as knowing what the change is.

---

### 5.3 Phase: FRAME

| Skill | Triggers when | What it does | Artifact |
|---|---|---|---|
| **`requirements-to-spec`** | A vague ask from a stakeholder; "they want us to add X"; ambiguous ticket | Turns prose into testable statements. Separates stated ask from underlying need, surfaces the unasked questions, writes acceptance criteria as observable behavior, and explicitly lists what is **out** of scope. Flags every assumption made in the absence of an answer. | `.fde/03-requirements.md` |
| **`feasibility-probe`** | Immediately after a spec exists, before any estimate | **The signature FDE move.** Takes each requirement and grounds it in the actual codebase: does this capability already exist (and where), what would have to change, what is missing entirely, what looks cheap but isn't. Turns "we think this is a two-week job" into "here are the seven files this touches and the one integration nobody remembers owning." | `.fde/04-feasibility.md` |
| **`delivery-plan`** | Feasibility is done and someone wants dates or sequence | Sequences the work by risk, not by convenience — unknowns first, so bad news arrives early. Identifies dependencies on other teams, defines slices that are independently shippable, states what would change the plan. | `.fde/05-delivery-plan.md` |

**Why `feasibility-probe` is the highest-value skill in the portfolio:** every other role in the org can write a spec. Almost nobody can tell you, in hours rather than weeks, what that spec means against the real code. This is the capability that makes an FDE worth their cost, and it is what most estimation failures are actually a failure of.

---

### 5.4 Phase: UNDERSTAND

Deployed *selectively* — only where the planned change actually lands. This phase is where FDEs most often over-invest.

| Skill | Triggers when | What it does | Artifact |
|---|---|---|---|
| **`trace-the-flow`** | "How does X actually work?"; before changing anything on a request path | Follows one concrete operation end to end across every layer and process boundary — entry point, orchestration, persistence, messaging, downstream calls, error and retry paths. Produces a sequence narrative with a citation at every hop. | `.fde/traces/<flow>.md` |
| **`data-archaeology`** | Schema is undocumented; the domain model is unclear; migration work | Reconstructs the data model from whatever exists: migrations, DDL, ORM definitions, and — most reliably — the queries actually issued. Surfaces the gap between the schema's intent and its real use (nullable columns that are never null, enums with dead values, denormalization nobody documented). | `.fde/traces/data-model.md` |
| **`git-archaeology`** | Code looks wrong; "why is it like this?"; before deleting anything odd | Recovers intent from history: blame → commit → PR → linked ticket, plus revert and hotfix patterns. Exists specifically to prevent Chesterton's Fence errors — the ugly branch is often an incident fix, and removing it re-opens the incident. | Inline, or appended to the relevant trace |
| **`blast-radius`** | Before any non-trivial change; "what breaks if I touch this?" | Maps everything downstream of a proposed change: direct callers, cross-repo consumers, published contracts, event subscribers, feature flags, config coupling, and the DB objects shared with systems outside this repo. Ends with a risk rating and the specific things to verify. | `.fde/06-blast-radius-<change>.md` |

---

### 5.5 Phase: DESIGN

| Skill | Triggers when | What it does | Artifact |
|---|---|---|---|
| **`solution-design`** | Non-trivial change with more than one plausible approach | Generates genuine alternatives (including "do nothing" and "do it outside this system"), evaluates against real constraints from the earlier artifacts, recommends one, and records why the others were rejected. Written as an ADR so the reasoning survives the FDE's departure. | `.fde/adr/NNNN-<title>.md` |
| **`contract-design`** | New or changed API, event, or schema; anything crossing a team boundary | Designs the interface with compatibility as the primary concern: versioning strategy, backward compatibility, migration path for existing consumers, failure semantics. Includes a consumer-impact list derived from `blast-radius`. | `.fde/adr/NNNN-contract-<name>.md` |
| **`nfr-baseline`** | Before build starts on anything user-facing or load-bearing | Makes the non-functional requirements explicit and measurable *before* they become a launch blocker: latency and throughput targets, data sensitivity classification, audit/logging obligations, observability needs, failure and degradation behavior. Each one written as something you can actually test. | `.fde/03b-nfrs.md` |

---

### 5.6 Phase: BUILD

| Skill | Triggers when | What it does | Artifact |
|---|---|---|---|
| **`characterization-tests`** | About to change code with no meaningful test coverage | Pins current behavior before touching it — including the behavior that looks like a bug, because something downstream may depend on it. Golden-master and approval-test patterns. This is what makes legacy change safe rather than brave. | Tests in the repo's own convention |
| **`safe-change`** | Implementing any change in an unfamiliar or high-stakes codebase | The core implementation discipline: smallest viable diff, match surrounding idiom rather than importing your own, separate refactor commits from behavior commits, gate behind a flag where the blast radius warrants it, draft the rollback before executing the change. | PR + `.fde/06b-change-log.md` |
| **`refactor-seams`** | Code must change but is not safely changeable; extraction or strangler work | Finds the seams that let you change behavior without rewriting: branch-by-abstraction, strangler fig, adapter insertion. Always incremental, always leaving the system releasable at every step. | ADR + staged PRs |
| **`integration-adapter`** | Consuming a legacy, undocumented, or externally-owned interface | Builds a client against a system you don't control and can't fully see: contract discovery from observed traffic and existing callers, defensive parsing, timeout/retry/circuit-breaking posture, and a fake for testing. | Adapter + `.fde/traces/<external-system>.md` |

---

### 5.7 Phase: VERIFY

| Skill | Triggers when | What it does | Artifact |
|---|---|---|---|
| **`verification-plan`** | Once implementation is underway; before claiming anything is done | Maps every acceptance criterion from `03-requirements.md` to the specific evidence that proves it — which test, which manual check, which metric. Its main output is the **gap list**: criteria with no verification. | `.fde/07-verification.md` |
| **`ci-forensics`** | Pipeline is red, flaky, or slow; "it works on my machine" | Diagnoses the failure class — genuine break, flake, environment drift, ordering dependency, resource contention — before attempting fixes. Distinguishes "make it green" from "make it right" and says which one is being done. | Fix + `.fde/07b-ci-notes.md` |
| **`nfr-validation`** | Before release, against `03b-nfrs.md` | Actually measures the things `nfr-baseline` declared: performance under realistic load, behavior at failure boundaries, that the audit logging exists and contains what it should. Reports measured numbers, not assurances. | Appended to `.fde/07-verification.md` |
| **`security-compliance-check`** | Pre-release gate; anything touching sensitive data | Reviews the change specifically for data handling: what PII/PCI/PHI crosses this path, is it logged, is it encrypted in transit and at rest, are secrets externalized, does the audit trail satisfy the obligation identified in `nfr-baseline`. | Appended to `.fde/08-release-readiness.md` |

---

### 5.8 Phase: SHIP

This phase is what "go-live" actually consists of, and it is the part most engineering skill sets ignore entirely.

| Skill | Triggers when | What it does | Artifact |
|---|---|---|---|
| **`release-readiness`** | Approaching go-live; a change board or approval is required | Assembles the go/no-go position from evidence already gathered, rather than from opinion: verification status, open gaps, blast radius, rollback plan, sign-offs still needed. Produces a recommendation **and** the honest list of what is still unknown. Formatted to survive a change-advisory review. | `.fde/08-release-readiness.md` |
| **`deploy-runbook`** | Before the first deploy of anything new or risky | Writes the executable sequence: pre-checks, ordered steps, expected observation after each, the specific conditions that trigger rollback, and the rollback procedure itself. Written so someone who is not the FDE, at 2am, can run it. | `.fde/runbooks/deploy-<service>.md` |
| **`cutover-plan`** | Migration or replatform; data moves; two systems briefly coexist | The hardest artifact in the portfolio. Covers data migration and backfill, dual-run and reconciliation strategy, the consistency window, traffic shifting, the point of no return, and what "abort" means at each stage. | `.fde/runbooks/cutover-<name>.md` |
| **`post-deploy-watch`** | Immediately after release | Defines and executes the watch: smoke checks, the specific metrics that would indicate this change broke something, the observation window, and pre-agreed rollback triggers. Converts "seems fine" into a recorded verification. | Appended to the deploy runbook |

---

### 5.9 Phase: SUSTAIN

| Skill | Triggers when | What it does | Artifact |
|---|---|---|---|
| **`incident-triage`** | Production is broken; alert fired; "customers are seeing errors" | Works backward from symptom to code under time pressure: stack trace to source, correlation IDs across services, log and metric narrowing, recent-change correlation. Prioritizes mitigation over root cause, and says explicitly which one it is doing. | `.fde/incidents/<date>-<name>.md` |
| **`observability-gap`** | After any incident where the answer was hard to find | Asks the diagnostic question: could we have seen this? Identifies missing logs, metrics, traces, and alerts, and adds them. The compounding skill — each pass makes the next incident cheaper. | PR + notes |
| **`handover-pack`** | Engagement ending; rotating to another team | Consolidates everything into what the receiving team actually needs: refreshed `CLAUDE.md`, runbooks, ADRs, known issues, the things only the FDE currently knows. Explicitly includes **open risks and unfinished business** — the section most handovers omit and every receiving team needs. | `.fde/09-handover.md` |

---

### 5.10 Cross-cutting

| Skill | Notes |
|---|---|
| **`stakeholder-brief`** | Used at every phase boundary, not once at the end. Translates the current technical position into something a director reads in ninety seconds: what changed, what it means, what decision is needed, what the risk is. Deliberately separate from the technical artifacts, because the same facts need very different framing for an engineer and for a sponsor. |

---

### 5.11 Second-pass additions (gap analysis)

The first-pass catalog was audited against what enterprise IT engagements actually contain. It was **service-and-application shaped** — it assumed the FDE arrives at a code repository and changes code. A large share of big-organization IT is not that. Thirteen additions close the genuine holes.

#### A. Week-one reality (the most costly omissions)

| Skill | The gap it closes |
|---|---|
| **`access-and-onboarding`** | The single most expensive omission. FDEs routinely lose one to two weeks to access: VPN, repo permissions, DB read grants, build and pipeline rights, ticket and wiki accounts, test environments, secrets vaults. The skill turns this into a tracked critical path — enumerate what's needed *before* it blocks, identify the approver for each, sequence the requests by lead time, and record workarounds. Nothing else in the portfolio can run until this does. |
| **`knowledge-interview`** | The original catalog assumed all answers live in the code. They don't. The highest-value source in a legacy organization is a person who has been there nine years, and the FDE gets maybe forty minutes of their time. Structured extraction: what to ask, in what order, how to capture tacit knowledge, how to distinguish what someone knows from what they assume, and how to convert an interview into cited artifacts. |
| **`context-strategy`** | Given that Claude Code is the only tool, this is core craft and it was entirely absent. How to work productively in a repository far larger than any context window: what to read versus search versus delegate to subagents, how to build a durable `CLAUDE.md` so each session doesn't re-derive the same map, when to write a throwaway script to answer a question at scale rather than reading files one by one, and how to structure long engagements across many sessions. |
| **`test-data-strategy`** | Blocks all verification and was missing. Production data usually cannot be copied for legal reasons, so realistic test data must be constructed: synthesis, subsetting, masking and referential-integrity preservation, fixtures for the awkward edge cases. In regulated organizations this is frequently the actual bottleneck to shipping, not the code. |

#### B. Project archetypes the catalog didn't serve

| Skill | The gap it closes |
|---|---|
| **`dependency-upgrade`** | EOL-driven work — Java 8→21, .NET Framework→Core, Angular 1→current, database major versions, expiring vendor support — is an enormous share of enterprise IT and behaves unlike feature work: the scope is fixed, the deadline is external, and the risk is concentrated in transitive breakage. Ordering, compatibility matrices, incremental cutover, and how to tell a real break from a warning. |
| **`data-pipeline-work`** | Analytics, ETL/ELT, warehouse and reporting projects are roughly half of large-organization IT and the original catalog had nothing for them. Different failure modes entirely: silent data quality decay, late-arriving and duplicate records, backfill and reprocessing, idempotency, lineage, reconciliation against a source of truth. |
| **`cots-configuration`** | SAP, Salesforce, ServiceNow, Workday, Dynamics, and industry platforms like Guidewire or Temenos. Vast swathes of enterprise IT are **configuration, not code** — and the discipline differs sharply: vendor upgrade paths constrain what you may customize, config lives in the platform rather than in git, and "how do I version and review this" is a real question. Includes when to refuse customization because it will break the next vendor upgrade. |
| **`decommission-plan`** | Turning systems off. Common, genuinely hard, almost never planned properly. Proving there are no remaining consumers (much harder than it sounds), data retention and archival obligations, the staged darkening sequence, and how long to keep the ability to reverse. |
| **`db-change-management`** | Schema change against a live production database is distinct from application change and was folded in too casually. Zero-downtime DDL, expand/contract patterns, migration reversibility, lock and replication-lag behavior on large tables, and coordinating a schema change with the application deploy that depends on it. |

#### C. Organizational navigation

The first pass had `ownership-map` and `stakeholder-brief` and little else. But an FDE's technical work most often dies for organizational reasons, not technical ones.

| Skill | The gap it closes |
|---|---|
| **`change-control-navigation`** | Large organizations have CAB, stage gates, release calendars, freeze periods, and mandatory approvals. Work that ignores this is technically complete and undeployable. Identify the applicable process early, understand what evidence each gate requires, and work backward from the release window. |
| **`estimation`** | Split out from `delivery-plan`, which conflated sequencing with sizing. Estimating under genuine uncertainty, grounded in `feasibility-probe` findings rather than optimism: ranges over points, explicit assumptions, what would move the number, and how to communicate uncertainty to people who want a single date. |
| **`escalation-and-renegotiation`** | The hardest thing an FDE does. When the plan is no longer achievable, when a dependency isn't moving, when the requirement is wrong — how to raise it early with evidence rather than late with excuses, and how to reopen scope without losing credibility. |
| **`enablement-handoff`** | Distinct from `handover-pack` (documents) — this is teaching the team. For many engagements the real deliverable is a team that can continue without you. Pairing, walkthroughs, deliberately leaving work for them to finish, and confirming they can actually operate what you built. |

---

### 5.12 Shared references (not directly invoked)

Consumed by the skills above, kept in one place so the conventions stay consistent:

- **`stack-detection.md`** — the detection routine and its signal table (build files, lockfiles, CI configs, container and orchestration manifests, IaC). Used by `env-bootstrap`, `repo-recon`, `safe-change`, `verification-plan`, `deploy-runbook`.
- **`evidence-discipline.md`** — the citation and confidence-tagging convention from §3.2.
- **`workspace-conventions.md`** — the `.fde/` layout, artifact naming, and how skills read each other's outputs.
- **`enterprise-constraints.md`** — working behind proxies and internal registries, without admin rights, offline; and the data-handling posture for proprietary code.
- **`comms-register.md`** — how to write for engineer vs. lead vs. sponsor vs. change board.

---

## 6. Shared infrastructure

### 6.1 The `.fde/` workspace

All artifacts land in a single directory, numbered to give whoever inherits it a natural reading order:

```
.fde/
├── 00-engagement.md              # charter: archetype, stakeholders, goal, constraints
├── 01-environment.md             # how to build, test, run — including the workarounds
├── 02-system-map.md              # cartography
├── 02b-ownership.md              # who owns what, who decides
├── 03-requirements.md            # testable spec with acceptance criteria
├── 03b-nfrs.md                   # measurable non-functionals
├── 04-feasibility.md             # requirements grounded in real code
├── 05-delivery-plan.md           # risk-ordered sequence
├── 06-blast-radius-<change>.md
├── 06b-change-log.md
├── 07-verification.md            # criteria → evidence, and the gap list
├── 08-release-readiness.md       # go/no-go
├── 09-handover.md
├── adr/       NNNN-<title>.md
├── traces/    <flow>.md
├── runbooks/  deploy-<svc>.md, cutover-<name>.md
└── incidents/ <date>-<name>.md
```

**Location is configurable per engagement**, decided in `fde-orient`. Some organizations will not accept a new top-level directory in their repo; the workspace then lives adjacent to the checkout. Skills read the location from `00-engagement.md` rather than hardcoding it.

### 6.2 Artifact contract

Every artifact carries a consistent header so a reader knows what they're holding and how much to trust it:

```markdown
# <Artifact title>
**Engagement:** <name> · **Author:** FDE · **Date:** <ISO date>
**Status:** draft | reviewed | superseded
**Confidence:** what in here is confirmed vs. inferred vs. unverified
**Sources:** repos, branches, commit SHAs, and environments this was derived from
```

The commit SHA matters more than it looks: an artifact describing a system that has since moved on is actively misleading, and the SHA is what lets a future reader tell.

### 6.3 Composition

Skills read each other's artifacts rather than re-deriving context. `feasibility-probe` reads `02-system-map.md` and `03-requirements.md`; `release-readiness` reads verification, blast radius, and NFR artifacts. When a required upstream artifact is missing, the skill says which one and offers to run that skill first — it does not silently guess.

---

## 7. Engagement archetypes (routing)

`fde-orient` classifies the engagement, because the path through the catalog differs sharply:

| Archetype | Characteristic path |
|---|---|
| **Brownfield enhancement** | recon → requirements → feasibility → trace → blast-radius → characterization → safe-change → verify → release |
| **Greenfield in an existing org** | recon *(of the platform, not a codebase)* → requirements → nfr-baseline → solution-design → contract-design → build → verify → deploy-runbook |
| **Integration** | recon *(both sides)* → contract discovery → integration-adapter → blast-radius → verify → release |
| **Migration / replatform** | recon → data-archaeology → solution-design → **cutover-plan** → refactor-seams → dual-run → cutover → post-deploy-watch |
| **Rescue / stabilization** | incident-triage → recon → ci-forensics → verification-plan → stabilize → delivery-plan *(replan honestly)* |
| **Assessment only** | recon → feasibility → blast-radius → stakeholder-brief *(no code change)* |
| **Version / EOL upgrade** | recon → dependency-upgrade → blast-radius → characterization → incremental cutover → verify |
| **Data / analytics** | recon → data-archaeology → data-pipeline-work → test-data-strategy → reconciliation → release |
| **COTS / package implementation** | recon *(of the platform and its config)* → requirements → cots-configuration → change-control → cutover |
| **Decommission / sunset** | recon → consumer discovery → decommission-plan → staged darkening → archival |
| **Regulatory / audit-driven** | requirements *(from the obligation, not a stakeholder)* → feasibility → nfr-baseline → change-control-navigation → evidence pack |
| **Proof of concept / spike** | timeboxed feasibility → stakeholder-brief *(decision, not code)* |

The archetype is recorded in `00-engagement.md` and revisited when the engagement changes shape — which it usually does, most often from "enhancement" to "rescue."

Two archetypes deserve a note. **Regulatory-driven work** inverts the normal negotiation: the deadline is externally fixed and the scope is theoretically negotiable but practically isn't, so `escalation-and-renegotiation` fires earlier and harder than elsewhere. **COTS implementation** is the archetype most likely to surprise an engineer who has only worked on code — the constraint is the vendor's upgrade path, and the correct answer is often "don't build that."

---

## 8. SKILL.md house style

Consistency across forty-three skills matters more than local cleverness.

**Frontmatter** — the `description` is the primary triggering mechanism, so it states both *what the skill does* and *the concrete situations that should invoke it*, phrased the way a user would actually describe the moment. Descriptions lean slightly assertive, because the common failure mode is under-triggering.

**Body structure:**
```markdown
## When this applies / when it doesn't
## Prerequisites          ← which upstream artifacts, and what to do if missing
## Procedure              ← cheap steps first; explicit stopping conditions
## Output template        ← the exact artifact structure
## Common traps           ← failure modes specific to this activity
```

**Length:** SKILL.md under ~250 lines. Depth goes to `references/`.

**Voice:** imperative, and explain *why* a step matters rather than issuing rules. A skill that says "always do X" gets followed mechanically; one that explains what goes wrong without X gets applied with judgment — which is the whole point in environments this varied.

**Stopping conditions are mandatory.** Each comprehension skill states when it has enough. Without this, they run until context is exhausted.

---

## 9. Build order

Not phase by phase. **A thin end-to-end spine first**, so we find out early whether the artifact chain actually composes — that's the risky assumption in this design, and it's cheap to test now and expensive to discover late.

**Wave 1 — the spine (8 skills)**
`fde-orient` · `access-and-onboarding` · `context-strategy` · `repo-recon` · `requirements-to-spec` · `feasibility-probe` · `safe-change` · `release-readiness`

Walks a real engagement from ask to go-live, thinly. Proves the workspace convention, the evidence discipline, and inter-skill composition. `access-and-onboarding` and `context-strategy` were promoted into Wave 1 by the gap analysis: the first because nothing else can run before it, the second because every other skill degrades badly in a repository too large for context.

**Wave 2 — depth where the risk is (8)**
`env-bootstrap` · `trace-the-flow` · `blast-radius` · `characterization-tests` · `verification-plan` · `deploy-runbook` · `knowledge-interview` · `test-data-strategy`

The skills that prevent the expensive failures: breaking something invisible, shipping without a way back, or being unable to verify anything because no usable data exists.

**Wave 3 — org and lifecycle (11)**
`solution-design` · `delivery-plan` · `estimation` · `nfr-baseline` · `stakeholder-brief` · `ownership-map` · `change-control-navigation` · `escalation-and-renegotiation` · `handover-pack` · `enablement-handoff` · `incident-triage`

**Wave 4 — specialist and archetype packs (16)**
`cutover-plan` · `integration-adapter` · `refactor-seams` · `contract-design` · `data-archaeology` · `git-archaeology` · `ci-forensics` · `observability-gap` · `security-compliance-check` · `nfr-validation` · `post-deploy-watch` · `db-change-management` · `dependency-upgrade` · `data-pipeline-work` · `cots-configuration` · `decommission-plan`

Wave 4 is deliberately last: these fire on specific engagement types, and their content will be sharper once the earlier waves have been exercised on real repos.

### 9.1 A constraint the count creates

Forty-three skills is a lot, and skill names and descriptions load into context **every session**, whether or not they fire. A portfolio this size spends real context budget continuously — which is exactly the resource `context-strategy` exists to protect.

That argues for splitting distribution rather than trimming content:

- **`fde-core`** — Waves 1–3 (27 skills). Always installed. Applies to every engagement.
- **`fde-data`** — data-pipeline-work, data-archaeology, test-data-strategy, db-change-management
- **`fde-migration`** — cutover-plan, decommission-plan, dependency-upgrade, refactor-seams
- **`fde-platform`** — cots-configuration, integration-adapter, contract-design
- **`fde-operate`** — incident-triage, observability-gap, ci-forensics, post-deploy-watch

The FDE installs core plus whichever pack matches the archetype `fde-orient` identified. This keeps the always-on cost near the original thirty while covering far more ground. It depends on the distribution decision in §13.

---

## 10. Deliberately excluded, and why

Not everything an FDE does deserves its own skill. These were considered and folded in elsewhere — recorded so the reasoning survives, and so we don't re-litigate them.

**Already provided by Claude Code — do not rebuild:** inbound code review (`/code-review`) and security review of pending changes (`/security-review`). The portfolio should reference them, not duplicate them.

**Folded into existing skills as `references/`:**

| Considered | Folded into |
|---|---|
| Infrastructure-as-code and provisioning (Terraform, Helm, CloudFormation) | `deploy-runbook` |
| Accessibility, internationalization, license/SBOM compliance | `nfr-baseline` |
| Capacity planning, disaster recovery and BCP validation | `nfr-validation` |
| Technical debt assessment | `feasibility-probe` — it's the same grounding procedure with a different output framing |
| Proof-of-concept and spike work | `feasibility-probe`, timeboxed variant |
| RAID logs and status reporting cadence | `stakeholder-brief` |
| Third-party and vendor coordination | `delivery-plan` |
| Performance tuning (as opposed to measurement) | `nfr-validation` |
| Cloud migration | an instance of the migration archetype, not a separate one |
| M&A systems integration | an instance of the integration archetype at larger scale |
| FinOps and cost optimization | an assessment-archetype engagement; no distinct procedure |

The test applied: *does this activity have a genuinely different procedure, or only a different subject?* Different procedure earns a skill. Different subject earns a reference file.

---

## 11. Why this list can never be complete

The honest answer to "have we covered everything" is no, and no version of this document will. Enterprise IT generates situations faster than anyone can enumerate them, and the next engagement will contain something absent from all forty-three entries.

That makes the **disciplines more important than the catalog**. An FDE who has internalized four things will handle an unlisted situation well:

1. **Ground every claim in evidence** — cite, or tag the uncertainty (§3.2)
2. **Establish blast radius before changing anything** — the question generalizes far past code
3. **Leave a durable artifact** — whatever the activity was
4. **Draft the way back before going forward** — reversibility as a default posture

`fde-orient` therefore carries a specific responsibility: when an engagement matches no archetype, it should not force a bad fit. It should compose a path from these principles and say plainly that it is improvising. A portfolio that silently mislabels an unfamiliar engagement is worse than one that admits the gap — the same standard §3.2 applies to technical claims, applied to the portfolio's own coverage.

---

## 12. How we'll know it works

Skills with procedural outputs are testable, so we should test them rather than trust them.

**Cold-start test.** Point the spine at a genuinely unfamiliar open-source repo of meaningful size, in a stack we didn't design for. Compare the resulting `02-system-map.md` against reality. Success is not "it produced a document" — it is "someone who knows that codebase reads it and doesn't find a material error."

**Comparative runs.** Per the skill-creator workflow: run realistic prompts with and without each skill, and check whether the skill actually changed the outcome. A skill that produces the same result as baseline is overhead, and should be deleted rather than defended.

**Stack portability.** Each Wave 1–2 skill runs against at least three unrelated stacks. Any skill that only works on one has leaked stack assumptions into its body and needs them pushed down into `references/`.

**The trust test.** For comprehension artifacts, the real metric is whether every claim carries a citation or a confidence tag. Ungrounded confident prose is the specific failure this portfolio exists to prevent.

---

## 13. Open questions

These change the build; worth settling before Wave 1.

1. **Workspace location** — can artifacts live in the target repo as `.fde/`, or must they sit outside the checkout? Some organizations will reject a new top-level directory on sight. This affects every skill's output path.
2. **Artifact format** — markdown in the repo is the default. Do these also need to land in Confluence/SharePoint, i.e. should templates be paste-friendly rather than repo-native?
3. **Tooling floor** — is it truly filesystem + git + shell, or can we assume a GitHub/GitLab CLI and a ticketing integration are usually present? Affects `ownership-map`, `git-archaeology`, and `release-readiness` most.
4. **Network** — assume offline by default, or assume internal network with an internal package registry reachable?
5. **Distribution** — personal `~/.claude/skills/`, or packaged as a plugin so it can be handed to a team? Changes directory layout and whether we build a marketplace manifest.
6. **Naming prefix** — should skills be namespaced (`fde-recon`, `fde-safe-change`) to avoid colliding with client-repo skills? I lean yes for everything except `fde-orient`, but it makes every invocation wordier.

---

## Appendix — catalog at a glance

Forty-three skills. Entries marked **†** were added by the §5.11 gap analysis.

| # | Skill | Phase | Wave | Pack |
|---|---|---|---|---|
| 1 | `fde-orient` | Entry | 1 | core |
| 2 | **†** `access-and-onboarding` | Land | 1 | core |
| 3 | **†** `context-strategy` | Land | 1 | core |
| 4 | `env-bootstrap` | Land | 2 | core |
| 5 | `repo-recon` | Land | 1 | core |
| 6 | `ownership-map` | Land | 3 | core |
| 7 | **†** `knowledge-interview` | Land | 2 | core |
| 8 | `requirements-to-spec` | Frame | 1 | core |
| 9 | `feasibility-probe` | Frame | 1 | core |
| 10 | `delivery-plan` | Frame | 3 | core |
| 11 | **†** `estimation` | Frame | 3 | core |
| 12 | `trace-the-flow` | Understand | 2 | core |
| 13 | `data-archaeology` | Understand | 4 | data |
| 14 | `git-archaeology` | Understand | 4 | core |
| 15 | `blast-radius` | Understand | 2 | core |
| 16 | `solution-design` | Design | 3 | core |
| 17 | `contract-design` | Design | 4 | platform |
| 18 | `nfr-baseline` | Design | 3 | core |
| 19 | `characterization-tests` | Build | 2 | core |
| 20 | `safe-change` | Build | 1 | core |
| 21 | `refactor-seams` | Build | 4 | migration |
| 22 | `integration-adapter` | Build | 4 | platform |
| 23 | **†** `dependency-upgrade` | Build | 4 | migration |
| 24 | **†** `db-change-management` | Build | 4 | data |
| 25 | **†** `data-pipeline-work` | Build | 4 | data |
| 26 | **†** `cots-configuration` | Build | 4 | platform |
| 27 | `verification-plan` | Verify | 2 | core |
| 28 | **†** `test-data-strategy` | Verify | 2 | data |
| 29 | `ci-forensics` | Verify | 4 | operate |
| 30 | `nfr-validation` | Verify | 4 | core |
| 31 | `security-compliance-check` | Verify | 4 | core |
| 32 | `release-readiness` | Ship | 1 | core |
| 33 | `deploy-runbook` | Ship | 2 | core |
| 34 | `cutover-plan` | Ship | 4 | migration |
| 35 | `post-deploy-watch` | Ship | 4 | operate |
| 36 | **†** `change-control-navigation` | Ship | 3 | core |
| 37 | **†** `decommission-plan` | Ship | 4 | migration |
| 38 | `incident-triage` | Sustain | 3 | operate |
| 39 | `observability-gap` | Sustain | 4 | operate |
| 40 | `handover-pack` | Sustain | 3 | core |
| 41 | **†** `enablement-handoff` | Sustain | 3 | core |
| 42 | `stakeholder-brief` | Cross-cutting | 3 | core |
| 43 | **†** `escalation-and-renegotiation` | Cross-cutting | 3 | core |
