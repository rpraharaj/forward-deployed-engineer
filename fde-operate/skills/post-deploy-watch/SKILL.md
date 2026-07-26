---
name: post-deploy-watch
description: Define and execute the observation window after a release - smoke checks, the specific metrics that would show this change broke something, how long to watch, and pre-agreed rollback triggers - converting "seems fine" into a recorded verification. Use immediately after any non-routine deploy, during a staged or percentage rollout, or when a change shipped with unverified items that were accepted as residual risk. A deploy is not done when the pipeline goes green; it is done when the observation window closes without incident.
---

# Post-deploy watch

The part after the pipeline goes green.

## Why this exists

Deployment is treated as complete when the pipeline succeeds. That's the moment the change starts being tested by reality, not the moment it finishes.

Two specific failures follow from stopping there. The first: nobody watches, the change degrades something subtly, and it's found days later by a customer or a month-end report — by which point the connection to the deploy is lost and diagnosis starts from scratch. The second: someone does watch, sees nothing alarming, and declares it fine — which is a feeling, not a verification, and it's indistinguishable from not having watched.

This skill exists to close the loop that `release-readiness` opened. Every item accepted as residual risk was accepted on the understanding that it would be detectable. This is where that promise is kept.

## When this applies

- Immediately after any non-routine deploy
- During a staged or percentage rollout
- A change shipped with accepted residual risk
- The first production run of anything new

## When it doesn't

- Routine low-risk deploys in a mature pipeline with good alerting
- Something has already broken — that's `incident-triage`
- Non-production environments

## Prerequisites

- `.fde/08-release-readiness.md` — **the residual unknowns are your watch list**
- `.fde/runbooks/deploy-*.md` — rollback triggers and procedure
- `.fde/03b-nfrs.md` — the targets you're watching against

## Procedure

### 1. Derive the watch list from the residual unknowns

The connection that makes this skill work. `release-readiness` produced a list of things that were unverified but accepted because they were judged detectable. **Each one is a watch item**, and the watch is where "detectable" gets tested.

For each: what specifically would you see if the pessimistic case is true, and where would you see it?

Add the standard set: error rate, latency, throughput, and the specific business metric this change touches.

**The business metric matters most and is most often omitted.** A refund change that leaves error rates and latency untouched while quietly halving the refund success rate is a serious incident with a perfectly healthy technical dashboard. Watch the thing the change was about.

### 2. Establish the baseline before you need it

Capture the normal range **before** deploying, or immediately after. Someone watching a dashboard without knowing normal cannot tell 40 errors per minute from a problem.

Note the daily and weekly shape too. A metric that always dips at 14:00 will produce a false alarm from anyone who doesn't know that, and a false rollback is expensive in a different way.

### 3. Smoke check immediately, on the real thing

Within minutes of deploying, verify the change actually works in production — not that the pods are healthy, but that the behavior is right.

Exercise the specific path that changed, with a real request where it's safe to do so. `deploy-runbook` should already name this step.

Where the change is behind a flag at zero percent, the smoke check is that the *old* path still works. That's a real check and it's routinely skipped, on the assumption that a disabled feature can't break anything — which is untrue when the deploy also changed shared code.

### 4. Set the window by how the failure would appear

Not an arbitrary "watch for an hour." Match the window to the failure mode:

| Failure mode | Window |
|---|---|
| Immediate errors | Minutes |
| Latency or resource degradation | 1–2 hours, through a load peak |
| Leak — memory, connections, file handles | Hours to days |
| Batch or scheduled job | Until the next run completes |
| Weekly or monthly process | Until it runs — days or weeks |
| Data correctness | Until reconciliation runs |

The long ones are what people get wrong. A change affecting a month-end process is not verified until month-end, and saying so is the honest position. Record it as an open watch item with a date and an owner rather than closing the deploy as complete.

### 5. Name who is watching, and make sure they know

A watch with no name doesn't happen. State who, until when, and what they do if they see something.

If the window extends beyond your working day, hand it over explicitly — to on-call, with the trigger conditions and the runbook. An unhanded-over watch ends when you close your laptop, and everyone assumes otherwise.

### 6. Use the pre-agreed triggers, and don't renegotiate them live

`deploy-runbook` defined rollback triggers with thresholds and a named decider. Use them as written.

The temptation under pressure is to reinterpret — "it's above the threshold but it looks like it's coming down." That's exactly the reasoning the thresholds were set in advance to prevent, because judgment degrades when you're invested in the change having worked.

Where a threshold turns out to be wrong, note it for next time and follow it now.

### 7. Record the outcome

Close the loop in writing, however briefly.

- What was watched, over what window
- What the metrics actually did, with numbers
- Which residual unknowns are now resolved, and which remain open
- Anything surprising, even if it didn't trigger anything

That third point is the substance. `release-readiness` accepted specific risks; this is where they get closed or carried forward. An unresolved item that nobody carried forward is one that quietly became permanent — and it belongs in `handover-pack` under open risks if it's still open when you leave.

## Output

Append to the deploy runbook, or `.fde/runbooks/deploy-<change>.md`:

```markdown
## Post-deploy watch

**Deployed:** <date, time> · **Watcher:** <name> · **Window:** 2h active, 7d passive
**Handover:** on-call from 18:00, triggers briefed ✅

### Baseline (captured pre-deploy)
| Metric | Normal | Peak-hour normal |
|---|---|---|
| `refund_errors` | 1/min | 3/min |
| Refund p95 | 0.7s | 0.9s |
| Refund success rate | 99.4% | 99.2% |

### Smoke check
| # | Check | Expect | Result | Time |
|---|---|---|---|---|
| 1 | EUR refund end to end | currency stored, correct amount | ✅ | 14:12 |
| 2 | Legacy GBP refund unaffected | unchanged behavior | ✅ | 14:14 |

### Watch items — from residual unknowns
| # | From | Watching | Result |
|---|---|---|---|
| 1 | Prod-volume latency unmeasured | p95 through the 16:00 peak | ✅ 0.94s, within target |
| 2 | Team D consumer compatibility | their 4xx rate | ✅ no change over 7d |
| 3 | **Month-end reconciliation** | recon job output | ⏳ **open until <date>** — owner <name> |

### Observed
| Time | Metric | Value | Note |
|---|---|---|---|
| 14:30 | errors | 1/min | baseline |
| 16:00 | p95 | 0.94s | peak, within target |
| 18:00 | success rate | 99.4% | unchanged |

### Outcome
**Resolved:** unknowns 1 and 2 — both now `[confirmed]`.
**Still open:** unknown 3, cannot resolve until month-end. Carried to `09-handover.md`.
**Surprises:** none.
**Rollback triggers:** none reached.
```

## Common traps

**Treating pipeline-green as done.** That's when reality starts testing it.

**"Seems fine" as verification.** Indistinguishable from not having looked.

**Watching without a baseline.** You can't tell 40 errors/min from a problem.

**Only watching technical metrics.** A change that halves the success rate with healthy error rates and latency is a serious incident with a clean dashboard.

**An arbitrary window.** Match it to how the failure would appear — leaks take days, month-end takes a month.

**No named watcher.** It doesn't happen.

**Not handing over at end of day.** The watch silently ends and everyone assumes otherwise.

**Renegotiating triggers under pressure.** Exactly what setting them in advance was for.

**Not closing the loop on residual unknowns.** They quietly become permanent, and nobody carries them into the handover.
