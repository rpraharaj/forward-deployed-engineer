# FDE Skills — How to use them

An operator's manual for the forward deployed engineer skill portfolio.

**Currently built:** 50 skills across seven packs — `fde-core` (34) plus six optional packs. The seven additions for discovery, outcomes, adoption, product feedback, and AI are experimental.
**Why it's shaped this way:** [DESIGN.md](DESIGN.md) · **What was tested:** [VALIDATION.md](VALIDATION.md)

---

## What this is

A set of Claude Code skills for an engineer who gets dropped into unfamiliar organizations and is expected to deliver — from a vague ask through to something running in production — on a stack they didn't choose, in a codebase nobody has documented, with Claude Code as their only tool.

The skills don't teach Claude to write Java or configure Kubernetes; it can already do that. They encode the **procedures** an experienced FDE follows and the **artifacts** those procedures produce, so the work is grounded, legible to the client team, and survives your departure.

---

## Install

Install `fde-core` always. Add the pack that matches the engagement archetype `fde-orient` identifies.

```bash
claude plugin marketplace add /path/to/FDE-Claude
claude plugin install fde-core@fde-skills
```

Install optional packs by name from the same marketplace, for example `claude plugin install fde-data@fde-skills`. For one development session, use `claude --plugin-dir /path/to/FDE-Claude/fde-core --plugin-dir /path/to/FDE-Claude/fde-data` instead. Loading a directory this way is session-only.

| Pack | Install when the engagement is | Skills |
|---|---|---|
| `fde-core` | **always** | 34 |
| `fde-data` | analytics, ETL, warehouse, reporting, schema change | 3 |
| `fde-migration` | replatform, EOL upgrade, cutover, decommission | 4 |
| `fde-platform` | integration, contract design, COTS (SAP/Salesforce/ServiceNow) | 3 |
| `fde-operate` | running what you shipped — pipelines, watch, observability | 3 |
| `fde-product` | vendor FDEs turning permitted field evidence into shared product improvements | 1 |
| `fde-ai` | delivered AI task evaluation and boundaries on agent tool actions | 2 |

The split is deliberate. Skill descriptions load into context every session whether they fire or not. Installing only what the engagement needs protects the budget `context-strategy` exists to defend.

Verify they loaded by asking Claude Code: *"what FDE skills do you have?"*

The skills are invoked by describing your situation in plain language — you don't need to name them. Say *"I've just been assigned to a payments system I've never seen"* and `fde-orient` fires.

---

## The mental model

Three ideas. Everything else follows from them.

**1. Artifacts, not conversations.** Every skill persists its findings in the resolved engagement workspace: `.fde/` by default, or the external location recorded in the charter / `FDE_WORKSPACE`. A finding that lives only in a chat transcript is gone next session, and gone entirely when you leave. The workspace *is* the engagement's memory. The `.fde/` paths in this walkthrough are examples of the default location.

**2. Evidence or a confidence tag.** Every claim carries a `file.java:88` citation, a command and its output, or one of three tags — `[confirmed]`, `[inferred]`, `[unverified]`. This is what makes you credible in week two rather than quietly routed around after being confidently wrong once.

**3. Skills compose.** Each reads the artifacts the previous ones wrote. `feasibility-probe` reads the system map and the spec rather than re-deriving them. Run them roughly in order and the work accumulates instead of repeating.

---

## Your first day

A concrete walkthrough. Roughly what the first two days look like on a typical brownfield engagement.

### 1. Open the engagement

> *"I've been assigned to the billing service at a client. They want me to add multi-currency refunds. I don't know anything about the system yet."*

Fires **`fde-orient`**. It reads the repo for what it can infer, asks you around six questions, classifies the engagement (here: *brownfield enhancement*), sets up `.fde/`, and writes the charter — including the distinction between what you were asked to do and what the sponsor actually needs.

**Produces:** `.fde/00-engagement.md`

### 2. Get access moving before anything else

> *"What access am I going to need, and what should I request first?"*

Fires **`access-and-onboarding`**. Enumerates every permission the engagement needs, finds the approver and lead time for each, and orders them by lead time so the slow ones are in flight on day one.

This runs first for a reason: access lead times are the one constraint you cannot compress later. A prod database grant needing two approvals should be requested now, not the week you need it.

**Produces:** `.fde/00b-access.md`

### 3. Set a context budget if the repo is large

> *"This monorepo has 30,000 files."*

Fires **`context-strategy`**. Sizes the problem and sets the approach — what to grep, what to script, what to read, what to delegate — before you start burning context on files that don't matter.

Skip on anything under ~5,000 files.

### 4. Map the system

> *"Help me understand this codebase."*

Fires **`repo-recon`**. A bounded breadth-first pass: entry points, module boundaries, what it stores, what it talks to, where churn concentrates, whether the tests run, and what you'd be scared to touch.

It stops when you can answer five questions without looking anything up. That stopping rule is deliberate — depth comes later, and only where the work lands.

**Produces:** `.fde/02-system-map.md` and a working `CLAUDE.md`

### 5. Write down what's actually being asked

> *"The ticket just says 'support multi-currency refunds'. That's all I've got."*

Fires **`requirements-to-spec`**. Separates the stated ask from the underlying need, writes acceptance criteria as observable behavior, forces the unhappy paths into the open, and records what's explicitly *out* of scope.

**Produces:** `.fde/03-requirements.md`

