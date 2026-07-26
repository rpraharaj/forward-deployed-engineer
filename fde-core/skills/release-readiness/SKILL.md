---
name: release-readiness
description: Assemble an evidence-based go/no-go position for a release - gather what prior artifacts already established, assess each readiness dimension as green, amber or red, state the recommendation together with the residual unknowns, and format it to survive a change advisory board. Use when approaching go-live, when a change needs CAB or stage-gate approval, when someone asks "are we ready to ship?", when a release decision is being made on opinion rather than evidence, or when you need to say no to a date and want the reasoning to hold up. Never launders uncertainty - an unverified item stays visible in the recommendation.
---

# Release readiness

Turning accumulated evidence into a defensible go/no-go.

## Why this exists

Release decisions in large organizations are usually made on vibes and seniority. Someone asks whether we're ready, the people closest to the work say they think so, and the residual uncertainty — which is real, and which someone privately knows about — never makes it into the room.

Then it fails, and the post-incident review discovers that three people each knew one piece of it.

This skill exists to make the uncertainty explicit at the moment the decision is made. Its distinguishing property is that **it refuses to launder uncertainty**. A recommendation of "go" with three unverified items says so, in the recommendation, where the approver reads it. That's what makes it worth anything: an assessment that always says yes carries no information.

It also happens to be the fastest way for an FDE to build trust. An engineer who says "no, and here's exactly what's missing" once is believed when they say yes.

## When this applies

- Approaching go-live on anything non-trivial
- A CAB, stage gate, or formal approval is required
- "Are we ready to ship?"
- You think the answer is no and need the reasoning to survive scrutiny
- A release decision is being made and nobody has assembled the evidence

## When it doesn't

- Routine low-risk deploys in a mature pipeline — don't add ceremony to a well-managed process
- Emergency mitigation during an incident, where the calculus is different and explicit
- You have no evidence to assemble. Then the honest output is "we can't assess this yet, and here's what's needed" — which is itself a legitimate and useful finding.

## Prerequisites

This skill **gathers**; it doesn't re-derive. It reads:

| Artifact | Provides |
|---|---|
| `03-requirements.md` | The acceptance criteria being claimed |
| `07-verification.md` | Which criteria have evidence, and the gap list |
| `06-blast-radius-*.md` | Who and what is exposed |
| `03b-nfrs.md` | Performance, security, compliance obligations |
| `06b-change-log.md` | What actually shipped, flags, rollback notes |
| `runbooks/deploy-*.md` | The deploy and rollback procedure |

Where an artifact is missing, that's a finding, not a blocker. Record the dimension as **red — no evidence** rather than assuming it's fine. Absence of evidence assessed as green is exactly the failure this skill prevents.

## Procedure

### 1. Gather, don't re-derive

Read the artifacts above. Pull the facts and their citations forward. If `07-verification.md` says AC-3 was verified manually in staging on the 14th, that sentence and its citation move into this document unchanged.

Resist re-testing here. This is an assembly and assessment step, and re-doing verification work at go/no-go time means it wasn't done properly earlier — worth noting as a process observation, separately.

### 2. Assess each dimension

Nine dimensions. Rate each **green / amber / red**, and cite.

| # | Dimension | Green means |
|---|---|---|
| 1 | **Functional verification** | Every acceptance criterion has evidence |
| 2 | **Regression** | Existing suite green; blast-radius callers specifically checked |
| 3 | **Non-functional** | NFRs from `03b-nfrs.md` measured, not assumed |
| 4 | **Security & compliance** | Data handling reviewed; required sign-offs held |
| 5 | **Blast radius mitigated** | Affected consumers notified or protected; contracts versioned |
| 6 | **Rollback** | Procedure written **and rehearsed**; one-way doors identified |
| 7 | **Observability** | You'd know within minutes if this broke; alerts exist |
| 8 | **Approvals** | Every required sign-off obtained, not merely requested |
| 9 | **Dependencies** | Everything this needs is itself ready and deployed |

The ratings that matter:

- **Amber** — a known gap with a stated mitigation. Amber is a normal, honest state. Most real releases go amber on something.
- **Red** — no evidence, or a gap with no mitigation. **Red on rollback (6) or on a one-way door should stop the release**, regardless of how green everything else is. That's the one asymmetry worth being rigid about: everything else can be fixed forward.

Two dimensions are routinely skipped and shouldn't be.

**Rollback rehearsed, not written.** A rollback procedure nobody has executed is a hypothesis. The question is not "do we have a rollback plan" but "has anyone run it, and how long did it take?" In enterprise environments the answer is often "no, and we discovered during the incident that the migration wasn't reversible."

**Observability.** If this change breaks in a way the existing dashboards wouldn't show, you will find out from a customer. Ask concretely: what metric moves, what alert fires, who receives it. See `observability-gap`.

### 3. Enumerate the residual unknowns

Every remaining `[unverified]` item and every amber, in one table, with:

- What is unknown
- What could go wrong if the pessimistic case holds
- Why it wasn't resolved — usually access, time, or environment
- The mitigation if it does go wrong
- Whether it's detectable — an unknown you'd notice immediately is far less dangerous than a silent one

