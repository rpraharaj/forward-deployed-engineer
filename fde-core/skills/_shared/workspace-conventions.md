# Workspace conventions

How FDE skills store artifacts and read each other's output.

## Locating the workspace

The workspace path is recorded in the engagement charter and **read from there, never hardcoded**. Some organizations will not accept a new top-level directory in their repository, so the workspace may live outside the checkout.

Resolution order, first hit wins:

1. `FDE_WORKSPACE` environment variable, if set
2. `.fde/` in the repository root
3. `../<repo-name>-fde/` adjacent to the checkout
4. Ask, and record the answer in `00-engagement.md`

Every skill after `fde-orient` begins by locating the workspace this way. If none exists, the engagement hasn't been opened — run `fde-orient` first rather than scattering artifacts into the current directory.

When the workspace lives inside the repo, check whether `.fde/` should be added to `.gitignore`. Both answers are defensible — committed artifacts are inheritable and reviewable, ignored ones avoid an argument about repo hygiene with a team you just met. Ask once, in `fde-orient`, and record it.

## Layout

```
.fde/
├── 00-engagement.md              # charter: archetype, stakeholders, goal, constraints, workspace decisions
├── 00b-access.md                 # access register and critical path
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
├── adr/       NNNN-<slug>.md
├── traces/    <flow>.md
├── runbooks/  deploy-<svc>.md, cutover-<name>.md
└── incidents/ <date>-<slug>.md
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

## Composition

Skills read upstream artifacts rather than re-deriving context. This is the whole reason the workspace exists: `feasibility-probe` should not have to re-map the system that `repo-recon` already mapped.

Declared dependencies:

| Skill | Reads |
|---|---|
| `access-and-onboarding` | `00-engagement.md` |
| `repo-recon` | `00-engagement.md`, `01-environment.md` *(optional)* |
| `requirements-to-spec` | `00-engagement.md` |
| `feasibility-probe` | `02-system-map.md`, `03-requirements.md` |
| `safe-change` | `04-feasibility.md`, `06-blast-radius-*.md` |
| `release-readiness` | `03-requirements.md`, `07-verification.md`, `06-blast-radius-*.md`, `03b-nfrs.md` |

### When an upstream artifact is missing

Say which one, and offer to run the skill that produces it. Do **not** silently reconstruct it inline — that produces an unrecorded, uncited version of an artifact that should have been durable, and the next skill will re-derive it again.

The exception is a deliberately narrow engagement. If the user is doing a one-hour spike, running the full chain is wrong. Note the missing input in the artifact's **Confidence** line and continue:

> **Confidence:** No blast-radius analysis was run — impact assessment here is `[inferred]` from the system map only.

That is an honest, useful artifact. A confident one that hides the gap is not.

## Naming

- Slugs are kebab-case: `06-blast-radius-payment-retry.md`
- ADRs are zero-padded and sequential: `adr/0004-event-schema-versioning.md`
- Traces are named for the business operation, not the code: `traces/customer-places-order.md`, not `traces/OrderController.md`
- Incidents lead with the date: `incidents/2026-03-14-payment-timeouts.md`

Business-language names matter for traces specifically. The class name is what *you* found; the operation name is what the *stakeholder* will search for.

## What never goes in the workspace

The workspace is likely to be committed, shared, or left behind. It must be safe on all three counts.

- Secrets, credentials, tokens, connection strings — reference where they live, never the value
- Customer or employee personal data, including in example payloads and log excerpts (invent the values, and say you did)
- Internal hostnames and IPs where the organization treats them as sensitive — check, don't assume
- Anything a named individual said in confidence. `ownership-map` and `knowledge-interview` record facts and decision rights, not opinions about colleagues.

The last one is worth a moment. An FDE hears a lot of candid commentary about other teams. None of it belongs in a durable document that outlives the engagement.