### 6. Ground it in the real code

> *"How hard is this actually?"*

Fires **`feasibility-probe`** — the skill that earns your keep. Per requirement: does this already exist, exactly which files change, what shape is the change, and what looks cheap but isn't.

This is where "we think it's two weeks" becomes *"three of these are straightforward, one is cross-cutting through eleven files, and one needs data we've never collected — that last one isn't an engineering problem."*

**Produces:** `.fde/04-feasibility.md`

### 7. Build it

> *"Let's implement R1."*

Fires **`safe-change`**. Green baseline first, read the neighbourhood for idiom, smallest viable diff, refactor separated from behavior, rollback drafted before merge, verified against the acceptance criteria rather than against "the tests pass."

**Produces:** the change, plus `.fde/06b-change-log.md`

### 8. Decide whether to ship

> *"Are we ready to go live?"*

Fires **`release-readiness`**. Assembles what the earlier artifacts already established into nine rated dimensions, states the residual unknowns, and gives a recommendation that doesn't hide them.

**Produces:** `.fde/08-release-readiness.md`

---

## Skill reference

### Wave 1 — the spine

| Skill | Fires when you say | Produces |
|---|---|---|
| **`fde-orient`** | "new client", "just been assigned", "dropped into", "where do I start" | `00-engagement.md` |
| **`access-and-onboarding`** | "can't get access", "waiting on permissions", "what do I need to request" | `00b-access.md` |
| **`context-strategy`** | "this repo is huge", "running out of context", "where do I even start reading" | `CLAUDE.md`, working set |
| **`repo-recon`** | "help me understand this repo", "what does this system do" | `02-system-map.md`, `CLAUDE.md` |
| **`requirements-to-spec`** | "they want us to add X", vague ticket, "nobody's defined done" | `03-requirements.md` |
| **`feasibility-probe`** | "how hard would it be", "can we do X by <date>", "this plan feels optimistic" | `04-feasibility.md` |
| **`safe-change`** | "let's implement", "make this change" — in code you don't own | the change, `06b-change-log.md` |
| **`release-readiness`** | "are we ready to ship", "CAB needs a submission", "go/no-go" | `08-release-readiness.md` |

### Wave 2 — depth where the risk is

| Skill | Fires when you say | Produces |
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

| Skill | Fires when you say | Produces |
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
| **`enablement-handoff`** | "the team has to run this without me" | enablement section |

Three skills load per-stack references on detection rather than hardcoding a language: `repo-recon` (entry points across nine stacks), `trace-the-flow` (following DI, reflection, event buses, generated code), and `characterization-tests` (test harnesses and approval-test tooling).

### Wave 5 — discovery, outcomes, adoption, and field learning

These seven procedures are experimental. Use them for the named situation; a clear small task does not need a new discovery or adoption workstream.

| Skill | Pack | Fires when you say | Produces under the resolved workspace |
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

Every artifact opens with engagement, date, status, **source revision**, and a confidence line. The source revision matters most: precise line citations against an unrecorded commit go stale silently, and a reader who trusts them will be misled.

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

Historical triggering results are 42/43 first choice on Claude before the description edits, then 43/43 on Grok, both for the earlier catalog. Those runs used the older permissive reply parser and did not establish valid runtime metadata. The repaired evaluator requires valid YAML and explicit answer syntax; the expanded 82-query suite covers all 50 skill descriptions. Consult the latest validation entry for actual execution results, not the historical badge. Four skills have documented repository-based procedure trials (`repo-recon`, `blast-radius`, `env-bootstrap`, `characterization-tests`), some only partially. Seven others have synthetic artifact trials; the remaining 39 have no recorded procedure trial. Shared-reference checks do not add to the skill count.

If you hit a skill whose procedure doesn't fit your situation, that's a finding worth recording — it's better evidence than anything in the design document.

Where a procedure does not fit, Claude Code handles the work without a skill — you just don't get the artifact template. Keep writing to the workspace with the same header and confidence conventions so the chain stays intact.

---

## Troubleshooting

**A skill doesn't fire when it should.** Describe the situation rather than the task — *"I've been dropped into a system I don't know"* triggers more reliably than *"analyze this repo."* You can also name it directly: *"use fde-orient."*

**Too many skills fire at once.** Usually means the request spans phases. Split it: map first, then spec, then probe.

**A skill wants artifacts you don't have.** Either run the upstream skill or tell it to proceed anyway — it'll record the reduced confidence.

**Artifacts feel like overhead on a short engagement.** Scale down deliberately: charter plus system map plus feasibility is a legitimate three-artifact engagement. What doesn't scale down is the evidence discipline, which costs nothing and is the whole point.

**The client won't allow a `.fde/` directory.** Set `FDE_WORKSPACE` or use `../<repo>-fde/`. Record the choice in the charter; skills read the location rather than hardcoding it.

---

## Adapting this

The portfolio is written to be edited. Two things to preserve if you change anything:

**The evidence discipline.** It's the convention every other part depends on, and the one that makes the difference between being trusted and being tolerated.

**Stack-agnosticism.** No SKILL.md body should name Maven, npm, or pytest. Stack specifics belong in `_shared/stack-detection.md` or a `references/` file loaded only when detected. If you find yourself writing a stack assumption into a skill body, push it down a level.

Everything else — templates, ordering, the artifact numbering — is yours to change to fit how your organization actually works.
