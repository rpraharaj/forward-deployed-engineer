---
name: incident-triage
description: Work backward from a production symptom to its cause under time pressure - stack trace to source, correlation IDs across services, log and metric narrowing, recent-change correlation - while prioritizing mitigation over root cause and saying explicitly which one you are doing. Use when production is broken, an alert has fired, customers are reporting errors, a batch job failed, or someone says "something is wrong in prod". Also use at the start of a rescue engagement, where the first task is usually to stop the bleeding.
---

# Incident triage

Finding the cause fast, in a system you don't know.

## Why this exists

An FDE gets pulled into incidents on systems they've known for days. That's genuinely harder than it is for the permanent team — you don't know what normal looks like, where the logs are, or which of the four services named `payments-*` is involved.

But you have two real advantages, and they're worth naming. You have **no assumptions** about where the problem is, which is exactly the bias that keeps experienced engineers looking in the wrong place for an hour. And you're comfortable saying "I don't know this system, walk me through it" — which under pressure, when everyone else is performing competence, is often what unblocks the room.

The main discipline: **mitigation and diagnosis are different jobs.** Doing them in the wrong order, or blurring them, extends outages. Stop the bleeding first, understand it after, and be explicit about which you're doing at any moment.

## When this applies

- Production is broken, degraded, or alerting
- Customers are reporting errors
- A batch job failed or produced wrong output
- The start of a rescue engagement — usually the first task

## When it doesn't

- A bug found in development — that's ordinary debugging, no urgency framing needed
- A performance concern that is not an active incident — measure it with `nfr-validation` if NFRs exist, otherwise ordinary debugging. Do not page this skill for "it has been getting slower."
- Post-incident improvement work — that's `observability-gap` *(fde-operate)*

## Prerequisites

Resolve `<workspace>` before reading or writing artifacts: read `../_shared/workspace-conventions.md` and follow its location and header rules. All artifact paths below use that resolved workspace. Preserve existing sections when appending.

None — incidents don't wait for artifacts. Use the workspace resolver only to locate existing records; if none exists, do not run `fde-orient` or delay mitigation to choose a directory. Keep minimal redacted notes in the response, then persist them in a chosen workspace once impact is stable. Where they exist, `02-system-map.md` and any traces are valuable. Where they don't, this skill degrades to careful work with a stranger's system, which is the normal FDE condition anyway.

## Procedure

### 1. Establish impact before cause

The first question is never "why." It's **what is broken, for whom, since when, and is it getting worse.**

- What's the observable symptom?
- Which users, how many, which regions or tenants?
- When did it start? Be precise — this is the single most useful fact you'll get.
- Is it ongoing, intermittent, or resolved?
- Is it worsening?

Impact determines urgency, and urgency determines whether you're mitigating or diagnosing. Establish it before touching anything.

### 2. Ask what changed

Most incidents are caused by a change. Before any deep investigation, check the cheapest hypothesis:

```bash
git log --oneline --since="48 hours ago"
git log --oneline --merges --since="7 days ago" | head -20
```

Git is the cheapest check, not the only one. Also look, in this order, and write down what you could not reach:

- CI/CD deploy history for the same window (the pipeline that promotes to prod)
- Feature-flag and config change audit, if a console exists
- Certificate `Not After` on anything this path calls
- Scheduled jobs whose run time matches the start
- Upstream / vendor status pages the team already uses

A nightly job is a change that happens every night, and "it started at 02:00" is a strong signal.

Correlating the start time against a deploy or a schedule solves a large fraction of incidents in the first five minutes.

### 3. Decide: mitigate or diagnose — and say which

The explicit decision that most improves outcomes.

**Mitigate first when** customers are actively affected, a rollback or flag is available, or the impact is growing. Rolling back without understanding is correct under those conditions, and the instinct to understand first is the wrong one.

**Diagnose first when** mitigation would destroy the evidence, the system is already stable, or you don't yet know which change to reverse.

Say aloud which you're doing. Incidents go badly when half the responders think they're diagnosing and half think they're fixing, and nobody notices the mismatch.

### 4. Narrow systematically, not by intuition

You don't know this system well enough for intuition, so use the structure instead. Halve the search space with each step:

- **Which component?** Follow the error to a service boundary. If A calls B calls C, find where the error first appears rather than where it surfaces.
- **Which instance?** All of them or one? One instance means environment, resource, or state — not code.
- **Which requests?** All, or a subset by tenant, region, user type, or payload shape? A subset is a strong clue, and worth characterizing precisely.
- **Which layer?** Application, database, network, infrastructure, or a dependency?

