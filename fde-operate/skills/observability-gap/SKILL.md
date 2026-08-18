---
name: observability-gap
description: Ask whether a failure could have been seen, then close the gaps - missing logs, metrics, traces, and alerts - so the next incident is cheaper to diagnose. Use after any incident where the answer was hard to find, before shipping anything whose failure would be silent, when a change has no way to be detected going wrong, or when diagnosis required guessing. The compounding skill: each pass makes every future incident shorter, and silent failures are the ones worth spending on.
---

# Observability gap

Making the next incident cheaper than this one.

## Why this exists

After an incident everyone discusses the cause. Almost nobody discusses **why it took forty minutes to find** — and that second question is usually the more valuable one, because the cause was specific to this incident while the diagnosis difficulty will recur across every future one.

If the answer was hard to find, that is a fixable defect. A missing log line, an absent metric, a dashboard that shows the symptom but not the cause, an alert that fires on the wrong thing. Each one costs time in every incident that touches that area, forever, and each is usually a small change.

This is the compounding skill in the portfolio. It's also the one most easily deferred, because the incident is over and the pressure is gone. That's precisely why it needs to be a deliberate step rather than an intention.

The other half is prospective: before shipping, asking whether this change's failure would be **silent**. A failure nobody detects is far more dangerous than one that pages someone at 3am.

## When this applies

- After any incident where diagnosis was hard
- Before shipping anything whose failure would be silent
- A change has no way to be detected going wrong
- Diagnosis required guessing rather than looking
- `nfr-baseline` flagged a silent-failure risk

## When it doesn't

- During an active incident — fix it first, come back after
- The system is already well instrumented in the relevant area
- Adding telemetry nobody will look at, which is cost without benefit

## Prerequisites

- Locate the workspace: `FDE_WORKSPACE`, else the charter Location, else `.fde/`, else `../<repo>-fde/`
- `.fde/incidents/*.md` — specifically the "what made this hard" section
- `.fde/03b-nfrs.md` — the silent-failure analysis
- `.fde/08-release-readiness.md` — the observability dimension

## Procedure

### 1. Start from a real diagnosis, not from a checklist

The best input is a specific incident and the specific moments where you were stuck. `incident-triage` records these under "what made this hard" for exactly this reason.

Reconstruct the diagnosis and mark each point where you had to guess, wait, or ask someone. Each is a gap with a known cost — you just paid it.

Working from a real incident produces a much better result than working from a generic observability checklist, because it targets what actually failed rather than what might.

### 2. Ask the four questions

For the area in question:

1. **Would we know it broke?** Is there an alert, or does it depend on someone noticing?
2. **Would we know *what* broke?** Or only that something did?
3. **Could we tell which requests, users, or tenants?** Aggregate-only metrics can't answer this, and it's usually the first question asked.
4. **Could we follow one request end to end?** Correlation IDs across services, or reconstruction from timestamps?

Question 1 is the one that matters most. A failure detected only when a customer complains has an unbounded detection time, and detection time dominates total incident duration far more often than diagnosis does.

### 3. Attend to the silent failures specifically

The highest-value target. Some failures are loud — errors, timeouts, crashes — and are usually already covered. The dangerous ones produce no error at all:

- Wrong data written, correctly
- A job that didn't run, and nothing noticed it was absent
- A message consumed and silently dropped
- A gradual degradation with no threshold crossed
- A partial failure where most things still work
- A config change that quietly disabled something

For each, the fix is usually an **assertion about what should be true** rather than a detector for what went wrong: this job should complete daily by 06:00; this count should match that count; this queue should not exceed this depth; this rate should stay within this band.

Absence detection — alerting on something that *didn't* happen — is the most commonly missing kind of monitoring and the most valuable to add. Nothing failing is indistinguishable from nothing running.

### 4. Prefer fewer, better signals

More telemetry is not better. An alert nobody acts on trains people to ignore alerts, and a dashboard with sixty panels hides the four that matter.

Add:

- **A metric** when you'd want to see a trend or set a threshold
- **A log line** when you'd want to know what happened in one specific case. Structured, with the identifiers you'd search by — a message with no correlation ID is nearly useless in a distributed system.
- **A trace** when the question spans services
- **An alert** only when there is a defined action. An alert with no runbook and no response is noise with a pager attached.

For each alert, answer: who receives it, what do they do, and what happens if they do nothing? If the honest answer to the last is "nothing," it should be a dashboard, not an alert.

### 5. Check the ones that already exist

Existing monitoring is often subtly wrong, and nobody has checked since it was written:

- Alerts that can't fire because the threshold is unreachable
- Alerts that fire constantly and are routed to a muted channel
- Dashboards showing a metric that stopped being emitted after a refactor
- Alerts routed to a team that no longer exists, or a person who left
- Log-based alerts broken by a change to a log format

That last one is a real risk from ordinary work — renaming a log field silently breaks any alert parsing it, with no error anywhere. `blast-radius` ring 6 covers this prospectively; this is the retrospective check.

Confirm the important alerts can actually fire. The only reliable way is to make one fire deliberately in a lower environment.

### 6. Make it a small, shipped change

The failure mode here is proposing an observability programme instead of adding four log lines and one alert.

Ship the small version now: the specific gaps from the specific incident. It's reviewable, it's cheap, and it makes the next incident measurably shorter. Larger platform gaps — no tracing at all, no log aggregation — belong in the handover as findings, not as a blocker to this change.

## Output

A PR plus a note appended to the incident record, or `.fde/07c-observability.md`:

```markdown
# Observability gaps — <area>

**Engagement:** <name> · **Author:** FDE · **Date:** <YYYY-MM-DD>
**Source:** incident `2026-03-14-payment-timeouts` — 37 min to diagnose

## Where diagnosis stalled
| # | Stuck on | Cost | Gap |
|---|---|---|---|
| 1 | Which downstream was slow | ~15 min | No per-dependency latency metric |
| 2 | Whether the recon job had run | ~10 min | No completion metric — had to read logs on the host |
| 3 | Which tenants were affected | ~8 min | Errors aggregated only, no tenant dimension |

## The four questions
| Question | Before | After |
|---|---|---|
| Would we know it broke? | Only via customer reports | ✅ alert on error rate |
| Would we know what broke? | No | ✅ per-dependency latency |
| Which requests/tenants? | No | ✅ tenant dimension added |
| Follow one request? | Partially — no ID across the queue | ⚠️ correlation ID propagated, tracing still absent |

## Silent failures found
| Failure | Currently detected? | Fix |
|---|---|---|
| Recon job doesn't run | **No** — silent until month-end | Absence alert: no completion by 06:00 → page |
| Refund written with wrong currency | **No** | Daily reconciliation count vs. source |

## Changes made
| # | Change | Type | Alerts to |
|---|---|---|---|
| 1 | `dependency_latency{dep}` histogram | metric | dashboard only |
| 2 | `recon_job_completed` + absence alert | metric + alert | #payments-oncall |
| 3 | `tenant_id` on error logs | log | — |

## Existing monitoring found broken
| What | Problem | Fixed |
|---|---|---|
| `payment_failures` alert | Routed to a team disbanded in 2024 | ✅ rerouted |
| `queue_depth` dashboard panel | Metric renamed in a 2025 refactor; empty since | ✅ |

## Platform gaps — not fixed here
<Larger findings for the handover: no distributed tracing, log retention only 7 days.>
```

## Common traps

**Skipping it because the incident is over.** The pressure is gone, which is exactly why it needs to be a deliberate step.

**Working from a generic checklist.** A real diagnosis targets what actually failed.

**Only instrumenting loud failures.** They're usually covered. Silent ones are the danger.

**Missing absence detection.** Nothing failing is indistinguishable from nothing running.

**Adding alerts with no defined action.** Noise with a pager attached, and it trains people to ignore the real ones.

**Not checking existing monitoring.** Alerts routed to disbanded teams and dashboards on dead metrics are extremely common.

**Not verifying an alert can fire.** Make one fire deliberately in a lower environment.

**Proposing a programme instead of shipping four log lines.** Ship the small version; record the platform gaps as findings.