**This table is the document.** Everything else supports it. An approver who reads only this section has what they need.

### 4. Make a recommendation

State one, plainly. "Here's the data, you decide" is an abdication — you're the person who did the work and you have a view. Give it.

Four forms, all legitimate:

- **Go** — evidence supports it; residual risk is understood and acceptable
- **Go with conditions** — proceed provided X happens first, or Y is monitored. Name the conditions specifically.
- **No-go** — a specific gap must close first. Name it, and what closing it takes.
- **Cannot assess** — insufficient evidence to have a view. Say what's needed. This is honest and occasionally the most useful answer available.

Attach the recommendation **to** the unknowns rather than after them: *"Recommend go, conditional on the staging rollback rehearsal completing. Three unverified items remain, all detectable within the first hour of monitoring."*

Never soften a red to keep a date. If the decision-maker overrides you, that's legitimate — it's their call and they may have context you don't. Record that it was overridden, by whom, on what date. Not defensively, but because it's the fact that matters most in the post-incident review, and because a decision made knowingly is a different thing from one made in ignorance.

### 5. Format for the actual reader

A CAB and an engineering lead need different documents from the same facts. See `../_shared/comms-register.md`.

Change boards read many submissions and look for reasons to defer. They want: what's changing in one plain sentence, who's affected and how many, verification evidence, rollback and whether it's been rehearsed, and residual risk stated plainly.

That last point is counter-intuitive but consistent: **naming your own residual risk gets changes approved more often than claiming there is none.** A submission with no acknowledged risk reads as one where nobody looked.

## Output template

Write to `.fde/08-release-readiness.md`:

```markdown
# Release readiness — <change>

**Engagement:** <name>
**Author:** FDE
**Date:** <YYYY-MM-DD>
**Status:** draft | submitted | approved | overridden
**Source revision:** <repo>@<short SHA>
**Release window:** <date/time, and any freeze that applies>

## Recommendation
**<GO | GO WITH CONDITIONS | NO-GO | CANNOT ASSESS>**

<Two or three sentences. Lead with the recommendation, then the reasoning, then the residual risk. Assume the reader stops here.>

**Conditions:** <if any, specifically>

## What is changing
<One sentence a non-specialist understands.>

## Who is affected
| Population | How many | Impact if this goes wrong |
|---|---|---|

## Readiness

| # | Dimension | Rating | Evidence |
|---|---|---|---|
| 1 | Functional verification | 🟢 | 7/7 ACs verified — `07-verification.md` |
| 2 | Regression | 🟢 | Full suite green @ `a3f9c1`; 4 blast-radius callers checked |
| 3 | Non-functional | 🟡 | p95 measured in staging at 0.9s vs 1.0s target; not load-tested at prod volume |
| 4 | Security & compliance | 🟢 | No new PII surface `[confirmed]`; sign-off J. Okafor 03-18 |
| 5 | Blast radius mitigated | 🟡 | 3 of 4 consumers confirmed; team D not responded since 03-12 |
| 6 | Rollback | 🟢 | Rehearsed in staging 03-19, 4 min; migration additive |
| 7 | Observability | 🟢 | `refund_currency_errors` alerting to #payments-oncall |
| 8 | Approvals | 🔴 | CAB submitted, not yet scheduled |
| 9 | Dependencies | 🟢 | None outstanding |

## Residual unknowns
| # | Unknown | Worst case | Why unresolved | Mitigation | Detectable? |
|---|---|---|---|---|---|
| 1 | Behavior at prod volume | Latency regression on the refund path | No prod-scale load environment | Flag off; staged rollout at 5% | Yes — p95 dashboard, minutes |
| 2 | Team D consumer compatibility | Their parser rejects the new field | No response since 03-12 | Field is additive and optional `[inferred]` | Partly — their error rate |

## Rollback
**Procedure:** `runbooks/deploy-refund-currency.md`
**Rehearsed:** yes — staging, 03-19, 4 minutes
**One-way doors:** none identified
**Trigger conditions:** <what specifically causes a rollback decision, and who makes it>

## Post-deploy watch
<What to watch, for how long, who is watching. See `post-deploy-watch`.>

## Decision log
| Date | Decision | By | Notes |
|---|---|---|---|
```

## Common traps

**Rating a dimension green because nobody raised a concern.** Absence of evidence is red, not green. This is the specific failure the skill exists to prevent.

**Averaging into an overall percentage.** "85% ready" is meaningless and hides which 15%. Dimensions stay separate.

**Softening a red to protect a date.** You get exactly one reputation for this, and losing it costs more than the date.

**Burying the recommendation.** Approvers read the first paragraph. Put it there.

**Claiming no residual risk.** Reads as not having looked, and gets deferred more often than an honest amber.

**Treating a written rollback as a tested one.** The question is whether anyone has run it, and how long it took.

**Skipping observability.** A change you can't detect failing is a change you'll hear about from a customer.

**Re-verifying here.** If verification is happening at go/no-go, it happened too late. Assemble what exists; note the process gap separately.