At each step write down what you ruled out. Under pressure people re-check the same thing twice and skip something entirely.

### 5. Read the evidence in the right order

Cheapest and most informative first:

1. **The alert itself** — what fired, what threshold, what it monitors
2. **Error rate and latency graphs** — shape and start time; a step change and a ramp mean different things
3. **The actual stack trace** — read it fully, including causes and suppressed exceptions
4. **Correlation IDs** — trace one failing request across services. If they exist, this is the highest-value tool available.
5. **Recent logs around the start time**, not just now — the first errors are more informative than the thousandth, which are usually cascade
6. **Resource metrics** — CPU, memory, connections, thread pools, disk
7. **Dependency health** — is this even your problem?

**Read the first error, not the loudest.** By the time you're looking, the logs are dominated by downstream cascade. The first occurrence at the start time is the one that matters.

### 6. Form a hypothesis you can falsify

State it explicitly: *"I think the connection pool is exhausted because the new query holds connections longer."*

Then find the check that would prove it **wrong**. This is the discipline that stops the classic incident failure — becoming attached to a plausible theory and interpreting everything as supporting it.

If you can't think of a falsifying check, the hypothesis is too vague to act on.

### 7. Mitigate with the least risky option available

In order of preference: disable a feature flag, roll back the deploy, scale up, restart, fail over, apply a targeted config change. Code changes under incident pressure are last — they're unreviewed, untested, and being written by someone tired.

**Confirm the mitigation worked.** Watch the metric that defined the impact return to normal. "We rolled back" is not resolution; the graph coming down is.

### 8. Write it down while it's fresh

Incident notes decay within hours. Capture the timeline, evidence, and what you did — during, if someone else is driving; immediately after if not.

Two things belong in it that people leave out: **what you ruled out**, which saves the next responder repeating it; and **what made this hard to diagnose**, which is the direct input to `observability-gap` *(fde-operate)*. If it took forty minutes to find because a log line was missing, that's a fixable defect and it will recur.

**Stop diagnosing** once impact is stable and the notes exist. Further root-cause work is post-incident, not this skill.

## Output template

Write to `<workspace>/incidents/<date>-<slug>.md`:

```markdown
# Incident — <short description>

**Date:** <YYYY-MM-DD> · **Detected:** <time> · **Mitigated:** <time> · **Duration:** <n>
**Severity:** <org's scale> · **Author:** FDE
**Status:** mitigated | resolved | ongoing
**Engagement:** <name>
**Source revision:** <repo>@<short SHA>, or "no repository yet"
**Confidence:** <what is confirmed, inferred, or unverified>

## Impact
**Symptom:** <observable> · **Affected:** <who, how many> · **Started:** <time, and how established>

## Timeline
| Time | Event |
|---|---|
| 02:14 | `refund_errors` alert fires |
| 02:22 | FDE engaged |
| 02:31 | Correlated start with nightly job at 02:00 |
| 02:38 | Hypothesis: connection pool exhaustion |
| 02:44 | Confirmed — pool at max, held by the recon query |
| 02:51 | Mitigated: recon job disabled |
| 03:05 | Error rate at baseline |

## Cause
<What actually happened, with citations. If not established, say so — "mitigated, cause not yet identified" is honest and common.>

## Mitigation
<What was done, and how it was confirmed.>

## Ruled out
<What was checked and eliminated. Saves the next responder the same hour.>

## What made this hard
<Missing logs, absent alerts, misleading dashboards, unclear ownership. → `observability-gap` (fde-operate), or a tracked instrumentation follow-up if that pack is unavailable.>

## Follow-ups
| # | Action | Why | Owner |
|---|---|---|---|
```

## Common traps

**Diagnosing while customers are affected.** Mitigate first, understand after.

**Not saying which mode you're in.** Half the room fixing, half investigating, nobody aware.

**Reading the loudest error.** It's cascade. Find the first one at the start time.

**Not establishing the start time precisely.** The most useful single fact, and it's usually obtainable in a minute.

**Skipping "what changed."** Most incidents are a change, and correlation is nearly free.

**Falling in love with a hypothesis.** Always ask what would prove it wrong.

**Fixing forward under pressure.** Unreviewed code written by a tired person at 3am. Roll back.

**Not confirming the mitigation.** "We rolled back" isn't resolution; the graph returning to baseline is.

**Not recording what you ruled out.** The next responder repeats your hour.

**Pretending to know the system.** "I don't know this — walk me through it" is faster than performing competence, and under pressure it's often what unblocks the room.
