# Workspace conventions

How FDE skills store artifacts and read each other's output.

## Locating the workspace

The workspace path is recorded in the engagement charter and **read from there, never hardcoded**. Some organizations will not accept a new top-level directory in their repository, so the workspace may live outside the checkout.

**Step 0 of every skill after `fde-orient`:** resolve the path, then read and write only there.

Resolution order, first hit wins:

1. `FDE_WORKSPACE` environment variable, if set and the directory exists
2. The `## Workspace` → **Location** line in an existing charter (search `.fde/00-engagement.md` and `../*-fde/00-engagement.md`)
3. `.fde/` in the repository root
4. `../<repo-name>-fde/` adjacent to the checkout
5. Ask, and record the answer in `00-engagement.md`

If `FDE_WORKSPACE` is explicitly set but unavailable, report that path as the blocker; do not silently fall back to another directory. `fde-orient` may create the chosen location when opening an engagement. `<workspace>` in skill procedures and templates always means the resolved path, not a directory literally named `<workspace>`.

If none exists, the engagement hasn't been opened — run `fde-orient` first rather than scattering artifacts into the current directory.

When the workspace lives inside the repo, check whether `.fde/` should be added to `.gitignore`. Both answers are defensible — committed artifacts are inheritable and reviewable, ignored ones avoid an argument about repo hygiene with a team you just met. Ask once, in `fde-orient`, and record it.

Archetype-pack skills (`fde-data`, `fde-migration`, `fde-operate`, `fde-platform`, `fde-product`, `fde-ai`) use this same order even when this file is not on disk. Do not invent a second `.fde/` when the charter already recorded a different location.

## Layout

```
.fde/
├── 00-engagement.md              # charter: archetype, stakeholders, goal, constraints, workspace decisions
├── 00b-access.md                 # access register and critical path
├── 00c-context.md                # scale, working set, what was delegated
├── 01-environment.md             # how to build, test, run — including the workarounds
├── 02-system-map.md              # cartography
├── 02b-ownership.md              # who owns what, who decides
├── 03-requirements.md            # testable spec with acceptance criteria
├── 03b-nfrs.md                   # measurable non-functionals
├── 03c-test-data.md              # permitted data, generator, what it does not represent
├── 04-feasibility.md             # requirements grounded in real code
├── 05-delivery-plan.md           # risk-ordered sequence
├── 05b-estimate.md               # ranges, assumptions, effort vs elapsed
├── 05c-upgrade-matrix.md         # EOL / major-version compatibility (fde-migration)
├── 05d-cots-assessment.md        # vendor-platform tiers and upgrade risk (fde-platform)
├── 06-blast-radius-<change>.md
├── 06b-change-log.md
├── 07-verification.md            # criteria → evidence, and the gap list
├── 07b-ci-notes.md               # pipeline failure class and verification impact (fde-operate)
├── 07c-observability.md          # gaps closed after an incident (fde-operate)
├── 08-release-readiness.md       # go/no-go
├── 08b-change-control.md         # gates, freezes, backwards schedule
├── 09-handover.md
├── 09b-enablement.md             # capability checklist; not a second handover
├── discovery/   workflow-<name>.md, opportunities.md
├── outcomes/    <initiative>.md  # original business baseline plus dated readouts
├── adoption/    <initiative>.md  # end-user pilot, support, fallback, observed use
├── product-feedback/ <topic>.md  # permitted field evidence (fde-product)
├── ai/          evaluation-<workflow>.md, action-safety-<workflow>.md (fde-ai)
├── adr/         NNNN-<slug>.md
├── traces/      <flow>.md, data-model.md, why-<symbol>.md, <external-system>.md
├── runbooks/    deploy-<svc>.md, cutover-<name>.md, decommission-<system>.md
├── incidents/   <date>-<slug>.md
├── interviews/  <date>-<person>.md
└── briefs/      <date>-<topic>.md
```

Numbering gives whoever inherits the workspace a reading order. It is not a workflow gate — engagements skip and loop, and a workspace with gaps is normal and honest.

## Artifact header

Every artifact opens with this block. It takes fifteen seconds and it is what makes the artifact safe to trust later.

```markdown
# <Artifact title>

**Engagement:** <name>
**Author:** FDE
**Date:** <YYYY-MM-DD>
**Status:** draft | reviewed | superseded
**Source revision:** <repo>@<short SHA>
**Confidence:** <one line — what here is solid, what isn't>
```

**Source revision matters more than it looks.** An artifact full of precise `path:line` citations against an unrecorded revision is actively misleading once the code moves: the reader trusts the precision and the lines have shifted. The SHA is what lets them tell.

**Status** is not decoration. `superseded` at the top of a stale document, with a pointer to what replaced it, prevents the most common workspace failure — a later reader acting on an earlier conclusion.

Standalone templates include this header; skill-specific states such as `live`, `rehearsed`, or `approved` may refine Status. For work with no source repository, write "no repository yet" in Source revision. Appended sections inherit the enclosing header and add their own date and revision where evidence changes. Create a missing destination with the standard header before appending. On a rerun, update the relevant section and preserve other skills' evidence; do not overwrite an NFR or security appendix while regenerating the enclosing assessment.

## Composition

Skills read upstream artifacts rather than re-deriving context. This is the whole reason the workspace exists: `feasibility-probe` should not have to re-map the system that `repo-recon` already mapped.

Declared dependencies (each skill's Prerequisites section is authoritative if they disagree):

| Skill | Reads |
|---|---|
| `access-and-onboarding` | `00-engagement.md` |
| `context-strategy` | `00-engagement.md` *(optional)* |
| `env-bootstrap` | `00-engagement.md`, `00b-access.md` |
| `repo-recon` | `00-engagement.md`, `00c-context.md` / `01-environment.md` *(optional)* |
| `ownership-map` | `00-engagement.md`, `02-system-map.md` *(optional)* |
| `knowledge-interview` | unverified gaps in existing artifacts, `02b-ownership.md` |
| `requirements-to-spec` | `00-engagement.md` |
| `nfr-baseline` | `03-requirements.md`, `02-system-map.md` |
| `feasibility-probe` | `02-system-map.md`, `03-requirements.md` |
| `estimation` | `04-feasibility.md`, `06-blast-radius-*.md`, `00b-access.md`, `02b-ownership.md` |
| `delivery-plan` | `04-feasibility.md`, `05b-estimate.md`, `06-blast-radius-*.md`, `00b-access.md`, `08b-change-control.md` |
| `blast-radius` | `02-system-map.md`, `04-feasibility.md` |
| `solution-design` | `03-requirements.md`, `04-feasibility.md` |
| `safe-change` | `04-feasibility.md`, `06-blast-radius-*.md` |
| `verification-plan` | `03-requirements.md`, `03b-nfrs.md`, `06-blast-radius-*.md`, `06b-change-log.md` |
| `nfr-validation` | `03b-nfrs.md`, `07-verification.md` |
| `deploy-runbook` | `06-blast-radius-*.md`, `07-verification.md`, `01-environment.md`, `08b-change-control.md` |
| `release-readiness` | `03-requirements.md`, `07-verification.md`, `06-blast-radius-*.md`, `03b-nfrs.md`, `06b-change-log.md`, `runbooks/deploy-*.md` |
| `handover-pack` | the workspace as a whole |
| `enablement-handoff` | `02b-ownership.md`, runbooks, `01-environment.md` — not `09-handover.md` |
| `observability-gap` *(fde-operate)* | Incident notes for post-incident work; proposed change/draft NFRs for pre-release work. NFR and release assessments are optional inputs. |
| `workflow-discovery` | Charter if available; approved cases/participant observations. No system map is required to map human work. |
| `use-case-selection` | Candidate problems, decision authority, and available workflow/impact/readiness evidence; discovery artifacts are optional. |
| `outcome-measurement` | Chosen problem and owner, permitted aggregate evidence, metric definitions. Retains its original baseline across readouts. |
| `adoption-plan` | Intended users/process owner, change, known readiness limits, and available usage evidence; operator enablement is separate. |
| `field-to-product` *(fde-product)* | Permitted deployment evidence, product context, and audience/reuse restrictions; no customer material is implicitly shareable. |
| `ai-evaluation` *(fde-ai)* | Task criteria/owner, versioned cases and grader, isolated runnable system or explicit measurement blockers. |
| `agent-action-safety` *(fde-ai)* | Tasks/principals, tool permissions, control owners, and isolated execution evidence. |

### When an upstream artifact is missing

Say which one, and offer to run the skill that produces it. Do **not** silently reconstruct it inline — that produces an unrecorded, uncited version of an artifact that should have been durable, and the next skill will re-derive it again.

The exception is a deliberately narrow engagement. If the user is doing a one-hour spike, running the full chain is wrong. Note the missing input in the artifact's **Confidence** line and continue:

> **Confidence:** No blast-radius analysis was run — impact assessment here is `[inferred]` from the system map only.

That is an honest, useful artifact. A confident one that hides the gap is not.

## Naming

- Slugs are kebab-case: `06-blast-radius-payment-retry.md`
- ADRs are zero-padded and sequential: `adr/0004-event-schema-versioning.md`
- Traces are named for the business operation, not the code: `traces/customer-places-order.md`, not `traces/OrderController.md`
- Intent recovered from history: `traces/why-<symbol>.md`
- Incidents lead with the date: `incidents/2026-03-14-payment-timeouts.md`
- Briefs and interviews lead with the date: `briefs/2026-03-26-feasibility.md`, `interviews/2026-03-14-okafor.md`

Business-language names matter for traces specifically. The class name is what *you* found; the operation name is what the *stakeholder* will search for.

## What never goes in the workspace

The workspace is likely to be committed, shared, or left behind. It must be safe on all three counts.

- Secrets, credentials, tokens, connection strings — reference where they live, never the value
- Customer or employee personal data, including in example payloads and log excerpts (invent the values, and say you did)
- Internal hostnames and IPs where the organization treats them as sensitive — check, don't assume
- Anything a named individual said in confidence. `ownership-map` and `knowledge-interview` record facts and decision rights, not opinions about colleagues.

The last one is worth a moment. An FDE hears a lot of candid commentary about other teams. None of it belongs in a durable document that outlives the engagement.
